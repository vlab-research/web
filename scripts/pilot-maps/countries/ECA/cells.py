#!/usr/bin/env python3
"""Cell table for country group ID-ECA (Indonesia, Bulgaria, Serbia, Kyrgyzstan, Turkiye).

Contract: notes/cells-schema.md. Method: notes/country-recipe.md ("The unit is the place").

    python3 cells.py --fetch     # re-pull (SELECT only) into raw/, then build
    python3 cells.py             # build from raw/

Needs shapely (for the pin checks); run it with the pilot-maps venv. GEO points at a directory
holding the Natural Earth geojson and geonames/<CC>.txt (fetch_ne.py); default scripts/pilot-maps.

Reads   ../../private/ID-ECA.map.json   recruitment id -> studies and forms (gitignored)
        raw/*                           read-only pulls (gitignored)
Writes  scripts/data/cells/ID-ECA.{cells,criteria,places}.json
        ../../private/ID-ECA.map.json   its 'cells' section: cell id -> raw stratum id

No study slug, id, programme or topic word is written to a tracked file: those live only in the
private map, and every label below is written from targeting geometry.
"""
import csv, collections, datetime as dt, hashlib, json, math, os, re, statistics, subprocess, sys, unicodedata

csv.field_size_limit(10 ** 9)
HERE = os.path.dirname(os.path.abspath(__file__))
PM = os.path.dirname(os.path.dirname(HERE))           # scripts/pilot-maps
RAW = os.path.join(HERE, "raw")
PRIV = os.path.join(PM, "private", "ID-ECA.map.json")
OUT = os.path.join(os.path.dirname(PM), "data", "cells")
GEO = os.environ.get("GEO", PM)
G = "ID-ECA"
P = lambda *f: os.path.join(RAW, *f)
MAP = json.load(open(PRIV))
REC = MAP["recruitments"]
MI = 1.609344


# ----------------------------------------------------------------------------- fetch
def sql(db, q, out):
    cmd = ["timeout", "170", "kubectl", "exec", "-n", "vprod", "gbv-cockroachdb-0", "--", "/cockroach/cockroach",
           "sql", "--insecure", "--format=tsv", f"--database={db}", "-e", q]
    assert re.match(r"\s*(SELECT|WITH|SHOW)\b", q, re.I), "read-only queries only"
    with open(out, "w") as fh:
        subprocess.run(cmd, stdout=fh, check=True)


def fetch():
    os.makedirs(P("rep"), exist_ok=True)
    sids = sorted({sid for r in REC.values() for sid in r["studies"].values()})
    ids = ",".join(f"'{s}'" for s in sids)
    sql("vlab", f"SELECT study_id, conf_type, created, conf::string AS conf FROM study_confs "
                f"WHERE study_id IN ({ids}) ORDER BY study_id, conf_type, created", P("all_confs.tsv"))
    # Insights: max per campaign x stratum x day (temp rows are cumulative snapshots). Impressions are
    # not stored for these studies; they are derived as spend / CPM x 1000 from the same row.
    sql("vlab", "SELECT e.study_id::string AS sid, c.key AS camp, s.key AS strat, "
                "coalesce(s.value->>'date_start', e.period_start::date::string) AS d, "
                "max((s.value->>'spend')::float8) AS spend, "
                "max(CASE WHEN (s.value->>'cpm')::float8 > 0 THEN 1000*(s.value->>'spend')::float8/(s.value->>'cpm')::float8 END) AS imp "
                "FROM recruitment_data_events e, jsonb_each(e.data) AS c, jsonb_each(c.value) AS s "
                f"WHERE e.study_id IN ({ids}) AND jsonb_typeof(c.value)='object' AND jsonb_typeof(s.value)='object' "
                "AND s.value->>'spend' IS NOT NULL GROUP BY 1,2,3,4", P("spend_daily.tsv"))
    camps = set()
    for r in csv.DictReader(open(P("spend_daily.tsv")), delimiter="\t"):
        camps.add(r["camp"])
    cl = ",".join(f"'{c}'" for c in sorted(camps))
    sql("vlab", "SELECT c.key AS camp, array_agg(DISTINCT e.study_id::string) AS sids FROM recruitment_data_events e, "
                f"jsonb_each(e.data) AS c WHERE jsonb_typeof(c.value)='object' AND c.key IN ({cl}) GROUP BY 1",
        P("shared_camps.tsv"))
    # people: ad-set labels and screening answers only; every other value (phone numbers) is dropped in SQL
    keep = "('md:stratum_age','md:stratum_gender','md:stratum_location','age','Age','Gender','Location')"
    sql("vlab", "SELECT study_id::string AS study_id, user_id, variable, "
                f"CASE WHEN variable IN {keep} THEN value::string END AS value, timestamp "
                f"FROM inference_data WHERE study_id IN ({ids})", P("inf.tsv"))
    for sid in sids:
        sql("vlab", "SELECT study_id, created, details::string AS details FROM adopt_reports "
                    f"WHERE study_id='{sid}' AND report_type='FACEBOOK_ADOPT' ORDER BY created DESC LIMIT 1",
            P("rep", sid + ".tsv"))
    scs = sorted({s for r in REC.values() for k, v in r["forms"].items() for s in (v if isinstance(v, list) else [v])})
    sl = ",".join(f"'{s}'" for s in scs)
    sql("chatroach", f"WITH l AS (SELECT shortcode, max(created) m FROM surveys WHERE shortcode IN ({sl}) GROUP BY 1) "
                     "SELECT s.shortcode, s.created, s.form_json::string AS form FROM surveys s "
                     "JOIN l ON l.shortcode=s.shortcode AND l.m=s.created", P("forms.tsv"))


if "--fetch" in sys.argv:
    fetch()

