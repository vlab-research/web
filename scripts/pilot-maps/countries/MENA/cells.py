#!/usr/bin/env python3
"""MENA group's slice of the cell table (notes/cells-schema.md): Iraq, Egypt, Morocco, Jordan,
Saudi Arabia, United Arab Emirates.

    python3 cells.py            # recompute from raw/ and write the four files
    python3 cells.py --fetch    # re-pull raw/ from production first (SELECT only), then recompute

Writes
    scripts/data/cells/MENA.cells.json      one row per ad set per recruitment (tracked)
    scripts/data/cells/MENA.criteria.json   one record per recruitment, excluded ones included (tracked)
    scripts/data/cells/MENA.places.json     geometry per place key (tracked)
    scripts/pilot-maps/private/MENA.map.json  "outputs": rec -> studies, cell -> raw stratum ids (gitignored)

Every study-identifying input (study filter, survey names, form shortcodes, question refs) is read
from the "inputs" section of the private map, so this file carries none of them. raw/ is gitignored.

Method (country-recipe.md, "The unit is the place"):
  spend      Insights per campaign x ad set x day, max within a day, summed over days with spend > 0;
             a campaign under more than one study would be dropped (none is).
  started    a person whose ad-set metadata (inference_data, the variables written from the ad at the
             first message) matches the cell's labels, and whose first answer in the programme's forms
             falls between 1 day before the recruitment's first spend day and 3 days after its last.
             The studies share survey pools, so the pools are unioned and each person counted once.
  qualified  started, and answered the recruitment's FINAL quota-rule question in its own forms.
  minutes    qualifying answer time - first answer time, median over qualified people.
"""
import csv, json, math, os, re, statistics, subprocess, sys
from collections import defaultdict, OrderedDict
from datetime import date, datetime, timedelta, timezone

csv.field_size_limit(10**9)
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
PM = os.path.dirname(os.path.dirname(HERE))
REPO = os.path.dirname(os.path.dirname(PM))
OUT = os.path.join(REPO, "scripts", "data", "cells")
PRIV = os.path.join(PM, "private", "MENA.map.json")
GN_DIR = os.path.join(RAW, "geonames")
MI = 1.609344

PRIVATE = json.load(open(PRIV))
INP = PRIVATE["inputs"]


# ------------------------------------------------------------------ pulls (read-only)
def sql(db, q, fmt="tsv", timeout=170):
    cmd = ["kubectl", "exec", "-n", "vprod", "gbv-cockroachdb-0", "--", "/cockroach/cockroach", "sql",
           "--insecure", f"--format={fmt}", f"--database={db}",
           "-e", "SET statement_timeout='160s'", "-e", q]
    assert re.match(r"^\s*(SELECT|WITH|SHOW)\b", q, re.I), "read-only: SELECT/WITH/SHOW only"
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=True).stdout
    lines = out.split("\n")
    if lines and lines[0].strip() == "SET":
        lines = lines[1:]
    return "\n".join(lines)


def study_filter():
    ex = ",".join(f"'{s}'" for s in INP["study_exclude"])
    return f"st.slug LIKE '{INP['study_like']}' AND st.slug NOT IN ({ex})"


