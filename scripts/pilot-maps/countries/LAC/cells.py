#!/usr/bin/env python3
"""Cell table for country group KE-LAC (Kenya, Bolivia, Argentina, Honduras).

    python3 cells.py --fetch   # re-pull raw/ from vprod (SELECT only), then build
    python3 cells.py           # build from raw/

The contract is notes/cells-schema.md; the method is notes/country-recipe.md ("The unit is the
place"). Writes, relative to the repo:

    scripts/data/cells/KE-LAC.cells.json      one row per ad set per recruitment (tracked)
    scripts/data/cells/KE-LAC.criteria.json   one record per recruitment (tracked)
    scripts/data/cells/KE-LAC.places.json     place key -> geometry (tracked)
    scripts/pilot-maps/private/KE-LAC.map.json   ids -> study slugs, UUIDs, raw strata (gitignored)

Raw pulls go to countries/KE/raw/ and countries/LAC/raw/ (gitignored). Respondent ids are hashed
in SQL with a salt that is generated per fetch and never written down, so the raw files join
with each other but not with anything else. Answer values are kept only for ad-set labels and
the screening answers a quota rule needs.

Inputs that could name a client or a topic (study ids, survey names, question refs) are read
from the gitignored scripts/pilot-maps/private/KE-LAC.inputs.json.

Attribution (the method, as in countries/KE/build.py): every recruitment writes the ad set's
labels into inference_data at the person's FIRST message, from the ad referral. A person counts
as "started" in a cell only if those labels carry their earliest timestamp in the study and the
first message falls inside the cell's spend window (1 day before the first spend day to 3 days
after the last). Each person counts once per recruitment, and once across sibling recruitments
that fed the same survey. Qualified = started and past the recruitment's final quota rule,
recounted from inference_data.

GeoNames dumps (KE, BO, AR, HN) are read from $GEONAMES_DIR or scripts/pilot-maps/geonames/,
and downloaded there if missing.
"""
import collections, csv, datetime, json, math, os, secrets, statistics, subprocess, sys, urllib.request, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
PM = os.path.dirname(os.path.dirname(HERE))            # scripts/pilot-maps
REPO = os.path.dirname(os.path.dirname(PM))
OUT = os.path.join(REPO, "scripts", "data", "cells")
PRIVATE = os.path.join(PM, "private")
G = "KE-LAC"
csv.field_size_limit(10**9)
MI = 1.609344


def inputs():
    p = os.path.join(PRIVATE, f"{G}.inputs.json")
    if not os.path.exists(p):
        raise SystemExit(f"missing {p}: the private list of studies, surveys and question refs (gitignored; ask for it)")
    return json.load(open(p))


# ============================================================================ database (read-only)
def q(sql, db="vlab", fmt="tsv"):
    assert sql.lstrip().upper().startswith(("SELECT", "WITH")), "read-only: SELECT/WITH only"
    return subprocess.run(["kubectl", "exec", "-n", "vprod", "gbv-cockroachdb-0", "--", "/cockroach/cockroach", "sql",
                           "--insecure", f"--format={fmt}", f"--database={db}", "-e", sql],
                          check=True, capture_output=True, text=True, timeout=170).stdout


def rows(path):
    return list(csv.DictReader(open(path), delimiter="\t"))


def ids_sql(ids):
    return ",".join(f"'{s}'" for s in ids)


