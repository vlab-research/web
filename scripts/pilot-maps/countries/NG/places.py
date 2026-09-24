#!/usr/bin/env python3
"""Pool stratum evidence (strata_evidence.json, from pipeline.py) into PLACES: targeting geometries.

A place is a geometry signature (included + excluded geo). Two merges, both same towns and
same radius: the 16 + 7 radius areas of 2 km in Yola-Jimeta, and the one 33-mile radius
area around Yola (with or without no-op exclusions of FCT and Nasarawa, which it does not touch).

Cost per starter  = summed Insights spend / people whose first message carried that ad set's metadata.
Cost per qualified = summed spend / people past the recruitment's own final quota rule, pooled only
within one questionnaire ("instrument"); across instruments a place shows each separately.
Writes places.json.
"""
import csv, json, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda f: os.path.join(HERE, f)
ev = json.load(open(P("strata_evidence.json")))
fam = json.load(open(P("fam.json")))
S2F = {s: f for f, v in fam.items() for s in v.values()}

SW6 = ["Ekiti", "Lagos", "Ogun", "Ondo", "Osun", "Oyo"]
GROUPS = {
    ("Abia", "Anambra", "Ebonyi", "Enugu", "Imo"): ("South-East: 5 states together", "group"),
    ("Akwa Ibom", "Bayelsa", "Cross River", "Delta", "Edo", "Rivers"): ("South-South: 6 states together", "group"),
    tuple(SW6): ("South-West: 6 states together", "group"),
    ("Ekiti", "Lagos", "Ogun", "Ondo", "Osun"): ("South-West without Oyo: 5 states together", "group"),
    ("Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Sokoto", "Zamfara"): ("North-West: 7 states together", "group"),
    ("Adamawa", "Bauchi", "Borno", "Gombe", "Taraba", "Yobe"): ("North-East: 6 states together", "group"),
    ("Benué", "Federal Capital Territory", "Kogi", "Kwara", "Nasarawa", "Niger", "Plateau"): ("North-Central with FCT: 7 together", "group"),
    ("Anambra", "Edo", "Federal Capital Territory", "Ogun", "Oyo", "Rivers"): ("FCT, Ogun, Oyo, Anambra, Edo and Rivers together", "group"),
}

# Radius-area sets, named from where the pins land (see pins.json from build.py; GeoNames towns of 20,000+)
PINSETS = {
    (24, 4.02336): ("Abuja and Suleja: 24 radius areas of 4 km", "radius"),
    (19, 4.02336): ("Abuja's south side and Kuje: 19 radius areas of 4 km", "radius"),
    (60, 4.02336): ("Lafia and Keffi: 60 radius areas of 4 km", "radius"),
    (4, 4.02336): ("Karu, on Abuja's edge in Nasarawa: 4 radius areas of 4 km", "radius"),
    (16, 2.011): ("Yola–Jimeta: 23 radius areas of 2 km", "radius"),
    (7, 2.011): ("Yola–Jimeta: 23 radius areas of 2 km", "radius"),
}


def name(geo):
    inc, exc = json.loads(geo)
    exc_regions = set(x.replace(" State", "") for x in (exc or {}).get("regions", []))
    exc_pins = (exc or {}).get("custom_locations", [])
    if inc.get("places"):
        return ("EXCLUDED: Meta place 'Kirfi LGA' pinned 67 km from Kirfi", "excluded")
    if inc.get("cities"):
        c = inc["cities"][0]
        return (f"{c[0]}: one radius area of {c[2]} miles ({round(c[2] * 1.609344)} km)", "radius")
    if inc.get("countries"):
        if sorted(exc_regions) == SW6:
            return ("Nigeria outside the 6 South-West states", "country")
        return ("Nigeria, whole country", "country")
    if inc.get("custom_locations"):
        pins = inc["custom_locations"]
        if len(pins) == 1:
            lat, lon, r, u = pins[0]
            if round(lat, 2) == 9.14:
                return ("Yola–Jimeta: one radius area of 53 km", "radius")
            if round(lat, 2) == 8.87:
                return ("South-west of Abuja around Kuje: one radius area of 19 km", "radius")
            if round(lat, 2) == 10.14:
                return ("Toro: one radius area of 16 km", "radius")
            return (f"one pin {lat},{lon} r{r}{u}", "radius")
        if len(pins) == 2 and pins[0][2] == 15:
            return ("Nasarawa town and Akwanga: 2 radius areas of 24 km", "radius")
        return PINSETS[(len(pins), pins[0][2])]
    regs = tuple(sorted(x.replace(" State", "") for x in inc.get("regions", [])))
    if len(regs) == 1:
        st = regs[0].replace(" State", "")
        st = "Federal Capital Territory" if st.startswith("Federal") else st
        if exc_pins:
            if st == "Federal Capital Territory":
                return ("FCT outside the radius area around Kuje", "state_minus")
            if st == "Nasarawa":
                return ("Nasarawa outside the Nasarawa-town and Akwanga radius areas", "state_minus")
            if st == "Adamawa":
                return ("Adamawa outside the Yola–Jimeta radius area", "state_minus")
        return (f"{st} (whole state)" if st != "Federal Capital Territory" else "FCT (whole territory)", "state")
    if regs in GROUPS:
        return GROUPS[regs]
    if set(regs) == {"Anambra State", "Bauchi State"} or set(regs) == {"Anambra", "Bauchi"}:
        return ("EXCLUDED: Anambra and Bauchi in one ad set ($20)", "excluded")
    if len(regs) == 16:
        return ("16 southern states together", "group")
    return (" + ".join(regs), "group")


