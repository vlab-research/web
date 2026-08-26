#!/usr/bin/env python3
"""Build the three artefacts of the coverage section from one data file.

    python3 scripts/build-coverage-map.py            # writes all three to build/
    python3 scripts/build-coverage-map.py --help
    python3 scripts/build-coverage-map.py --only map --stdout > coverage-map.html

The coverage section is **map + region strip + region totals**, and all three come
from `scripts/data/coverage.json`. They used to come from two places — the map from
this script, the strip from a scratch session that was lost — which is how the strip
drifted out of the build. One command, one data file, three files out:

  build/coverage-map.html      cropped choropleth · legend · source line
  build/coverage-strip.html    respondents-by-region bar · source line
  build/coverage-regions.html  region totals cells · source line · floors note

**The map is settled as D-018.** Cropped choropleth: countries where we have fielded
a study are filled in `--data` at one of five opacity steps by order of magnitude;
every other country is a hairline outline in `--rule`; the frame is cropped to the
bounding box of the covered countries. Read D-018 before changing the treatment, and
DESIGN.md §6 before reaching for any other kind of map.

Three rules this script exists to keep, all of them easy to break by hand:

1. **Pending is not zero.** Countries in `pending` are coverage *without a count*.
   They render as a dashed `--data` outline on the map, they add nothing to a region
   total, and a region that contains one has a total that is a **floor** — which the
   region fragment states in words, per `_regions_note`.
2. **Region totals do not sum to the whole.** They sum to the *attributed*
   respondents; the balance belongs to studies whose strata carry no country tag
   (CLAIMS.md, "Two limits on this table"). Every source line here names both numbers
   so no reader can mistake one for the other.
3. **Tokens only.** No literal colour anywhere in the emitted markup — every fill and
   stroke is a `var(--…)` from DESIGN.md §3, so the graphics inherit the page theme
   and work in all three theme states.

Inputs, both in scripts/data/:
  coverage.json   respondent counts per ISO-2 country. Refresh from production; see
                  CLAIMS.md, "Refreshing the placeholders". Bump `as_of` when you do.
  world.geojson   Natural Earth 1:110m country boundaries, simplified at 0.35 deg.

The required CSS for each fragment is emitted in a comment at the head of that
fragment. Never hand-edit the output; refresh the data and re-run.
"""
import argparse
import html
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
DATA = HERE / "data"
DEFAULT_OUT = HERE.parent / "build"

# --- map geometry -----------------------------------------------------------
# Equirectangular, clipped north and south of the inhabited latitudes.
W, LAT_N, LAT_S = 1160.0, 84.0, -56.0
H = W * (LAT_N - LAT_S) / 360.0
PAD = 26  # viewBox padding, in projected units

# Five discrete steps, not a continuous ramp: the map reads as an instrument with
# states rather than as a heat blur. DESIGN.md §8 fixes these five values.
OPACITY = {1: ".26", 2: ".40", 3: ".56", 4: ".76", 5: "1"}
# What each step actually means, given magnitude() below. Generated into the legend
# rather than written by hand — the hand-written version had every threshold wrong.
MAG_LABEL = {1: "under 100", 2: "100+", 3: "1,000+", 4: "10,000+", 5: "100,000+"}

# --- strip geometry ---------------------------------------------------------
STRIP_W, STRIP_H = 1160.0, 30.0
STRIP_GAP = 1.0   # hairline of --rule showing between segments
STRIP_MIN = 2.0   # a region never disappears, however small its share
# Rank ramp for the strip, darkest first. Distinct from the map's five magnitude
# steps: on the strip the segment *width* already carries the value, so opacity is
# doing the secondary job of ordering. Six values for the six settled regions;
# interpolated between the same endpoints if the region list ever changes length.
STRIP_RAMP = [0.95, 0.78, 0.62, 0.48, 0.34, 0.22]

