#!/usr/bin/env python3
"""Bangladesh country page (D-032 pilot, recipe notes/country-recipe.md). Scratch work.

    ../../geo/venv/bin/python build.py            # uses adopt_study1.tsv as fetched
    ../../geo/venv/bin/python build.py --fetch    # re-fetch the adopt report first (SELECT only)

Writes, into this directory:
  bangladesh-2023-divisions.svg   the map (seven whole divisions, ad cost per qualified respondent)
  bangladesh-2023-divisions.png   one light-theme review render
  country-bd.json                 the data file, recipe shape

Inputs: ../../confs.tsv (latest strata conf per study), adopt_study1.tsv (latest
FACEBOOK_ADOPT report for bangladesh-study-1, fetched 2026-09-24), and the helpers in
../../geo/build_maps.py (Natural Earth 10m admin-1, which for Bangladesh is the same
seven divisions Meta offers as regions).
"""
import csv, json, os, re, subprocess, sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
SP = os.path.dirname(os.path.dirname(HERE))
GEO = os.path.join(SP, "geo")
sys.path.insert(0, GEO)
import build_maps as bm  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

csv.field_size_limit(10**9)
SID = "079dd448-f42d-4102-870c-34dedc7ecf0a"   # bangladesh-study-1
SLUG = "bangladesh-study-1"
ADOPT = os.path.join(HERE, "adopt_study1.tsv")

if "--fetch" in sys.argv:
    sql = (f"select created, report_type, details from adopt_reports where study_id='{SID}' "
           "and report_type='FACEBOOK_ADOPT' order by created desc limit 1")
    out = subprocess.run(["kubectl", "exec", "-n", "vprod", "gbv-cockroachdb-0", "--", "/cockroach/cockroach",
                          "sql", "--insecure", "--format=tsv", "--database=vlab", "-e", sql],
                         check=True, capture_output=True, text=True).stdout
    open(ADOPT, "w").write(out)

# ------------------------------------------------------------------ targeting (strata conf)
strata = None
for r in csv.DictReader(open(os.path.join(SP, "confs.tsv")), delimiter="\t"):
    if r["study_id"] == SID and r["conf_type"] == "strata":
        strata = (r["created"], json.loads(r["conf"]))
conf_created, strata = strata
assert len(strata) == 14
META_DIV = {}   # stratum Division label -> Meta region name
for s in strata:
    ft = s["facebook_targeting"]
    g = {k: v for k, v in ft["geo_locations"].items() if k != "location_types"}
    assert list(g) == ["regions"] and len(g["regions"]) == 1, s["id"]
    assert "genders" not in ft, "gender ad sets were not gender-targeted; if this changes, revisit the pooling"
    assert (ft["age_min"], ft["age_max"]) == (25, 45)
    assert s["question_targeting"]["vars"][-1] == {"op": "answered", "vars": [{"type": "variable", "value": "seenads"}]}
    META_DIV[bm.part(s["id"], "Division")] = g["regions"][0]["name"].replace(" Division", "")

# ------------------------------------------------------------------ adopt report
row = list(csv.reader(open(ADOPT), delimiter="\t"))[1]
report_created, rep = row[0], json.loads(row[2])
assert set(rep) == {s["id"] for s in strata}

INSIGHTS_SPEND = 5909.92       # recruitment_data_events, one campaign, 14 ad sets (spend.sql)
AD_DAYS, D0, D1 = 22, "2023-11-30", "2023-12-21"
STARTED = 24624                # distinct users with the study's own ad-set metadata (Age = 'Age all')

tot_s = sum(v["lifetime_spent"] for v in rep.values())
tot_n = sum(v["current_participants"] for v in rep.values())
assert round(tot_s, 2) == INSIGHTS_SPEND, tot_s
assert tot_n == 2878

div = OrderedDict()
for k, v in rep.items():
    d = META_DIV[bm.part(k, "Division")]
    a = div.setdefault(d, dict(spend=0.0, qualified=0))
    a["spend"] += v["lifetime_spent"]
    a["qualified"] += v["current_participants"]
rows = sorted(({"division": d, "spend": round(a["spend"], 2), "qualified": a["qualified"],
                "cost": round(a["spend"] / a["qualified"], 2)} for d, a in div.items()), key=lambda r: r["cost"])
EXPECT = {"Dhaka": (601.69, 590), "Chittagong": (821.98, 607), "Khulna": (707.16, 336), "Sylhet": (788.64, 357),
          "Rajshahi": (814.54, 358), "Rangpur": (921.90, 364), "Barisal": (1254.01, 266)}
for r in rows:
    assert (r["spend"], r["qualified"]) == EXPECT[r["division"]], r

