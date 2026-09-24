#!/usr/bin/env python3
"""Pakistan country page (D-032 pilot recipe): map + summary for pakistan-hpv-pannel.

    ../../geo/venv/bin/python build.py

Inputs, all in this directory, pulled read-only from vprod on 2026-09-24:
  confs_all.tsv   every study_confs row of the four Pakistan studies
  adopt_<sid>.tsv the latest FACEBOOK_ADOPT report per study (ORDER BY created DESC LIMIT 1)
Map helpers and Natural Earth / GeoNames come from ../../geo (build_maps.py).

Writes pakistan-sindh.svg, summary.json. Nothing here writes to the database.
"""
import csv, json, os, sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "geo"))
import build_maps as B  # noqa: E402
from shapely.geometry import Point, box  # noqa: E402
from shapely.ops import unary_union, transform  # noqa: E402
from pyproj import Transformer  # noqa: E402

csv.field_size_limit(10**9)
SID = "361859fc-8d49-46df-bfe7-500f939a5577"  # pakistan-hpv-pannel
SPEND_INSIGHTS = 4444.25  # recruitment_data_events, max per campaign x stratum x day, summed (see country-pk.json)

# ---------------------------------------------------------------- data
rows = list(csv.DictReader(open(os.path.join(HERE, "confs_all.tsv")), delimiter="\t"))
strata_versions = [(r["created"], json.loads(r["conf"])) for r in rows
                   if r["study_id"] == SID and r["conf_type"] == "strata"]
strata_versions.sort()
# targeting identical in all three saved versions (27 Aug, 3 Sep, 10 Sep 2025)
geo_of = lambda s: {x["id"]: json.dumps(x["facebook_targeting"], sort_keys=True) for x in s}
assert all(geo_of(v) == geo_of(strata_versions[0][1]) for _, v in strata_versions), "targeting changed"
first_created, strata = strata_versions[0]
rep = next(csv.DictReader(open(os.path.join(HERE, f"adopt_{SID}.tsv")), delimiter="\t"))
report = json.loads(rep["details"])

# stratum label -> place. Labels are the study's own; the pins, not the labels, define the place.
PLACE = OrderedDict([
    ("Hyderabad", dict(labels=["Hyderabad"], title="Hyderabad")),
    ("Karachi", dict(labels=["Central", "East", "West", "Malir"], title="Karachi")),
    ("Sukkur", dict(labels=["Sukkar"], title="Around Sukkur")),
    ("Larkana", dict(labels=["Larkana"], title="Around Larkana")),
])
label_place = {l: p for p, d in PLACE.items() for l in d["labels"]}

pins = {}  # stratum label -> custom_locations (identical for the two genders)
for x in strata:
    g = x["facebook_targeting"]["geo_locations"]
    assert set(g) == {"custom_locations", "location_types"} and not x["facebook_targeting"].get("excluded_geo_locations")
    lab = x["metadata"]["District"]
    pins.setdefault(lab, g["custom_locations"])
    assert pins[lab] == g["custom_locations"], lab

acc = OrderedDict((p, dict(spend=0.0, n=0, women=[0.0, 0], men=[0.0, 0])) for p in PLACE)
tot = [0.0, 0]
for sid, v in report.items():
    lab = B.part(sid, "District")
    gen = B.part(sid, "Gender").lower()
    a = acc[label_place[lab]]
    a["spend"] += v["lifetime_spent"]; a["n"] += v["current_participants"]
    a[gen][0] += v["lifetime_spent"]; a[gen][1] += v["current_participants"]
    tot[0] += v["lifetime_spent"]; tot[1] += v["current_participants"]
assert abs(tot[0] - SPEND_INSIGHTS) < 0.01, tot
assert tot[1] == 3053, tot

provs = B.admin1("PAK")
sindh = provs["Sindh"]
laea = Transformer.from_crs("EPSG:4326", "+proj=laea +lat_0=26 +lon_0=68.5 +units=km", always_xy=True).transform
A = lambda g: transform(laea, g).area