ISO2_TO_ISO3 = {
    "AE": "ARE", "BD": "BGD", "BG": "BGR", "BZ": "BLZ", "CG": "COG", "CM": "CMR",
    "DE": "DEU", "DJ": "DJI", "EG": "EGY", "GH": "GHA", "GM": "GMB", "HN": "HND",
    "HT": "HTI", "ID": "IDN", "IE": "IRL", "IL": "ISR", "IN": "IND", "IQ": "IRQ",
    "JM": "JAM", "JO": "JOR", "KE": "KEN", "KG": "KGZ", "KW": "KWT", "LA": "LAO",
    "LB": "LBN", "LY": "LBY", "MA": "MAR", "MD": "MDA", "MK": "MKD", "NG": "NGA",
    "PG": "PNG", "PK": "PAK", "PS": "PSE", "RO": "ROU", "RS": "SRB", "SA": "SAU",
    "TD": "TCD", "UA": "UKR", "US": "USA", "XK": "KOS", "ZM": "ZMB",
}
# Natural Earth carries no ISO code for these; match on the `name` property instead.
BY_NAME = {"XK": "Kosovo"}
# Natural Earth 1:110m is dated in places. Display name wins; the geometry does not.
DISPLAY_NAME = {"MK": "North Macedonia"}


# --- projection and paths ---------------------------------------------------

def project(lon, lat):
    lat = max(LAT_S, min(LAT_N, lat))
    return ((lon + 180.0) / 360.0 * W, (LAT_N - lat) / (LAT_N - LAT_S) * H)


def rings(geom):
    coords = geom["coordinates"]
    polys = [coords] if geom["type"] == "Polygon" else coords
    return [p[0] for p in polys]


def path_of(polys):
    out = []
    for ring in polys:
        if len(ring) < 3:
            continue
        out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in ring) + "Z")
    return "".join(out)


def magnitude(v):
    return max(1, min(5, int(math.log10(v)) if v >= 10 else 1))


def esc(s):
    return html.escape(str(s), quote=True)


# --- data -------------------------------------------------------------------

def load_coverage():
    return json.loads((DATA / "coverage.json").read_text())


def feature_for(cc, by3, by_name):
    return by3.get(ISO2_TO_ISO3.get(cc, "")) or by_name.get(BY_NAME.get(cc, ""))


def warn(lines):
    """Loud, not silent: a country we cover that never renders is a lie of omission."""
    bar = "!" * 72
    print("\n".join([bar] + [f"!! {line}" for line in lines] + [bar]), file=sys.stderr)


def region_rows(cov):
    """Region totals, largest first, each carrying its own pending count.

    A region containing a pending country is a floor, not a total. That fact travels
    with the row so no caller can render the number without it.
    """
    resp, pending = cov["respondents"], set(cov["pending"])
    listed = [c for r in cov["regions"] for c in r["countries"]]
    unplaced = (set(resp) | pending) - set(listed)
    duplicated = sorted({c for c in listed if listed.count(c) > 1})
    if unplaced or duplicated:
        problems = []
        if unplaced:
            problems.append(f"in no region, so absent from every total: "
                            f"{', '.join(sorted(unplaced))}")
        if duplicated:
            problems.append(f"in more than one region, so double-counted: "
                            f"{', '.join(duplicated)}")
        warn(["coverage.json regions do not partition the countries"] + problems)

    rows = []
    for r in cov["regions"]:
        countries = r["countries"]
        rows.append({
            "name": r["name"],
            "total": sum(resp.get(c, 0) for c in countries),
            "countries": len(countries),
            "pending": [c for c in countries if c in pending],
        })
    rows.sort(key=lambda r: -r["total"])
    n = len(rows)
    for i, r in enumerate(rows):
        if n == len(STRIP_RAMP):
            r["opacity"] = STRIP_RAMP[i]
        else:
            t = i / (n - 1) if n > 1 else 0.0
            r["opacity"] = STRIP_RAMP[0] + (STRIP_RAMP[-1] - STRIP_RAMP[0]) * t
    return rows


def pending_names(cov, by3, by_name):
    out = []
    for cc in cov["pending"]:
        f = feature_for(cc, by3, by_name)
        out.append(DISPLAY_NAME.get(cc, f["properties"]["name"] if f else cc))
    return out


def prose_list(items):
    items = list(items)
    if len(items) < 2:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


# --- fragments --------------------------------------------------------------