# ------------------------------------------------------------------ map
units = bm.admin1("BGD", "name")
assert set(units) == set(EXPECT), units.keys()
country = unary_union(list(units.values()))
W = 760
MAPBOX = (0, 26, 440, 470)
body = [bm.text(0, 12, "Bangladesh, 2023 · seven divisions, each targeted whole", "gm-eye")]
f = bm.Frame(90.3, 23.7, country, MAPBOX, pad=4)
byname = {r["division"]: r for r in rows}
# finer steps than Nigeria's (whose $1-3 band would hold six of the seven divisions here)
STEPS = [(1.5, ".25", "under $1.50"), (3.0, ".55", "$1.50–3"), (1e9, "1", "$3 or more")]
step = lambda c: next(s for s in STEPS if c < s[0])
for name, g in units.items():
    r = byname[name]
    body.append(bm.path(f.g(g, simplify=0.3), "gm-circ",
                        f' fill-opacity="{step(r["cost"])[1]}" style="stroke-width:.8"'))
body.append(bm.path(f.g(country, simplify=0.3), "gm-outline"))
# label offsets (px) from each division's representative point; lead line where the label leaves the unit
LAB = {"Rangpur": (0, 0, "middle", None), "Rajshahi": (-6, 4, "middle", None), "Dhaka": (4, 18, "middle", None),
       "Sylhet": (4, 0, "middle", None), "Khulna": (-4, 20, "middle", None), "Barisal": (0, 6, "middle", None),
       "Chittagong": (40, 4, "middle", None)}
for r in rows:
    g = units[r["division"]]
    rp = g.representative_point()
    px, py = f.xy(rp.x, rp.y)
    dx, dy, an, lead = LAB[r["division"]]
    tx, ty = px + dx, py + dy
    if lead:
        body.append(f'<path class="gm-lead" d="M{px:.1f},{py:.1f}L{tx:.1f},{ty - 12:.1f}"/>')
    body.append(bm.text(tx, ty - 2, r["division"], "gm-lab gm-halo", an))
    body.append(bm.text(tx, ty + 12, bm.money(r["cost"]), "gm-val gm-halo", an))
body.append(bm.scalebar(10, MAPBOX[1] + MAPBOX[3] - 10, f, 100))

x0, y0 = 480, 40
body.append(bm.text(x0, 12, "Ad cost per qualified respondent", "gm-eye"))
bw = W - (x0 + 84) - 62
mx = max(r["cost"] for r in rows)
for i, r in enumerate(rows):
    y = y0 + i * 50
    body.append(bm.text(x0, y + 10, r["division"], "gm-lab"))
    L = max(2.0, bw * r["cost"] / mx)
    op = step(r["cost"])[1]
    body.append(f'<rect class="gm-bar" x="{x0 + 84}" y="{y}" width="{L:.1f}" height="12" fill-opacity="{op}"/>')
    body.append(bm.text(x0 + 84 + L + 6, y + 10.5, bm.money(r["cost"]), "gm-val"))
    body.append(bm.text(x0, y + 27, f'{r["qualified"]:,} qualified · {bm.money(r["spend"])}', "gm-tiny"))
yl = y0 + len(rows) * 50 + 6
body.append(bm.text(x0, yl, "Fill, by cost per qualified respondent", "gm-tiny"))
xx = x0
for _, op, lab in STEPS:
    body.append(f'<rect class="gm-bar" x="{xx}" y="{yl + 8}" width="12" height="10" fill-opacity="{op}"/>')
    body.append(bm.text(xx + 16, yl + 17, lab, "gm-tiny"))
    xx += 16 + 6.3 * len(lab) + 12
yn = MAPBOX[1] + MAPBOX[3] + 20
for i, line in enumerate([
        "30 Nov – 21 Dec 2023. Each division was targeted whole (a Meta region), so the coloured area is the real",
        "targeting area. Meta lists seven divisions; Mymensingh, split from Dhaka in 2015, is drawn inside Dhaka.",
        "Both ad sets in each division (one with creatives for women, one for men) are pooled."]):
    body.append(bm.text(0, yn + 16 * i, line, "gm-note"))
H = yn + 40
svg = bm.svg(W, H, "Bangladesh, 2023: advertising cost per qualified respondent in seven whole divisions",
             "Seven divisions each targeted whole, 30 November to 21 December 2023. Ad cost per qualified respondent: "
             + ", ".join(f'{r["division"]} {bm.money(r["cost"])}' for r in rows) + ".", body, "bd23")
open(os.path.join(HERE, "bangladesh-2023-divisions.svg"), "w").write(svg)
print("wrote bangladesh-2023-divisions.svg", f"{len(svg) / 1024:.0f} KB")

