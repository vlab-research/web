#!/usr/bin/env python3
"""Build assets/figures/ad-cost.svg from scripts/data/ad-cost.json.

The figure is M3 (interval) drawn on M4 (tick rule), from the four primitives only:
a bracket at each whisker end, a bar for the interquartile box, a cell for the median,
and ticks for the ruler. Same form as the throughput figure, deliberately -- speed and
cost read as one pair. No chart library, no literal colour -- hard rule 8 and
DESIGN.md sec 3.

Never hand-edit the SVG. Change this script or the data and re-run.

    python3 scripts/build-adcost-figure.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "scripts" / "data" / "ad-cost.json"
OUT = ROOT / "assets" / "figures" / "ad-cost.svg"
NARROW_OUT = ROOT / "assets" / "figures" / "ad-cost-narrow.svg"

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
    v = lo
    while v <= hi + 1e-9:
        major = v in ax["major_ticks"]
        tx = x(v)
        ticks.append(f'  <line class="axis" x1="{tx:.1f}" y1="{Y_AXIS}" '
                     f'x2="{tx:.1f}" y2="{Y_AXIS + (7 if major else 4)}"/>')
        v += ax["tick_every"]

    src1 = (f'Advertising spend only — not the incentive, not the survey platform, not our '
            f'fee. Distribution across {pop["n_studies"]} studies. Box: 25th to 75th '
            f'percentile. Whiskers: 10th (${p["p10"]:.2f}) to 90th (${p["p90"]:.2f}); '
            f'the range runs ${d["min"]:.2f} to ${d["max"]:.2f}.')
    # No "Virtual Lab production database" line -- see build-throughput-figure.py and
    # check-claims.py, "THE CITATION RULE". The scope clause in src1 stays and is the
    # load-bearing half: this figure is advertising spend and is never a price.
    src2 = (f'Per respondent newly recruited, ${d["totals"]["spend_usd"]:,} over '
            f'{d["totals"]["new_respondents"]:,} respondents.')

    desc = (f'Advertising cost per respondent newly recruited, across {pop["n_studies"]} '
            f'studies. The median study pays ${p["median"]:.2f}. The middle half fall '
            f'between ${p["p25"]:.2f} and ${p["p75"]:.2f}. The tenth percentile is '
            f'${p["p10"]:.2f} and the ninetieth ${p["p90"]:.2f}, read against a scale '
            f'from $0 to ${int(hi)}. The full range runs ${d["min"]:.2f} to '
            f'${d["max"]:.2f}. Advertising spend only. This is a distribution across '
            f'studies, not an uncertainty interval on an estimate.')

    LAB_Y1 = 14 if narrow else Y_MID - 6
    LAB_Y2 = 30 if narrow else Y_MID + 12

    # Wrap the provenance lines and size the viewBox to hold them.
    src_svg, src_last_y = src_block(src1, src2, y0=Y_AXIS + 52, W=W)
    H = int(src_last_y + 10)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%"
     class="fig-cost{" narrow" if narrow else ""}" role="img" aria-labelledby="costTitle costDesc"
     preserveAspectRatio="xMinYMin meet" data-claim-unit="">
  <title id="costTitle">Respondents recruited per study on an active day</title>
  <desc id="costDesc">{esc(desc)}</desc>

  <style>
    /* Local roles, resolved from DESIGN.md sec 3 tokens only. No literal colour. */
    .fig-cost{{
      --cost-data:  var(--data);
      --cost-label: var(--ink);
      --cost-rule:  var(--rule);
      --cost-axis:  var(--ink-3);
      --cost-src:   var(--ink-3);
    }}
    /* On an ink band. --data reads 2.10:1 and --ink-3 reads 4.00:1 there; see sec 3. */
    .fig-cost.inv{{
      --cost-data:  var(--data-inv);
      --cost-label: var(--on-invert);
      --cost-rule:  var(--rule-invert);
      --cost-axis:  var(--on-invert-2);
      --cost-src:   var(--on-invert-2);
    }}
    .fig-cost .box    {{ fill: var(--cost-data); fill-opacity:.26;
                        stroke: var(--cost-data); stroke-width:1 }}
    .fig-cost .cell   {{ fill: var(--cost-data) }}
    .fig-cost .whisk  {{ stroke: var(--cost-data); stroke-width:1;
                        shape-rendering:crispEdges }}
    .fig-cost .rule   {{ stroke: var(--cost-rule); stroke-width:1;
                        shape-rendering:crispEdges }}
    .fig-cost .axis   {{ stroke: var(--cost-axis); stroke-width:1;
                        shape-rendering:crispEdges }}
    .fig-cost .lab{{
      font:600 13px/1 "Source Sans 3","Helvetica Neue",Arial,sans-serif;
      fill: var(--cost-label);
    }}
    .fig-cost .num{{
      font:400 15px/1 "IBM Plex Mono",ui-monospace,monospace;
      font-variant-numeric: tabular-nums; letter-spacing:-.01em;
      fill: var(--cost-data); text-anchor:middle;
    }}
    .fig-cost .qnum{{
      font:400 12px/1 "IBM Plex Mono",ui-monospace,monospace;
      font-variant-numeric: tabular-nums;
      fill: var(--cost-data); text-anchor:middle;
    }}
    .fig-cost .tik{{
      font:500 9.5px/1 "IBM Plex Mono",ui-monospace,monospace;
      font-variant-numeric: tabular-nums; letter-spacing:.11em;
      text-transform:uppercase; fill: var(--cost-axis);
    }}
    .fig-cost .src{{
      font:italic 400 12px/1 "Source Serif 4",Georgia,serif;
      fill: var(--cost-src);
    }}
  </style>

  <text class="lab" x="0" y="{LAB_Y1}">Advertising cost</text>
  <text class="lab" x="0" y="{LAB_Y2}">per respondent</text>

  <!-- The values, above the interval they mark. C-091. -->
  <g data-claim="C-091">
    <text class="qnum" x="{x25:.1f}" y="{Y_MID - 20:.0f}">${p["p25"]:.2f}</text>
    <text class="num"  x="{x50:.1f}" y="{Y_MID - 20:.0f}">${p["median"]:.2f}</text>
    <text class="qnum" x="{x75:.1f}" y="{Y_MID - 20:.0f}">${p["p75"]:.2f}</text>
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
  <text class="tik" x="{PLOT_X0}" y="{Y_AXIS + 20:.0f}" data-claim="none">$0</text>
  <text class="tik" x="{x(2):.1f}" y="{Y_AXIS + 20:.0f}" text-anchor="middle" data-claim="none">$2</text>
  <text class="tik" x="{PLOT_X1}" y="{Y_AXIS + 20:.0f}" text-anchor="end" data-claim="none">$4 PER RESPONDENT</text>

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
