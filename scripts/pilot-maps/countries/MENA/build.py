#!/usr/bin/env python3
"""MENA country pages (D-032 pilot, v4 recipe): Iraq, Egypt, Morocco pass; Saudi Arabia and Jordan
are held out. Scratch work, not in the repo.

    ../../geo/venv/bin/python build.py     # country-XX.json, maps/*.svg, section-XX.html, excluded-XX.json
    ../../geo/venv/bin/python build.py png # + png/*.png review renders (light tokens substituted)

Inputs, all pulled read-only from production (queries in sql/, outputs in raw/):
  raw/adopt-<slug>.tsv   latest FACEBOOK_ADOPT report per study, fetched one study at a time
  raw/qualified.tsv      qualified people per stratum under each study's LATEST quota rule (sql/qualified.sql)
  raw/daily.tsv          spend / impressions / clicks per stratum per day (sql/daily.sql)
  raw/people.tsv         unique people per country (sql/people.sql)
  raw/strata-<slug>.tsv  latest strata conf (targeting), raw/hist-<slug>.tsv the conf history
  raw/dropoff.tsv        where people stopped in the survey (sql/dropoff.sql)
Map helpers are imported from ../../geo/build_maps.py (Natural Earth 10m there); GeoNames dumps for
IQ/EG/MA are in ./geonames (CC BY 4.0), used only to place the Meta city points.
"""
import csv, json, os, re, subprocess, sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
SP = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(SP, "geo"))
import build_maps as bm  # noqa: E402
from shapely.geometry import box, shape  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
from pyproj import Transformer  # noqa: E402
from shapely.ops import transform  # noqa: E402
import analyse  # noqa: E402

REPO = "/home/nandan/Documents/vlab-research/vlab.digital"
TPL = os.path.join(REPO, "scripts/pilot-maps/review-page.tpl.html")
MAPS = os.path.join(HERE, "maps")
os.makedirs(MAPS, exist_ok=True)
csv.field_size_limit(10**9)
MI = 1.609344

# ---------------------------------------------------------------- GeoNames (local copies, same parser)
for cc in ("IQ", "EG", "MA"):
    rows = []
    for line in open(os.path.join(HERE, "geonames", cc + ".txt"), encoding="utf8"):
        r = line.rstrip("\n").split("\t")
        if r[6] == "P":
            rows.append(dict(id=int(r[0]), name=r[1], ascii=r[2], lat=float(r[4]), lon=float(r[5]),
                             code=r[7], a1=r[10], pop=int(r[14] or 0)))
    bm._GN[cc] = rows

# Meta stores a city by key and name, not by point. The point is the GeoNames record for that city
# (capital or first-order seat), found by geonameid so the choice is reproducible.
CITY_POINT = {"Baghdad": ("IQ", 98182), "Mosul": ("IQ", 99072), "Basra": ("IQ", 99532),
              "Cairo": ("EG", 360630), "Giza": ("EG", 360995), "Alexandria": ("EG", 361058),
              "Casablanca": ("MA", 2553604), "Fez": ("MA", 2548885), "Marrakech": ("MA", 2542997)}
DISPLAY = {"Marrakech": "Marrakesh"}  # Meta's and GeoNames' spelling; the stratum label says Marrakech


def city_point(city):
    cc, gid = CITY_POINT[city]
    x = next(r for r in bm._GN[cc] if r["id"] == gid)
    return x


A0 = {f["properties"]["ADM0_A3"]: shape(f["geometry"]).buffer(0)
      for f in json.load(open(os.path.join(SP, "geo", "ne_10m_admin_0_countries.geojson")))["features"]}

COUNTRY = OrderedDict([
    ("IQ", dict(name="Iraq", a3="IRQ", slug="embed-iraq", langs="Arabic or English",
                frame=dict(lon0=43.7, lat0=33.2, fit="country", bx=(0, 26, 400, 440)),
                lab={"Baghdad": (12, 4, "start"), "Mosul": (12, 4, "start"), "Basra": (-12, -6, "end")},
                scale_km=200)),
    ("EG", dict(name="Egypt", a3="EGY", slug="embed-egypt", langs="Arabic or English",
                frame=dict(lon0=30.6, lat0=30.55, fit=(29.2, 29.55, 32.2, 31.65), bx=(0, 26, 400, 440)),
                lab={"Alexandria": (26, 36, "start"), "Cairo": (30, -24, "start"), "Giza": (-30, 34, "end")},
                scale_km=50)),
    ("MA", dict(name="Morocco", a3="MAR", slug="embed-morocco", langs="Arabic or French",
                frame=dict(lon0=-6.9, lat0=33.0, fit=(-9.9, 30.9, -3.9, 35.2), bx=(0, 26, 400, 440)),
                lab={"Casablanca": (-14, -6, "end"), "Fez": (14, 4, "start"), "Marrakech": (14, 4, "start")},
                scale_km=100)),
])
PASS = list(COUNTRY)

INCENTIVE = "phone credit, set at $1 per respondent in the study settings"


def money(x, cents=True):
    return f"${x:,.2f}" if cents else f"${x:,.0f}"


def fmt_date(d, year=True):
    import datetime
    t = datetime.date.fromisoformat(d)
    return t.strftime("%-d %b %Y") if year else t.strftime("%-d %b")


