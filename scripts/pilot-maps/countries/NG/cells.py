#!/usr/bin/env python3
"""Group NG-GH (Nigeria, Ghana): the cell table, per notes/cells-schema.md.

    python3 cells.py            # build from raw/ pulls already on disk
    python3 cells.py --fetch    # re-pull NG/raw and GH/raw from vprod (SELECT only), then build

Writes (tracked, neutral ids only):
    scripts/data/cells/NG-GH.cells.json      one row per ad set per recruitment
    scripts/data/cells/NG-GH.criteria.json   one record per recruitment, plus "excluded" records
    scripts/data/cells/NG-GH.places.json     place key -> geometry
and (gitignored) scripts/pilot-maps/private/NG-GH.map.json, whose "recruitments" and "excluded"
sections are this script's INPUT (recruitment id -> study slugs and ids) and whose "cells" section
it writes (cell -> raw stratum id). Study slugs, ids and stratum ids never reach a tracked file.

The per-stratum evidence comes from pipeline.py (the Nigeria v7 place pipeline, unchanged in
method): spend is Insights max per campaign x stratum x day, summed over days with spend > 0;
people are assigned by the ad-set metadata on their first record inside the spend window;
qualified = past the recruitment's final quota rule, recounted from inference_data.
../GH/cells.py is a wrapper that runs this script.
"""
import csv, json, os, re, subprocess, sys, collections, math, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
PM = os.path.normpath(os.path.join(HERE, "..", ".."))            # scripts/pilot-maps
DATA = os.path.normpath(os.path.join(PM, "..", "data", "cells"))
PRIV = os.path.join(PM, "private", "NG-GH.map.json")
RAW = {"NG": os.path.join(HERE, "raw"), "GH": os.path.normpath(os.path.join(HERE, "..", "GH", "raw"))}
csv.field_size_limit(10 ** 9)
MAP = json.load(open(PRIV))
REC = MAP["recruitments"]


def jl(s):
    # cockroach's tsv writes non-ASCII as \UXXXXXXXX
    s = re.sub(r'\\U([0-9A-Fa-f]{8})', lambda m: json.dumps(chr(int(m.group(1), 16)))[1:-1], s)
    try:
        return json.loads(s)
    except json.JSONDecodeError:            # a few confs carry stray backslashes
        return json.loads(re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', s))


# ============================================================================ fetch (read-only)
def q(sql, db="vlab"):
    assert sql.lstrip().upper().startswith(("SELECT", "WITH")), "read-only"
    return subprocess.run(["kubectl", "exec", "-n", "vprod", "gbv-cockroachdb-0", "--", "/cockroach/cockroach", "sql",
                           "--insecure", "--format=tsv", f"--database={db}", "-e", sql],
                          check=True, capture_output=True, text=True, timeout=600).stdout


def fetch(cc):
    raw = RAW[cc]
    os.makedirs(os.path.join(raw, "rep"), exist_ok=True)
    w = lambda n, s: open(os.path.join(raw, n), "w").write(s)
    fam = {r["family"]: r["studies"] for r in REC.values() if r["country"] == cc}
    json.dump(fam, open(os.path.join(raw, "fam.json"), "w"), indent=1)
    sids = [s for f in fam.values() for s in f.values()]
    IDS = ",".join(f"'{s}'" for s in sids)
    w("all_confs.tsv", q(f"SELECT study_id, conf_type, created, conf::string AS conf FROM study_confs "
                         f"WHERE study_id IN ({IDS}) ORDER BY created"))
    # Insights per campaign x stratum x day. temp rows are cumulative snapshots: max, never sum.
    # impressions: the field when present, else spend / CPM x 1000. conv: Meta's conversations started.
    ins = q(f"""WITH x AS (SELECT e.study_id::string AS sid, c.key AS camp, s.key AS strat,
          coalesce(s.value->>'date_start', e.period_start::date::string) AS d,
          (s.value->>'spend')::float8 AS spend, (s.value->>'reach')::float8 AS reach,
          coalesce((s.value->>'impressions')::float8,
                   round((s.value->>'spend')::float8 * 1000 / nullif((s.value->>'cpm')::float8, 0))) AS imp,
          (s.value->>'cpm')::float8 AS cpm,
          (SELECT max((a->>'value')::float8) FROM jsonb_array_elements(
              CASE WHEN jsonb_typeof(s.value->'actions') = 'array' THEN s.value->'actions' ELSE '[]'::jsonb END) a
           WHERE a->>'action_type' = 'onsite_conversion.messaging_conversation_started_7d') AS conv
        FROM recruitment_data_events e, jsonb_each(e.data) AS c, jsonb_each(c.value) AS s
        WHERE e.study_id IN ({IDS}) AND jsonb_typeof(c.value) = 'object' AND jsonb_typeof(s.value) = 'object'
          AND s.value->>'spend' IS NOT NULL)
        SELECT sid, camp, strat, d, max(spend) AS spend, max(reach) AS reach, max(imp) AS imp, max(conv) AS conv,
               max(cpm) AS cpm FROM x GROUP BY 1, 2, 3, 4 ORDER BY 1, 4""")
    w("insights_daily.tsv", ins)
    rows = list(csv.DictReader(ins.splitlines(), delimiter="\t"))
    with open(os.path.join(raw, "spend_daily.tsv"), "w") as fh:
        fh.write("sid\tcamp\tstrat\td\tspend\n")
        for r in rows:
            if r["spend"] not in ("", "NULL") and float(r["spend"]) > 0:
                fh.write(f'{r["sid"]}\t{r["camp"]}\t{r["strat"]}\t{r["d"]}\t{r["spend"]}\n')
    w("shared_camps.tsv", q(f"""WITH mine AS (SELECT DISTINCT c.key AS camp FROM recruitment_data_events e, jsonb_each(e.data) c
          WHERE e.study_id IN ({IDS}) AND jsonb_typeof(c.value) = 'object')
        SELECT c.key AS camp, array_agg(DISTINCT e.study_id::string) FROM recruitment_data_events e, jsonb_each(e.data) c
        WHERE c.key IN (SELECT camp FROM mine) AND jsonb_typeof(c.value) = 'object'
        GROUP BY 1 HAVING count(DISTINCT e.study_id) > 1"""))
    # values are kept ONLY for ad-set metadata variables and the language choice: never answers
    H = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(raw, "all_confs.tsv")), delimiter="\t"):
        H[r["conf_type"]].append(jl(r["conf"]))
    keep, names = {"language"}, set()
    for c in H["inference_data"]:
        for src in (c.get("data_sources") or {}).values():
            keep.update(e["name"] for e in src.get("extraction_confs", []) if e["location"] == "metadata")
    for c in H["data_sources"]:
        for d in c:
            if (d.get("config") or {}).get("survey_name"):
                names.add(d["config"]["survey_name"])
    KEEP = ",".join("'" + k.replace("'", "''") + "'" for k in sorted(keep))
    w("inf.tsv", q(f"SELECT study_id, user_id, variable, CASE WHEN variable IN ({KEEP}) THEN value::string ELSE '' END AS value, "
                   f"timestamp FROM inference_data WHERE study_id IN ({IDS})"))
    NAMES = ",".join("'" + n.replace("'", "''") + "'" for n in sorted(names))
    w("user_creatives.tsv", q(f"SELECT userid, metadata->>'creative' AS cr, min(timestamp) AS t0, count(*) AS count "
                              f"FROM responses WHERE surveyid IN (SELECT id FROM surveys WHERE survey_name IN ({NAMES})) "
                              f"GROUP BY 1, 2", db="chatroach"))
    # base64, because cockroach's tsv mangles escaped quotes inside form descriptions
    w("forms.tsv", q(f"SELECT survey_name, shortcode, created, encode(convert_to(form_json::string, 'UTF8'), 'base64') AS form_b64 "
                     f"FROM surveys WHERE survey_name IN ({NAMES}) ORDER BY created", db="chatroach"))
    for f in fam.values():
        for slug, sid in f.items():
            w(os.path.join("rep", slug + ".tsv"),
              q(f"SELECT created, details::string AS details FROM adopt_reports WHERE study_id = '{sid}' "
                f"AND report_type = 'FACEBOOK_ADOPT' ORDER BY created DESC LIMIT 1"))


