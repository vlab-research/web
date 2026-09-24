#!/usr/bin/env python3
"""Targeting maps for the country-page pilot (D-032). Scratch work, not in the repo.

    venv/bin/python fetch_ne.py      # Natural Earth + GeoNames, once
    venv/bin/python build_maps.py    # writes out/*.svg and out/summary.json
    venv/bin/python render_png.py    # review PNGs, light tokens substituted

What each map draws is exactly the Meta ad-set geography of each stratum:
  custom_locations  geodesic circles at true radius (mile -> km at 1.609344)
  regions           whole admin-1 units (Natural Earth 10m boundaries)
  cities            Meta city + radius. Meta gives the city NAME, not its point,
                    so the point comes from GeoNames (named in summary.json)
  places            a Meta place with its own lat/lon + radius, drawn as a circle
  countries + excluded circles   "everywhere except these circles"

Cost = sum(lifetime_spent) / sum(current_participants) over strata sharing one
geography (gender and age collapsed), from the study's latest FACEBOOK_ADOPT
report. Advertising spend only, never a price. current_participants counts the
respondents counted toward the stratum quota, not everyone recruited.

Inputs: geo/targeting.json; ../confs.tsv, ../adopt.tsv, ../studies.json for the
Nigeria studies that are not in targeting.json. Two figures are supplied by the
coordinator and are marked as such in summary.json (Bolivia's fresh report).
"""
import csv, json, math, os, sys
from collections import defaultdict, OrderedDict

from pyproj import Geod, Transformer
from shapely.geometry import Point, Polygon, MultiPolygon, box, shape
from shapely.ops import transform, unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
SP = os.path.dirname(HERE)
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
csv.field_size_limit(10**9)
GEOD = Geod(ellps="WGS84")
MI = 1.609344

T = json.load(open(os.path.join(HERE, "targeting.json")))
A1 = json.load(open(os.path.join(HERE, "ne_10m_admin_1_states_provinces.geojson")))["features"]
PP = [f["properties"] for f in json.load(open(os.path.join(HERE, "ne_10m_populated_places_simple.geojson")))["features"]]
SUMMARY = OrderedDict()


# --------------------------------------------------------------------------- data
def admin1(a3, field="name_en"):
    return {f["properties"][field] or f["properties"]["name"]: shape(f["geometry"]).buffer(0)
            for f in A1 if f["properties"]["adm0_a3"] == a3}


NG_ALIAS = {"Abuja": "Federal Capital Territory", "Nasarawa": "Nassarawa"}


def ng_state(meta_name):
    """Meta region / stratum label -> Natural Earth `name` for a Nigerian state."""
    n = meta_name.replace(" State", "").strip()
    return NG_ALIAS.get(n, n)


def places_near(geom_lonlat, a3, cc, min_pop=50000, dedupe_km=4.0):
    """Natural Earth 10m places, plus GeoNames places of min_pop+, inside a lon/lat
    area. Used only to orient the reader; never to name a targeting circle."""
    out = []
    for p in PP:
        if p["adm0_a3"] == a3 and geom_lonlat.contains(Point(p["longitude"], p["latitude"])):
            out.append(dict(name=p["name"], lat=p["latitude"], lon=p["longitude"], source="Natural Earth"))
    for x in sorted(geonames(cc), key=lambda x: -x["pop"]):
        if x["pop"] < min_pop or not geom_lonlat.contains(Point(x["lon"], x["lat"])):
            continue
        if all(hav(x["lat"], x["lon"], o["lat"], o["lon"]) > dedupe_km and x["name"] != o["name"] for o in out):
            out.append(dict(name=x["name"], lat=x["lat"], lon=x["lon"], source="GeoNames", pop=x["pop"]))
    return out


def which_unit(units, lon, lat):
    """Admin-1 unit containing the point; nearest one if the point falls in a gap of
    the 10m boundaries (reported, so a boundary artefact is never silent)."""
    p = Point(lon, lat)
    for k, g in units.items():
        if g.contains(p):
            return k
    k = min(units, key=lambda k: units[k].distance(p))
    print(f"  note: ({lat}, {lon}) is outside every admin-1 polygon; nearest is {k}")
    return k


def km(c):
    return c["radius"] * (MI if c["distance_unit"] == "mile" else 1.0)


def circle(lon, lat, r_km, n=96):
    az = [i * 360.0 / n for i in range(n)]
    lons, lats, _ = GEOD.fwd([lon] * n, [lat] * n, az, [r_km * 1000.0] * n)
    return Polygon(zip(lons, lats))


def hav(lat1, lon1, lat2, lon2):
    return GEOD.inv(lon1, lat1, lon2, lat2)[2] / 1000.0


_GN = {}
def geonames(cc):
    if cc not in _GN:
        rows = []
        for line in open(os.path.join(HERE, "geonames", cc + ".txt"), encoding="utf8"):
            r = line.rstrip("\n").split("\t")
            if r[6] != "P":
                continue
            rows.append(dict(id=int(r[0]), name=r[1], ascii=r[2], lat=float(r[4]), lon=float(r[5]),
                             code=r[7], a1=r[10], pop=int(r[14] or 0)))
        _GN[cc] = rows
    return _GN[cc]


def name_point(lat, lon, a3, cc, max_km=5.0):
    """Nearest of: a Natural Earth 10m place, or a GeoNames town of 20,000+, within
    max_km. Failing that, the nearest GeoNames place of 1,000+ within max_km. Else
    None, and the caller labels by admin unit. Never a guess."""
    ne = [(hav(lat, lon, p["latitude"], p["longitude"]), p["name"], "Natural Earth") for p in PP if p["adm0_a3"] == a3]
    gn = [(hav(lat, lon, x["lat"], x["lon"]), x["name"], "GeoNames", x["pop"]) for x in geonames(cc) if x["pop"] >= 1000]
    best = min(ne + [g[:3] for g in gn if g[3] >= 20000])
    if best[0] > max_km:
        best = min(g[:3] for g in gn)
    if best[0] <= max_km:
        return dict(name=best[1], source=best[2], km=round(best[0], 1))
    return None


def geocode(cc, name, a1code):
    """Forward-geocode a Meta city object (name only) inside one GeoNames admin-1.
    Administrative seats (PPLA*) first, then population."""
    c = [x for x in geonames(cc) if x["a1"] == a1code and (x["name"] == name or x["ascii"] == name)]
    if not c:
        raise SystemExit(f"geocode: no GeoNames place {name!r} in {cc}/{a1code}")
    c.sort(key=lambda x: (not x["code"].startswith("PPLA"), -x["pop"]))
    x = c[0]
    return dict(name=name, lat=x["lat"], lon=x["lon"], geonameid=x["id"], feature_code=x["code"],
                candidates=len(c))


def strata_conf(slug):
    sid = {s["slug"]: s["sid"] for s in json.load(open(os.path.join(SP, "studies.json")))}[slug]
    best = None
    with open(os.path.join(SP, "confs.tsv")) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r["study_id"] == sid and r["conf_type"] == "strata" and (best is None or r["created"] > best[0]):
                best = (r["created"], json.loads(r["conf"]))
    return best


def adopt(slug):
    sid = {s["slug"]: s["sid"] for s in json.load(open(os.path.join(SP, "studies.json")))}[slug]
    best = None
    with open(os.path.join(SP, "adopt.tsv")) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r["study_id"] == sid and (best is None or r["created"] > best[0]):
                best = (r["created"], json.loads(r["details"]))
    return best


def part(sid, key):
    for p in sid.split(","):
        k, _, v = p.partition(":")
        if k.lower() == key.lower():
            return v
    return None


def money(x):
    return f"${x:,.2f}"


