#!/usr/bin/env python3
"""Nigeria place page (D-032, recipe "The unit is the place, not the study").

    ../../geo/venv/bin/python build.py

1. pipeline.py  -> strata_evidence.json, people.tsv   (every stratum of every cleaned recruitment)
2. places.py    -> places.json                          (pooled by targeting geometry)
3. this file    -> nigeria-states.svg, nigeria-radius.svg, country-ng.json, section.html

All inputs are read-only pulls from vprod saved in this directory (see pipeline.py's docstring).
"""
import csv, json, os, subprocess, sys, html
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.normpath(os.path.join(HERE, "..", "..", "geo"))
sys.path.insert(0, GEO)
import build_maps as bm  # noqa: E402
from shapely.geometry import Point, box  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

P = lambda f: os.path.join(HERE, f)
for step in ("pipeline.py", "places.py"):
    subprocess.run([sys.executable, P(step)], check=True, stdout=subprocess.DEVNULL)
PL = json.load(open(P("places.json")))
EV = json.load(open(os.path.join(HERE, "raw", "strata_evidence.json")))
places = [p for p in PL["places"] if p["shown"]]
byname = {p["name"]: p for p in PL["places"]}

STEPS = [(0.5, ".2", "under $0.50"), (1.5, ".42", "$0.50–1.50"), (5.0, ".68", "$1.50–5"), (1e9, "1", "$5+")]


def step(c):
    return next(s for s in STEPS if c < s[0])


def money(x):
    return f"${x:,.2f}"


def geos_of(name):
    out = []
    for r in EV["rows"]:
        if r["geo"] and name_of(r["geo"]) == name:
            out.append(json.loads(r["geo"]))
    return out


sys.path.insert(0, HERE)
import places as PLmod  # noqa: E402  (re-runs quickly; gives name())
name_of = lambda g: PLmod.name(g)[0]

units = bm.admin1("NGA", "name")
NE = {"FCT": "Federal Capital Territory", "Nasarawa": "Nassarawa"}
country = unary_union(list(units.values()))

# ------------------------------------------------------------------ map 1: whole states
state_places = [p for p in places if p["kind"] == "state"]
W = 760
body = [bm.text(0, 12, "Nigeria · whole states, advertising cost per person who started", "gm-eye")]
f = bm.Frame(8.1, 9.1, country, (0, 26, 470, 410), pad=4)
st_of = {}
for p in state_places:
    nm = p["name"].split(" (")[0]
    st_of[NE.get(nm, nm)] = p
for n, g in units.items():
    p = st_of.get(n)
    if p:
        body.append(bm.path(f.g(g, simplify=0.3), "gm-circ", f' fill-opacity="{step(p["cost_per_starter"])[1]}" style="stroke-width:.8"'))
    else:
        body.append(bm.path(f.g(g, simplify=0.3), "gm-ctx"))
body.append(bm.path(f.g(country, simplify=0.3), "gm-outline"))
LAB = {"Sokoto": (0, 0, "middle", 0), "Kano": (-50, -20, "end", 1), "Niger": (0, 6, "middle", 0),
       "Bauchi": (0, 0, "middle", 0), "Adamawa": (0, 0, "middle", 0), "Federal Capital Territory": (-46, 30, "end", 1),
       "Nassarawa": (40, 36, "start", 1), "Lagos": (-30, 44, "middle", 1), "Rivers": (58, 22, "start", 1),
       "Anambra": (70, -10, "start", 1)}
for n, p in st_of.items():
    g = units[n]
    rp = g.centroid if n in ("Niger",) else g.representative_point()
    px, py = f.xy(rp.x, rp.y)
    dx, dy, an, lead = LAB[n]
    tx, ty = px + dx, py + dy
    if lead:
        body.append(f'<path class="gm-lead" d="M{px:.1f},{py:.1f}L{tx:.1f},{ty - 12 if dy > 0 else ty - 4:.1f}"/>')
    short = "FCT" if n.startswith("Federal") else ("Nasarawa" if n == "Nassarawa" else n)
    body.append(bm.text(tx, ty - 2, short, "gm-lab gm-halo", an))
    body.append(bm.text(tx, ty + 12, money(p["cost_per_starter"]), "gm-val gm-halo", an))