def people_of(cc):
    """people.tsv from pipeline.py: family, study id, stratum, user, first message, qualified, minutes."""
    out = []
    for line in open(os.path.join(RAW[cc], "people.tsv")):
        f, sid, stid, u, t0, qq, m = line.rstrip("\n").split("\t")
        out.append(dict(family=f, sid=sid, stid=stid, user=u, t0=t0, q=qq == "True", minutes=float(m) if m else None))
    return out


def confs(cc):
    H = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(RAW[cc], "all_confs.tsv")), delimiter="\t"):
        H[(r["study_id"], r["conf_type"])].append((r["created"], jl(r["conf"])))
    return H


def fetch_qpoints(cc, EV):
    """Questions answered at the qualifying point, measured on the qualified people themselves:
    the median number of distinct questions a qualified person had answered when they gave the
    qualifying answer, and within 24 hours after it. Forms branch, so counting form fields
    overstates what anyone sees; this counts what people actually answered."""
    H = confs(cc)
    ppl = people_of(cc)
    out = {}
    for rid, rec in REC.items():
        if rec["country"] != cc:
            continue
        studies = rec.get("only_studies") or list(rec["studies"])
        sids = [rec["studies"][s] for s in studies]
        users = sorted({p["user"] for p in ppl if p["family"] == rec["family"] and p["sid"] in sids and p["q"]})
        rows = [r for r in EV[cc]["rows"] if r["family"] == rec["family"] and r["sid"] in sids]
        if not users or not rows:
            continue
        names, refs = set(), set()
        for sid in sids:
            for _, c in H.get((sid, "data_sources"), []):
                names.update(d["config"]["survey_name"] for d in c if (d.get("config") or {}).get("survey_name"))
            keymap = {}
            for _, c in H.get((sid, "inference_data"), []):
                for src in (c.get("data_sources") or {}).values():
                    keymap.update({e["name"]: e["key"] for e in src.get("extraction_confs", [])})
            for r in rows:
                refs.update(keymap.get(v, v) for v in r["rule"] if "==" not in v)
        days = sorted(d for r in rows for d in r["days"])
        lo = (dt.date.fromisoformat(days[0]) - dt.timedelta(days=1)).isoformat()
        hi = (dt.date.fromisoformat(days[-1]) + dt.timedelta(days=45)).isoformat()
        U = ",".join(f"'{u}'" for u in users)
        N = ",".join("'" + n.replace("'", "''") + "'" for n in sorted(names))
        R = ",".join("'" + x.replace("'", "''") + "'" for x in sorted(refs))
        res = q(f"""WITH r AS (SELECT userid, question_ref, min(timestamp) AS t FROM responses
              WHERE userid IN ({U}) AND surveyid IN (SELECT id FROM surveys WHERE survey_name IN ({N}))
                AND timestamp BETWEEN '{lo}' AND '{hi}' GROUP BY 1, 2),
            qq AS (SELECT userid, min(t) AS tq FROM r WHERE question_ref IN ({R}) GROUP BY 1),
            n AS (SELECT r.userid, (count(*) FILTER (WHERE r.t <= qq.tq))::float8 AS k,
                         (count(*) FILTER (WHERE r.t <= qq.tq + INTERVAL '24 hours'))::float8 AS tot
                  FROM r JOIN qq ON qq.userid = r.userid GROUP BY 1)
            SELECT count(*) AS n, percentile_disc(0.5) WITHIN GROUP (ORDER BY k) AS k,
                   percentile_disc(0.5) WITHIN GROUP (ORDER BY tot) AS tot FROM n""", db="chatroach")
        row = list(csv.DictReader(res.splitlines(), delimiter="\t"))[0]
        out[rid] = dict(people=int(row["n"]), question=int(float(row["k"])) if row["k"] not in ("", "NULL") else None,
                        of=int(float(row["tot"])) if row["tot"] not in ("", "NULL") else None)
        print(" qpoint", rid, out[rid], file=sys.stderr)
    json.dump(out, open(os.path.join(RAW[cc], "qpoint.json"), "w"), indent=1)