def fetch(raw, studies, keep_values, keep_language, surveys, qual_paths, salt, platforms=None):
    """studies: {uuid: neutral key}. keep_values: inference variables whose value is an ad-set label or a
    needed screening answer. qual_paths: [(rec_id, qual_ref, lo, hi)] for the qualify-point count."""
    os.makedirs(raw, exist_ok=True)
    w = lambda n, s: open(os.path.join(raw, n), "w").write(s)
    I = ids_sql(studies)
    h = f"substr(sha256(user_id::string || '{salt}'), 1, 20)"
    keep = ",".join(f"'{v}'" for v in keep_values)
    lang = ",".join(f"'\"{v}\"'" for v in keep_language) or "''"
    w("inference.tsv", q(f"SELECT substr(study_id::string,1,8) AS s, {h} AS u, variable, "
                         f"CASE WHEN variable IN ({keep}) OR (variable='language' AND value::string IN ({lang})) "
                         f"THEN value::string ELSE '' END AS value, timestamp FROM inference_data WHERE study_id IN ({I})"))
    w("daily.tsv", q(f"""WITH x AS (SELECT e.study_id, c.key AS camp, s.key AS strat,
          coalesce(s.value->>'date_start', e.period_start::date::string) AS d,
          (s.value->>'spend')::float8 AS spend, (s.value->>'impressions')::float8 AS imp, (s.value->>'cpm')::float8 AS cpm,
          (SELECT max((a->>'value')::float8) FROM jsonb_array_elements(CASE WHEN jsonb_typeof(s.value->'actions')='array'
             THEN s.value->'actions' ELSE '[]'::jsonb END) AS a
           WHERE a->>'action_type'='onsite_conversion.messaging_conversation_started_7d') AS conv
        FROM recruitment_data_events e, jsonb_each(e.data) AS c, jsonb_each(c.value) AS s
        WHERE e.study_id IN ({I}) AND jsonb_typeof(c.value)='object' AND jsonb_typeof(s.value)='object'
          AND s.value->>'spend' IS NOT NULL)
        SELECT substr(study_id::string,1,8) AS s, camp, strat, d, max(spend) AS spend, max(imp) AS imp, max(cpm) AS cpm, max(conv) AS conv
        FROM x GROUP BY 1,2,3,4 ORDER BY 1,2,3,4"""))
    # campaigns used by any other study: dropped (ws-inbound 5.3 trap 2)
    w("shared_campaigns.tsv", q(f"""WITH c AS (SELECT DISTINCT c.key AS camp FROM recruitment_data_events e, jsonb_each(e.data) c
        WHERE e.study_id IN ({I})) SELECT c.camp, count(DISTINCT e.study_id) AS n FROM recruitment_data_events e, jsonb_each(e.data) x, c
        WHERE x.key = c.camp GROUP BY 1"""))
    w("confs.tsv", q(f"SELECT substr(study_id::string,1,8) AS s, conf_type, created, conf::string AS conf FROM study_confs "
                     f"WHERE study_id IN ({I}) AND conf_type IN ('strata','general','recruitment','destinations','data_sources') ORDER BY 1,2,3"))
    out = []
    for sid in studies:   # one at a time: a correlated max() over adopt_reports hangs
        r = q(f"SELECT substr(study_id::string,1,8) AS s, created, details::string AS details FROM adopt_reports "
              f"WHERE study_id='{sid}' AND report_type='FACEBOOK_ADOPT' ORDER BY created DESC LIMIT 1").splitlines()
        out += r[1:] if out else r
    w("adopt.tsv", "\n".join(out) + "\n")
    hc = f"substr(sha256(userid || '{salt}'), 1, 20)"
    if platforms:
        w("platform.tsv", q(f"SELECT {hc} AS u, min(timestamp) AS t0, max(metadata->>'platform') AS platform FROM responses "
                            f"WHERE shortcode IN ({ids_sql(platforms)}) GROUP BY userid", db="chatroach"))
    scs = {}
    for name in surveys:
        scs[name] = [r["shortcode"] for r in csv.DictReader(q(f"SELECT DISTINCT shortcode FROM surveys WHERE survey_name='{name}'",
                                                                db="chatroach").splitlines(), delimiter="\t")]
    json.dump(scs, open(os.path.join(raw, "shortcodes.json"), "w"))
    allsc = ids_sql(sorted({s for v in scs.values() for s in v}))
    lines = ["rec\tu\tupto\ttotal"]
    for rec, ref, lo, hi in qual_paths:
        r = q(f"""WITH u AS (SELECT userid, min(timestamp) AS tq FROM responses WHERE shortcode IN ({allsc})
                    AND question_ref='{ref}' AND timestamp BETWEEN '{lo}' AND '{hi}' GROUP BY 1),
                  r AS (SELECT userid, question_ref, min(timestamp) AS ts FROM responses WHERE shortcode IN ({allsc})
                    AND userid IN (SELECT userid FROM u) GROUP BY 1,2)
                  SELECT {hc.replace('userid', 'u.userid')} AS u,
                    count(*) FILTER (WHERE r.ts <= u.tq AND r.ts >= u.tq - INTERVAL '3 days') AS upto,
                    count(*) FILTER (WHERE r.ts >= u.tq - INTERVAL '3 days' AND r.ts <= u.tq + INTERVAL '1 day') AS total
                  FROM u JOIN r ON r.userid = u.userid GROUP BY 1""", db="chatroach")
        lines += [f"{rec}\t{l}" for l in r.splitlines()[1:]]
    w("qualify_path.tsv", "\n".join(lines) + "\n")


