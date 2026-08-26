#!/usr/bin/env python3
"""Emit the DESIGN.md 7 icon set: twelve 24x24 inline SVGs plus a <symbol> sprite.

Geometry rules held constant across the set (see ws-icons.md):
  - viewBox 0 0 24 24; every coordinate on a 0.5 sub-grid
  - optical box x,y in [3,21]; square caps add 0.875 each end, so extremes land
    inside 2.125..21.875 and nothing clips
  - three-bar icons share rows y = 6 / 12 / 18
  - stroke 1.75, square caps, miter joins (round only on Survey, the thread)
"""
import os, re

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)))
REPO = "/home/nandan/Documents/vlab-research/vlab.digital"
DIR = os.path.join(REPO, "assets", "icons")

ROOT = ('fill="none" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="square" stroke-linejoin="miter"')
CELLS = 'fill="currentColor" stroke="none"'
THREAD = ('fill="none" stroke="currentColor" stroke-width="1.75" '
          'stroke-linecap="round" stroke-linejoin="round"')

def line(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'

def cell(x, y, w, h, op=None):
    o = f' fill-opacity="{op}"' if op is not None else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="currentColor" stroke="none"{o}/>'

def path(d):
    return f'<path d="{d}"/>'

# ---------------------------------------------------------------- the twelve
ICONS = []

def add(name, attrs, body):
    ICONS.append((name, attrs, body))

# 1 Stratify - three bars, descending lengths, left-anchored at x=4
add("stratify", ROOT, [
    line(4, 6, 20, 6),
    line(4, 12, 15.5, 12),
    line(4, 18, 11, 18),
])

# 2 Optimize - three bars + a full-height target tick at right (M2)
add("optimize", ROOT, [
    line(17.5, 3, 17.5, 21),          # target tick, same x for the whole stack
    line(4, 6, 17.5, 6),              # at target
    line(4, 12, 11.5, 12),            # under
    line(4, 18, 14.5, 18),            # under
])

# 3 Recruit - three centred bars narrowing downward
add("recruit", ROOT, [
    line(4, 6, 20, 6),
    line(6.5, 12, 17.5, 12),
    line(9, 18, 15, 18),
])

# 4 Survey - two offset rounded bars (M5 thread; the one rounded icon)
add("survey", THREAD, [
    '<rect x="3" y="4.5" width="12" height="6" rx="3"/>',
    '<rect x="9" y="13.5" width="12" height="6" rx="3"/>',
])

# 5 Weight - a rule carrying three cells of differing size, seated on it.
# 7 says "three dots of differing radius"; a circle is not one of the four
# primitives and stroked circles read as chain links at 24px. See ws-icons.md.
add("weight", ROOT, [
    line(3, 15.5, 21, 15.5),
    cell(3, 11.5, 3, 3),
    cell(7.5, 9.5, 5, 5),
    cell(14, 7.5, 7, 7),
])

# 6 Waves - a baseline with three verticals of differing height (M4)
add("waves", ROOT, [
    line(3, 19, 21, 19),
    line(6.5, 19, 6.5, 9),
    line(12, 19, 12, 5),
    line(17.5, 19, 17.5, 12),
])

# 7 Open source - two facing brackets
add("open-source", ROOT, [
    path("M8.5 4 H5 V20 H8.5"),
    path("M15.5 4 H19 V20 H15.5"),
])

# 8 Precision - two rules, a centre cell, two end ticks
add("precision", ROOT, [
    line(4.5, 7.5, 4.5, 16.5),
    line(19.5, 7.5, 19.5, 16.5),
    line(4.5, 12, 9, 12),
    line(15, 12, 19.5, 12),
    cell(9.5, 9.5, 5, 5),
])

# 9 Coverage - six cells at two opacities (the one filled icon)
_cov = [(3, 6, 1), (9.5, 6, .4), (16, 6, 1),
        (3, 13, .4), (9.5, 13, 1), (16, 13, 1)]
add("coverage", CELLS, [cell(x, y, 5, 5, None if o == 1 else o) for x, y, o in _cov])

# 10 Monitor - an axis with a polyline
add("monitor", ROOT, [
    path("M4 3.5 V20 H21"),
    path("M6.5 14 L10.5 8.5 L14.5 15 L19 10"),
])

# 11 Export - a grid with one column rule emphasised (it runs past the frame)
add("export", ROOT, [
    line(4, 5.5, 20.5, 5.5),
    line(4, 12, 20.5, 12),
    line(4, 18.5, 20.5, 18.5),
    line(4, 5.5, 4, 18.5),
    line(15, 5.5, 15, 18.5),
    line(20.5, 5.5, 20.5, 18.5),
    line(9.5, 3, 9.5, 21),            # emphasised column rule
])

# 12 Interval - two brackets with two crossbars (M3)
add("interval", ROOT, [
    path("M6 5 H3.5 V19 H6"),
    path("M18 5 H20.5 V19 H18"),
    line(3.5, 10, 20.5, 10),
    line(7.5, 15, 16.5, 15),
])

# ---------------------------------------------------------------- emit
os.makedirs(DIR, exist_ok=True)
HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" '

for name, attrs, body in ICONS:
    doc = HEAD + attrs + '>\n  ' + '\n  '.join(body) + '\n</svg>\n'
    with open(os.path.join(DIR, name + ".svg"), "w") as f:
        f.write(doc)

sym = ['<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="display:none" aria-hidden="true">',
       '  <!-- Virtual Lab icon set, DESIGN.md 7. Inline this file into the document;',
       '       <use> across documents is not supported in Chrome or Safari. -->']
for name, attrs, body in ICONS:
    sym.append(f'  <symbol id="icon-{name}" viewBox="0 0 24 24" {attrs}>')
    sym += ['    ' + b for b in body]
    sym.append('  </symbol>')
sym.append('</svg>')
with open(os.path.join(DIR, "icons.svg"), "w") as f:
    f.write("\n".join(sym) + "\n")

print("wrote", len(ICONS), "icons +", os.path.join(DIR, "icons.svg"))
