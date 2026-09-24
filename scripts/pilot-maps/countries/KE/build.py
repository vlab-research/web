#!/usr/bin/env python3
"""Kenya country page, place design (notes/country-recipe.md, "The unit is the place").

    ../../geo/venv/bin/python build.py --fetch   # re-pull raw/ from vprod (SELECT only), then build
    ../../geo/venv/bin/python build.py           # build from raw/

Writes country-ke.json, kenya-places.svg, kenya-places.png.

How people are attributed to a place: every recruitment writes the ad set's stratum
labels (gender, location, demo_group ...) into inference_data at the person's FIRST
message, from the ad referral. A person counts as "started" in a stratum only if those
labels carry the first timestamp they have in that study (answers come later). People
whose first record has no labels, or whose labels arrive after they had already answered,
are not attributed to any ad and are left out of both counts.
"""
import csv, json, os, sys, subprocess, datetime, collections

HERE = os.path.dirname(os.path.abspath(__file__))
SP = os.path.dirname(os.path.dirname(HERE))
RAW = os.path.join(HERE, "raw")
csv.field_size_limit(10**9)
sys.path.insert(0, os.path.join(SP, "geo"))

STUDIES = {
    "215d714c-2d40-4079-bf55-683378f70d3c": "kenya-tvet-scoping-pilot",
    "84757600-d8fd-4767-be40-12f383cc1e58": "kenya-tvet-scoping-survey",
    "ca72c2f8-2508-40f5-aaab-eed4ff99d147": "shujaaz-free2choose-digital-evaluation",
    "ab059733-d087-42fd-acb1-b91e5eb1cdcb": "llm-bias-kenya-pilot",
    "7ff75f3c-e4cb-4105-82ad-2dc24acf7586": "girl-effect-pilot",
    "8fe1ffb9-ab04-4f8e-bc8d-9afcf341f0ef": "girl-effect-pilot-2",
    "e3440713-c44a-4333-bdd3-f8b7097fb010": "girl-effect",
    "8a5b150a-fbbf-4708-b2df-3c84c1ce487d": "kenya-tvet",
}
IDS = ",".join(f"'{s}'" for s in STUDIES)


# ----------------------------------------------------------------------------- fetch
def q(sql, db="vlab"):
    assert sql.lstrip().upper().startswith(("SELECT", "WITH")), "read-only"
    return subprocess.run(["kubectl", "exec", "-n", "vprod", "gbv-cockroachdb-0", "--", "/cockroach/cockroach", "sql",
                           "--insecure", "--format=tsv", f"--database={db}", "-e", sql],
                          check=True, capture_output=True, text=True, timeout=300).stdout


def fetch():
    os.makedirs(RAW, exist_ok=True)
    w = lambda n, s: open(os.path.join(RAW, n), "w").write(s)
    # values kept only for ad-set labels and the language choice: never answers (phone numbers, names)
    w("inference_all.tsv", q(f"SELECT study_id, user_id, variable, "
                              f"CASE WHEN variable IN ('gender','location','geography','demo_group','clusters') OR (variable='language' AND value::string IN ('\"English\"','\"Kiswahili\"','\"Swahili\"')) "
                              f"THEN value::string ELSE '' END AS value, timestamp FROM inference_data WHERE study_id IN ({IDS})"))
    w("daily.tsv", q(f"""WITH x AS (SELECT e.study_id, c.key AS camp, s.key AS strat,
          coalesce(s.value->>'date_start', e.period_start::date::string) AS d,
          max((s.value->>'spend')::float8) AS spend, max((s.value->>'impressions')::float8) AS imp
        FROM recruitment_data_events e, jsonb_each(e.data) AS c, jsonb_each(c.value) AS s
        WHERE e.study_id IN ({IDS}) AND jsonb_typeof(c.value)='object' AND jsonb_typeof(s.value)='object'
          AND s.value->>'spend' IS NOT NULL GROUP BY 1,2,3,4)
        SELECT study_id, camp, strat, d, spend, imp FROM x ORDER BY 1,4"""))
    confs = {}
    for sid in STUDIES:
        out = q(f"SELECT conf::string FROM study_confs WHERE study_id='{sid}' AND conf_type='strata' ORDER BY created DESC LIMIT 1")
        rows = list(csv.reader(out.splitlines(), delimiter="\t"))
        confs[sid] = json.loads(rows[1][0]) if len(rows) > 1 else []
    json.dump(confs, open(os.path.join(RAW, "strata_latest.json"), "w"))


