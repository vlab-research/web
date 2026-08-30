# scripts

Thirteen scripts. **Four are rules from the documentation made executable**
(`check-claims.py`, `test-check-claims.py`, `check-contrast.py`, `check-links.py`), **seven
generate committed or built artefacts**, and **one** is a piece of arithmetic kept because a
design rule rests on it. **Where a script and a paragraph disagree, the script is what runs** — so fix the
paragraph, in the same change.

Nothing here needs a dependency. Python 3, standard library, run from anywhere.

| Script | What it does | Run it when |
|---|---|---|
| `check-claims.py` | Every number on a page traces to a `VERIFIED` row in `CLAIMS.md`, and carries a visible source line in the same visual unit | Before publishing any page that states a figure |
| `test-check-claims.py` | Ten fixtures asserting how `check-claims.py` behaves | After touching `check-claims.py`, or `CLAIMS.md`'s status vocabulary or publication rules |
| `check-contrast.py` | Every colour pair in `DESIGN.md` §3 meets its stated WCAG target — 38 pairs across both themes | Before publishing anything with a new colour pairing |
| `check-links.py` | Every internal link, `<img src>` and `#fragment` in `_site/` resolves — the fragment against the ids on the page it points at | After the build, and after moving or renaming any docs page or heading. **Expected count is 9, not 0** — see below |
| `build-coverage-map.py` | Emits the coverage section's three artefacts **plus the country list for structured data** from one data file | After `scripts/data/coverage.json` changes — and never hand-edit the output |
| `build-throughput-figure.py` | Emits `assets/figures/throughput-box.svg` — respondents recruited per study per active day | After `scripts/data/throughput.json` changes — and never hand-edit the output |
| `build-adcost-figure.py` | Emits `assets/figures/ad-cost.svg` — advertising cost per respondent recruited | After `scripts/data/ad-cost.json` changes — and never hand-edit the output |
| `build-reallocations-figure.py` | Emits `assets/figures/reallocations-box.svg` — budget reallocations per study. **Blocked: exits 1 until `p10` and `p25` exist** | After `scripts/data/reallocations.json` gets its two missing percentiles |
| `build-og-image.py` | Emits `assets/og.svg` — the 1200×630 social share card, figures and map from `coverage.json` | After `scripts/data/coverage.json` changes. **Re-rasterize `og.png` in the same change** |
| `build-icons.py` | Emits the twelve §7 icons **and** the sprite from one geometric table | After any icon change — editing an icon file by hand desynchronises the sprite |
| `build-paper-json.py` | Emits `_data/paper.json` from the manuscript in the paper repo | After the manuscript changes. Reads a repo outside this one |
| `build-review.py` | Builds the self-contained asset-review page (`DESIGN.md` §13) into `build/` | After any asset changes, if the review page is being republished |
| `build-favicon.py` | Emits `assets/favicon.ico` and `apple-touch-icon.png` from `assets/favicon.svg` | After the favicon changes — and never hand-edit either derivative |
| `check-fourth-hue.py` | Shows that no fourth brand hue can satisfy both AA on `--paper` and D-011's greyscale requirement | Only if someone proposes a product colour (D-024) |

**`check-links.py` exists because of what the docs migration gave up.** Under Hugo, internal
links were `{{< ref "..." >}}` and the build failed on a broken one. D-008 resolved all 116
of those to plain URLs — the right end state, but it hands the guarantee back. This checker
takes it, and covers more: `ref` validated the path and took the `#anchor` on trust, and
heading ids are generated from heading *text*, so rewording a heading silently breaks every
link into it. **It reports 9 today**, all screenshots that were never committed and were
broken on the Hugo site too (`notes/ws-docs-screenshots.md`). Any other number is a
regression.

**Seven of these write into the repo** — `build-icons.py` (`assets/icons/`),
`build-paper-json.py` (`_data/paper.json`), `build-throughput-figure.py` and
`build-adcost-figure.py` and `build-reallocations-figure.py` (all three `assets/figures/`), and `build-coverage-map.py` and
`build-review.py` (both `build/`). The other four only report. **Never hand-edit generated
output:** the next run reverts you silently, and in the icons' case the file and the sprite
drift apart first.

**Two of the six run on every deploy.** `netlify.toml` runs `npm run build`, which is
`build-coverage-map.py` and then Eleventy — `build/` is untracked, and `_data/coverage.js`
raises rather than rendering an empty coverage section if it is missing. The figure
generators are **not** in the deploy path: their output is committed, because a figure is an
asset and a map fragment is a build product.

---

## `check-claims.py` — the provenance rule

```
python3 scripts/check-claims.py                           # walks _site/ and build/
python3 scripts/check-claims.py --register                # print the parsed register and stop
python3 scripts/check-claims.py --only-failures <files>   # failures only
```