# ============================================================================ run
ONLY = [a.split("=", 1)[1] for a in sys.argv if a.startswith("--only=")]     # e.g. --only=GH
COUNTRIES = ONLY or ["NG", "GH"]
if "--fetch" in sys.argv:
    for cc in COUNTRIES:
        print("fetching", cc, file=sys.stderr)
        fetch(cc)
EV = {}
for cc in ("NG", "GH"):
    subprocess.run([sys.executable, os.path.join(HERE, "pipeline.py"), RAW[cc]], check=True, stdout=subprocess.DEVNULL)
    EV[cc] = json.load(open(os.path.join(RAW[cc], "strata_evidence.json")))
if "--fetch" in sys.argv or "--qpoints" in sys.argv:
    for cc in COUNTRIES:
        fetch_qpoints(cc, EV)
if "--fetch-only" in sys.argv:
    sys.exit(0)

# ============================================================================ geometry -> places
# Natural Earth + GeoNames via build_maps.py (fetch_ne.py downloads them; GH.txt from GeoNames too).
GEO = os.environ.get("PILOT_GEO", PM)
sys.path.insert(0, GEO)
import build_maps as bm  # noqa: E402
from shapely.geometry import Point  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
import hashlib  # noqa: E402

A3 = {"NG": "NGA", "GH": "GHA"}
CNAME = {"NG": "Nigeria", "GH": "Ghana"}
A1CACHE = {}


def units(cc):
    if cc not in A1CACHE:
        A1CACHE[cc] = bm.admin1(A3[cc], "name")
    return A1CACHE[cc]


def region_name(cc, meta):
    n = meta.replace(" State", "").replace(" Region", "").strip()
    return "Federal Capital Territory" if n.startswith("Federal Capital") else n


def ne_region(cc, n):
    u = units(cc)
    alias = {"Nasarawa": "Nassarawa", "Benué": "Benue"}
    for k in (n, alias.get(n, n), n + " Region"):
        if k in u:
            return u[k]
    raise SystemExit(f"no Natural Earth unit for {cc}/{n}: {sorted(u)[:5]}...")


def norm(s):
    return s.replace("’", "'").replace("`", "'").lower()


# Meta region id -> GeoNames admin-1 code (Ghana; Brong-Ahafo is GeoNames' Bono). Meta gives a
# city's NAME and region, never its point, so the point comes from GeoNames inside that region.
GH_A1 = {"1421": "01", "1422": "02", "1423": "13", "1424": "04", "1425": "05", "1426": "06",
         "1427": "08", "1428": "09", "1430": "11"}
# Names GeoNames holds differently: Teshie is "Teshi Old Town"; Madina (Accra) is only "Medina
# Estates" as a populated place; Obuasi is only a district (ADM2) there, so Natural Earth's point.
ALIAS = {("GH", "Teshie"): "Teshi Old Town", ("GH", "Madina"): "Medina Estates"}
NE_ONLY = {("GH", "Obuasi")}
CITY_REGION = {}


def city_regions(cc):
    if cc not in CITY_REGION:
        m = {}
        for (sid, t), hist in confs(cc).items():
            if t == "strata":
                for _, conf in hist:
                    for s_ in conf:
                        ft = s_.get("facebook_targeting") or {}
                        for side in ("geo_locations", "excluded_geo_locations"):
                            for c in (ft.get(side) or {}).get("cities", []):
                                m[c["key"]] = c.get("region_id")
        CITY_REGION[cc] = m
    return CITY_REGION[cc]


def geocode_city(cc, name, key):
    if (cc, name) in NE_ONLY:
        p = [x for x in bm.PP if x["adm0_a3"] == A3[cc] and x["name"] == name]
        return dict(id=None, lat=p[0]["latitude"], lon=p[0]["longitude"], code="NaturalEarth"), len(p)
    a1 = "46" if cc == "NG" else GH_A1[city_regions(cc)[key]]      # Nigeria's Meta cities are all in Bauchi
    nm = ALIAS.get((cc, name), name)
    c = [x for x in bm.geonames(cc) if x["a1"] == a1 and norm(nm) in (norm(x["name"]), norm(x["ascii"]))]
    if not c:
        raise SystemExit(f"geocode: no GeoNames place {name!r} in {cc}/{a1}")
    c.sort(key=lambda x: (not x["code"].startswith("PPLA") and x["code"] != "PPLC", -x["pop"]))
    return c[0], len(c)


def nearest(cc, lat, lon, min_pop=0):
    best = min(((bm.hav(lat, lon, x["lat"], x["lon"]), x) for x in bm.geonames(cc) if x["pop"] >= min_pop), key=lambda t: t[0])
    return best[1]["name"], round(best[0], 1)


def admin1_of(cc, lat, lon):
    p = Point(lon, lat)
    for k, g in units(cc).items():
        if g.contains(p):
            return k
    return min(units(cc), key=lambda k: units(cc)[k].distance(p)) + " (nearest)"


def pin_check(cc, lat, lon):
    """Where a pin actually lands: its admin-1 unit (Natural Earth), the nearest GeoNames populated
    place of any size, and the nearest town of 20,000+. Labels use the town, never the stratum name."""
    n0, k0 = nearest(cc, lat, lon)
    n1, k1 = nearest(cc, lat, lon, 20000)
    return dict(kind="pin", admin1=admin1_of(cc, lat, lon), nearest_place=n0, nearest_place_km=k0,
                nearest_town=n1, nearest_town_km=k1, within_5km_of_a_place=k0 <= 5.0)


