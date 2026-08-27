#!/usr/bin/env python3
"""Emit assets/og.svg -- the social share card, 1200x630.

DIRECTION 08 "ATLAS PLATE", chosen by Nandan 2026-08-27 from eight mocked options.
Paper ground, the mark and wordmark over a hairline, two figures, and the coverage
map filling the lower two thirds at one solid fill.

WHY THIS IS GENERATED AND NOT DRAWN
-----------------------------------
Everything else on this site is generated, and a share card has the same two failure
modes as the page: the figures can drift from the database, and the map can drift from
the coverage. Both are solved the same way -- this reads `scripts/data/coverage.json`
and `world.geojson`, the identical sources `build-coverage-map.py` uses, and imports
that script's projection so the two drawings cannot disagree.

  Figures      coverage.json `totals`. NEVER typed. C-010 and C-016.
  Map          world.geojson, same projection, same `respondents` keys.
  Mark         assets/mark.svg, parsed -- not a second copy of the nine rects.

THE COUNTRY COUNT IS DELIBERATELY ABSENT, and this is the one composition decision
that is load-bearing rather than aesthetic. The map draws the 37 countries that have
a count; C-017 says 41. On the page those never meet. Setting "41 COUNTRIES" beside a
37-country map would put the gap on the most-shared surface we own. So the card states
respondents and responses, and says nothing about countries. **Do not add it.**

WHY THE RAMP IS FLAT. The page's five-step opacity ramp is really a two-step ramp --
33 of 37 countries sit at .56 and .76, which differ by 1.35:1 and read as one value.
At 360px in a Slack feed it is one value. So the card fills every covered country at
`--data` solid, and carries no legend because a binary fill has nothing to key. D-018
governs the page's map; it does not reach an asset that renders at a third of size.

WHY PAPER AND NOT INK. Measured, against expectation: the choropleth's top step is
6.52:1 on paper and 4.88:1 on ink. The `--rule-2` border exists because paper on a
white Slack ground is 1.11:1 -- without it the card has no edge.

THEME. An og:image is one fixed raster and inherits nothing, so every colour here is
a literal. Each is a DESIGN.md 3 token RESOLVED AT LIGHT -- the same resolution
build-favicon.py makes, and for the same reason. Note that `--invert` and `--on-invert`
are NOT theme-identical, whatever the comment in that script says; the genuinely
identical pair is `--brass-inv` / `--data-inv`, and neither appears on this card.

RASTERIZING. og:image must be raster; no platform renders SVG. That step is NOT in
this script and NOT in the deploy: `netlify.toml` promises scripts/ is stdlib Python
needing nothing installed, and a rasterizer would break that promise. assets/og.png is
committed, exactly as assets/apple-touch-icon.png is. scripts/README.md has the
command, and it needs the brand faces, which are not installed system-wide.

  python3 scripts/build-og-image.py        # -> assets/og.svg
"""
import argparse
import pathlib
import re
import sys
import importlib.util

# The map generator's filename is not a Python identifier, so it cannot be imported
# by name. Load it by path -- the point being that its projection, its ISO lookups
# and its coverage loader are used here rather than reimplemented.

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
_spec = importlib.util.spec_from_file_location("covmap", HERE / "build-coverage-map.py")
covmap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(covmap)

W, H = 1200, 630
OUT = REPO / "assets" / "og.svg"

# DESIGN.md 3, resolved at light. See the theme note above.
PAPER, INK, INK_2 = "#F1F4F5", "#1F272E", "#4A555E"
RULE, RULE_2, DATA = "#CFD9DD", "#AEBCC2", "#1D5F6E"
LAT_OP = ".042"


def mark_rects():
    """The nine cells of assets/mark.svg, read rather than re-typed."""
    svg = (REPO / "assets" / "mark.svg").read_text()
    out = []
    for m in re.finditer(r"<rect\b([^>]*)/>", svg):
        a = m.group(1)
        g = lambda k: re.search(rf'{k}="([^"]+)"', a)
        op = g("fill-opacity")
        out.append((float(g("x").group(1)), float(g("y").group(1)),
                    float(g("width").group(1)), float(g("height").group(1)),
                    op.group(1) if op else None))
    if len(out) != 9:
        raise SystemExit(f"mark.svg: expected 9 cells, found {len(out)}")
    return out


