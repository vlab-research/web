#!/usr/bin/env python3
"""Cell table for the SA-ASIA group (Bangladesh, India, Pakistan). Contract: notes/cells-schema.md.

    ../../geo/venv/bin/python cells.py --fetch   # re-pull raw/ from vprod (SELECT only), then build
    ../../geo/venv/bin/python cells.py           # build from raw/

(`../../geo` is the session scratchpad copy of build_maps.py with Natural Earth and GeoNames;
set GEO=/path/to/geo to point elsewhere.)

Reads  scripts/pilot-maps/private/SA-ASIA.map.json   (gitignored: study ids, form shortcodes,
       qualifying question refs per recruitment)
       raw/                                          (gitignored pulls)
Writes scripts/data/cells/SA-ASIA.{cells,criteria,places}.json and the "cells" and "checks"
       sections of the private map (cell -> raw stratum ids).

One script for the three countries; the raw pulls for all of them live in BD/raw/.

Method (country-recipe.md, "The unit is the place"):
- spend: Insights per campaign x stratum x day, max within a day, days with spend > 0 only;
  a campaign seen under two studies is counted once (max per campaign x stratum x day).
- started: a person's EARLIEST message in any of the recruitment's forms must carry ad-set
  labels (Fly response metadata, written from the ad referral) that match a stratum of one of
  the recruitment's studies, and must fall 1 day before to 3 days after the recruitment's spend
  window. Where a stratum lists its creatives, the person's creative must be one of them: that is
  what separates sibling studies that share one form and one set of labels. Each person once per
  recruitment.
- qualified: started, in a quota group (the labels above) and answered the recruitment's
  qualifying question in one of its forms (the final quota rule, recounted from Fly responses;
  checked against inference_data and the adopt report).
- impressions: Insights rows carry cpm but no impressions for these accounts, so
  impressions = spend x 1000 / cpm per day.
"""
import csv, json, os, re, sys, subprocess, hashlib, statistics, collections, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
PM = os.path.dirname(os.path.dirname(HERE))                # scripts/pilot-maps
REPO = os.path.dirname(os.path.dirname(PM))
RAW = os.path.join(HERE, "raw")
PRIV = os.path.join(PM, "private", "SA-ASIA.map.json")
OUT = os.path.join(REPO, "scripts", "data", "cells")
G = "SA-ASIA"
GEO = os.environ.get("GEO", os.path.join(PM, "geo"))
if not os.path.exists(os.path.join(GEO, "build_maps.py")):
    GEO = os.environ.get("PILOT_GEO", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "geo"))
csv.field_size_limit(10 ** 9)

MAP = json.load(open(PRIV))
CFG = MAP["recruitments"]
EXCL = MAP.get("excluded", {})
ALL_SIDS = sorted({sid for r in list(CFG.values()) + list(EXCL.values()) for sid in r["studies"].values()})
SC_ALL = sorted({sc for r in CFG.values() for sc in r["shortcodes"]})
IDS = ",".join(f"'{s}'" for s in ALL_SIDS)
SCS = ",".join(f"'{s}'" for s in SC_ALL)
# stratum metadata key -> column of the Fly first-row pull
LABEL_COL = {"Division": "div", "Gender": "gen", "Genders": "gen", "gender": "gen", "Caregiver": "cg",
             "Age": "age", "age": "age", "District": "loc", "Province": "loc", "location": "loc",
             "geography": "loc", "language": "lang"}
NORM = {"हिन्दी": "Hindi"}
norm = lambda v: NORM.get(v, v)


# ----------------------------------------------------------------------------- fetch (SELECT only)
def q(sql, db="vlab", fmt="tsv"):
    assert sql.lstrip().upper().startswith(("SELECT", "WITH")), "read-only"
    return subprocess.run(["kubectl", "exec", "-n", "vprod", "gbv-cockroachdb-0", "--", "/cockroach/cockroach", "sql",
                           "--insecure", f"--format={fmt}", f"--database={db}", "-e", sql],
                          check=True, capture_output=True, text=True, timeout=300).stdout


