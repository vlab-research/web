#!/usr/bin/env python3
"""Nigeria, campaign-2-nigeria-hpv-baseline (9-18 Apr 2025): inside vs outside the radius
areas in FCT, Nasarawa and Adamawa. REVIEW MAP ONLY -- the split fails rules 7 and 8
(see country-ng-split.json), so this is drawn to show why, not for the page.

    ../../geo/venv/bin/python build.py

Inputs, all in this directory, all pulled read-only from vprod:
  c2_strata_hist.tsv   every strata conf of the study (latest = the one used from 16 Apr)
  c2_adopt.tsv         latest FACEBOOK_ADOPT report (2025-04-18 20:31)
  c2_daily.tsv         Insights spend per stratum per day
  c2_resp_daily.tsv    starts / qualified per State x Gender x day (inference_data)
  c2_insights.tsv      summed daily reach and Meta-counted conversations per stratum
Writes nigeria-2025-radius-review.svg, geometry.json.
"""
import csv, json, os, sys
from collections import OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.join(HERE, "..", "..", "geo")
sys.path.insert(0, GEO)
import build_maps as bm  # noqa: E402
from shapely.geometry import Point, box  # noqa: E402
from shapely.ops import transform, unary_union  # noqa: E402
from pyproj import Transformer  # noqa: E402

csv.field_size_limit(10 ** 9)
rows = list(csv.DictReader(open(os.path.join(HERE, "c2_strata_hist.tsv")), delimiter="\t"))
strata = json.loads(rows[-1]["conf"])
rep = list(csv.DictReader(open(os.path.join(HERE, "c2_adopt.tsv")), delimiter="\t"))[0]
report = json.loads(rep["details"])

STATES = {"Abuja": "Federal Capital Territory", "Adamawa": "Adamawa", "Nasarawa": "Nassarawa"}
units = bm.admin1("NGA", "name")
if "Nassarawa" not in units:
    units = {k.replace("Nasarawa", "Nassarawa"): v for k, v in units.items()}
laea = Transformer.from_crs("EPSG:4326", "+proj=laea +lat_0=9 +lon_0=9 +units=km", always_xy=True).transform
A = lambda g: round(transform(laea, g).area, 0)
nga = unary_union([g for g in units.values()])

# ---- per state: which arm is inside, the pins, the geometry
facts = OrderedDict()
for st, ne in STATES.items():
    sides = {}
    for s in strata:
        lvl = bm.part(s["id"], "State").replace("  ", " ")
        if not lvl.startswith(st):
            continue
        arm = lvl.split()[-1]
        ft = s["facebook_targeting"]
        inc, exc = ft["geo_locations"], ft.get("excluded_geo_locations") or {}
        sides.setdefault(arm, dict(inc=inc, exc=exc, spend=0.0, n=0, strata=[]))
        sides[arm]["spend"] += report[s["id"]]["lifetime_spent"]
        sides[arm]["n"] += report[s["id"]]["current_participants"]
        sides[arm]["strata"].append(s["id"])
    inside_arm = [a for a, v in sides.items() if v["inc"].get("custom_locations")][0]
    outside_arm = [a for a in sides if a != inside_arm][0]
    pins = sides[inside_arm]["inc"]["custom_locations"]
    # the outside side must exclude exactly the inside side's pins
    ex_pins = sides[outside_arm]["exc"]["custom_locations"]
    key = lambda cs: sorted((c["latitude"], c["longitude"], c["radius"], c["distance_unit"]) for c in cs)
    assert key(pins) == key(ex_pins), st
    assert [r["name"] for r in sides[outside_arm]["inc"]["regions"]][0].startswith(ne.replace("Nassarawa", "Nasarawa")) \
        , st
    pg = units[ne]
    circ = unary_union([bm.circle(c["longitude"], c["latitude"], bm.km(c)) for c in pins])
    spill = circ.difference(pg)
    spill_by = {k: A(circ.intersection(g)) for k, g in units.items() if k != ne and circ.intersection(g).area > 0}
    spill_abroad = A(circ.difference(nga))
    pin_facts = []
    for c in pins:
        near = sorted(((bm.hav(c["latitude"], c["longitude"], x["lat"], x["lon"]), x["name"], x["pop"])
                       for x in bm.geonames("NG") if x["pop"] >= 10000))[:3]
        nm = bm.name_point(c["latitude"], c["longitude"], "NGA", "NG")
        pin_facts.append(dict(lat=c["latitude"], lon=c["longitude"], radius=f'{c["radius"]} {c["distance_unit"]}',
                              radius_km=round(bm.km(c), 1), meta_primary_city_id=c.get("primary_city_id"),
                              nearest_named_place_5km=nm,
                              nearest_towns_10k=[dict(name=n, km=round(d, 1), pop=p) for d, n, p in near]))
    facts[st] = dict(
        state_ne=ne, inside_arm=inside_arm, outside_arm=outside_arm, pins=pin_facts,
        state_area_km2=A(pg), inside_area_km2_in_state=A(circ.intersection(pg)),
        inside_area_km2_outside_state=A(spill), spill_by_neighbour_km2=spill_by, spill_outside_nigeria_km2=spill_abroad,
        inside=dict(arm=inside_arm, spend=round(sides[inside_arm]["spend"], 2), qualified=sides[inside_arm]["n"],
                    cost=round(sides[inside_arm]["spend"] / sides[inside_arm]["n"], 2)),
        outside=dict(arm=outside_arm, spend=round(sides[outside_arm]["spend"], 2), qualified=sides[outside_arm]["n"],
                     cost=round(sides[outside_arm]["spend"] / sides[outside_arm]["n"], 2)),
        _geom=dict(pg=pg, circ=circ))