def radius_of(slug):
    r = next(csv.DictReader(open(os.path.join(HERE, "raw", f"strata-{slug}.tsv")), delimiter="\t"))
    geo = {}
    for s in json.loads(r["conf"]):
        g = s["facebook_targeting"]["geo_locations"]
        geo.setdefault(s["metadata"]["City"], json.dumps({k: v for k, v in g.items() if k != "location_types"}, sort_keys=True))
    out = {}
    for city, g in geo.items():
        g = json.loads(g)
        assert list(g) == ["cities"] and len(g["cities"]) == 1, (slug, city, g)
        c = g["cities"][0]
        assert c["distance_unit"] == "mile" and c["radius"] == 10, (slug, city, c)
        out[city] = dict(meta_key=c["key"], meta_name=c["name"], meta_region=c["region"], radius_mi=10,
                         radius_km=round(10 * MI, 1), location_types=["home", "recent"])
    return out, r["created"]


# ---------------------------------------------------------------- map
def build_map(cc, d, tgt):
    C = COUNTRY[cc]
    a3 = C["a3"]
    land = A0[a3]
    adm = bm.admin1(a3)
    f = C["frame"]
    fit = land if f["fit"] == "country" else box(*f["fit"])
    fr = bm.Frame(f["lon0"], f["lat0"], fit, f["bx"], pad=4)
    x, y, w, h = f["bx"]
    body = [bm.text(0, 12, f"{C['name']} · three cities, 16 km radius areas", "gm-eye")]
    view = box(*[v for v in (fit.bounds if f["fit"] == "country" else f["fit"])]).buffer(6)
    for k, g in A0.items():
        if k != a3 and g.intersects(view):
            body.append(bm.path(fr.g(g, simplify=0.3), "gm-ctx0"))
    body.append(bm.path(fr.g(land, simplify=0.3), "gm-land"))
    for g in adm.values():
        body.append(bm.path(fr.g(g, simplify=0.3), "gm-adm"))
    body.append(bm.path(fr.g(land, simplify=0.3), "gm-outline"))
    circles = {}
    for city in d["by_city"]:
        p = city_point(city)
        circles[city] = bm.circle(p["lon"], p["lat"], tgt[city]["radius_km"])
    body.append(bm.path(fr.g(unary_union(list(circles.values())), simplify=0.1), "gm-circ"))
    for g in circles.values():
        body.append(bm.path(fr.g(g, simplify=0.1), "gm-ring"))
    for city, a in d["by_city"].items():
        p = city_point(city)
        px, py = fr.xy(p["lon"], p["lat"])
        body.append(bm.cell(px, py, "gm-cell", 3))
        dx, dy, an = C["lab"][city]
        if abs(dx) > 20 or abs(dy) > 20:
            body.append(f'<path class="gm-lead" d="M{px:.1f},{py:.1f}L{px + dx * .7:.1f},{py + dy * .7:.1f}"/>')
        body.append(bm.text(px + dx, py + dy, DISPLAY.get(city, city), "gm-lab gm-halo", an))
        body.append(bm.text(px + dx, py + dy + 14, money(a["cost"]), "gm-val gm-halo", an))
    body.append(f'<rect class="gm-panel" x="{x}" y="{y}" width="{w}" height="{h}"/>')
    body.append(bm.scalebar(x + 10, y + h - 12, fr, C["scale_km"]))

    # ranked list: the table behind the map, and the legend
    x0, y0 = 424, 40
    body.append(bm.text(x0, 12, "Ad cost per qualified respondent", "gm-eye"))
    rows = sorted(d["by_city"].items(), key=lambda kv: kv[1]["cost"])
    mx = max(a["cost"] for _, a in rows)
    bw = 760 - (x0 + 92) - 60
    for i, (city, a) in enumerate(rows):
        yy = y0 + i * 60
        body.append(bm.text(x0, yy + 10, DISPLAY.get(city, city), "gm-lab"))
        L = max(2.0, bw * a["cost"] / mx)
        body.append(f'<rect class="gm-bar" x="{x0 + 92}" y="{yy}" width="{L:.1f}" height="12"/>')
        body.append(bm.text(x0 + 92 + L + 6, yy + 10.5, money(a["cost"]), "gm-val"))
        body.append(bm.text(x0, yy + 27, f'{a["qualified"]:,} qualified · {money(a["spend"])} ad spend', "gm-tiny"))
        body.append(bm.text(x0, yy + 41, f'10 mi (16 km) around the city', "gm-tiny"))
    tot_y = y0 + len(rows) * 60 + 4
    body.append(f'<path class="gm-lead" d="M{x0},{tot_y - 8}H760"/>')
    body.append(bm.text(x0, tot_y + 10, "All three", "gm-lab"))
    body.append(bm.text(x0 + 92, tot_y + 10.5, money(d["cost"]), "gm-val"))
    body.append(bm.text(x0, tot_y + 27, f'{d["qualified"]:,} qualified · {money(d["spend"])} ad spend', "gm-tiny"))

    yn = y + h + 20
    notes = MAP_NOTES[cc](d)
    for i, line in enumerate(notes):
        body.append(bm.text(0, yn + 16 * i, line, "gm-note"))
    H = yn + 16 * (len(notes) - 1) + 8
    title = f"{C['name']}: advertising cost per qualified respondent in three city radius areas"
    desc = (f"Radius areas of 10 miles (16 km) around " + ", ".join(DISPLAY.get(c, c) for c in d["by_city"]) +
            ", drawn to scale. Ad cost per qualified respondent: " +
            ", ".join(f"{DISPLAY.get(c, c)} {money(a['cost'])}" for c, a in rows) + f"; all three {money(d['cost'])}.")
    s = bm.svg(760, H, title, desc, body, cc.lower() + "-map")
    out = os.path.join(MAPS, f"{C['name'].lower()}-cities.svg")
    open(out, "w").write(s)
    print("wrote", out, f"{len(s) / 1024:.0f} KB")
    return out, s