# ----------------------------------------------------------------------------- configs
H = collections.defaultdict(list)
for r in csv.DictReader(open(P("all_confs.tsv")), delimiter="\t"):
    H[(r["study_id"], r["conf_type"])].append((r["created"], json.loads(r["conf"])))


def latest(sid, t):
    v = H.get((sid, t))
    return v[-1][1] if v else None


def md_vars(sid):
    out = set()
    for _, c in H.get((sid, "inference_data"), []):
        for src in c["data_sources"].values():
            if isinstance(src, dict):
                src = src.get("extraction_confs", [])
            for e in src:
                if e["location"] == "metadata":
                    out.add(e["name"])
    return out


def rule_answered(q, out):
    if not q:
        return out
    if q.get("op") in ("and", "or", "not"):
        for v in q["vars"]:
            rule_answered(v, out)
    elif q.get("op") == "answered":
        out.append(q["vars"][0]["value"])
    return out


def gsig(ft):
    """Targeting geometry, normalised: what decides the place key."""
    def one(g):
        if not g:
            return None
        d = {}
        if g.get("countries"):
            d["countries"] = sorted(g["countries"])
        if g.get("regions"):
            d["regions"] = sorted(x["name"] for x in g["regions"])
        if g.get("cities"):
            d["cities"] = sorted({(x["name"], x["key"], round(km(x), 1)) for x in g["cities"]})
        if g.get("custom_locations"):
            d["pins"] = sorted({(round(x["latitude"], 4), round(x["longitude"], 4), round(km(x), 2)) for x in g["custom_locations"]})
        return d or None
    return one(ft.get("geo_locations")), one(ft.get("excluded_geo_locations"))


def km(x):
    return x["radius"] * (MI if x.get("distance_unit") == "mile" else 1.0)


def tsig(s):
    ft = s.get("facebook_targeting") or {}
    return json.dumps([gsig(ft), ft.get("genders"), ft.get("age_min"), ft.get("age_max"),
                       bool(ft.get("flexible_spec") or ft.get("interests"))], sort_keys=True, default=str)


# ----------------------------------------------------------------------------- spend
spend = {}          # (sid, strat, day) -> [spend, imp]
camp_of = collections.defaultdict(set)
for r in csv.DictReader(open(P("spend_daily.tsv")), delimiter="\t"):
    k = (r["sid"], r["strat"], r["d"])
    v = float(r["spend"])
    imp = float(r["imp"]) if r["imp"] not in ("", "NULL") else 0.0
    camp_of[r["sid"]].add(r["camp"])
    if k not in spend or v > spend[k][0]:
        spend[k] = [v, imp]
for r in list(csv.DictReader(open(P("shared_camps.tsv")), delimiter="\t")):
    s = list(r.values())[1].strip("{}").split(",")
    assert len(s) == 1, f"campaign shared across studies: {r['camp']} (would need de-duplication)"

# ----------------------------------------------------------------------------- recruitments -> strata
STRATA = {}         # rec -> {stratum id: dict(defn, versions, introduced, sid)}
for rec, R in REC.items():
    (sid,) = R["studies"].values()
    hist = H[(sid, "strata")]
    st = {}
    for i, (t, c) in enumerate(hist):
        nxt = hist[i + 1][0] if i + 1 < len(hist) else "9999"
        for s in c:
            e = st.setdefault(s["id"], dict(introduced=t[:10], versions=[], sid=sid))
            e["defn"] = s
            e["versions"].append((t[:10], nxt[:10], tsig(s), s))
    if R.get("strata_introduced_before"):
        st = {k: v for k, v in st.items() if v["introduced"] < R["strata_introduced_before"]}
    if R.get("strata_introduced_after"):
        st = {k: v for k, v in st.items() if v["introduced"] >= R["strata_introduced_after"]}
    STRATA[rec] = st

FINAL_ANSWERED = {}  # the recruitment's final quota rule: which question counts as qualifying
for rec, R in REC.items():
    (sid,) = R["studies"].values()
    last = latest(sid, "strata")
    mine = [s for s in last if s["id"] in STRATA[rec]] or last
    FINAL_ANSWERED[rec] = sorted({v for s in mine for v in rule_answered(s.get("question_targeting"), [])})

WIN = {}
for rec, st in STRATA.items():
    days = [d for (sid, strat, d), (v, _) in spend.items() if strat in st and sid == st[strat]["sid"] and v > 0]
    WIN[rec] = (min(days), max(days))

# ----------------------------------------------------------------------------- people
inf = collections.defaultdict(lambda: collections.defaultdict(dict))   # sid -> user -> var -> (value, ts)
for r in csv.DictReader(open(P("inf.tsv")), delimiter="\t"):
    val = json.loads(r["value"]) if r["value"] not in ("", "NULL") else None
    ts = r["timestamp"][:19]
    cur = inf[r["study_id"]][r["user_id"]].get(r["variable"])
    if cur is None or ts < cur[1]:
        inf[r["study_id"]][r["user_id"]][r["variable"]] = (val, ts)


def evaluate(q, vars_, rename):
    op = q.get("op")
    if op == "and":
        return all(evaluate(v, vars_, rename) for v in q["vars"])
    if op == "or":
        return any(evaluate(v, vars_, rename) for v in q["vars"])
    if op == "not":
        return not evaluate(q["vars"][0], vars_, rename)
    a = q["vars"][0]["value"]
    if op == "answered":
        return rename.get(a, a) in vars_
    b = q["vars"][1]["value"]
    x = vars_.get(a, (None,))[0]
    if x is None:
        return False
    if op == "equal":
        return str(x) == str(b)
    if op == "not_equal":
        return str(x) != str(b)
    try:
        x, b = float(x), float(b)
    except (TypeError, ValueError):
        return False
    return {"greater_than": x > b, "less_than": x < b, "greater_equal_than": x >= b, "lower_than": x < b}[op]