# One questionnaire per recruitment, except the 15-16-question surveys, which are one instrument
# fielded five times with the same screen and the same final question.
INSTR = {
    "2024-oct-short-1": "S15", "2024-oct-short-2": "S15", "2025-feb-short-mid": "S15", "2025-apr-c2": "S15",
}
WHO = {
    "S15": "cares for a girl aged 9–17 and answered a 15–16-question survey",
    "2023-six-states": "cares for a girl aged 9–17 and answered all 35 questions (ads to ages 30–50)",
    "2023-lagos-kano/dkt-study-nigeria": "any adult who reached question 22 of 29 (ads to ages 18–35)",
    "2023-lagos-kano/dkt_nigeria_test": "reached question 27 of 29, which only some were asked (ads to ages 18–49)",
    "2024-sep-three-states": "cares for a girl aged 9–17 and answered all 31 questions (ads to ages 25–55)",
    "2024-sep-long": "cares for a girl aged 9–17 and answered 27 of 31 questions",
    "2025-feb-long-mid": "cares for a girl aged 9–17 and answered 28 of 31 questions",
    "2025-nov-c2-end": "cares for a girl aged 9–17 and answered all 21 questions",
    "2025-may-signup": "left a phone number on a one-question sign-up",
    "2025-country-llm": "any adult who finished a 53-question survey and gave a number for payment",
    "2025-dec-hpvv": "a parent or caregiver who finished a 55-question survey and gave a number for payment (ads to ages 27–65)",
    "2025-dec-mr-test": "answered 97 of 98 questions (ads to ages 18–55)",
    "2026-jan-mr": "a parent or caregiver of a child aged 6–14 who answered 41 of 42 questions (ads to ages 18–55)",
    "2026-feb-bauchi-ct": "a parent or caregiver of a child aged 9–14 who finished a 12-question survey and gave a number for payment",
    "2026-apr-bauchi-pilot": "an adult with a daughter aged 9–14 at home who finished a 34-question survey and gave a number for payment (ads to ages 20–55)",
    "2026-apr-nstudy": "a parent or caregiver who answered all 55 questions (ads to ages 27–65)",
    "2026-may-bauchi-mnch": "an adult with a daughter aged 9–14 at home who finished a 38-question survey and gave a number for payment",
    "2026-ecd": "an adult who answered all 131 questions (ads to ages 25–65)",
    "2026-mentality": "an adult who reached question 38 of a 48-question follow-up (ads to ages 18–65)",
    "2026-owis": "a parent or caregiver who answered all 55 questions (ads to ages 36–65)",
}


def instr(r):
    f = r["family"]
    if f in INSTR:
        return INSTR[f]
    if f == "2023-lagos-kano":
        return f"{f}/{r['study']}"
    return f


# conversations (Meta-counted), deduped per family x campaign x stratum x day, summed per family x stratum id
best = {}
for r in csv.DictReader(open(P("insights_daily.tsv")), delimiter="\t"):
    k = (S2F[r["sid"]], r["camp"], r["strat"], r["d"])
    c = float(r["conv"]) if r["conv"] not in ("", "NULL") else None
    if k not in best or (c or 0) > (best[k] or 0):
        best[k] = c
convs = collections.defaultdict(float)
has_conv = collections.defaultdict(bool)
for (f, camp, strat, d), c in best.items():
    if c is not None:
        convs[(f, strat)] += c
        has_conv[(f, strat)] = True

