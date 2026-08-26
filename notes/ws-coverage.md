# Proposed doc edits — coverage build workstream (D-018 drift)

Written to the scratchpad rather than applied, because other agents hold
`AGENTS.md` / `DESIGN.md` / `DECISIONS.md` / `CLAIMS.md` concurrently. Apply verbatim,
or close enough.

**What shipped:** `scripts/build-coverage-map.py` now emits all three artefacts of the
coverage section from `scripts/data/coverage.json` in one run, with `--help`:

```
build/coverage-map.html      cropped choropleth · six-state legend · source line
build/coverage-strip.html    respondents-by-region bar · source line
build/coverage-regions.html  region-totals cells · source line · floors note
```

No new dependency; Python 3 stdlib only. Review page:
`scratchpad/specimen-coverage.html` (+ `specimen-{light,dark,unstamped}.png`).

**No number changed.** Every figure the script emits reproduces the published record
exactly: 311,363 / 143,816 / 136,558 / 113,460 / 30,573 / 2,838, summing to 738,608 of
841,660. What changed is that they are now computed rather than typed.

---

## 1. `AGENTS.md` — "Known drift", delete the first bullet

The drift is closed.

```diff
-- **The region strip is not in the build script.** `scripts/build-coverage-map.py` emits
-  only the map; the strip was generated in a scratch session and is gone. Fold it in so
-  one command builds both from `scripts/data/coverage.json`.
```

## 2. `AGENTS.md` — verification checklist, tighten one line

The script no longer only warns; a country it cannot draw now exits **2**, so the
checklist item can be enforced by a runner rather than by a human reading stderr.

```diff
-- [ ] `python3 scripts/build-coverage-map.py` runs clean if coverage data changed
-      (it warns on stderr for any country it cannot draw — never ignore that)
+- [ ] `python3 scripts/build-coverage-map.py` runs clean if coverage data changed
+      (it exits non-zero and prints a banner for any country it cannot draw, or for
+      a country that is in no region or in two — never ignore either)
```

## 3. `AGENTS.md` — "Things about this repo…", add one line

```diff
+- **`build/` is generated.** `scripts/build-coverage-map.py` writes there. It is not
+  committed; add `build/` to `.gitignore` when one exists (there is no `.gitignore`
+  in this repo at all yet, which is its own small problem).
```

## 4. `DESIGN.md` §8 — replace the "Coverage map" component with "Coverage section"

The settled component is three parts, not one, and §8 currently describes only the map.
Two substantive corrections are folded in, both flagged below the diff.

```diff
-### Coverage map
+### Coverage section
+
+Three artefacts, always built together by `scripts/build-coverage-map.py` from
+`scripts/data/coverage.json`. Never hand-edit the output; refresh the data and re-run.
+
+**1 · Map.** Cropped choropleth, per D-018. Covered countries fill `--data` at five
+opacity steps by order of magnitude (`.26 / .40 / .56 / .76 / 1`); everything else is a
+`--rule` hairline at `.7`; countries covered but not counted are a dashed `--data`
+outline, **never a zero fill**. Frame is the bounding box of covered countries.
+
+The legend names all six states, and the five step labels are **thresholds by order of
+magnitude, not round marketing numbers**: `under 100 · 100+ · 1,000+ · 10,000+ ·
+100,000+`, plus `covered, count pending`. Generate them; do not write them by hand.
+
+**2 · Region strip.** One horizontal bar (M2 without a target tick), regions largest
+first. Segment **width** carries the value; segment **opacity** carries the rank, on a
+six-step ramp `.95 / .78 / .62 / .48 / .34 / .22` over a `--rule` ground showing through
+as 1px gaps. Height 30px, full width, `preserveAspectRatio="none"`.
+
+**3 · Region totals.** Six cells, 1px gaps over `--rule`, top and bottom rules — the
+stat row at region scale. Number in Plex Mono `clamp(22px,2.2vw,28px)`, region in mono
+uppercase `--ink-2`, country count in Source Serif italic `--ink-3`. A region containing
+a country with no count carries `floor — N not yet counted` in `--brass` **in the cell**,
+and the block below it explains why in prose.
+
+**The bar and the cells span the attributed respondents, not the whole.** 103,052 of
+841,660 belong to studies whose strata carry no country tag (`CLAIMS.md`). Each of the
+three source lines states its own denominator; none of them may imply the regions sum to
+the headline figure.
 
-Cropped choropleth, per D-018. Covered countries fill `--data` at five opacity steps by
-order of magnitude (`.26 / .40 / .56 / .76 / 1`); everything else is a `--rule` hairline
-at `.7`; countries covered but not counted are a dashed `--data` outline, **never a zero
-fill**. Frame is the bounding box of covered countries. Legend names all six states.
-Source line mandatory, as for any figure.
-
-Built by `scripts/build-coverage-map.py`, which emits inline SVG referencing tokens only,
-so it inherits the theme. Never hand-edit the output; refresh the data and re-run.
+Source line mandatory on each of the three, as for any figure. All colour is `var(--…)`
+— there is no literal hex anywhere in the emitted markup, so all three inherit the page
+theme and hold in all three theme states.
```