def window(d):
    return f"{fmt_date(d['first_ad_day'], False)} {d['first_ad_day'][:4]} – {fmt_date(d['last_ad_day'])}" \
        if d["first_ad_day"][:4] != d["last_ad_day"][:4] else f"{fmt_date(d['first_ad_day'], False)} – {fmt_date(d['last_ad_day'])}"


MAP_NOTES = {
    "IQ": lambda d: [
        f"{window(d)}, {d['ad_days']} days of advertising. Each radius area is a Meta city target with a 10-mile radius;",
        "the city points are placed from GeoNames (Meta stores the city, not its point). Men and women and",
        "all three age groups pooled."],
    "EG": lambda d: [
        f"{window(d)}, {d['ad_days']} days of advertising. Each radius area is a Meta city target with a 10-mile radius;",
        f"the Cairo and Giza areas overlap, since their centres are {d['_overlap']['centre_km']:.0f} km apart. City points placed from GeoNames",
        "(Meta stores the city, not its point). Men and women and all three age groups pooled."],
    "MA": lambda d: [
        f"{window(d)}, {d['ad_days']} days of advertising. Each radius area is a Meta city target with a 10-mile radius;",
        "the city points are placed from GeoNames (Meta stores the city, not its point). Men and women and",
        "all three age groups pooled."],
}


# ---------------------------------------------------------------- page section
def modules():
    s = open(TPL).read()
    i = s.index('<div class="how">')
    j = s.index("<h2>Lagos cost")
    block = s[i:j].rstrip()
    assert block.count('<div class="how">') == 2
    return block


def group_rows(d):
    rows = []
    for k, lab in (("Men", "Men"), ("Women", "Women")):
        a = d["by_gender"][k]
        rows.append((lab, a))
    for k, lab in (("30-39", "Age 30–39"), ("40-49", "Age 40–49"), ("50+", "Age 50–65")):
        rows.append((lab, d["by_age"][k]))
    return "\n".join(
        f'        <tr><td>{lab}</td><td class=n>{a["qualified"]:,}</td><td class=n>{money(a["spend"], False)}</td>'
        f'<td class=n>{money(a["cost"])}</td></tr>' for lab, a in rows)


def city_rows(d):
    return "\n".join(
        f'        <tr><td>{DISPLAY.get(c, c)}</td><td>10 mi (16 km) around the city</td><td class=n>{a["qualified"]:,}</td>'
        f'<td class=n>{money(a["spend"], False)}</td><td class=n>{money(a["cost"])}</td></tr>'
        for c, a in sorted(d["by_city"].items(), key=lambda kv: kv[1]["cost"]))


def programme_table(all_d, here):
    rows = []
    for cc in PASS:
        d = all_d[cc]
        name = COUNTRY[cc]["name"]
        cities = ", ".join(DISPLAY.get(c, c) for c in d["by_city"])
        nm = f"<b>{name}</b>" if cc == here else name
        rows.append(f'        <tr><td>{nm}</td><td>{cities}</td><td>{window(d)}</td><td class=n>{d["qualified"]:,}</td>'
                    f'<td class=n>{money(d["spend"], False)}</td><td class=n>{money(d["cost"])}</td></tr>')
    return "\n".join(rows)