def fetch():
    os.makedirs(os.path.join(RAW, "rep"), exist_ok=True)
    os.makedirs(os.path.join(RAW, "forms"), exist_ok=True)
    w = lambda n, s: open(os.path.join(RAW, n), "w").write(s)
    w("confs_all.ndjson", q(f"SELECT study_id, conf_type, created, conf::string AS conf FROM study_confs "
                            f"WHERE study_id IN ({IDS}) ORDER BY 1,2,3", fmt="ndjson"))
    w("daily.tsv", q(f"""WITH r AS (SELECT e.study_id, c.key AS camp, s.key AS strat,
          coalesce(s.value->>'date_start', e.period_start::date::string) AS d,
          (s.value->>'spend')::float8 AS spend, (s.value->>'impressions')::float8 AS imp, (s.value->>'cpm')::float8 AS cpm
        FROM recruitment_data_events e, jsonb_each(e.data) AS c, jsonb_each(c.value) AS s
        WHERE e.study_id IN ({IDS}) AND jsonb_typeof(c.value)='object' AND jsonb_typeof(s.value)='object'
          AND s.value->>'spend' IS NOT NULL),
      m AS (SELECT study_id, camp, strat, d, max(spend) spend FROM r GROUP BY 1,2,3,4)
      SELECT m.study_id, m.camp, m.strat, m.d, m.spend, max(r.imp) imp, max(r.cpm) cpm
      FROM m JOIN r USING (study_id, camp, strat, d) WHERE r.spend = m.spend GROUP BY 1,2,3,4,5 ORDER BY 1,2,3,4"""))
    w("shared_camps.tsv", q("WITH c AS (SELECT DISTINCT e.study_id, k.key AS camp FROM recruitment_data_events e, "
                            "jsonb_object_keys(e.data) AS k(key)) SELECT camp, array_agg(study_id::string) FROM c "
                            "GROUP BY 1 HAVING count(*)>1"))
    for sid in ALL_SIDS:   # one study at a time: a correlated max() over adopt_reports hangs
        w(os.path.join("rep", sid + ".ndjson"),
          q(f"SELECT study_id, created, details::string AS details FROM adopt_reports WHERE study_id='{sid}' "
            "AND report_type='FACEBOOK_ADOPT' ORDER BY created DESC LIMIT 1", fmt="ndjson"))
    # label values only (ad-set metadata; the language CHOICE for India). Never answers, never free text.
    w("inference.tsv", q(f"""SELECT study_id, user_id, variable,
          CASE WHEN variable IN ('Gender','Genders','Division','Age','Caregiver','District','Province','gender',
                                 'location','age','geography')
                 OR (variable='language' AND value::string IN ('"English"','"हिन्दी"'))
               THEN value::string ELSE '' END AS value, timestamp
        FROM inference_data WHERE study_id IN ({IDS})"""))
    # Fly: earliest message per person x form, and the first row carrying ad metadata (labels only)
    w("fly_first.tsv", q(f"""WITH f AS (SELECT userid, shortcode, min(timestamp) t0 FROM responses
            WHERE shortcode IN ({SCS}) AND timestamp > '2023-10-01' GROUP BY 1,2),
          m AS (SELECT DISTINCT ON (userid, shortcode) userid, shortcode, timestamp tm, metadata->>'creative' cr,
              coalesce(metadata->>'Division','') div, coalesce(metadata->>'Gender', metadata->>'Genders', metadata->>'gender','') gen,
              coalesce(metadata->>'Caregiver','') cg, coalesce(metadata->>'Age', metadata->>'age','') age,
              coalesce(metadata->>'District', metadata->>'Province', metadata->>'location', metadata->>'geography','') loc,
              coalesce(metadata->>'language','') lang
            FROM responses WHERE shortcode IN ({SCS}) AND timestamp > '2023-10-01' AND metadata ? 'creative'
            ORDER BY userid, shortcode, timestamp)
        SELECT f.userid, f.shortcode, f.t0, m.tm, m.cr, m.div, m.gen, m.cg, m.age, m.loc, m.lang
        FROM f LEFT JOIN m USING (userid, shortcode)""", db="chatroach"))
    refs = sorted({r["qualify_ref"] for r in CFG.values()})
    w("fly_answers.tsv", q(f"SELECT userid, shortcode, question_ref, min(timestamp) t FROM responses "
                           f"WHERE shortcode IN ({SCS}) AND timestamp > '2023-10-01' AND question_ref IN "
                           f"({','.join(repr(x) for x in refs)}) GROUP BY 1,2,3", db="chatroach"))
    # the form each recruitment's people saw (version in force at the middle of its spend window)
    spend_win = windows(load_spend())
    for rid, r in CFG.items():
        lo, hi = spend_win[rid]
        mid = (dt.date.fromisoformat(lo) + (dt.date.fromisoformat(hi) - dt.date.fromisoformat(lo)) / 2).isoformat()
        out = q(f"SELECT id, created, form_json::string AS f FROM surveys WHERE shortcode='{r['form']}' "
                f"AND created <= '{mid} 23:59' ORDER BY created DESC LIMIT 1", db="chatroach", fmt="ndjson")
        w(os.path.join("forms", rid + ".ndjson"), out)


# ----------------------------------------------------------------------------- loaders
def num(v):
    return 0.0 if v in ("NULL", "", None) else float(v)


def load_confs():
    H = collections.defaultdict(list)
    for l in open(os.path.join(RAW, "confs_all.ndjson")):
        r = json.loads(l)
        H[(r["study_id"], r["conf_type"])].append((r["created"], json.loads(r["conf"])))
    for v in H.values():
        v.sort(key=lambda x: x[0])
    return H


def load_spend():
    """(sid, camp, strat, d) -> (spend, impressions) for spend > 0."""
    out = {}
    for r in csv.DictReader(open(os.path.join(RAW, "daily.tsv")), delimiter="\t"):
        sp = num(r["spend"])
        if sp <= 0:
            continue
        imp = num(r["imp"]) or (sp * 1000 / num(r["cpm"]) if num(r["cpm"]) else 0.0)
        out[(r["study_id"], r["camp"], r["strat"], r["d"])] = (sp, imp)
    return out


def windows(spend):
    w = {}
    for rid, r in CFG.items():
        ds = [k[3] for k in spend if k[0] in r["studies"].values()]
        w[rid] = (min(ds), max(ds))
    return w


def ts(s):
    s = s.replace("+00", "")
    return dt.datetime.fromisoformat(s[:26])


# ----------------------------------------------------------------------------- targeting
def km_of(c):
    r = float(c.get("radius", 0))
    return round(r * 1.609344, 2) if c.get("distance_unit") == "mile" else round(r, 2)


def genders(ft):
    g = ft.get("genders")
    return "men" if g == [1] else "women" if g == [2] else "all"


def geo_sig(ft):
    def one(g):
        if not g:
            return None
        d = {}
        if g.get("countries"):
            d["countries"] = sorted(g["countries"])
        if g.get("regions"):
            d["regions"] = sorted(x["name"] for x in g["regions"])
        if g.get("cities"):
            d["cities"] = sorted((x["key"], x.get("name"), x.get("region"), km_of(x)) for x in g["cities"])
        if g.get("custom_locations"):
            d["custom_locations"] = sorted((round(x["latitude"], 5), round(x["longitude"], 5), km_of(x))
                                           for x in g["custom_locations"])
        return d or None
    return json.dumps([one(ft.get("geo_locations")), one(ft.get("excluded_geo_locations"))], sort_keys=True)