# Abuja city centre (GeoNames PPLC) against the FCT pin
abuja = [x for x in bm.geonames("NG") if x["code"] == "PPLC"][0]
p = facts["Abuja"]["pins"][0]
facts["Abuja"]["city_centre_to_pin_km"] = round(bm.hav(abuja["lat"], abuja["lon"], p["lat"], p["lon"]), 1)

# ---- map (review only)
W = 760
body = [bm.text(0, 12, "For review, not for publication · Nigeria, 9–18 Apr 2025", "gm-eye")]
fit1 = unary_union([units["Federal Capital Territory"], units["Nassarawa"]])
p1 = (0, 26, 460, 330)
f1 = bm.Frame(7.9, 8.6, fit1, p1, pad=10)
p2 = (480, 26, 280, 330)
f2 = bm.Frame(12.4, 9.3, units["Adamawa"], p2, scale=f1.s * 0.62)
for fr, keys in ((f1, ("Abuja", "Nasarawa")), (f2, ("Adamawa",))):
    for k, g in units.items():
        body.append(bm.path(fr.g(g, simplify=0.3), "gm-ctx0"))
    for st in keys:
        G = facts[st]["_geom"]
        body.append(bm.path(fr.g(G["pg"], simplify=0.3), "gm-land"))
        body.append(bm.path(fr.g(G["pg"].difference(G["circ"]), simplify=0.3), "gm-area"))
        body.append(bm.path(fr.g(G["circ"], simplify=0.2), "gm-circ"))
        body.append(bm.path(fr.g(G["pg"], simplify=0.3), "gm-outline"))
    body.append(f'<rect class="gm-panel" x="{fr.bx[0]}" y="{fr.bx[1]}" width="{fr.bx[2]}" height="{fr.bx[3]}"/>')
    body.append(bm.scalebar(fr.bx[0] + 10, fr.bx[1] + fr.bx[3] - 10, fr, 50))

# orientation towns (GeoNames), labelled as such
TOWNS = [(f1, "Abuja", (0, -8, "middle")), (f1, "Kuje", (-6, 4, "end")), (f1, "Lafia", (0, -8, "middle")),
         (f1, "Keffi", (6, -4, "start")), (f1, "Nasarawa", (0, 14, "middle")), (f1, "Akwanga", (0, -8, "middle")),
         (f2, "Yola", (-6, 12, "end")), (f2, "Jimeta", (-6, -4, "end")), (f2, "Mubi", (6, 4, "start"))]
gn = sorted(bm.geonames("NG"), key=lambda x: -x["pop"])
town_src = {}
for fr, nm, (dx, dy, an) in TOWNS:
    x = next(x for x in gn if x["name"] == nm and x["code"].startswith("PPL"))
    town_src[nm] = dict(lat=x["lat"], lon=x["lon"], geonameid=x["id"], pop=x["pop"])
    px, py = fr.xy(x["lon"], x["lat"])
    body.append(bm.cell(px, py, "gm-cell", 4))
    body.append(bm.text(px + dx, py + dy, nm, "gm-lab2 gm-halo", an))
for fr, (lon, lat), s in ((f1, (7.05, 8.55), "FCT"), (f1, (8.3, 8.25), "NASARAWA"), (f2, (12.1, 10.1), "ADAMAWA")):
    px, py = fr.xy(lon, lat)
    body.append(bm.text(px, py, s, "gm-eye gm-halo", "middle"))
body.append(bm.text(p2[0] + 8, p2[1] + 18, "scale 0.62× the left panel", "gm-tiny"))

y = p1[1] + p1[3] + 26
body.append(bm.text(0, y, "Ad cost per qualified respondent, gender pooled. Arm = the survey form the ads led to.", "gm-eye"))
y += 16
rows_ = []
for st, lab in (("Abuja", "FCT"), ("Nasarawa", "Nasarawa"), ("Adamawa", "Adamawa")):
    F = facts[st]
    rows_.append((f"{lab}, inside", f'arm {F["inside"]["arm"]}', F["inside"]["cost"], F["inside"]["qualified"], F["inside"]["spend"], "gm-bar"))
    rows_.append((f"{lab}, outside", f'arm {F["outside"]["arm"]}', F["outside"]["cost"], F["outside"]["qualified"], F["outside"]["spend"], "gm-bar2"))
y = bm.cost_rows(body, 0, y, rows_, W, row_h=34, label_w=150)
body.append(bm.text(0, y + 8, "Arm A is the cheaper side in all three states, whichever side of the line it was on.", "gm-note"))
body.append(bm.text(0, y + 24, "Report of 18 Apr 2025. Towns from GeoNames, for orientation only.", "gm-note"))
H = y + 34
desc = "; ".join(f'{st}: inside (arm {F["inside"]["arm"]}) {bm.money(F["inside"]["cost"])}, outside (arm {F["outside"]["arm"]}) '
                 f'{bm.money(F["outside"]["cost"])}' for st, F in facts.items())
s = bm.svg(W, H, "Review: inside against outside the radius areas in FCT, Nasarawa and Adamawa, April 2025", desc + ".", body, "ng25")
open(os.path.join(HERE, "nigeria-2025-radius-review.svg"), "w").write(s)
for F in facts.values():
    F.pop("_geom")
json.dump(dict(report_created=rep["created"], towns=town_src, states=facts), open(os.path.join(HERE, "geometry.json"), "w"), indent=1)
print(json.dumps(facts, indent=1))