# ------------------------------------------------------------------ PNG (light tokens, private fontconfig)
TOK = {"--ink": "#1F272E", "--ink-2": "#4A555E", "--ink-3": "#79858D", "--rule": "#CFD9DD", "--rule-2": "#AEBCC2",
       "--surface": "#FFFFFF", "--sunk": "#E5EBED", "--paper": "#F1F4F5", "--data": "#1D5F6E",
       "--data-2": "#9DB6BC", "--brass": "#7A5C1E"}
tmp = os.path.join(HERE, "_render.svg")
open(tmp, "w").write(re.sub(r"var\((--[a-z0-9-]+)\)", lambda m: TOK[m.group(1)], svg))
subprocess.run(["rsvg-convert", "-w", str(W * 2), "-b", TOK["--paper"], "-o",
                os.path.join(HERE, "bangladesh-2023-divisions.png"), tmp], check=True,
               env=dict(os.environ, FONTCONFIG_FILE=os.path.join(GEO, "fonts.conf")))
os.remove(tmp)

# ------------------------------------------------------------------ data file
RULES = json.load(open("/home/nandan/Documents/vlab-research/vlab.digital/scripts/data/country-id.json"))["_meta"]
meta = OrderedDict(RULES)
meta["generated"] = "2026-09-24"
meta["queries"] = "scripts/data/country-queries.sql; spend.sql in this directory (per-campaign spend, CPM, ad days)"
meta["terms"] = {k: v for k, v in RULES["terms"].items() if k != "whole_state"}
meta["terms"]["whole_division"] = ("ads shown to people Meta places anywhere inside the division (a Meta region). "
                                   "Meta offers seven Bangladeshi divisions; Mymensingh, created from Dhaka in 2015, is not one of them")

by_gender_adset = {}
for k, v in rep.items():
    a = by_gender_adset.setdefault(bm.part(k, "Gender"), [0.0, 0])
    a[0] += v["lifetime_spent"]; a[1] += v["current_participants"]