# ============================================================================ loading
class Raw:
    def __init__(self, raw):
        self.raw = raw
        self.shared = {r["camp"] for r in rows(os.path.join(raw, "shared_campaigns.tsv")) if int(r["n"]) > 1}
        self.daily = collections.defaultdict(dict)       # (s, camp, strat) -> {d: (spend, imp, imp_from_cpm, conv)}
        for r in rows(os.path.join(raw, "daily.tsv")):
            sp = num(r["spend"])
            if sp <= 0 or r["camp"] in self.shared:
                continue
            imp, est = num(r["imp"]), False
            if not imp and num(r["cpm"]):
                imp, est = sp / num(r["cpm"]) * 1000, True
            self.daily[(r["s"], r["camp"], r["strat"])][r["d"]] = (sp, imp, est, num(r["conv"]))
        self.people = collections.defaultdict(lambda: collections.defaultdict(dict))   # s -> u -> var -> (value, ts)
        for r in rows(os.path.join(raw, "inference.tsv")):
            d = self.people[r["s"]][r["u"]]
            if r["variable"] not in d or r["timestamp"] < d[r["variable"]][1]:
                d[r["variable"]] = (r["value"].strip('"'), r["timestamp"])
        self.confs = collections.defaultdict(list)
        for r in rows(os.path.join(raw, "confs.tsv")):
            self.confs[(r["s"], r["conf_type"])].append((r["created"], json.loads(r["conf"])))
        self.adopt = {}
        for r in rows(os.path.join(raw, "adopt.tsv")):
            self.adopt[r["s"]] = (r["created"], json.loads(r["details"]))
        p = os.path.join(raw, "platform.tsv")
        self.platform = {r["u"]: r["platform"] for r in rows(p)} if os.path.exists(p) else {}
        self.qpath = collections.defaultdict(dict)
        for r in rows(os.path.join(raw, "qualify_path.tsv")):
            self.qpath[r["rec"]][r["u"]] = (int(r["upto"]), int(r["total"]))

    def latest(self, s, t):
        return self.confs[(s, t)][-1][1] if self.confs[(s, t)] else None

    def stratum(self, s, sid):
        """The last configured version of a stratum id (strata are append-only; renamed ones survive in history)."""
        for _, st in reversed(self.confs[(s, "strata")]):
            for x in st:
                if x["id"] == sid:
                    return x
        return None


def num(v):
    return 0.0 if v in ("NULL", "", None) else float(v)


def ts(s):
    return datetime.datetime.fromisoformat(s[:19])


def day(s, k):
    return (datetime.date.fromisoformat(s) + datetime.timedelta(days=k)).isoformat()