def pinhash(pins):
    s = json.dumps(sorted((round(a, 3), round(b, 3), None if r is None else round(r, 2)) for a, b, r in pins))
    return hashlib.sha1(s.encode()).hexdigest()[:6]


def towns(cc, pins, k=3):
    """Towns of 20,000+ nearest the pins (within 25 km), most pins first: orientation, not a claim."""
    c = collections.Counter()
    for lat, lon, _ in pins:
        n1, k1 = nearest(cc, lat, lon, 20000)
        if k1 > 25:
            n1, k1 = nearest(cc, lat, lon)
            n1 = n1 if k1 <= 5 else "open country"
        c[n1] += 1
    return [n for n, _ in c.most_common(k)]


def kmtxt(x):
    return f"{x:.0f}" if x >= 3 else f"{x:.1f}"


def rkm(r, unit):
    return None if r is None else round(r * (bm.MI if unit == "mile" else 1.0), 2)


PLACES = collections.OrderedDict()
PIN_NOTES = {}


def pins_of(cc, g):
    """custom_locations and cities as [lat, lon, radius_km]; cities geocoded through GeoNames."""
    pins, notes = [], []
    for lat, lon, r, u in g.get("custom_locations", []):
        pins.append([lat, lon, rkm(r, u)])
        notes.append(dict(pin_check(cc, lat, lon), kind="pin"))
    for name, key, r, u in g.get("cities", []):
        x, n = geocode_city(cc, name, key)
        pins.append([x["lat"], x["lon"], rkm(r, u)])
        notes.append(dict(kind="meta_city", meta_name=name, geonameid=x["id"], feature=x["code"],
                          point_name=ALIAS.get((cc, name), name), candidates=n))
    return pins, notes


def place_of(cc, geo_json):
    """(place key, side-kind) for a stratum's targeting; registers the place in PLACES."""
    inc, exc = json.loads(geo_json)
    exc = exc or {}
    if inc.get("places"):
        return None, "meta_place"
    ireg = [region_name(cc, x) for x in inc.get("regions", [])]
    ereg = [region_name(cc, x) for x in exc.get("regions", [])]
    ipins, inotes = pins_of(cc, inc)
    epins, enotes = pins_of(cc, exc)
    kind_city = bool(inc.get("cities")) or bool(exc.get("cities"))
    # excluded regions that do not touch the included area change nothing: drop them
    if ereg:
        if inc.get("countries"):
            pass
        else:
            area = unary_union([ne_region(cc, n) for n in ireg] +
                               [bm.circle(lon, lat, r or 1.0) for lat, lon, r in ipins])
            ereg = [n for n in ereg if n in ireg or area.intersection(ne_region(cc, n)).area > 0.005 * area.area]
    rtype = "city_radius" if kind_city else "radius_set"

    def radius_key(pins):
        rs = sorted({p[2] for p in pins}, key=lambda x: (x is None, x))
        rtxt = "+".join("city" if x is None else f"{x:g}km" for x in rs)
        return f"{cc}:{'city-radius' if kind_city else 'radius'}:{len(pins)}x{rtxt}:{pinhash(pins)}"

    def reg_radius(pins, notes):
        key = radius_key(pins)
        if key not in PLACES:
            rs = sorted({p[2] for p in pins}, key=lambda x: (x is None, x))
            tw = towns(cc, pins)
            if kind_city:
                lab = f"{len(pins)} Meta cit{'ies' if len(pins) > 1 else 'y'}" + (" (no radius set)" if rs == [None] else f" with a {'/'.join(kmtxt(x) for x in rs if x)} km radius") + ": " + ", ".join(
                    n["meta_name"] for n in notes[:4]) + (", …" if len(pins) > 4 else "")
            else:
                a1 = collections.Counter(n["admin1"] for n in notes if n.get("kind") == "pin")
                where = " and ".join(sorted(a for a, k_ in a1.items() if k_ >= max(2, 0.1 * len(pins)) or len(a1) == 1))
                where = where.replace("Nassarawa", "Nasarawa").replace("Federal Capital Territory", "the FCT")
                lab = (f"{len(pins)} radius area" + ("s" if len(pins) > 1 else "") + f" of {'/'.join(kmtxt(x) for x in rs)} km in {where}, near " + ", ".join(tw))
            PLACES[key] = dict(country=cc, type=rtype, label=lab, pins=pins, pin_check=notes)
        return key

    if inc.get("countries") and not ereg and not epins:
        key = f"{cc}:country"
        PLACES.setdefault(key, dict(country=cc, type="country", label=f"{CNAME[cc]}, whole country"))
        return key, None
    if inc.get("countries") and ereg and not epins:
        key = f"{cc}:country-minus:" + "+".join(sorted(ereg))
        PLACES.setdefault(key, dict(country=cc, type="country_minus", label=f"{CNAME[cc]} except " + (
            ", ".join(sorted(ereg)) if len(ereg) <= 3 else f"{len(ereg)} states: " + ", ".join(sorted(ereg))),
            regions_excluded=sorted(ereg)))
        return key, None
    if inc.get("countries") and epins and not ereg:
        inner = reg_radius(epins, enotes)
        key = f"{cc}:outside:{inner.split(':', 1)[1]}"
        PLACES.setdefault(key, dict(country=cc, type="radius_outside", label=f"{CNAME[cc]} outside the " + PLACES[inner]["label"],
                                    complement_of=inner, within=[CNAME[cc]]))
        return key, "outside"
    if ireg and not ipins and not epins:
        key = f"{cc}:region:" + "+".join(sorted(ireg))
        what = "State" if cc == "NG" else "Region"
        lab = (f"{ireg[0]} {what} (whole)" if ireg[0] != "Federal Capital Territory" else "FCT (whole territory)") if len(ireg) == 1 else (
            f"{len(ireg)} {what.lower()}s together: " + ", ".join(sorted(ireg)))
        PLACES.setdefault(key, dict(country=cc, type="region", label=lab, regions=sorted(ireg)))
        return key, None
    if ireg and epins and not ipins:
        inner = reg_radius(epins, enotes)
        key = f"{cc}:outside:{inner.split(':', 1)[1]}:in:" + "+".join(sorted(ireg))
        PLACES.setdefault(key, dict(country=cc, type="radius_outside", label=" and ".join(sorted(ireg)) + " outside the " + PLACES[inner]["label"],
                                    complement_of=inner, regions=sorted(ireg)))
        return key, "outside"
    if ipins and not ireg and not epins and not inc.get("countries"):
        if not ereg:
            return reg_radius(ipins, inotes), "inside"
        inner = reg_radius(ipins, inotes)          # radius areas that spill into an excluded state
        key = f"{inner}:minus:" + "+".join(sorted(ereg))
        PLACES.setdefault(key, dict(PLACES[inner], label=PLACES[inner]["label"] + ", less the part in " + " and ".join(sorted(ereg)),
                                    regions_excluded=sorted(ereg)))
        return key, "inside"
    raise SystemExit(f"geometry not handled: {geo_json[:300]}")