CSS_MAP = """  .cov       { margin:0 }
  .coverage  { display:block; width:100%; height:auto }
  .cv-ghost  { fill:none; stroke:var(--rule); stroke-width:.7 }
  .cv-on     { fill:var(--data); stroke:var(--paper); stroke-width:.6 }
  .cv-pending{ fill:none; stroke:var(--data); stroke-width:1.2; stroke-dasharray:3 2 }
  .mlegend   { display:flex; flex-wrap:wrap; gap:18px; margin-top:18px; align-items:center }
  .ml        { display:flex; align-items:center; gap:8px; color:var(--ink-3);
               font:400 11.5px "IBM Plex Mono", ui-monospace, monospace;
               font-variant-numeric:tabular-nums }
  .ml i      { width:20px; height:10px; background:var(--data); display:block; border-radius:2px }
  .ml i.p    { background:none; border:1.1px dashed var(--data) }
  .src       { font:400 13px/1.5 "Source Serif 4", Georgia, serif; font-style:italic;
               color:var(--ink-3); margin-top:16px; max-width:66ch }"""

CSS_STRIP = """  .cs-bar    { display:block; width:100%; height:30px }
  .cs-ground { fill:var(--rule) }
  .cs-seg    { fill:var(--data) }
  .src       { font:400 13px/1.5 "Source Serif 4", Georgia, serif; font-style:italic;
               color:var(--ink-3); margin-top:16px; max-width:66ch }"""

CSS_REGIONS = """  .cs-cells  { display:grid; grid-template-columns:repeat(6,1fr); gap:1px;
               background:var(--rule); border-top:1px solid var(--rule);
               border-bottom:1px solid var(--rule); margin-top:1px }
  .cs-cell   { background:var(--paper); padding:18px 16px 16px;
               display:flex; flex-direction:column; gap:0 }
  .cs-n      { font:400 clamp(22px,2.2vw,28px)/1 "IBM Plex Mono", ui-monospace, monospace;
               letter-spacing:-.025em; color:var(--ink); font-variant-numeric:tabular-nums }
  .cs-r      { margin-top:11px; font:500 10px "IBM Plex Mono", ui-monospace, monospace;
               letter-spacing:.13em; text-transform:uppercase; color:var(--ink-2); line-height:1.5 }
  .cs-m      { margin-top:7px; font:400 12.5px "Source Serif 4", Georgia, serif;
               font-style:italic; color:var(--ink-3) }
  .cs-p      { margin-top:5px; font:400 11px "IBM Plex Mono", ui-monospace, monospace;
               color:var(--brass); font-variant-numeric:tabular-nums }
  .note      { border-left:2px solid var(--brass); padding:4px 0 4px 18px; margin-top:34px;
               display:flex; flex-direction:column; gap:9px; max-width:66ch }
  .note .hd  { font:500 10.5px "IBM Plex Mono", ui-monospace, monospace; letter-spacing:.14em;
               text-transform:uppercase; color:var(--brass) }
  .note p    { font:400 15px/1.6 "Source Sans 3", "Helvetica Neue", Arial, sans-serif;
               color:var(--ink-2); margin:0 }
  @media (max-width:1000px){ .cs-cells{ grid-template-columns:repeat(3,1fr) } }
  @media (max-width:640px) { .cs-cells{ grid-template-columns:repeat(2,1fr) } }"""


def header(cov, css):
    return "\n".join([
        "<!-- Generated by scripts/build-coverage-map.py. Do not hand-edit. -->",
        f'<!-- Data as of {cov["as_of"]}. Source: {cov["_source"]} -->',
        "<!-- Required CSS (tokens from DESIGN.md §3):",
        css,
        "-->",
    ])