def within(rec, ts):
    lo, hi = WIN[rec]
    d = dt.date.fromisoformat(ts[:10])
    return dt.date.fromisoformat(lo) - dt.timedelta(days=1) <= d <= dt.date.fromisoformat(hi) + dt.timedelta(days=3)


def dtm(ts):
    return dt.datetime.fromisoformat(ts)


ROWS = collections.defaultdict(lambda: dict(started=0, qualified=0, minutes=[], t0=[]))
UNASSIGNED = collections.Counter()
RULE_RENAMED = collections.Counter()
for sid in {s for R in REC.values() for s in R["studies"].values()}:
    recs = [rec for rec, R in REC.items() if sid in R["studies"].values()]
    mv = md_vars(sid)
    for u, vars_ in inf[sid].items():
        md = {k: v for k, v in vars_.items() if k in mv}
        if not md:
            UNASSIGNED[(sid[:8], "no ad metadata")] += 1
            continue
        t0 = min(v[1] for v in md.values())
        cands = []
        for rec in recs:
            for stid, e in STRATA[rec].items():
                meta = e["defn"].get("metadata") or {}
                keys = {k: (k if k in mv else "md:" + k) for k in meta}
                if keys and all(keys[k] in md and str(md[keys[k]][0]) == str(meta[k]) for k in meta) \
                        and len([k for k in md]) >= len(keys) and within(rec, t0):
                    # every metadata variable the person carries must be matched by the stratum's labels
                    if set(md) == set(keys.values()):
                        cands.append((rec, stid))
        if len(cands) != 1:
            UNASSIGNED[(sid[:8], "no matching ad set in window" if not cands else "ambiguous")] += 1
            continue
        rec, stid = cands[0]
        q = STRATA[rec][stid]["defn"].get("question_targeting")
        answered = rule_answered(q, [])
        rename = {a: FINAL_ANSWERED[rec][0] for a in answered if a not in FINAL_ANSWERED[rec]} if len(FINAL_ANSWERED[rec]) == 1 else {}
        if not answered:     # a stratum retired before any rule was set: apply the final rule
            q = {"op": "answered", "vars": [{"type": "variable", "value": FINAL_ANSWERED[rec][0]}]}
            RULE_RENAMED[(rec, stid, "no rule; final applied")] += 1
        elif rename:
            RULE_RENAMED[(rec, stid, json.dumps(rename))] += 1
        ok = evaluate(q, vars_, rename)
        row = ROWS[(rec, stid)]
        row["started"] += 1
        row["t0"].append(t0[:10])
        if ok:
            row["qualified"] += 1
            qv = [rename.get(a, a) for a in rule_answered(q, [])]
            tq = max(vars_[a][1] for a in qv)
            m = (dtm(tq) - dtm(t0)).total_seconds() / 60
            if m >= 0:
                row["minutes"].append(m)

# ----------------------------------------------------------------------------- geography
import importlib.util
from shapely.geometry import Point, shape

A1 = [f for f in json.load(open(os.path.join(GEO, "ne_10m_admin_1_states_provinces.geojson")))["features"]
      if f["properties"]["iso_a2"] in {R["country"] for R in REC.values()}]
PP = [f["properties"] for f in json.load(open(os.path.join(GEO, "ne_10m_populated_places_simple.geojson")))["features"]]
A3 = {"ID": "IDN", "BG": "BGR", "RS": "SRB", "KG": "KGZ", "TR": "TUR"}


def norm(s):
    s = unicodedata.normalize("NFKD", s.replace("İ", "I").replace("ı", "i"))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return re.sub(r"\s+(province|oblast|region)$", "", s).strip()


UNITS = collections.defaultdict(dict)
UNITNAME = {}
for f in A1:
    p = f["properties"]
    UNITS[p["iso_a2"]][norm(p["name_en"] or p["name"])] = shape(f["geometry"])
    UNITNAME[(p["iso_a2"], norm(p["name_en"] or p["name"]))] = p["name_en"] or p["name"]
_GN = {}


def geonames(cc):
    if cc not in _GN:
        rows = []
        for line in open(os.path.join(GEO, "geonames", cc + ".txt"), encoding="utf8"):
            r = line.rstrip("\n").split("\t")
            if r[6] == "P":
                rows.append(dict(id=int(r[0]), name=r[1], ascii=r[2], lat=float(r[4]), lon=float(r[5]),
                                 code=r[7], a1=r[10], pop=int(r[14] or 0)))
        _GN[cc] = rows
    return _GN[cc]


def hav(a, b, c, d):
    p = math.pi / 180
    x = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(x))


def name_point(lat, lon, cc, max_km=5.0):
    """Nearest Natural Earth place or GeoNames town of 20,000+ within max_km; else nearest GeoNames place
    of 1,000+ within max_km; else None. The same rule as build_maps.name_point."""
    ne = [(hav(lat, lon, p["latitude"], p["longitude"]), p["name"], "Natural Earth") for p in PP if p["adm0_a3"] == A3[cc]]
    gn = [(hav(lat, lon, x["lat"], x["lon"]), x["name"], "GeoNames", x["pop"]) for x in geonames(cc) if x["pop"] >= 1000]
    best = min(ne + [g[:3] for g in gn if g[3] >= 20000])
    if best[0] > max_km:
        best = min(g[:3] for g in gn)
    if best[0] <= max_km:
        return dict(name=best[1], source=best[2], km=round(best[0], 1))
    # GeoNames carries no population for most Indonesian and Kyrgyz villages: fall back to the nearest
    # populated place of any size, recorded as such
    anyp = min((hav(lat, lon, x["lat"], x["lon"]), x["name"]) for x in geonames(cc))
    if anyp[0] <= max_km:
        return dict(name=anyp[1], source="GeoNames (any size)", km=round(anyp[0], 1))
    return None


def unit_of(cc, lat, lon):
    pt = Point(lon, lat)
    for k, g in UNITS[cc].items():
        if g.contains(pt):
            return k
    k = min(UNITS[cc], key=lambda k: UNITS[cc][k].distance(pt))
    return k + " (nearest)"