places = collections.OrderedDict()
gender = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0]))
excluded = collections.defaultdict(lambda: dict(spend=0.0, starters=0, families=set()))
for r in ev["rows"]:
    if not r["geo"]:
        continue
    nm, kind = name(r["geo"])
    if kind == "excluded":
        e = excluded[nm]; e["spend"] += r["spend"]; e["starters"] += r["starters"]; e["families"].add(r["family"])
        continue
    p = places.setdefault(nm, dict(name=nm, kind=kind, spend=0.0, starters=0, days=set(), families=set(),
                                   studies=set(), instruments=collections.defaultdict(lambda: [0.0, 0, 0]),
                                   by_family=collections.defaultdict(lambda: [0.0, 0, 0]), geos=set(),
                                   conv=0.0, conv_starters=0))
    p["spend"] += r["spend"]; p["starters"] += r["starters"]
    p["days"].update(r["days"]); p["families"].add(r["family"]); p["studies"].add(r["study"]); p["geos"].add(r["geo"])
    i = p["instruments"][instr(r)]; i[0] += r["spend"]; i[1] += r["starters"]; i[2] += r["qualified"]
    bf = p["by_family"][r["family"]]; bf[0] += r["spend"]; bf[1] += r["starters"]; bf[2] += r["qualified"]
    if r.get("meta_conversations") is not None:
        p["conv_starters"] += r["starters"]
        p["conv"] += r["meta_conversations"]
    g = r["genders"]
    if g in ([1], [2]):
        gender[(r["family"], nm)][g[0]][0] += r["spend"]
        gender[(r["family"], nm)][g[0]][1] += r["starters"]

out = []
for p in places.values():
    days = sorted(p["days"])
    rows_i = []
    for k, (sp, st, q) in sorted(p["instruments"].items()):
        rows_i.append(dict(instrument=k, who=WHO[k], spend=round(sp, 2), starters=st, qualified=q,
                           cost_per_qualified=round(sp / q, 2) if q else None))
    fams = {f: dict(spend=round(v[0], 2), starters=v[1], qualified=v[2]) for f, v in sorted(p["by_family"].items())}
    top = max(fams.values(), key=lambda v: v["spend"])
    out.append(dict(
        name=p["name"], kind=p["kind"], spend=round(p["spend"], 2), starters=p["starters"],
        cost_per_starter=round(p["spend"] / p["starters"], 2) if p["starters"] else None,
        first_day=days[0] if days else None, last_day=days[-1] if days else None, ad_days=len(days),
        recruitments=len(p["families"]), families=sorted(p["families"]), studies=sorted(p["studies"]),
        qualified_by_instrument=rows_i, by_recruitment=fams,
        largest_recruitment_share_of_spend=round(top["spend"] / p["spend"], 2) if p["spend"] else None,
        meta_conversations=round(p["conv"]), starters_where_conversations_recorded=p["conv_starters"],
        thin=p["starters"] < 200, shown=p["starters"] >= 50))
out.sort(key=lambda x: (x["kind"], -(x["starters"])))

# gender: only place x recruitment cells where both a men-only and a women-only ad set ran
gt = {1: [0.0, 0], 2: [0.0, 0]}
cells = 0
for k, v in gender.items():
    if v[1][1] and v[2][1]:
        cells += 1
        for g in (1, 2):
            gt[g][0] += v[g][0]; gt[g][1] += v[g][1]
gender_out = dict(cells=cells, men=dict(spend=round(gt[1][0], 2), starters=gt[1][1], cost_per_starter=round(gt[1][0] / gt[1][1], 2)),
                  women=dict(spend=round(gt[2][0], 2), starters=gt[2][1], cost_per_starter=round(gt[2][0] / gt[2][1], 2)),
                  note="pooled over place x recruitment cells where ads ran separately to men and to women in the same place")
json.dump(dict(places=out, gender=gender_out,
               excluded={k: dict(spend=round(v["spend"], 2), starters=v["starters"], families=sorted(v["families"])) for k, v in excluded.items()}),
          open(P("places.json"), "w"), indent=1, ensure_ascii=False)
for p in out:
    q = "; ".join(f'{i["cost_per_qualified"]}' for i in p["qualified_by_instrument"])
    print(f'{p["kind"]:11} {p["name"][:58]:58} ${p["spend"]:9.2f} {p["starters"]:6d} ${p["cost_per_starter"] or 0:6.2f} | q {q} | {p["first_day"]}..{p["last_day"]} r{p["recruitments"]} top{p["largest_recruitment_share_of_spend"]} conv {p["meta_conversations"]}/{p["starters_where_conversations_recorded"]}')
print(json.dumps(gender_out))
print(json.dumps({k: dict(spend=round(v["spend"], 2), starters=v["starters"]) for k, v in excluded.items()}))