def strata_in_force(H, sid, lo, hi, spent_ids=()):
    """Each stratum id -> the latest version of it saved before the last spend day; and whether its
    targeting differed between the versions that were live during the spend window."""
    hist = H.get((sid, "strata"), [])
    out, changed = {}, set()
    live = []
    for i, (t, conf) in enumerate(hist):
        nxt = hist[i + 1][0] if i + 1 < len(hist) else "9999"
        if t[:10] <= hi and nxt[:10] >= lo:
            live.append(conf)
    if not live:
        live = [hist[-1][1]]
    seen = {}
    for conf in live:
        for s in conf:
            ft = s.get("facebook_targeting") or {}
            if not ft.get("geo_locations"):
                continue          # a draft saved without locations: no ad set can run on it
            sig = (geo_sig(ft), genders(ft), ft.get("age_min"), ft.get("age_max"))
            if s["id"] in seen and seen[s["id"]] != sig:
                changed.add(s["id"])
            seen[s["id"]] = sig
            out[s["id"]] = s
    # ids that spent but are only in older versions (renamed ad sets); never stale copies that did not spend
    for t, conf in hist:
        for s in conf:
            if s["id"] in spent_ids:
                out.setdefault(s["id"], s)
    return out, changed


# ----------------------------------------------------------------------------- places
import importlib


def bm():
    sys.path.insert(0, GEO)
    return importlib.import_module("build_maps")


A3 = {"BD": "BGD", "PK": "PAK", "IN": "IND"}
_PLACES = {}


def place_of(cc, ft, side_hint=None):
    """Place key and record for a stratum's geometry."""
    g = ft.get("geo_locations") or {}
    ex = ft.get("excluded_geo_locations") or {}
    h = hashlib.md5(geo_sig(ft).encode()).hexdigest()[:6]
    if g.get("custom_locations") and not ex:
        cl = g["custom_locations"]
        radii = sorted({km_of(c) for c in cl})
        r = "-".join(f"{x:g}" for x in radii)
        key = f"{cc}:radius:{len(cl)}x{r}km-{h}"
        rec = dict(country=cc, type="radius_set", label=f"Inside {len(cl)} radius areas of {r} km",
                   pins=[[round(c["latitude"], 5), round(c["longitude"], 5), km_of(c)] for c in cl])
        return key, rec, None
    if g.get("regions") and not ex and not g.get("custom_locations") and not g.get("cities"):
        meta = sorted(x["name"] for x in g["regions"])
        names = [x.replace(" Division", "") for x in meta]
        key = f"{cc}:region:{'+'.join(names)}"
        lab = " and ".join(names) + (" (whole divisions)" if cc == "BD" and len(names) > 1 else
                                     " Division (whole)" if cc == "BD" else " (whole)")
        return key, dict(country=cc, type="region", label=lab, regions=meta), None
    if g.get("cities") and not ex:
        cs = g["cities"]
        r = "-".join(f"{x:g}" for x in sorted({km_of(c) for c in cs}))
        key = f"{cc}:city_radius:{len(cs)}x{r}km-{h}"
        return key, dict(country=cc, type="city_radius", label=f"Inside {len(cs)} city radius areas of {r} km",
                         pins=[geocode_city(cc, c) for c in cs]), "inside"
    if g.get("countries") == [cc] and not ex:
        return f"{cc}:country", dict(country=cc, type="country", label=f"{COUNTRY[cc]}, whole country"), None
    if g.get("countries") == [cc] and ex.get("cities"):
        cs = ex["cities"]
        r = "-".join(f"{x:g}" for x in sorted({km_of(c) for c in cs}))
        key = f"{cc}:country-minus:{len(cs)}-cities-{r}km-{h}"
        return key, dict(country=cc, type="country_minus",
                         label=f"{COUNTRY[cc]} except {len(cs)} city radius areas of {r} km",
                         pins_excluded=[geocode_city(cc, c) for c in cs]), "outside"
    raise SystemExit(f"unhandled geometry {geo_sig(ft)[:200]}")


COUNTRY = {"BD": "Bangladesh", "PK": "Pakistan", "IN": "India"}
CITY_CHECK = {}
GN_ALIAS = {"Rahimyar Khan": "Rahim Yar Khan"}   # Meta spelling -> GeoNames


def geocode_city(cc, c):
    """Meta cities carry a name and region but no coordinates: take the GeoNames populated place of
    that name (administrative seats first, then population) and record whether it sits in the admin-1
    Meta names."""
    B = bm()
    name = GN_ALIAS.get(c["name"], c["name"])
    cand = [x for x in B.geonames(cc) if x["name"] == name or x["ascii"] == name]
    cand.sort(key=lambda x: (not x["code"].startswith(("PPLA", "PPLC")), -x["pop"]))
    if not cand:
        CITY_CHECK[c["name"]] = "not found in GeoNames"
        return [None, None, km_of(c)]
    x = cand[0]
    units = B.admin1(A3[cc])
    from shapely.geometry import Point
    inside = [n for n, gg in units.items() if gg.contains(Point(x["lon"], x["lat"]))]
    CITY_CHECK[c["name"]] = dict(meta_region=c.get("region"), geonames_unit=inside[0] if inside else None,
                                 lat=x["lat"], lon=x["lon"], feature=x["code"], candidates=len(cand))
    return [round(x["lat"], 4), round(x["lon"], 4), km_of(c)]


NE_NAME = {"Chittagong": "Chattogram"}      # Meta / stratum name -> Natural Earth admin-1 name
PK_AREA = {"Central": "Karachi", "East": "Karachi", "West": "Karachi", "Malir": "Karachi (outer)",
           "Hyderabad": "Hyderabad", "Sukkar": "around Sukkur", "Larkana": "around Larkana"}
PK_SINDH = set(PK_AREA)


