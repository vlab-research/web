# scripts

Eight scripts. Three are rules from the documentation made executable, four generate
committed artefacts, and one is a piece of arithmetic kept because a design rule rests
on it. **Where a script and a paragraph disagree, the script is
what runs** — so fix the paragraph, in the same change.

Nothing here needs a dependency. Python 3, standard library, run from anywhere.

| Script | What it does | Run it when |
|---|---|---|
| `check-claims.py` | Every number on a page traces to a `VERIFIED` row in `CLAIMS.md`, and carries a visible source line in the same visual unit | Before publishing any page that states a figure |
| `test-check-claims.py` | Nine fixtures asserting how `check-claims.py` behaves | After touching `check-claims.py`, or `CLAIMS.md`'s status vocabulary or publication rules |
| `check-contrast.py` | Every colour pair in `DESIGN.md` §3 meets its stated WCAG target | Before publishing anything with a new colour pairing |
| `build-coverage-map.py` | Emits the coverage section's three artefacts from one data file | After `scripts/data/coverage.json` changes — and never hand-edit the output |
| `build-throughput-figure.py` | Emits `assets/figures/throughput-box.svg` — respondents recruited per study per active day | After `scripts/data/throughput.json` changes — and never hand-edit the output |
| `build-adcost-figure.py` | Emits `assets/figures/ad-cost.svg` — advertising cost per respondent recruited | After `scripts/data/ad-cost.json` changes — and never hand-edit the output |
| `build-icons.py` | Emits the twelve §7 icons **and** the sprite from one geometric table | After any icon change — editing an icon file by hand desynchronises the sprite |
| `build-paper-json.py` | Emits `_data/paper.json` from the manuscript in the paper repo | After the manuscript changes. Reads a repo outside this one |
| `build-review.py` | Builds the self-contained asset-review page (`DESIGN.md` §13) into `build/` | After any asset changes, if the review page is being republished |
| `check-fourth-hue.py` | Shows that no fourth brand hue can satisfy both AA on `--paper` and D-011's greyscale requirement | Only if someone proposes a product colour (D-024) |

**Four of these write into the repo** — `build-icons.py` (`assets/icons/`),
`build-paper-json.py` (`_data/paper.json`), `build-coverage-map.py` and `build-review.py`
(both `build/`). The other four only report. **Never hand-edit generated output:** the
next run reverts you silently, and in the icons' case the file and the sprite drift apart
first.

---

## `check-claims.py` — the provenance rule

```
python3 scripts/check-claims.py index.html build/*.html   # the useful invocation
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
was; a gate that can never pass is a gate nobody runs. It still exits 1 today, on 25 real
findings. The count, and which of them are expected, is in
`AGENTS.md`, "Known drift". Never edit a fixture to make a number go down.

**`warn` is not a failure and is not noise either.** A `data-claim-quote` block shields
its numerals from the banned-value check — attributed quotation, `DESIGN.md` §8 — but
every withheld value it shields is reported at `warn` on every run, naming the row that
withholds it. The shield stops a build failing; it never stops a human seeing. Exactly one
page on the site is expected to produce one of these: the abstract on Papers (D-016).

## `test-check-claims.py` — the checker's own suite

```
python3 scripts/test-check-claims.py
```

Nine cases, each a fixture in `scripts/fixtures/` with an expected exit code. **Exit 0
means all nine behaved; exit 1 means one did not**, and the script prints which and what
it proves. Two of the nine were real bugs that shipped — read the docstring before
assuming a failure is the fixture's fault. **A stale fixture is the checker working, not
the checker broken:** if `CLAIMS.md` changed in a way a fixture no longer reflects, read
the failure before editing anything.

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

## `build-coverage-map.py` — the coverage section

```
python3 scripts/build-coverage-map.py                       # all three, to build/
python3 scripts/build-coverage-map.py --only map --stdout
```

Reads `scripts/data/coverage.json` and a vendored Natural Earth 1:110m boundary file;
writes `build/coverage-map.html`, `build/coverage-strip.html` and
`build/coverage-regions.html`. The treatment is settled in D-018 and described in
`DESIGN.md` §8, "Coverage section". **Do not hand-edit the output** — refresh the data and
re-run, which is the whole reason the three artefacts come from one command.

**Exit 0 with a summary line is success.** It **exits non-zero and prints a banner** for
any country it cannot draw, and for any country that is in no region or in two. Never
ignore either: a country in two regions is double-counted in the totals, and a country in
none silently disappears from them.

`build/` is generated and untracked. Deleting it costs one command.

---

## The two figure generators — `build-throughput-figure.py`, `build-adcost-figure.py`

**Added 2026-08-25.** Both draw a box plot: M3 interval on an M4 tick rule, built from the
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