# --------------------------------------------------------------------------- drawing
class Frame:
    """Azimuthal-equidistant projection fitted into a pixel box."""

    def __init__(self, lon0, lat0, fit, bx, pad=6, scale=None, anchor="center"):
        self.tr = Transformer.from_crs("EPSG:4326", f"+proj=aeqd +lat_0={lat0} +lon_0={lon0} +units=km",
                                       always_xy=True)
        g = transform(self.tr.transform, fit)
        minx, miny, maxx, maxy = g.bounds
        x, y, w, h = bx
        self.s = scale or min((w - 2 * pad) / (maxx - minx), (h - 2 * pad) / (maxy - miny))
        cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
        self.ox, self.oy = x + w / 2 - self.s * cx, y + h / 2 + self.s * cy
        self.box = box(x, y, x + w, y + h)
        self.bx = bx

    def _px(self, xs, ys):
        X, Y = self.tr.transform(xs, ys)
        if isinstance(X, float):
            return self.ox + self.s * X, self.oy - self.s * Y
        return [self.ox + self.s * a for a in X], [self.oy - self.s * b for b in Y]

    def xy(self, lon, lat):
        return self._px(lon, lat)

    def g(self, geom, clip=True, simplify=0.35):
        p = transform(self._px, geom)
        if clip:
            p = p.intersection(self.box)
        return p.simplify(simplify) if simplify else p


def d_of(geom):
    polys = [geom] if isinstance(geom, Polygon) else [q for q in getattr(geom, "geoms", []) if isinstance(q, Polygon)]
    out = []
    for p in polys:
        if p.is_empty:
            continue
        for ring in [p.exterior] + list(p.interiors):
            c = list(ring.coords)
            if len(c) < 3:
                continue
            out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in c[:-1]) + "Z")
    return "".join(out)


def path(geom, cls, extra=""):
    d = d_of(geom)
    return f'<path class="{cls}" d="{d}"{extra}/>' if d else ""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, cls, anchor="start", extra=""):
    if "gm-eye" in cls:
        s = s.upper()
    a = "" if anchor == "start" else f' text-anchor="{anchor}"'
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}"{a}{extra}>{esc(s)}</text>'


def cell(x, y, cls="gm-cell", size=4):
    return f'<rect class="{cls}" x="{x - size / 2:.1f}" y="{y - size / 2:.1f}" width="{size}" height="{size}"/>'


def scalebar(x, y, frame, km_len, label=None):
    L = frame.s * km_len
    return (f'<path class="gm-scale" d="M{x:.1f},{y:.1f}h{L:.1f}M{x:.1f},{y - 4:.1f}v4M{x + L:.1f},{y - 4:.1f}v4'
            f'M{x + L / 2:.1f},{y - 2.5:.1f}v2.5"/>'
            + text(x + L + 5, y + 3.5, label or f"{km_len:g} km", "gm-tiny"))


STYLE = """<style>
.gm-land{fill:var(--surface);stroke:none}
.gm-adm{fill:none;stroke:var(--rule-2);stroke-width:.6;stroke-linejoin:round}
.gm-adm-in{fill:none;stroke:var(--surface);stroke-width:.8;stroke-linejoin:round}
.gm-ctx{fill:var(--surface);stroke:var(--rule);stroke-width:.6;stroke-linejoin:round}
.gm-ctx0{fill:none;stroke:var(--rule-2);stroke-width:.6;stroke-linejoin:round}
.gm-outline{fill:none;stroke:var(--ink-3);stroke-width:.8;stroke-linejoin:round}
.gm-area{fill:var(--data-2);fill-opacity:.55}
.gm-circ{fill:var(--data);stroke:var(--surface);stroke-width:.5}
.gm-ring{fill:none;stroke:var(--surface);stroke-width:.6}
.gm-open{fill:var(--surface);fill-opacity:.9;stroke:var(--data);stroke-width:1.1}
.gm-excl{fill:var(--paper);stroke:var(--ink-3);stroke-width:.9;stroke-dasharray:3 2}
.gm-frame{fill:none;stroke:var(--ink-3);stroke-width:.8}
.gm-panel{fill:none;stroke:var(--rule);stroke-width:1}
.gm-lead{fill:none;stroke:var(--ink-3);stroke-width:.7}
.gm-scale{fill:none;stroke:var(--ink-2);stroke-width:1;shape-rendering:crispEdges}
.gm-cell{fill:var(--ink)}
.gm-bar{fill:var(--data)}
.gm-bar2{fill:var(--data-2)}
.gm-track{fill:var(--sunk)}
.gm-lab{font:400 12.5px "Source Sans 3","Helvetica Neue",Arial,sans-serif;fill:var(--ink)}
.gm-lab2{font:400 12px "Source Sans 3","Helvetica Neue",Arial,sans-serif;fill:var(--ink-2)}
.gm-halo{paint-order:stroke;stroke:var(--surface);stroke-width:3px;stroke-linejoin:round}
.gm-val{font:500 12.5px "IBM Plex Mono",ui-monospace,monospace;fill:var(--ink);font-variant-numeric:tabular-nums}
.gm-num{font:400 11.5px "IBM Plex Mono",ui-monospace,monospace;fill:var(--ink-2);font-variant-numeric:tabular-nums}
.gm-tiny{font:400 10.5px "IBM Plex Mono",ui-monospace,monospace;fill:var(--ink-2)}
.gm-eye{font:500 10px "IBM Plex Mono",ui-monospace,monospace;fill:var(--ink-2);letter-spacing:.13em;text-transform:uppercase}
.gm-note{font:400 12px "Source Sans 3","Helvetica Neue",Arial,sans-serif;fill:var(--ink-2)}
</style>"""


def svg(w, h, title, desc, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h:.0f}" role="img" '
            f'aria-labelledby="{label}-t {label}-d" data-claim="none">'
            f'<title id="{label}-t">{esc(title)}</title><desc id="{label}-d">{esc(desc)}</desc>'
            + STYLE + "".join(body) + "</svg>\n")


def write(name, s):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(s)
    print("wrote", name, f"{len(s) / 1024:.0f} KB")


def cost_rows(body, x, y, rows, width, max_cost=None, bar_h=12, row_h=34, label_w=170):
    """Rows of (label, sub, cost, n, spend, barclass). Bar length is cost on a shared scale."""
    mc = max_cost or max(r[2] for r in rows)
    bw = width - label_w - 70
    for i, (lab, sub, c, n, sp, cls) in enumerate(rows):
        yy = y + i * row_h
        body.append(text(x, yy + 10, lab, "gm-lab"))
        if sub:
            body.append(text(x, yy + 24, sub, "gm-tiny"))
        L = max(2.0, bw * c / mc)
        body.append(f'<rect class="{cls}" x="{x + label_w:.1f}" y="{yy:.1f}" width="{L:.1f}" height="{bar_h}"/>')
        body.append(text(x + label_w + L + 6, yy + 10.5, money(c), "gm-val"))
        body.append(text(x + label_w, yy + bar_h + 12, f"{n:,} respondents · {money(sp)} ad spend", "gm-tiny"))
    return y + len(rows) * row_h


# =========================================================================== BOLIVIA
BO_FRESH = {  # coordinator, 2026-09-24: fresh FACEBOOK_ADOPT reports, both studies pooled
    "source": "coordinator-supplied, fresh reports 2026-09-24 (targeting.json's channel report is stale)",
    "Urban": {"Men": (20.58, 213), "Women": (55.49, 153)},
    "Rural": {"Men": (104.23, 115), "Women": (135.13, 81)},
}