def ads_of(stratum):
    ft = stratum["facebook_targeting"]
    g = ft.get("genders") or []
    flex = ft.get("flexible_spec")
    if isinstance(flex, str):
        flex = json.loads(flex)
    interests = bool(flex) or any(k in ft for k in ("interests", "behaviors"))
    return {"genders": "women" if g == [2] else "men" if g == [1] else "all",
            "age_min": ft.get("age_min", 18), "age_max": ft.get("age_max", 65), "interests": interests}


def ad_flags(stratum):
    ft = stratum["facebook_targeting"]
    f = []
    if "age_min" not in ft and "age_max" not in ft:
        f.append("meta_default_age")
    if ft.get("excluded_custom_audiences"):
        f.append("excluded_custom_audience")
    if ads_of(stratum)["interests"]:
        f.append("interest_targeting")
    return f


# ============================================================================ geography
GEONAMES = None


def geonames(cc):
    global GEONAMES
    if GEONAMES is None:
        GEONAMES = {}
    if cc in GEONAMES:
        return GEONAMES[cc]
    d = os.environ.get("GEONAMES_DIR") or os.path.join(PM, "geonames")
    p = os.path.join(d, cc + ".txt")
    if not os.path.exists(p):
        os.makedirs(d, exist_ok=True)
        z = os.path.join(d, cc + ".zip")
        urllib.request.urlretrieve(f"https://download.geonames.org/export/dump/{cc}.zip", z)
        zipfile.ZipFile(z).extract(cc + ".txt", d)
    out = []
    for line in open(p, encoding="utf8"):
        r = line.rstrip("\n").split("\t")
        if r[6] == "P":
            out.append(dict(name=r[1], ascii=r[2], lat=float(r[4]), lon=float(r[5]), code=r[7], pop=int(r[14] or 0)))
    GEONAMES[cc] = out
    return out


def hav(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(a))


def name_pin(cc, lat, lon, max_km=5.0):
    """Nearest GeoNames town of 1,000+ within max_km; failing that, any populated place within max_km."""
    best = None
    for x in geonames(cc):
        d = hav(lat, lon, x["lat"], x["lon"])
        key = (x["pop"] < 1000, d)
        if d <= max_km and (best is None or key < best[0]):
            best = (key, x["name"], round(d, 1), x["pop"])
    return None if best is None else dict(name=best[1], km=best[2], pop=best[3])


def city_point(cc, name):
    c = [x for x in geonames(cc) if x["name"] == name or x["ascii"] == name]
    c.sort(key=lambda x: (x["code"] != "PPLC" and not x["code"].startswith("PPLA"), -x["pop"]))
    return c[0] if c else None


def km(c):
    return c["radius"] * (MI if c.get("distance_unit") == "mile" else 1.0)


def pin_set(cc, pins):
    """[lat, lon, r_km] for a list of Meta custom_locations, with a GeoNames check of every pin."""
    out, check = [], []
    for c in pins:
        out.append([round(c["latitude"], 6), round(c["longitude"], 6), round(km(c), 2)])
        n = name_pin(cc, c["latitude"], c["longitude"])
        check.append(n)
    return out, check


def radius_label(pins):
    r = sorted({p[2] for p in pins})
    f = lambda x: f"{x:g}"
    return f"{f(r[0])}km" if len(r) == 1 else f"{f(r[0])}-{f(r[-1])}km"