def claimed_units(cc, ft, md):
    """The admin-1 each pin claims to be in: the stratum's division label (BD), Sindh for the Sindh
    radius sets (PK), or the Meta region of each city (Meta city objects)."""
    g = ft.get("geo_locations") or {}
    ex = ft.get("excluded_geo_locations") or {}
    cities = g.get("cities") or ex.get("cities")
    if cities:
        return [c.get("region") for c in cities]
    if cc == "BD" and md.get("Division"):
        return NE_NAME.get(md["Division"], md["Division"])
    if cc == "PK" and md.get("District") in PK_SINDH:
        return "Sindh"
    return None


def pin_check(cc, pins, claimed):
    """Every pin: the country and admin-1 it falls in (Natural Earth 10m; within ~2 km of the unit
    counts as in it, for coastline artefacts), against the unit it claims; and whether a named place
    (Natural Earth or GeoNames) is within 5 km."""
    B = bm()
    from shapely.geometry import Point
    units = B.admin1(A3[cc])
    res = collections.Counter()
    ok = other = out = unc = named = 0
    for i, (lat, lon, r) in enumerate(pins):
        want = claimed[i] if isinstance(claimed, list) else claimed
        if lat is None:
            unc += 1
            continue
        p = Point(lon, lat)
        u = next((n for n, gg in units.items() if gg.contains(p)), None)
        if u is None:
            near = min(units, key=lambda n: units[n].distance(p))
            u = near if units[near].distance(p) < 0.02 else None
        res[u or "outside country"] += 1
        if u is None:
            out += 1
        elif want and u != want:
            if isinstance(claimed, list):
                unc += 1          # a Meta city whose name matches a place in another region
            else:
                other += 1
        else:
            ok += 1
        if B.name_point(lat, lon, A3[cc], cc):
            named += 1
    flag = ("pins_outside_country" if out else "pin_uncertain" if unc else
            "pins_in_other_division" if other else "pin_checked")
    return dict(claimed=claimed if not isinstance(claimed, list) else "each city's Meta region", n=len(pins),
                admin1=dict(res), in_claimed_unit=ok, other_unit=other, outside_country=out, uncertain=unc,
                named_place_within_5km=named, flag=flag)


# ----------------------------------------------------------------------------- build
def median(xs):
    return round(statistics.median(xs), 1) if xs else None