def section(cc, d, all_d, svg_text):
    C = COUNTRY[cc]
    name = C["name"]
    T = TEXT[cc](d, all_d)
    others = [COUNTRY[k]["name"] for k in PASS if k != cc]
    return f"""  <section id="{name.lower()}" role="tabpanel" aria-labelledby="t-{name.lower()}">
    <div class="eyebrow">{name} · Recruitment cost</div>
    <h1>What does it cost to recruit survey respondents in {name}?</h1>
    <p class="lede">{T['lede']}</p>
{T.get('lede2', '')}
    <div class="facts">
{T['facts']}
    </div>

    {modules()}

    <h2>{T['h2']}</h2>
    <p>{T['p']}</p>
    <figure>{svg_text.strip()}</figure>
    <div class="tbl"><table>
      <thead><tr><th>City</th><th>Radius area</th><th class=n>Qualified</th><th class=n>Ad spend</th><th class=n>Per qualified</th></tr></thead>
      <tbody>
{city_rows(d)}
      </tbody>
    </table></div>
{T.get('after_city', '')}
    <h2>{T['h2_groups']}</h2>
    <div class="tbl"><table>
      <thead><tr><th>Group</th><th class=n>Qualified</th><th class=n>Ad spend</th><th class=n>Per qualified</th></tr></thead>
      <tbody>
{group_rows(d)}
      </tbody>
    </table></div>
    <p class="cap">Each group is pooled over the other two dimensions: city and age, or city and gender.</p>

    <h2>The same survey in three countries</h2>
    <p>This study was one of three that ran the same survey, with the same quotas and the same rule for who qualified, in {', '.join(sorted([name] + others)[:-1])} and {sorted([name] + others)[-1]}, over overlapping weeks between December 2025 and February 2026. Each advertised around three large cities.</p>
    <div class="tbl"><table>
      <thead><tr><th>Country</th><th>Cities</th><th>Ads ran</th><th class=n>Qualified</th><th class=n>Ad spend</th><th class=n>Per qualified</th></tr></thead>
      <tbody>
{programme_table(all_d, cc)}
      </tbody>
    </table></div>
    <p class="cap">One survey, one design, one season, so the three are comparable in a way separate studies are not. The cities differ, and the ads ran on different days, so these are the costs of these recruitments, not a fixed price for each country.</p>

    <h2>How the study was set up</h2>
    <dl>
      <dt>Quotas</dt><dd>City ({', '.join(DISPLAY.get(c, c) for c in d['by_city'])}) × gender × age (30–39, 40–49, 50–65): 18 groups with equal targets. A person's group is set by the ad that reached them, each ad aimed at one city, one gender and one age band.</dd>
      <dt>Channel</dt><dd>Facebook and Instagram ads leading to a survey in Messenger, in {C['langs']}. Incentive: {INCENTIVE}, not included in the advertising cost.</dd>
      <dt>Screening</dt><dd>The survey ended early for anyone under 30 or living outside the three cities.</dd>
      <dt>Qualified</dt><dd>In a quota group, and answered through to the phone-number question that follows the main survey. {d['qualified']:,} of the {d['started']:,} who started did.</dd>
    </dl>

    <p class="cta">Planning a study in {name}? Write to <b>info@vlab.digital</b>.</p>

    <div class="note">
      <h3>For review</h3>
      <ul>
{T['review']}
      </ul>
    </div>
  </section>
"""


def facts(cells):
    return "\n".join(f"      <div><b>{b}</b><span>{s}</span></div>" for b, s in cells)


COMMON_REVIEW = lambda d: [
    (f"<b>Qualified counts are recomputed, not read from the report.</b> This study's latest report ({d['report_created'][:10]}) ran under the final quota rule, the phone-number question, and counts {d['report_qualified']:,}; the recomputation gives {d['qualified']:,}. It is used so that all three countries are counted the same way: the Egypt and Morocco reports predate the switch to that rule on 15 Jan 2026. Spend is the report's own per-group spend, which reconciles with Meta's total. <b>This needs Nandan's OK: it departs from reading the report.</b>"
     if d["cc"] == "IQ" else
     f"<b>Qualified counts are recomputed, not read from the report.</b> The study's latest report ({d['report_created'][:10]}) was generated under an earlier quota rule ({ {'EG': 'answering recruit_learn', 'MA': 'answering the height question'}[d['cc']] }; it counts {d['report_qualified']:,}). On 15 Jan 2026 every study in the programme was switched to the phone-number question. Counting each quota group under that final rule gives {d['qualified']:,}, and reproduces Iraq's report, which ran under it, to within 2 people (1,415 against 1,413). Spend is the report's own per-group spend, which reconciles with Meta's total. <b>This needs Nandan's OK: it departs from reading the report.</b>"),
    "<b>One survey, five countries.</b> The Iraq, Egypt, Saudi Arabia, Morocco and Jordan studies all fed one survey, so every study's respondent table holds all five countries. People are assigned to a country by the city of the ad that reached them; 7 people carry two cities. Spend is separate per country (one campaign each, not shared).",
    f"<b>\"Ad days\" means days with spend.</b> Ads ran in bursts: {d['ad_days']} days with spend between {fmt_date(d['first_ad_day'])} and {fmt_date(d['last_ad_day'])}. The recipe's query counts every day with a row, including days with none, which gives a larger number.",
    "<b>Held out of the comparison:</b> Saudi Arabia (the Jeddah ad sets were aimed at Mecca for 12 days, which carried 68% of Jeddah's spend; and $11.03 per qualified with no known cause) and Jordan (ads on 5 days only, under the 7-day rule).",
    "City points are placed from GeoNames; Meta stores the city, not its point.",
]

TEXT = {}


def _iq(d, all_d):
    c = d["by_city"]
    return dict(
        lede=(f"In one Virtual Lab study between December 2025 and February 2026, advertising around Baghdad, Mosul and Basra "
              f"recruited <b>{d['qualified']:,} qualified respondents</b> for <b>{money(d['spend'], False)}</b>, or "
              f"<b>{money(d['cost'])} each</b>. By city, the cost ran from <b>{money(c['Baghdad']['cost'])}</b> around Baghdad "
              f"to <b>{money(c['Basra']['cost'])}</b> around Basra."),
        facts=facts([(f"{d['qualified']:,}", f"qualified respondents, {window(d)}"),
                     (money(c["Baghdad"]["cost"]), "per qualified respondent, 16 km around Baghdad"),
                     (money(c["Basra"]["cost"]), "per qualified respondent, 16 km around Basra"),
                     (f"{d['people']['unique_people']:,}", "people surveyed in Iraq, Nov 2025 – Feb 2026")]),
        h2="Basra cost four and a half times as much as Baghdad",
        p=(f"The study advertised in a radius area of 10 miles (16 km) around each of the three cities, with the same survey and the same quotas in each. "
           f"A qualified respondent cost {money(c['Baghdad']['cost'])} around Baghdad, {money(c['Mosul']['cost'])} around Mosul and "
           f"{money(c['Basra']['cost'])} around Basra. The gap opened before the survey began: each person who started it cost "
           f"{money(c['Basra']['cost_per_started'])} in advertising around Basra and {money(c['Baghdad']['cost_per_started'])} around Baghdad, "
           f"while a similar share went on to qualify ({c['Basra']['completion_pct']:.0f}% and {c['Baghdad']['completion_pct']:.0f}%)."),
        h2_groups="Women cost nearly three times as much as men",
        review="\n".join(f"        <li>{x}</li>" for x in COMMON_REVIEW(d) + [
            "<b>Incentive to confirm.</b> The study settings record $1 per respondent until 10 Feb 2026, then $0 for the last three days. The Arabic welcome message promises \"0.70 dinar\" of credit, the same text as Jordan's. Confirm what respondents in Iraq were sent before stating it.",
            "<b>Excluded:</b> <code>embed-pilot-iraq</code> (Nov 2025, a separate pilot survey: 3 days, $230).",
            "Study id: <code>embed-iraq</code>. One study, so the page says what happened, not what Iraq costs in general.",
        ]),
    )