def geocode_city(cc, name, region):
    """A Meta city carries a name and a region, no point: take the GeoNames place of that name inside the
    region's Natural Earth polygon, capitals and admin seats first, then population."""
    reg = UNITS[cc].get(norm(region)) if region else None
    c = [x for x in geonames(cc) if (x["name"] == name or x["ascii"] == name)
         and (reg is None or reg.buffer(0.05).contains(Point(x["lon"], x["lat"])))]
    if not c:
        raise SystemExit(f"geocode: no GeoNames place {name!r} in {cc}/{region}")
    c.sort(key=lambda x: (not x["code"].startswith("PPLC"), not x["code"].startswith("PPLA"), -x["pop"]))
    x = c[0]
    return dict(name=name, lat=x["lat"], lon=x["lon"], geonameid=x["id"], feature_code=x["code"])


def h4(obj):
    return hashlib.sha1(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:4]


def rng(rs):
    lo, hi = min(rs), max(rs)
    f = lambda v: f"{v:g}"
    return f"{f(lo)}km" if lo == hi else f"{f(lo)}-{f(hi)}km"


COUNTRY = {"ID": "Indonesia", "BG": "Bulgaria", "RS": "Serbia", "KG": "Kyrgyzstan", "TR": "Türkiye"}
PLACES, PINCHECK = {}, {}


def check_pins(cc, pins):
    out = []
    for lat, lon, r in pins:
        n = name_point(lat, lon, cc)
        out.append(dict(pin=[lat, lon, r], near=n, unit=unit_of(cc, lat, lon)))
    return out


def city_pins(cc, cities):
    out, seen = [], set()
    for name, key, r in cities:
        g = CITY_REGION[(cc, key)]
        gc = geocode_city(cc, name, g)
        k = (gc["geonameid"], r)
        if k in seen:          # two Meta city keys with one name resolve to one GeoNames point
            continue
        seen.add(k)
        out.append([round(gc["lat"], 4), round(gc["lon"], 4), r])
    return out


CITY_REGION = {}
for (sid, t), v in H.items():
    if t == "strata":
        for _, c in v:
            for s in c:
                ft = s.get("facebook_targeting") or {}
                for g in (ft.get("geo_locations") or {}, ft.get("excluded_geo_locations") or {}):
                    for x in g.get("cities") or []:
                        CITY_REGION[(x["country"], x["key"])] = x.get("region")


def slug(s):
    s = norm(s)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def place_for(rec, cc, ft, loc_label):
    """Place key and record from one ad set's geometry. loc_label is the ad set's own location label with
    'Urban/Rural/Cities' stripped, used only to make the key readable."""
    inc, exc = gsig(ft)
    inc, exc = inc or {}, exc or {}
    base = slug(loc_label) if loc_label else ""
    if set(inc) == {"countries"} and not exc:
        return f"{cc}:country", dict(country=cc, type="country", label=f"{COUNTRY[cc]}, whole country")
    if set(inc) == {"countries"} and set(exc) <= {"pins", "cities"}:
        pins = [list(p) for p in exc.get("pins", [])] + city_pins(cc, exc.get("cities", []))
        rs = [p[2] for p in pins]
        if exc.get("cities") and not exc.get("pins"):
            names = "+".join(slug(c[0]) for c in exc["cities"])
            key = f"{cc}:country-minus:{names}-{rng(rs)}"
            lab = f"{COUNTRY[cc]} except {len(pins)} radius area{'s' if len(pins) > 1 else ''} of {rng(rs).replace('km', ' km')} around " + \
                  ", ".join(sorted({c[0] for c in exc['cities']}))
        else:
            key = f"{cc}:country-minus:{len(pins)}-areas-{rng(rs)}-{h4(pins)}"
            lab = f"{COUNTRY[cc]} outside {len(pins)} radius areas ({rng(rs).replace('km', ' km')})"
        return key, dict(country=cc, type="country_minus", label=lab, pins_excluded=pins)
    if set(inc) == {"cities"} and not exc:
        pins = city_pins(cc, inc["cities"])
        names = ", ".join(sorted({c[0] for c in inc["cities"]}))
        key = f"{cc}:city-radius:{'+'.join(slug(c[0]) for c in inc['cities'])}-{rng([p[2] for p in pins])}"
        return key, dict(country=cc, type="city_radius", label=f"{names}, {rng([p[2] for p in pins]).replace('km', ' km')} radius", pins=pins)
    if set(inc) == {"pins"}:
        pins = [list(p) for p in inc["pins"]]
        rs = [p[2] for p in pins]
        ex = city_pins(cc, exc.get("cities", [])) if exc else []
        key = f"{cc}:radius:{base + '-' if base else ''}{len(pins)}-areas-{rng(rs)}-{h4([pins, ex])}"
        lab = f"Inside {len(pins)} radius area{'s' if len(pins) > 1 else ''} ({rng(rs).replace('km', ' km')})" + \
              (f" in {loc_label}" if loc_label else "") + \
              (f", minus {len(ex)} excluded radius area{'s' if len(ex) > 1 else ''} of {rng([p[2] for p in ex]).replace('km', ' km')}" if ex else "")
        rec_ = dict(country=cc, type="radius_set", label=lab, pins=pins)
        if ex:
            rec_["pins_excluded"] = ex
        return key, rec_
    if set(inc) == {"regions"}:
        regs = inc["regions"]
        short = [re.sub(r"\s+Province$", "", x) for x in regs]
        if not exc:
            key = f"{cc}:region:{base or slug('-'.join(short))}-{len(regs)}-{h4(regs)}" if len(regs) > 1 else f"{cc}:region:{slug(short[0])}"
            lab = (f"{loc_label}: {len(regs)} provinces, whole ({', '.join(short)})" if len(regs) > 1
                   else f"{short[0]} (whole)")
            return key, dict(country=cc, type="region", label=lab, regions=regs)
        pins = [list(p) for p in exc.get("pins", [])]
        ex = city_pins(cc, exc.get("cities", []))
        inside = dict(pins=[tuple(p) for p in pins])
        comp = None
        for k, v in PLACES.items():
            if v["type"] == "radius_set" and sorted(map(tuple, v["pins"])) == sorted(map(tuple, pins)):
                comp = k
        key = f"{cc}:outside:{base + '-' if base else ''}{len(pins)}-areas-{rng([p[2] for p in pins])}-{h4([regs, pins, ex])}"
        where = (f"{loc_label} ({len(regs)} provinces)" if len(regs) > 1 else short[0])
        lab = f"{where} outside its {len(pins)} radius areas" + \
              (f" and {len(ex)} excluded radius area{'s' if len(ex) > 1 else ''} of {rng([p[2] for p in ex]).replace('km', ' km')}" if ex else "")
        r_ = dict(country=cc, type="radius_outside", label=lab, regions=regs, complement_of=comp, pins_excluded=pins)
        if ex:
            r_["pins_excluded_cities"] = ex
        return key, r_
    raise SystemExit(f"{rec}: geometry not handled: {inc} / {exc}")


