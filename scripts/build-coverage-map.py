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
  .mlegend   { display:flex; flex-wrap:wrap; gap:18px; margin-top:18px; align-items:center }
  .ml        { display:flex; align-items:center; gap:8px; color:var(--ink-3);
               font:400 11.5px "IBM Plex Mono", ui-monospace, monospace;
               font-variant-numeric:tabular-nums }
  .ml i      { width:20px; height:10px; background:var(--data); display:block; border-radius:2px }
  .ml i.p    { background:none; border:1.1px dashed var(--data) }
  .src       { font:400 13px/1.5 "Source Serif 4", Georgia, serif; font-style:italic;
               color:var(--ink-3); margin-top:16px; max-width:66ch }"""

CSS_STRIP = """  .cs-bar    { display:block; width:100%; height:auto }
  .cs-ground { fill:var(--rule) }
  .cs-seg    { fill:var(--data) }
  .cs-tick   { stroke:var(--rule-2); stroke-width:1; shape-rendering:crispEdges }
  .cs-lab    { font:500 10px "IBM Plex Mono", ui-monospace, monospace;
               letter-spacing:.13em; fill:var(--ink-2) }
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
    # `ours` is the countries with a COUNT, and nothing else. Until 2026-08-26 it also
    # held `pending` -- the four countries covered but not yet counted -- which had two
    # consequences beyond the dashed outline they were drawn with, and both would have
    # survived deleting the outline alone:
    #
    #   1. `covered_ids` is what the ghost pass skips. A pending country that is no
    #      longer drawn as covered but is still in `covered_ids` gets NO path at all --
    #      an invisible hole in the world, which reads worse than the outline did.
    #   2. The viewBox is the bounding box of `ours`, so uncounted countries were
    #      framing a map they contributed no value to.
    #
    # Dropping them here fixes both: they fall through to the ghost hairline and look
    # like every other country we have not surveyed, which is what they are on this
    # drawing. The DATA still records them (coverage.json `pending`, and its note that
    # they must never render as zero) -- not drawing a country is not calling it zero.
    respondents, pending = cov["respondents"], cov["pending"]
    ours, missing = {}, []
    for cc in list(respondents):
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

    # The map states no count. It used to read "Map of the N countries", which was
    # true only while the four uncounted countries were drawn; now that they are not,
    # a count in the label would disagree with the shapes underneath it. The totals
    # band states the country figure (C-017) and the map is a picture of coverage --
    # one number, in one place, is the whole point.
    svg = [
        '<svg class="coverage" xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{vb[0]:.0f} {vb[1]:.0f} {vb[2]:.0f} {vb[3]:.0f}" role="img" '
        'aria-label="Map of the countries where Virtual Lab has fielded studies">',
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
        # Countries in `pending` are NOT DRAWN. Nandan, 2026-08-26: "If that's true,
        # just leave them off entirely. Those are small details nobody cares about."
        # They used to render as a dashed outline with its own legend state and a
        # sentence of explanation -- three pieces of chrome for four countries whose
        # only property is that we have not finished a query. The data keeps them
        # (`pending` in coverage.json is still true and still says never render as
        # zero); the drawing does not. Leaving them off is not the same as calling
        # them zero, which is what that rule guards against.
    svg.append("</svg>")

    # The five step labels are thresholds by order of magnitude — scale marks on a
    # legend, not claims about anything. DESIGN.md 8 "Coverage section" says they carry
    # data-claim="none"; until 2026-08-25 this emitted no data-claim at all, so three of
    # them reported as `unsourced` on every run of check-claims.py and, once a page
    # annotated its own figures, as `unannotated`. The spec was right and the generator
    # had not caught up. Fixed here rather than in the output, which is never hand-edited.
    legend = ['<div class="mlegend">']
    for step in sorted(OPACITY):
        style = f' style="opacity:{OPACITY[step]}"' if OPACITY[step] != "1" else ""
        legend.append(f'<span class="ml" data-claim="none">'
                      f'<i{style}></i>{MAG_LABEL[step]}</span>')
    legend.append("</div>")

    # No source line. It read "Virtual Lab production database, queried read-only,
    # <date>" plus a sentence about the four uncounted countries, and both halves are
    # gone for the same reason -- see check-claims.py, "THE CITATION RULE". A map of
    # our own coverage attributed to our own database cites nothing a reader can check.
    # The legend still names every state it draws, which is what a reader actually
    # needs, and the magnitude labels carry data-claim="none".
    src = None
    return "\n".join(x for x in [
        header(cov, CSS_MAP),
        '<figure class="cov cov-map">',
        "".join(svg),
        "\n".join(legend),
        f'<figcaption class="src">{esc(src)}</figcaption>' if src else None,
        "</figure>",
    ] if x is not None), len(ours), len(missing)


# Label band under the bar. Added 2026-08-26 -- Nandan: "The bars per continent are
# missing the continents." They were: the region names existed only in the aria-label and
# in each segment's <title>, so they reached a screen reader and a hover and nobody else.
# The strip was drawn as the top half of a pair whose bottom half -- the six region cells,
# [P-4] -- carried the names, and [P-4] is held on the bucket question. A bar with no
# labels is not half a component, it is an unreadable one.
#
# Names only, never values. The bucketing is editorial and has no CLAIMS.md row, so the
# six numbers stay off the page; a name is not a figure and the widths are drawn from a
# VERIFIED table.
LAB_SIZE = 10.0      # mono, uppercase
LAB_TRACK = 0.13     # letter-spacing, em -- sec 4: uppercase always carries >= .11em
LAB_CPW = LAB_SIZE * 0.6 + LAB_SIZE * LAB_TRACK   # advance per character, ~7.3px
LAB_ROWS = (20.0, 38.0, 56.0)  # candidate baselines below the bar
LAB_PAD = 10.0                 # space kept clear at the right edge
LAB_GAP = 20.0                 # clear space between two labels sharing a baseline


def build_strip(cov, rows, attributed):
    total = cov["totals"]["respondents"]
    inner = STRIP_W - STRIP_GAP * (len(rows) - 1)
    widths = [max(STRIP_MIN, inner * r["total"] / attributed) if attributed else 0.0
              for r in rows]
    segs, labels, ticks, x = [], [], [], 0.0
    row_end = [0.0] * len(LAB_ROWS)   # rightmost x consumed on each baseline
    for i, (r, w) in enumerate(zip(rows, widths)):
        share = 100.0 * r["total"] / attributed if attributed else 0.0
        floor = " or more" if r["pending"] else ""
        segs.append(
            f'<rect class="cs-seg" x="{x:.2f}" y="0" width="{w:.2f}" height="{STRIP_H:.0f}" '
            f'fill-opacity="{r["opacity"]:.2f}">'
            f'<title>{esc(r["name"])} — {r["total"]:,}{floor} respondents, '
            f"{share:.1f}% of those attributed to a country</title></rect>")

        # Four of the six segments are wide enough to hold their own name; Europe &
        # Central Asia is 4% of the bar and the Pacific is 0.4%, so their labels are far
        # wider than the thing they name. Labels are therefore placed GREEDILY onto the
        # first baseline where they clear the last label already on it -- alternating by
        # index was the first attempt and it ran "SOUTH & SOUTHEAST ASIA" straight into
        # "PACIFIC", which reads as one region with a strange name.
        #
        # A leader tick keeps every label attached to its own segment however far the
        # text has been pushed, which is what makes pushing safe.
        name = r["name"].upper()
        est = len(name) * LAB_CPW
        lx = max(0.0, min(x, STRIP_W - LAB_PAD - est))
        row = next((k for k in range(len(LAB_ROWS)) if lx >= row_end[k]), None)
        if row is None:                       # every baseline occupied at this x
            row = min(range(len(LAB_ROWS)), key=lambda k: row_end[k])
            lx = max(lx, row_end[row])
        row_end[row] = lx + est + LAB_GAP
        ly = LAB_ROWS[row]
        ticks.append(f'<line class="cs-tick" x1="{x:.2f}" y1="{STRIP_H:.0f}" '
                     f'x2="{x:.2f}" y2="{STRIP_H + ly - LAB_SIZE:.1f}"/>')
        labels.append(f'<text class="cs-lab" x="{lx:.2f}" '
                      f'y="{STRIP_H + ly:.1f}">{esc(name)}</text>')
        x += w + STRIP_GAP

    used = [LAB_ROWS[k] for k in range(len(LAB_ROWS)) if row_end[k] > 0.0]
    band = STRIP_H + (max(used) if used else 0.0) + 6.0
    label = "; ".join(f'{r["name"]} {r["total"]:,}' for r in rows)
    # preserveAspectRatio="none" is GONE. It let the 30px bar stay 30px at any width, and
    # it also stretched everything else horizontally -- which is why this drawing could
    # never carry a word of type. Uniform scaling costs a pixel of bar height at full
    # measure and buys labels that are not smeared.
    svg = ("".join([
        '<svg class="cs-bar" xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {STRIP_W:.0f} {band:.0f}" '
        f'role="img" aria-label="Respondents by region, largest first: {esc(label)}">',
        "<title>Respondents by region</title>",
        f'<rect class="cs-ground" x="0" y="0" width="{STRIP_W:.0f}" '
        f'height="{STRIP_H:.0f}"/>',
        "".join(segs),
        "".join(ticks),
        "".join(labels),
        "</svg>",
    ]))
    # No source line at all. It read "The bar spans the N respondents attributable to a
    # country, not the M total: the remaining K belong to studies whose strata carry no
    # country tag" -- which is word for word the sentence Nandan cut from the prose
    # beneath this section on 2026-08-26 ("We dont need this"). Keeping it in the caption
    # would be reinstating by the back door what was removed from the front.
    #
    # What is lost is a reconciliation between two internal denominators. What is gained
    # is a figure that states its regions and nothing else. The numbers are still in
    # CLAIMS.md if a reader ever asks.
    src = None
    return "\n".join(x for x in [
        header(cov, CSS_STRIP),
        '<figure class="cov cov-strip">',
        svg,
        f'<figcaption class="src">{esc(src)}</figcaption>' if src else None,
        "</figure>",
    ] if x is not None)


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
    src = (f"Region totals sum to {attributed:,} of {total:,} respondents; the "
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
        print(f"{drawn} countries drawn; {len(cov['pending'])} pending, not drawn "
              f"({', '.join(cov['pending'])})",
              file=sys.stderr)
    if "strip" in fragments or "regions" in fragments:
        total = cov["totals"]["respondents"]
        print(f"{len(rows)} regions, {attributed:,} of {total:,} respondents "
              f"attributed ({total - attributed:,} unattributed)", file=sys.stderr)
    return 2 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