def _eg(d, all_d):
    c = d["by_city"]
    ov = d["_overlap"]
    gc = d["_greater_cairo"]
    return dict(
        lede=(f"In one Virtual Lab study in December 2025 and January 2026, advertising around Cairo, Giza and Alexandria "
              f"recruited <b>{d['qualified']:,} qualified respondents</b> for <b>{money(d['spend'], False)}</b>, or "
              f"<b>{money(d['cost'])} each</b>. No city cost more than {money(c['Alexandria']['cost'])}."),
        facts=facts([(f"{d['qualified']:,}", f"qualified respondents, {window(d)}"),
                     (money(d["cost"]), "advertising cost per qualified respondent"),
                     (money(d["by_gender"]["Women"]["cost"]), "per qualified woman; a man cost " + money(d["by_gender"]["Men"]["cost"])),
                     (f"{d['people']['unique_people']:,}", "people surveyed in Egypt, Dec 2025 – Feb 2026")]),
        h2="Every city cost under 60 cents",
        p=(f"The study advertised in a radius area of 10 miles (16 km) around each city. Cairo and Giza sit {ov['centre_km']:.0f} km apart, so their "
           f"radius areas overlap: {ov['giza_share_pct']:.0f}% of the Giza area is also inside the Cairo area. Taken together they cost "
           f"{money(gc['cost'])} per qualified respondent, against {money(c['Alexandria']['cost'])} around Alexandria."),
        h2_groups="Women cost more than men; age made little difference",
        review="\n".join(f"        <li>{x}</li>" for x in COMMON_REVIEW(d) + [
            f"<b>The report's own figure is very different.</b> The latest report counts {d['report_qualified']:,} qualified and so {money(d['spend'] / d['report_qualified'])} each. It was generated on 15 Jan under an interim rule: answering <code>recruit_learn</code>, an invitation to a follow-up that comes after the payment question and was answered by about a quarter of those who finished. Under the study's final rule, the phone-number question, the count is {d['qualified']:,}.",
            "<b>Cairo against Giza is not a clean comparison.</b> The two ad sets were aimed at mostly the same area, so the page pools them in the text and shows both in the table.",
            "<b>Excluded:</b> <code>embed-pilot-egypt</code> (Nov 2025, a separate pilot survey: $248, under $500; none of its respondents carries an Egyptian city).",
            "Study id: <code>embed-egypt</code>. One study, so the page says what happened, not what Egypt costs in general.",
        ]),
    )


def _ma(d, all_d):
    c = d["by_city"]
    iq, eg = all_d["IQ"], all_d["EG"]
    return dict(
        lede=(f"In one Virtual Lab study in December 2025 and January 2026, advertising around Casablanca, Fez and Marrakesh "
              f"recruited <b>{d['qualified']:,} qualified respondents</b> for <b>{money(d['spend'], False)}</b>, or "
              f"<b>{money(d['cost'])} each</b>. By city, the cost ran from <b>{money(c['Casablanca']['cost'])}</b> around Casablanca "
              f"to <b>{money(c['Fez']['cost'])}</b> around Fez."),
        facts=facts([(f"{d['qualified']:,}", f"qualified respondents, {window(d)}"),
                     (money(c["Casablanca"]["cost"]), "per qualified respondent, 16 km around Casablanca"),
                     (money(c["Fez"]["cost"]), "per qualified respondent, 16 km around Fez"),
                     (f"{d['people']['unique_people']:,}", "people surveyed in Morocco, Nov 2025 – Feb 2026")]),
        h2="Casablanca cost a third as much as Fez",
        p=(f"The study advertised in a radius area of 10 miles (16 km) around each of the three cities, with the same survey and the same quotas in each. "
           f"A qualified respondent cost {money(c['Casablanca']['cost'])} around Casablanca, {money(c['Marrakech']['cost'])} around Marrakesh and "
           f"{money(c['Fez']['cost'])} around Fez."),
        after_city=(f"    <p>Reaching people was not the expensive part. Each person who started the survey cost {money(d['spend'] / d['started'])} in advertising, "
                    f"close to Iraq's {money(iq['spend'] / iq['started'])}. But only {100 * d['qualified'] / d['started']:.0f}% of them went on to qualify, "
                    f"against {100 * iq['qualified'] / iq['started']:.0f}% in Iraq and {100 * eg['qualified'] / eg['started']:.0f}% in Egypt. "
                    f"Most who dropped out stopped at or before the consent question.</p>\n"),
        h2_groups="Women and older respondents cost more",
        review="\n".join(f"        <li>{x}</li>" for x in COMMON_REVIEW(d) + [
            f"<b>Why so few qualified is not known.</b> The drop is at the start: {d['_drop']['no_answer_or_consent_pct']:.0f}% of people who started stopped at or before consent in Morocco, against {all_d['IQ']['_drop']['no_answer_or_consent_pct']:.0f}% in Iraq and {all_d['EG']['_drop']['no_answer_or_consent_pct']:.0f}% in Egypt. We can show where, not why (language is one candidate: the survey was offered in Arabic and French). Judged explainable at that level; say if that is not enough for rule 8.",
            "<b>Excluded:</b> <code>embed-pilot-morocco</code> (Nov 2025, a separate pilot survey: 2 days, $73).",
            "Study id: <code>embed-morocco</code>. One study, so the page says what happened, not what Morocco costs in general.",
        ]),
    )