facts = OrderedDict()
polys = {}
for p, d in PLACE.items():
    cl = [c for l in d["labels"] for c in pins[l]]
    ps = [B.circle(c["longitude"], c["latitude"], B.km(c)) for c in cl]
    polys[p] = ps
    u = unary_union(ps)
    a = acc[p]
    facts[p] = dict(
        stratum_labels=d["labels"], radius_areas=len(cl),
        radius_km=sorted({B.km(c) for c in cl}),
        per_label={l: dict(radius_areas=len(pins[l]), radius_km=sorted({B.km(c) for c in pins[l]})) for l in d["labels"]},
        union_area_km2=round(A(u), 1),
        spend=round(a["spend"], 2), qualified=a["n"], cost=round(a["spend"] / a["n"], 2),
        women=dict(spend=round(a["women"][0], 2), qualified=a["women"][1], cost=round(a["women"][0] / a["women"][1], 2)),
        men=dict(spend=round(a["men"][0], 2), qualified=a["men"][1], cost=round(a["men"][0] / a["men"][1], 2)),
        pins_outside_sindh_polygon=sum(1 for c in cl if not sindh.contains(Point(c["longitude"], c["latitude"]))),
        named_pins={})
    for c in cl:
        nm = B.name_point(c["latitude"], c["longitude"], "PAK", "PK")
        k = nm["name"] if nm else "(no named place within 5 km)"
        facts[p]["named_pins"][k] = facts[p]["named_pins"].get(k, 0) + 1

# overlap between the four Karachi sets, so the pooling is on the record
kar = {l: unary_union([B.circle(c["longitude"], c["latitude"], B.km(c)) for c in pins[l]]) for l in PLACE["Karachi"]["labels"]}
overlaps = {}
ks = list(kar)
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        o = A(kar[ks[i]].intersection(kar[ks[j]]))
        if o > 0:
            overlaps[f"{ks[i]} & {ks[j]}"] = round(o, 1)
all_u = unary_union([q for ps in polys.values() for q in ps])
share_sindh = 100 * A(all_u.intersection(sindh)) / A(sindh)

# ---------------------------------------------------------------- drawing
W = 760
body = [B.text(0, 12, "Sindh, Pakistan, 2025 · 265 radius areas in four places", "gm-eye")]

def ctx(frame, bounds):
    for name, g in provs.items():
        if name != "Sindh" and g.intersects(box(*bounds)):
            body.append(B.path(frame.g(g, simplify=0.3), "gm-ctx0"))
    body.append(B.path(frame.g(sindh, simplify=0.3), "gm-land"))

def areas(frame, p, simp=0.3, rings=True):
    body.append(B.path(frame.g(unary_union(polys[p]), simplify=simp), "gm-circ"))
    for q in (polys[p] if rings else []):
        body.append(B.path(frame.g(q, simplify=simp), "gm-ring"))

def towns(frame, lonlat_box, names, offs):
    shown = []
    for t in B.places_near(box(*lonlat_box), "PAK", "PK", min_pop=50000):
        if t["name"] not in names:
            continue
        px, py = frame.xy(t["lon"], t["lat"])
        if not frame.box.buffer(-6).contains(Point(px, py)):
            continue
        dx, dy, an = offs.get(t["name"], (7, 4, "start"))
        body.append(B.cell(px, py, "gm-cell", 4))
        body.append(B.text(px + dx, py + dy, t["name"], "gm-lab2 gm-halo", an))
        shown.append(f'{t["name"]} ({t["source"]})')
    return shown

def panel(bx, title, sub=None):
    body.append(B.text(bx[0] + 8, bx[1] + 18, title, "gm-eye gm-halo"))
    if sub:
        body.append(B.text(bx[0] + 8, bx[1] + 32, sub, "gm-tiny gm-halo"))
    body.append(f'<rect class="gm-panel" x="{bx[0]}" y="{bx[1]}" width="{bx[2]}" height="{bx[3]}"/>')

shown = {}
# ---- panel 1: Sindh, true scale, with a frame around each enlarged place
p1 = (0, 26, 300, 400)
f1 = B.Frame(68.8, 26.0, sindh, p1, pad=12)
ctx(f1, sindh.buffer(1.0).bounds)
body.append(B.path(f1.g(sindh, simplify=0.3), "gm-outline"))
for p in PLACE:
    areas(f1, p, simp=0.05, rings=False)
