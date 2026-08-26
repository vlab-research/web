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
    src2 = (f'Per respondent newly recruited, ${d["totals"]["spend_usd"]:,} over '
            f'{d["totals"]["new_respondents"]:,} respondents. Virtual Lab production '
            f'database, August 2026.')

    desc = (f'Advertising cost per respondent newly recruited, across {pop["n_studies"]} '
            f'studies. The median study pays ${p["median"]:.2f}. The middle half fall '
            f'between ${p["p25"]:.2f} and ${p["p75"]:.2f}. The tenth percentile is '
            f'${p["p10"]:.2f} and the ninetieth ${p["p90"]:.2f}, read against a scale '
            f'from $0 to ${int(hi)}. The full range runs ${d["min"]:.2f} to '
            f'${d["max"]:.2f}. Advertising spend only. This is a distribution across '
            f'studies, not an uncertainty interval on an estimate.')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%"
     class="fig-cost" role="img" aria-labelledby="costTitle costDesc"
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

  <text class="lab" x="0" y="{Y_MID - 6:.0f}">Advertising cost</text>
  <text class="lab" x="0" y="{Y_MID + 12:.0f}">per respondent</text>

  <!-- The values, above the interval they mark. C-091. -->
  <g data-claim="C-091">
    <text class="qnum" x="{x25:.1f}" y="14">${p["p25"]:.2f}</text>
    <text class="num"  x="{x50:.1f}" y="14">${p["median"]:.2f}</text>
    <text class="qnum" x="{x75:.1f}" y="14">${p["p75"]:.2f}</text>
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
  <text class="src" x="0" y="{Y_AXIS + 52:.0f}" data-claim-source="">{esc(src1)}</text>
  <text class="src" x="0" y="{Y_AXIS + 68:.0f}" data-claim-source="">{esc(src2)}</text>
</svg>
'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg)
    print(f"wrote {OUT}")
    print(f"  box ${p['p25']:.2f}-${p['p75']:.2f}, median ${p['median']:.2f}, "
          f"whiskers ${p['p10']:.2f}-${p['p90']:.2f}, n={pop['n_studies']} studies")


if __name__ == "__main__":
    main()
