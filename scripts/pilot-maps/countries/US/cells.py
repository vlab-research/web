#!/usr/bin/env python3
"""Group US-EU (United States, Ireland, Germany): the cell table, per notes/cells-schema.md.

    python3 cells.py            # build from raw/ pulls already on disk
    python3 cells.py --fetch    # re-pull raw/ from vprod (SELECT only), then build

Writes (tracked, neutral ids only):
    scripts/data/cells/US-EU.cells.json      one row per ad set (cell) per recruitment
    scripts/data/cells/US-EU.criteria.json   one record per recruitment, plus "excluded" records
    scripts/data/cells/US-EU.places.json     place key -> geometry
and (gitignored) scripts/pilot-maps/private/US-EU.map.json, whose "recruitments", "md_alias" and
"excluded" sections are this script's INPUT (recruitment id -> study slugs, ids, Fly survey names)
and whose "cells" and "places_private" sections it writes. Slugs, study ids, stratum ids and survey
names never reach a tracked file. Raw pulls go to raw/ (gitignored) and hold ad-set labels,
timestamps and the few screening answers the quota rules test; never names, phones, emails or text.
../EU-W/cells.py is a wrapper that runs this script (Ireland and Germany are built here too).

Method (country-recipe.md, "The unit is the place"):
  spend      Insights max per campaign x ad set x day, summed over campaigns and over days with
             spend > 0. Impressions: the field when present, else spend / CPM x 1000.
  cell       ad sets of one recruitment with the same labels and the same targeting are one cell
             (a stratum renamed or split mid-run keeps its people; the split ad sets are listed
             in the private map).
  started    a person's FIRST Fly response carrying ad metadata, inside the recruitment's spend
             window (1 day before to 3 days after), whose labels match a cell. Ties between cells
             with the same labels: the creative, then the ad set spending that day or the day
             before, then the more specific labels. Each person counts once per recruitment, and
             only if they had no response in the survey before the window (re-contacts are out).
  qualified  started, and past ANY of the recruitment's final quota rules (question_targeting),
             evaluated on the person's ad labels and inference_data answers. The person stays in
             the cell of the ad that brought them.
  minutes    median of (first qualifying answer - first message) over the cell's qualified people.
"""
import csv, json, os, re, subprocess, sys, collections, statistics, hashlib, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
PM = os.path.normpath(os.path.join(HERE, "..", ".."))            # scripts/pilot-maps
DATA = os.path.normpath(os.path.join(PM, "..", "data", "cells"))
PRIV = os.path.join(PM, "private", "US-EU.map.json")
RAW = os.path.join(HERE, "raw")
# GeoNames (US postal codes + cities15000) for the ZIP-code pins: GEO_DIR, else scripts/pilot-maps
# (fetch into geonames/uspostal/US.txt and geonames/cities15000.txt; both gitignored)
GEO = os.environ.get("GEO_DIR", PM)
G = "US-EU"
csv.field_size_limit(10 ** 9)
MAP = json.load(open(PRIV))
REC = MAP["recruitments"]
ALIAS = MAP.get("md_alias", {})
P = lambda *a: os.path.join(RAW, *a)