FR = {"Hyderabad": (68.30, 25.17, 68.60, 25.52), "Karachi": (66.90, 24.74, 67.55, 25.56),
      "Upper": (67.90, 27.10, 69.60, 28.00)}
for k, (x0, y0, x1, y1) in FR.items():
    a, b = f1.xy(x0, y1); c, d = f1.xy(x1, y0)
    body.append(f'<rect class="gm-frame" x="{a:.1f}" y="{b:.1f}" width="{c - a:.1f}" height="{d - b:.1f}"/>')
for lab, lon, lat, an, dx in (("Larkana, Sukkur", 69.6, 28.1, "start", 4), ("Hyderabad", 68.62, 25.34, "start", 6),
                               ("Karachi", 67.62, 24.95, "start", 4)):
    px, py = f1.xy(lon, lat)
    body.append(B.text(px + dx, py + 4, lab, "gm-lab2 gm-halo", an))
body.append(B.text(*f1.xy(69.05, 25.9), "SINDH", "gm-eye gm-halo", "middle"))
body.append(B.scalebar(p1[0] + 10, p1[1] + p1[3] - 10, f1, 100))
panel(p1, "Sindh province")

# ---- panel 2: Larkana and Sukkur (5 km radius areas)
p2 = (316, 26, 444, 400)
fitU = box(67.90, 27.10, 69.60, 28.00)
f2 = B.Frame(68.65, 27.55, fitU, p2, pad=8)
ctx(f2, fitU.buffer(0.5).bounds)
body.append(B.path(f2.g(sindh, simplify=0.2), "gm-outline"))
areas(f2, "Larkana"); areas(f2, "Sukkur")
shown["upper"] = towns(f2, (67.6, 26.8, 69.7, 28.3),
                       {"Larkana", "Sukkur", "Rohri", "Shikarpur", "Khairpur", "Ratodero", "Naudero", "Dokri",
                        "Kambar", "Pano Aqil", "Khairpur Mir’s", "Garhi Yasin"},
                       {"Larkana": (-7, -8, "end"), "Sukkur": (0, -24, "middle"), "Rohri": (7, 12, "start"),
                        "Shikarpur": (0, -9, "middle"), "Khairpur Mir’s": (-7, 14, "end"),
                        "Kambar": (-7, 4, "end"), "Ratodero": (-7, -6, "end"), "Dokri": (-7, 12, "end")})
body.append(B.scalebar(p2[0] + 10, p2[1] + p2[3] - 10, f2, 20))
panel(p2, "Larkana and Sukkur, enlarged", "5 km radius areas")

# ---- panel 3: Karachi, panel 4: Hyderabad, at one shared scale
y3 = 26 + 400 + 16
p3 = (0, y3, 500, 430)
fitK = box(66.90, 24.74, 67.55, 25.56)
f3 = B.Frame(67.2, 25.1, fitK, p3, pad=24)
ctx(f3, fitK.buffer(0.3).bounds)
areas(f3, "Karachi")
shown["karachi"] = towns(f3, (66.8, 24.6, 67.7, 25.7), {"Karachi", "Hub"}, {"Karachi": (-7, 16, "end"), "Hub": (7, 4, "start")})
body.append(B.scalebar(p3[0] + 10, p3[1] + p3[3] - 10, f3, 10))
panel(p3, "Karachi, enlarged", "1 km radius areas in the city; 4 km on its edges")

p4 = (516, y3, 244, 430)
f4 = B.Frame(68.45, 25.34, box(68.30, 25.17, 68.60, 25.52), p4, scale=f3.s)
ctx(f4, (67.9, 25.0, 68.9, 25.8))
areas(f4, "Hyderabad")
shown["hyderabad"] = towns(f4, (68.0, 25.0, 68.8, 25.8), {"Hyderabad", "Kotri", "Tando Jam"},
                           {"Hyderabad": (-9, -6, "end"), "Kotri": (-7, 14, "end"), "Tando Jam": (7, 14, "start")})
body.append(B.scalebar(p4[0] + 10, p4[1] + p4[3] - 10, f4, 10))
panel(p4, "Hyderabad, enlarged", "1 km radius areas · Karachi's scale")