TEXT.update(IQ=_iq, EG=_eg, MA=_ma)


# ---------------------------------------------------------------- data files
META = lambda: OrderedDict(
    generated="2026-09-24",
    status="PILOT v4 - D-032. Not registered in CLAIMS.md, not on the site. Scratch output for review.",
    rules=[
        "Ad account spends in US dollars (tested by CPM: naira accounts show CPMs of 500+)",
        "The study's per-group report reconciles with Meta's reported spend, so group costs add up to the total",
        "Ads ran at least 7 days (counted here as days with spend > 0)",
        "At least $500 of advertising and at least 200 qualified respondents",
        "Recruitment waves only: baseline or single-wave studies. Follow-up waves re-contact people and are excluded",
        "Studies that fed one survey at the same time are combined: spend summed, respondents counted once",
        "The targeting can be stated in a sentence, and it did what it said",
        "The result can be explained",
    ],
    definitions=OrderedDict(
        qualified_respondent=("a person counted toward one of the study's quota groups: in the targeted group (Gender, Age and City "
                              "from the ad that reached them) and past the study's own quota rule, answering the phone-number question "
                              "that follows the main survey."),
        qualified_source=("RECOMPUTED, not the report's current_participants: the latest reports of embed-egypt, embed-morocco and "
                          "embed-jordan predate the final quota rule (15 Jan 2026 18:14-18:16 UTC, phone_number; pre_pay_info for "
                          "embed-ksa). sql/qualified.sql counts, per stratum, people in the study's own inference pool whose ad "
                          "metadata matches the stratum, who arrived in the study's window, and who answered the rule question. "
                          "Validation: embed-iraq's report ran under phone_number and gives 1,413; the recomputation gives 1,415."),
        ad_cost=("Meta-reported advertising spend (per-group lifetime_spent from the latest FACEBOOK_ADOPT report, which reconciles "
                 "with Insights) / qualified respondents. Excludes incentives, the survey platform and our fee."),
        ad_days="days on which the study's campaign recorded spend > 0",
    ),
    terms=OrderedDict(
        radius_area=("a Meta city target plus a radius (here 10 miles, 16.1 km), or a pin plus a radius. Never 'circles' and never "
                     "urban/rural."),
    ),
    queries="sql/*.sql in this folder (read-only). Raw outputs in raw/.",
)


def overlap(d):
    g, c = city_point("Giza"), city_point("Cairo")
    laea = Transformer.from_crs("EPSG:4326", "+proj=laea +lat_0=30 +lon_0=31.2 +units=km", always_xy=True).transform
    cg = transform(laea, bm.circle(g["lon"], g["lat"], 10 * MI))
    ccairo = transform(laea, bm.circle(c["lon"], c["lat"], 10 * MI))
    return dict(centre_km=round(bm.hav(g["lat"], g["lon"], c["lat"], c["lon"]), 1),
                giza_share_pct=round(100 * cg.intersection(ccairo).area / cg.area, 1),
                area_km2_each=round(cg.area))


def drop():
    out = {}
    for r in csv.DictReader(open(os.path.join(HERE, "raw", "dropoff.tsv")), delimiter="\t"):
        n = int(r["people"])
        out[r["cc"]] = dict(people=n, no_baseline_answer=int(r["no_baseline_answer"]),
                            stopped_at_consent=int(r["stopped_at_consent"]),
                            no_answer_or_consent_pct=round(100 * (int(r["no_baseline_answer"]) + int(r["stopped_at_consent"])) / n, 1),
                            reached_height=int(r["reached_height"]), screened_or_declined=int(r["screened_or_declined"]))
    return out


def camps():
    return {r["slug"]: r for r in csv.DictReader(open(os.path.join(HERE, "raw", "camps.tsv")), delimiter="\t")}