`AGENTS.md` hard rule 1 and `DESIGN.md` §2 state the provenance rule in prose; this
enforces it. Pages declare their figures with `data-claim` and friends — the markup
convention is `DESIGN.md` §8, "Claim annotation", and the script's own docstring repeats
it in full. An un-annotated page is still scanned, heuristically, but heuristic mode can
pass a number by coincidence. **Annotate.**

**Exit 0 means every named file is clean. Exit 1 means at least one failure, in one of
six kinds** — `register`, `banned`, `phrase`, `provenance`, `quote`, `unsourced`
(plus `unannotated` on pages that use annotation). `register` is checked first and is
fatal: a typo in a status column must not silently widen what the site may say.

**A bare run is now the useful one.** The walker skips `scripts/fixtures/` — nine pages
whose entire job is to fail — so `python3 scripts/check-claims.py` reports real drift and
nothing else. Before 2026-08-21 it did not, and exited 1 no matter how healthy the site
was; a gate that can never pass is a gate nobody runs. It still exits 1 today, on **9** real
findings, all of them the region totals. The count, and which of them are expected, is in
`AGENTS.md`, "Known drift". Never edit a fixture to make a number go down.

**It scans what ships, added 2026-08-25 with the Eleventy build.** Two more things are now
skipped, and both are the same mistake in different clothes — checking an input instead of an
output:

- **Eleventy source templates**, detected by the front-matter fence on line one. A template's
  own text is not what a visitor receives: its `{# #}` comments carry section numbers, motif
  ids and claim ids that are stripped at build time, and scanning them reported ten findings
  that existed on no page. The walk prints a `note` naming each template it skipped, so a
  skip is never silent.
- **`_includes/`**, which holds layouts. A layout is half a page and reaches a reader only
  through the built output already being scanned.

**`_site/` is walked when it exists**, and only then — on a clean checkout with no build,
the root `.html` files are walked exactly as before, so the gate still means something before
anyone runs `npm run build`. `--include-vendor` restores the old behaviour and adds
`node_modules`.

**The practical invocation has not changed**, and naming the files is still better than
trusting the walk:

```
npm run build && python3 scripts/check-claims.py _site/index.html _site/privacy/index.html
```

**`warn` is not a failure and is not noise either.** A `data-claim-quote` block shields
its numerals from the banned-value check — attributed quotation, `DESIGN.md` §8 — but
every withheld value it shields is reported at `warn` on every run, naming the row that
withholds it. The shield stops a build failing; it never stops a human seeing. Exactly one
page on the site is expected to produce one of these: the abstract on Papers (D-016).

## `test-check-claims.py` — the checker's own suite

```
python3 scripts/test-check-claims.py
```

Ten cases, each a fixture in `scripts/fixtures/` with an expected exit code. **Exit 0
means all ten behaved; exit 1 means one did not**, and the script prints which and what
it proves. Two of the nine were real bugs that shipped — read the docstring before
assuming a failure is the fixture's fault. **A stale fixture is the checker working, not
the checker broken:** if `CLAIMS.md` changed in a way a fixture no longer reflects, read
the failure before editing anything.

**The citation pair is the one to read before touching the provenance check.**
`pass-own-record.html` is first-party figures with **no** source line and must exit 0;
`fail-provenance.html` is Donati & Rao figures with no source line and must exit 1. They
assert the two halves of one rule (`DESIGN.md` §2, amended 2026-08-26): a number resting
on somebody else's document carries its citation, and a figure from our own operating
record carries nothing. **If both ever pass, citation has stopped applying to anything** —
which is the failure a single fixture could not have caught.

The split is read from the register's table header — `Definition` is ours and is exempt,
`Source` is somebody else's and is not — and it **fails safe**, because exemption requires
the `Definition` column.

The quotation pair is the one to read before widening anything about quotation:
`quote-abstract.html` is the case the shield exists for, `fail-quote-unattributed.html` is
the same mechanism used as a loophole in three shapes. If a change makes both pass, the
shield has stopped being a shield.

**Two files in `fixtures/` are not in the suite.** `claims-typo.md` is an alternate
register with `WITHELD` misspelt, which is what makes the `register` failure kind fire —
no case uses it, so that kind is currently untested. It is also a **stale** copy of
`CLAIMS.md` from before D-023 and still carries the withheld comparison rows as
`VERIFIED`; it reaches no page, but never read it as the register.
`content-method.html` is a parser sanity check over known-good copy.

## `check-contrast.py` — DESIGN.md §3

```
python3 scripts/check-contrast.py
```

22 pairs, light and dark, computed with the WCAG 2.x relative-luminance formula. **Exit 0
means all pairs pass.** Re-run it if any token in §3 moves.