def bolivia():
    A = T["lac-healthy-diets-bolivia"]["strata"]
    B = T["lac-healthy-diets-bolivia-channel"]["strata"]
    key = lambda s: json.dumps(s["geo_locations"].get("custom_locations") or
                               (s.get("excluded_geo_locations") or {}).get("custom_locations"), sort_keys=True)
    assert len({key(s) for s in A + B}) == 1, "Bolivia studies do not share one circle set"
    circ = next(s for s in A if part(s["id"], "Location") == "Urban")["geo_locations"]["custom_locations"]
    depts = admin1("BOL")
    country = unary_union(list(depts.values()))
    polys = [circle(c["longitude"], c["latitude"], km(c)) for c in circ]
    urban = unary_union(polys)

    names = []
    for c in circ:
        nm = name_point(c["latitude"], c["longitude"], "BOL", "BO")
        dept = which_unit(depts, c["longitude"], c["latitude"])
        names.append(dict(lat=c["latitude"], lon=c["longitude"], radius_km=km(c), department=dept,
                          label=(nm or {}).get("name", dept), label_source=(nm or {}).get("source", "department"),
                          label_km=(nm or {}).get("km")))
    DISPLAY = {"Santa Cruz de la Sierra": "Santa Cruz"}
    for n in names:
        n["label"] = DISPLAY.get(n["label"], n["label"])

    W, H = 760, 700
    body = []
    main = Frame(-64.7, -16.7, country, (0, 26, 455, 540), pad=4)
    body.append(text(0, 12, "Bolivia · where the ads ran", "gm-eye"))
    body.append(path(main.g(country, simplify=0.3), "gm-area"))
    body.append(path(main.g(country, simplify=0.3), "gm-land", ' fill-opacity="0"'))
    for g in depts.values():
        body.append(path(main.g(g.boundary.buffer(0) if False else g, simplify=0.3), "gm-adm-in"))
    body.append(path(main.g(country, simplify=0.3), "gm-outline"))
    for p in polys:
        body.append(path(main.g(p, simplify=0.15), "gm-circ"))

    # insets
    insets = [("Cochabamba", -66.17, -17.37, (480, 26, 280, 190), ["Quillacollo", "Tiquipaya", "Cochabamba", "Sacaba"]),
              ("Santa Cruz", -63.215, -17.56, (480, 256, 280, 310), ["Montero", "Santa Cruz"])]
    INSET_SCALE = 2.9  # px per km, the same in both insets so the circles compare
    OFF = {  # label offsets, px, hand-placed for legibility
        "main": {"Cobija": (8, 4, "start"), "Trinidad": (8, 4, "start"), "La Paz": (8, -6, "start"),
                 "Oruro": (-8, 4, "end"), "Sucre": (8, 4, "start"), "Potosí": (-7, 12, "end"),
                 "Tarija": (8, 4, "start")},
        "Cochabamba": {"Quillacollo": (-40, 66, "middle"), "Tiquipaya": (-30, -58, "middle"),
                       "Cochabamba": (40, 70, "middle"), "Sacaba": (8, -40, "start")},
        "Santa Cruz": {"Montero": (22, 0, "start"), "Santa Cruz": (56, 0, "start")},
    }
    for title, lon0, lat0, bx, members in insets:
        pts = [p for p, n in zip(polys, names) if n["label"] in members]
        u = unary_union(pts)
        f = Frame(lon0, lat0, u, bx, scale=INSET_SCALE)
        x, y, w, h = bx
        body.append(text(x, y - 14, title + " · inset", "gm-eye"))
        body.append(f'<rect class="gm-land" x="{x}" y="{y}" width="{w}" height="{h}"/>')
        body.append(path(f.g(country, simplify=0.2), "gm-area"))
        for g in depts.values():
            body.append(path(f.g(g, simplify=0.2), "gm-adm-in"))
        body.append(path(f.g(u, simplify=0.15), "gm-circ"))
        for p in pts:
            body.append(path(f.g(p, simplify=0.15), "gm-ring"))
        for n in names:
            if n["label"] not in members:
                continue
            px, py = f.xy(n["lon"], n["lat"])
            dx, dy, an = OFF[title][n["label"]]
            body.append(cell(px, py, "gm-cell", 3))
            if abs(dy) > 14 or abs(dx) > 30:
                ex, ey = px + dx, py + dy + (-10 if dy > 0 else 4)
                body.append(f'<path class="gm-lead" d="M{px:.1f},{py:.1f}L{ex:.1f},{ey:.1f}"/>')
            body.append(text(px + dx, py + dy + 4 * (dy == 0), n["label"], "gm-lab gm-halo", an))
            body.append(text(px + dx, py + dy + 4 * (dy == 0) + 13, f'{n["radius_km"]:g} km radius', "gm-tiny gm-halo", an))
        body.append(f'<rect class="gm-panel" x="{x}" y="{y}" width="{w}" height="{h}"/>')
        body.append(scalebar(x + 10, y + 16, f, 10))
        # locator on the main map
        mb = main.g(u.buffer(0.12), clip=False, simplify=0).bounds
        body.append(f'<rect class="gm-frame" x="{mb[0]:.1f}" y="{mb[1]:.1f}" width="{mb[2] - mb[0]:.1f}" height="{mb[3] - mb[1]:.1f}"/>')
        if title == "Cochabamba":
            body.append(text(mb[2] + 5, (mb[1] + mb[3]) / 2 + 4, "Cochabamba", "gm-lab gm-halo"))
        else:
            body.append(text(mb[2] + 5, mb[3] + 2, "Santa Cruz", "gm-lab gm-halo"))
            body.append(text(mb[2] + 5, mb[3] + 15, "and Montero", "gm-lab2 gm-halo"))
    inset_members = {m for _, _, _, _, ms in insets for m in ms}
    for n in names:
        if n["label"] in inset_members:
            continue
        px, py = main.xy(n["lon"], n["lat"])
        dx, dy, an = OFF["main"][n["label"]]
        body.append(text(px + dx, py + dy, n["label"], "gm-lab gm-halo", an))
    body.append(scalebar(10, 26 + 540 - 12, main, 200))

    # cost rows, which double as the legend
    rows = []
    for loc, cls, sub in (("Urban", "gm-bar", "13 circles, 4–17 km"),
                          ("Rural", "gm-bar2", "rest of Bolivia")):
        sp = sum(v[0] for v in BO_FRESH[loc].values())
        n = sum(v[1] for v in BO_FRESH[loc].values())
        rows.append((loc, sub, sp / n, n, sp, cls))
    y0 = 600
    body.append(text(0, y0 - 14, "Ad cost per respondent · provisional — still fielding, as of 24 Sep 2026", "gm-eye"))
    yb = cost_rows(body, 0, y0, rows, 760, label_w=170, row_h=36)
    body.append(text(0, yb + 12, "Cost is recorded per stratum, not per city: all 13 circles share the urban figure. "
                                 "Both study arms and both genders pooled.", "gm-note"))
    H = yb + 22
    s = svg(W, H, "Bolivia: where the ads were targeted, and the ad cost per respondent",
            "Thirteen urban circles of 4 to 17 km radius, drawn to scale, in all nine departments; the rest of "
            f"Bolivia was targeted as rural. Urban {money(rows[0][2])} and rural {money(rows[1][2])} "
            "per respondent in advertising, provisional, as of 24 September 2026.", body, "bo")
    write("bolivia.svg", s)

    laea = Transformer.from_crs("EPSG:4326", "+proj=laea +lat_0=-16.7 +lon_0=-64.7 +units=km", always_xy=True).transform
    SUMMARY["bolivia"] = dict(
        studies=["lac-healthy-diets-bolivia", "lac-healthy-diets-bolivia-channel"],
        targeting=dict(
            urban="13 custom_locations circles (identical in all Urban strata of both studies), location_types home + frequently_in",
            rural="countries=[BO] with the same 13 circles excluded (excluded location_types: home only)",
            circles=len(circ), radius_km=[min(km(c) for c in circ), max(km(c) for c in circ)],
            departments_with_circles=sorted({n["department"] for n in names}),
            urban_area_km2=round(transform(laea, urban).area), country_area_km2=round(transform(laea, country).area),
            urban_share_of_country_pct=round(100 * transform(laea, urban).area / transform(laea, country).area, 3),
            circles_detail=names),
        cost=dict(source=BO_FRESH["source"], definition="sum(lifetime_spent)/sum(current_participants)",
                  by_group={f"{loc} {g}": dict(spend=v[0], respondents=v[1], cost=round(v[0] / v[1], 2))
                            for loc in ("Urban", "Rural") for g, v in BO_FRESH[loc].items()},
                  drawn={r[0]: dict(spend=round(r[4], 2), respondents=r[3], cost=round(r[2], 2)) for r in rows},
                  per_circle="NOT AVAILABLE: cost is recorded per stratum (urban/rural x gender), not per circle or department",
                  stale_report_in_targeting_json={s["id"]: s["report"] for s in B}),
        label_rule=name_point.__doc__.split("\n")[0] + " (see name_point)")


