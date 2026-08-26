#!/usr/bin/env python3
"""Build assets/figures/throughput-box.svg from scripts/data/throughput.json.

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
DATA = ROOT / "scripts" / "data" / "throughput.json"
OUT = ROOT / "assets" / "figures" / "throughput-box.svg"

# Geometry. Width matches assets/figures/mad-comparison.svg so the two figures sit
# on one page without a rescale being read into either.
W = 620
PLOT_X0, PLOT_X1 = 180.0, 564.0
Y_MID = 34.0          # the interval's centreline
BOX_H = 24.0          # the bar primitive
CELL = 12.0           # the median cell -- a cell, never a dot (sec 6 M3)
CAP_H = 18.0          # bracket height at each whisker end
Y_AXIS = 58.0         # M4 tick rule
H = 152


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
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
    v = int(lo)
    while v <= hi:
        major = v in ax["major_ticks"]
        tx = x(v)
        ticks.append(f'  <line class="axis" x1="{tx:.1f}" y1="{Y_AXIS}" '
                     f'x2="{tx:.1f}" y2="{Y_AXIS + (7 if major else 4)}"/>')
        v += ax["tick_every"]

    src1 = (f'Distribution across {pop["n_studies"]} studies, each at its own median '
            f'active day. Box: 25th to 75th percentile. Whiskers: 10th ({p["p10"]}) '
            f'to 90th ({p["p90"]}).')
    src2 = (f'An active day is a study-day recruiting at least 20 respondents; half of '
            f'studies have {d["median_active_days"]} or more. Virtual Lab production '
            f'database, August 2026.')

    desc = (f'Respondents recruited per study on a day of active recruitment, across '
            f'{pop["n_studies"]} studies. The median study recruits {p["median"]} on '
            f'such a day. The middle half of studies fall between {p["p25"]} and '
            f'{p["p75"]}. The tenth percentile is {p["p10"]} and the ninetieth is '
            f'{p["p90"]}, read against a scale running from {int(lo)} to {int(hi)} '
            f'respondents. This is a distribution across studies, not an uncertainty '
            f'interval on an estimate.')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%"
     class="fig-thru" role="img" aria-labelledby="thruTitle thruDesc"
     preserveAspectRatio="xMinYMin meet" data-claim-unit="">
  <title id="thruTitle">Respondents recruited per study on an active day</title>
  <desc id="thruDesc">{esc(desc)}</desc>

  <style>
    /* Local roles, resolved from DESIGN.md sec 3 tokens only. No literal colour. */
    .fig-thru{{
      --thru-data:  var(--data);
      --thru-label: var(--ink);
      --thru-rule:  var(--rule);
      --thru-axis:  var(--ink-3);
      --thru-src:   var(--ink-3);
    }}
    /* On an ink band. --data reads 2.10:1 and --ink-3 reads 4.00:1 there; see sec 3. */
    .fig-thru.inv{{
      --thru-data:  var(--data-inv);
      --thru-label: var(--on-invert);
      --thru-rule:  var(--rule-invert);
      --thru-axis:  var(--on-invert-2);
      --thru-src:   var(--on-invert-2);
    }}
    .fig-thru .box    {{ fill: var(--thru-data); fill-opacity:.26;
                        stroke: var(--thru-data); stroke-width:1 }}
    .fig-thru .cell   {{ fill: var(--thru-data) }}
    .fig-thru .whisk  {{ stroke: var(--thru-data); stroke-width:1;
                        shape-rendering:crispEdges }}
    .fig-thru .rule   {{ stroke: var(--thru-rule); stroke-width:1;
                        shape-rendering:crispEdges }}
    .fig-thru .axis   {{ stroke: var(--thru-axis); stroke-width:1;
                        shape-rendering:crispEdges }}
    .fig-thru .lab{{
      font:600 13px/1 "Source Sans 3","Helvetica Neue",Arial,sans-serif;
      fill: var(--thru-label);
    }}
    .fig-thru .num{{
      font:400 15px/1 "IBM Plex Mono",ui-monospace,monospace;
      font-variant-numeric: tabular-nums; letter-spacing:-.01em;
      fill: var(--thru-data); text-anchor:middle;
    }}
    .fig-thru .qnum{{
      font:400 12px/1 "IBM Plex Mono",ui-monospace,monospace;
      font-variant-numeric: tabular-nums;
      fill: var(--thru-data); text-anchor:middle;
    }}
    .fig-thru .tik{{
      font:500 9.5px/1 "IBM Plex Mono",ui-monospace,monospace;
      font-variant-numeric: tabular-nums; letter-spacing:.11em;
      text-transform:uppercase; fill: var(--thru-axis);
    }}
    .fig-thru .src{{
      font:italic 400 12px/1 "Source Serif 4",Georgia,serif;
      fill: var(--thru-src);
    }}
  </style>

  <text class="lab" x="0" y="{Y_MID - 6:.0f}">Respondents recruited</text>
  <text class="lab" x="0" y="{Y_MID + 12:.0f}">per active day</text>

  <!-- The values, above the interval they mark. C-089. -->
  <g data-claim="C-089">
    <text class="qnum" x="{x25:.1f}" y="14">{p["p25"]}</text>
    <text class="num"  x="{x50:.1f}" y="14">{p["median"]}</text>
    <text class="qnum" x="{x75:.1f}" y="14">{p["p75"]}</text>
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
  <text class="tik" x="{PLOT_X0}" y="{Y_AXIS + 20:.0f}" data-claim="none">0</text>
  <text class="tik" x="{x(250):.1f}" y="{Y_AXIS + 20:.0f}" text-anchor="middle" data-claim="none">250</text>
  <text class="tik" x="{PLOT_X1}" y="{Y_AXIS + 20:.0f}" text-anchor="end" data-claim="none">500 RESPONDENTS</text>

  <line class="rule" x1="0" y1="{Y_AXIS + 34:.0f}" x2="{W}" y2="{Y_AXIS + 34:.0f}"/>

  <!-- Provenance rule, DESIGN.md sec 2. Mandatory, same visual unit as the figure. -->
  <text class="src" x="0" y="{Y_AXIS + 52:.0f}" data-claim-source="">{esc(src1)}</text>
  <text class="src" x="0" y="{Y_AXIS + 68:.0f}" data-claim-source="">{esc(src2)}</text>
</svg>
'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg)
    print(f"wrote {OUT}")
    print(f"  box {p['p25']}-{p['p75']}, median {p['median']}, "
          f"whiskers {p['p10']}-{p['p90']}, n={pop['n_studies']} studies")


if __name__ == "__main__":
    main()