# ============================================================================ criteria (curated from the forms)
# Screening read from each recruitment's Fly form (the screen-out logic before the qualifying
# question) and its quota rule. Plain words, no topics. Amounts are what the form text offered.
G9_17 = ["caregiver:child_gender:girl", "caregiver:child_age:9-17"]
G9_14 = ["caregiver:child_gender:girl", "caregiver:child_age:9-14"]
NGN = lambda a, form="airtime": {"amount": a, "currency": "NGN", "form": form}
GHS = lambda a, form="airtime": {"amount": a, "currency": "GHS", "form": form}
CRIT = {
    "NG-2023-08": dict(round="baseline", screen=G9_17, languages=["en"], incentive=NGN(400),
                       who="cares for a girl aged 9–17; answered to the last question",
                       rule="answered the last question of the survey",
                       notes="Four sibling configurations fed one questionnaire. Three ad sets ($20) that put two distant states in one ad set are left out. "
                             "Several ad sets ran to all genders although their quota group was labelled by gender; ads.genders is the Meta targeting."),
    "NG-2023-10": dict(round="pilot", screen=[], languages=["en", "ha"], incentive=NGN(100),
                       who="any adult who answered a late question that only some respondents were routed to",
                       rule="answered a question near the end that the form showed only to some respondents",
                       notes="The quota rule sat on a routed question, so 9 of 973 qualified. Cost per qualified from this round is not comparable; cost per starter is."),
    "NG-2023-11": dict(round="cross-section", screen=[], languages=["en", "ha"], incentive=NGN(100),
                       who="any adult who reached the respondent-gender question, about three quarters of the way through",
                       rule="answered the respondent-gender question"),
    "NG-2024-09a": dict(round="pilot", screen=["consent"] + G9_17, languages=["en", "ha"], incentive=NGN(600),
                        who="cares for a girl aged 9–17; answered to the last question", rule="answered the last question"),
    "NG-2024-09b": dict(round="baseline", screen=["consent"] + G9_17, languages=["en", "ha"], incentive=NGN(600),
                        who="cares for a girl aged 9–17; answered to near the end of the survey", rule="answered a question near the end"),
    "NG-2024-10a": dict(round="baseline", screen=["consent"] + G9_17, languages=["en", "ha"], incentive=NGN(400),
                        who="cares for a girl aged 9–17; answered to the last question of a short survey", rule="answered the last question"),
    "NG-2024-10b": dict(round="baseline", screen=["consent"] + G9_17, languages=["en", "ha"], incentive=NGN(400),
                        who="cares for a girl aged 9–17; answered to the last question of a short survey", rule="answered the last question",
                        notes="The same short questionnaire as NG-2024-10a, fielded again two days after it ended."),
    "NG-2025-02a": dict(round="midline-fresh", screen=["consent"] + G9_17, languages=["en", "ha"], incentive=NGN(600),
                        who="cares for a girl aged 9–17; answered to near the end of the survey", rule="answered a question near the end",
                        notes="A midline round recruited as a fresh sample by ads in the same places."),
    "NG-2025-02b": dict(round="midline-fresh", screen=["consent"] + G9_17, languages=["en", "ha"], incentive=NGN(400),
                        who="cares for a girl aged 9–17; answered to the last question of a short survey", rule="answered the last question",
                        notes="A midline round recruited as a fresh sample by ads in the same places."),
    "NG-2025-04": dict(round="baseline", screen=["consent"] + G9_17, languages=["en", "ha"], incentive=NGN(600),
                       who="cares for a girl aged 9–17; answered to near the end of a short survey", rule="answered a question near the end",
                       notes="Two ad arms (A and B) were each tied to one side of the radius lines, so inside/outside is confounded with the arm."),
    "NG-2025-05": dict(round="cross-section", screen=[], languages=["en"], incentive=None,
                       who="anyone who answered a one-question sign-up", rule="answered the one question",
                       notes="A sign-up, not a survey. One ad set of this round ($27) recorded no people and is left out."),
    "NG-2025-06": dict(round="pilot", screen=["age:18-99", "language:en|ha|yo", "quota_group:education", "gave_phone"],
                       languages=["en", "ha", "yo"], incentive=NGN(500),
                       who="any adult who finished the survey in English, Hausa or Yoruba and gave a number for payment",
                       rule="answered the phone-operator question after giving a number; the ad set's language group counts by the language chosen",
                       notes="One ad set per language. Some higher education levels were screened out at random to balance the sample."),
    "NG-2025-11": dict(round="endline-fresh", screen=G9_17, languages=["en", "ha"], incentive=NGN(400),
                       who="cares for a girl aged 9–17; answered to the last question of a short survey", rule="answered the last question",
                       notes="An endline recruited as a fresh sample by ads. Earlier respondents who came back are not counted (no ad metadata inside the window). "
                             "Ad arms A and B were tied to sides of the radius lines, as in NG-2025-04."),
    "NG-2025-12a": dict(round="pilot", screen=["age:18-99", "consent"] + G9_14 + ["lives_in:NG-not-Lagos", "gave_phone"],
                        languages=["en"], incentive=NGN(500),
                        who="a parent or caregiver of a girl aged 9–14, living outside Lagos State, who finished the survey and gave a number for payment",
                        rule="answered the phone-operator question after giving a number"),
    "NG-2025-12b": dict(round="pilot", screen=["consent", "caregiver:child_age:0-14"], languages=["en"], incentive=NGN(200),
                        who="a parent or caregiver of a child aged 9 months to 14 years who answered to the second-last question",
                        rule="answered the second-last question"),
    "NG-2026-01": dict(round="baseline", screen=["consent", "caregiver:child_age:0-14"], languages=["en"], incentive=NGN(None),
                       who="a parent or caregiver of a child aged 9 months to 14 years who answered to the second-last question",
                       rule="answered the second-last question",
                       notes="The screen read 9 months to 14 years while the ads ran (the form was narrowed to 6–14 a day after they stopped). "
                             "The form offered ₦400 to ₦1,000 of credit depending on the respondent's path."),
    "NG-2026-02": dict(round="pilot", screen=["consent", "caregiver:child_age:9-14", "gave_phone"], languages=["ha"], incentive=NGN(500),
                       who="a parent or caregiver of a child aged 9–14 who finished a short survey and gave a number for payment",
                       rule="gave a phone number for payment"),
    "NG-2026-04a": dict(round="pilot", screen=["age:18-54"] + G9_14 + ["gave_phone"], languages=["en", "ha"], incentive=NGN(800),
                        who="an adult aged 18–54 with a daughter aged 9–14 at home who finished the survey and gave a number for payment",
                        rule="gave a phone number for payment",
                        notes="A second ₦800 was offered for a follow-up survey two weeks later. One ad set targeted a Meta place pinned 67 km from the town it named; it is left out."),
    "NG-2026-04b": dict(round="baseline", screen=["age:18-99"] + G9_14 + ["attention_check", "lives_in:NG-7-listed-states"],
                        languages=["en"], incentive=NGN(None),
                        who="a parent or caregiver of a girl aged 9–14, in one of seven listed states, who passed an attention check and answered all questions",
                        rule="answered the last question",
                        notes="Credit per questionnaire completed (up to ₦3,500 across the study) and a prize draw."),
    "NG-2026-05": dict(round="baseline", screen=["consent", "age:18-54"] + G9_14 + ["behaviour:attended_event", "gave_phone"],
                       languages=["en", "ha"], incentive=NGN(800),
                       who="an adult aged 18–54 with a daughter aged 9–14 at home, who had attended a specific local event, and gave a number for payment",
                       rule="gave a phone number for payment",
                       notes="A second ₦800 was offered for a follow-up two weeks later."),
    "NG-2026-06": dict(round="baseline", screen=["age:18-99"] + G9_14 + ["attention_check", "lives_in:NG-7-listed-states"],
                       languages=["en"], incentive=NGN(None),
                       who="a parent or caregiver of a girl aged 9–14, in one of seven listed states, who passed an attention check and answered all questions",
                       rule="answered the last question",
                       notes="Credit per questionnaire and a prize draw (a phone and ₦25,000 of airtime). Three campaigns with different welcome flows fed one questionnaire."),
    "NG-2026-07": dict(round="pilot", screen=["consent", "age:18-99"], languages=["en"], incentive=NGN(1000),
                       who="any adult who answered to the last question", rule="answered the last question",
                       notes="Two days of ads, $20. Meta counted 648 conversations for 414 people who started: treat as thin."),
    "NG-2026-08": dict(round="cross-section", screen=["age:18-99", "parent_any", "caregiver:child_age:0-4", "consent"], languages=["en", "ha"],
                       incentive=NGN(1000),
                       who="a parent or caregiver whose youngest child is under 5, who answered all questions",
                       rule="answered the last question"),
    "GH-2023-08": dict(round="pilot", screen=["age:18-99", "caregiver:child_age:5-12", "consent", "child_task", "gave_phone", "completed_follow_up"],
                       languages=["en"], incentive=GHS(8),
                       who="a parent of a child aged 5–12 who did the baseline with the child and came back for a follow-up about two weeks later",
                       rule="answered the last question of the follow-up survey",
                       notes="Qualified here means retained into a second wave, so the qualified share is far lower than a one-survey round's. ₵4 after the baseline, up to ₵8 in all."),
    "GH-2023-12": dict(round="pilot", screen=["consent"], languages=["en"], incentive=GHS(2),
                       who="any adult who reached the respondent-gender question, about four fifths of the way through",
                       rule="answered the respondent-gender question",
                       notes="Three days, $38. ₵2 on finishing part one, ₵5 more for part two."),
    "GH-2024-01a": dict(round="cross-section", screen=["consent"], languages=["en", "tw", "dag"], incentive=GHS(2),
                        who="any adult who reached the respondent-gender question, about four fifths of the way through",
                        rule="answered the respondent-gender question",
                        notes="Two language versions of one questionnaire (English; Twi and Dagbani) ran as sibling ad sets in the same regions and days; "
                              "379 people started both and are counted once. ₵2 on finishing part one, ₵5 more for part two."),
    "GH-2024-01b": dict(round="pilot", screen=["age:18-99", "caregiver:child_age:5-12", "consent", "child_task", "gave_phone"],
                        languages=["en"], incentive=GHS(4),
                        who="a parent of a child aged 5–12 whose child also completed a short task during the survey, and who gave a number for payment",
                        rule="gave a phone number for payment",
                        notes="Ads outside the listed cities ran only the first six days and were then dropped. ₵4 at the qualifying point, up to ₵8 in all."),
    "GH-2024-03": dict(round="pilot", screen=["age:18-99", "caregiver:child_age:5-12", "consent", "child_task", "gave_phone"],
                       languages=["en"], incentive=GHS(None),
                       who="a parent of a child aged 5–12 whose child also completed a short task during the survey, and who gave a number for payment",
                       rule="gave a phone number for payment",
                       notes="Two incentive arms ran side by side as separate ad sets: ₵15 at the qualifying point (up to ₵30) and ₵35 (up to ₵70). "
                             "The cells carry the arm in their flags."),
}
EXCL_CELL = {  # (recruitment, reason) for ad sets left out; the matching stratum ids are in the private map
    "meta_place": "targeted a Meta place pinned 67 km from the town it was named for",
    "two_states_one_ad_set": "one ad set covered two distant states, and its quota rule named a question the form did not have",
    "no_people": "ad spend with no people attributable to the ad set",
}