def build_map(cov, feats, by3, by_name):
    respondents, pending = cov["respondents"], cov["pending"]
    ours, missing = {}, []
    for cc in list(respondents) + pending:
        f = feature_for(cc, by3, by_name)
        if f is None:
            missing.append(cc)
            continue
        ours[cc] = [[project(*pt) for pt in r] for r in rings(f["geometry"])]
    if missing:
        warn([f"no boundary for {', '.join(missing)}",
              "those countries are covered but will not appear on the map",
              "fix ISO2_TO_ISO3 / BY_NAME, or the map understates the footprint"])

    covered_ids = {id(feature_for(c, by3, by_name)) for c in ours}
    xs = [x for polys in ours.values() for r in polys for x, _ in r]
    ys = [y for polys in ours.values() for r in polys for _, y in r]
    vb = (min(xs) - PAD, min(ys) - PAD,
          max(xs) - min(xs) + 2 * PAD, max(ys) - min(ys) + 2 * PAD)

    ghost = []
    for f in feats:
        if id(f) in covered_ids or f["properties"]["name"] == "Antarctica":
            continue
        d = path_of([[project(*pt) for pt in r] for r in rings(f["geometry"])])
        if d:
            ghost.append(d)

    n_countries = cov["totals"]["countries"]
    svg = [
        '<svg class="coverage" xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{vb[0]:.0f} {vb[1]:.0f} {vb[2]:.0f} {vb[3]:.0f}" role="img" '
        f'aria-label="Map of the {n_countries} countries where Virtual Lab '
        'has fielded studies">',
        "<title>Countries where Virtual Lab has fielded studies</title>",
        f'<path class="cv-ghost" d="{"".join(ghost)}"/>',
    ]
    for cc, polys in ours.items():
        d = path_of(polys)
        if not d:
            continue
        name = esc(DISPLAY_NAME.get(cc, (feature_for(cc, by3, by_name) or {})
                                    .get("properties", {}).get("name", cc)))
        if cc in respondents:
            n = respondents[cc]
            svg.append(
                f'<path class="cv-on" fill-opacity="{OPACITY[magnitude(n)]}" d="{d}">'
                f"<title>{name} — {n:,} respondents</title></path>")
        else:
            svg.append(f'<path class="cv-pending" d="{d}">'
                       f"<title>{name} — covered, count pending</title></path>")
    svg.append("</svg>")

    legend = ['<div class="mlegend">']
    for step in sorted(OPACITY):
        style = f' style="opacity:{OPACITY[step]}"' if OPACITY[step] != "1" else ""
        legend.append(f'<span class="ml"><i{style}></i>{MAG_LABEL[step]}</span>')
    legend.append('<span class="ml"><i class="p"></i>covered, count pending</span>')
    legend.append("</div>")

    src = (f'Virtual Lab production database, queried read-only, {cov["as_of"]}. '
           f'{n_countries} countries; {len(pending)} of them '
           f'({", ".join(pending)}) are covered but not yet counted, and are drawn '
           "as an outline rather than as a value.")
    return "\n".join([
        header(cov, CSS_MAP),
        '<figure class="cov cov-map">',
        "".join(svg),
        "\n".join(legend),
        f'<figcaption class="src">{esc(src)}</figcaption>',
        "</figure>",
    ]), len(ours), len(missing)


def build_strip(cov, rows, attributed):
    total = cov["totals"]["respondents"]
    inner = STRIP_W - STRIP_GAP * (len(rows) - 1)
    widths = [max(STRIP_MIN, inner * r["total"] / attributed) if attributed else 0.0
              for r in rows]
    segs, x = [], 0.0
    for r, w in zip(rows, widths):
        share = 100.0 * r["total"] / attributed if attributed else 0.0
        floor = " or more" if r["pending"] else ""
        segs.append(
            f'<rect class="cs-seg" x="{x:.2f}" y="0" width="{w:.2f}" height="{STRIP_H:.0f}" '
            f'fill-opacity="{r["opacity"]:.2f}">'
            f'<title>{esc(r["name"])} — {r["total"]:,}{floor} respondents, '
            f"{share:.1f}% of those attributed to a country</title></rect>")
        x += w + STRIP_GAP

    label = "; ".join(f'{r["name"]} {r["total"]:,}' for r in rows)
    svg = ("".join([
        '<svg class="cs-bar" xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {STRIP_W:.0f} {STRIP_H:.0f}" preserveAspectRatio="none" '
        f'role="img" aria-label="Respondents by region, largest first: {esc(label)}">',
        "<title>Respondents by region</title>",
        f'<rect class="cs-ground" x="0" y="0" width="{STRIP_W:.0f}" '
        f'height="{STRIP_H:.0f}"/>',
        "".join(segs),
        "</svg>",
    ]))
    src = (f'Virtual Lab production database, queried read-only, {cov["as_of"]}. '
           f"The bar spans the {attributed:,} respondents attributable to a country, "
           f"not the {total:,} total: the remaining {total - attributed:,} belong to "
           "studies whose strata carry no country tag.")
    return "\n".join([
        header(cov, CSS_STRIP),
        '<figure class="cov cov-strip">',
        svg,
        f'<figcaption class="src">{esc(src)}</figcaption>',
        "</figure>",
    ])