def jl(s):
    try:
        return json.loads(s)
    except json.JSONDecodeError:            # a few confs carry stray backslashes
        return json.loads(re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', s))


def tsv(name):
    return list(csv.DictReader(open(P(name)), delimiter="\t"))


# ============================================================================ fetch (read-only)
def q(sql, db="vlab"):
    assert sql.lstrip().upper().startswith(("SELECT", "WITH")), "read-only"
    return subprocess.run(["kubectl", "exec", "-n", "vprod", "gbv-cockroachdb-0", "--", "/cockroach/cockroach", "sql",
                           "--insecure", "--format=tsv", f"--database={db}", "-e", sql],
                          check=True, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL).stdout


def all_sids():
    out = {}
    for r in list(REC.values()) + MAP.get("excluded", []):
        out.update(r["studies"])
    return out


def fetch():
    os.makedirs(P("rep"), exist_ok=True)
    os.makedirs(P("starts"), exist_ok=True)
    w = lambda n, s: open(P(n), "w").write(s)
    sids = all_sids()
    IDS = ",".join(f"'{s}'" for s in sids.values())
    w("studies.tsv", q(f"SELECT id, slug FROM studies WHERE id IN ({IDS})"))
    w("all_confs.tsv", q(f"SELECT study_id, conf_type, created, conf::string AS conf FROM study_confs "
                         f"WHERE study_id IN ({IDS}) ORDER BY study_id, conf_type, created"))
    # Insights per campaign x ad set x day; temp rows are cumulative snapshots: max, never sum
    w("spend_daily.tsv", q(f"""WITH x AS (SELECT e.study_id AS sid, c.key AS camp, s.key AS strat,
        coalesce(s.value->>'date_start', e.period_start::date::string) AS d,
        max((s.value->>'spend')::float8) AS spend, max((s.value->>'impressions')::float8) AS imp,
        max((s.value->>'cpm')::float8) AS cpm
      FROM recruitment_data_events e, jsonb_each(e.data) AS c, jsonb_each(c.value) AS s
      WHERE e.study_id IN ({IDS}) AND jsonb_typeof(c.value)='object' AND jsonb_typeof(s.value)='object'
        AND s.value->>'spend' IS NOT NULL GROUP BY 1,2,3,4)
      SELECT * FROM x WHERE spend > 0 ORDER BY 1,2,3,4"""))
    w("shared_camps.tsv", q(f"""SELECT c.key AS camp, array_agg(DISTINCT e.study_id::string) AS sids
      FROM recruitment_data_events e, jsonb_each(e.data) AS c WHERE jsonb_typeof(c.value)='object'
        AND c.key IN (SELECT DISTINCT c2.key FROM recruitment_data_events e2, jsonb_each(e2.data) c2
                      WHERE e2.study_id IN ({IDS}))
      GROUP BY 1 HAVING count(DISTINCT e.study_id) > 1"""))
    for slug, sid in sids.items():   # one at a time: a correlated max() over adopt_reports hangs
        w(os.path.join("rep", slug + ".tsv"),
          q(f"SELECT created, details::string AS details FROM adopt_reports WHERE study_id='{sid}' "
            f"AND report_type='FACEBOOK_ADOPT' ORDER BY created DESC LIMIT 1"))
    surveys = sorted({s for r in REC.values() for s in r["surveys"]})
    SV = ",".join("'" + s.replace("'", "''") + "'" for s in surveys)
    w("forms.tsv", q(f"SELECT survey_name, shortcode, created, form_json::string FROM surveys "
                     f"WHERE survey_name IN ({SV}) ORDER BY 1,2,3", db="chatroach"))
    load_confs()
    # Fly: per survey, each person's first response carrying ad metadata (labels only), and first
    # response of any kind. No answer values are read.
    for sv in surveys:
        keys = sorted({k for rid, r in REC.items() if sv in r["surveys"] for sid in r["studies"].values()
                       for st in strata_all(sid).values() for k in st["meta"]} | {"creative"})
        cols = ", ".join(f"metadata->>'{k}' AS \"{k}\"" for k in keys)
        sub = f"surveyid IN (SELECT id FROM surveys WHERE survey_name='{sv.replace(chr(39), chr(39) * 2)}')"
        out = q(f"""WITH f AS (SELECT userid, min(timestamp) AS t_any FROM responses WHERE {sub} GROUP BY 1),
            m AS (SELECT DISTINCT ON (userid) userid, timestamp AS t_md, shortcode, {cols}
                  FROM responses WHERE {sub} AND metadata ? 'creative' ORDER BY userid, timestamp)
            SELECT f.userid, f.t_any, m.* FROM f LEFT JOIN m ON m.userid = f.userid""", db="chatroach")
        w(os.path.join("starts", re.sub(r"\W+", "_", sv) + ".tsv"), out)
        print("fetched starts", sv, out.count("\n") - 1)
    fetch_inf()
    print("fetched")


def fetch_inf():
    # inference_data: timestamps for every variable a final quota rule tests; values only for the
    # screening answers a rule compares (never free text, names, phones or emails).
    load_confs()
    parts = []
    for rid, r in REC.items():
        for slug, sid in r["studies"].items():
            ans, cmp_ = rule_vars_final(sid)
            src = var_sources(sid)
            need = sorted({v for v in ans | cmp_ if src.get(v, ("variable",))[0] == "variable"})
            if not need:
                continue
            # a value is kept only when it equals one of the constants a rule compares it with
            # (e.g. "A", "Female"): anything else, typed text included, is blanked in the query
            consts = rule_constants(sid)
            cases = " ".join(
                f"WHEN variable='{v}' AND value::string IN ({','.join(chr(39) + json.dumps(c) + chr(39) for c in sorted(cs))}) "
                f"THEN value::string" for v, cs in sorted(consts.items())
                if src.get(v, ("variable",))[0] == "variable")
            NL = ",".join(f"'{v}'" for v in need)
            parts.append(f"SELECT study_id::string AS sid, user_id, variable, "
                         f"CASE {cases or 'WHEN false THEN NULL'} ELSE '' END AS value, timestamp "
                         f"FROM inference_data WHERE study_id='{sid}' AND variable IN ({NL})")
    open(P("inf.tsv"), "w").write(q(" UNION ALL ".join(parts)))


# ============================================================================ configs
H = collections.defaultdict(list)
SLUG = {}


def load_confs():
    H.clear()
    for r in tsv("studies.tsv"):
        SLUG[r["id"]] = r["slug"]
    for r in tsv("all_confs.tsv"):
        H[(r["study_id"], r["conf_type"])].append((r["created"], jl(r["conf"])))


def latest(sid, t):
    v = H.get((sid, t))
    return v[-1][1] if v else None


def strata_all(sid):
    """every stratum id ever configured; the last definition seen wins"""
    st = {}
    for created, conf in H.get((sid, "strata"), []):
        for s in conf:
            ft = s.get("facebook_targeting") or {}
            kinds = {k for blk in (ft.get("flexible_spec") or []) for k in blk}
            prev = st.get(s["id"])
            st[s["id"]] = dict(meta={k: str(v) for k, v in (s.get("metadata") or {}).items()}, ft=ft,
                               creatives=set(s.get("creatives") or []), created=created,
                               rule=s.get("question_targeting"),
                               kinds_all=(prev["kinds_all"] if prev else set()) | kinds,
                               changed=bool(prev) and (prev["changed"] or prev["kinds_now"] != kinds),
                               kinds_now=kinds)
    return st


def var_sources(sid):
    """rule variable name -> ('metadata', key) | ('variable', name)"""
    out = {}
    inf = latest(sid, "inference_data") or {}
    for name, src in (inf.get("data_sources") or {}).items():
        for e in (src if isinstance(src, list) else src.get("extraction_confs", [])):
            out[e["name"]] = (e["location"], e["key"]) if e["location"] == "metadata" else ("variable", e["name"])
    return out


def walk(q_, f):
    if not q_:
        return
    if q_.get("op") in ("and", "or"):
        for v in q_["vars"]:
            walk(v, f)
    else:
        f(q_)


def rule_vars_final(sid):
    ans, cmp_ = set(), set()

    def f(x):
        v = x["vars"][0]["value"]
        (ans if x["op"] == "answered" else cmp_).add(v)
    for s in latest(sid, "strata") or []:
        walk(s.get("question_targeting"), f)
    return ans, cmp_


def rule_constants(sid):
    out = collections.defaultdict(set)

    def f(x):
        if x["op"] != "answered":
            out[x["vars"][0]["value"]].add(str(x["vars"][1]["value"]))
    for s in latest(sid, "strata") or []:
        walk(s.get("question_targeting"), f)
    return out


def ev(q_, get):
    """evaluate a question_targeting tree; get(var) -> (value, ts) or None"""
    op = q_.get("op")
    if op == "and":
        return all(ev(v, get) for v in q_["vars"])
    if op == "or":
        return any(ev(v, get) for v in q_["vars"])
    var = q_["vars"][0]["value"]
    got = get(var)
    if op == "answered":
        return got is not None
    if got is None:
        return False
    val, c = got[0], q_["vars"][1]["value"]
    if op == "equal":
        return str(val) == str(c)
    if op == "not_equal":
        return str(val) != str(c)
    try:
        if op == "greater_than":
            return float(val) > float(c)
        if op == "less_than":
            return float(val) < float(c)
    except (TypeError, ValueError):
        return False
    raise ValueError(op)


def answered_vars(q_):
    out = []
    walk(q_, lambda x: out.append(x["vars"][0]["value"]) if x["op"] == "answered" else None)
    return out


# ============================================================================ geometry
def geo_key(g):
    """canonical, comparable description of one geo_locations object"""
    if not g:
        return None
    d = {}
    for k, v in g.items():
        if k == "location_types":
            continue
        if k == "countries":
            d[k] = sorted(v)
        elif k == "regions":
            d[k] = sorted(x["name"] for x in v)
        elif k in ("medium_geo_areas", "zips", "location_cluster_ids"):
            d[k] = sorted(str(x.get("key")) for x in v)
        elif k == "cities":
            d[k] = sorted((x.get("key"), x.get("name"), x.get("radius"), x.get("distance_unit")) for x in v)
        elif k == "custom_locations":
            d[k] = sorted((round(x["latitude"], 4), round(x["longitude"], 4), x.get("radius"), x.get("distance_unit")) for x in v)
        else:
            d[k] = json.dumps(v, sort_keys=True)
    return d


def targ_sig(ft):
    fs = ft.get("flexible_spec")
    return json.dumps(dict(geo=geo_key(ft.get("geo_locations")), ex=geo_key(ft.get("excluded_geo_locations")),
                           g=ft.get("genders"), a=(ft.get("age_min"), ft.get("age_max")), fs=fs), sort_keys=True)


def interests_of(ft):
    fs = ft.get("flexible_spec") or []
    kinds = sorted({k for blk in fs for k in blk})
    return kinds


# ============================================================================ build
def day(ts):
    return ts[:10]


def dshift(d, n):
    return (dt.date.fromisoformat(d) + dt.timedelta(days=n)).isoformat()


def median(xs):
    return round(statistics.median(xs), 2) if xs else None


def build():
    load_confs()
    sid2rec = {sid: rid for rid, r in REC.items() for sid in r["studies"].values()}
    shared = {r["camp"]: r["sids"].strip("{}").split(",") for r in tsv("shared_camps.tsv")}
    bad_shared = {c: s for c, s in shared.items() if any(x in sid2rec for x in s)}
    assert not bad_shared, f"campaigns shared across studies: {bad_shared}"

    # ---------------------------------------------------------------- spend
    spend = collections.defaultdict(float)     # (rid, sid, strat, d) -> usd (summed over campaigns)
    imp = collections.defaultdict(float)
    for r in tsv("spend_daily.tsv"):
        rid = sid2rec.get(r["sid"])
        if rid is None:
            continue
        v = float(r["spend"])
        k = (rid, r["sid"], r["strat"], r["d"])
        spend[k] += v
        if r["imp"] not in ("", "NULL"):
            imp[k] += float(r["imp"])
        elif r["cpm"] not in ("", "NULL") and float(r["cpm"]) > 0:
            imp[k] += 1000 * v / float(r["cpm"])
    win = {}
    for (rid, sid, strat, d) in spend:
        lo, hi = win.get(rid, (d, d))
        win[rid] = (min(lo, d), max(hi, d))

    # ---------------------------------------------------------------- cells
    cells = {}            # (rid, cellsig) -> dict
    strat2cell = {}       # (rid, sid, strat) -> cellsig
    for rid, r in REC.items():
        al = ALIAS.get(rid, {})
        for slug, sid in r["studies"].items():
            for stid, s in strata_all(sid).items():
                meta = {k: al.get(k, {}).get(v, v) for k, v in s["meta"].items()}
                sig = json.dumps([sorted(meta.items()), targ_sig(s["ft"])], sort_keys=True)
                c = cells.setdefault((rid, sig), dict(rid=rid, meta=meta, ft=s["ft"], strata=set(), studies=set(),
                                                      creatives=set(), days=collections.defaultdict(float),
                                                      imp=0.0, people=[], unmatched_spend=0.0))
                c["strata"].add(stid)
                c["kinds_all"] = c.get("kinds_all", set()) | s["kinds_all"]
                c["changed"] = c.get("changed", False) or s["changed"]
                c["studies"].add(slug)
                c["creatives"] |= s["creatives"]
                strat2cell[(rid, sid, stid)] = sig
    unmatched = collections.defaultdict(float)
    for (rid, sid, strat, d), v in spend.items():
        sig = strat2cell.get((rid, sid, strat))
        if sig is None:
            unmatched[(rid, strat)] += v
            continue
        c = cells[(rid, sig)]
        c["days"][d] += v
        c["imp"] += imp.get((rid, sid, strat, d), 0.0)
    live = collections.defaultdict(set)   # (rid, sig) -> spend days
    for (rid, sig), c in cells.items():
        live[(rid, sig)] = {d for d, v in c["days"].items() if v > 0}

    # ---------------------------------------------------------------- people
    inf = collections.defaultdict(dict)   # (rid, user) -> var -> (value, ts)
    for r in tsv("inf.tsv"):
        rid = sid2rec[r["sid"]]
        val = json.loads(r["value"]) if r["value"] not in ("", "NULL") else None
        cur = inf[(rid, r["user_id"])].get(r["variable"])
        if cur is None or r["timestamp"] < cur[1]:
            inf[(rid, r["user_id"])][r["variable"]] = (val, r["timestamp"][:19])
    src_of = {rid: {} for rid in REC}
    rules = {rid: [] for rid in REC}
    for rid, r in REC.items():
        for sid in r["studies"].values():
            src_of[rid].update(var_sources(sid))
            for s in latest(sid, "strata") or []:
                if float(s.get("quota") or 0) > 0:      # a quota-0 group is not a target: its rule is not a qualification
                    rules[rid].append(s.get("question_targeting"))

    diag = collections.defaultdict(collections.Counter)
    for rid, r in REC.items():
        lo, hi = win[rid]
        wlo, whi = dshift(lo, -1), dshift(hi, 3)
        al = ALIAS.get(rid, {})
        rcells = [(sig, c) for (rr, sig), c in cells.items() if rr == rid]
        rcre = set().union(*(c["creatives"] for _, c in rcells))
        for sid in r["studies"].values():
            for _, conf in H.get((sid, "creatives"), []):
                rcre |= {x.get("name") for x in conf}
        seen = set()
        for sv in r["surveys"]:
            for p in tsv(os.path.join("starts", re.sub(r"\W+", "_", sv) + ".tsv")):
                u = p["userid"]
                if u in seen:
                    continue
                if p["t_md"] in ("", "NULL"):
                    continue
                t0 = p["t_md"][:19]
                if not (wlo <= day(t0) <= whi):
                    continue
                seen.add(u)
                if day(p["t_any"]) < wlo:
                    diag[rid]["earlier respondent (re-contact), left out"] += 1
                    continue
                md = {k: al.get(k, {}).get(v, v) for k, v in p.items()
                      if k not in ("userid", "t_any", "t_md", "shortcode", "creative") and v not in ("", "NULL")}
                cands = [(sig, c) for sig, c in rcells if c["meta"] and all(md.get(k) == v for k, v in c["meta"].items())]
                if p.get("creative") and p["creative"] not in rcre:
                    # the survey was shared with ads outside this recruitment (another campaign's creative)
                    diag[rid]["creative from another campaign, left out"] += 1
                    continue
                if len(cands) > 1:
                    # labels only a more specific ad set writes identify that ad set
                    mx = max(len(x[1]["meta"]) for x in cands)
                    cands = [x for x in cands if len(x[1]["meta"]) == mx]
                if len(cands) > 1 and p.get("creative"):
                    by_cr = [x for x in cands if p["creative"] in x[1]["creatives"]]
                    if by_cr:
                        cands = by_cr
                if len(cands) > 1:
                    # same labels, different targeting: the ad set spending on the person's first day or
                    # the day before; failing that, over the week before; failing that, over the run
                    d0 = day(t0)
                    for span in (2, 8, None):
                        amt = (lambda x, span=span: sum(v for d, v in x[1]["days"].items()
                                                        if span is None or dshift(d0, -span + 1) <= d <= d0))
                        top = max(amt(x) for x in cands)
                        if top > 0:
                            cands = [x for x in cands if amt(x) == top][:1]
                            diag[rid]["same labels: placed by spend" + ("" if span == 2 else f" (window {span or 'run'})")] += 1
                            cands[0][1]["tie_placed"] = cands[0][1].get("tie_placed", 0) + 1
                            break
                if len(cands) > 1:
                    diag[rid]["ambiguous between cells"] += 1
                    continue
                if not cands:
                    diag[rid]["labels match no cell"] += 1
                    continue
                sig, c = cands[0]
                vals = inf.get((rid, u), {})

                def get(var, md=md, vals=vals):
                    s_ = src_of[rid].get(var)
                    if var.startswith("md:"):
                        k = var[3:]
                        return (md[k], t0) if k in md else None
                    if s_ and s_[0] == "metadata":
                        return (md[s_[1]], t0) if s_[1] in md else None
                    return vals.get(var)
                ok = [q_ for q_ in rules[rid] if q_ and ev(q_, get)]
                mins = None
                if ok:
                    ts = [vals[v][1] for q_ in ok for v in answered_vars(q_) if v in vals]
                    if ts:
                        mins = (dt.datetime.fromisoformat(min(ts)) - dt.datetime.fromisoformat(t0)).total_seconds() / 60
                c["people"].append((u, t0, bool(ok), mins))
                diag[rid]["started"] += 1
    return cells, win, unmatched, diag


# ============================================================================ outputs
POSTAL = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
          "Connecticut": "CT", "Delaware": "DE", "Washington D. C.": "DC", "District of Columbia": "DC", "Florida": "FL",
          "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
          "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
          "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
          "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
          "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
          "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
          "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}
CNAME = {"US": "United States", "IE": "Ireland", "DE": "Germany"}
h8 = lambda x: hashlib.sha1(json.dumps(x, sort_keys=True).encode()).hexdigest()[:8]


def zip_pins(zips, city_names):
    """GeoNames postal-code centroids for Meta ZIP targets; GeoNames populated places for Meta cities"""
    pc = {}
    for line in open(os.path.join(GEO, "geonames", "uspostal", "US.txt"), encoding="utf8"):
        r = line.rstrip("\n").split("\t")
        pc[r[1]] = (float(r[9]), float(r[10]), r[2], r[4])
    ct = {}
    for line in open(os.path.join(GEO, "geonames", "cities15000.txt"), encoding="utf8"):
        r = line.rstrip("\n").split("\t")
        if r[8] == "US":
            ct.setdefault((r[1], r[10]), (float(r[4]), float(r[5])))
    pins, checks = [], []
    for z in zips:
        lat, lon, name, st = pc[z]
        pins.append([round(lat, 4), round(lon, 4), None])
        checks.append(f"ZIP {z}: GeoNames postal centroid ({name}, {st})")
    for name, st in city_names:
        lat, lon = ct[(name, st)]
        pins.append([round(lat, 4), round(lon, 4), None])
        checks.append(f"city {name}: GeoNames populated place, {st}")
    return pins, checks


def place_of(rid, cc, ft, cluster_n):
    """(place key, place record, private note) from the ad set's targeting. Keys are geometry."""
    g, ex = ft.get("geo_locations") or {}, ft.get("excluded_geo_locations") or {}
    kinds = set(g) - {"location_types"}
    if kinds == {"countries"} and not ex:
        (c,) = g["countries"]
        return f"{c}:country", dict(country=c, type="country", label=f"{CNAME[c]}, whole country"), None
    if kinds == {"regions"} and not ex:
        names = sorted(x["name"] for x in g["regions"])
        if cc == "US":
            codes = sorted(POSTAL[n] for n in names)
            if len(codes) == 1:
                return (f"US:region:{names[0]}", dict(country="US", type="region", label=f"{names[0]} (whole state)",
                                                      regions=names), None)
            return (f"US:regions:{'+'.join(codes)}",
                    dict(country="US", type="region", label=f"{len(codes)} whole states: {', '.join(codes)}",
                         regions=names), None)
        return (f"{cc}:region:{'+'.join(names)}", dict(country=cc, type="region", label=" + ".join(names) + " (whole state)",
                                                       regions=names), None)
    if kinds == {"medium_geo_areas"} and not ex:
        areas = sorted(x["name"] for x in g["medium_geo_areas"])
        reg = sorted({x["region"] for x in g["medium_geo_areas"]})
        k = f"US:counties:{'+'.join(reg)}-{len(areas)}-{h8(areas)}"
        return k, dict(country="US", type="subregion_set", label=f"{len(areas)} counties in {', '.join(reg)}",
                       region=reg, areas=areas,
                       note="Meta 'medium geo areas' (US counties), each targeted whole"), None
    if kinds == {"regions"} and set(ex) - {"location_types"} == {"medium_geo_areas"}:
        names = sorted(x["name"] for x in g["regions"])
        areas = sorted(x["name"] for x in ex["medium_geo_areas"])
        reg = sorted({x["region"] for x in ex["medium_geo_areas"]})
        comp = f"US:counties:{'+'.join(reg)}-{len(areas)}-{h8(areas)}"
        return (f"US:region-minus:{'+'.join(names)}-{len(areas)}-{h8(areas)}",
                dict(country="US", type="region_minus", label=f"{', '.join(names)} outside the {len(areas)} counties",
                     regions=names, excluded_areas=areas, complement_of=comp), None)
    if kinds == {"location_cluster_ids"} and not ex:
        key = str(g["location_cluster_ids"][0]["key"])
        n = cluster_n.setdefault(key, len(cluster_n) + 1)
        return (f"US:cluster:{key}", dict(country="US", type="location_cluster",
                                          label=f"US location cluster {n} (a saved Meta set of ZIP codes; contents not recorded)",
                                          note="geometry not stored with the study; cannot be mapped"), None)
    if kinds <= {"zips", "cities"} and not ex:
        zips = sorted(x["name"] for x in g.get("zips", []))
        cities = sorted((x["name"], "CA" if x.get("region") == "California" else x.get("region")) for x in g.get("cities", []))
        radius = {x.get("radius") for x in g.get("cities", [])}
        assert radius <= {None}, radius
        pins, checks = zip_pins(zips, cities)
        k = f"US:zips:{len(zips)}+{len(cities)}city-{h8([zips, cities])}"
        return k, dict(country="US", type="zip_set",
                       label=f"{len(zips)} ZIP codes and {len(cities)} city in California (Meta city, no radius set)",
                       pins=pins, zips=zips, cities=[c[0] for c in cities],
                       note="pins are GeoNames centroids of the ZIP codes and the city, radius null: Meta targets the "
                            "whole ZIP area and its own city area", pin_checks=checks), None
    raise SystemExit(f"{rid}: unhandled geometry {json.dumps(g)[:200]} / {json.dumps(ex)[:200]}")


def ads_of(ft):
    gd = ft.get("genders")
    genders = "women" if gd == [2] else "men" if gd == [1] else "all"
    fs = ft.get("flexible_spec") or []
    kinds = sorted({k for blk in fs for k in blk})
    return dict(genders=genders, age_min=ft.get("age_min"), age_max=ft.get("age_max"), interests=bool(kinds)), kinds


FLAG_OF_KIND = {"interests": "interest_targeting", "behaviors": "behaviour_targeting",
                "education_statuses": "education_targeting", "education_majors": "education_major_targeting",
                "education_schools": "education_major_targeting", "family_statuses": "parent_targeting",
                "work_positions": "job_targeting", "work_employers": "job_targeting", "industries": "job_targeting",
                "income": "income_targeting"}

# ---------------------------------------------------------------- criteria, read from the forms (Fly)
# and the quota rules. Plain words, no topics. qualify_point counts fields on the main path of the
# entry form as the respondent sees them (statements included) unless the note says otherwise.
USD = lambda a, form: dict(amount=a, currency="USD", form=form)
CRIT = {
    "US-2023-02": dict(
        round="cross-section", channel="messenger", languages=["en"],
        incentive=USD(5.0, "gift card"),
        screen=["occupation:health_worker", "consent"],
        who_qualified="works in one of four clinical health care roles; reached the end of the first block of questions",
        qualify_rule="said they work in one of four clinical roles, and answered a question about two-thirds of the way through",
        qualify_point={"question": 55, "of": 68},
        notes="Final quota rule: health care workers only. Until mid-March a second group (parents of children under 18, "
              "reached by the same ads) was also a quota target; under the final rule they do not qualify, so most "
              "people who started did not qualify. Early ad sets (Feb-Apr 7) targeted three age bands x gender with "
              "profession and interest targeting; the last 12 days ran one whole-country ad set with no interests. "
              "qualify_point = field position in the form, which includes branches a respondent may skip. "
              "The adopt report counts people from other campaigns that shared the survey; recounted here."),
    "US-2023-05": dict(
        round="screener", channel="messenger", languages=["en"],
        incentive=USD(10.0, "gift card"),
        screen=["age:18-34", "lives_in:US", "consent", "gave_phone"],
        who_qualified="aged 18-34, living in the United States, gave name, phone and email, and opened the linked enrolment survey",
        qualify_rule="opened the external enrolment survey from the last message (its id returned to the platform)",
        qualify_point={"question": 17, "of": 17},
        notes="The qualifying event happens in an external survey opened from the 17th and last message; the screener "
              "asks a specific behaviour but does not screen on it under the final rule. Incentive: $10 for the first of "
              "five surveys. Minutes to qualify run to the external survey's own record, which is written when that survey syncs (hours later), so they overstate the time. 40 ad sets in the first two weeks (same states and gender, split by answers) are folded into "
              "the 10 cells they fed."),
    "US-2023-08": dict(
        round="baseline", channel="messenger", languages=["en"],
        incentive=USD(5.0, "gift card"),
        screen=["lives_in:US", "age:18-24", "gender:men_or_women", "consent"],
        who_qualified="aged 18-24, living in the United States, answered man or woman, and completed a linked external survey",
        qualify_rule="returned from the external survey to the payment message",
        qualify_point=None,
        notes="Three sibling configurations fed one survey (a main run, a two-week creative test and a later top-up); "
              "one recruitment, each person once. A 7-question screener in Messenger, then an external survey of unknown "
              "length, then a payment message that is the qualifying point. Gender was screened by answer (non-binary "
              "and other answers do not qualify); people stay in the cell of the ad that brought them. The adopt reports "
              "do not reconcile: one sibling's latest report is stale with zero spend, another covers part of the run."),
    "US-2024-01a": dict(
        round="pilot", channel="messenger", languages=["en"],
        incentive=dict(amount=None, currency="USD", form="lottery"),
        screen=["lives_in:US", "consent", "age:18-80"],
        who_qualified="living in the United States, aged 18-80, agreed to take part, reached a demographic question early in the survey",
        qualify_rule="answered the education question (field 24 of 29)",
        qualify_point={"question": 24, "of": 29},
        notes="Ten days. The 'young'/'old' ad sets carried the same Meta age range (18-65) and differ only in their labels "
              "and budgets; the cells keep them apart as the recruitment did."),
    "US-2024-04": dict(
        round="cross-section", channel="messenger", languages=["en", "es"],
        incentive=USD(5.0, "gift card"),
        screen=["consent", "lives_in:US", "age:18-100"],
        who_qualified="adults living in the United States who finished the survey",
        qualify_rule="answered the second-to-last question",
        qualify_point={"question": 53, "of": 55},
        notes="72 cells: 3 location clusters x gender x 4 age bands x 3 education levels (Meta education targeting). "
              "A language choice (English or Spanish) comes first; counted as field 1. The location clusters are saved "
              "Meta ZIP-code sets whose contents are not stored; they cannot be mapped."),
    "US-2024-05a": dict(
        round="screener", channel="messenger", languages=["en", "es"],
        incentive=dict(amount=100.0, currency="USD", form="prize draw"),
        screen=["lives_in:California", "works_or_studies_in:California", "age:18-99"],
        who_qualified="aged 18+, living and working or studying in California, answered the last screening question",
        qualify_rule="answered the race and ethnicity question (the last screening question)",
        qualify_point={"question": 6, "of": 7},
        notes="A short eligibility screener that links to an external survey; qualified = passed the screener. Ad sets "
              "targeted California, split by gender and by Meta interests chosen to reach particular groups."),
    "US-2024-05b": dict(
        round="screener", channel="messenger", languages=["en", "es"],
        incentive=dict(amount=100.0, currency="USD", form="prize draw"),
        screen=["lives_in:California", "works_or_studies_in:California", "age:18-99"],
        who_qualified="aged 18+, living and working or studying in California, answered the last screening question",
        qualify_rule="answered the race and ethnicity question (the last screening question)",
        qualify_point={"question": 6, "of": 7},
        notes="The same screener as US-2024-05a, re-run with three narrower interest-targeted ad sets (all genders)."),
    "US-2024-08a": dict(
        round="screener", channel="messenger", languages=["en", "es"],
        incentive=dict(amount=100.0, currency="USD", form="prize draw"),
        screen=["lives_in:California", "works_or_studies_in:California", "age:18-99"],
        who_qualified="aged 18+, living and working or studying in California, answered the last screening question",
        qualify_rule="answered the race and ethnicity question",
        qualify_point={"question": 6, "of": 8},
        notes="Three days in nine ZIP codes and one city; very small."),
    "US-2024-08b": dict(
        round="cross-section", channel="messenger", languages=["en", "es"],
        incentive=USD(5.0, "gift card"),
        screen=["consent", "lives_in:US", "age:18-100"],
        who_qualified="adults living in the United States who finished the survey",
        qualify_rule="answered the second-to-last question",
        qualify_point={"question": 53, "of": 55},
        notes="A second round of US-2024-04's design, same 72 cells, three weeks later."),
    "US-2025-01": dict(
        round="baseline", channel="messenger", languages=["en", "so"],
        incentive=USD(5.0, "gift card"),
        screen=["consent"],
        who_qualified="adults in Minnesota who agreed to take part and reached a question near the end of the survey",
        qualify_rule="answered a question 74 fields into an 82-field survey",
        qualify_point={"question": 75, "of": 83},
        notes="A language choice (English or Somali) comes first, counted as field 1. First six days: 8 ad sets split "
              "by two Meta age bands; then 4 ad sets without an age split. Age and county are asked but do not screen."),
    "US-2025-06": dict(
        round="screener", channel="messenger", languages=["en"],
        incentive=None,
        screen=[],
        who_qualified="anyone who opened the conversation (the eligibility screen is on an external site)",
        qualify_rule="received the first message",
        qualify_point={"question": 1, "of": 4},
        notes="The quota rule is met at the first message, so qualified = started; the real screen happens on an external "
              "site whose results are not recorded here. Ads targeted people on Android phones (a Meta device "
              "behaviour), aged 18-25."),
    "US-2025-08": dict(
        round="cross-section", channel="messenger", languages=["en"],
        incentive=USD(5.0, "gift card"),
        screen=["consent"],
        who_qualified="adults in Minnesota who agreed to take part and reached the last question",
        qualify_rule="answered the last question",
        qualify_point={"question": 56, "of": 57},
        notes="A fresh cross-section in the same places as US-2025-01, seven months later; earlier respondents are left "
              "out. The quota rule moved to the last question four days in; recounted under the final rule. The count "
              "here is 11 above the adopt report."),
    "US-2025-12": dict(
        round="pilot", channel="messenger", languages=["en"],
        incentive=USD(5.0, "gift card"),
        screen=["age:18-99", "consent"],
        who_qualified="adults who agreed to take part and reached a question near the end",
        qualify_rule="answered a question 50 fields into a 54-field survey",
        qualify_point={"question": 50, "of": 54},
        notes="Three days; a pilot."),
    "IE-2024-04": dict(
        round="pilot", channel="messenger", languages=["en"],
        incentive=dict(amount=None, currency="EUR", form="voucher (3 or 5 by arm)"),
        screen=["consent", "attention_check"],
        who_qualified="agreed to take part, watched a short video without problems, and reached the last question block",
        qualify_rule="answered a question 79 fields into an 87-field survey (fields include branches not all respondents see)",
        qualify_point={"question": 79, "of": 87},
        notes="Two arms (a smaller and a larger voucher) run as two campaigns over the same 8 ad sets; pooled into one "
              "cell per ad set. Nobody who started in the window reached the qualifying question. Ad account currency "
              "not verified (the account is used only for Ireland; CPM $8-10 is plausible in USD or EUR)."),
    "IE-2024-06": dict(
        round="cross-section", channel="messenger", languages=["en"],
        incentive=dict(amount=3.0, currency="EUR", form="voucher"),
        screen=["consent", "attention_check"],
        who_qualified="agreed to take part, watched a short video without problems, and reached the last question block",
        qualify_rule="answered a question 79 fields into an 87-field survey (fields include branches not all respondents see)",
        qualify_point={"question": 79, "of": 87},
        notes="Ad account currency not verified (see IE-2024-04). The screen-out after the video is an attention/technical check."),
    "DE-2024-02": dict(
        round="baseline", channel="messenger", languages=["de"],
        incentive=dict(amount=3.0, currency="EUR", form="gift voucher"),
        screen=["consent"],
        who_qualified="completed a linked external survey and returned to the platform",
        qualify_rule="returned from the external survey to the voucher message",
        qualify_point=None,
        notes="The recruiting (first) wave of a panel: a two-message invitation in Messenger, then an external survey. 14 people "
              "started inside the ad window and 3 qualified for $591 of ads: the external survey lost almost everyone. "
              "Very thin; kept as recorded."),
}


def write_outputs(cells, win, unmatched, diag):
    os.makedirs(DATA, exist_ok=True)
    rows, places, crit, priv_cells, cluster_n = [], {}, [], {}, {}
    rep_check = {}
    for rid, r in REC.items():
        cc = r["country"]
        rc = sorted(((sig, c) for (rr, sig), c in cells.items() if rr == rid and (c["days"] or c["people"])),
                    key=lambda x: (json.dumps(geo_key(x[1]["ft"].get("geo_locations")), sort_keys=True),
                                   ads_of(x[1]["ft"])[0]["genders"], str(ads_of(x[1]["ft"])[0]["age_min"]),
                                   sorted(x[1]["meta"].items())))
        tot_sp = tot_st = tot_q = 0
        allmins, genders, amin, amax, anyint = [], set(), [], [], False
        for n, (sig, c) in enumerate(rc, 1):
            cid = f"{rid}/{n:02d}"
            pk, prec, _ = place_of(rid, cc, c["ft"], cluster_n)
            if pk in places:
                assert {k: v for k, v in places[pk].items() if k != "label"} == {k: v for k, v in prec.items() if k != "label"}, pk
            places[pk] = prec
            ads, kinds = ads_of(c["ft"])
            kinds = sorted(set(kinds) | c.get("kinds_all", set()))   # any version the ad set ran under
            ads["interests"] = bool(kinds)
            days = sorted(d for d, v in c["days"].items() if v > 0)
            sp = round(sum(c["days"].values()), 2)
            ppl = c["people"]
            q = [p for p in ppl if p[2]]
            mins = [p[3] for p in q if p[3] is not None and p[3] >= 0]
            flags = sorted({FLAG_OF_KIND.get(k, k + "_targeting") for k in kinds})
            if len(ppl) < 200:
                flags.append("thin")
            if len(days) == 1:
                flags.append("one_day")
            if len(c["strata"]) > 1:
                flags.append(f"merged_ad_sets:{len(c['strata'])}")
            if c.get("tie_placed"):
                flags.append(f"placed_by_spend:{c['tie_placed']}")
            if prec["type"] == "location_cluster":
                flags.append("geometry_unknown")
            if cc == "IE":
                flags.append("currency_unverified")
            if rid == "US-2024-01a":
                flags.append("age_label_not_targeted")
            if not days:
                flags.append("no_spend")
            if c.get("changed"):
                flags.append("targeting_changed")
            row = dict(rec=rid, cell=cid, country=cc, place=pk, side=None, ads=ads, person_override=None,
                       first=days[0] if days else None, last=days[-1] if days else None, spend_days=len(days),
                       spend_usd=sp, impressions=round(c["imp"]) if c["imp"] else None,
                       started=len(ppl), qualified=len(q),
                       median_daily_spend=median([c["days"][d] for d in days]),
                       median_minutes_to_qualify=median(mins), flags=flags, attribution="ad_metadata")
            rows.append(row)
            priv_cells[cid] = dict(strata=sorted(c["strata"]), studies=sorted(c["studies"]), labels=c["meta"])
            tot_sp += sp; tot_st += len(ppl); tot_q += len(q); allmins += mins
            genders.add(ads["genders"]); anyint |= ads["interests"]
            if ads["age_min"] is not None:
                amin.append(ads["age_min"]); amax.append(ads["age_max"])
        cr = CRIT[rid]
        lo, hi = win[rid]
        gl = sorted(genders)
        crit.append(dict(rec=rid, country=cc, first=lo, last=hi, round=cr["round"],
                         ads=dict(genders=gl if len(gl) > 1 else gl[0], age_min=min(amin) if amin else None,
                                  age_max=max(amax) if amax else None, interests=anyint),
                         screen=cr["screen"], who_qualified=cr["who_qualified"], qualify_rule=cr["qualify_rule"],
                         qualify_point=cr["qualify_point"], median_minutes_to_qualify=median(allmins),
                         channel=cr["channel"], languages=cr["languages"], incentive=cr["incentive"],
                         started=tot_st, qualified=tot_q, notes=cr["notes"]))
        # adopt-report reconciliation (for the report; per recruitment)
        rs = rq = 0.0
        for slug in r["studies"]:
            rr = tsv(os.path.join("rep", slug + ".tsv"))
            if rr:
                d = json.loads(rr[0]["details"])
                rs += sum(v.get("lifetime_spent") or 0 for v in d.values())
                rq += sum(v.get("current_participants") or 0 for v in d.values())
        rep_check[rid] = dict(spend=round(tot_sp, 2), report_spend=round(rs, 2), started=tot_st, qualified=tot_q,
                              report_qualified=int(rq), diag=dict(diag[rid]))
    for e in MAP.get("excluded", []):
        crit.append(dict(rec=e["rec"], country=e["country"], first=None, last=None, round="excluded", ads=None, screen=[],
                         who_qualified=None, qualify_rule=None, qualify_point=None, median_minutes_to_qualify=None,
                         channel=None, languages=[], incentive=None, started=0, qualified=0,
                         notes=e["public_reason"]))
    json.dump(rows, open(os.path.join(DATA, f"{G}.cells.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(crit, open(os.path.join(DATA, f"{G}.criteria.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(dict(sorted(places.items())), open(os.path.join(DATA, f"{G}.places.json"), "w"), indent=1, ensure_ascii=False)
    MAP["cells"] = priv_cells
    MAP["checks"] = rep_check
    json.dump(MAP, open(PRIV, "w"), indent=1)
    for rid, v in rep_check.items():
        print(f"{rid:12} spend {v['spend']:9.2f} report {v['report_spend']:9.2f} | started {v['started']:6d} "
              f"qualified {v['qualified']:5d} report {v['report_qualified']:5d}")
    print(len(rows), "cells,", len(places), "places,", len(crit), "criteria records")


def main():
    if "--fetch" in sys.argv:
        fetch()
    cells, win, unmatched, diag = build()
    assert not unmatched, unmatched
    write_outputs(cells, win, unmatched, diag)


if __name__ == "__main__":
    main()