# ============================================================================ build
import statistics  # noqa: E402


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 1) if xs else None


def gender_of(g):
    return {None: "all", (1,): "men", (2,): "women"}.get(tuple(g) if g else None, "all")


def report(cc, slugs):
    sp = qual = 0.0
    seen = False
    for slug in slugs:
        p = os.path.join(RAW[cc], "rep", slug + ".tsv")
        rr = list(csv.DictReader(open(p), delimiter="\t")) if os.path.exists(p) else []
        if rr:
            seen = True
            d = json.loads(rr[0]["details"])
            sp += sum(v.get("lifetime_spent", v.get("total_spent", 0)) or 0 for v in d.values())
            qual += sum(v.get("current_participants", 0) or 0 for v in d.values())
    return (round(sp, 2), int(qual)) if seen else (None, None)


def arm_split(cc, rid, rows):
    """GH-2024-03: two incentive arms, each its own campaign with its own ad sets. Split spend by
    campaign and people by the arm of the creative on their first response."""
    fam = REC[rid]["family"]
    sids = set(REC[rid]["studies"].values())
    spend = collections.defaultdict(lambda: collections.defaultdict(float))
    imp = collections.defaultdict(float)
    for r in csv.DictReader(open(os.path.join(RAW[cc], "insights_daily.tsv")), delimiter="\t"):
        if r["sid"] in sids and r["spend"] not in ("", "NULL") and float(r["spend"]) > 0:
            arm = "high" if r["camp"].endswith("High") else "low"
            d = spend[(arm, r["strat"])]
            d[r["d"]] = max(d[r["d"]], float(r["spend"]))
            if r["imp"] not in ("", "NULL"):
                imp[(arm, r["strat"], r["d"])] = max(imp[(arm, r["strat"], r["d"])], float(r["imp"]))
    cr = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(RAW[cc], "user_creatives.tsv")), delimiter="\t"):
        if r["cr"] and r["cr"].endswith(("_Low", "_High")):
            cr[r["userid"]].append((r["t0"], r["cr"]))
    ppl = collections.defaultdict(list)
    for p in people_of(cc):
        if p["family"] == fam:
            xs = sorted(cr.get(p["user"], []))
            if not xs:
                raise SystemExit(f"{rid}: a person with no arm creative")
            ppl[("high" if xs[0][1].endswith("High") else "low", p["stid"])].append(p)
    out = []
    for r in rows:
        for arm in ("low", "high"):
            daily = spend[(arm, r["stratum"])]
            ps = ppl[(arm, r["stratum"])]
            out.append(dict(r, spend=round(sum(daily.values()), 2), days=sorted(daily),
                            impressions=round(sum(imp[(arm, r["stratum"], d)] for d in daily)),
                            median_daily_spend=round(statistics.median(daily.values()), 2),
                            starters=len(ps), qualified=sum(p["q"] for p in ps),
                            minutes=[p["minutes"] for p in ps if p["q"] and p["minutes"] is not None],
                            median_minutes_to_qualify=med([p["minutes"] for p in ps if p["q"]]),
                            arm=arm, starters_by_spend_fallback=0))
    return out