# ============================================================================ the engine
def build_rec(R, rec):
    """rec: id, sids (study8 list), spend(s, camp, strat, d) -> cell key|None,
    person(labels_at_t0, t0, u, s) -> cell key|None, labels (vars that are ad-set labels),
    qual(vars, cellkey) -> var name of the qualifying answer or None, cells {key: meta}, siblings (set of people)."""
    cells = {k: dict(spend=0.0, days=set(), imp=0.0, imp_est=False, conv=0.0, daily=[], strata=set(),
                     started=0, qualified=0, mins=[], people=set()) for k in rec["cells"]}
    for (s, camp, strat), days in R.daily.items():
        if s not in rec["sids"]:
            continue
        for d, (sp, imp, est, conv) in days.items():
            k = rec["spend"](s, camp, strat, d)
            if k is None:
                continue
            c = cells[k]
            c["spend"] += sp; c["days"].add(d); c["imp"] += imp; c["imp_est"] |= est; c["conv"] += conv
            c["strata"].add((s, camp, strat))
    daily = collections.defaultdict(lambda: collections.defaultdict(float))
    for (s, camp, strat), days in R.daily.items():
        if s in rec["sids"]:
            for d, v in days.items():
                k = rec["spend"](s, camp, strat, d)
                if k is not None:
                    daily[k][d] += v[0]
    win = {k: (day(min(c["days"]), -1), day(max(c["days"]), 3)) for k, c in cells.items() if c["days"]}
    dropped = collections.Counter()
    counted = set()
    for s in rec["sids"]:
        for u, v in R.people[s].items():
            t0 = min(x[1] for x in v.values())
            m = {k: v[k][0] for k in rec["labels"] if k in v and v[k][1] == t0}
            k = rec["person"](m, t0, u, s) if m else None
            if k is None:
                dropped["labelled_for_another_phase" if m else "no_ad_labels_at_first_record"] += 1
                continue
            if k not in win or not win[k][0] <= t0[:10] <= win[k][1]:
                dropped["first_message_outside_spend_window"] += 1
                continue
            if u in rec.get("siblings", set()) or u in counted:
                dropped["counted_in_sibling_recruitment"] += 1
                continue
            counted.add(u)
            c = cells[k]; c["started"] += 1; c["people"].add(u)
            qv = rec["qual"](v, k)
            if qv:
                c["qualified"] += 1
                c["mins"].append((ts(v[qv][1]) - ts(t0)).total_seconds() / 60)
                c.setdefault("qualified_people", set()).add(u)
    for k, c in cells.items():
        c["median_daily_spend"] = round(statistics.median(daily[k].values()), 2) if daily[k] else None
    return cells, dict(dropped), counted


def med(x):
    return round(statistics.median(x), 1) if x else None


def emit(R, rec, cells, dropped, places):
    out_cells, private_cells = [], {}
    keys = [k for k in rec["cells"] if cells[k]["spend"] > 0 or cells[k]["started"] > 0]
    for i, k in enumerate(keys, 1):
        c, meta = cells[k], rec["cells"][k]
        cid = f"{rec['id']}/{i:02d}"
        flags = list(meta.get("flags", []))
        if c["started"] < 200:
            flags.append("thin")
        if len(c["days"]) == 1:
            flags.append("one_day")
        if c["imp_est"]:
            flags.append("impressions_from_cpm")
        assert meta["place"] in places, meta["place"]
        out_cells.append(dict(
            rec=rec["id"], cell=cid, country=rec["country"], place=meta["place"], side=meta.get("side"),
            ads=meta["ads"], person_override=meta.get("person_override"),
            first=min(c["days"]) if c["days"] else None, last=max(c["days"]) if c["days"] else None,
            spend_days=len(c["days"]), spend_usd=round(c["spend"], 2), impressions=int(round(c["imp"])),
            started=c["started"], qualified=c["qualified"], median_daily_spend=c["median_daily_spend"],
            median_minutes_to_qualify=med(c["mins"]), flags=sorted(set(flags)), attribution="ad_metadata"))
        private_cells[cid] = dict(key=k, strata=sorted("|".join(x) for x in c["strata"]),
                                  meta_conversations_started=int(c["conv"]) if c["conv"] else None)
    return out_cells, private_cells


def qualify_point(R, rec, cells):
    qp = R.qpath.get(rec["id"], {})
    qual = set().union(*[c.get("qualified_people", set()) for c in cells.values()])
    got = [qp[u] for u in qual if u in qp]
    if not got:
        return None, 0, len(qual)
    return ({"question": int(round(statistics.median(x[0] for x in got))),
             "of": int(round(statistics.median(x[1] for x in got)))}, len(got), len(qual))