out = OrderedDict(
    _meta=meta,
    country="BD",
    all_people_surveyed=dict(unique_people=49986, first="2023-11-08", last="2024-12-22", studies=18,
                             note="Distinct user_id in inference_data across every Bangladesh study on the current "
                                  "platform, tests and endlines included. Anyone who answered in any of them."),
    study=OrderedDict(
        slug=SLUG, fielded="30 Nov – 21 Dec 2023", ad_days=AD_DAYS, started_survey=STARTED, qualified=tot_n,
        spend=INSIGHTS_SPEND, report_spend=round(tot_s, 2), cost=round(tot_s / tot_n, 2), incentive_usd=None,
        incentive_note="none in the study configuration (no incentive_per_respondent; no payment field in the form)",
        channel="Messenger", ad_account_currency="USD (CPM $0.31)",
        campaign_objective="MESSAGES, optimised for replies",
        quota_rule=("in a quota group and answered the 'seen HPV vaccine ads in the last 3 months' question, "
                    "question 48 of 52. The form screens out anyone who does not consent, does not care for a girl, "
                    "or cares for a girl under 9 or over 17, in the first seven questions"),
        quotas="Division (7, whole Meta regions) × two ad sets (women's and men's creatives, NOT gender-targeted): 14 equal groups",
        meta_age_targeting="25–45",
        target_max_sample=4200,
        strata_conf_created=conf_created, report_created=report_created),
    by_division={r["division"]: dict(spend=r["spend"], qualified=r["qualified"], cost=r["cost"]) for r in rows},
    by_gender_adset_not_for_publication=dict(
        note=("The two 'Gender' ad sets were not restricted by gender on Meta (no genders key; the Gender variable's "
              "facebook_targeting is empty). Self-reported gender among qualified: 'Men' ad sets 629 women / 843 men; "
              "'Women' ad sets 689 women / 761 men. So these are creative versions, not genders. Do not publish."),
        **{k: dict(spend=round(a[0], 2), qualified=a[1], cost=round(a[0] / a[1], 2)) for k, a in by_gender_adset.items()}),
    strata=[dict(id=k, current_participants=v["current_participants"], lifetime_spent=v["lifetime_spent"],
                 current_price_per_participant=v["current_price_per_participant"]) for k, v in sorted(rep.items())],
    checks=[
        "per-group lifetime_spent sums to $5,909.92, exactly Meta's reported spend for the one campaign",
        "ad account 272226257305969 (all 18 Bangladesh studies): CPM $0.23–0.62, so US dollars, not taka",
        "targeting saved 21 Nov 2023, before the first ad day (30 Nov); the 11 Dec re-save is identical",
        "1,000 respondents from the 8–12 Nov test run share this study's inference data under different labels "
        "('All Age', 'Rangpour'); none match a stratum id, so none are counted as qualified",
        "24,624 people started from the study's ads; 2,878 qualified (11.7%)",
    ],
    held_for_review=OrderedDict(
        hpv_baseline_2024=OrderedDict(
            studies=["bangladesh-hpv-baseline (campaign 'T3')", "bangladesh-hpv-baseline-t1",
                     "bangladesh-hpv-baseline-t2", "bangladesh-hpv-baseline-t4"],
            fielded="30 Sep – 10 Oct 2024", ad_days=11,
            design=("one survey (BDTBaselineBangla), four concurrent ad runs, one per trial arm; each run targets "
                    "its own set of 1 km radius areas (about 980 pins in total) in Chittagong, Barisal and Sylhet"),
            spend=1296.46, qualified=1101, cost=1.18,
            by_group={"Chittagong, women 25–45": [74.74, 148, 0.50], "Chittagong, men 30–50": [130.71, 278, 0.47],
                      "Barisal, women 25–45": [78.15, 120, 0.65], "Barisal, men 30–50": [511.01, 230, 2.22],
                      "Sylhet, women 25–45": [227.16, 112, 2.03], "Sylhet, men 30–50": [274.69, 213, 1.29]},
            why_held=["the candidate figure '$797, 1,101 qualified' for -t2 alone is double-counted: all four arms' "
                      "reports carry the same 1,101 qualified (the survey-wide pool); combined it is $1,296 for 1,101",
                      "radius areas only, no 'outside' side, so no within-study place comparison",
                      "Meta places 2 of the pins in India (country 'IN'); the pins were not otherwise checked",
                      "set against 2023 it invites a cross-year comparison that cannot be explained: the 2024 survey "
                      "is shorter (qualifying question 33 of 36, not 48 of 52) and used a different campaign objective"]),
    ),
    excluded_for_review=OrderedDict(
        follow_up_waves=[
            "remaining-divisions-bangladesh-hpv-endline (13–22 Dec 2024, $807.64, 3,366 qualified, $0.24; whole Dhaka, "
            "Khulna, Rajshahi, Rangpur). NOTE: a fresh ad-recruited cross-section, not a re-contact: only 564 of its "
            "10,110 people were in an earlier Bangladesh study. Passes every other mechanical rule",
            "t1-, t2-, t3-, t4-bangladesh-hpv-endline (13–22 Dec 2024, $378, $448, $579, $308; 1 km radius areas)",
        ],
        under_7_ad_days=[
            "bangladesh-survey-1-test (4 days, $187)",
            "bangladesh-baseline-remaining-divisions (3 days, $307; 1,007 qualified, whole Khulna, Rajshahi, Rangpur)",
            "bangladesh-baseline-test (3 days, $53)", "bangladesh-baseline-test-2 (2 days, $13)",
            "bangladesh-baseline-survey-test-t1, -t2, -t3 (6, 6, 2 days; $54, $55, $1)",
        ],
        under_500_or_200=["all the tests above", "bangladesh-hpv-baseline-t1/-t4 alone ($345, $13): combined with siblings, see held_for_review"],
        shared_campaign=["bangladesh-baseline-test and -test-2 share campaign 'Bangla HPV Baseline TEST'"],
        no_ad_spend=["bangladesh-baseline-survey-test-t4"],
        umbrella_double_count=["the four 2024 baseline arms each report the same 1,101 qualified (see held_for_review)"],
    ),
    strata_note="Stratum ids are the study's own labels ('Khula' = Khulna). Meta region names are used on the page: "
                "Barisal and Chittagong, officially Barishal and Chattogram since 2018.",
)
json.dump(out, open(os.path.join(HERE, "country-bd.json"), "w"), indent=1, ensure_ascii=False)
print("wrote country-bd.json")
for r in rows:
    print(f'  {r["division"]:11s} {r["qualified"]:5d} {r["spend"]:9.2f} {r["cost"]:6.2f}')

# ------------------------------------------------------------------ section fragment
tpl = open(os.path.join(HERE, "section.tpl.html")).read()
trs = "\n".join(f'        <tr><td>{r["division"]}</td><td class=n>{r["qualified"]:,}</td>'
                f'<td class=n>${r["spend"]:,.0f}</td><td class=n>{bm.money(r["cost"])}</td></tr>' for r in rows)
html = tpl.replace("{{BD2023}}", svg.strip()).replace("{{BDROWS}}", trs)
assert "{{" not in html
open(os.path.join(HERE, "section.html"), "w").write(html)
print("wrote section.html")
