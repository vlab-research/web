#!/usr/bin/env python3
"""Build assets/figures/reallocations-box.svg from scripts/data/reallocations.json.

BLOCKED, 2026-08-26. This script is complete and it will not draw yet, on purpose.
C-092 gives median 61, p75 165, p90 351 and max 1,308 -- but a box plot's box spans
p25 to p75 and its whiskers span p10 to p90, so TWO of the five values the form needs
do not exist. AGENTS.md hard rule 2: never invent a figure, not as a placeholder, not
"to be replaced later". So it exits non-zero and names what is missing.

The query that fills them is in scripts/data/reallocations.json. One read-only run and
this figure draws.

Why the same form and not a different one: the three box plots are deliberately ONE
figure in three units, so a reader who learns to read one has learned to read all of
them. Inventing an asymmetric variant for this dataset because two numbers are absent
would break that for the sake of shipping a week early.

The figure is M3 (interval) drawn on M4 (tick rule), from the four primitives only:
a bracket at each whisker end, a bar for the interquartile box, a cell for the median,
and ticks for the ruler. No chart library, no literal colour -- hard rule 8 and
DESIGN.md sec 3.

Never hand-edit the SVG. Change this script or the data and re-run.

    python3 scripts/build-throughput-figure.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "scripts" / "data" / "reallocations.json"
OUT = ROOT / "assets" / "figures" / "reallocations-box.svg"
NARROW_OUT = ROOT / "assets" / "figures" / "reallocations-box-narrow.svg"

# Geometry. Width matches assets/figures/mad-comparison.svg so the two figures sit
# on one page without a rescale being read into either.
# Width. Widened 620 -> 1160 on 2026-08-26: Nandan, "The box plots are beautiful but too
# small. Should probably be full width. Need to be bigger."
#
# The figure is REDRAWN wider rather than scaled up, and the difference is the whole
# point. These SVGs carry their own type at absolute sizes -- 13px labels, 15px numerals,
# 12px source lines -- so stretching a 620-unit drawing across 1116 CSS px would scale
# every one of them by 1.8x and land the axis labels somewhere between h3 and h2 on a
# scale DESIGN.md sec 4 fixes exactly. Widening the viewBox instead keeps the type at its
# designed size and spends the extra room on the ruler, which is where it is worth having:
# the same interval is drawn against three times the graduation.
#
# 1160 matches STRIP_W in build-coverage-map.py, so every full-width drawing on the page
# is set out on one measure.
W = 1160
PLOT_X0, PLOT_X1 = 180.0, W - 56.0
Y_MID = 34.0          # the interval's centreline
BOX_H = 24.0          # the bar primitive
CELL = 12.0           # the median cell -- a cell, never a dot (sec 6 M3)
CAP_H = 18.0          # bracket height at each whisker end
Y_AXIS = 58.0         # M4 tick rule
H = 152


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# --- Source-line wrapping ------------------------------------------------------
# DESIGN.md sec 2 makes the source line mandatory and sec 8 puts it in the same
# visual unit as the figure -- so it lives inside this SVG. An outer <svg> clips at
# its own bounds, and both source strings are longer than W at 12px, so the second
# half of each was being SILENTLY TRUNCATED: "Whiskers: 10th" with no closing value,
# and the ad-cost line losing "not our fee" entirely. A figure that drops half its
# provenance is the one failure this drawing cannot afford, so the lines wrap and
# the viewBox grows to hold them.
#
# SRC_CPL is a character budget, not a measurement: there is no font metric here and
# no dependency is permitted. 12px Source Serif 4 italic averages a shade under 6px
# per character, so W/6 is the budget and it is deliberately conservative.
SRC_SIZE = 12.0
SRC_LEAD = 16.0
SRC_CPL = int(W // 6)


def wrap_src(text, cpl=SRC_CPL):
    """Greedy wrap on spaces. Never breaks a word -- a hyphenated figure caption
    reads as a typo, and every one of these strings carries a number."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and len(trial) > cpl:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def src_block(*texts, y0, W=W, cpl=None):
    """The wrapped source lines as SVG, plus the y of the last baseline.

    Exits non-zero on a single word wider than the box, for the same reason the
    axis guard exists: a figure must fail loudly rather than clip its evidence."""
    cpl = cpl or int(W // 6)
    lines = [ln for t in texts for ln in wrap_src(t, cpl)]
    for ln in lines:
        if len(ln) > cpl:
            sys.exit(f"FIGURE CLIPPED: source line does not fit {W}px at {SRC_SIZE}px "
                     f"({len(ln)} > {cpl} chars): {ln!r}")
    svg = "\n".join(
        f'  <text class="src" x="0" y="{y0 + i * SRC_LEAD:.0f}" '
        f'data-claim-source="">{esc(ln)}</text>'
        for i, ln in enumerate(lines))
    return svg, y0 + SRC_LEAD * (len(lines) - 1)


def render(W, PLOT_X0, PLOT_X1, Y_MID, Y_AXIS, narrow=False):
    """One figure at one width. Called twice.

    NARROW VARIANT, added 2026-08-26 -- Nandan: "The box plots don't always fit on the
    page in mobile." They did not: the drawing is 1160 units wide and its type is sized
    in absolute pixels, so scaling it into ~440px of phone puts the 13px label at 5px.
    A minimum width plus overflow-x kept it legible but made it scroll, which is what he
    was seeing.

    An SVG scales its text with itself, so the only real fix is a SECOND viewBox that is
    already narrow. Same drawing, same primitives, same source text -- the label moves
    above the plot instead of beside it, the plot starts at x=0, and the source lines
    rewrap to the narrower budget. CSS shows exactly one; both come from this script.
    """
    d = json.loads(DATA.read_text())
    p = d["percentiles"]

    # The block. Same shape as the axis guard below: fail loudly rather than draw
    # something that is not the claim.
    absent = [k for k in ("p10", "p25", "median", "p75", "p90") if p.get(k) is None]
    if absent:
        sys.exit(
            f"BLOCKED: {', '.join(absent)} missing from {DATA.name}.\n"
            f"  C-092 records median/p75/p90/max only. A box plot's box is p25-p75 and\n"
            f"  its whiskers are p10-p90, so this figure cannot be drawn from it.\n"
            f"  Hard rule 2: never invent a figure, not even as a placeholder.\n"
            f"  The query that fills them is the `query` field of {DATA.name}.")
    ax = d["axis"]
    pop = d["population"]

    lo, hi = float(ax["min"]), float(ax["max"])
    span = PLOT_X1 - PLOT_X0

    def x(v):
        if not lo <= v <= hi:
            sys.exit(f"FAIL: {v} is outside the drawn axis {lo}-{hi}. The axis must "
                     f"contain every value it draws, or the figure clips a claim.")
        return PLOT_X0 + (v - lo) / (hi - lo) * span

    x10, x25, x50, x75, x90 = (x(p[k]) for k in ("p10", "p25", "median", "p75", "p90"))

    # Ruler graduations. Major marks reach higher than minor ones (sec 6 M4).
    ticks = []
    v = int(lo)
    while v <= hi:
        major = v in ax["major_ticks"]
        tx = x(v)
        ticks.append(f'  <line class="axis" x1="{tx:.1f}" y1="{Y_AXIS}" '
                     f'x2="{tx:.1f}" y2="{Y_AXIS + (7 if major else 4)}"/>')
        v += ax["tick_every"]

    # Axis labels come from the data file's major_ticks, so the ruler and its numbers
    # can never disagree. The last one carries the unit.
    mt = ax["major_ticks"]
    tick_labels = []
    for i, v in enumerate(mt):
        anchor = ("" if i == 0 else
                  ' text-anchor="end"' if i == len(mt) - 1 else ' text-anchor="middle"')
        txt = f"{v:,} REALLOCATIONS" if i == len(mt) - 1 else f"{v:,}"
        tick_labels.append(
            f'  <text class="tik" x="{x(v):.1f}" y="{Y_AXIS + 20:.0f}"{anchor} '
            f'data-claim="none">{txt}</text>')

    src1 = (f'Distribution across {pop["n_studies"]} studies, each counted once. '
            f'Box: 25th to 75th percentile. Whiskers: 10th ({p["p10"]}) '
            f'to 90th ({p["p90"]}); the longest ran to {d["max"]:,}.')
    # No "Virtual Lab production database" line. Nandan, 2026-08-26: "We are the ones
    # claiming the data. Nobody cares where it comes from." What stays is the DEFINITION
    # -- what an active day is, what the box spans -- because a reader cannot read this
    # figure without it. A definition is not an attribution. See check-claims.py,
    # "THE CITATION RULE".
    src2 = ('One reallocation is one pass over every stratum, resetting each budget from '
            'what the stratum currently costs and how far it is from its target share.')

    desc = (f'Budget reallocations per study, across {pop["n_studies"]} studies. The '
            f'median study takes {p["median"]}. The middle half of studies fall between '
            f'{p["p25"]} and {p["p75"]}. The tenth percentile is {p["p10"]} and the '
            f'ninetieth is {p["p90"]}, read against a scale running from {int(lo)} to '
            f'{int(hi)} reallocations; the longest study ran to {d["max"]:,}. This is a '
            f'distribution across studies, not an uncertainty interval on an estimate.')

    LAB_Y1 = 14 if narrow else Y_MID - 6
    LAB_Y2 = 30 if narrow else Y_MID + 12

    # Wrap the provenance lines and size the viewBox to hold them.
    src_svg, src_last_y = src_block(src1, src2, y0=Y_AXIS + 52, W=W)
    H = int(src_last_y + 10)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%"
     class="fig-realloc{" narrow" if narrow else ""}" role="img" aria-labelledby="reallocTitle reallocDesc"
     preserveAspectRatio="xMinYMin meet" data-claim-unit="">
  <title id="reallocTitle">Budget reallocations per study</title>
  <desc id="reallocDesc">{esc(desc)}</desc>

  <style>
    /* Local roles, resolved from DESIGN.md sec 3 tokens only. No literal colour. */
    .fig-realloc{{
      --realloc-data:  var(--data);
      --realloc-label: var(--ink);
      --realloc-rule:  var(--rule);
      --realloc-axis:  var(--ink-3);
      --realloc-src:   var(--ink-3);
    }}
    /* On an ink band. --data reads 2.10:1 and --ink-3 reads 4.00:1 there; see sec 3. */
    .fig-realloc.inv{{
      --realloc-data:  var(--data-inv);
      --realloc-label: var(--on-invert);
      --realloc-rule:  var(--rule-invert);
      --realloc-axis:  var(--on-invert-2);
      --realloc-src:   var(--on-invert-2);
    }}
    .fig-realloc .box    {{ fill: var(--realloc-data); fill-opacity:.26;
                        stroke: var(--realloc-data); stroke-width:1 }}
    .fig-realloc .cell   {{ fill: var(--realloc-data) }}
    .fig-realloc .whisk  {{ stroke: var(--realloc-data); stroke-width:1;
                        shape-rendering:crispEdges }}
    .fig-realloc .rule   {{ stroke: var(--realloc-rule); stroke-width:1;
                        shape-rendering:crispEdges }}
    .fig-realloc .axis   {{ stroke: var(--realloc-axis); stroke-width:1;
                        shape-rendering:crispEdges }}
    .fig-realloc .lab{{
      font:600 13px/1 "Source Sans 3","Helvetica Neue",Arial,sans-serif;
      fill: var(--realloc-label);
    }}
    .fig-realloc .num{{
      font:400 15px/1 "IBM Plex Mono",ui-monospace,monospace;
      font-variant-numeric: tabular-nums; letter-spacing:-.01em;
      fill: var(--realloc-data); text-anchor:middle;
    }}
    .fig-realloc .qnum{{
      font:400 12px/1 "IBM Plex Mono",ui-monospace,monospace;
      font-variant-numeric: tabular-nums;
      fill: var(--realloc-data); text-anchor:middle;
    }}
    .fig-realloc .tik{{
      font:500 9.5px/1 "IBM Plex Mono",ui-monospace,monospace;
      font-variant-numeric: tabular-nums; letter-spacing:.11em;
      text-transform:uppercase; fill: var(--realloc-axis);
    }}
    .fig-realloc .src{{
      font:italic 400 12px/1 "Source Serif 4",Georgia,serif;
      fill: var(--realloc-src);
    }}
  </style>

  <text class="lab" x="0" y="{LAB_Y1}">Budget reallocations</text>
  <text class="lab" x="0" y="{LAB_Y2}">per study</text>

  <!-- The values, above the interval they mark. C-089. -->
  <g data-claim="C-089">
    <text class="qnum" x="{x25:.1f}" y="{Y_MID - 20:.0f}">{p["p25"]}</text>
    <text class="num"  x="{x50:.1f}" y="{Y_MID - 20:.0f}">{p["median"]}</text>
    <text class="qnum" x="{x75:.1f}" y="{Y_MID - 20:.0f}">{p["p75"]}</text>
  </g>

  <!-- M3 interval. Bracket, bar, cell: three of the four primitives. -->
  <line class="whisk" x1="{x10:.1f}" y1="{Y_MID}" x2="{x25:.1f}" y2="{Y_MID}"/>
  <line class="whisk" x1="{x75:.1f}" y1="{Y_MID}" x2="{x90:.1f}" y2="{Y_MID}"/>
  <line class="whisk" x1="{x10:.1f}" y1="{Y_MID - CAP_H / 2}" x2="{x10:.1f}" y2="{Y_MID + CAP_H / 2}"/>
  <line class="whisk" x1="{x90:.1f}" y1="{Y_MID - CAP_H / 2}" x2="{x90:.1f}" y2="{Y_MID + CAP_H / 2}"/>
  <rect class="box" x="{x25:.1f}" y="{Y_MID - BOX_H / 2}" width="{x75 - x25:.1f}" height="{BOX_H}"/>
  <rect class="cell" x="{x50 - CELL / 2:.1f}" y="{Y_MID - CELL / 2}" width="{CELL}" height="{CELL}"/>

  <!-- M4 tick rule: the scale the interval is read against -->
  <line class="axis" x1="{PLOT_X0}" y1="{Y_AXIS}" x2="{PLOT_X1}" y2="{Y_AXIS}"/>
{chr(10).join(ticks)}
{chr(10).join(tick_labels)}

  <line class="rule" x1="0" y1="{Y_AXIS + 34:.0f}" x2="{W}" y2="{Y_AXIS + 34:.0f}"/>

  <!-- Provenance rule, DESIGN.md sec 2. Mandatory, same visual unit as the figure. -->
{src_svg}
</svg>
'''
    if not narrow:
        print(f"  box {p['p25']}-{p['p75']}, median {p['median']}, "
              f"whiskers {p['p10']}-{p['p90']}, n={pop['n_studies']} studies")
    return svg


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wide = render(1160, 180.0, 1104.0, 34.0, 58.0)
    OUT.write_text(wide)
    print(f"wrote {OUT}")
    # The narrow variant: label above, plot flush left, source lines rewrapped.
    narrow = render(480, 0.0, 468.0, 68.0, 92.0, narrow=True)
    NARROW_OUT.write_text(narrow)
    print(f"wrote {NARROW_OUT}")


if __name__ == "__main__":
    main()