# ----------------------------------------------------------------------------- cells
GENDER = {None: "all", (1,): "men", (2,): "women", (1, 2): "all"}
LOCWORD = re.compile(r"\s+(Urban|Rural|Cities)$")
LOCLABEL = {"ID": lambda s: LOCWORD.sub("", s), "TR": lambda s: LOCWORD.sub("", s).replace("İ", "I"),
            "KG": lambda s: LOCWORD.sub("", s) if s != "Rural" else "", "BG": lambda s: "", "RS": lambda s: ""}

cells, cellmap = [], {}
order = sorted(REC, key=lambda r: (REC[r]["country"], r))
# radius sets first, so each outside area can name its complement
for pass_ in ("pins", "rest"):
    for rec in order:
        cc = REC[rec]["country"]
        for stid, e in STRATA[rec].items():
            ft = e["defn"].get("facebook_targeting") or {}
            inc, _ = gsig(ft)
            is_pins = bool(inc) and set(inc) == {"pins"}
            if (pass_ == "pins") != is_pins:
                continue
            loc = (e["defn"].get("metadata") or {})
            loc = loc.get("Location") or loc.get("stratum_location") or ""
            key, rec_ = place_for(rec, cc, ft, LOCLABEL[cc](loc))
            if key in PLACES and PLACES[key] != rec_:
                raise SystemExit(f"place key collision {key}")
            PLACES[key] = rec_
            e["place"] = key

# An ad set whose metadata label is carried by nobody (the label was never extracted into the people
# data) cannot be told apart from the ad set that shares its other labels and its geometry: pool the two.
CARRIED = collections.defaultdict(set)
for sid_, us in inf.items():
    for vs in us.values():
        CARRIED[sid_].update(vs)
POOL = {}
for rec in order:
    for stid, e in STRATA[rec].items():
        mv = md_vars(e["sid"])
        meta = e["defn"].get("metadata") or {}
        var = lambda k: k if k in mv else "md:" + k
        if all(var(k) in CARRIED[e["sid"]] for k in meta):
            continue
        red = {k: v for k, v in meta.items() if var(k) in CARRIED[e["sid"]]}
        tgt = [t for t, f in STRATA[rec].items() if t != stid and (f["defn"].get("metadata") or {}) == red
               and f["place"] == e["place"]]
        if len(tgt) == 1:
            POOL[(rec, stid)] = tgt[0]


def run_version(e, days):
    """The ad set as it ran: the version in force on the days that carried most of its spend."""
    by_ver = collections.Counter()
    for d, v, _ in days:
        live_v = [x for x in e["versions"] if x[0] <= d] or e["versions"][:1]
        by_ver[live_v[-1][2]] += v
    run_sig = by_ver.most_common(1)[0][0]
    return next(x[3] for x in e["versions"] if x[2] == run_sig), by_ver