def fetch():
    os.makedirs(RAW, exist_ok=True)
    F = study_filter()
    names = ",".join(f"'{s}'" for s in INP["survey_names"])
    scx = " ".join(f"AND r.shortcode NOT LIKE '{p}'" for p in INP["shortcode_skip"])
    Q = {
        "daily_all.tsv": ("vlab", f"""
WITH x AS (SELECT st.slug, c.key AS camp, s.key AS strat, coalesce(s.value->>'date_start', e.period_start::date::string) AS d,
  max((s.value->>'spend')::float8) AS spend, max((s.value->>'impressions')::float8) AS imp, max((s.value->>'unique_clicks')::float8) AS clicks
  FROM recruitment_data_events e JOIN studies st ON st.id=e.study_id, jsonb_each(e.data) AS c, jsonb_each(c.value) AS s
  WHERE jsonb_typeof(c.value)='object' AND jsonb_typeof(s.value)='object' AND s.value->>'spend' IS NOT NULL AND {F}
  GROUP BY 1,2,3,4)
SELECT slug, camp, strat, d, spend, imp, clicks FROM x ORDER BY 1,2,3,4""", "tsv"),
        "all_camps.tsv": ("vlab", f"""
WITH m AS (SELECT DISTINCT c.key AS camp FROM recruitment_data_events e JOIN studies st ON st.id=e.study_id, jsonb_each(e.data) AS c WHERE {F})
SELECT c.key AS camp, count(DISTINCT e.study_id) AS n FROM recruitment_data_events e, jsonb_each(e.data) AS c
WHERE c.key IN (SELECT camp FROM m) GROUP BY 1""", "tsv"),
        "confs.csv": ("vlab", f"""
SELECT st.slug, c.conf_type, c.created, c.conf::string AS conf FROM study_confs c JOIN studies st ON st.id=c.study_id
WHERE {F} AND c.conf_type IN ('strata','general','recruitment') ORDER BY 1,2,3""", "csv"),
        "studies.tsv": ("vlab", f"SELECT st.id, st.slug FROM studies st WHERE {F}", "tsv"),
        "pool.tsv": ("vlab", f"""
SELECT st.slug, i.user_id, i.variable, i.value->>0 AS v, i.timestamp FROM inference_data i JOIN studies st ON st.id=i.study_id
WHERE {F} AND i.variable IN ('City','Location','Gender','Age')""", "tsv"),
        "responses.tsv": ("chatroach", f"""
WITH sc AS (SELECT DISTINCT shortcode FROM surveys WHERE survey_name IN ({names}))
SELECT r.userid, r.shortcode, r.question_ref, min(r.timestamp) AS t, count(*) AS n FROM responses r
WHERE r.timestamp > '2025-10-01' AND r.timestamp < '2026-03-15' AND r.shortcode IN (SELECT shortcode FROM sc) {scx}
GROUP BY 1,2,3""", "tsv"),
        "forms.csv": ("chatroach", f"""
SELECT DISTINCT ON (shortcode) shortcode, created, form_json::string AS form_json FROM surveys
WHERE survey_name IN ({names}) ORDER BY shortcode, created DESC""", "csv"),
    }
    for fn, (db, q, fmt) in Q.items():
        print("pull", fn, file=sys.stderr)
        open(os.path.join(RAW, fn), "w").write(sql(db, q, fmt))
    for rec, v in INP["recs"].items():
        for slug in v["slugs"]:
            q = (f"SELECT a.created, a.details::string AS details FROM adopt_reports a WHERE a.study_id=(SELECT id FROM "
                 f"studies WHERE slug='{slug}') AND a.report_type='FACEBOOK_ADOPT' ORDER BY a.created DESC LIMIT 1")
            open(os.path.join(RAW, f"adopt-{slug}.csv"), "w").write(sql("vlab", q, "csv"))
    os.makedirs(GN_DIR, exist_ok=True)
    for cc in ("IQ", "EG", "MA", "JO", "SA", "AE"):
        if not os.path.exists(os.path.join(GN_DIR, cc + ".txt")):
            subprocess.run(f"curl -sf -o {cc}.zip https://download.geonames.org/export/dump/{cc}.zip && unzip -oq {cc}.zip {cc}.txt",
                           shell=True, cwd=GN_DIR, check=True)