def map_paths():
    """Ghost world and covered countries, from the map generator's own projection."""
    cov = covmap.load_coverage()
    feats = covmap.json.loads((covmap.DATA / "world.geojson").read_text())["features"]
    by3, by_name = {}, {}
    for f in feats:
        p = f["properties"]
        if p.get("iso_a3") and p["iso_a3"] != "-99":
            by3[p["iso_a3"]] = f
        by_name[p["name"]] = f

    ours, missing = {}, []
    for cc in cov["respondents"]:
        f = covmap.feature_for(cc, by3, by_name)
        if f is None:
            missing.append(cc)
            continue
        ours[cc] = [[covmap.project(*pt) for pt in r] for r in covmap.rings(f["geometry"])]
    if missing:
        raise SystemExit(f"no boundary for {', '.join(missing)} -- see build-coverage-map.py")

    covered = {id(covmap.feature_for(c, by3, by_name)) for c in ours}
    ghost = []
    for f in feats:
        if id(f) in covered or f["properties"]["name"] == "Antarctica":
            continue
        d = covmap.path_of([[covmap.project(*pt) for pt in r] for r in covmap.rings(f["geometry"])])
        if d:
            ghost.append(d)

    solid = [covmap.path_of(p) for p in ours.values()]
    xs = [x for polys in ours.values() for r in polys for x, _ in r]
    ys = [y for polys in ours.values() for r in polys for _, y in r]
    P = covmap.PAD
    box = (min(xs) - P, min(ys) - P, max(xs) - min(xs) + 2 * P, max(ys) - min(ys) + 2 * P)
    return "".join(ghost), "".join(d for d in solid if d), box, len(ours)


def build():
    ghost, solid, (bx, by, bw, bh), drawn = map_paths()
    cov = covmap.load_coverage()

    # Figures from the database, never typed. C-010 and C-016.
    respondents = f"{cov['totals']['respondents']:,}"
    responses = f"{cov['totals']['responses']:,}"

    # The map occupies everything below the figures, scaled to fill the full width.
    #
    # 262 is not arbitrary and is not taste. The covered-country bounding box is 340
    # projected units tall; at 1200/1108 it renders 368px, and 630 - 262 = 368. So the
    # footprint lands flush to the bottom edge with nothing clipped, and the ghost
    # world runs off the card exactly as D-018 crops it on the page. Changing `top`
    # without re-deriving it either clips the footprint or floats it.
    top = 262
    scale = W / bw
    tx, ty = -bx * scale, top - by * scale

    cells = "".join(
        f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"'
        + (f' fill-opacity="{op}"' if op else "") + "/>"
        for x, y, w, h, op in mark_rects())

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"
     viewBox="0 0 {W} {H}" role="img"
     aria-label="Virtual Lab — {respondents} respondents, {responses} survey responses, and the countries where studies have been fielded">
<!-- GENERATED by scripts/build-og-image.py. Do not hand-edit. -->
<!-- Figures: Virtual Lab production database, {cov['as_of']}. Map: {drawn} countries with a count. -->
<title>Virtual Lab</title>
<defs>
  <pattern id="lat" width="18" height="18" patternUnits="userSpaceOnUse">
    <rect width="8" height="8" fill="{INK}"/>
  </pattern>
  <clipPath id="card"><rect width="{W}" height="{H}"/></clipPath>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{PAPER}"/>
  <rect width="{W}" height="{H}" fill="url(#lat)" opacity="{LAT_OP}"/>

  <g fill="{INK}" transform="translate(64,56) scale(1.7)">{cells}</g>
  <text x="119" y="86" font-family="Zilla Slab, Georgia, serif" font-weight="300"
        font-size="32" letter-spacing="-0.32" fill="{INK}">Virtual Lab</text>

  <rect x="64" y="130" width="{W - 128}" height="1" fill="{RULE}"/>

  <g font-family="IBM Plex Mono, ui-monospace, monospace" font-weight="400"
     font-size="48" letter-spacing="-1.44" fill="{INK}">
    <text x="64" y="196">{respondents}</text>
    <text x="470" y="196">{responses}</text>
  </g>
  <g font-family="IBM Plex Mono, ui-monospace, monospace" font-weight="500"
     font-size="16" letter-spacing="2.08" fill="{INK_2}">
    <text x="64" y="226">RESPONDENTS</text>
    <text x="470" y="226">SURVEY RESPONSES</text>
  </g>

  <g transform="translate({tx:.3f},{ty:.3f}) scale({scale:.4f})">
    <path d="{ghost}" fill="{RULE}"/>
    <path d="{solid}" fill="{DATA}"/>
  </g>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" fill="none"
      stroke="{RULE_2}" stroke-width="1"/>
</svg>
'''


def main():
    ap = argparse.ArgumentParser(
        prog="build-og-image.py",
        description="Emit assets/og.svg, the 1200x630 social share card.",
        epilog="Rasterize separately; see scripts/README.md. og.png is committed.")
    ap.add_argument("-o", "--out", type=pathlib.Path, default=OUT)
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args()

    svg = build()
    if args.stdout:
        print(svg)
    else:
        args.out.write_text(svg)
        print(f"wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