for rec in order:
    cc = REC[rec]["country"]
    n = 0
    for stid, e in sorted(STRATA[rec].items(), key=lambda x: (x[1]["place"], x[0])):
        if (rec, stid) in POOL:
            continue
        sid = e["sid"]
        members = [stid] + sorted(s_ for (r_, s_), t_ in POOL.items() if r_ == rec and t_ == stid)
        mdays = {m: sorted((d, v, imp) for (s_, st_, d), (v, imp) in spend.items() if s_ == sid and st_ == m and v > 0)
                 for m in members}
        members = [m for m in members if mdays[m]]
        dd = collections.defaultdict(lambda: [0.0, 0.0])
        for m in members:
            for d, v, imp in mdays[m]:
                dd[d][0] += v
                dd[d][1] += imp
        days = sorted((d, v, imp) for d, (v, imp) in dd.items())
        row = ROWS.get((rec, stid), dict(started=0, qualified=0, minutes=[], t0=[]))
        if not days:
            if row["started"]:
                UNASSIGNED[(rec, "people on an ad set with no spend")] += row["started"]
            continue
        n += 1
        cid = f"{rec}/{n:02d}"
        runs = {m: run_version(STRATA[rec][m], mdays[m]) for m in members}
        main = max(members, key=lambda m: sum(v for _, v, _ in mdays[m]))
        ft = dict(runs[main][0].get("facebook_targeting") or {})
        if len(members) > 1:      # pooled ad sets: the widest age range they covered
            fts = [runs[m][0].get("facebook_targeting") or {} for m in members]
            ft["age_min"] = min(f.get("age_min") or 18 for f in fts)
            ft["age_max"] = max(f.get("age_max") or 65 for f in fts)
        int_spend = sum(v for m in members for sg, v in runs[m][1].items() if json.loads(sg)[4])
        sp = sum(v for _, v, _ in days)
        flags = []
        if row["started"] < 200:
            flags.append("thin")
        if len(days) == 1:
            flags.append("one_day")
        if len(members) > 1:
            flags.append("pooled_ad_sets")
        if PLACES[e["place"]]["type"] in ("radius_set", "radius_outside", "country_minus", "city_radius"):
            flags.append("pin_checked")
        if ft.get("flexible_spec") or ft.get("interests"):
            flags.append("interest_targeting")
        lo, hi = days[0][0], days[-1][0]
        live = {v[2] for v in e["versions"] if v[1] > lo and v[0] <= hi}
        if len(live) > 1:
            flags.append("targeting_changed")
        if len({json.dumps(json.loads(x[2])[0]) for x in e["versions"] if x[1] > lo and x[0] <= hi}) > 1:
            flags.append("geometry_changed")
        if rec == "KG-2023-01" and (ft.get("age_min") or 0) >= 35:
            # six ad sets that ran on the first day only, then were replaced; Insights recorded under $1 each
            # while over a hundred people arrived through them: the spend is very likely under-recorded
            flags.append("spend_doubtful")
        if 0 < int_spend < sp - 0.005:
            flags.append("interests_part_of_run")
        if any(k[0] == rec and k[1] == stid for k in RULE_RENAMED):
            flags.append("final_rule_applied")
        late = sum(1 for t in row["t0"] if t > (dt.date.fromisoformat(hi) + dt.timedelta(days=3)).isoformat())
        if row["started"] and late / row["started"] > 0.2:
            flags.append("people_after_spend")   # over a fifth first wrote after this ad set had stopped spending
        side = {"radius_set": "inside", "radius_outside": "outside"}.get(PLACES[e["place"]]["type"])
        g = ft.get("genders")
        meta = e["defn"].get("metadata") or {}
        override = None
        q = e["defn"].get("question_targeting") or {}
        ages = [(x["op"], float(x["vars"][1]["value"])) for x in (q.get("vars") or [])
                if x.get("op") in ("greater_than", "less_than") and x["vars"][0]["value"] == "age"]
        if ages:
            lo_a = next((int(v) + 1 for o, v in ages if o == "greater_than"), 18)
            hi_a = next((int(v) - 1 for o, v in ages if o == "less_than"), 99)
            override = [f"age:{lo_a}-{hi_a}"]
        cells.append(dict(
            rec=rec, cell=cid, country=cc, place=e["place"], side=side,
            ads=dict(genders=GENDER[tuple(sorted(g)) if g else None], age_min=ft.get("age_min"),
                     age_max=ft.get("age_max"), interests=bool(ft.get("flexible_spec") or ft.get("interests"))),
            person_override=override,
            first=lo, last=hi, spend_days=len(days), spend_usd=round(sp, 2),
            impressions=int(round(sum(i for *_, i in days))) or None,
            started=row["started"], qualified=row["qualified"],
            median_daily_spend=round(statistics.median(v for _, v, _ in days), 2),
            median_minutes_to_qualify=round(statistics.median(row["minutes"]), 1) if row["minutes"] else None,
            flags=flags, attribution="ad_metadata"))
        cellmap[cid] = dict(stratum=members if len(members) > 1 else stid, study=[k for k, v in REC[rec]["studies"].items()][0])

# ----------------------------------------------------------------------------- pin checks
for key, p in PLACES.items():
    cc = p["country"]
    pins = p.get("pins") or p.get("pins_excluded") or []
    chk = check_pins(cc, pins) + check_pins(cc, p.get("pins_excluded_cities", []))
    if not chk:
        continue
    far = [c for c in chk if c["near"] is None]
    units = collections.Counter(c["unit"] for c in chk)
    names = sorted({c["near"]["name"] for c in chk if c["near"]})
    if p["type"] == "radius_set" and cc != "TR":   # TR labels name the statistical region, which is right
        u = collections.Counter(c["unit"].replace(" (nearest)", "") for c in check_pins(cc, p["pins"]))
        disp = {k: v for k, v in UNITNAME.items()}
        where = " and ".join(f"{disp.get((cc, k), k.title())}" + (f" ({n})" if len(u) > 1 else "") for k, n in u.most_common()) \
            if len(u) <= 3 else f"{len(u)} provinces"
        p["label"] = re.sub(r" in [^,]+(,|$)", f" in {where}\\1", p["label"], count=1) if " in " in p["label"] else p["label"] + f" in {where}"
    anysize = sum(1 for c in chk if c["near"] and c["near"]["source"] == "GeoNames (any size)")
    p["pin_check"] = (f"{len(chk) - len(far)} of {len(chk)} pins within 5 km of a named place (Natural Earth or GeoNames"
                      + (f"; {anysize} of them a GeoNames place with no recorded population" if anysize else "") + "); "
                      f"admin-1 units: " + ", ".join(f"{k} {v}" for k, v in sorted(units.items())))
    p["pin_names"] = names
    PINCHECK[key] = dict(far=[c["pin"] for c in far], units=dict(units))

# ----------------------------------------------------------------------------- forms: qualifying point
FORMS = {r["shortcode"]: json.loads(r["form"]) for r in csv.DictReader(open(P("forms.tsv")), delimiter="\t")}