# ----------------------------------------------------------------------------- recruitments
SHU_G = {"Nice Girl Nana": "Women", "Barasa Wa Town": "Women", "Barasa Amerix": "Men", "Nina Siri": "Women",
         "Nina Baddie": "Women", "ngn": "Women", "bwt": "Women", "ba": "Men", "ns": "Women", "nb": "Women"}
SHU_P = lambda g: "KE-10" if g in ("Nina Siri", "ns") else "KE-NBO" if g in ("Nina Baddie", "nb") else "KE"
TV_P = lambda s: "IN81" if "urban" in s else "OUT81"
cap = lambda s: s.capitalize()

# id, study, ad window (first..last spend day + 3), labels written at first message, stratum key,
# place, gender, qualifying rule, who qualified (plain words; no topics)
REC = [
    dict(id="2024-09", sid="215d714c", keys=["gender", "location"], win=("2024-09-23", "2024-09-30"),
         key=lambda m: f"gender:{m['gender']},location:{m['location']}" if {"gender", "location"} <= set(m) else None,
         ins=lambda s: s, place=TV_P, gender=lambda k: "Men" if k.startswith("gender:men") else "Women",
         qual=lambda v, k: "career_info_source" in v,
         who="aged 18–35; reached the end of the questions, about {m} minutes in", minutes_var="career_info_source"),
    dict(id="2025-02", sid="84757600", keys=["location"], win=("2025-02-05", "2025-02-23"),
         key=lambda m: f"location:{m['location']}" if "location" in m else None,
         ins=lambda s: "location:" + s.split("location:")[1], place=TV_P, gender=None,
         qual=lambda v, k: "linkedin_account" in v,
         who="aged 18–35; reached the end of the questions, about {m} minutes in", minutes_var="linkedin_account",
         sibling_of="215d714c"),
    dict(id="2025-05", sid="ca72c2f8", keys=["demo_group"], win=("2025-05-04", "2025-07-17"),
         key=lambda m: m.get("demo_group"), ins=lambda s: s.split(":", 1)[1], place=SHU_P, gender=lambda k: SHU_G[k],
         qual=lambda v, k: "phone_number" in v and k in ("Nice Girl Nana", "Barasa Wa Town", "Barasa Amerix", "Nina Siri", "Nina Baddie"),
         who="aged 18–24, mostly women, chosen by Meta interests; reached the end of the questions, about {m} minutes in", minutes_var="phone_number"),
    dict(id="2025-08", sid="ab059733", keys=["gender", "geography"], win=("2025-08-11", "2025-08-18"),
         key=lambda m: m.get("gender"), ins=lambda s: s.split(",")[0].split(":")[1], place=lambda k: "KE", gender=cap,
         # final quota rule also requires language == English or Swahili; the answer was stored as
         # "Kiswahili", so under the rule as written only English-language finishers qualify
         qual=lambda v, k: "operator" in v and v.get("language", ("",))[0] in ("English", "Swahili"),
         who="aged 18–65, chose English; reached the end of the questions, about {m} minutes in", minutes_var="operator"),
    dict(id="2025-12", sid="7ff75f3c", keys=["gender", "geography"], win=("2025-12-03", "2025-12-16"),
         key=lambda m: m.get("gender"), ins=lambda s: s.split(",")[0].split(":")[1], place=lambda k: "KE", gender=cap,
         qual=lambda v, k: "operator" in v,
         who="aged 18–30; reached the end of the questions, about {m} minutes in", minutes_var="operator"),
    dict(id="2026-01", sid="8fe1ffb9", keys=["gender", "geography"], win=("2026-01-14", "2026-01-29"),
         key=lambda m: m.get("gender"), ins=lambda s: s.split(",")[0].split(":")[1], place=lambda k: "KE", gender=cap,
         qual=lambda v, k: "thankyou_end_baseline" in v,
         who="aged 18–30; reached the end of the questions, about {m} minutes in", minutes_var="thankyou_end_baseline",
         sibling_of="7ff75f3c"),
    dict(id="2026-05", sid="e3440713", keys=["gender", "location"], win=("2026-05-20", "2026-07-10"),
         key=lambda m: m.get("gender") if m.get("location") == "geography" else None,
         ins=lambda s: s.split(",")[0].split(":")[1] if "geography" in s else None, place=lambda k: "KE", gender=cap,
         qual=lambda v, k: "gnormi_phone" in v,
         who="aged 18–30; reached the end of the questions, about {m} minutes in", minutes_var="gnormi_phone"),
    dict(id="2026-07", sid="e3440713", keys=["gender", "location"], win=("2026-07-16", "2026-09-25"),
         key=lambda m: m.get("gender") if m.get("location") == "location" else None,
         ins=lambda s: s.split(",")[0].split(":")[1] if "location:location" in s else None, place=lambda k: "KE", gender=cap,
         qual=lambda v, k: "gnormi_phone" in v,
         who="aged 18–30; reached the end of the questions, about {m} minutes in", minutes_var="gnormi_phone"),
]
PLACES = {
    "KE": ("Whole country", "all of Kenya"),
    "KE-NBO": ("Whole country except Nairobi", "Nairobi excluded, 24 km"),
    "KE-10": ("Whole country except 10 cities", "10 cities excluded, 16 km"),
    "IN81": ("Inside 81 radius areas", "around 81 towns, 2–9 km"),
    "OUT81": ("Outside the 81 radius areas", "the rest of Kenya"),
}