# =========================================================================== NIGERIA
COST_STEPS = [(1.0, ".22", "under $1"), (3.0, ".42", "$1–3"), (10.0, ".68", "$3–10"), (1e9, "1", "$10+")]


def cost_step(c):
    return next(s for s in COST_STEPS if c < s[0])


def pooled_by(strata_reports, key):
    """{geo: [spend, respondents]} over every stratum of every report."""
    acc = defaultdict(lambda: [0.0, 0])
    for rep in strata_reports:
        for sid, v in rep.items():
            acc[key(sid)][0] += v["lifetime_spent"]
            acc[key(sid)][1] += v["current_participants"]
    return acc


def geo_key(s):
    g = s["facebook_targeting"]["geo_locations"]
    return json.dumps({k: v for k, v in g.items() if k != "location_types"}, sort_keys=True)


def nigeria_2023():
    MAIN, SIB = "nigeria-final-hpv-august-23", "nigeria-hpv-config-8-1"
    c_main, strata = strata_conf(MAIN)
    c_sib, strata_sib = strata_conf(SIB)
    # one geography per state, identical across gender, and identical between the two runs
    geo = defaultdict(set)
    for s in strata + strata_sib:
        geo[part(s["id"], "State")].add(geo_key(s))
    assert all(len(v) == 1 for v in geo.values()), geo
    for st, v in geo.items():
        g = json.loads(next(iter(v)))
        assert list(g) == ["regions"] and len(g["regions"]) == 1, (st, g)
    r_main, r_sib = adopt(MAIN), adopt(SIB)
    sp_main = pooled_by([r_main[1]], lambda k: part(k, "State"))
    sp_sib = pooled_by([r_sib[1]], lambda k: part(k, "State"))
    rows = []
    for st in sp_main:
        spend = sp_main[st][0] + sp_sib[st][0]
        n = sp_main[st][1]
        rows.append(dict(state=st, spend=round(spend, 2), respondents=n, cost=round(spend / n, 2),
                         spend_final=round(sp_main[st][0], 2), spend_config_8_1=round(sp_sib[st][0], 2),
                         respondents_config_8_1_report=sp_sib[st][1]))
    rows.sort(key=lambda r: r["cost"])
    EXPECT = {"Lagos": (226.62, 433), "Rivers": (190.16, 260), "Bauchi": (321.23, 176), "Niger": (452.20, 139),
              "Sokoto": (709.94, 98), "Anambra": (1044.83, 74)}
    for r in rows:
        assert (round(r["spend"], 2), r["respondents"]) == EXPECT[r["state"]], (r, EXPECT[r["state"]])

    states = admin1("NGA", "name")
    country = unary_union(list(states.values()))
    W = 760
    body = [text(0, 12, "Nigeria, 2023 · six states, each targeted whole", "gm-eye")]
    f = Frame(8.1, 9.1, country, (0, 26, 470, 410), pad=4)
    byname = {ng_state(r["state"]): r for r in rows}
    for name, g in states.items():
        r = byname.get(name)
        if r:
            body.append(path(f.g(g, simplify=0.3), "gm-circ", f' fill-opacity="{cost_step(r["cost"])[1]}" style="stroke-width:.8"'))
        else:
            body.append(path(f.g(g, simplify=0.3), "gm-ctx"))
    body.append(path(f.g(country, simplify=0.3), "gm-outline"))
    LAB = {"Sokoto": (0, 0, "middle", None), "Niger": (0, 6, "middle", None), "Bauchi": (0, 0, "middle", None),
           "Lagos": (-30, 44, "middle", "lead"), "Rivers": (58, 22, "start", "lead"),
           "Anambra": (70, -10, "start", "lead")}
    for r in rows:
        g = states[ng_state(r["state"])]
        rp = g.representative_point() if r["state"] != "Niger" else g.centroid
        px, py = f.xy(rp.x, rp.y)
        dx, dy, an, lead = LAB[r["state"]]
        tx, ty = px + dx, py + dy
        if lead:
            body.append(f'<path class="gm-lead" d="M{px:.1f},{py:.1f}L{tx:.1f},{ty - 12:.1f}"/>' if dy > 0 else
                        f'<path class="gm-lead" d="M{px:.1f},{py:.1f}L{tx - 3:.1f},{ty - 4:.1f}"/>')
        body.append(text(tx, ty - 2, r["state"], "gm-lab gm-halo", an))
        body.append(text(tx, ty + 12, money(r["cost"]), "gm-val gm-halo", an))
    body.append(scalebar(10, 26 + 410 - 10, f, 200))

    # ranked list on the right: the table behind the map, and the legend
    x0, y0 = 500, 40
    body.append(text(x0, 12, "Ad cost per respondent", "gm-eye"))
    bw = 760 - (x0 + 70) - 62
    mx = max(r["cost"] for r in rows)
    for i, r in enumerate(rows):
        y = y0 + i * 50
        body.append(text(x0, y + 10, r["state"], "gm-lab"))
        L = max(2.0, bw * r["cost"] / mx)
        op = cost_step(r["cost"])[1]
        body.append(f'<rect class="gm-bar" x="{x0 + 70}" y="{y}" width="{L:.1f}" height="12" fill-opacity="{op}"/>')
        body.append(text(x0 + 70 + L + 6, y + 10.5, money(r["cost"]), "gm-val"))
        body.append(text(x0, y + 27, f'{r["respondents"]:,} respondents · {money(r["spend"])}', "gm-tiny"))
    yl = y0 + len(rows) * 50 + 6
    body.append(text(x0, yl, "Fill, by cost per respondent", "gm-tiny"))
    xx = x0
    for _, op, lab in COST_STEPS:
        body.append(f'<rect class="gm-bar" x="{xx}" y="{yl + 8}" width="12" height="10" fill-opacity="{op}"/>')
        body.append(text(xx + 16, yl + 17, lab, "gm-tiny"))
        xx += 16 + 6.3 * len(lab) + 12
    yn = 26 + 410 + 20
    others = len(states) - len(rows) - 1
    for i, line in enumerate([
            "12 Aug – 12 Sep 2023. Each state was targeted whole (a Meta region), so the coloured area is the real",
            f"targeting area. Two concurrent ad runs for one survey, and both genders, pooled. The other {others} states",
            "and the Federal Capital Territory were not targeted."]):
        body.append(text(0, yn + 16 * i, line, "gm-note"))
    H = yn + 40
    s = svg(W, H, "Nigeria, 2023: advertising cost per respondent in six whole-state targets",
            "Six states targeted whole, August to September 2023. Ad cost per respondent: " +
            ", ".join(f'{r["state"]} {money(r["cost"])}' for r in rows) + ".", body, "ng23")
    write("nigeria-2023-states.svg", s)
    SUMMARY["nigeria_2023_states"] = dict(
        studies=[MAIN, SIB], strata_conf_created={MAIN: c_main, SIB: c_sib},
        report_created={MAIN: r_main[0], SIB: r_sib[0]}, fielded="2023-08-12..2023-09-12 (coordinator)",
        targeting="regions: one whole state per stratum; identical in both studies and across gender",
        rule="spend = both studies' lifetime_spent; respondents = nigeria-final-hpv-august-23's report (the two runs share one survey, so the final report counts the shared pool)",
        states=rows, fill_steps=[dict(upper=s[0] if s[0] < 1e8 else None, opacity=s[1], label=s[2]) for s in COST_STEPS])