cells, crit, private_cells, checks, excluded_cells = [], [], {}, {}, []
QP = {cc: (json.load(open(os.path.join(RAW[cc], "qpoint.json"))) if os.path.exists(os.path.join(RAW[cc], "qpoint.json")) else {})
      for cc in ("NG", "GH")}
for rid in sorted(REC, key=lambda r: (r[:2] != "NG", r)):
    rec = REC[rid]
    cc = rec["country"]
    studies = rec.get("only_studies") or list(rec["studies"])
    sids = {rec["studies"][s] for s in studies}
    rows = [r for r in EV[cc]["rows"] if r["family"] == rec["family"] and r["sid"] in sids]
    keep = []
    for r in rows:
        key, side = place_of(cc, r["geo"])
        why = None
        if side == "meta_place":
            why = "meta_place"
        elif key and key.endswith("region:Anambra+Bauchi"):
            why = "two_states_one_ad_set"
        elif r["starters"] == 0 and r["spend"] > 0:
            why = "no_people"
        if why:
            excluded_cells.append(dict(rec=rid, reason=EXCL_CELL[why], spend_usd=r["spend"], started=r["starters"]))
            private_cells[f"{rid}/excluded/{len(excluded_cells)}"] = dict(study=r["study"], stratum=r["stratum"], reason=why)
            continue
        keep.append(dict(r, place=key, side_kind=side))
    if rid == "GH-2024-03":
        keep = arm_split(cc, rid, keep)
    sides = {r["side_kind"] for r in keep}
    two_sided = "inside" in sides and "outside" in sides
    n_studies = len(studies)
    keep.sort(key=lambda r: (r["place"], gender_of(r["genders"]), r.get("arm", ""), r["stratum"]))
    for i, r in enumerate(keep, 1):
        cid = f"{rid}/{i:02d}"
        g = gender_of(r["genders"])
        a0, a1 = r["age"] if r["age"] else (None, None)
        flags = []
        if r["starters"] < 200:
            flags.append("thin")
        if len(r["days"]) == 1:
            flags.append("one_day")
        if r.get("historic"):
            flags.append("ad_set_dropped_before_end")
        if r.get("starters_by_spend_fallback"):
            flags.append(f"assigned_by_daily_spend:{r['starters_by_spend_fallback']}")
        if n_studies > 1:
            flags.append("pooled_siblings")
        if rid in ("NG-2025-04", "NG-2025-11"):
            flags.append("ad_arm_confounded_with_side")
        if rid == "GH-2023-08":
            flags.append("qualified_after_follow_up")
        if rid == "NG-2023-10":
            flags.append("qualify_rule_on_routed_question")
        if r.get("arm"):
            flags.append(f"arm:{r['arm']}_incentive")
        cells.append(dict(
            rec=rid, cell=cid, country=cc, place=r["place"],
            side=(r["side_kind"] if two_sided else None),
            ads=dict(genders=g, age_min=a0 or 18, age_max=a1 or 65, interests=False),
            person_override=None,
            first=r["days"][0], last=r["days"][-1], spend_days=len(r["days"]),
            spend_usd=round(r["spend"], 2), impressions=r.get("impressions"),
            started=r["starters"], qualified=r["qualified"],
            median_daily_spend=r.get("median_daily_spend"),
            median_minutes_to_qualify=r.get("median_minutes_to_qualify"),
            flags=flags, attribution="ad_metadata"))
        private_cells[cid] = dict(study=r["study"], stratum=r["stratum"], arm=r.get("arm"))
    mine = [c for c in cells if c["rec"] == rid]
    C = CRIT[rid]
    rs, rq = report(cc, studies)
    sp = round(sum(c["spend_usd"] for c in mine), 2)
    st, qu = sum(c["started"] for c in mine), sum(c["qualified"] for c in mine)
    conv = sum(r.get("meta_conversations") or 0 for r in rows)
    mins = [m for r in keep for m in r.get("minutes", [])]
    checks[rid] = dict(spend=sp, report_spend=rs, spend_vs_report=(round(sp / rs, 3) if rs else None),
                       qualified=qu, report_qualified=rq, started=st, meta_conversations=round(conv),
                       excluded_cells_spend=round(sum(e["spend_usd"] for e in excluded_cells if e["rec"] == rid), 2))
    qp = QP[cc].get(rid) or {}
    crit.append(dict(
        rec=rid, country=cc, first=min(c["first"] for c in mine), last=max(c["last"] for c in mine), round=C["round"],
        ads=dict(genders=sorted({c["ads"]["genders"] for c in mine}), age_min=min(c["ads"]["age_min"] for c in mine),
                 age_max=max(c["ads"]["age_max"] for c in mine), interests=False),
        screen=C["screen"], who_qualified=C["who"], qualify_rule=C["rule"],
        qualify_point=(dict(question=qp["question"], of=qp["of"]) if qp.get("question") else None),
        median_minutes_to_qualify=med(mins), channel="messenger", languages=C["languages"], incentive=C["incentive"],
        started=st, qualified=qu,
        notes=" ".join(x for x in [
            C.get("notes", ""),
            "qualify_point: the median number of distinct questions the qualified people had answered when they gave the qualifying answer, "
            "of those they had answered 24 hours later (counted from their responses, not from the form, because forms branch).",
            ("Impressions derived from Insights spend and CPM where Meta returned no impression count." if any(c["impressions"] for c in mine) else ""),
        ] if x)))