# ------------------------------------------------------------------ recruitments (no slugs here)
# Places are keyed by geometry. Each Meta city target is its own place (a pin with its radius, or
# Meta's own city area when no radius was set). See PLACES below.
RECS = OrderedDict([
    ("AE-2025-10", dict(country="AE", round="pilot", label="Location",
        places={"Dubai": "AE:city_radius:Dubai-40km", "Abu Dhabi": "AE:city_radius:AbuDhabi-40km",
                "Other": "AE:country_minus:Dubai+AbuDhabi-40km"},
        screen=["consent", "age:30-99"],
        who="aged 30 and over; reached the last survey question",
        rule="answered the last survey question (before the payment step)",
        incentive={"amount": 20, "currency": "AED", "form": "gift_card"},
        notes=("Short diagnostic run in October 2025, before the main recruitment. Three places: two 25-mile (40 km) "
               "radius areas and the rest of the country outside them. Separate ad account, also USD (it runs US studies). "
               "Consent text promised a $5 gift card; the payment step sent AED 20, raised to AED 30 from 9 Oct. "
               "A citizenship question was asked but did not end the survey."))),
    ("SA-2025-10", dict(country="SA", round="pilot", label="City",
        places={"Riyadh": "SA:city:Riyadh", "Jeddah": "SA:city:Jeddah", "Mecca": "SA:city:Mecca"},
        screen=["consent", "age:30-99"],
        who="aged 30 and over; reached the second-to-last survey question",
        rule="answered the second-to-last survey question (before the payment step)",
        incentive={"amount": 20, "currency": "SAR", "form": "gift_card"},
        notes=("Pilot, late October 2025. Meta city targets with no radius (Meta's own city area). The consent text "
               "promised a $5 gift card; the payment step sent SAR 20. The pilot form's city question listed the wrong "
               "country's cities; it did not end the survey, so qualification is unaffected."))),
    ("IQ-2025-11", dict(country="IQ", round="pilot", label="City",
        places={"Baghdad": "IQ:city_radius:Baghdad-16km", "Mosul": "IQ:city_radius:Mosul-16km",
                "Basra": "IQ:city_radius:Basra-16km"},
        screen=["consent", "age:30-99"],
        who="aged 30 and over; reached the third-to-last survey question",
        rule="answered the third-to-last survey question (before the payment step)",
        incentive={"amount": 1300, "currency": "IQD", "form": "airtime"},
        notes=("Pilot, two ad days in November 2025. The consent text promised a $5 gift card; the payment step sent "
               "IQD 1,300 of mobile credit. Same 10-mile (16.1 km) city radius areas as the main recruitment."))),
    ("JO-2025-11", dict(country="JO", round="pilot", label="City",
        places={"Amman": "JO:city:Amman", "Zarqa": "JO:region:Zarqa", "Irbid": "JO:radius:Irbid-8km"},
        screen=["consent", "age:30-99"],
        who="aged 30 and over; reached the third-to-last survey question",
        rule="answered the third-to-last survey question (before the payment step)",
        incentive={"amount": 0.7, "currency": "JOD", "form": "airtime"},
        flags=["mixed_forms"],
        notes=("Pilot, one ad day in November 2025. About half of the people these ads brought in were routed to a "
               "neighbouring country's pilot form (same questions, other city list and payment); the city question did "
               "not end the survey there either, so they count. Consent promised JOD 0.70; the payment step sent JOD 1."))),
    ("MA-2025-11", dict(country="MA", round="pilot", label="City",
        places={"Casablanca": "MA:city_radius:Casablanca-16km", "Fez": "MA:city_radius:Fez-16km",
                "Marrakech": "MA:city_radius:Marrakesh-16km"},
        screen=["consent", "age:30-99"],
        who="aged 30 and over; reached the third-to-last survey question",
        rule="answered the third-to-last survey question (before the payment step)",
        incentive={"amount": 6.4, "currency": "MAD", "form": "airtime"},
        notes="Pilot, one ad day in November 2025. Consent promised MAD 6.40; the payment step sent MAD 5.85.")),
    ("AE-2025-12", dict(country="AE", round="baseline", label="City",
        places={"Abu Dhabi": "AE:city_radius:AbuDhabi-16km", "Sharja": "AE:city:Sharjah"},
        drop={"Dubai": "the 'Dubai' ad sets targeted Dubai and Mecca together (two cities in two countries), so "
                       "their spend and people cannot be given one place"},
        screen=["consent", "age:30-99", "citizen:AE"],
        who="aged 30 and over and UAE citizens; reached the payment step after the last survey question",
        rule="answered the gift-card question that follows the main survey",
        incentive={"amount": 30, "currency": "AED", "form": "gift_card"},
        notes=("Main recruitment. Abu Dhabi is a Meta city with a 10-mile radius; Sharjah is Meta's own city area "
               "(no radius). The Dubai ad sets are left out (below). Non-citizens were screened out, which the other "
               "five countries did not do. The quota rule was the last survey question for three days in January and "
               "the gift-card question before and after; counted under the final rule. The gift card promised was "
               "AED 30; the payment step sent AED 30, then AED 37 from 22 Dec."))),
    ("SA-2025-12", dict(country="SA", round="baseline", label="City",
        places={"Riyadh": "SA:city:Riyadh", "Mecca": "SA:city:Mecca", "Jeddah": "SA:city:Jeddah"},
        # 6 Dec to 18 Dec 2025 the ad sets labelled Jeddah aimed at Meta's Mecca city. Split them by date.
        phases={"Jeddah": [dict(until_spend_day="2025-12-18", until_time="2025-12-18T21:22:19+00:00",
                                place="SA:city:Mecca", flag="label_jeddah_aimed_at_mecca"),
                           dict(place="SA:city:Jeddah", flag="after_fix")]},
        screen=["consent", "age:30-99", "lives_in:target_cities"],
        who="aged 30 and over, living in one of the three cities; reached the payment step after the last survey question",
        rule="answered the gift-card question that follows the main survey",
        incentive={"amount": 20, "currency": "SAR", "form": "gift_card"},
        notes=("Main recruitment. Meta city targets with no radius (Meta's own city area) from the second day; the first "
               "day ($14 of spend) used 10-mile radius areas. From 6 to 18 Dec the ad sets labelled Jeddah aimed at "
               "Mecca: those days are counted as Mecca (cells flagged label_jeddah_aimed_at_mecca), split at the "
               "configuration change (people by first-answer time, spend by Insights day, so the 18 Dec day goes to "
               "Mecca). The quota rule changed twice; counted under the final rule. Citizenship was asked, not screened. "
               "Ads cost more per person who started than in the other countries here (clicks $0.21 against $0.03-0.11 in "
               "the Dec 2025 runs); the cause is not known."))),
    ("EG-2025-12", dict(country="EG", round="baseline", label="City",
        places={"Cairo": "EG:city_radius:Cairo-16km", "Giza": "EG:city_radius:Giza-16km",
                "Alexandria": "EG:city_radius:Alexandria-16km"},
        screen=["consent", "age:30-99", "lives_in:target_cities"],
        who="aged 30 and over, living in one of the three cities; reached the payment step after the last survey question",
        rule="answered the phone-number question that follows the main survey",
        incentive={"amount": 50, "currency": "EGP", "form": "airtime"},
        notes=("Main recruitment. The quota rule changed on 15 Jan 2026, after the last report, so qualified is "
               "recounted under the final rule (the report's 966 becomes about 3,700). The Cairo and Giza radius areas "
               "overlap (centres 7 km apart)."))),
    ("MA-2025-12", dict(country="MA", round="baseline", label="City",
        places={"Casablanca": "MA:city_radius:Casablanca-16km", "Fez": "MA:city_radius:Fez-16km",
                "Marrakech": "MA:city_radius:Marrakesh-16km"},
        screen=["consent", "age:30-99", "lives_in:target_cities"],
        who="aged 30 and over, living in one of the three cities; reached the payment step after the last survey question",
        rule="answered the phone-number question that follows the main survey",
        incentive={"amount": 9.3, "currency": "MAD", "form": "airtime"},
        notes=("Main recruitment. Only 13% of starters qualified: about half stopped at or before consent. The quota "
               "rule changed on 15 Jan 2026; recounted under the final rule."))),
    ("JO-2025-12", dict(country="JO", round="baseline", label="City",
        places={"Amman": "JO:city:Amman", "Zarqa": "JO:region:Zarqa", "Irbid": "JO:radius:Irbid-8km"},
        screen=["consent", "age:30-99", "lives_in:target_cities"],
        who="aged 30 and over, living in one of the three cities; reached the payment step after the last survey question",
        rule="answered the phone-number question that follows the main survey",
        incentive={"amount": 0.7, "currency": "JOD", "form": "airtime"},
        notes=("Main recruitment; ads on 5 days only. Three kinds of place: Amman as Meta's city area (no radius), "
               "the whole Zarqa governorate, and a 5-mile (8 km) pin at Irbid. The quota rule changed on 15 Jan 2026; "
               "recounted under the final rule. Consent promised JOD 0.70; the payment step sent JOD 1."))),
    ("IQ-2025-12", dict(country="IQ", round="baseline", label="City",
        places={"Baghdad": "IQ:city_radius:Baghdad-16km", "Mosul": "IQ:city_radius:Mosul-16km",
                "Basra": "IQ:city_radius:Basra-16km"},
        screen=["consent", "age:30-99", "lives_in:target_cities"],
        who="aged 30 and over, living in one of the three cities; reached the payment step after the last survey question",
        rule="answered the phone-number question that follows the main survey",
        incentive={"amount": 2000, "currency": "IQD", "form": "airtime"},
        notes=("Main recruitment. Incentive: the consent text promised IQD 2,000 of mobile credit (about $1.50), paid "
               "through an outside rewards service whose amount is not held in our configuration. The study setting of "
               "$1 per respondent was an input to the budget optimiser, set to 0 on 10 Feb 2026; it was never the "
               "payment. Only about one in ten people who gave a number reached the payment-processing message, so we "
               "cannot confirm how many were paid."))),
])
EXCLUDED = OrderedDict([
    ("SA-2025-11", dict(country="SA", round="excluded",
        notes=("Excluded: a two-day pilot ($87, 9 people) whose targeting changed partway through from Meta city areas "
               "to 10-mile radius areas, so no single place describes it."))),
    ("EG-2025-11", dict(country="EG", round="excluded",
        notes=("Excluded: a pilot with $248 of recorded ad spend over six days and no respondent carrying its ad "
               "metadata; its own forms have essentially no answers. The spend cannot be matched to people."))),
])
ORDER = ["AE-2025-10", "SA-2025-10", "SA-2025-11", "IQ-2025-11", "EG-2025-11", "JO-2025-11", "MA-2025-11",
         "AE-2025-12", "SA-2025-12", "EG-2025-12", "MA-2025-12", "JO-2025-12", "IQ-2025-12"]