def nigeria_2024():
    A, B = "short-a-hpv-nigeria", "short-b-hpv-nigeria"
    ca, sa = strata_conf(A)
    cb, sb = strata_conf(B)
    circ = {}  # (study, state) -> list of circles
    for slug, strata in ((A, sa), (B, sb)):
        per = defaultdict(set)
        for s in strata:
            g = s["facebook_targeting"]["geo_locations"]
            assert set(g) <= {"custom_locations", "location_types"}, g.keys()
            per[part(s["id"], "State")].add(json.dumps(g["custom_locations"], sort_keys=True))
        for st, v in per.items():
            assert len(v) == 1, (slug, st)
            circ[(slug, st)] = json.loads(next(iter(v)))
    ra, rb = adopt(A), adopt(B)
    pa = pooled_by([ra[1]], lambda k: part(k, "State"))
    pb = pooled_by([rb[1]], lambda k: part(k, "State"))
    EXPECT = {"Abuja": (992.50, 812), "Adamawa": (3488.06, 68), "Nasarawa": (5536.94, 129)}

    states = admin1("NGA", "name")
    laea = Transformer.from_crs("EPSG:4326", "+proj=laea +lat_0=9 +lon_0=8 +units=km", always_xy=True).transform
    facts = OrderedDict()
    polys = {}
    for st in ("Abuja", "Adamawa", "Nasarawa"):
        spend = pa[st][0] + pb[st][0]
        n = pa[st][1]
        assert (round(spend, 2), n) == EXPECT[st], (st, spend, n)
        ca_, cb_ = circ[(A, st)], circ[(B, st)]
        pA = [circle(c["longitude"], c["latitude"], km(c)) for c in ca_]
        pB = [circle(c["longitude"], c["latitude"], km(c)) for c in cb_]
        polys[st] = (pA, pB)
        u = unary_union(pA + pB)
        sg = states[ng_state(st)]
        outside = [dict(lat=c["latitude"], lon=c["longitude"], centre_in=which_unit(states, c["longitude"], c["latitude"]))
                   for c in ca_ + cb_ if not sg.contains(Point(c["longitude"], c["latitude"]))]
        radii = sorted({round(km(c), 3) for c in ca_ + cb_})
        facts[st] = dict(
            ne_state=ng_state(st), circles_short_a=len(ca_), circles_short_b=len(cb_),
            circles_shared=len({(c["latitude"], c["longitude"]) for c in ca_} & {(c["latitude"], c["longitude"]) for c in cb_}),
            radius_km=radii, radius_as_stored=sorted({(c["radius"], c["distance_unit"]) for c in ca_ + cb_}),
            union_area_km2=round(transform(laea, u).area, 1),
            union_area_inside_state_km2=round(transform(laea, u.intersection(sg)).area, 1),
            state_area_km2=round(transform(laea, sg).area),
            share_of_state_pct=round(100 * transform(laea, u.intersection(sg)).area / transform(laea, sg).area, 2),
            circle_centres_outside_state=outside,
            spend=round(spend, 2), spend_short_a=round(pa[st][0], 2), spend_short_b=round(pb[st][0], 2),
            respondents=n, respondents_short_b_report=pb[st][1], cost=round(spend / n, 2))

    W = 760
    body = [text(0, 12, "Nigeria, October 2024 · the “states” were clusters of small circles", "gm-eye")]
    # ---- panel 1: FCT + Nasarawa
    fit = unary_union([states["Federal Capital Territory"], states["Nassarawa"]])
    p1 = (0, 26, 760, 370)
    f1 = Frame(7.9, 8.55, fit, p1, pad=6)
    ctx_area = box(*fit.buffer(0.6).bounds)
    for name, g in states.items():
        if g.intersects(ctx_area):
            cls = "gm-land" if name in ("Federal Capital Territory", "Nassarawa") else "gm-ctx0"
            body.append(path(f1.g(g, simplify=0.3), cls))
    for name in ("Federal Capital Territory", "Nassarawa"):
        body.append(path(f1.g(states[name], simplify=0.3), "gm-outline"))
    for st in ("Abuja", "Nasarawa"):
        pA, pB = polys[st]
        body.append(path(f1.g(unary_union(pA), simplify=0.15), "gm-circ"))
        for p in pA:
            body.append(path(f1.g(p, simplify=0.15), "gm-ring"))
        for p in pB:
            body.append(path(f1.g(p, simplify=0.15), "gm-open"))
    view1 = Polygon([(x, y) for x, y in [(fit.bounds[0] - 1, fit.bounds[1] - 1), (fit.bounds[2] + 1, fit.bounds[1] - 1),
                                           (fit.bounds[2] + 1, fit.bounds[3] + 1), (fit.bounds[0] - 1, fit.bounds[3] + 1)]])
    towns1 = [t for t in places_near(fit.buffer(0.05), "NGA", "NG", min_pop=60000)]
    TOFF = {"Abuja": (-8, -8, "end"), "Lafia": (8, 4, "start"), "Keffi": (8, -6, "start"), "Suleja": (-8, -4, "end"),
            "Nasarawa": (8, 4, "start"), "Akwanga": (8, 4, "start"), "Kuje": (-8, 12, "end"),
            "Gwagwalada": (-8, 12, "end"), "Karu": (6, -8, "start"), "Mararaba": (6, -8, "start"),
            "Nyanya": (6, 14, "start"), "Kubwa": (-6, -8, "end"), "Doma": (8, 4, "start")}
    shown1 = []
    for t in towns1:
        px, py = f1.xy(t["lon"], t["lat"])
        if not f1.box.contains(Point(px, py)):
            continue
        dx, dy, an = TOFF.get(t["name"], (7, 4, "start"))
        body.append(cell(px, py, "gm-cell", 4))
        body.append(text(px + dx, py + dy, t["name"], "gm-lab2 gm-halo", an))
        shown1.append(t)
    for name, lab, (lx, ly) in (("Federal Capital Territory", "FEDERAL CAPITAL TERRITORY", (7.05, 8.55)),
                                ("Nassarawa", "NASARAWA STATE", (8.95, 8.2))):
        px, py = f1.xy(lx, ly)
        body.append(text(px, py, lab, "gm-eye gm-halo", "middle"))
    body.append(scalebar(p1[0] + 10, p1[1] + p1[3] - 10, f1, 20))
    body.append(f'<rect class="gm-panel" x="{p1[0]}" y="{p1[1]}" width="{p1[2]}" height="{p1[3]}"/>')

    # ---- panel 2: Adamawa whole state, and panel 3: the Yola circles
    ad = states["Adamawa"]
    p2 = (0, 426, 250, 330)
    f2 = Frame(12.4, 9.3, ad, p2, pad=10)
    for name, g in states.items():
        if g.intersects(box(*ad.buffer(0.3).bounds)):
            body.append(path(f2.g(g, simplify=0.3), "gm-land" if name == "Adamawa" else "gm-ctx0"))
    body.append(path(f2.g(ad, simplify=0.3), "gm-outline"))
    pA, pB = polys["Adamawa"]
    uAd = unary_union(pA + pB)
    body.append(path(f2.g(uAd, simplify=0.15), "gm-circ"))
    mb = f2.g(uAd.buffer(0.05), clip=False, simplify=0).bounds
    body.append(f'<rect class="gm-frame" x="{mb[0]:.1f}" y="{mb[1]:.1f}" width="{mb[2] - mb[0]:.1f}" height="{mb[3] - mb[1]:.1f}"/>')
    body.append(text(p2[0] + 8, p2[1] + 18, "ADAMAWA STATE", "gm-eye"))
    body.append(scalebar(p2[0] + 10, p2[1] + p2[3] - 10, f2, 50))
    body.append(f'<rect class="gm-panel" x="{p2[0]}" y="{p2[1]}" width="{p2[2]}" height="{p2[3]}"/>')
    p3 = (266, 426, 494, 330)
    f3 = Frame(12.445, 9.28, uAd, p3, scale=f1.s * 4)
    body.append(f'<rect class="gm-land" x="{p3[0]}" y="{p3[1]}" width="{p3[2]}" height="{p3[3]}"/>')
    body.append(path(f3.g(unary_union(pA), simplify=0.15), "gm-circ"))
    for p in pA:
        body.append(path(f3.g(p, simplify=0.15), "gm-ring"))
    for p in pB:
        body.append(path(f3.g(p, simplify=0.15), "gm-open"))
    lonlat3 = Polygon([(12.25, 9.12), (12.65, 9.12), (12.65, 9.44), (12.25, 9.44)])
    for t in places_near(lonlat3, "NGA", "NG", min_pop=60000):
        px, py = f3.xy(t["lon"], t["lat"])
        if f3.box.contains(Point(px, py)):
            body.append(cell(px, py, "gm-cell", 4))
            body.append(text(px + 8, py + 4, t["name"], "gm-lab2 gm-halo"))
    body.append(text(p3[0] + 8, p3[1] + 18, "ADAMAWA · YOLA–JIMETA, ENLARGED", "gm-eye"))
    body.append(scalebar(p3[0] + 10, p3[1] + p3[3] - 10, f3, 5))
    body.append(f'<rect class="gm-panel" x="{p3[0]}" y="{p3[1]}" width="{p3[2]}" height="{p3[3]}"/>')

    # ---- key and cost rows
    y = 426 + 330 + 26
    body.append(f'<rect class="gm-bar" x="0" y="{y - 9}" width="12" height="12"/>')
    body.append(text(18, y + 1, "circles of ad run A", "gm-note"))
    body.append(f'<circle class="gm-open" cx="{150 + 6}" cy="{y - 3}" r="6"/>')
    body.append(text(168, y + 1, "circles of ad run B (same survey, same days)", "gm-note"))
    body.append(f'<rect class="gm-cell" x="{452}" y="{y - 5}" width="4" height="4"/>')
    body.append(text(462, y + 1, "town, for orientation", "gm-note"))
    y += 34
    body.append(text(0, y - 10, "Ad cost per respondent, both runs pooled", "gm-eye"))
    rows = []
    for st, lab in (("Abuja", "Abuja (FCT)"), ("Nasarawa", "Nasarawa"), ("Adamawa", "Adamawa")):
        fc = facts[st]
        r = fc["radius_km"][0]
        sub = f'{fc["circles_short_a"] + fc["circles_short_b"]} circles of {r:.1f} km · {fc["share_of_state_pct"]:.1f}% of the state'
        rows.append((lab, sub, fc["cost"], fc["respondents"], fc["spend"], "gm-bar"))
    yb = cost_rows(body, 0, y, rows, 760, label_w=300, row_h=38)
    body.append(text(0, yb + 10, "12–25 Oct 2024. Radii 4.02 km and 2.01 km (2.5 and 1.25 miles). Cost is recorded per state, "
                                 "not per circle. Both genders pooled.", "gm-note"))
    H = yb + 20
    s = svg(W, H, "Nigeria, October 2024: the Abuja, Nasarawa and Adamawa targets were clusters of small circles",
            "Strata labelled by state were targeted as small circles: " +
            "; ".join(f'{st}, {facts[st]["circles_short_a"] + facts[st]["circles_short_b"]} circles covering '
                      f'{facts[st]["share_of_state_pct"]:.1f}% of the state, {money(facts[st]["cost"])} per respondent'
                      for st in facts) + ".", body, "ng24")
    write("nigeria-2024-circles.svg", s)
    SUMMARY["nigeria_2024_circles"] = dict(
        studies=[A, B], strata_conf_created={A: ca, B: cb}, report_created={A: ra[0], B: rb[0]},
        fielded="2024-10-12..2024-10-25 (coordinator)",
        rule="spend = both runs' lifetime_spent; respondents = short-a-hpv-nigeria's report (one survey; short-b's report counts the same pool, differing by at most 1)",
        area_method="geodesic circles, union, intersected with Natural Earth 10m state polygon, area in LAEA (lat_0 9, lon_0 8)",
        states=facts, towns_shown_panel1=[t["name"] + f' ({t["source"]})' for t in shown1])