def build():
    H = load_confs()
    SP = load_spend()
    WIN = windows(SP)
    sid2slug = {sid: slug for r in list(CFG.values()) + list(EXCL.values()) for slug, sid in r["studies"].items()}

    fly = collections.defaultdict(dict)       # shortcode -> user -> row
    for r in csv.DictReader(open(os.path.join(RAW, "fly_first.tsv")), delimiter="\t"):
        fly[r["shortcode"]][r["userid"]] = r
    ans = collections.defaultdict(dict)       # (shortcode, ref) -> user -> first time
    for r in csv.DictReader(open(os.path.join(RAW, "fly_answers.tsv")), delimiter="\t"):
        ans[(r["shortcode"], r["question_ref"])][r["userid"]] = ts(r["t"])
    inf_lang, inf_users = {}, collections.defaultdict(set)
    inf_q = collections.defaultdict(set)
    for r in csv.DictReader(open(os.path.join(RAW, "inference.tsv")), delimiter="\t"):
        inf_users[r["study_id"]].add(r["user_id"])
        inf_q[(r["study_id"], r["variable"])].add(r["user_id"])
        if r["variable"] == "language" and r["value"]:
            inf_lang[(r["study_id"], r["user_id"])] = json.loads(r["value"])
    shared = {}
    for r in list(csv.reader(open(os.path.join(RAW, "shared_camps.tsv")), delimiter="\t"))[1:]:
        shared[r[0]] = r[1].strip("{}").split(",")

    cells, crit_auto, places, private_cells, checks = [], {}, {}, {}, {}
    for rid, R in CFG.items():
        cc = rid[:2]
        sids = list(R["studies"].values())
        lo, hi = WIN[rid]
        wlo = (dt.date.fromisoformat(lo) - dt.timedelta(days=1)).isoformat()
        whi = (dt.date.fromisoformat(hi) + dt.timedelta(days=3)).isoformat()
        # strata in force, per study
        ST, changed = {}, {}
        for sid in sids:
            spent_ids = {k[2] for k in SP if k[0] == sid}
            ST[sid], changed[sid] = strata_in_force(H, sid, lo, hi, spent_ids)
        # cell key: identical targeting and identical labels pool across sibling studies
        def ckey(sid, stid):
            s = ST[sid][stid]
            ft = s.get("facebook_targeting") or {}
            lab = tuple(sorted((LABEL_COL.get(k, k), norm(str(v))) for k, v in (s.get("metadata") or {}).items()))
            return (geo_sig(ft), genders(ft), ft.get("age_min"), ft.get("age_max"), lab)

        # ---- spend (dedupe campaigns seen under two studies: max per campaign x stratum x day)
        sp = {}
        for (sid, camp, strat, d), v in SP.items():
            if sid in sids:
                k = (camp, strat, d)
                if k not in sp or v[0] > sp[k][0][0]:
                    sp[k] = (v, sid)
        agg = collections.defaultdict(lambda: dict(spend=0.0, imp=0.0, days=collections.defaultdict(float), src=set()))
        live = collections.defaultdict(set)     # (sid, stid) -> days with spend
        unmatched_spend = 0.0
        for (camp, strat, d), ((v, imp), sid) in sp.items():
            if strat not in ST[sid]:
                unmatched_spend += v
                continue
            a = agg[ckey(sid, strat)]
            a["spend"] += v; a["imp"] += imp; a["days"][d] += v; a["src"].add((sid, strat))
            live[(sid, strat)].add(d)
        cross = {c: s for c, s in shared.items() if set(s) & set(sids) and set(s) - set(sids)}
        agg_day = {(k, d): v for k, a in agg.items() for d, v in a["days"].items()}
        resolved = collections.Counter()

        # ---- people
        first = {}
        for sc in R["shortcodes"]:
            for u, row in fly[sc].items():
                if u not in first or row["t0"] < first[u]["t0"]:
                    first[u] = dict(row, sc=sc)
        pc = collections.defaultdict(lambda: dict(started=0, qualified=0, mins=[]))
        drop = collections.Counter()
        seen_users = set()
        for u, row in first.items():
            if not row["tm"] or row["tm"] == "NULL":
                drop["no ad metadata"] += 1; continue
            t0, tm = ts(row["t0"]), ts(row["tm"])
            if (tm - t0).total_seconds() > 120:
                drop["ad labels arrive after the first message"] += 1; continue
            if not wlo <= row["t0"][:10] <= whi:
                drop["first message outside the spend window"] += 1; continue
            lab = {k: norm(row[k]) for k in ("div", "gen", "cg", "age", "loc", "lang")}
            cands = []
            for sid in sids:
                for stid, s in ST[sid].items():
                    md = s.get("metadata") or {}
                    if md and all(lab.get(LABEL_COL.get(k, k)) == norm(str(v)) for k, v in md.items()):
                        cands.append((sid, stid))
            if not cands:
                drop["labels match no stratum"] += 1; continue
            bycr = [c for c in cands if row["cr"] in (ST[c[0]][c[1]].get("creatives") or [])]
            if bycr:
                cands = bycr
            keys = {ckey(*c) for c in cands}
            if len(keys) > 1:
                d0 = t0.date()
                okd = {(d0 - dt.timedelta(days=k)).isoformat() for k in (0, 1)}
                lv = [c for c in cands if live[c] & okd]
                if lv:
                    cands = lv
                keys = {ckey(*c) for c in cands}
            if len(keys) > 1:
                # the ad sets that could have brought them spent on the same days: attribute to the one that
                # spent at least 10x the others on the first day and the day before, else leave out
                d0 = t0.date()
                days2 = [(d0 - dt.timedelta(days=k)).isoformat() for k in (0, 1)]
                w = collections.defaultdict(float)
                for c in cands:
                    for dd in days2:
                        w[ckey(*c)] += agg_day.get((ckey(*c), dd), 0.0)
                top = sorted(w.items(), key=lambda kv: -kv[1])
                if len(top) > 1 and top[0][1] >= 10 * top[1][1] and top[0][1] > 0:
                    keys = {top[0][0]}
                    resolved[top[0][0]] += 1
                else:
                    drop["ambiguous: two ad sets with different targeting"] += 1; continue
            k = keys.pop()
            if k not in agg:
                drop["matched ad set never spent in this recruitment"] += 1; continue
            seen_users.add(u)
            c = pc[k]; c["started"] += 1
            tq = [ans[(sc, R["qualify_ref"])].get(u) for sc in R["shortcodes"]]
            tq = [t for t in tq if t and t0 - dt.timedelta(minutes=1) <= t <= t0 + dt.timedelta(days=7)]
            ok = bool(tq)
            if ok and R.get("language_values"):
                langs = {inf_lang.get((sid, u)) for sid in sids}
                ok = bool(langs & set(R["language_values"]))
            if ok:
                c["qualified"] += 1
                c["mins"].append((min(tq) - t0).total_seconds() / 60)

        # ---- rows
        rows = []
        for i, (k, a) in enumerate(sorted(agg.items(), key=lambda kv: sorted(kv[1]["src"]))):
            sid, stid = sorted(a["src"])[0]
            s = ST[sid][stid]
            ft = s.get("facebook_targeting") or {}
            pkey, prec, side = place_of(cc, ft)
            places.setdefault(pkey, prec)
            geo_pins = prec.get("pins") or prec.get("pins_excluded")
            if geo_pins and pkey not in checks.get("_pins", {}):
                claimed = claimed_units(cc, ft, s.get("metadata") or {})
                pcx = pin_check(cc, geo_pins, claimed)
                checks.setdefault("_pins", {})[pkey] = pcx
                prec["pin_check"] = {k: pcx[k] for k in ("n", "in_claimed_unit", "other_unit", "outside_country",
                                                         "uncertain", "named_place_within_5km", "claimed")}
                if isinstance(claimed, str) and prec["type"] == "radius_set":
                    unit = {"Chattogram": "Chittagong"}.get(claimed, claimed)
                    if cc == "PK":
                        unit = PK_AREA[(s.get("metadata") or {}).get("District")] + ", Sindh"
                    extra = []
                    if pcx["other_unit"]:
                        extra.append(f"{pcx['other_unit']} in a neighbouring division" if cc == "BD" else
                                     f"{pcx['other_unit']} just outside it")
                    if pcx["outside_country"]:
                        extra.append(f"{pcx['outside_country']} across the border")
                    prec["label"] += f", {unit}" + (" Division" if cc == "BD" else "") + \
                        (f" ({'; '.join(extra)})" if extra else "")
            p = pc[k]
            days = sorted(a["days"])
            flags = []
            if p["started"] < 200:
                flags.append("thin")
            if len(days) == 1:
                flags.append("one_day")
            pcx = checks.get("_pins", {}).get(pkey)
            if pcx:
                flags.append(pcx["flag"])
            if len({x[0] for x in a["src"]}) > 1:
                flags.append("pooled_siblings")
            elif len(a["src"]) > 1:
                flags.append("renamed_ad_sets_pooled")
            if any(st in changed[sd] for sd, st in a["src"]):
                flags.append("targeting_changed_in_window")
            interests = bool(ft.get("flexible_spec") or ft.get("interests") or ft.get("behaviors"))
            if interests:
                flags.append("interest_targeting")
            md = s.get("metadata") or {}
            glab = next((v for kk, v in md.items() if LABEL_COL.get(kk) == "gen"), None)
            gl = {"women": "women", "female": "women", "men": "men", "male": "men"}.get(str(glab).lower())
            if glab and genders(ft) != "all" and gl != genders(ft):
                flags.append("gender_label_differs_from_ad_targeting")
            if glab and genders(ft) == "all":
                flags.append("gender_label_is_creative_version")
            if resolved.get(k):
                flags.append("some_people_attributed_by_dominant_spend")
            flags.append("impressions_from_cpm")
            cell_id = f"{rid}/{i + 1:02d}"
            rows.append(dict(rec=rid, cell=cell_id, country=cc, place=pkey, side=side,
                             ads=dict(genders=genders(ft), age_min=ft.get("age_min"), age_max=ft.get("age_max"),
                                      interests=interests),
                             person_override=None, first=days[0], last=days[-1], spend_days=len(days),
                             spend_usd=round(a["spend"], 2), impressions=int(round(a["imp"])),
                             started=p["started"], qualified=p["qualified"],
                             median_daily_spend=round(statistics.median(a["days"].values()), 2),
                             median_minutes_to_qualify=median(p["mins"]), flags=flags, attribution="ad_metadata"))
            private_cells[cell_id] = [dict(study=sid2slug[sd], study_id=sd, stratum=st) for sd, st in sorted(a["src"])]
        cells += rows

        # ---- checks against reports and inference_data
        rep_sp = rep_q = 0.0
        reps = {}
        for sid in sids:
            L = open(os.path.join(RAW, "rep", sid + ".ndjson")).read().strip().splitlines()
            if L:
                d = json.loads(json.loads(L[0])["details"])
                reps[sid2slug[sid]] = dict(created=json.loads(L[0])["created"][:16],
                                           spend=round(sum(v.get("lifetime_spent", 0) for v in d.values()), 2),
                                           qualified=sum(v["current_participants"] for v in d.values()))
        allm = sorted(x for k in pc for x in pc[k]["mins"])
        ins = round(sum(v[0][0] for v in sp.values()), 2)
        crit_auto[rid] = dict(first=min(r["first"] for r in rows), last=max(r["last"] for r in rows),
                              started=sum(r["started"] for r in rows), qualified=sum(r["qualified"] for r in rows),
                              median_minutes_to_qualify=median(allm),
                              ads=dict(genders=sorted({r["ads"]["genders"] for r in rows}),
                                       age_min=min((r["ads"]["age_min"] for r in rows if r["ads"]["age_min"]), default=None),
                                       age_max=max((r["ads"]["age_max"] for r in rows if r["ads"]["age_max"]), default=None),
                                       interests=any(r["ads"]["interests"] for r in rows)))
        checks[rid] = dict(insights_spend=ins, cell_spend=round(sum(r["spend_usd"] for r in rows), 2),
                           spend_not_in_any_stratum=round(unmatched_spend, 2), reports=reps,
                           inference_qualified={sid2slug[s]: len(inf_q[(s, R["qualify_ref"])]) for s in sids},
                           not_attributed=dict(drop), cross_recruitment_shared_campaigns=len(cross),
                           window=[wlo, whi])

    # ---- excluded recruitments
    for rid, R in EXCL.items():
        sids = list(R["studies"].values())
        ins = round(sum(v[0] for k, v in SP.items() if k[0] in sids), 2)
        checks[rid] = dict(insights_spend=ins)
    return cells, crit_auto, places, private_cells, checks