# ------------------------------------------------------------------ places
# pins: [lat, lon, radius_km]; radius None = Meta's own city area (no radius set).
GEO = {  # GeoNames point for each Meta city target, by geonameid (checked below)
    "Baghdad": ("IQ", 98182), "Mosul": ("IQ", 99072), "Basra": ("IQ", 99532),
    "Cairo": ("EG", 360630), "Giza": ("EG", 360995), "Alexandria": ("EG", 361058),
    "Casablanca": ("MA", 2553604), "Fez": ("MA", 2548885), "Marrakesh": ("MA", 2542997),
    "Riyadh": ("SA", 108410), "Jeddah": ("SA", 105343), "Mecca": ("SA", 104515),
    "Dubai": ("AE", 292223), "Abu Dhabi": ("AE", 292968), "Sharjah": ("AE", 292672),
    "Amman": ("JO", 250441), "Irbid": ("JO", 248946),
}
PLACES = OrderedDict()


def city_place(key, cc, city, radius_km, label):
    PLACES[key] = dict(country=cc, type="city_radius", label=label, cities=[city], pins=[[None, None, radius_km]])


for c, cc in [("Baghdad", "IQ"), ("Mosul", "IQ"), ("Basra", "IQ"), ("Cairo", "EG"), ("Giza", "EG"),
              ("Alexandria", "EG"), ("Casablanca", "MA"), ("Fez", "MA"), ("Marrakesh", "MA")]:
    city_place(f"{cc}:city_radius:{c}-16km", cc, c, 16.1, f"{c}: 10-mile (16.1 km) radius area around the city")
city_place("AE:city_radius:AbuDhabi-16km", "AE", "Abu Dhabi", 16.1, "Abu Dhabi: 10-mile (16.1 km) radius area around the city")
city_place("AE:city_radius:AbuDhabi-40km", "AE", "Abu Dhabi", 40.2, "Abu Dhabi: 25-mile (40.2 km) radius area around the city")
city_place("AE:city_radius:Dubai-40km", "AE", "Dubai", 40.2, "Dubai: 25-mile (40.2 km) radius area around the city")
for c, cc in [("Riyadh", "SA"), ("Jeddah", "SA"), ("Mecca", "SA"), ("Sharjah", "AE"), ("Amman", "JO")]:
    city_place(f"{cc}:city:{c}", cc, c, None, f"{c}: Meta's city area (no radius set)")