def data_file(cc, d, tgt, tgt_created):
    C = COUNTRY[cc]
    cp = camps()
    pilot = {"IQ": ["embed-pilot-iraq"], "EG": ["embed-pilot-egypt"], "MA": ["embed-pilot-morocco"]}[cc]
    excl = [OrderedDict(slug=p, reason="pilot on a separate survey (Embed Mena Pilot), Nov 2025; fails rule 3 and/or rule 4",
                        campaigns=[dict(camp=v["camp"], days_with_rows=int(v["days"]), first=v["min"], last=v["max"], spend=float(v["round"]))
                                   for k, v in [(r["slug"], r) for r in csv.DictReader(open(os.path.join(HERE, "raw", "camps.tsv")), delimiter="\t")] if k == p])
            for p in pilot]
    if cc == "EG":
        excl[0]["note"] = "none of the pilot's recorded respondents carries an Egyptian city in its ad metadata"
    excl += [OrderedDict(slug="embed-ksa", reason="Saudi Arabia, same programme: see excluded-sa.json"),
             OrderedDict(slug="embed-jordan", reason="Jordan, same programme: see excluded-jo.json")]
    return OrderedDict(
        _meta=META(),
        country=cc,
        all_people_surveyed=OrderedDict(unique_people=d["people"]["unique_people"], first=d["people"]["first"],
                                        last=d["people"]["last"],
                                        note=("Anyone with a recorded answer whose ad carried one of this country's cities, in any study "
                                              "on the current platform (the embed programme and its pilot are the only ones). The "
                                              "studies share one survey pool, so people are assigned by ad city, never by study table.")),
        study=OrderedDict(
            slug=d["slug"], fielded=window(d), ad_days=d["ad_days"], first_ad_day=d["first_ad_day"], last_ad_day=d["last_ad_day"],
            started_survey=d["started"], qualified=d["qualified"], spend=d["spend"], cost=d["cost"],
            insights_spend=d["insights_spend"], report_created=d["report_created"],
            report_qualified=d["report_qualified"], report_cost=round(d["spend"] / d["report_qualified"], 2),
            incentive=INCENTIVE, channel=f"Messenger ({C['langs']})",
            quota_rule="answered the phone-number question that follows the main survey (final strata conf, 15 Jan 2026)",
            quotas="City (3, Meta city + 10 mi radius) × Gender × Age (30–39, 40–49, 50–65): 18 groups, quota 0.045 each",
            screening="survey ends early for under-30s and for anyone saying they live outside the three cities",
            ad_account_currency="USD (CPM " + ", ".join(f"{k} ${1000 * v['spend'] / v['impressions']:.2f}" for k, v in d["insights_by_city"].items()) + ")",
        ),
        targeting=OrderedDict(strata_conf_created=tgt_created, stable_during_fielding=True, cities=tgt,
                              city_points={c: dict(source="GeoNames", geonameid=CITY_POINT[c][1],
                                                   lat=city_point(c)["lat"], lon=city_point(c)["lon"]) for c in tgt}),
        by_city=d["by_city"], by_gender=d["by_gender"], by_age=d["by_age"],
        insights_by_city=d["insights_by_city"],
        strata=d["strata"],
        funnel=d["_drop"],
        programme=OrderedDict((k, OrderedDict(slug=v["slug"], qualified=v["qualified"], spend=v["spend"], cost=v["cost"],
                                              fielded=window(v), ad_days=v["ad_days"], started=v["started"]))
                              for k, v in ALL.items() if k in PASS),
        checks=[
            f"per-group spend sums to {money(d['spend'])}; Insights spend {money(d['insights_spend'])}",
            f"qualified recomputed: {d['qualified']:,}; the latest report counts {d['report_qualified']:,} under the rule in force when it ran",
            "targeting (city keys, 10 mi radius, home + recent) unchanged from before the first ad day to the end",
            "respondent arrivals track the spend days (one-day timezone offset); a tail arrives after the ads stop",
        ] + ([f"Cairo and Giza radius areas overlap: centres {d['_overlap']['centre_km']} km apart, {d['_overlap']['giza_share_pct']}% of the Giza area inside Cairo's"] if cc == "EG" else []),
        excluded_for_review=excl,
        strata_note="Stratum ids are the study's own labels (City:Marrakech is Meta's Marrakesh).",
    )