# excluded recruitments: neutral ids, reasons, no slugs
for xid, x in sorted(MAP.get("excluded", {}).items()):
    crit.append(dict(rec=xid, country=x["country"], round="excluded", notes=x["reason"]))

# ============================================================================ write + check
used = {c["place"] for c in cells}
for k in list(PLACES):
    if k not in used and not any(p.get("complement_of") == k for kk, p in PLACES.items() if kk in used):
        PLACES.pop(k)
for c in cells:
    assert c["place"] in PLACES, c["cell"]
BANNED = re.compile("|".join(w.strip() for w in open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "private", "denylist.txt"))
                             if w.strip() and not w.startswith("#")), re.I)  # gitignored: it names clients and topics
os.makedirs(DATA, exist_ok=True)
out = {"cells": cells, "criteria": crit, "places": PLACES}
for name, obj in out.items():
    txt = json.dumps(obj, indent=1, ensure_ascii=False)
    for s_ in {s for r in REC.values() for s in r["studies"]} | {s for r in MAP.get("excluded", {}).values() for s in r["studies"]}:
        if re.fullmatch(r"[a-z]+", s_):      # one-word slugs ("test") are ordinary words: check as whole words
            assert not re.search(rf"\b{s_}\b", txt, re.I) or s_ == "test", (name, "slug leaked", s_)
        else:
            assert s_ not in txt, (name, "slug leaked", s_)
    for sid in {v for r in REC.values() for v in r["studies"].values()}:
        assert sid not in txt, (name, "study id leaked")
    hit = BANNED.search(txt)
    assert not hit, (name, "topic word", txt[max(0, hit.start() - 60):hit.end() + 60])
    open(os.path.join(DATA, f"NG-GH.{name}.json"), "w").write(txt + "\n")
MAP["cells"] = private_cells
MAP["checks"] = checks
MAP["excluded_cells"] = excluded_cells
json.dump(MAP, open(PRIV, "w"), indent=1, ensure_ascii=False)

print(f"{'rec':12} {'cells':>5} {'spend':>10} {'report':>10} {'ratio':>6} {'started':>7} {'qual':>6} {'rep.q':>6} {'conv':>6}")
for rid, k in checks.items():
    print(f"{rid:12} {sum(c['rec'] == rid for c in cells):5d} {k['spend']:10.2f} {k['report_spend'] or 0:10.2f} {k['spend_vs_report'] or 0:6.3f} "
          f"{k['started']:7d} {k['qualified']:6d} {k['report_qualified'] or 0:6d} {k['meta_conversations']:6d}")
print("excluded cells:", [(e["rec"], e["reason"][:30], e["spend_usd"], e["started"]) for e in excluded_cells])
print(len(cells), "cells;", len(crit), "criteria records;", len(PLACES), "places")