PLACES["JO:region:Zarqa"] = dict(country="JO", type="region", label="Zarqa Governorate (whole)", regions=["Zarqa Governorate"])
PLACES["JO:radius:Irbid-8km"] = dict(country="JO", type="radius_set", label="Irbid: a 5-mile (8.0 km) radius area on a pin",
                                     pins=[[32.549183, 35.860062, 8.0]])
PLACES["AE:country_minus:Dubai+AbuDhabi-40km"] = dict(country="AE", type="country_minus",
    label="United Arab Emirates outside the Dubai and Abu Dhabi 25-mile (40.2 km) radius areas",
    pins_excluded=[[None, None, 40.2], [None, None, 40.2]], excluded_cities=["Dubai", "Abu Dhabi"])


def load_geonames(cc):
    rows = {}
    for line in open(os.path.join(GN_DIR, cc + ".txt"), encoding="utf8"):
        r = line.rstrip("\n").split("\t")
        if r[6] == "P":
            rows[int(r[0])] = dict(name=r[1], ascii=r[2], alt=r[3], lat=float(r[4]), lon=float(r[5]), code=r[7], a1=r[10])
    return rows


def hav(lat1, lon1, lat2, lon2):
    p = math.pi / 180
    a = math.sin((lat2 - lat1) * p / 2) ** 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(a))


def fill_pins(meta_cities):
    """Each Meta city target gets the GeoNames point of the city of that name (seat or capital, by id).
    Checks: GeoNames name (or alternate) matches Meta's name; Natural Earth's point is within 5 km."""
    gn = {cc: load_geonames(cc) for cc in {v[0] for v in GEO.values()}}
    ne = []
    nef = os.path.join(PM, "ne_10m_populated_places_simple.geojson")
    if os.path.exists(nef):
        ne = [f["properties"] for f in json.load(open(nef))["features"]]
    checks = {}
    for city, (cc, gid) in GEO.items():
        x = gn[cc][gid]
        names = {x["name"], x["ascii"], *x["alt"].split(",")}
        mc = meta_cities.get({"Marrakesh": "Marrakesh", "Mecca": "Mecca"}.get(city, city))
        ok_name = (mc is None) or (mc["name"] in names or city in names)
        near = [hav(x["lat"], x["lon"], p["latitude"], p["longitude"]) for p in ne
                if p.get("iso_a2") == cc or p.get("adm0_a3", "")[:2] == cc[:2]]
        d_ne = round(min(near), 1) if near else None
        checks[city] = dict(geonameid=gid, gn_name=x["name"], code=x["code"], lat=x["lat"], lon=x["lon"],
                            meta=mc, name_match=ok_name, natural_earth_km=d_ne)
    # GeoNames' Dubai record (292223) lies 17.5 km south of the city centre; use Natural Earth's point,
    # which has GeoNames' As Satwah (385024) 1.2 km away.
    ov = dict(source="Natural Earth", lat=25.231942, lon=55.278029,
              note="GeoNames 292223 is 17.5 km from Natural Earth's Dubai; the Natural Earth point is used "
                   "(GeoNames As Satwah, 385024, is 1.2 km from it)")
    checks["Dubai"].update(ov)
    for k, p in PLACES.items():
        if p["type"] == "city_radius":
            c = checks[p["cities"][0]]
            p["pins"] = [[c["lat"], c["lon"], p["pins"][0][2]]]
        if p["type"] == "country_minus":
            p["pins_excluded"] = [[checks[c]["lat"], checks[c]["lon"], r[2]] for c, r in zip(p["excluded_cities"], p["pins_excluded"])]
    # the one custom pin: Irbid, against GeoNames Irbid
    ir = gn["JO"][248946]
    checks["Irbid pin"] = dict(km_to_geonames_irbid=round(hav(32.549183, 35.860062, ir["lat"], ir["lon"]), 2))
    return checks


# ------------------------------------------------------------------ helpers
def f(x):
    return float(x) if x not in ("NULL", "", None) else 0.0


def ts(s):
    s = s.strip().replace(" ", "T")
    if s.endswith("+00"):
        s += ":00"
    return datetime.fromisoformat(s)


def labels(sid):
    return dict(p.split(":", 1) for p in sid.split(","))


def read_tsv(fn):
    return list(csv.DictReader(open(os.path.join(RAW, fn)), delimiter="\t"))


def read_csv(fn):
    return list(csv.DictReader(open(os.path.join(RAW, fn))))


def median(v):
    return round(statistics.median(v), 2) if v else None