# ----------------------------------------------------------------------------- criteria (authored)
BD_CARE = ["consent", "caregiver:child_age:9-17", "caregiver:child_gender:girl"]
BD_WHO = "cares for a girl aged 9–17; reached the {q}th of {n} questions"
CRIT = {
    "BD-2023-11a": dict(round="pilot", screen=BD_CARE, channel="messenger", languages=["bn"],
                        incentive=dict(amount=100, currency="BDT", form="airtime"),
                        qualify_rule="in a quota group and answered the last screening-block question near the end of the form",
                        notes="Four-day pilot of the form used in BD-2023-11b, whole divisions, gender-targeted ad sets. "
                              "The rule used is the one saved when its ads ran; a re-save 18 days after its ads stopped "
                              "moved it to an early question and is ignored."),
    "BD-2023-11b": dict(round="baseline", screen=BD_CARE, channel="messenger", languages=["bn"],
                        incentive=dict(amount=100, currency="BDT", form="airtime"),
                        qualify_rule="in a quota group and answered the last screening-block question near the end of the form",
                        notes="Seven whole divisions x two creative versions. The 'Men'/'Women' ad sets were NOT gender-"
                              "targeted on Meta (no genders key): they are creative versions, so ads.genders is 'all'. "
                              "Airtime of 100 taka on a stitched payment form after the qualifying point."),
    "BD-2024-06a": dict(round="pilot", screen=BD_CARE, channel="messenger", languages=["bn"],
                        incentive=dict(amount=200, currency="BDT", form="airtime"),
                        qualify_rule="in a quota group and answered the follow-up to the near-final screening-block question",
                        notes="Three-day test, whole divisions, gender-targeted. The ad set labelled for Sylhet targeted "
                              "Barisal and Sylhet together, so its place is the two divisions."),
    "BD-2024-06b": dict(round="pilot", screen=BD_CARE, channel="messenger", languages=["bn"],
                        incentive=dict(amount=200, currency="BDT", form="airtime"),
                        qualify_rule="in a quota group and answered the near-final screening-block question",
                        notes="One day of ads ($13). Same geometry as BD-2024-06a, different form version."),
    "BD-2024-09a": dict(round="pilot", screen=BD_CARE, channel="messenger", languages=["bn"],
                        incentive=dict(amount=200, currency="BDT", form="airtime"),
                        qualify_rule="in a quota group and answered the near-final screening-block question",
                        notes="Three sibling test runs feeding one form, 1 km radius areas. In two of them every ad set, "
                              "including those labelled for women, was targeted at men on Meta; ads.genders records the "
                              "targeting, and the flag marks the mismatch. Two runs share identical targeting and are "
                              "pooled per ad set. A third run spent $0.91 in one ad set and brought nobody attributable; 17 "
                              "people whose labels fit two differently-targeted ad sets live on the same day are left out."),
    "BD-2024-09b": dict(round="baseline", screen=BD_CARE, channel="messenger", languages=["bn"],
                        incentive=dict(amount=200, currency="BDT", form="airtime"),
                        qualify_rule="in a quota group and answered the near-final screening-block question",
                        notes="Four sibling ad runs feeding one form, each with its own set of 1 km radius areas in three "
                              "divisions; women 25–45 and men 30–50 as separate ad sets. People are split between the runs by "
                              "the creative in their ad metadata (each run had its own creatives). The per-run reports all "
                              "carry the form-wide qualified count."),
    "BD-2024-10": dict(round="baseline", screen=BD_CARE, channel="messenger", languages=["bn"],
                       incentive=dict(amount=200, currency="BDT", form="airtime"),
                       qualify_rule="in a quota group and answered the near-final screening-block question",
                       notes="Three whole divisions, no gender or age targeting, one creative, three days. Qualified (1,410) "
                             "is above the last per-group report (1,007): the report ran on the last ad day and the "
                             "recorded answers stop there, while 356 people who had started from the ads answered the "
                             "qualifying question the next day (counted from the form responses)."),
    "BD-2024-12a": dict(round="endline-fresh", screen=BD_CARE, channel="messenger", languages=["bn"],
                        incentive=dict(amount=200, currency="BDT", form="airtime"),
                        qualify_rule="in a quota group and answered the near-final screening-block question",
                        notes="A fresh cross-section recruited with ads: about 6% of its people had been in an earlier "
                              "Bangladesh recruitment. Four whole divisions, no gender or age targeting. Qualified is 3 above the "
                              "last report, which ran two days after the last ad day."),
    "BD-2024-12b": dict(round="endline-fresh", screen=BD_CARE, channel="messenger", languages=["bn"],
                        incentive=dict(amount=200, currency="BDT", form="airtime"),
                        qualify_rule="in a quota group and answered the near-final screening-block question",
                        notes="Fresh sample with ads (7% had been in an earlier Bangladesh recruitment). 1 km radius "
                              "areas, gender-targeted, no age targeting. Ran alongside BD-2024-12a/c/d/e, each with its own "
                              "form; 15% of its people also started one of those, and are counted in each."),
    "BD-2024-12c": dict(round="endline-fresh", screen=BD_CARE, channel="messenger", languages=["bn"],
                        incentive=dict(amount=200, currency="BDT", form="airtime"),
                        qualify_rule="in a quota group and answered the near-final screening-block question",
                        notes="Fresh sample with ads (5% had been in an earlier Bangladesh recruitment; 14% also started "
                              "another December form). Same radius areas as BD-2024-12b. Gender-targeted, no age targeting."),
    "BD-2024-12d": dict(round="endline-fresh", screen=BD_CARE, channel="messenger", languages=["bn"],
                        incentive=dict(amount=200, currency="BDT", form="airtime"),
                        qualify_rule="in a quota group and answered the near-final screening-block question",
                        notes="Fresh sample with ads (6% had been in an earlier Bangladesh recruitment; 12% also started "
                              "another December form). Same radius areas as one run of BD-2024-09b. Gender-targeted, no "
                              "age targeting."),
    "BD-2024-12e": dict(round="endline-fresh", screen=BD_CARE, channel="messenger", languages=["bn"],
                        incentive=dict(amount=200, currency="BDT", form="airtime"),
                        qualify_rule="in a quota group and answered the near-final screening-block question",
                        notes="Fresh sample with ads (5% had been in an earlier Bangladesh recruitment; 14% also started "
                              "another December form), one division only (47 radius areas of 1 km). Gender-targeted, no age "
                              "targeting."),
    "IN-2025-09": dict(round="pilot", screen=["age:18-99", "consent", "quota_group:education_subsample", "gave_phone"],
                       channel="messenger", languages=["en", "hi"],
                       incentive=dict(amount=10, currency="INR", form="airtime"),
                       qualify_rule="chose English or Hindi, and answered the phone-operator question after giving a number",
                       notes="Whole country, gender-targeted, 18–65, with English-language and Hindi-language ad sets "
                             "(cells are ad language x gender; the Hindi ad sets were renamed mid-run and are pooled). "
                             "Adults only; a random share of people without a degree were screened out. The first question "
                             "(language choice) is a separate form and is counted. Offer was 10–20 rupees of airtime. The "
                             "per-group report ($538.62) leaves out the $86.99 spent by the Hindi ad sets before their rename."),
    "PK-2024-04": dict(round="baseline", screen=["consent"], channel="messenger", languages=["en"],
                       incentive=dict(amount=100, currency="PKR", form="airtime"),
                       qualify_rule="in a quota group and answered the last question before the payment block",
                       notes="Inside 14 Meta cities with a 25-mile (40 km) radius against the rest of the country, "
                             "gender-targeted, 18–50. The inside set names Islamabad by one Meta city key and the outside "
                             "set excludes a different Islamabad key, so the two sides may overlap around Islamabad (the "
                             "excluded Rawalpindi area covers most of it). Meta lists one city (Kotli) under a region it is "
                             "not in, so that pin is uncertain. Qualified (413) is above the last report (291): the report "
                             "ran on the last ad day and about 100 people answered the qualifying question the next day. "
                             "A different ad account from the other Pakistan recruitments (US dollars, CPM $0.66)."),
    "PK-2024-05": dict(round="cross-section", screen=["consent"], channel="messenger", languages=["en"],
                       incentive=dict(amount=100, currency="PKR", form="airtime"),
                       qualify_rule="in a quota group and answered the last question before the payment block",
                       notes="Same targeting as PK-2024-04 a month later, a longer form. Three days of ads. The quota rule "
                             "moved to a later question on the second ad day; the final rule is used. Qualified (227) is "
                             "above the last report (133), which ran before the ads stopped."),
    "PK-2025-07": dict(round="cross-section", screen=["consent", "caregiver:child_age:9-17", "caregiver:child_gender:girl"],
                       channel="messenger", languages=["ur", "sd"],
                       incentive=dict(amount=500, currency="PKR", form="airtime"),
                       qualify_rule="in a quota group and answered the near-final screening-block question",
                       notes="Five whole provinces/territories x gender (women 23–49, men 25–60). Two days of ads; the "
                             "last per-group report was written early on the second day (it has $286.50 of $315.68 and 1,506 "
                             "qualified); the recount (2,029) agrees with the recorded answers (2,035)."),
    "PK-2025-08": dict(round="baseline", screen=["consent", "caregiver:child_age:9-17", "caregiver:child_gender:girl"],
                       channel="messenger", languages=["ur"],
                       incentive=dict(amount=280, currency="PKR", form="airtime"),
                       qualify_rule="in a quota group and answered the last question of the first-wave form",
                       notes="Wave 1 of a two-wave panel; wave 2 re-contacted people without ads and is out. Seven sets of "
                             "radius areas in one province (1 km in two cities, 4 km and 5 km elsewhere) x gender "
                             "(women 23–49, men 25–60)."),
}
WHO = {
    "PK-2024-04": "aged 18–50 by ad targeting; reached question {q} of {n}",
    "PK-2024-05": "aged 18–50 by ad targeting; reached question {q} of {n}",
    "IN-2025-09": "adults who chose English or Hindi; gave a phone number at question {q} of {n}",
}