# =========================================================================== INDONESIA
ID_GN_A1 = {"West Java": "30", "Central Java": "07", "South Kalimantan": "12"}


def indonesia():
    slug = "sigap-media-first-evaluation"
    strata = T[slug]["strata"]
    groups = OrderedDict()
    for s in strata:
        loc = part(s["id"], "Location")
        prov, _, kind = loc.rpartition(" ")
        g = groups.setdefault(loc, dict(province=prov, kind=kind, geo=set(), spend=0.0, n=0, strata=0))
        g["geo"].add(json.dumps([s["geo_locations"], s.get("excluded_geo_locations")], sort_keys=True))
        g["spend"] += s["report"]["lifetime_spent"]
        g["n"] += s["report"]["current_participants"]
        g["strata"] += 1
    assert all(len(g["geo"]) == 1 for g in groups.values())
    provs = admin1("IDN")
    laea = Transformer.from_crs("EPSG:4326", "+proj=laea +lat_0=-6.5 +lon_0=110 +units=km", always_xy=True).transform
    facts = OrderedDict()
    geo = {}
    for prov in ("West Java", "Central Java", "South Kalimantan"):
        u_inc, u_exc = json.loads(next(iter(groups[prov + " Urban"]["geo"])))
        r_inc, r_exc = json.loads(next(iter(groups[prov + " Rural"]["geo"])))
        assert [x["name"] for x in r_inc["regions"]] == [prov]
        circ = u_inc["custom_locations"]
        r_circ = (r_exc or {}).get("custom_locations", [])
        # the rural exclusion repeats the urban circles (South Kalimantan's copy is rounded to 6 dp)
        rk = lambda cs: sorted((round(c["latitude"], 4), round(c["longitude"], 4), km(c)) for c in cs)
        assert rk(circ) == rk(r_circ), prov
        cities_u = (u_exc or {}).get("cities", [])
        cities_r = (r_exc or {}).get("cities", [])
        assert json.dumps(cities_u, sort_keys=True) == json.dumps(cities_r, sort_keys=True), prov
        excl = []
        for c in cities_u:
            gc = geocode("ID", c["name"], ID_GN_A1[prov])
            gc.update(meta_key=c["key"], radius_km=km(c), region=c["region"])
            excl.append(gc)
        pg = provs[prov]
        polys = [circle(c["longitude"], c["latitude"], km(c)) for c in circ]
        urb = unary_union(polys)
        exz = unary_union([circle(e["lon"], e["lat"], e["radius_km"]) for e in excl]) if excl else Polygon()
        urban_eff = urb.difference(exz)
        rural_eff = pg.difference(urb).difference(exz)
        centres_outside = sum(1 for c in circ if not pg.contains(Point(c["longitude"], c["latitude"])))
        in_excl = sum(1 for p in polys if p.intersects(exz)) if excl else 0
        A = lambda g: round(transform(laea, g).area, 1)
        geo[prov] = dict(pg=pg, polys=polys, urb=urb, exz=exz, excl=excl, rural=rural_eff, urban=urban_eff)
        facts[prov] = dict(
            urban_definition=f"{len(circ)} custom_locations circles" + (", minus the excluded city radii" if excl else ""),
            rural_definition=f"region '{prov}' minus the same {len(circ)} circles" + (" and minus the excluded city radii" if excl else ""),
            circles=len(circ), radius_km=[min(km(c) for c in circ), max(km(c) for c in circ)],
            circle_centres_outside_province=centres_outside,
            circles_touching_excluded_zones=in_excl,
            excluded_cities=excl,
            province_area_km2=A(pg), urban_area_km2=A(urban_eff), rural_area_km2=A(rural_eff),
            excluded_area_km2=A(exz.intersection(pg)) if excl else 0,
            urban_share_pct=round(100 * transform(laea, urban_eff).area / transform(laea, pg).area, 2),
            excluded_share_pct=round(100 * transform(laea, exz.intersection(pg)).area / transform(laea, pg).area, 2) if excl else 0)
        for kind in ("Urban", "Rural"):
            g = groups[f"{prov} {kind}"]
            facts[prov][kind.lower()] = dict(strata=g["strata"], spend=round(g["spend"], 2), respondents=g["n"],
                                             cost=round(g["spend"] / g["n"], 2))

    W = 760
    body = [text(0, 12, "Indonesia, 2025 · urban circles and the rural remainder", "gm-eye")]
    java = unary_union([provs["West Java"], provs["Central Java"]])
    # Karimunjawa and other small islands would stretch the frame; fit to Java's main body
    fitj = max(java.geoms, key=lambda g: g.area) if hasattr(java, "geoms") else java
    pj = (0, 26, 760, 330)
    fj = Frame(108.6, -7.0, fitj, pj, pad=8)
    SC = fj.s
    ctxbox = box(104.5, -9.2, 112.8, -5.3)
    for name, g in provs.items():
        if g.intersects(ctxbox) and name not in ("West Java", "Central Java"):
            body.append(path(fj.g(g, simplify=0.3), "gm-ctx0"))
    labels_j = {"West Java": (107.55, -6.62), "Central Java": (110.2, -6.93)}
    for prov in ("West Java", "Central Java"):
        G = geo[prov]
        body.append(path(fj.g(G["pg"], simplify=0.3), "gm-land"))
        body.append(path(fj.g(G["rural"], simplify=0.3), "gm-area"))
        body.append(path(fj.g(G["urban"], simplify=0.15), "gm-circ"))
        body.append(path(fj.g(G["exz"].intersection(G["pg"]), simplify=0.3), "gm-excl"))
        body.append(path(fj.g(G["pg"], simplify=0.3), "gm-outline"))
    EXOFF = {"Sukabumi": (0, 50, "middle"), "Banjar": (0, 52, "middle"), "Brebes": (0, 52, "middle")}
    for prov in ("West Java", "Central Java"):
        for e in {e["name"]: e for e in geo[prov]["excl"]}.values():
            px, py = fj.xy(e["lon"], e["lat"])
            dx, dy, an = EXOFF[e["name"]]
            body.append(text(px + dx, py + dy, f'{e["name"]} · excluded', "gm-lab2 gm-halo", an))
    for prov, (lx, ly) in labels_j.items():
        px, py = fj.xy(lx, ly)
    body.append(text(fj.xy(107.1, -7.95)[0], fj.xy(107.1, -7.95)[1], "WEST JAVA", "gm-eye gm-halo", "middle"))
    body.append(text(fj.xy(109.55, -8.0)[0], fj.xy(109.55, -8.0)[1], "CENTRAL JAVA", "gm-eye gm-halo", "middle"))
    TOWN = {"Bandung": (-7, -7, "end"), "Semarang": (0, -9, "middle"), "Bogor": (-7, -6, "end"),
            "Cirebon": (0, -9, "middle"), "Tegal": (-4, -9, "middle"), "Surakarta": (7, 4, "start"),
            "Purwokerto": (0, 14, "middle"), "Tasikmalaya": (7, 12, "start"), "Jakarta": (0, -9, "middle"),
            "Pekalongan": (0, -9, "middle"), "Magelang": (-7, 4, "end")}
    for p in PP:
        if p["adm0_a3"] == "IDN" and p["name"] in TOWN and fj.box.contains(Point(*fj.xy(p["longitude"], p["latitude"]))):
            px, py = fj.xy(p["longitude"], p["latitude"])
            dx, dy, an = TOWN[p["name"]]
            body.append(cell(px, py, "gm-cell", 4))
            body.append(text(px + dx, py + dy, p["name"], "gm-lab2 gm-halo", an))
    body.append(scalebar(pj[0] + 10, pj[1] + pj[3] - 10, fj, 50))
    body.append(f'<rect class="gm-panel" x="{pj[0]}" y="{pj[1]}" width="{pj[2]}" height="{pj[3]}"/>')

    # South Kalimantan at the same scale as Java
    G = geo["South Kalimantan"]
    pk = (0, 26 + 330 + 30, 330, 420)
    fk = Frame(115.4, -2.9, G["pg"], pk, scale=SC)
    for name, g in provs.items():
        if g.intersects(box(113.5, -4.8, 117.5, -1.0)) and name != "South Kalimantan":
            body.append(path(fk.g(g, simplify=0.3), "gm-ctx0"))
    body.append(path(fk.g(G["pg"], simplify=0.3), "gm-land"))
    body.append(path(fk.g(G["rural"], simplify=0.3), "gm-area"))
    body.append(path(fk.g(G["urban"], simplify=0.15), "gm-circ"))
    body.append(path(fk.g(G["pg"], simplify=0.3), "gm-outline"))
    # five circles only, so each is named (nearest place within 5 km, never a guess)
    SKOFF = [(8, 4, "start"), (8, 4, "start"), (8, -8, "start"), (8, -2, "start"), (8, 10, "start")]
    sk_names = []
    for (c, (dx, dy, an)) in zip(T[slug]["strata"][16]["geo_locations"]["custom_locations"], SKOFF):
        nm = name_point(c["latitude"], c["longitude"], "IDN", "ID")
        lab = {"Bandjarmasin": "Banjarmasin"}.get((nm or {}).get("name"), (nm or {}).get("name"))
        sk_names.append(dict(lat=c["latitude"], lon=c["longitude"], radius_km=km(c), label=lab,
                             source=(nm or {}).get("source"), km=(nm or {}).get("km")))
        if lab:
            px, py = fk.xy(c["longitude"], c["latitude"])
            body.append(text(px + dx, py + dy, lab, "gm-lab2 gm-halo", an))
    facts["South Kalimantan"]["circle_names"] = sk_names
    body.append(text(pk[0] + 8, pk[1] + 18, "SOUTH KALIMANTAN", "gm-eye"))
    body.append(text(pk[0] + 8, pk[1] + 32, "same scale as Java", "gm-tiny"))
    body.append(scalebar(pk[0] + 10, pk[1] + pk[3] - 10, fk, 50))
    body.append(f'<rect class="gm-panel" x="{pk[0]}" y="{pk[1]}" width="{pk[2]}" height="{pk[3]}"/>')

    # cost table
    x0, y0 = 352, pk[1] + 14
    body.append(text(x0, y0 - 2, "Ad cost per respondent", "gm-eye"))
    mx = max(facts[p][k]["cost"] for p in facts for k in ("urban", "rural"))
    bw = 760 - (x0 + 120) - 60
    y = y0 + 18
    for prov in facts:
        body.append(text(x0, y + 10, prov, "gm-lab"))
        y += 18
        for k, cls, lab in (("urban", "gm-bar", "Urban"), ("rural", "gm-bar2", "Rural")):
            fc = facts[prov][k]
            L = max(2.0, bw * fc["cost"] / mx)
            body.append(text(x0 + 10, y + 10, lab, "gm-lab2"))
            body.append(f'<rect class="{cls}" x="{x0 + 120}" y="{y}" width="{L:.1f}" height="12"/>')
            body.append(text(x0 + 120 + L + 6, y + 10.5, money(fc["cost"]), "gm-val"))
            body.append(text(x0 + 120, y + 24, f'{fc["respondents"]:,} respondents · {money(fc["spend"])}', "gm-tiny"))
            y += 34
        y += 6
    yk = max(y, pk[1] + pk[3]) + 22
    body.append(f'<rect class="gm-bar" x="0" y="{yk - 9}" width="12" height="12"/>')
    body.append(text(18, yk + 1, "urban: circles of 2–11 km", "gm-note"))
    body.append(f'<rect class="gm-bar2" x="190" y="{yk - 9}" width="12" height="12"/>')
    body.append(text(208, yk + 1, "rural: rest of the province", "gm-note"))
    body.append(f'<rect class="gm-excl" x="390" y="{yk - 9}" width="12" height="12"/>')
    body.append(text(408, yk + 1, "40 km around a city, excluded from both", "gm-note"))
    body.append(text(0, yk + 22, "Report of 9 May 2025. Cost is recorded per stratum, not per circle; gender and age pooled. "
                                 "Exclusion centres placed from GeoNames.", "gm-note"))
    H = yk + 32
    s = svg(W, H, "Indonesia: urban circles and rural remainder in three provinces, with ad cost per respondent",
            "; ".join(f'{p}: {facts[p]["circles"]} urban circles, urban {money(facts[p]["urban"]["cost"])}, '
                      f'rural {money(facts[p]["rural"]["cost"])} per respondent' for p in facts) + ".", body, "id")
    write("indonesia.svg", s)
    SUMMARY["indonesia"] = dict(study=slug, report_created=T[slug]["adopt_report_created"],
                                provinces=facts,
                                note="Brebes appears twice among the excluded cities, as two Meta city keys with one name; one GeoNames point serves both.")