# ------------------------------------------------------------------ form: where the qualifying question sits
def count_path(form, variant, pay_form, q_ref):
    """Questions a respondent sees on the main path (statements, error repeats and unshown branches not
    counted; conditional follow-ups such as 'minutes on those days' counted as shown). Returns
    (position of the qualifying question, total to the end of the payment step)."""
    seen, groups = [], set()
    one_of = [r"^intro_consent", r"^city", r"^nationality", r"^react_community_", r"^pledge_", r"^conditionality_",
              r"^pnb_(sed|vain)$", r"^ne_(sed|vain)$", r"^ee_(sed|vain)$"]
    for x in form["fields"]:
        ref, t = x["ref"], x["type"]
        if t == "statement" or "error" in ref or ref.startswith("conditional_srei"):
            continue
        if ref.startswith("nationality") and variant.startswith("main") and not (
                (variant == "main-ae" and ref.endswith("uae")) or (variant == "main-sa" and ref.endswith("ksa"))):
            continue
        if ref.startswith("condition_"):
            if sum(1 for s in seen if s.startswith("condition_")) >= 2:
                continue
            seen.append(ref)
            continue
        g = next((p for p in one_of if re.match(p, ref)), None)
        if g:
            if g in groups:
                continue
            groups.add(g)
        seen.append(ref)
    if variant.startswith("main"):
        seen = ["language"] + seen
    pay = [x["ref"] for x in pay_form["fields"] if x["type"] != "statement" and "error" not in x["ref"]] if pay_form else []
    if pay and variant.startswith("pilot") is False and variant != "diag":
        pay = [p for p in pay if not p.startswith("recruit_")]
    path = seen + pay
    return path.index(q_ref) + 1 if q_ref in path else None, len(path), path