**Correction A — the published legend labels were wrong.** The record read
`under 1,000 · 1,000+ · 10,000+ · 50,000+ · 100,000+`. The code that fills the map has
always been `int(log10(v))` clamped to 1–5, so the true steps are
`under 100 · 100+ · 1,000+ · 10,000+ · 100,000+`. Under the old labels, Germany (23) and
Ireland (206) sat in a bucket labelled "under 1,000" at two different opacities, and
every country from 1,000 to 9,999 — twenty of the forty-one, the largest bucket — was
labelled "10,000+". The labels are now generated from `magnitude()`, so they cannot drift
again. **This is the one place where the rebuild does not match the record, because the
record was wrong.**

**Correction B — the strip's source line conflated two different gaps.** The record read
"Regional figures cover 738,608 of 841,660 respondents; four countries are covered but
not yet counted and contribute nothing to the totals above." Those two clauses sit next
to each other and the missing 103,052 is *not* the four pending countries — it is the
unattributed studies. A reader would reasonably conclude Palestine, Moldova, North
Macedonia and Kosovo account for 103,052 respondents. The emitted line now names each
gap separately.

## 5. `DECISIONS.md` D-021 — this work bears on both open questions

Neither needs reopening; both now have a worked example to point at.

- **Item 1, "should M2 require a real target?"** The region strip is a bar with **no**
  target tick, because there is no target for "respondents by region" — nothing to
  compare an achieved fill against. It looks right without one, which is the practical
  case for extending the M3 rule to M2. **Nothing to decide differently; the
  recommendation holds and the strip is evidence for it.**
- **Item 2, "does the lattice hold at other scales?"** Not exercised. The rebuilt strip
  uses no lattice at all — the 5.6/12.6 pitch cited in D-021 came from the scratch
  session's ink-band treatment, which did not survive into the settled section. The
  question is still worth answering, but nothing in the current build depends on it.

## 6. Proposed new entry — `D-022`, one question this work could not settle alone

```
### D-022 — Should the region strip show the unattributed respondents?
**Status:** OPEN · Owner: Nandan · *low stakes*

The strip spans the 738,608 respondents attributable to a country. The other 103,052
(12.2%) belong to studies whose strata carry no country tag. Today the bar is 100%
"attributed" and the gap is named only in the source line beneath it.

**Options:** leave it as built (gap in prose only); or add a sixth-and-a-bit segment in
`--rule` with a dashed `--data` edge — the same treatment the map already gives coverage
without a count — labelled "not attributed to a country".

**Recommendation:** leave as built for now. The ghost segment is more honest at a glance
but it puts an eighth of the strip into a category a buyer cannot act on, and it invites
the reading that we lost track of those respondents rather than that they were recruited
without country strata. Revisit if the strip ever appears without its source line.
```

## 7. `CLAIMS.md` — no change needed

Everything the section renders traces to the Production figures section: C-010
(841,660), C-017 (41 countries, per-country table), the four pending countries, and the
"Two limits on this table" paragraph for the 103,052. The per-region totals are sums of
C-017 rows, computed at build time rather than stored, so there is nothing new to add a
row for.

---

## Restored, not reconstructed — with four deliberate deviations

The published Artifact `ce3dbf66-d7e4-4616-82bf-31e3515ee5e8` fetched cleanly and the
strip and totals are rebuilt from it, not re-imagined. Every geometry constant, class
name, opacity and CSS declaration below the fold is the record's. The four deviations:

1. **The strip bar is inline SVG, not flex `<div>`s.** The record drew it with
   `display:flex` and `flex:42.1554`. Hard rule 8 says all graphics are inline SVG, and
   the brief requires the emitted SVG to reference tokens only. Same geometry, same
   1px `--rule` gaps, same ramp; `preserveAspectRatio="none"` so it stretches. The
   totals cells stay HTML — they are the stat row at region scale, not a drawing.
2. **Legend labels corrected** (Correction A above).
3. **Source lines rewritten** to separate the two gaps (Correction B above).
4. **`floor — N not yet counted`** in the affected cells; the record said
   `N not yet counted` and left the word "floor" to the note block. `_regions_note` says
   to say so on the page, and the cell is the page.

Map tooltips now name the country ("Jordan — 79,915 respondents") instead of the ISO-2
code. The map geometry, cropping, opacity steps and ghost borders are byte-for-byte the
same treatment as before — D-018 was not touched.