It exists because the bug shipped once: `--brass` on an ink band measures 2.43:1 in light
mode and looks perfect in dark. Three pairs in the list are that trap and its relatives —
`--brass-inv`, `--data-inv`, and the source line on an ink band, which is `--on-invert-2`
and not `--ink-3` (4.00:1). **An ink band is dark in both themes and the tokens are not.**

## `build-og-image.py` — the social share card

```
python3 scripts/build-og-image.py            # -> assets/og.svg
python3 scripts/build-og-image.py --stdout
```

Direction 08 "Atlas Plate", chosen 2026-08-27. The script's docstring holds the
composition reasoning — why the country count is absent, why the ramp is flat, why
paper rather than ink, and why `top = 262` is derived rather than chosen. **Read it
before changing the layout**; three of those four are load-bearing.

It **imports `build-coverage-map.py` by path** and uses its projection, its ISO
lookups and its coverage loader, so the card's map and the page's map cannot disagree.
Figures come from `coverage.json` `totals` and are never typed.

**Rasterizing is a separate, local step and is deliberately not in the deploy.**
`netlify.toml` promises `scripts/` is standard-library Python needing nothing
installed; a rasterizer would break that. `assets/og.png` is **committed**, exactly as
`assets/apple-touch-icon.png` is. The brand faces are not installed system-wide, so a
naive `rsvg-convert` renders fallback type — the woff2 kit has to be converted and
pointed at first:

```
pip install fonttools brotli          # in a throwaway venv; not a repo dependency
# convert fonts/*.woff2 -> .ttf, setting name IDs 1/2/4/6 and OS/2.usWeightClass
# to match what og.svg asks for: Zilla Slab 300, IBM Plex Mono 400 and 500
FONTCONFIG_FILE=<conf pointing at those ttfs> \
  rsvg-convert -w 1200 -h 630 assets/og.svg -o assets/og.png
```

**Look at the output at 360px as well as 1200px.** A share card is rendered about a
third of size in a feed, and the direction this one beat died exactly there.

## `build-coverage-map.py` — the coverage section

```
python3 scripts/build-coverage-map.py                       # all four, to build/
python3 scripts/build-coverage-map.py --only map --stdout
python3 scripts/build-coverage-map.py --only countries       # just the JSON
```

Reads `scripts/data/coverage.json` and a vendored Natural Earth 1:110m boundary file;
writes `build/coverage-map.html`, `build/coverage-strip.html`,
`build/coverage-regions.html` and `build/coverage-countries.json`. The treatment is settled
in D-018 and described in `DESIGN.md` §8, "Coverage section". **Do not hand-edit the
output** — refresh the data and re-run, which is the whole reason the artefacts come from
one command.

**`coverage-countries.json` is the fourth artefact, added 2026-08-26**, and it is the only
one no human reads: `_data/schema.js` uses it for the JSON-LD `areaServed` block.
`coverage.json` carries ISO-2 codes and no names, and the names live in `world.geojson`,
which only this script reads — so emitting them here is what keeps the structured data and
the map from disagreeing about where we work. **It lists all 41**: the 37 with a count and
the 4 in `pending`, whose `respondents` is `null` and **never `0`**. `areaServed` is a
statement about where we operate, not about counts, so the pending four belong in it even
though the map does not draw them.

**Countries in `pending` are no longer drawn** (2026-08-26). They are covered but not yet
counted; they used to render as a dashed outline with their own legend state and a
sentence of prose. Nandan: *"If that's true, just leave them off entirely. Those are small
details nobody cares about."* They now fall through to the same hairline as every other
country we have not surveyed. **Dropping them at collection matters and deleting the
outline alone would have been a bug**: `covered_ids` is what the ghost pass skips, so a
pending country left in it and no longer drawn gets *no path at all* — an invisible hole
in the world — and it would still have been framing the viewBox. **Not drawing a country
is not calling it zero**, which is what `coverage.json`'s note guards against; the data
still records all four.

The map also **states no count** in its accessible label. It read *"Map of the N
countries"*, which was true only while those four were drawn.

**Exit 0 with a summary line is success.** It **exits non-zero and prints a banner** for
any country it cannot draw, and for any country that is in no region or in two. Never
ignore either: a country in two regions is double-counted in the totals, and a country in
none silently disappears from them.

`build/` is generated and untracked. Deleting it costs one command.

---

## The three figure generators — `build-throughput-figure.py`, `build-adcost-figure.py`, `build-reallocations-figure.py`

**Added 2026-08-25; a third on 2026-08-26.** All three draw a box plot: M3 interval on an M4 tick rule, built from the
four primitives — bracket whiskers, a bar for the interquartile box, a **cell** at the median
(§6 M3 is explicit that the centre mark is a cell, never a dot), and ticks for the ruler.
**They are deliberately the same figure in two units**, so a reader who learns to read one has
learned to read the other. No chart library, no literal colour, `.inv` variants for an ink
band.