EXCLUDED = {
    "SA": lambda d: OrderedDict(
        country="SA", slug="embed-ksa", verdict="HELD OUT: rules 7 and 8",
        figures=OrderedDict(spend=d["spend"], insights_spend=d["insights_spend"], qualified_recomputed=d["qualified"],
                            cost_recomputed=d["cost"], report_qualified=d["report_qualified"],
                            report_cost=round(d["spend"] / d["report_qualified"], 2), ad_days=d["ad_days"],
                            fielded=window(d), started=d["started"], by_city=d["by_city"], by_gender=d["by_gender"],
                            by_age=d["by_age"], insights_by_city=d["insights_by_city"], people=d["people"]),
        reasons=[
            "Rule 7: from 6 to 18 Dec 2025 the stored strata conf aimed every 'Jeddah' ad set at Meta city key 2116956 (Mecca). "
            "$3,483 of the Jeddah strata's $5,086 (68%) was spent in that window, so the Jeddah / Mecca split is not what it says.",
            "Cities carry no radius from 6 Dec (Meta's own city area, not a radius area), and a 10 mi radius on 5 Dec: the geography changed on day 2.",
            "Rule 8: the figure is real (USD account; report spend reconciles with Insights to $0.13; CPM $1.76-1.98, like the other countries), "
            "but not explained. The gap is before the survey: clicks cost $0.21 (vs $0.03-0.11 elsewhere), 0.9% of impressions were clicked "
            "(vs 1.7-4.0%), and each person who started cost $3.30 in ads (Egypt $0.22, Iraq $0.89). Why people in Saudi Arabia engaged less "
            "is unknown (creatives differed: 'Group 2', 'Cats'; incentive a 20-riyal gift card).",
            "Not an eligibility artefact: no nationality screen applied in KSA (nationality_no = 0 there; it fired only in the UAE). Completion "
            "(30%) is lower than Iraq/Egypt (44-47%), which adds to, but does not make, the cost.",
            "Report vs recomputed: the latest report (15 Jan 16:40) counted recruit_learn answers (848); the final rule pre_pay_info gives 1,069.",
        ],
        also_noted="embed-uae (not in scope) aims its 'Dubai' ad sets at Mecca as well as Dubai, so some UAE-labelled respondents are in Saudi Arabia.",
        pilots=["embed-pilot-ksa (6 days, $137)", "embed-pilot-ksa-2 (3 days, $87)"],
    ),
    "JO": lambda d: OrderedDict(
        country="JO", slug="embed-jordan", verdict="HELD OUT: rule 3 (5 days with spend)",
        figures=OrderedDict(spend=d["spend"], insights_spend=d["insights_spend"], qualified_recomputed=d["qualified"],
                            cost_recomputed=d["cost"], report_qualified=d["report_qualified"],
                            report_cost=round(d["spend"] / d["report_qualified"], 2), ad_days=d["ad_days"],
                            fielded=window(d), started=d["started"], by_city=d["by_city"], by_gender=d["by_gender"],
                            by_age=d["by_age"], people=d["people"]),
        reasons=[
            "Rule 3: spend on 5 days only (11-12 Dec, 18-19 Dec, 6 Jan). The recipe's query reports 19, because it counts days with a row and no spend.",
            "If Nandan counts the 27-day window instead, Jordan passes the other rules and costs $0.71 per qualified ($614, 859). "
            "Then note the targeting mixes three kinds: Amman as a Meta city with no radius, the whole Zarqa governorate, and an 8 km (5 mi) pin at Irbid "
            "(1.2 km from GeoNames' Irbid). Statable in one sentence, but the three costs compare different kinds of area.",
        ],
        pilots=["embed-pilot-jordan (2 days, $109)"],
    ),
}


# ---------------------------------------------------------------- png
TOK = {"--ink": "#1F272E", "--ink-2": "#4A555E", "--ink-3": "#79858D", "--rule": "#CFD9DD",
       "--rule-2": "#AEBCC2", "--surface": "#FFFFFF", "--sunk": "#E5EBED", "--paper": "#F1F4F5",
       "--data": "#1D5F6E", "--data-2": "#9DB6BC", "--brass": "#7A5C1E"}


def png(path):
    out = os.path.join(HERE, "png")
    os.makedirs(out, exist_ok=True)
    svg = re.sub(r"var\((--[a-z0-9-]+)\)", lambda m: TOK[m.group(1)], open(path).read())
    tmp = os.path.join(out, "tmp.svg")
    open(tmp, "w").write(svg)
    env = dict(os.environ, FONTCONFIG_FILE=os.path.join(SP, "geo", "fonts.conf"))
    for w, suf in ((1520, ""), (800, "-phone")):
        p = os.path.join(out, os.path.basename(path)[:-4] + suf + ".png")
        subprocess.run(["rsvg-convert", "-w", str(w), "-b", TOK["--paper"], "-o", p, tmp], check=True, env=env)
        print("wrote", p)
    os.remove(tmp)


# ---------------------------------------------------------------- main
ALL = OrderedDict()
if __name__ == "__main__":
    D = drop()
    for cc in analyse.STUDIES:
        ALL[cc] = analyse.country_data(cc)
        ALL[cc]["_drop"] = D[cc]
    ALL["EG"]["_overlap"] = overlap(ALL["EG"])
    gc = [ALL["EG"]["by_city"][k] for k in ("Cairo", "Giza")]
    ALL["EG"]["_greater_cairo"] = dict(spend=round(sum(a["spend"] for a in gc), 2), qualified=sum(a["qualified"] for a in gc),
                                       cost=round(sum(a["spend"] for a in gc) / sum(a["qualified"] for a in gc), 2))
    for cc in PASS:
        d = ALL[cc]
        tgt, tgt_created = radius_of(d["slug"])
        path, s = build_map(cc, d, tgt)
        if "png" in sys.argv[1:]:
            png(path)
        f = data_file(cc, d, tgt, tgt_created)
        if cc == "EG":
            f["cairo_giza_overlap"] = d["_overlap"]
            f["cairo_and_giza_pooled"] = d["_greater_cairo"]
        json.dump(f, open(os.path.join(HERE, f"country-{cc.lower()}.json"), "w"), indent=1, ensure_ascii=False)
        open(os.path.join(HERE, f"section-{cc.lower()}.html"), "w").write(section(cc, d, ALL, s))
        print("wrote", f"country-{cc.lower()}.json", f"section-{cc.lower()}.html")
    for cc, fn in EXCLUDED.items():
        json.dump(fn(ALL[cc]), open(os.path.join(HERE, f"excluded-{cc.lower()}.json"), "w"), indent=1, ensure_ascii=False)
        print("wrote", f"excluded-{cc.lower()}.json")