def build_regions(cov, rows, attributed, pending_display):
    total = cov["totals"]["respondents"]
    cells = ['<div class="cs-cells">']
    for r in rows:
        cells.append(
            '<div class="cs-cell">'
            f'<span class="cs-n">{r["total"]:,}</span>'
            f'<span class="cs-r">{esc(r["name"])}</span>'
            f'<span class="cs-m">{r["countries"]} '
            f'{"country" if r["countries"] == 1 else "countries"}</span>'
            + (f'<span class="cs-p">floor — {len(r["pending"])} not yet counted</span>'
               if r["pending"] else "")
            + "</div>")
    cells.append("</div>")

    floors = [r["name"] for r in rows if r["pending"]]
    src = (f'Virtual Lab production database, queried read-only, {cov["as_of"]}. '
           f"Region totals sum to {attributed:,} of {total:,} respondents; the "
           f"remaining {total - attributed:,} belong to studies whose strata carry no "
           f"country tag, not to any country outside the "
           f'{cov["totals"]["countries"]}.')
    one = len(floors) == 1
    note = (f'{prose_list(pending_display)} have verified coverage but no computed '
            "respondent count yet, so they contribute nothing to the totals above. "
            f'{prose_list(floors)} {"is" if one else "are"} '
            f'therefore {"a floor, not a complete figure" if one else "floors, not complete figures"}'
            " — the affected cells carry the note themselves rather than a footnote.")
    heading = ("Why a regional total is a floor" if one
               else "Why these regional totals are floors")
    return "\n".join([
        header(cov, CSS_REGIONS),
        '<div class="cov cov-regions">',
        "".join(cells),
        f'<p class="src">{esc(src)}</p>',
        f'<div class="note"><span class="hd">{esc(heading)}</span>'
        f"<p>{esc(note)}</p></div>",
        "</div>",
    ])


# --- cli --------------------------------------------------------------------

FILENAMES = {"map": "coverage-map.html",
             "strip": "coverage-strip.html",
             "regions": "coverage-regions.html"}


def main():
    ap = argparse.ArgumentParser(
        prog="build-coverage-map.py",
        description=("Build the coverage section — map, region strip and region "
                     "totals — from scripts/data/coverage.json. Every artefact is "
                     "inline SVG or plain markup referencing DESIGN.md tokens only."),
        epilog=("Countries in `pending` are coverage without a count: never a zero "
                "fill, and a region containing one has a total that is a floor. "
                "Region totals sum to the attributed respondents, not to the whole; "
                "every source line says so. See D-018 and DESIGN.md §8."),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--out-dir", type=pathlib.Path, default=DEFAULT_OUT,
                    help=f"directory to write into (default: {DEFAULT_OUT})")
    ap.add_argument("--only", choices=sorted(FILENAMES), action="append",
                    help="build just this artefact; repeatable (default: all three)")
    ap.add_argument("--stdout", action="store_true",
                    help="write to stdout instead of files; use with a single --only")
    args = ap.parse_args()

    wanted = args.only or sorted(FILENAMES)
    if args.stdout and len(wanted) != 1:
        ap.error("--stdout needs exactly one --only")

    cov = load_coverage()
    feats = json.loads((DATA / "world.geojson").read_text())["features"]
    by3, by_name = {}, {}
    for f in feats:
        p = f["properties"]
        if p.get("iso_a3") and p["iso_a3"] != "-99":
            by3[p["iso_a3"]] = f
        by_name[p["name"]] = f

    rows = region_rows(cov)
    attributed = sum(r["total"] for r in rows)
    fragments, drawn, missing = {}, 0, 0
    if "map" in wanted:
        fragments["map"], drawn, missing = build_map(cov, feats, by3, by_name)
    if "strip" in wanted:
        fragments["strip"] = build_strip(cov, rows, attributed)
    if "regions" in wanted:
        fragments["regions"] = build_regions(
            cov, rows, attributed, pending_names(cov, by3, by_name))

    if args.stdout:
        print(fragments[wanted[0]])
    else:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        for key in wanted:
            path = args.out_dir / FILENAMES[key]
            path.write_text(fragments[key] + "\n")
            print(f"wrote {path}", file=sys.stderr)

    if "map" in fragments:
        print(f"{drawn} countries drawn, {len(cov['pending'])} of them pending",
              file=sys.stderr)
    if "strip" in fragments or "regions" in fragments:
        total = cov["totals"]["respondents"]
        print(f"{len(rows)} regions, {attributed:,} of {total:,} respondents "
              f"attributed ({total - attributed:,} unattributed)", file=sys.stderr)
    return 2 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