```
python3 scripts/build-throughput-figure.py
python3 scripts/build-adcost-figure.py
```

**Each exits non-zero if a value falls outside its own drawn axis**, printing which value and
which axis. That guard exists so a figure can never silently clip a claim — if the data moves
past the ruler, the build stops rather than cropping the evidence.

**A second clip was found on 2026-08-25 and it was not on the axis — it was in the source
line.** Both scripts emitted each provenance line as one unwrapped `<text>` at 12px in a
620-unit viewBox, and an outer `<svg>` clips at its own bounds, so the second half of every
source line was being **silently truncated**: the throughput figure stopped at *"Whiskers:
10th"* with no closing value, and the ad-cost figure lost *"not our fee"* entirely. The
figures looked finished and were quietly failing the one rule they exist to demonstrate.

Both now **wrap the source lines and grow the viewBox to hold them** (`wrap_src`,
`src_block`), and `src_block` **exits non-zero on a single word wider than the box** — the
same shape of guard as the axis one, for the same reason. `SRC_CPL` is a character budget of
`W // 6`, not a measurement: there is no font metric here and no dependency is permitted, so
it is deliberately conservative. If a source line ever needs to be tighter, widen `W` rather
than shaving the budget.

**Their data files carry the query that produced them**, so any figure can be re-derived
against production without reconstructing the SQL. Two traps are recorded in
`scripts/data/ad-cost.json` and in `CLAIMS.md`, both of which produced a wrong number once:
spend must be the **max** per campaign/stratum/day rather than the sum (`temp=true` rows are
cumulative intra-day snapshots), and `adopt_reports` must be **filtered by `report_type`**
because only `FACEBOOK_ADOPT` is a decision.

**A CockroachDB quirk that also produced a wrong number:** `count(DISTINCT x)` returns garbage
when it shares a `SELECT` list with `percentile_cont()`. Compute distinct counts separately.

## What is not here

**Two specimen builders did not survive.** `build-specimen.py` and `mk_specimen.py` built
review aids — a type specimen and a paper specimen — and lived only in a session-scoped
scratchpad. They are gone. Nothing committed depends on them and either is cheap to
rewrite; they are noted so their absence reads as a fact rather than an oversight.

**There is no test suite for anything but `check-claims.py`.** `build-coverage-map.py`
warns loudly and exits 2 on data it cannot draw, which is most of the protection it needs.
`build-icons.py` has none: nothing checks that the twelve files and the sprite agree, and
that is exactly the drift it exists to prevent. A fixture comparing the two would be worth
writing before Phase 4.


### `build-reallocations-figure.py` was blocked, and the block worked

**Added 2026-08-26, blocked for an afternoon, drawn the same day.** While `p10` and `p25`
were missing it exited 1 and named them:

```
BLOCKED: p10, p25 missing from reallocations.json.
```

C-092 records **median 61 · p75 165 · p90 351 · max 1,308** across 109 studies. A box
plot's box spans **p25 to p75** and its whiskers span **p10 to p90**, so two of the five
values the form needs do not exist. `AGENTS.md` hard rule 2 is unambiguous about the
alternative — *never invent a figure, not as a placeholder, not "to be replaced later"* —
so the script refuses rather than drawing something that is not the claim.

**The query is the `query` field of `scripts/data/reallocations.json`**, alongside the two
traps that have each produced a wrong number here before: always filter `report_type`
(counting monitoring rows gives a median of 84 instead of 61), and never put
`count(DISTINCT …)` in a `SELECT` list with `percentile_cont()`.

**Why the same form rather than a variant that fits the data we have.** The box plots are
deliberately one figure in three units, so a reader who learns to read one has learned to
read all of them. An asymmetric variant invented for this dataset because two numbers are
absent would spend that property to ship a week early.

**The query was run read-only against cluster `vprod` on 2026-08-26** and returned p10 = 13,
p25 = 28 — plus median 61, p75 165, max 1,308 and 17,596 across 109 studies, **every one of
which reconciled with C-092 as it already stood.** That is the more useful half of the result:
it confirms the `report_type` filter and shows the row had not drifted.

**Add a third trap to the two above.** CockroachDB's `percentile_cont` needs a **FLOAT**
ordering column — `count(*)::FLOAT` — or it fails outright with *unknown signature:
percentile_cont_impl(decimal, int)*.

**The repo has production access and nothing recorded it.** `kubectl` is configured against
`gke_toixotoixo_europe-west1-b_toixo`, namespace `vprod`:

```
kubectl exec -n vprod gbv-cockroachdb-0 -- \
  /cockroach/cockroach sql --insecure --database=vlab --execute="SELECT …"
```

**Every figure in `CLAIMS.md` can therefore be re-derived rather than taken on trust.** Read
only; nothing in this repo has any business writing to that cluster.
