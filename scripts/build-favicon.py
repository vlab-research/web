#!/usr/bin/env python3
"""Build assets/favicon.ico and assets/apple-touch-icon.png from assets/favicon.svg.

assets/favicon.svg is the SOURCE; the other two are derived and must never be edited
by hand. Written 2026-08-26, when the favicon changed motif -- before this the three
files were hand-made and nothing tied them together, so they could silently disagree.

    python3 scripts/build-favicon.py

THE FAVICON IS M1, THE CELL LATTICE, NOT M2. It was a bar and target tick on an ink
tile until 2026-08-26. Nandan: "That one doesn't really fit the visual style of the
page." Two things were wrong and only the first was obvious:

  1. The tab showed M2 while the mark beside the wordmark, two centimetres below,
     showed M1. Different motifs for the same company.
  2. Louder, and the reason it read as foreign: an ink tile carrying BOTH teal and
     brass made it the most saturated object in the whole system, on a site whose
     first screen has no filled colour on it at all and whose mark is a bare ink
     glyph on paper.

What replaced it is not a new lock-up. It is the FOOTER lock-up -- ink band,
on-invert lattice, beside the wordmark -- cropped square. Same nine cells and the
same five-at-target pattern as assets/mark.svg.

Geometry is chosen for the 16px grid and should not be nudged: cell 8, gap 2, margin
2 in a 32 viewBox, so at 16px every cell is exactly 4 device px and every gap exactly
1. No half-pixels. Changing any of those four numbers reintroduces them.

A favicon has NO THEME CONTEXT to inherit -- it cannot use custom properties or a
media query -- so it carries its own ground and uses only the tokens whose value is
identical in both themes: --invert #1F272E and --on-invert #EDF1F2 (DESIGN.md 3).
Under-target cells are that same token at reduced alpha, exactly as mark.svg does;
no second hue exists in the file.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "favicon.svg"
ICO = ROOT / "assets" / "favicon.ico"
TOUCH = ROOT / "assets" / "apple-touch-icon.png"

# The three sizes a .ico is actually read at: tab, bookmark bar, Windows shortcut.
ICO_SIZES = (16, 32, 48)
TOUCH_SIZE = 180

# Only these may appear in the source. A favicon cannot resolve a token at runtime,
# so these are the literal values -- and they are the two whose value is IDENTICAL in
# both themes, which is why no others are permitted here.
ALLOWED = {"#1F272E", "#EDF1F2"}


def render(size, out):
    """rsvg-convert rather than a rasteriser that anti-aliases the grid into mush.
    The geometry is whole device pixels at every size below, so the edges stay hard."""
    subprocess.run(
        ["rsvg-convert", "-w", str(size), "-h", str(size), "-o", str(out), str(SRC)],
        check=True)


def main():
    import re
    import tempfile
    from PIL import Image

    svg = SRC.read_text()
    found = {c.upper() for c in re.findall(r'#[0-9A-Fa-f]{6}', svg)}
    if not found <= ALLOWED:
        sys.exit(f"FAIL: {SRC.name} uses colours outside the both-theme tokens: "
                 f"{sorted(found - ALLOWED)}. A favicon has no theme to inherit, so "
                 f"only {sorted(ALLOWED)} are permitted. See DESIGN.md sec 3.")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        frames = []
        for s in ICO_SIZES:
            p = tmp / f"{s}.png"
            render(s, p)
            frames.append(Image.open(p).convert("RGBA"))
        # Pillow writes every size into one .ico from the largest frame.
        frames[-1].save(ICO, format="ICO",
                        sizes=[(s, s) for s in ICO_SIZES])
        render(TOUCH_SIZE, TOUCH)

    print(f"wrote {ICO.relative_to(ROOT)}  ({', '.join(f'{s}x{s}' for s in ICO_SIZES)})")
    print(f"wrote {TOUCH.relative_to(ROOT)}  ({TOUCH_SIZE}x{TOUCH_SIZE})")
    print(f"  source {SRC.relative_to(ROOT)}, M1 cell lattice, colours {sorted(found)}")


if __name__ == "__main__":
    main()
