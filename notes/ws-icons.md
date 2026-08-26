# ws-icons — icon set, mark, favicon

Workstream note. **Proposed doc edits only — nothing here has been written into
`DESIGN.md`, `DECISIONS.md`, `AGENTS.md`, `CLAIMS.md` or `CONTENT.md`.** Other agents
were working in those files concurrently.

## What shipped

| Path | What |
|---|---|
| `assets/icons/*.svg` | the twelve icons, one file each, 24×24 |
| `assets/icons/icons.svg` | `<symbol>` sprite of all twelve, ids `#icon-<slug>` |
| `assets/mark.svg` | the nav mark, 22px, nine cells, five filled |
| `assets/favicon.svg` | favicon, motif M2 on an ink tile |
| `assets/favicon.ico` | 16 / 32 / 48 packed |
| `assets/apple-touch-icon.png` | 180×180, opaque, square (iOS applies its own mask) |

Specimen: `scratchpad/specimen-icons.html`.
Generator (not promoted to `scripts/`, see "Open question" below):
`scratchpad/build-icons.py` — defines all twelve geometrically in one table and emits
both the individual files and the sprite, so the two cannot drift.

## The grid

- `viewBox="0 0 24 24"`. **Every coordinate is a multiple of 0.5.** No exceptions in
  any of the twelve.
- Content lives in an **18×18 optical box, x and y in [3, 21]**. Square caps add
  0.875 at each end, so the outermost rendered pixel is 2.125 / 21.875 and nothing
  ever touches the viewBox edge.
- Three-bar icons (Stratify, Optimize, Recruit) share **rows y = 6 / 12 / 18**.
- Stroke 1.75, `stroke-linecap="square"`, `stroke-linejoin="miter"`,
  `stroke="currentColor"`, `fill="none"` — except Coverage, which is the cells icon
  and is `fill="currentColor" stroke="none"`, and Survey, which is the thread and is
  the set's only `round` cap/join.
- No `<title>`; decorative use carries `aria-hidden="true"` at the call site.
- No colour literal anywhere in the icon set or the mark. The favicon is the one file
  with hexes in it, and every one is a token value — see below.

## Where §7 did not survive contact with the grid

Nothing had to reach outside the four primitives, so **no concept was flagged as not
belonging on the page**. But four things in §7/§8 are wrong as written, and drawing
them is what exposed it.

### 1 · "Dots" are not a primitive. §7 Weight and §7 Precision both call for one.

§7 specifies *Weight* as "a rule with three **dots** of differing radius" and
*Precision* as "two rules, **a centre dot**, two end ticks". A circle is not one of
the four primitives (bar, tick, cell, bracket), and §6/§10 and `AGENTS.md` rule 8 are
absolute about that. It is not a pedantic point: I drew the circle version, and at
24px three stroked circles on a rule read as **chain links**, not as weights.

Both are drawn with **square cells** instead. A cell is a primitive, it is the same
form the lattice is made of, and it holds at 24px.

> **Proposed §7 edit.** Weight: "A rule carrying three cells of differing size."
> Precision: "Two rules, a centre cell, two end ticks."
> **Proposed §6 M3 edit.** M3 is written as `├──●──┤`. If the dot is a cell in the
> icon it should be a cell in the motif too, or the two drift. Recommend `├──■──┤`.

### 2 · Weight does not work with the cells centred on the rule.

Even as cells, "three of differing size, threaded on a rule" produces a squat
horizontal object 6 units tall in a 24-unit box that reads as a **bolt or a dart** —
monotone growth joined by a line. Eight variants were rendered at 24 and 56px
(`scratchpad/weight-variants.html`); every centred one failed.

Shipped construction: the three cells (3 / 5 / 7) are **seated on the rule**, bottoms
aligned, rule extending past them at both ends. It reads immediately as mass on a
beam. It is still one bar plus three cells.

> **Proposed §7 edit.** Weight: "A rule with three cells of differing size seated on
> it, ascending."

Risk to watch: Weight now shares a silhouette family with *Waves* (a baseline with
three verticals). They are distinguished by fill — Waves is hairline strokes reaching
much higher, Weight is solid cells in the lower band. If both ever appear in the same
row, revisit.

### 3 · The nav mark cannot use the M1 lattice ratio. This bears on D-021.

§6 fixes the lattice at cell 8 / pitch 18 and says "do not alter the ratio"; §6 lists
"the mark" among M1's uses; §8 sets the mark at 22px, nine cells.

Those three are not jointly satisfiable at a legible size. Nine cells at 4:9 in a
22px box gives **cell 4, pitch 9** (2×9 + 4 = 22 exactly — which is almost certainly
why 22px was chosen). Rendered, it is a scatter of 4px dots lost in whitespace: it
reads as faint texture beside the wordmark and it is gone at 16px.

Shipped: **cell 6, pitch 8** (3:4), which also lands exactly on 22 and holds down to
12px. Five variants were rendered side by side at 16 / 22 / 44px
(`scratchpad/mark-variants.html`).

The distinction I would write into the doc: **4:9 is a *tiling* ratio.** It governs
the lattice as a background field, where the cells must disappear at a glance. The
mark is a discrete object of nine cells that must survive at 16px, and it needs its
own ratio.

> **Proposed §6 M1 edit.** "Cell 8, pitch 18 — the 4:9 ratio is fixed wherever the
> lattice is used as a *field*; the pitch is free (the coverage map uses 5.6 / 12.6).
> The nav mark is not a field: it is nine discrete cells at cell 6 / pitch 8."
> **This is D-021 question 2 and it now has an answer with a rendering behind it.**
> D-021 recommends "the ratio is fixed, the pitch is not"; that recommendation is
> right for fields and wrong for the mark.