def default_path(form):
    """Walk the form taking unconditional jumps, except that a screen-out is never taken (where the
    unconditional jump ends the form, the conditional jump to a question is the passing branch).
    Randomised arms and branch-only questions are not taken: the path of a respondent who passes
    every screen."""
    fields = form["fields"]
    idx = {f["ref"]: i for i, f in enumerate(fields)}
    logic = {l["ref"]: l["actions"] for l in form.get("logic", [])}
    i, path, seen = 0, [], set()
    while i < len(fields) and len(path) < 1000:
        f = fields[i]
        path.append(f)
        seen.add(i)
        nxt = i + 1
        acts = logic.get(f["ref"], [])
        always = [a for a in acts if a.get("condition", {}).get("op") == "always"]
        to_field = [a for a in acts if a["details"]["to"].get("type") == "field"]
        if always and always[0]["details"]["to"].get("type") == "field":
            nxt = idx[always[0]["details"]["to"]["value"]]
        elif always and to_field:          # the unconditional jump is a screen-out: take the passing branch
            nxt = idx[to_field[0]["details"]["to"]["value"]]
        elif always:
            nxt = len(fields)
        if nxt in seen:      # a retry loop (e.g. a failed payment): carry on down the form
            nxt = i + 1
            while nxt in seen:
                nxt += 1
        i = nxt
    return path


def qualify_point(rec):
    R = REC[rec]["forms"]
    pre = sum(1 for s in R["prefix"] for f in FORMS[s]["fields"] if f["type"] != "statement")
    path = [f for f in default_path(FORMS[R["main"]]) if f["type"] != "statement"]
    refs = [f["ref"] for f in path]
    qv = FINAL_ANSWERED[rec][0]
    if qv not in refs:
        raise SystemExit(f"{rec}: qualifying question {qv} not on the default path of the form")
    end = next((i for i, r in enumerate(refs) if r.startswith("hello_again") or r.startswith("stitch")), len(refs))
    return {"question": pre + refs.index(qv) + 1, "of": pre + end}


# ----------------------------------------------------------------------------- criteria (hand-written from the forms)
CRIT = {
    "ID-2025-04": dict(
        round="baseline",
        screen=["consent", "caregiver:child_age:0-2", "age:18-99"],
        who_qualified="aged 18 or over, caring for a child under 2 in their home; gave a phone number",
        qualify_rule="answered the phone-number question",
        channel="messenger", languages=["id"],
        incentive=dict(amount=10000, currency="IDR", form="airtime"),
        notes=("Ads in three provinces, each split into radius areas and the rest of the province, by gender and "
               "two ad age bands (21-29, 30-44). The quota rule changed on day 6 from 'answered the last main "
               "question' to 'gave a phone number' (a few questions later); qualified is recounted under the final "
               "rule. The phone question comes after the qualifying screens; the form states the airtime amount "
               "per wave. Question count: the path of a respondent who passes every screen, unconditional jumps only.")),
    "BG-2023-02": dict(
        round="baseline",
        screen=["consent", "age:18-99", "caregiver:child_age:0-6"],
        who_qualified="aged 18 or over, with a child aged 0-6 in the family; finished the survey and agreed to be contacted again",
        qualify_rule="answered the follow-up permission question (after the questions and the gift-card step)",
        channel="messenger", languages=["bg"],
        incentive=dict(amount=7, currency="BGN", form="gift_card"),
        notes=("A 10-day first round: ads split by gender, two ad age bands (18-26, 27-40) and inside/outside a "
               "40 km radius around Sofia, with Meta's parent-of-young-child targeting. A separate survey from "
               "BG-2023-03. The form randomises respondents into one of two question blocks; the count follows one. "
               "Question count: the path of a respondent who passes every screen, unconditional jumps only.")),
    "BG-2023-03": dict(
        round="baseline",
        screen=["consent", "age:18-99", "caregiver:child_age:0-6"],
        who_qualified="aged 18 or over, with a child aged 0-6 in the family; finished the survey and a link step",
        qualify_rule="reached the 'you have qualified' message, after the questions and a step asking them to open a link",
        channel="messenger", languages=["bg"],
        incentive=dict(amount=7, currency="BGN", form="gift_card"),
        notes=("One ad set for the whole country (ages 20-40, all genders) for six months, after four days with two "
               "age-band ad sets. Before qualifying, each respondent was asked to open a link (an app or a website, "
               "by randomised arm) and answer one question about it; any answer counted. Quota rule changed on day 10 "
               "from the follow-up question to the 'qualified' message just before it; recounted under the final rule. "
               "The first four days' two ad sets carried an age label that was never extracted, so their people "
               "cannot be told from the main ad set's: the three are pooled into one cell (flag pooled_ad_sets). On "
               "15-16 April 2023 a configuration error pointed this ad set at Serbia for about a day ($100 of spend, "
               "1%; arrivals fell from about 140 a day to 24 over the two days); left in. "
               "Follow-up waves re-contacted these people and are not counted.")),
    "RS-2023-04": dict(
        round="baseline",
        screen=["consent", "age:18-99", "caregiver:child_age:0-6"],
        who_qualified="aged 18 or over, with a child aged 0-6 in the family; finished the survey and a link step",
        qualify_rule="reached the 'you have qualified' message, after the questions and a step asking them to open a link",
        channel="messenger", languages=["sr"],
        incentive=dict(amount=430, currency="RSD", form="gift_card"),
        notes=("One ad set for the whole country (ages 20-40, all genders) for five and a half months. The same "
               "survey design as BG-2023-03: a link step before qualifying (any answer counted). Follow-up waves "
               "re-contacted these people and are not counted.")),
    "KG-2023-01": dict(
        round="baseline",
        screen=["consent", "caregiver:child_age:0-3", "age:18-99"],
        who_qualified="aged 18 or over with a child aged 0-3, whose stated age matched the ad's age band; finished the short survey",
        qualify_rule="answered the follow-up permission question at the end of the survey, with a stated age in the ad set's band",
        channel="messenger", languages=["ky", "ru"],
        incentive=dict(amount=100, currency="KGS", form="airtime", when="after_followup"),
        notes=("Nothing was paid for this survey; airtime was promised for completing a follow-up weeks later. Ads by "
               "gender and two ad age bands (18-24, 25-40) across 23 radius areas of 2-9 km in five regions, and the "
               "rest of the country. From day 45 the rule also required the stated age to match the ad set's band "
               "(per cell in person_override); recounted under that final rule, which gives 2,797 qualified against the "
               "3,004 in the last report (April 2023); the gap is not explained. Six ad sets for ages 35+ ran on the first "
               "day only; their recorded spend is very likely incomplete (flag spend_doubtful). The first question is "
               "a language choice.")),
    "TR-2023-01": dict(
        round="baseline",
        screen=["consent", "caregiver:child_age:0-3", "age:18-99"],
        who_qualified="aged 18 or over with a child aged 0-3; finished the short survey",
        qualify_rule="answered the follow-up permission question at the end of the survey",
        channel="messenger", languages=["tr"],
        incentive=dict(amount=35, currency="TRY", form="gift_card", when="after_followup"),
        notes=("Nothing was paid for this survey; a gift card was promised for completing a follow-up weeks later. "
               "96 ad sets: 12 statistical regions, each split into radius areas of 2-11 km around its towns and the "
               "rest of the region, by gender and two ad age bands (18-24, 25-40). For the first week the ad sets also "
               "used Meta's parent-of-young-child targeting (flag interests_part_of_run). Daily spend per ad set was very "
               "small, so every cell is thin. Four of the Mediterranean radius areas are in Antalya province, which "
               "is in no region's whole-region targeting.")),
    "TR-2023-07": dict(
        round="baseline",
        screen=["consent", "caregiver:child_age:0-3", "age:18-99"],
        who_qualified="aged 18 or over with a child aged 0-3; finished the short survey",
        qualify_rule="answered the follow-up permission question at the end of the survey",
        channel="messenger", languages=["tr"],
        incentive=dict(amount=35, currency="TRY", form="gift_card", when="after_followup"),
        notes=("A one-week second round of the same survey, five months after TR-2023-01, with new ad sets: 12 whole "
               "statistical regions by gender, ages 18-40. Antalya province is in no region's targeting. About a quarter "
               "of this round's labelled people first wrote after its ads stopped and are not counted.")),
}