# ------------------------------------------------------------------ main
def main():
    daily = read_tsv("daily_all.tsv")
    confs = read_csv("confs.csv")
    studies = {r["slug"]: r["id"] for r in read_tsv("studies.tsv")}
    forms = {}
    for r in read_csv("forms.csv"):
        try:
            forms[r["shortcode"]] = json.loads(r["form_json"])
        except json.JSONDecodeError:
            pass
    camp_n = {r["camp"]: int(r["n"]) for r in read_tsv("all_camps.tsv")}

    # people: union of the pools; per variable, the value from the earliest row
    meta = defaultdict(dict)
    for r in read_tsv("pool.tsv"):
        v = r["variable"] if r["variable"] != "Location" else "City"
        cur = meta[r["user_id"]].get(v)
        if cur is None or r["timestamp"] < cur[1]:
            meta[r["user_id"]][v] = (r["v"], r["timestamp"])
    qans, forms_of = defaultdict(dict), defaultdict(set)
    for r in read_tsv("responses.tsv"):
        u, t = r["userid"], ts(r["t"])
        forms_of[u].add(r["shortcode"])
        key = (r["shortcode"], r["question_ref"])
        if key not in qans[u] or t < qans[u][key]:
            qans[u][key] = t

    latest = {}
    for r in confs:
        latest[(r["slug"], r["conf_type"])] = r
    shared = [c for c, n in camp_n.items() if n > 1]

    meta_cities = {}
    cells, crit, pmap, paths = [], [], {}, {}
    report = {}
    for rec in ORDER:
        if rec in EXCLUDED:
            E = EXCLUDED[rec]
            crit.append(OrderedDict(rec=rec, country=E["country"], first=None, last=None, round="excluded",
                                    ads=None, screen=None, who_qualified=None, qualify_rule=None, qualify_point=None,
                                    median_minutes_to_qualify=None, channel="messenger", languages=None, incentive=None,
                                    started=None, qualified=None, notes=E["notes"]))
            pi = INP["recs"][rec]
            spend = sum(f(r["spend"]) for r in daily if r["slug"] in pi["slugs"])
            pmap[rec] = dict(slugs=pi["slugs"], study_ids=[studies[s] for s in pi["slugs"]], excluded=True,
                             insights_spend=round(spend, 2))
            continue
        R, pi = RECS[rec], INP["recs"][rec]
        slugs = pi["slugs"]
        rows = [r for r in daily if r["slug"] in slugs]
        bad = sorted({r["camp"] for r in rows} & set(shared))
        rows = [r for r in rows if r["camp"] not in shared]
        # strata conf (latest) for Meta targeting
        strata_conf = {}
        for s in slugs:
            for x in json.loads(latest[(s, "strata")]["conf"]):
                strata_conf[x["id"]] = x
                for c in x["facebook_targeting"].get("geo_locations", {}).get("cities", []):
                    meta_cities.setdefault(c["name"], dict(key=c["key"], name=c["name"], region=c.get("region"),
                                                                          radius=c.get("radius"), unit=c.get("distance_unit")))
        spend_days = sorted({r["d"] for r in rows if f(r["spend"]) > 0})
        d0, d1 = date.fromisoformat(spend_days[0]), date.fromisoformat(spend_days[-1])
        w0 = datetime.combine(d0 - timedelta(days=1), datetime.min.time(), timezone.utc)
        w1 = datetime.combine(d1 + timedelta(days=4), datetime.min.time(), timezone.utc)
        qre = re.compile(pi["q_shortcodes"])
        ere = re.compile(pi["entry_shortcodes"])
        # a person's first message for this recruitment: their first answer in its own forms
        first = {}
        for u, a in qans.items():
            t = [t for (sc, ref), t in a.items() if ere.search(sc)]
            if t:
                first[u] = min(t)
        by_strat = defaultdict(list)
        for r in rows:
            by_strat[r["strat"]].append(r)

        rec_cells, dropped, qual_people = [], {}, set()
        for sid in sorted(by_strat, key=lambda s: (labels(s).get(R["label"]), labels(s)["Gender"], labels(s)["Age"])):
            L = labels(sid)
            city = L[R["label"]]
            is_dropped = city in R.get("drop", {})
            if is_dropped:
                d = dropped.setdefault(city, dict(spend=0.0, strata=[], started=0, qualified=0))
                d["spend"] += sum(f(r["spend"]) for r in by_strat[sid])
                d["strata"].append(sid)
            phases = R.get("phases", {}).get(city) or [dict(place=R["places"].get(city))]
            # people with these ad labels whose first answer is in the window
            ppl = []
            for u, m in meta.items():
                if (m.get("City", ("",))[0] == city and m.get("Gender", ("",))[0] == L["Gender"]
                        and m.get("Age", ("",))[0] == L["Age"] and u in first and w0 <= first[u] < w1):
                    tq = [t for (sc, ref), t in qans[u].items() if ref in pi["q_refs"] and qre.search(sc) and t >= first[u]]
                    ppl.append((u, first[u], min(tq) if tq else None))
            if is_dropped:  # counted only for the check against the report
                d["started"] += len(ppl)
                d["qualified"] += sum(1 for p in ppl if p[2] is not None)
                continue
            prev_day, prev_time = None, None
            for ph in phases:
                til_d, til_t = ph.get("until_spend_day"), ph.get("until_time")
                til_t = datetime.fromisoformat(til_t) if til_t else None
                drows = [r for r in by_strat[sid] if (prev_day is None or r["d"] > prev_day) and (til_d is None or r["d"] <= til_d)]
                pp = [p for p in ppl if (prev_time is None or p[1] >= prev_time) and (til_t is None or p[1] < til_t)]
                prev_day, prev_time = til_d, til_t
                daysp = defaultdict(float)
                imp = 0.0
                for r in drows:
                    daysp[r["d"]] += f(r["spend"])
                    imp += f(r["imp"])
                pos = sorted(d for d, v in daysp.items() if v > 0)
                q = [p for p in pp if p[2] is not None]
                ft = strata_conf[sid]["facebook_targeting"]
                g = ft.get("genders")
                flags = []
                if ph.get("flag"):
                    flags.append(ph["flag"])
                if len(pp) < 200:
                    flags.append("thin")
                if len(pos) == 1:
                    flags.append("one_day")
                flags += R.get("flags", [])
                cell = OrderedDict(
                    rec=rec, cell=None, country=R["country"], place=ph["place"], side=None,
                    ads=OrderedDict(genders={(1,): "men", (2,): "women"}.get(tuple(g or []), "all"),
                                    age_min=ft.get("age_min"), age_max=ft.get("age_max"),
                                    interests=bool(ft.get("flexible_spec") or ft.get("interests") or ft.get("behaviors"))),
                    person_override=None,
                    first=pos[0] if pos else None, last=pos[-1] if pos else None, spend_days=len(pos),
                    spend_usd=round(sum(daysp.values()), 2), impressions=int(imp),
                    started=len(pp), qualified=len(q),
                    median_daily_spend=median([daysp[d] for d in pos]),
                    median_minutes_to_qualify=median([(p[2] - p[1]).total_seconds() / 60 for p in q]),
                    flags=flags, attribution="ad_metadata")
                cell["_labels"] = OrderedDict(gender=L["Gender"], age=L["Age"], city=city)
                cell["_sid"] = sid
                cell["_q_minutes"] = [(p[2] - p[1]).total_seconds() / 60 for p in q]
                qual_people.update(p[0] for p in q)
                rec_cells.append(cell)
        for i, c in enumerate(rec_cells, 1):
            c["cell"] = f"{rec}/{i:02d}"
        # recruitment record
        qm = [m for c in rec_cells for m in c.pop("_q_minutes")]
        st, qu = sum(c["started"] for c in rec_cells), sum(c["qualified"] for c in rec_cells)
        firsts = [c["first"] for c in rec_cells if c["first"]]
        lasts = [c["last"] for c in rec_cells if c["last"]]
        # languages: forms the starters answered in
        lang_n = defaultdict(int)
        for u in qual_people:
            for lg in {pi["lang_forms"][sc] for sc in forms_of[u] if sc in pi["lang_forms"]}:
                lang_n[lg] += 1
        langs = {lg for lg, n in lang_n.items() if n >= 0.02 * max(1, len(qual_people))}
        # qualify point from the form
        form = forms.get(pi["form"])
        pay_sc = pi.get("pay_form")
        pay_form = forms.get(pay_sc) if pay_sc else None
        if pay_form is None:  # the stitch target at the end of the main-path form
            for x in form["fields"]:
                d = (x.get("properties") or {}).get("description") or ""
                m = re.search(r'"form":\s*"([^"]+)"', d)
                if m:
                    pay_form = forms.get(m.group(1))
        pos_q, total, path = count_path(form, pi["form_variant"], pay_form, pi["q_refs"][0])
        ads_g = sorted({c["ads"]["genders"] for c in rec_cells})
        crit.append(OrderedDict(
            rec=rec, country=R["country"], first=min(firsts), last=max(lasts), round=R["round"],
            ads=OrderedDict(genders=ads_g, age_min=min(c["ads"]["age_min"] for c in rec_cells),
                            age_max=max(c["ads"]["age_max"] for c in rec_cells),
                            interests=any(c["ads"]["interests"] for c in rec_cells)),
            screen=R["screen"], who_qualified=R["who"], qualify_rule=R["rule"],
            qualify_point=OrderedDict(question=pos_q, of=total),
            median_minutes_to_qualify=median(qm), channel="messenger", languages=sorted(langs),
            incentive=R["incentive"], started=st, qualified=qu,
            notes=(R["notes"] + (" Left out: " + "; ".join(f"{k}: {v}" for k, v in R["drop"].items()) +
                                 f" (${sum(d['spend'] for d in dropped.values()):,.2f} of spend)." if dropped else "")
                   + " Question count: questions shown on the main path, including the language choice where there "
                     "is one and conditional follow-ups; statements, error repeats and unshown branches not counted.")))
        # checks against the latest report (written under the rule in force when it ran)
        rep_spend, rep_part, rep_created = 0.0, 0, []
        for s in slugs:
            rr = read_csv(f"adopt-{s}.csv")
            if rr:
                d = json.loads(rr[0]["details"])
                rep_spend += sum(v.get("lifetime_spent", 0) for v in d.values())
                rep_part += sum(v.get("current_participants", 0) for v in d.values())
                rep_created.append(rr[0]["created"][:16])
        ins_all = sum(f(r["spend"]) for r in daily if r["slug"] in slugs)
        cpm = {}
        for r in rows:
            k = labels(r["strat"])[R["label"]]
            a = cpm.setdefault(k, [0.0, 0.0])
            a[0] += f(r["spend"]); a[1] += f(r["imp"])
        report[rec] = OrderedDict(
            cells=len(rec_cells), spend=round(sum(c["spend_usd"] for c in rec_cells), 2),
            spend_dropped=round(sum(d["spend"] for d in dropped.values()), 2),
            insights_spend_all=round(ins_all, 2), report_lifetime_spent=round(rep_spend, 2), report_created=rep_created,
            started=st, qualified=qu, report_participants=rep_part, spend_days=len(spend_days),
            dropped_started=sum(d["started"] for d in dropped.values()),
            dropped_qualified=sum(d["qualified"] for d in dropped.values()),
            languages_qualified=dict(lang_n),
            window=[spend_days[0], spend_days[-1]], shared_campaigns=bad,
            cpm={k: round(1000 * v[0] / v[1], 2) for k, v in cpm.items() if v[1]},
            qualify_path_len=len(path))
        paths[rec] = path
        pmap[rec] = OrderedDict(slugs=slugs, study_ids=[studies[s] for s in slugs],
                                cells={c["cell"]: c["_sid"] for c in rec_cells},
                                dropped={k: v["strata"] for k, v in dropped.items()},
                                qualify_refs=pi["q_refs"], qualify_path=path)
        for c in rec_cells:
            c.pop("_sid")
            c.pop("_labels")
        cells += rec_cells

    checks = fill_pins(meta_cities)
    used = {c["place"] for c in cells}
    places = OrderedDict((k, v) for k, v in PLACES.items() if k in used)
    for k, v in places.items():
        v.pop("cities", None)
        v.pop("excluded_cities", None)
    missing = used - set(places)
    assert not missing, missing

    os.makedirs(OUT, exist_ok=True)
    json.dump(cells, open(os.path.join(OUT, "MENA.cells.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(crit, open(os.path.join(OUT, "MENA.criteria.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(places, open(os.path.join(OUT, "MENA.places.json"), "w"), indent=1, ensure_ascii=False)
    # The private map holds only what identifies a study (slugs, ids, raw stratum ids); the checks go to
    # raw/ so that no date or field name in it can be mistaken for a slug by the merge's leak check.
    for v in pmap.values():
        v.pop("qualify_path", None)
        v.pop("qualify_refs", None)
    PRIVATE["outputs"] = OrderedDict(recs=pmap)
    json.dump(PRIVATE, open(PRIV, "w"), indent=1, ensure_ascii=False)
    json.dump(OrderedDict(generated=str(date.today()), report=report, geo_checks=checks,
                          paths={k: v for k, v in paths.items()}),
              open(os.path.join(RAW, "cells_report.json"), "w"), indent=1, ensure_ascii=False)

    # ------------------------------------------------------------------ print the checks
    for rec, r in report.items():
        print(f"{rec}: cells {r['cells']} spend {r['spend']:,.2f} (+dropped {r['spend_dropped']:,.2f}; insights "
              f"{r['insights_spend_all']:,.2f}; report {r['report_lifetime_spent']:,.2f}) started {r['started']} "
              f"qualified {r['qualified']} (report {r['report_participants']}) days {r['spend_days']} {r['window']} "
              f"cpm {r['cpm']} shared {r['shared_campaigns']}")
    for k, v in checks.items():
        print("geo", k, {kk: vv for kk, vv in v.items() if kk not in ("lat", "lon")})
    for c in crit:
        print("crit", c["rec"], c["qualify_point"], c["median_minutes_to_qualify"], c["languages"])


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        fetch()
    main()