def num(v):
    return 0.0 if v in ("NULL", "", None) else float(v)


def ts(s):
    return datetime.datetime.fromisoformat(s[:19])


def analyse():
    spend = collections.defaultdict(lambda: collections.defaultdict(float))
    imps = collections.defaultdict(float)
    for r in csv.DictReader(open(os.path.join(RAW, "daily.tsv")), delimiter="\t"):
        if num(r["spend"]) > 0:
            spend[(r["study_id"][:8], r["strat"])][r["d"]] += num(r["spend"])
            imps[(r["study_id"][:8], r["strat"], r["d"])] += num(r["imp"])
    S = collections.defaultdict(lambda: collections.defaultdict(dict))
    for r in csv.DictReader(open(os.path.join(RAW, "inference_all.tsv")), delimiter="\t"):
        d = S[r["study_id"][:8]][r["user_id"]]
        if r["variable"] not in d or r["timestamp"] < d[r["variable"]][1]:
            d[r["variable"]] = (r["value"].strip('"'), r["timestamp"])

    out = []
    for rec in REC:
        lo, hi = rec["win"]
        st = collections.defaultdict(lambda: dict(spend=0.0, days=set(), imp=0.0, started=0, qualified=0, mins=[]))
        for (sid, strat), days in spend.items():
            if sid != rec["sid"]:
                continue
            k = rec["ins"](strat)
            for d, v in days.items():
                if k is not None and lo <= d <= hi:
                    st[k]["spend"] += v; st[k]["days"].add(d); st[k]["imp"] += imps[(sid, strat, d)]
        dropped = collections.Counter()
        for u, v in S[rec["sid"]].items():
            t0 = min(x[1] for x in v.values())
            m = {k: v[k][0] for k in rec["keys"] if k in v and v[k][1] == t0}
            k = rec["key"](m)
            if k is None:
                dropped["labelled for the other phase" if set(rec["keys"]) <= set(m) else
                        "no ad-set labels at first record (not attributable to an ad)"] += 1; continue
            if not lo <= t0[:10] <= hi:
                dropped["first message outside the ad window"] += 1; continue
            if rec.get("sibling_of") and u in S[rec["sibling_of"]]:
                dropped["already counted in the sibling recruitment"] += 1; continue
            s = st[k]; s["started"] += 1
            if rec["qual"](v, k):
                s["qualified"] += 1
                s["mins"].append((ts(v[rec["minutes_var"]][1]) - ts(t0)).total_seconds() / 60)
        strata = []
        for k, s in sorted(st.items()):
            strata.append(dict(stratum=k, place=rec["place"](k), gender=rec["gender"](k) if rec["gender"] else None,
                               spend=round(s["spend"], 2), spend_days=len(s["days"]),
                               first=min(s["days"]) if s["days"] else None, last=max(s["days"]) if s["days"] else None,
                               impressions=int(s["imp"]), started=s["started"], qualified=s["qualified"],
                               median_minutes=round(sorted(s["mins"])[len(s["mins"]) // 2], 1) if s["mins"] else None))
        days = set().union(*[st[k]["days"] for k in st])
        allm = sorted(x for k in st for x in st[k]["mins"])
        med = round(allm[len(allm) // 2]) if allm else None
        out.append(dict(id=rec["id"], study=STUDIES[[x for x in STUDIES if x.startswith(rec["sid"])][0]],
                        who_qualified=rec["who"].format(m=med), median_minutes_to_qualify=med, ad_days=len(days), first=min(days), last=max(days),
                        spend=round(sum(x["spend"] for x in strata), 2),
                        started=sum(x["started"] for x in strata), qualified=sum(x["qualified"] for x in strata),
                        not_attributed=dict(dropped), strata=strata))
    return out


def pool(recs, pred):
    sp = st = qu = 0; days = []; ids = set()
    for r in recs:
        for s in r["strata"]:
            if pred(r, s):
                sp += s["spend"]; st += s["started"]; qu += s["qualified"]; ids.add(r["id"])
                if s["first"]: days += [s["first"], s["last"]]
    return dict(spend=round(sp, 2), started=st, qualified=qu, recruitments=sorted(ids),
                first=min(days) if days else None, last=max(days) if days else None,
                cost_per_started=round(sp / st, 2) if st else None)


def build_data(recs):
    places = {}
    for p in PLACES:
        x = pool(recs, lambda r, s, p=p: s["place"] == p)
        x["by_recruitment"] = []
        for r in recs:
            y = pool([r], lambda r_, s, p=p: s["place"] == p)
            if y["started"]:
                y.update(who_qualified=r["who_qualified"],
                         cost_per_qualified=round(y["spend"] / y["qualified"], 2) if y["qualified"] else None)
                x["by_recruitment"].append(y)
        x["label"], x["geometry"] = PLACES[p]
        x["flag_under_200_started"] = x["started"] < 200
        places[p] = x
    gender = {g: pool(recs, lambda r, s, g=g: s["place"] == "KE" and s["gender"] == g) for g in ("Men", "Women")}
    return places, gender


# ----------------------------------------------------------------------------- map
def kenya_map(places):
    import build_maps as bm
    from shapely.geometry import shape
    from shapely.ops import unary_union
    rows = []
    for line in open(os.path.join(HERE, "geonames", "KE.txt"), encoding="utf8"):
        r = line.rstrip("\n").split("\t")
        if r[6] == "P":
            rows.append(dict(id=int(r[0]), name=r[1], ascii=r[2], lat=float(r[4]), lon=float(r[5]), code=r[7], a1=r[10], pop=int(r[14] or 0)))
    bm._GN["KE"] = rows
    conf = json.load(open(os.path.join(RAW, "strata_latest.json")))
    tv = conf["84757600-d8fd-4767-be40-12f383cc1e58"]
    pins = next(s for s in tv if "urban" in s["id"])["facebook_targeting"]["geo_locations"]["custom_locations"]
    sh = {s["id"]: s for s in conf["ca72c2f8-2508-40f5-aaab-eed4ff99d147"]}
    ex10 = sh["demo_group:Nina Siri"]["facebook_targeting"]["excluded_geo_locations"]["cities"]
    exN = sh["demo_group:Nina Baddie"]["facebook_targeting"]["excluded_geo_locations"]["cities"]

    def city_pt(name):
        c = [x for x in rows if x["name"] == name]
        c.sort(key=lambda x: (x["code"] not in ("PPLC",) and not x["code"].startswith("PPLA"), -x["pop"]))
        return c[0]
    counties = bm.admin1("KEN")
    country = unary_union(list(counties.values()))
    A0 = json.load(open(os.path.join(SP, "geo", "ne_10m_admin_0_countries.geojson")))["features"]
    nbrs = [shape(f["geometry"]) for f in A0 if f["properties"]["ADM0_A3"] in ("UGA", "TZA", "SSD", "ETH", "SOM")]
    circ = [bm.circle(c["longitude"], c["latitude"], bm.km(c)) for c in pins]
    rings10 = [(c["name"], city_pt(c["name"]), bm.km(c)) for c in ex10]
    ringN = [(c["name"], city_pt(c["name"]), bm.km(c)) for c in exN]

    W = 760
    body = [bm.text(0, 12, "Kenya · where the ads ran", "gm-eye")]
    main = bm.Frame(37.9, 0.25, country, (0, 26, 460, 560), pad=4)
    for n in nbrs:
        body.append(bm.path(main.g(n, simplify=0.4), "gm-ctx0"))
    body.append(bm.path(main.g(country, simplify=0.3), "gm-land"))
    body.append(bm.path(main.g(country, simplify=0.3), "gm-outline"))
    for nm, p, r in rings10:
        body.append(bm.path(main.g(bm.circle(p["lon"], p["lat"], r), simplify=0.1), "gm-excl"))
    for nm, p, r in ringN:
        body.append(bm.path(main.g(bm.circle(p["lon"], p["lat"], r), simplify=0.1), "gm-excl"))
    for c in circ:
        body.append(bm.path(main.g(c, simplify=0.05), "gm-circ"))
    # dots for areas too small to see at this scale
    for c in pins:
        x, y = main.xy(c["longitude"], c["latitude"])
        body.append(f'<circle class="gm-circ" cx="{x:.1f}" cy="{y:.1f}" r="1.6"/>')
    OFF = {"Eldoret": (14, 4, "start"), "Kitale": (14, 0, "start"), "Kakamega": (14, 2, "start"), "Kisumu": (14, 12, "start"),
           "Nakuru": (-4, -16, "end"), "Nairobi": (-22, 16, "end"), "Thika": (16, -8, "start"), "Garissa": (16, 4, "start"),
           "Malindi": (14, 2, "start"), "Mombasa": (-16, 8, "end")}
    for nm, p, r in rings10:
        x, y = main.xy(p["lon"], p["lat"]); dx, dy, an = OFF[nm]
        body.append(bm.text(x + dx, y + dy, nm, "gm-lab gm-halo", an))
    body.append(bm.scalebar(10, 26 + 560 - 12, main, 200))
    # inset: Nairobi and the central highlands
    from shapely.geometry import box as sbox
    ib = (486, 40, 274, 300)
    ctr = (36.85, -0.85)
    f = bm.Frame(ctr[0], ctr[1], sbox(ctr[0] - 0.9, ctr[1] - 0.9, ctr[0] + 0.9, ctr[1] + 0.9), ib, pad=0)
    x0, y0, w, h = ib
    body.append(bm.text(x0, y0 - 14, "Around Nairobi · inset", "gm-eye"))
    body.append(f'<rect class="gm-land" x="{x0}" y="{y0}" width="{w}" height="{h}"/>')
    body.append(bm.path(f.g(country, simplify=0.2), "gm-outline"))
    for nm, p, r in rings10 + ringN:
        body.append(bm.path(f.g(bm.circle(p["lon"], p["lat"], r), simplify=0.1), "gm-excl"))
    for c in circ:
        body.append(bm.path(f.g(c, simplify=0.05), "gm-circ"))
    inset_names = []
    for c in pins:
        nm = bm.name_point(c["latitude"], c["longitude"], "KEN", "KE")
        x, y = f.xy(c["longitude"], c["latitude"])
        if nm and x0 + 30 < x < x0 + w - 30 and y0 + 12 < y < y0 + h - 12:
            inset_names.append((nm["name"], x, y, bm.km(c)))
    for nm, x, y, r in inset_names:
        if nm not in ("Nyeri", "Naivasha", "Gilgil", "Murang’a", "Machakos", "Kangundo", "Ol Kalou", "Thika"):
            continue
        body.append(bm.text(x + 7, y + 4, nm, "gm-lab2 gm-halo"))
    for nm, p, r in rings10 + ringN:
        x, y = f.xy(p["lon"], p["lat"])
        if x0 < x < x0 + w and y0 < y < y0 + h and nm in ("Nairobi",):
            body.append(bm.text(x, y + 30, "Nairobi", "gm-lab gm-halo", "middle"))
            body.append(bm.text(x, y + 62, "excluded: 16 km and 24 km", "gm-tiny gm-halo", "middle"))
    body.append(f'<rect class="gm-panel" x="{x0}" y="{y0}" width="{w}" height="{h}"/>')
    body.append(bm.scalebar(x0 + 10, y0 + h - 10, f, 20))
    # locator on the main map
    a = main.xy(ctr[0] - 0.9, ctr[1] + 0.9); b = main.xy(ctr[0] + 0.9, ctr[1] - 0.9)
    body.append(f'<rect class="gm-frame" x="{a[0]:.1f}" y="{a[1]:.1f}" width="{b[0] - a[0]:.1f}" height="{b[1] - a[1]:.1f}"/>')
    # key
    ky = y0 + h + 30
    body.append(f'<circle class="gm-circ" cx="{x0 + 6}" cy="{ky - 4}" r="4"/>')
    body.append(bm.text(x0 + 18, ky, "81 radius areas, 2–9 km, around towns", "gm-lab"))
    body.append(bm.text(x0 + 18, ky + 14, "Sep 2024 and Feb 2025", "gm-tiny"))
    body.append(f'<circle class="gm-excl" cx="{x0 + 6}" cy="{ky + 36}" r="6"/>')
    body.append(bm.text(x0 + 18, ky + 40, "cities excluded from some ads", "gm-lab"))
    body.append(bm.text(x0 + 18, ky + 54, "10 cities at 16 km, Nairobi", "gm-tiny"))
    body.append(bm.text(x0 + 18, ky + 68, "also at 24 km · May–Jul 2025", "gm-tiny"))
    body.append(bm.text(x0, ky + 96, "The inside of an excluded city was", "gm-note"))
    body.append(bm.text(x0, ky + 110, "never targeted on its own.", "gm-note"))

    # cost rows: cost per person who started, the legend
    order = ["KE", "KE-NBO", "KE-10", "IN81", "OUT81"]
    y = 26 + 560 + 34
    body.append(bm.text(0, y - 14, "Ad cost per person who started the survey", "gm-eye"))
    mc = max(places[p]["cost_per_started"] for p in order)
    lw, bw = 250, 760 - 250 - 70
    for i, p in enumerate(order):
        P = places[p]; yy = y + i * 40
        body.append(bm.text(0, yy + 10, P["label"], "gm-lab"))
        body.append(bm.text(0, yy + 24, P["geometry"], "gm-tiny"))
        L = max(2.0, bw * P["cost_per_started"] / mc)
        body.append(f'<rect class="gm-bar" x="{lw}" y="{yy:.1f}" width="{L:.1f}" height="12"/>')
        body.append(bm.text(lw + L + 6, yy + 10.5, bm.money(P["cost_per_started"]), "gm-val"))
        d0 = datetime.date.fromisoformat(P["first"]).strftime("%b %Y"); d1 = datetime.date.fromisoformat(P["last"]).strftime("%b %Y")
        body.append(bm.text(lw, yy + 24, f"{P['started']:,} started · {bm.money(P['spend'])} ad spend · {d0}–{d1}", "gm-tiny"))
    H = y + len(order) * 40 + 4
    desc = ("Kenya, with 81 radius areas of 2 to 9 km around towns drawn to scale, and dashed outlines for "
            "10 cities excluded at 16 km and Nairobi at 24 km. Below, the advertising cost per person who started the survey: " +
            "; ".join(f"{places[p]['label']} {bm.money(places[p]['cost_per_started'])}" for p in order) + ".")
    s = bm.svg(W, H, "Kenya: where the ads ran, and the ad cost per person who started", desc, body, "ke")
    open(os.path.join(HERE, "kenya-places.svg"), "w").write(s)
    return dict(pins=len(pins), pins_named=[(bm.name_point(c["latitude"], c["longitude"], "KEN", "KE") or {}).get("name") for c in pins],
                excluded_cities=[(n, p["lat"], p["lon"], round(r, 1)) for n, p, r in rings10 + ringN])


def render_png():
    import re
    tok = {"--ink": "#1F272E", "--ink-2": "#4A555E", "--ink-3": "#79858D", "--rule": "#CFD9DD", "--rule-2": "#AEBCC2",
           "--surface": "#FFFFFF", "--sunk": "#E5EBED", "--paper": "#F1F4F5", "--data": "#1D5F6E", "--data-2": "#9DB6BC",
           "--brass": "#7A5C1E"}
    s = open(os.path.join(HERE, "kenya-places.svg")).read()
    s = re.sub(r"var\((--[a-z0-9-]+)\)", lambda m: tok[m.group(1)], s)
    tmp = os.path.join(HERE, "_render.svg"); open(tmp, "w").write(s)
    env = dict(os.environ, FONTCONFIG_FILE=os.path.join(SP, "geo", "fonts.conf"))
    subprocess.run(["rsvg-convert", "-w", "1520", "-b", tok["--paper"], "-o", os.path.join(HERE, "kenya-places.png"), tmp], check=True, env=env)
    os.remove(tmp)


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        fetch()
    recs = analyse()
    places, gender = build_data(recs)
    geo = kenya_map(places)
    meta = json.load(open(os.path.join(HERE, "meta.json")))
    ppl = collections.defaultdict(set)
    for r in csv.DictReader(open(os.path.join(RAW, "inference_all.tsv")), delimiter="\t"):
        ppl[r["user_id"]].add(r["timestamp"][:10])
    allp = dict(unique_people=len(ppl), first=min(min(v) for v in ppl.values()), last=max(max(v) for v in ppl.values()),
                studies=len(STUDIES), note="anyone in any Kenya study on the current platform (distinct inference_data user_id), including test entries before ads")
    out = dict(_meta=meta, country="KE", design="place (recipe: 'The unit is the place, not the study')",
               all_people_surveyed=allp,
               totals=dict(spend=round(sum(p["spend"] for p in places.values()), 2),
                           started=sum(p["started"] for p in places.values()),
                           qualified=sum(p["qualified"] for p in places.values())),
               places=places, by_gender_whole_country=gender, recruitments=recs, geography=geo,
               excluded_for_review=json.load(open(os.path.join(HERE, "excluded.json"))))
    json.dump(out, open(os.path.join(HERE, "country-ke.json"), "w"), indent=1, ensure_ascii=False)
    render_png()
    for k, p in places.items():
        print(k, p["started"], p["qualified"], p["spend"], p["cost_per_started"], p["first"], p["last"], p["recruitments"])
        for y in p["by_recruitment"]:
            print("    ", y["recruitments"], y["started"], y["qualified"], y["spend"], y["cost_per_started"], y["cost_per_qualified"], y["first"], y["last"])
    print(gender)
    print(out["totals"], allp)