# ---- key and cost rows
y = y3 + 430 + 26
body.append(f'<rect class="gm-bar" x="0" y="{y - 9}" width="12" height="12"/>')
body.append(B.text(18, y + 1, "radius area (a pin with a 1, 4 or 5 km radius)", "gm-note"))
body.append(f'<rect class="gm-cell" x="330" y="{y - 5}" width="4" height="4"/>')
body.append(B.text(340, y + 1, "town, for orientation", "gm-note"))
y += 34
body.append(B.text(0, y - 10, "Ad cost per qualified respondent, men and women pooled", "gm-eye"))
cr = []
for p in sorted(facts, key=lambda p: facts[p]["cost"]):
    fc = facts[p]
    rk = fc["radius_km"]
    r = f"{rk[0]:g} km" if len(rk) == 1 else f"{rk[0]:g} and {rk[-1]:g} km"
    cr.append((PLACE[p]["title"], f'{fc["radius_areas"]} radius areas of {r}', fc["cost"], fc["qualified"], fc["spend"], "gm-bar"))
yb = B.cost_rows(body, 0, y, cr, 760, label_w=260, row_h=38)
body.append(B.text(0, yb + 10, f"28 Aug – 13 Sep 2025. Together the radius areas cover {share_sindh:.1f}% of Sindh. "
                               "Cost is recorded per group of radius areas, not per area.", "gm-note"))
H = yb + 20
desc = ("Radius areas in four places in Sindh, August to September 2025, with advertising cost per qualified respondent: " +
        "; ".join(f'{PLACE[p]["title"]}, {facts[p]["radius_areas"]} radius areas, {B.money(facts[p]["cost"])}'
                  for p in sorted(facts, key=lambda p: facts[p]["cost"])) + ".")
svg = B.svg(W, H, "Pakistan, 2025: advertising cost per qualified respondent in four places in Sindh", desc, body, "pk25")
open(os.path.join(HERE, "pakistan-sindh.svg"), "w").write(svg)
print("wrote pakistan-sindh.svg", f"{len(svg) / 1024:.0f} KB")

summary = OrderedDict(
    study="pakistan-hpv-pannel", study_id=SID, strata_conf_created=[c for c, _ in strata_versions],
    report_created=rep["created"], report_spend=round(tot[0], 2), report_qualified=tot[1],
    places=facts, karachi_set_overlaps_km2=overlaps, share_of_sindh_pct=round(share_sindh, 2),
    sindh_area_km2=round(A(sindh)), towns_shown=shown,
    area_method="geodesic circles, union, area in LAEA (lat_0 26, lon_0 68.5); Sindh = Natural Earth 10m admin-1",
    label_rule=B.name_point.__doc__.split("\n")[0] + " (see name_point)")
json.dump(summary, open(os.path.join(HERE, "summary.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps({p: (f["cost"], f["qualified"], f["spend"], f["women"]["cost"], f["men"]["cost"]) for p, f in facts.items()}))
print("overlaps", overlaps, "share", round(share_sindh, 2), "shown", shown)

# ---------------------------------------------------------------- review PNG (light tokens), as geo/render_png.py
import re, subprocess  # noqa: E402
GEO = os.path.join(HERE, "..", "..", "geo")
TOK = {"--ink": "#1F272E", "--ink-2": "#4A555E", "--ink-3": "#79858D", "--rule": "#CFD9DD",
       "--rule-2": "#AEBCC2", "--surface": "#FFFFFF", "--sunk": "#E5EBED", "--paper": "#F1F4F5",
       "--data": "#1D5F6E", "--data-2": "#9DB6BC", "--brass": "#7A5C1E"}
tmp = os.path.join(HERE, "pakistan-sindh.tmp.svg")
open(tmp, "w").write(re.sub(r"var\((--[a-z0-9-]+)\)", lambda m: TOK[m.group(1)], svg))
subprocess.run(["rsvg-convert", "-w", "1520", "-b", TOK["--paper"], "-o", os.path.join(HERE, "pakistan-sindh.png"), tmp],
               check=True, env=dict(os.environ, FONTCONFIG_FILE=os.path.join(GEO, "fonts.conf")))
os.remove(tmp)
print("wrote pakistan-sindh.png")