body.append(bm.scalebar(10, 26 + 410 - 10, f, 200))
x0, y0 = 500, 40
body.append(bm.text(x0, 12 + 14, "Per person who started", "gm-tiny"))
rows = sorted(state_places, key=lambda p: p["cost_per_starter"])
mx = max(p["cost_per_starter"] for p in rows)
bw = 760 - (x0 + 78) - 58
for i, p in enumerate(rows):
    y = y0 + i * 38
    nm = p["name"].split(" (")[0]
    body.append(bm.text(x0, y + 10, nm, "gm-lab"))
    L = max(2.0, bw * p["cost_per_starter"] / mx)
    body.append(f'<rect class="gm-bar" x="{x0 + 78}" y="{y}" width="{L:.1f}" height="12" fill-opacity="{step(p["cost_per_starter"])[1]}"/>')
    body.append(bm.text(x0 + 78 + L + 6, y + 10.5, money(p["cost_per_starter"]), "gm-val"))
    body.append(bm.text(x0, y + 25, f'{p["starters"]:,} started · {p["first_day"][:4]}' + (f'–{p["last_day"][:4]}' if p["last_day"][:4] != p["first_day"][:4] else ""), "gm-tiny"))
yl = y0 + len(rows) * 38 + 4
for k, (_, op, lab) in enumerate(STEPS):
    xx, yy = x0 + (k % 2) * 130, yl + (k // 2) * 16
    body.append(f'<rect class="gm-bar" x="{xx}" y="{yy}" width="12" height="10" fill-opacity="{op}"/>')
    body.append(bm.text(xx + 15, yy + 9, lab, "gm-tiny"))
yn = max(26 + 410 + 22, yl + 44)
for i, line in enumerate(["Each coloured state was targeted whole (a Meta region). Every recruitment that targeted it is pooled:",
                          "spend summed, people summed. Groups of states and the whole country are in the table below."]):
    body.append(bm.text(0, yn + 16 * i, line, "gm-note"))
H = yn + 26
svg1 = bm.svg(W, H, "Nigeria: advertising cost per person who started the survey, in ten whole-state targets, 2023–2026",
              "; ".join(f'{p["name"].split(" (")[0]} {money(p["cost_per_starter"])} ({p["starters"]:,} started)' for p in rows) + ".",
              body, "ngst")
open(P("nigeria-states.svg"), "w").write(svg1)

# ------------------------------------------------------------------ map 2: radius areas
rad = [p for p in places if p["kind"] == "radius"]


def shapes(name):
    polys = []
    for inc, exc in geos_of(name):
        if inc.get("custom_locations"):
            for lat, lon, r, u in inc["custom_locations"]:
                polys.append(bm.circle(lon, lat, r * (bm.MI if u == "mile" else 1.0)))
        if inc.get("cities"):
            for c in inc["cities"]:
                gc = bm.geocode("NG", c[0], "46")
                polys.append(bm.circle(gc["lon"], gc["lat"], c[2] * bm.MI))
    return unary_union(polys)


SH = {p["name"]: shapes(p["name"]) for p in rad}
body = [bm.text(0, 12, "Nigeria · radius areas, advertising cost per person who started", "gm-eye")]
panels = [
    ("Abuja, Nasarawa", (0, 26, 470, 300), (6.85, 8.15, 8.95, 9.45), ["Federal Capital Territory", "Nassarawa"]),
    ("Yola–Jimeta", (490, 26, 270, 140), (12.0, 8.8, 13.05, 9.55), ["Adamawa"]),
    ("Bauchi State", (490, 186, 270, 140), (8.6, 9.7, 11.1, 12.5), ["Bauchi"]),
]
KEY = OrderedDict()
code = iter("ABCDEFGHIJKLMNOP")
order = sorted(rad, key=lambda p: p["cost_per_starter"])
for p in order:
    KEY[p["name"]] = next(code)
f0 = None
for title, bx, (lo0, la0, lo1, la1), sts in panels:
    fitb = box(lo0, la0, lo1, la1)
    fr = bm.Frame((lo0 + lo1) / 2, (la0 + la1) / 2, fitb, bx, pad=4, scale=(f0.s if f0 and title != "Bauchi State" else None))
    if f0 is None:
        f0 = fr
    for n, g in units.items():
        if g.intersects(fitb.buffer(1)):
            body.append(bm.path(fr.g(g, simplify=0.3), "gm-land" if n in sts else "gm-ctx"))
    for n in sts:
        body.append(bm.path(fr.g(units[n], simplify=0.3), "gm-outline"))
    # big areas first, small on top
    here = [p for p in rad if SH[p["name"]].intersects(fitb)]
    for p in sorted(here, key=lambda p: -SH[p["name"]].area):
        big = SH[p["name"]].area > 0.02
        body.append(bm.path(fr.g(SH[p["name"]], simplify=0.2), "gm-circ",
                            f' fill-opacity="{step(p["cost_per_starter"])[1]}"' + (' style="stroke:var(--ink-3);stroke-width:.8"' if big else "")))
    for p in here:
        g = SH[p["name"]]
        parts = list(getattr(g.buffer(0.03), "geoms", [g.buffer(0.03)]))
        pts = []
        for part in parts:
            if part.area < 0.002 and len(parts) > 1:
                continue
            c = part.representative_point()
            pts.append((c.x, c.y))
        nm = p["name"]
        if nm.startswith("Yola–Jimeta: one"):
            b = g.bounds; pts = [(b[0] + 0.1, (b[1] + b[3]) / 2 + 0.05)]
        if nm.startswith("South-west of Abuja"):
            b = g.bounds; pts = [((b[0] + b[2]) / 2, b[1] + 0.05)]
        if nm.startswith("Yola–Jimeta: 23"):
            pts = [(12.47, 9.30)]
        for (x, y_) in pts:
            px, py = fr.xy(x, y_)
            body.append(bm.text(px, py + 4, KEY[nm], "gm-val gm-halo", "middle"))
    body.append(bm.text(bx[0] + 8, bx[1] + 16, title.upper(), "gm-eye"))
    body.append(bm.scalebar(bx[0] + 10, bx[1] + bx[3] - 10, fr, 25 if title != "Bauchi State" else 50))
    body.append(f'<rect class="gm-panel" x="{bx[0]}" y="{bx[1]}" width="{bx[2]}" height="{bx[3]}"/>')
body.append(bm.text(490 + 8, 186 + 30, "smaller scale", "gm-tiny"))
y = 26 + 300 + 24
body.append(bm.text(0, y, "Per person who started · letters match the map", "gm-eye"))
y += 14
mx = max(p["cost_per_starter"] for p in rad)
bwid = 760 - 420 - 60
for i, p in enumerate(order):
    yy = y + i * 30
    body.append(bm.text(0, yy + 10, f'{KEY[p["name"]]}  {p["name"]}', "gm-lab"))
    L = max(2.0, bwid * p["cost_per_starter"] / mx)
    body.append(f'<rect class="gm-bar" x="420" y="{yy}" width="{L:.1f}" height="12" fill-opacity="{step(p["cost_per_starter"])[1]}"/>')
    body.append(bm.text(420 + L + 6, yy + 10.5, money(p["cost_per_starter"]), "gm-val"))
    body.append(bm.text(18, yy + 23, f'{p["starters"]:,} started' + (" · few people" if p["thin"] else ""), "gm-tiny"))
y2 = y + len(order) * 30 + 6
xx = 0
for _, op, lab in STEPS:
    body.append(f'<rect class="gm-bar" x="{xx}" y="{y2}" width="12" height="10" fill-opacity="{op}"/>')
    body.append(bm.text(xx + 15, y2 + 9, lab, "gm-tiny"))
    xx += 15 + 6.3 * len(lab) + 10
body.append(bm.text(0, y2 + 30, "Radius areas drawn at true size. Larger areas outlined; smaller ones drawn on top where they overlap.", "gm-note"))
H = y2 + 40
svg2 = bm.svg(W, H, "Nigeria: advertising cost per person who started the survey, in radius areas around towns, 2024–2026",
              "; ".join(f'{p["name"]} {money(p["cost_per_starter"])} ({p["starters"]:,} started)' for p in order) + ".",
              body, "ngra")
open(P("nigeria-radius.svg"), "w").write(svg2)

# ------------------------------------------------------------------ data file
WHO = PLmod.WHO
FIRST = {}
for r in EV["rows"]:
    k = PLmod.instr(r)
    if r["days"]:
        FIRST[k] = min(FIRST.get(k, "9999"), r["days"][0])
USED = {i["instrument"] for p in places for i in p["qualified_by_instrument"] if i["qualified"] >= 20}
instr_order = sorted([k for k in FIRST if k in USED], key=lambda k: FIRST[k]) + sorted([k for k in FIRST if k not in USED], key=lambda k: FIRST[k])
LET = OrderedDict((k, chr(ord("A") + i) if k in USED else f"x{i}") for i, k in enumerate(instr_order))

tot_sp = sum(p["spend"] for p in places)
tot_st = sum(p["starters"] for p in places)
fams = sorted({f for p in places for f in p["families"]})
data = OrderedDict(
    _meta=OrderedDict(
        generated="2026-09-24",
        status="PILOT v6 - D-032 place page. Not registered in CLAIMS.md, not on the site.",
        method=("Every stratum of every cleaned Nigeria recruitment is evidence about a place (a Meta targeting geometry). "
                "Places pool across recruitments: spend summed, people summed, never ratios averaged. People are assigned to "
                "a place by the ad-set metadata written at their first message (inference_data variables with location "
                "'metadata'; where sibling studies shared stratum labels, by the Fly 'creative' recorded on their first "
                "response and the ad set that was spending that day)."),
        cleaning_rules=["USD ad account (account 2976439342687286 is naira: excluded)",
                        "spend from Insights per ad set (campaigns shared inside a family counted once, attributed by the study's final campaign name)",
                        "people recruited by ads: first message inside the ad set's spend window (1 day before to 3 after) and carrying ad metadata",
                        "sibling studies de-duplicated: each person once per recruitment",
                        "pins and regions checked against GeoNames/Natural Earth; the Kirfi 'place' (67 km off) is out",
                        "qualifying rule = the recruitment's final question_targeting, recounted from inference_data"],
        thresholds="places shown with at least 50 people who started; under 200 flagged",
        definitions=OrderedDict(
            started="a person whose first message in the survey carried the ad metadata of an ad set targeting this place, during that ad set's run",
            qualified="a person who started and then answered the recruitment's final quota-rule question (its question_targeting 'answered' variable)",
            cost_per_starter="Insights spend / people who started",
            cost_per_qualified="Insights spend / qualified people, pooled only within one questionnaire"),
        terms={
            "whole_state": "ads shown to people Meta places anywhere inside the state's official boundary",
            "radius_area": "a pin or Meta city plus a radius; 'inside the radius areas' and 'outside them' are the two sides",
            "recruitment": "one round of ads filling one set of quotas; sibling studies that fed one survey are one recruitment"}),
    country="NG",
    all_people_surveyed=dict(unique_people=55798, first="2023-08-12", last="2026-09-10", studies=49,
                             note="Anyone who answered in any Nigeria study on the current platform (distinct inference_data user_id over studies with country NG). Unchanged from v4."),
    totals=dict(places_shown=len(places), recruitments=len(fams), spend=round(tot_sp, 2), people_started=tot_st,
                first_day=min(p["first_day"] for p in places), last_day=max(p["last_day"] for p in places),
                note="people who started in two recruitments are counted in each"),
    places=PL["places"],
    gender=PL["gender"],
    instruments=OrderedDict((LET[k], dict(key=k, who=WHO[k], first_ad_day=FIRST[k])) for k in instr_order),
    recruitments=OrderedDict(),
    attribution=OrderedDict(),
    excluded_places=PL["excluded"],
    excluded_for_review=OrderedDict(),
)
agg = OrderedDict()
for r in EV["rows"]:
    a = agg.setdefault(r["family"], dict(studies=set(), spend=0.0, starters=0, qualified=0, days=set(), conv=0.0, conv_starters=0))
    a["studies"].add(r["study"]); a["spend"] += r["spend"]; a["starters"] += r["starters"]; a["qualified"] += r["qualified"]
    a["days"].update(r["days"])
    if r.get("meta_conversations") is not None:
        a["conv"] += r["meta_conversations"]; a["conv_starters"] += r["starters"]
for f_, a in sorted(agg.items(), key=lambda x: min(x[1]["days"]) if x[1]["days"] else ""):
    d = sorted(a["days"])
    data["recruitments"][f_] = dict(studies=sorted(a["studies"]), first_ad_day=d[0] if d else None, last_ad_day=d[-1] if d else None,
                                    ad_days=len(d), spend=round(a["spend"], 2), started=a["starters"], qualified=a["qualified"],
                                    meta_conversations=round(a["conv"]), started_where_conversations_recorded=a["conv_starters"])
    data["attribution"][f_] = dict(
        unassigned=EV["unassigned"].get(f_, {}),
        started_per_meta_conversation=round(a["conv_starters"] / a["conv"], 2) if a["conv"] else None)
data["attribution"]["_how_to_read"] = ("started_per_meta_conversation at or below 1 means the survey saw no more starters than Meta counted "
                                       "conversations from those ad sets: consistent with every starter being ad-driven. owis records no "
                                       "conversation metric; the llm recruitment records it on 9 of 28 stratum-days, so its ratio is not a test.")
data["attribution"]["_ambiguous"] = EV["assign_log"]
data["attribution"]["_spend_not_attributed"] = EV["spend_unmatched"]
data["excluded_for_review"] = OrderedDict(
    naira_account=["cohort-2-pilot, -2, -3, -4, -5, fly_test, test (account ...7286, naira; Flier 1 and Flier 3 campaigns also shared between studies)"],
    no_respondent_data=["upswell-fogg-1, upswell-fogg-2 (2022, Typeform destination: no respondents in our database; reports cover $399 of $870 and $165 of $2,482)"],
    no_ads_or_re_contacts=["vl-pulse-nigeria-smoke ($0), vl-pulse-nigeria-smoke-wa ($1.79)", "hpv-nigeria, hpv-nigeria-scale-up, test-custom-audience, nigeria-full-study (no spend; their people are other recruitments' people)",
                           "nigeria-hausa-pilot, wb-fossil-fuel-subsidies-nigeria, nigeriahpv-fly-config ($0)"],
    places_out=["Kirfi: Meta place 'Kirfi LGA' 67 km from Kirfi, near Bauchi city ($257, 321 started)",
                "Anambra and Bauchi in one ad set ($20, 68 started, 0 qualified)",
                "Dambam radius area: 30 started (under 50)"],
    spend_not_attributed=["$10.46 of the first 2023 run's ad sets carry stratum ids from an earlier configuration and are not in the final strata"],
)
json.dump(data, open(P("country-ng.json"), "w"), indent=1, ensure_ascii=False)

# ------------------------------------------------------------------ section.html
def fmt_q(p, minq=20):
    parts = []
    for i in sorted(p["qualified_by_instrument"], key=lambda i: LET[i["instrument"]]):
        if i["qualified"] >= minq:
            parts.append(f'{LET[i["instrument"]]}&nbsp;{money(i["cost_per_qualified"])}')
    return " · ".join(parts) if parts else "—"


def dates(p):
    import datetime as dt
    a, b = dt.date.fromisoformat(p["first_day"]), dt.date.fromisoformat(p["last_day"])
    if (a.year, a.month) == (b.year, b.month):
        return a.strftime("%b %Y")
    if a.year == b.year:
        return f'{a.strftime("%b")}–{b.strftime("%b %Y")}'
    return f'{a.strftime("%b %Y")} – {b.strftime("%b %Y")}'


def row(p):
    thin = ' <span class="id">fewer than 200 people</span>' if p["thin"] else ""
    dom = ""
    if p["recruitments"] > 1 and p["largest_recruitment_share_of_spend"] >= 0.8:
        top = max(p["by_recruitment"].items(), key=lambda kv: kv[1]["spend"])[0]
        import datetime as dt
        d0 = dt.date.fromisoformat(min(r["days"][0] for r in EV["rows"] if r["family"] == top and r["days"]))
        dom = f' <span class="id">{round(100 * p["largest_recruitment_share_of_spend"])}% of the spend from one round, {d0.strftime("%b %Y")}</span>'
    return (f'<tr><td>{html.escape(p["name"])}{thin}{dom}</td><td>{dates(p)}</td><td class=n>{p["recruitments"]}</td>'
            f'<td class=n>{p["starters"]:,}</td><td class=n>${p["spend"]:,.0f}</td><td class=n><b>{money(p["cost_per_starter"])}</b></td>'
            f'<td>{fmt_q(p)}</td></tr>')


groups = [p for p in places if p["kind"] in ("group", "country")]
statesp = sorted([p for p in places if p["kind"] == "state"], key=lambda p: p["cost_per_starter"])
minus = sorted([p for p in places if p["kind"] == "state_minus"], key=lambda p: p["cost_per_starter"])
radp = sorted(rad, key=lambda p: p["cost_per_starter"])
groups = sorted(groups, key=lambda p: p["cost_per_starter"])
TH = '<thead><tr><th>Place</th><th>Ads ran</th><th class=n>Recruit&shy;ments</th><th class=n>Started</th><th class=n>Ad spend</th><th class=n>Per person who started</th><th>Per qualified respondent</th></tr></thead>'
big = [p for p in places if not p["thin"]]
lo = min(big, key=lambda p: p["cost_per_starter"]); hi = max(big, key=lambda p: p["cost_per_starter"])
used_letters = sorted({LET[i["instrument"]] for p in places for i in p["qualified_by_instrument"] if i["qualified"] >= 20})
legend = "\n".join(f'      <dt>{L}</dt><dd>{html.escape(WHO[k])}.</dd>' for k, L in LET.items() if L in used_letters)
g = PL["gender"]
kano, lagos, bauchi = byname["Kano (whole state)"], byname["Lagos (whole state)"], byname["Bauchi (whole state)"]
yj2, ab24 = byname["Yola–Jimeta: 23 radius areas of 2 km"], byname["Abuja and Suleja: 24 radius areas of 4 km"]

HOW_RADIUS = open(P("how_radius.html")).read()
HOW_COST = open(P("how_cost.html")).read()

section = f'''  <section id="nigeria" role="tabpanel" aria-labelledby="t-nigeria">
    <div class="eyebrow">Nigeria · Recruitment cost</div>
    <h1>What does it cost to recruit survey respondents in Nigeria?</h1>
    <p class="lede">Recruiting survey respondents in Nigeria between 2023 and 2026 cost from <b>{money(lo["cost_per_starter"])}</b> to <b>{money(hi["cost_per_starter"])}</b> in advertising per person who started the survey, depending on where the ads ran (places with at least 200 people). Whole states ranged from <b>{money(kano["cost_per_starter"])} in Kano</b> to <b>{money(bauchi["cost_per_starter"])} in Bauchi</b>; small radius areas around towns cost the most, up to <b>{money(yj2["cost_per_starter"])}</b> in Yola–Jimeta.</p>

    <div class="facts">
      <div><b>55,798</b><span>people surveyed in Nigeria, Aug 2023 – Sep 2026</span></div>
      <div><b>{tot_st:,}</b><span>people who started a survey from an ad, in the {len(places)} places below</span></div>
      <div><b>{money(lo["cost_per_starter"])}</b><span>per person who started, {html.escape(lo["name"].split(":")[0])}</span></div>
      <div><b>{money(hi["cost_per_starter"])}</b><span>per person who started, {html.escape(hi["name"].split(":")[0])}</span></div>
    </div>

{HOW_RADIUS}
{HOW_COST}

    <h2>Whole states cost {money(kano["cost_per_starter"])} to {money(bauchi["cost_per_starter"])} per person who started</h2>
    <p>{len(statesp)} states were each targeted whole at least once. Kano, the Federal Capital Territory and Rivers cost under 30 cents per person who started; Lagos cost {money(lagos["cost_per_starter"])}, and Bauchi {money(bauchi["cost_per_starter"])}. Where several recruitments targeted the same state, their spend and their people are added together, so a state's figure spans every year it was targeted. Groups of states and the whole country are in the same table.</p>
    <figure>{{{{NGST}}}}</figure>
    <div class="tbl"><table>
      {TH}
      <tbody>
        {"".join(row(p) for p in statesp)}
        {"".join(row(p) for p in groups)}
        {"".join(row(p) for p in minus)}
      </tbody>
    </table></div>

    <h2>Radius areas around Abuja cost least; small ones around smaller towns cost the most</h2>
    <p>Around Abuja, {ab24["name"].split(":")[1].strip()} cost {money(ab24["cost_per_starter"])} per person who started, over {ab24["starters"]:,} people. The same size of radius area around Lafia and Keffi cost {money(byname["Lafia and Keffi: 60 radius areas of 4 km"]["cost_per_starter"])}, and radius areas of 2 km in Yola–Jimeta {money(yj2["cost_per_starter"])}. A single 53 km radius area over Yola–Jimeta cost {money(byname["Yola–Jimeta: one radius area of 53 km"]["cost_per_starter"])}: the wider the area, the more people the ads could find.</p>
    <figure>{{{{NGRA}}}}</figure>
    <div class="tbl"><table>
      {TH}
      <tbody>
        {"".join(row(p) for p in radp)}
      </tbody>
    </table></div>
    <p class="cap">Places with fewer than 50 people who started are left out. The per-qualified column lists each group of recruitments that shared one questionnaire and screening, with at least 20 qualified people there; the letters are explained below. Qualified costs are never added across different questionnaires.</p>

    <h2>Women cost {round(100 * (g["women"]["cost_per_starter"] / g["men"]["cost_per_starter"] - 1))}% more than men to reach</h2>
    <div class="tbl"><table>
      <thead><tr><th>Ads shown to</th><th class=n>Started</th><th class=n>Ad spend</th><th class=n>Per person who started</th></tr></thead>
      <tbody>
        <tr><td>Men</td><td class=n>{g["men"]["starters"]:,}</td><td class=n>${g["men"]["spend"]:,.0f}</td><td class=n>{money(g["men"]["cost_per_starter"])}</td></tr>
        <tr><td>Women</td><td class=n>{g["women"]["starters"]:,}</td><td class=n>${g["women"]["spend"]:,.0f}</td><td class=n>{money(g["women"]["cost_per_starter"])}</td></tr>
      </tbody>
    </table></div>
    <p class="cap">Pooled over the {g["cells"]} place-and-recruitment pairs in which ads ran separately to men and to women in the same place. Age was set per recruitment rather than split, so there is no age table.</p>

    <h2>Who qualified</h2>
    <p>A qualified respondent is someone who started and then got through the recruitment's screening and questions. That depends on who the recruitment was looking for and how long its survey was, so each group below is shown separately.</p>
    <dl>
{legend}
    </dl>
    <dl>
      <dt>Channel</dt><dd>Facebook and Instagram ads leading to a survey in Messenger, in English and Hausa (and Yoruba in one recruitment). Incentives, where paid, ranged from nothing to $1 in mobile credit and are not in the advertising cost.</dd>
      <dt>Recruitments</dt><dd>{len(fams)} rounds of ads, August 2023 to August 2026, from three-day runs to month-long ones. The first people in a round are often the cheapest; the dates show when each place was targeted.</dd>
    </dl>
    <p class="cta">Planning a study in Nigeria? Write to <b>info@vlab.digital</b>.</p>
'''
rec = data["recruitments"]
def pct(p):
    return round(100 * p["largest_recruitment_share_of_spend"])
notes = [
    f"<b>How people were placed.</b> Every starter is placed by the ad-set metadata written at their first message, never by their answers. Where two sibling ad runs used the same labels (the A and B runs of 2024–25), the Fly creative on their first response decided, then which ad set was spending that day; {sum(v for k, v in EV['assign_log'].items() if 'ambiguous' in k)} people were placed by 'same geometry either way' and {sum(sum(c for kk, c in u.items() if 'ambiguous' in kk) for u in EV['unassigned'].values())} could not be placed and are left out.",
    "<b>The attribution checks out where it can be tested.</b> In 18 of 22 recruitments the survey saw fewer starters than Meta counted conversations from the same ad sets (ratio 0.45–0.95); two were just over (1.03 and 1.06). One recruitment (<code>owis-nigeria-study</code>) records no conversation metric and one (<code>llm-bias-nigeria-pilot</code>) records it on 9 of 28 stratum-days, so neither is tested.",
    f"<b>Pooled places can be one recruitment in disguise.</b> Bauchi (whole state): {pct(bauchi)}% of the spend is the May–June 2026 round, which cost {money(rec['2026-may-bauchi-mnch']['spend'] / rec['2026-may-bauchi-mnch']['started'])} per starter against $0.87 in the February 2026 round; Meta itself charged $4.43 per conversation there, so the cost is at the ad stage, cause unknown. FCT outside the Kuje radius area: {pct(byname['FCT outside the radius area around Kuje'])}% is the November 2025 round ($0.10 per qualified in April 2025, $6.16 in November). The table flags any place where one round is 80% or more of the spend.",
    "<b>The April 2025 A/B arms.</b> The inside/outside places around Kuje, Nasarawa-Akwanga and Yola come from a round whose two ad arms flipped sides by state, and arm A was cheaper in every state. They are shown as places because the geometry is honest; do not read them as an inside-versus-outside comparison.",
    "<b>Pins checked.</b> 3 of the 24 radius areas labelled Abuja sit across the FCT border around Suleja (Niger and Kaduna states), hence the name. The 4 labelled Nasarawa sit 11–15 km from Abuja's centre, on the Karu side. The Kuje area's pin is 24 km south-south-west of Abuja's centre. Toro's pin is 12.6 km from Toro town. The Kirfi 'place' is out.",
    "<b>Qualified counts are recounted</b> from each recruitment's final quota rule. Where one study is one recruitment the recount matches its latest report (2,096 = 2,096; 298; 329; 170) or runs a few percent over it (+41 of 1,411; +42 of 734; +10 of 1,180), which is people who finished after the report ran.",
    "<b>Midlines and the November 2025 endline are in:</b> each was a fresh sample recruited by ads, and only people whose first message fell inside that round's ad days count. A person who started in two rounds counts in each.",
    "<b>Out:</b> the naira account (<code>cohort-2-pilot*</code>, <code>fly_test</code>, <code>test</code>); <code>upswell-fogg-1/2</code> (2022, no respondents in our database); zero-ad studies; the Kirfi place; one $20 ad set covering Anambra and Bauchi together; Dambam (30 starters).",
    "<b>Uncertain wording:</b> the 2025 sign-up counts people who answered 'Ending', which is not in the one-question form we could read; the 2026 adult recruitment's rule is question 38 of a follow-up form. Both are marked in the data file.",
    "<b>Recruitment ids</b> (slugs, for review only): " + "; ".join(f"<code>{k}</code>: " + ", ".join(v["studies"]) for k, v in rec.items()) + ".",
]
section += '\n    <div class="note">\n      <h3>For review</h3>\n      <ul>\n' + "\n".join(f"        <li>{n}</li>" for n in notes) + '\n      </ul>\n    </div>\n  </section>\n'
open(P("section.html"), "w").write(section)
print("built", len(places), "places;", tot_st, "started; $", round(tot_sp, 2))
