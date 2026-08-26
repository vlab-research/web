# Proposed doc edits — font kit workstream (D-012)

Written to the scratchpad rather than applied, because other agents hold
`DESIGN.md` / `DECISIONS.md` / `AGENTS.md` concurrently. Apply verbatim, or close
enough.

**What shipped:** `fonts/` at the repo root (12 woff2 files, 264.6 kB) and
`css/fonts.css` (14 `@font-face` rules). No build step, no dependency added.

---

## 1. `DECISIONS.md` — D-012, replace the "How" table

The table lists what was absent as of 2026-08-20. All of it is now present.

```diff
-**How.** *Corrected 2026-08-20 — less already exists than the original note claimed.*
-`../proposals/src/vlab_proposals/static/fonts/` holds three of the four families, but
-not the weights `DESIGN.md` §4 actually specifies:
+**How.** *Fetched 2026-08-20.* The kit now lives in `fonts/` at the repo root and is
+declared in `css/fonts.css`. Nothing is loaded from a Google origin at runtime:
 
-| Face | Weight needed | For | Present? |
-|---|---|---|---|
-| Zilla Slab | 300 | Display, wordmark | Yes — `ZillaSlab-Light` |
-| Zilla Slab | 400 | `h3`, study-card titles, client wall | **No** |
-| Source Sans 3 | 400 | Body, UI, nav | **No** — only `Bold` (700) is there |
-| Source Sans 3 | 600 | Buttons | **No** |
-| Source Serif 4 | 400 | Abstracts, source lines | Yes |
-| IBM Plex Mono | 400, 500 | Every numeral, eyebrows, labels | **No** |
-
-**Five faces to fetch, not one.** Source Serif 4 300 and 700 are also present and are
-not in the spec — do not carry them over. Subset to latin + latin-ext, serve from our
-own origin with `font-display: swap`.
+| Face | Weight | For | File(s) in `fonts/` | Source |
+|---|---|---|---|---|
+| Zilla Slab | 300 | Display, wordmark | `ZillaSlab-300-{latin,latin-ext}` | Copied from proposals — byte-identical to Google's current file |
+| Zilla Slab | 400 | `h3`, study-card titles, client wall | `ZillaSlab-400-{latin,latin-ext}` | Fetched |
+| Source Sans 3 | 400, 600 | Body, UI, nav, buttons | `SourceSans3-400-600-{latin,latin-ext}` | Fetched — **variable file, one per subset, both weights** |
+| Source Serif 4 | 400 | Abstracts, source lines | `SourceSerif4-400-{latin,latin-ext}` | Copied from proposals |
+| IBM Plex Mono | 400 | Numerals, table cells, code | `IBMPlexMono-400-{latin,latin-ext}` | Fetched |
+| IBM Plex Mono | 500 | Eyebrows, labels, stat numerals | `IBMPlexMono-500-{latin,latin-ext}` | Fetched |
+
+264.6 kB total across latin + latin-ext; 127.4 kB is the latin half, which is all a
+normal English page fetches. Source Serif 4 300/700 and Source Sans 3 Bold exist in the
+proposals directory, are not in §4, and were **not** carried over. Adding a weight is a
+`DESIGN.md` §4 change first.
+
+**Two things to know before touching this.** Google publishes Source Sans 3 only as a
+variable font — there is no static instance to fetch and no subsetter installed here, so
+one file per subset carries the weight axis (it has an `fvar` table; the exact axis range
was not read, only that both weights resolve from it) and two `@font-face` rules point at
+it. It is also the smaller option: 28.7 kB of variable latin serves both weights where
+two statics would be ~32 kB. And the `unicode-range` values in `css/fonts.css` are
+Google's own latin / latin-ext partitions copied verbatim from the CSS2 API — they match
+the files they select. Do not hand-edit a range; refetch the pair together.
```

## 2. `DESIGN.md` §4 — replace the "Font hosting" first paragraph

It still reads as a to-do list.

```diff
-`proposals/src/vlab_proposals/static/fonts/` holds three of the four families, but only
-two of the weights this section specifies: Zilla Slab 300 and Source Serif 4 400. **Zilla
-Slab 400, Source Sans 3 400, Source Sans 3 600 and IBM Plex Mono 400/500 all have to be
-fetched** — the proposals directory has Source Sans in Bold only. Full table in D-012.
-Serve from our own origin with `font-display: swap`.
+All seven face+weight combinations are in `fonts/` and declared in `css/fonts.css` —
+latin and latin-ext woff2, `font-display: swap`, 264.6 kB total. Link `css/fonts.css`;
+never link a `fonts.googleapis.com` stylesheet from a page. File table in D-012.
```

## 3. `DESIGN.md` §4 — a real gap: Source Serif 4 has no fallback stack

"Every stack declares a real fallback" is followed by three stacks for four faces. I used
`"Source Serif 4", Georgia, serif` in `css/fonts.css` and marked it PROPOSED in the
comment there. It needs a decision, and Georgia doubling as the Zilla fallback is worth a
second look — a page that loses both faces loses the contrast between them.

```diff
 - Every stack declares a real fallback: `"Zilla Slab", Georgia, serif` /
   `"Source Sans 3", "Helvetica Neue", Arial, sans-serif` /
-  `"IBM Plex Mono", ui-monospace, monospace`.
+  `"IBM Plex Mono", ui-monospace, monospace` /
+  `"Source Serif 4", Georgia, serif`.
```

## 4. `AGENTS.md` — "Things about this repo…", the proposals bullet

```diff
 - **The brand already existed in the proposals repo** before the website caught up:
   `../proposals/src/vlab_proposals/static/style.css` and `static/fonts/` hold the
   wordmark, colours and three of the four `.woff2` files. The website inherits from
-  the proposals, not the other way round.
+  the proposals, not the other way round. **The fonts no longer need it:** the website
+  has its own complete kit in `fonts/` + `css/fonts.css` (D-012). The proposals copy
+  carries weights §4 does not use — do not sync the directories.
```

---

## Not done, and deliberately

- **Glyph-level coverage was not verified.** Neither `fontTools` nor `brotli` is
  installed and this workstream was told not to require them, so the woff2 table
  directories were parsed by hand (magic bytes, `fvar` presence) but the `cmap` was not
  decompressed. One consequence is unresolved below.
- **`SourceSerif4-400` is 428 / 256 bytes smaller than Google's current build of the same
  subset** (the Zilla 300 pair is byte-identical). The proposals file predates whatever
  Google last added to the latin partition — plausibly the combining marks and
  `U+2212 / U+2215` that the current range names. Pairing an older file with the current
  `unicode-range` means those few codepoints would fall through to Georgia rather than
  render. English abstracts will not notice; a minus sign set in Source Serif might. The
  instruction was to copy rather than refetch, so the copy stands. Refetching the pair
  from `https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400` closes it in
  one command if it ever shows.