crit = []
for rec in order:
    cs = [c for c in cells if c["rec"] == rec]
    R = REC[rec]
    gens = sorted({c["ads"]["genders"] for c in cs})
    mins = [m for (r, _), row in ROWS.items() if r == rec for m in row["minutes"]]
    rec_ = dict(rec=rec, country=R["country"], first=min(c["first"] for c in cs), last=max(c["last"] for c in cs),
                round=CRIT[rec]["round"],
                ads=dict(genders=gens, age_min=min(c["ads"]["age_min"] or 18 for c in cs),
                         age_max=max(c["ads"]["age_max"] or 65 for c in cs),
                         interests=any(c["ads"]["interests"] for c in cs)),
                screen=CRIT[rec]["screen"], who_qualified=CRIT[rec]["who_qualified"],
                qualify_rule=CRIT[rec]["qualify_rule"], qualify_point=qualify_point(rec),
                median_minutes_to_qualify=round(statistics.median(mins), 1) if mins else None,
                channel=CRIT[rec]["channel"], languages=CRIT[rec]["languages"], incentive=CRIT[rec]["incentive"],
                started=sum(c["started"] for c in cs), qualified=sum(c["qualified"] for c in cs),
                spend_usd=round(sum(c["spend_usd"] for c in cs), 2), cells=len(cs),
                notes=CRIT[rec]["notes"])
    crit.append(rec_)

# ----------------------------------------------------------------------------- write
os.makedirs(OUT, exist_ok=True)
used = {c["place"] for c in cells}
PLACES = {k: v for k, v in sorted(PLACES.items()) if k in used or any(PLACES[u].get("complement_of") == k for u in used)}
json.dump(cells, open(os.path.join(OUT, G + ".cells.json"), "w"), indent=1, ensure_ascii=False)
json.dump(crit, open(os.path.join(OUT, G + ".criteria.json"), "w"), indent=1, ensure_ascii=False)
json.dump(PLACES, open(os.path.join(OUT, G + ".places.json"), "w"), indent=1, ensure_ascii=False)
MAP["cells"] = cellmap
json.dump(MAP, open(PRIV, "w"), indent=1)

# ----------------------------------------------------------------------------- checks
print("rec          cells  spend      insights   report_spend  started  qualified  report_qual  window")
for rec in order:
    (sid,) = REC[rec]["studies"].values()
    cs = [c for c in cells if c["rec"] == rec]
    ins = sum(v for (s_, st_, d), (v, _) in spend.items() if s_ == sid and st_ in STRATA[rec])
    rp = P("rep", sid + ".tsv")
    rr = list(csv.DictReader(open(rp), delimiter="\t")) if os.path.exists(rp) else []
    rs = rq = ""
    if rr:
        d = json.loads(rr[0]["details"])
        d = {k: v for k, v in d.items() if k in STRATA[rec]}
        rs = round(sum(v.get("lifetime_spent") or 0 for v in d.values()), 2) if any("lifetime_spent" in v for v in d.values()) else "n/a"
        rq = sum(v.get("current_participants") or 0 for v in d.values())
    print(f"{rec:12} {len(cs):5d} {sum(c['spend_usd'] for c in cs):9.2f} {ins:10.2f} {rs!s:>12} "
          f"{sum(c['started'] for c in cs):8d} {sum(c['qualified'] for c in cs):9d} {rq!s:>11}  {WIN[rec]}")
print("final qualifying question per recruitment:", FINAL_ANSWERED)
print("unassigned people:", dict(UNASSIGNED))
print("rule substitutions:", {f"{a}|{c}": n for (a, b, c), n in RULE_RENAMED.items()})
print("pins not within 5 km of a named place:", {k: v["far"] for k, v in PINCHECK.items() if v["far"]})
print("pin admin-1 units:", {k: v["units"] for k, v in PINCHECK.items()})
bad = [c["cell"] for c in cells if c["place"] not in PLACES]
assert not bad, bad