def report_check(R, rec, cells):
    """Compare with the latest FACEBOOK_ADOPT report(s) of the recruitment's studies."""
    out = {}
    for s in rec["sids"]:
        if s not in R.adopt:
            continue
        created, det = R.adopt[s]
        ls = sum((v.get("lifetime_spent") or 0) for v in det.values() if isinstance(v, dict))
        cp = sum((v.get("current_participants") or 0) for v in det.values() if isinstance(v, dict))
        out[s] = dict(report_created=created[:16], lifetime_spent=round(ls, 2), current_participants=cp)
    return out


# ============================================================================ group runner
def run(fetch_flag):
    sys.path.insert(0, HERE)
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "KE"))
    import ke_cells, lac_cells
    parts = [ke_cells, lac_cells]
    salt = secrets.token_hex(12)
    all_cells, all_crit, all_places, private = [], [], {}, {"recruitments": {}, "excluded": {}}
    checks = {}
    for part in parts:
        if fetch_flag:
            part.fetch(salt)
        R = Raw(part.RAW)
        places, pchecks = part.places(R)
        all_places.update(places)
        checks.update(pchecks)
        for rec in part.recruitments(R):
            if rec.get("excluded"):
                all_crit.append(rec["criteria"])
                private["excluded"][rec["id"]] = rec["private"]
                continue
            cells, dropped, counted = build_rec(R, rec)
            if "register" in rec:
                rec["register"](counted)
            oc, pc = emit(R, rec, cells, dropped, all_places)
            qpt, nq, nqual = qualify_point(R, rec, cells)
            crit = dict(rec["criteria"])
            spend = round(sum(c["spend_usd"] for c in oc), 2)
            days = [c["first"] for c in oc if c["first"]] + [c["last"] for c in oc if c["last"]]
            allm = [m for c in cells.values() for m in c["mins"]]
            crit.update(first=min(days), last=max(days), started=sum(c["started"] for c in oc),
                        qualified=sum(c["qualified"] for c in oc), median_minutes_to_qualify=med(allm),
                        qualify_point=qpt)
            crit["who_qualified"] = crit["who_qualified"].format(m=round(med(allm)) if allm else "?")
            order = ["rec", "country", "first", "last", "round", "ads", "screen", "who_qualified", "qualify_rule",
                     "qualify_point", "median_minutes_to_qualify", "channel", "languages", "incentive", "started", "qualified", "notes"]
            all_crit.append({k: crit.get(k) for k in order})
            all_cells += oc
            private["recruitments"][rec["id"]] = dict(rec["private"], cells=pc, not_counted=dropped, spend_usd=spend,
                                                      report=report_check(R, rec, cells),
                                                      qualify_point_people=f"{nq} of {nqual} qualified people found in the response path")
    private["place_checks"] = checks
    os.makedirs(OUT, exist_ok=True); os.makedirs(PRIVATE, exist_ok=True)
    dump = lambda p, x: json.dump(x, open(p, "w"), indent=1, ensure_ascii=False)
    dump(os.path.join(OUT, f"{G}.cells.json"), all_cells)
    dump(os.path.join(OUT, f"{G}.criteria.json"), all_crit)
    dump(os.path.join(OUT, f"{G}.places.json"), all_places)
    dump(os.path.join(PRIVATE, f"{G}.map.json"), private)
    for c in all_crit:
        print(c["rec"], c.get("round"), c.get("first"), c.get("last"), c.get("started"), c.get("qualified"), c.get("qualify_point"))
    for c in all_cells:
        print("  ", c["cell"], c["place"], c["ads"]["genders"], c["spend_usd"], c["started"], c["qualified"], c["spend_days"], c["flags"])
    for k, v in private["recruitments"].items():
        print(k, v["spend_usd"], v["report"], v["not_counted"])


if __name__ == "__main__":
    run("--fetch" in sys.argv)
