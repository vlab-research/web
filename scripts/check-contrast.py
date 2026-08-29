#!/usr/bin/env python3
"""Verify every colour pair in DESIGN.md meets its stated WCAG contrast target.

Run before publishing anything that introduces a new colour pairing:

    python3 scripts/check-contrast.py

Exists because this bug already shipped once: brass on an ink band measured 2.43:1
in light mode and looked perfect in dark mode. See DESIGN.md §3.

Checks both palettes. The site itself serves only light (D-028); the dark palette is
kept dormant and verified so that restoring it stays a one-block edit.
"""
import sys

LIGHT = {
    "paper": "#F1F4F5", "surface": "#FFFFFF", "sunk": "#E5EBED", "invert": "#1F272E",
    "ink": "#1F272E", "ink-2": "#4A555E", "ink-3": "#79858D",
    "brass": "#7A5C1E", "data": "#1D5F6E",
    "on-invert-2": "#A9B8BF", "brass-inv": "#C9A250", "data-inv": "#4E9DB0",
    "ink-3-on-band": "#79858D", "data-raw": "#1D5F6E",
}
# Still checked although the site no longer serves dark: D-028 left the palette
# dormant rather than deleting it, on the condition that it stay verified. Do not
# "clean this up" because no page renders it — scripts/build-review.py does, and
# an unchecked palette makes restoring dark a re-design instead of a one-block edit.
DARK = {
    "paper": "#13181C", "surface": "#1C2227", "sunk": "#262E34", "invert": "#0C1013",
    "ink": "#E6EBEE", "ink-2": "#B2BEC6", "ink-3": "#808E97",
    "brass": "#C9A250", "data": "#4E9DB0",
    "on-invert-2": "#94A3AB", "brass-inv": "#C9A250", "data-inv": "#4E9DB0",
    "ink-3-on-band": "#808E97", "data-raw": "#4E9DB0",
}

# (foreground, background, minimum ratio, note)
# 4.5 = AA normal text · 3.0 = AA large text / non-text
PAIRS = [
    ("ink",         "paper",  4.5, "body text"),
    ("ink-2",       "paper",  4.5, "secondary prose"),
    ("ink-3",       "paper",  3.0, "eyebrows, captions, axis labels only"),
    ("brass",       "paper",  4.5, "links, kickers"),
    ("data",        "paper",  4.5, "data labels"),
    ("brass",       "surface",4.5, "links on a card"),
    ("paper",       "ink",    4.5, ".btn.pri label"),
    ("brass-inv",   "invert", 4.5, "brass on an ink band - NOT --brass, see DESIGN.md §3"),
    ("on-invert-2", "invert", 4.5, "prose on an ink band"),
    ("data-inv",    "invert", 4.5, "data on an ink band - NOT --data, which is 2.10:1"),
    ("on-invert-2", "invert", 4.5, "source line on an ink band - NOT --ink-3, which is 4.00:1"),

    # css/docs.css. Documentation adds two grounds the marketing page never uses:
    # --surface under code, and --sunk under callouts. D-029.
    ("ink",         "surface",4.5, "code, and search result titles"),
    ("ink-2",       "surface",4.5, "code punctuation, operators and comments"),
    ("data",        "surface",4.5, "code literals - on --sunk this is 4.45:1 in dark, which is why code sits on --surface"),
    ("ink-3",       "surface",3.0, "search result sub-line - a label, not prose"),
    ("ink",         "sunk",   4.5, "bold text inside a callout"),
    ("ink-2",       "sunk",   4.5, "callout body text"),
    ("ink-3",       "sunk",   3.0, "callout label - eyebrow treatment, label minimum"),
    ("brass",       "sunk",   4.5, "warning callout label"),
]


def luminance(hex_colour):
    h = hex_colour.lstrip("#")
    chans = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in chans]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def ratio(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def main():
    failures = []
    for theme_name, theme in (("light", LIGHT), ("dark", DARK)):
        print(f"\n{theme_name.upper()}")
        for fg, bg, minimum, note in PAIRS:
            r = ratio(theme[fg], theme[bg])
            ok = r >= minimum
            mark = "ok  " if ok else "FAIL"
            print(f"  {mark} --{fg} on --{bg}: {r:5.2f}:1  (min {minimum})  {note}")
            if not ok:
                failures.append((theme_name, fg, bg, r, minimum, note))

    print()
    if failures:
        print(f"{len(failures)} failing pair(s):")
        for theme_name, fg, bg, r, minimum, note in failures:
            print(f"  [{theme_name}] --{fg} on --{bg} = {r:.2f}:1, needs {minimum}:1 — {note}")
        print("\nFix the token in DESIGN.md and in the stylesheet, then re-run.")
        return 1
    print("All pairs pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