### 4 · M2's hatch does not exist at 16px, so the favicon drops it.

§6 M2 requires under-target to be hatched brass *and* brass-hued — "hue and pattern
both encode the state", redundantly, so it survives greyscale. At 16px a 3px-period
135° hatch is sub-pixel; it renders as flat brass at best and as mud at worst.

The favicon keeps the redundancy by a different second channel: the under-target bar
is brass **and stops visibly short of the target tick**, while the on-target bar
reaches it. Length is the encoding M2 is actually about. Verified by rasterising to
true 16px and inspecting at 9× nearest-neighbour.

> **Proposed §6 M2 edit.** "Below ~24px the hatch is dropped; state is carried by hue
> and by the bar's length against the tick."

## Decisions I made where §7 was silent

- **Optimize** — the three bars are deliberately **non-monotonic** (17.5 / 11.5 /
  14.5) so the icon cannot be mistaken for Stratify's descending stack. It also makes
  the tick do work: two cells are short of target, one is at it.
- **Precision vs Interval.** As specified these are near-duplicates — both are a
  horizontal span with end markers. Shipped: *Precision* is a **short, centred** span
  with a prominent 5×5 centre cell and vertical end ticks; *Interval* is a **wide**
  bracketed frame with **two crossbars of different width** (a wide estimate and a
  tight one), which is M3's actual job — benchmark comparison.
- **Export** — "one column rule emphasised" cannot be done with weight (stroke is
  fixed at 1.75) or colour (one `currentColor`). The emphasised rule is emphasised by
  **extension**: it runs past the frame top and bottom while the other three stop at
  it.
- **Coverage** — the "two opacities" are **1 and .4**, matching two steps of the
  coverage map's `.26 / .40 / .56 / .76 / 1` scale rather than inventing a value.
  Four cells full, two at .4, in a pattern with no row or column uniform.
- **Monitor** — the polyline ends mid-height, not high right, so it cannot read as
  the upward-right arrow §6 bans.
- **Mark fill pattern** — row 0 `■ ■ □`, row 1 `■ □ ■`, row 2 `□ ■ □`. Five filled.
  Every row and every column carries at least one cell at target and none is
  complete, so it reads as a design mid-field rather than as ornament; it has no
  rotational symmetry, which keeps it identifiable rather than decorative. Unfilled
  cells are drawn at `fill-opacity .28` — nine cells exist, five are filled, as §8
  says; at 16px the four ghosts read as the lattice doing its usual job.

## Two things to flag rather than fix

- **Recruit** is "three centred bars narrowing downward" (§7) and §6 bans "funnels
  narrowing to a coin". I built §7's version. The banned thing is the *coin* — the
  conversion metaphor — and three centred bars read as a population narrowing to a
  sample, which is the true mechanism. But the two lines are adjacent enough that
  someone should say so out loud in the doc.
- **D-021 question 1** ("should M2 require a real target, as M3 requires a real
  interval?") applies to the *Optimize* icon: its target tick is decorative, because
  an icon has no data. If D-021.1 is adopted as written, it bans the icon §7 asks
  for. Recommend the rule be scoped to **figures**, not icons — an icon is a glyph of
  a mechanism, not a reading of one.

## One build note

`<use href="external.svg#id">` does **not** work cross-document in Chrome or Safari.
`assets/icons/icons.svg` is therefore written to be **inlined into the page** (it is
`width="0" height="0" style="display:none" aria-hidden="true"` so it can be dropped
straight after `<body>`), after which `<use href="#icon-stratify"/>` works. This is
also what `AGENTS.md` rule 8 wants — all graphics inline.

Also: **`--` cannot appear inside an XML comment.** The first favicon draft named the
tokens `--invert`, `--data-inv` etc. in its header comment; browsers tolerated it,
`rsvg-convert` refused to parse the file. Token names in SVG comments are written
without the leading dashes.

## Rasterisation — what was generated and how

Tooling was present (`rsvg-convert` 2.x, ImageMagick 7), so the rasters were built
rather than described:

```sh
# favicon.ico — 16 / 32 / 48, from the rounded tile
for s in 16 32 48; do rsvg-convert -w $s -h $s assets/favicon.svg -o ico-$s.png; done
magick ico-16.png ico-32.png ico-48.png -strip assets/favicon.ico

# apple-touch-icon — 180x180, square and fully opaque; iOS applies its own mask,
# so the 2px radius is removed and the alpha flattened onto --invert
sed 's/ rx="2"//' assets/favicon.svg > favicon-square.svg
rsvg-convert -w 180 -h 180 favicon-square.svg -o at180.png
magick at180.png -background '#1F272E' -alpha remove -alpha off -strip PNG32:assets/apple-touch-icon.png
```

If a web manifest is added in Phase 4 it will also want 192 and 512 PNGs from
`favicon-square.svg`; they were not generated because nothing references them yet.

Head markup for Phase 4:

```html
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/favicon.ico" sizes="16x16 32x32 48x48">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
```

## Open question for the user

Should `build-icons.py` be promoted to `scripts/build-icons.py`? The coverage map has
the precedent — "never hand-edit the output; refresh the data and re-run" — and the
same argument applies here: the sprite is derived from the twelve, and a hand edit to
one file silently desynchronises them. It was left in the scratchpad because adding a
file to `scripts/` while three agents are working was not mine to decide.