def form_point(rid):
    L = open(os.path.join(RAW, "forms", rid + ".ndjson")).read().strip().splitlines()
    s = json.loads(L[0])["f"]
    try:
        f = json.loads(s)
    except json.JSONDecodeError:
        f = json.loads(re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', s))
    qs = []
    for x in f["fields"]:
        d = (x.get("properties") or {}).get("description", "") or ""
        if x["type"] == "statement" or re.search(r'"type"\s*:\s*"(stitch|wait|webview)"', d):
            continue
        qs.append(x["ref"])
    ref = CFG[rid]["qualify_ref"]
    pre = CFG[rid].get("form_prefix_questions", 0)
    return dict(question=qs.index(ref) + 1 + pre, of=len(qs) + pre)


def main():
    if "--fetch" in sys.argv:
        fetch()
    cells, auto, places, private_cells, checks = build()
    crit = []
    for rid in CFG:
        a, c = auto[rid], CRIT[rid]
        qp = form_point(rid)
        who = WHO.get(rid, "cares for a girl aged 9–17; reached question {q} of {n}").format(q=qp["question"], n=qp["of"])
        crit.append(dict(rec=rid, country=rid[:2], first=a["first"], last=a["last"], round=c["round"], ads=a["ads"],
                         screen=c["screen"], who_qualified=who, qualify_rule=c["qualify_rule"], qualify_point=qp,
                         median_minutes_to_qualify=a["median_minutes_to_qualify"], channel=c["channel"],
                         languages=c["languages"], incentive=c["incentive"], started=a["started"],
                         qualified=a["qualified"],
                         notes=c["notes"] + " Qualifying point: non-statement fields in form order, branches counted as "
                                            "if asked. Impressions derived from Insights CPM."))
    for rid in EXCL:
        crit.append(dict(rec=rid, country=rid[:2], first=None, last=None, round="excluded", ads=None, screen=[],
                         who_qualified=None, qualify_rule=None, qualify_point=None, median_minutes_to_qualify=None,
                         channel="messenger", languages=["bn"], incentive=None, started=0, qualified=0,
                         notes="A fourth sibling test run of BD-2024-09a with no recorded spend and no location targeting "
                               "saved; nothing to attribute."))
    os.makedirs(OUT, exist_ok=True)
    json.dump(cells, open(os.path.join(OUT, f"{G}.cells.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(crit, open(os.path.join(OUT, f"{G}.criteria.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(dict(sorted(places.items())), open(os.path.join(OUT, f"{G}.places.json"), "w"), indent=1, ensure_ascii=False)
    MAP["cells"] = private_cells
    MAP["checks"] = checks
    MAP["city_geocode"] = CITY_CHECK
    json.dump(MAP, open(PRIV, "w"), indent=1, ensure_ascii=False)
    # summary
    print(f"{'rec':12} {'cells':>5} {'spend':>9} {'insights':>9} {'report$':>9} {'started':>7} {'qual':>6} {'rep.q':>6}")
    for r in crit:
        if r["round"] == "excluded":
            continue
        ch = checks[r["rec"]]
        rs = sum(v["spend"] for v in ch["reports"].values())
        rq = sorted({v["qualified"] for v in ch["reports"].values()})
        print(f"{r['rec']:12} {sum(1 for c in cells if c['rec'] == r['rec']):5} {ch['cell_spend']:9.2f} "
              f"{ch['insights_spend']:9.2f} {rs:9.2f} {r['started']:7} {r['qualified']:6} {str(rq):>6}  "
              f"drop={ch['not_attributed']} inf={ch['inference_qualified']}")


if __name__ == "__main__":
    main()