# =========================================================================== BAUCHI
def nigeria_bauchi():
    slug = "bauchi-state-hpv-pilot"
    strata = T[slug]["strata"]
    states = admin1("NGA", "name")
    bauchi = states["Bauchi"]
    gn_kirfi = geocode("NG", "Kirfi", "46")
    rows = []
    for s_ in strata:
        g = s_["geo_locations"]
        lga = part(s_["id"], "LGA")
        if "cities" in g:
            c = g["cities"][0]
            gc = geocode("NG", c["name"], "46")
            kind, lat, lon, r = "Meta city + radius (point from GeoNames)", gc["lat"], gc["lon"], km(c)
            extra = dict(meta_city=c["name"], meta_key=c["key"], geonames=gc)
        elif "custom_locations" in g:
            c = g["custom_locations"][0]
            kind, lat, lon, r, extra = "custom circle", c["latitude"], c["longitude"], km(c), {}
        else:
            c = g["places"][0]
            kind, lat, lon, r = "Meta place + radius", c["latitude"], c["longitude"], km(c)
            extra = dict(meta_place=c["name"], meta_key=c["key"],
                         km_from_geonames_kirfi_town=round(hav(lat, lon, gn_kirfi["lat"], gn_kirfi["lon"]), 1),
                         nearest_place=name_point(lat, lon, "NGA", "NG"))
        rep = s_["report"]
        rows.append(dict(lga=lga, kind=kind, lat=lat, lon=lon, radius_km=round(r, 2),
                         radius_as_set=f'{c["radius"]} {c["distance_unit"]}', spend=round(rep["lifetime_spent"], 2),
                         respondents=rep["current_participants"],
                         cost=round(rep["lifetime_spent"] / rep["current_participants"], 2), **extra))
    rows.sort(key=lambda r: r["cost"])
    W = 760
    body = [text(0, 12, "Bauchi State, April 2026 · six local-government strata", "gm-eye")]
    pb = (0, 26, 400, 470)
    f = Frame(9.8, 10.8, bauchi, pb, pad=10)
    for name, g in states.items():
        if g.intersects(box(*bauchi.buffer(0.4).bounds)):
            body.append(path(f.g(g, simplify=0.3), "gm-land" if name == "Bauchi" else "gm-ctx0"))
    body.append(path(f.g(bauchi, simplify=0.3), "gm-outline"))
    for r in rows:
        body.append(path(f.g(circle(r["lon"], r["lat"], r["radius_km"]), simplify=0.15), "gm-circ",
                         ' fill-opacity=".85"'))
    for p in PP:
        if p["adm0_a3"] == "NGA" and p["name"] in ("Bauchi", "Azare"):
            px, py = f.xy(p["longitude"], p["latitude"])
            body.append(cell(px, py, "gm-cell", 4))
            body.append(text(px + 7, py + 4, p["name"], "gm-lab2 gm-halo", "start" if p["name"] == "Azare" else "end") if p["name"] == "Azare" else text(px - 7, py - 6, p["name"], "gm-lab2 gm-halo", "end"))
    OFF = {"Gamawa": (-36, 0, "end"), "Dambam": (0, 44, "middle"), "Jama’are": (-28, 4, "end"),
           "Jama'are": (-28, 4, "end"), "Giade": (0, 36, "middle"), "Toro": (-28, 4, "end"),
           "Kirfi": (10, 16, "start")}
    for r in rows:
        px, py = f.xy(r["lon"], r["lat"])
        dx, dy, an = OFF[r["lga"]]
        body.append(text(px + dx, py + dy, r["lga"], "gm-lab gm-halo", an))
        body.append(text(px + dx, py + dy + 13, money(r["cost"]), "gm-val gm-halo", an))
    body.append(text(pb[0] + 8, pb[1] + 18, "BAUCHI STATE", "gm-eye"))
    body.append(scalebar(pb[0] + 10, pb[1] + pb[3] - 10, f, 50))
    body.append(f'<rect class="gm-panel" x="{pb[0]}" y="{pb[1]}" width="{pb[2]}" height="{pb[3]}"/>')
    x0, y0 = 424, 40
    body.append(text(x0, 12, "Ad cost per respondent", "gm-eye"))
    mx = max(r["cost"] for r in rows)
    bw = 760 - (x0 + 74) - 60
    for i, r in enumerate(rows):
        y = y0 + i * 56
        body.append(text(x0, y + 10, r["lga"], "gm-lab"))
        L = max(2.0, bw * r["cost"] / mx)
        body.append(f'<rect class="gm-bar" x="{x0 + 74}" y="{y}" width="{L:.1f}" height="12"/>')
        body.append(text(x0 + 74 + L + 6, y + 10.5, money(r["cost"]), "gm-val"))
        body.append(text(x0, y + 26, f'{r["respondents"]:,} respondents · {money(r["spend"])}', "gm-tiny"))
        where = "a point near Bauchi city" if "place" in r["kind"] else ("a set point" if r["kind"] == "custom circle" else "the town")
        body.append(text(x0, y + 39, f'{r["radius_as_set"].replace("mile", "mi")} ({r["radius_km"]:.1f} km) around {where}', "gm-tiny"))
    yn = pb[1] + pb[3] + 20
    kd = next(r for r in rows if r["lga"] == "Kirfi")["km_from_geonames_kirfi_town"]
    for i, line in enumerate([
            "6–17 Apr 2026. The strata are named for local government areas, but each was targeted as a radius",
            "around one point, not the LGA boundary. Town points for Gamawa, Dambam, Jama’are and Giade are placed",
            f"from GeoNames (Meta stores the name, not the point). Kirfi’s target point is near Bauchi city, {kd:.0f} km from Kirfi."]):
        body.append(text(0, yn + 16 * i, line, "gm-note"))
    H = yn + 40
    s_ = svg(W, H, "Bauchi State: six local-government strata targeted as radii around a point, with ad cost per respondent",
             "; ".join(f'{r["lga"]} {money(r["cost"])}' for r in rows) + ".", body, "bau")
    write("nigeria-bauchi.svg", s_)
    SUMMARY["nigeria_bauchi"] = dict(study=slug, report_created=T[slug]["adopt_report_created"], strata=rows,
                                     fielded="2026-04-06..2026-04-17 (country-ng.json)")


if __name__ == "__main__":
    which = sys.argv[1:] or ["bolivia", "nigeria_2023", "nigeria_2024", "nigeria_bauchi", "indonesia"]
    for w in which:
        globals()[w]()
    json.dump(SUMMARY, open(os.path.join(OUT, "summary.json" if not sys.argv[1:] else "summary.partial.json"), "w"),
              indent=1, ensure_ascii=False)
