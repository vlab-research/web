# Workstream: `scripts/check-claims.py`

Written 2026-08-20. The script is in the repo and runnable. Everything below is a
**proposed edit to a document I am not allowed to touch** — `AGENTS.md`, `DESIGN.md`,
`CLAIMS.md` — plus the findings that need a human decision.

```
python3 scripts/check-claims.py                       # every .html in the repo
python3 scripts/check-claims.py index.html --only-failures
python3 scripts/check-claims.py --register            # what the register parsed to
```

Exit 1 on any failure, a line per check, failures grouped in a summary — the same shape
as `check-contrast.py`.

---

## 1. The design judgement, and why

A naive "every numeral must be in `CLAIMS.md`" check produces so much noise it gets
switched off. On `index.html` it produces 57 lines of output for 11 real problems, and
the privacy policy alone contributes GDPR article numbers, retention periods, a street
number and thirteen heading numbers.

So the check has **two modes, chosen per file**:

- **Annotated** — the page declares what it is claiming, and the check is *exact*.
  Engaged automatically when a file contains any `data-claim` attribute.
- **Heuristic** — every numeral in body text is matched against the register, with an
  explicit allowlist (`ALLOW` at the top of the script) carrying years, ISO dates, legal
  citations, list numbering, street addresses and ZIP codes. Engaged when a file has no
  annotation at all, so an un-annotated page still gets checked.

**Recommendation: annotate every Phase 4 page.** Heuristic mode is deliberately weaker
and the script says so — on `index.html` the bare "19" in "aged between 13 and 19"
matches C-011's 19-day median field window by coincidence and passes. That kind of
false pass is unfixable heuristically; it is fixed by the page saying what it means.

**Banned values ignore both modes and the allowlist entirely.** A `WITHHELD`,
`PLACEHOLDER` or `STALE` value on a page is a hard failure everywhere, including inside
`data-claim-scan="off"` legal copy.

---

## 2. Proposed `DESIGN.md` §8 addition — the markup convention

This is a design-system addition and needs your approval before it is real. Suggested
placement: a new subsection at the end of §8, after "Forms", since it applies to every
component that carries a figure. **`scripts/check-claims.py` already implements it.**

> ### Claim annotation
>
> Any element carrying a figure declares which claim it is, so the provenance rule can
> be checked rather than reviewed. Five attributes, no classes, no JavaScript:
>
> | Attribute | Meaning |
> |---|---|
> | `data-claim="C-003"` | This element's numerals are the value of C-003. Space-separate several ids. |
> | `data-claim="none"` | This numeral is deliberately not a claim — a list counter, a year in a kicker, a street number. |
> | `data-claim-source` | This element is the visible source line. |
> | `data-claim-unit` | This element is the visual unit — the widest element a value may draw its source line from. |
> | `data-claim-scan="off"` | Stop scanning numerals inside this element. Legal copy only. Banned values are still checked inside it. |
>
> ```html
> <div class="cell" data-claim-unit>
>   <div class="num" data-claim="C-003">6.1<span class="unit">p.p.</span></div>
>   <div class="label">MEAN ABS. DEVIATION</div>
>   <div class="src" data-claim-source>vs. GSS, CPS, Pew</div>
> </div>
> ```
>
> Without `data-claim-unit` the unit is the nearest `figure`/`li`/`td`/`section` or
> `.cell`/`.card` ancestor, and **only that one counts** — a source line elsewhere on
> the page is not provenance. With it, the search widens to that element and stops
> there, which is how one `<figcaption>` legitimately serves every row of one figure.
>
> `python3 scripts/check-claims.py` enforces this. It is not optional decoration: the
> stat row's source line is mandatory in this section, and this is the mechanism that
> makes "mandatory" mean something.

Two smaller consequences, if you take the above:

- **§8, Stat row** — after "**Source line in Source Serif italic `--ink-3` — mandatory**",
  add: "Mark it `data-claim-source`, and the number `data-claim="C-00n"`. See 'Claim
  annotation' below."
- **§8, Coverage map** — "Source line mandatory, as for any figure" gains the same
  pointer. The legend's magnitude labels (1,000 / 10,000 / 100,000) are scale marks,
  not claims, and want `data-claim="none"`. See finding 3 below.
- **§13, Reference** — add a line beside the contrast check:
  `- Claims check: python3 scripts/check-claims.py`

---

## 3. Proposed `AGENTS.md` edits

**Remove** this bullet from "Known drift" — it is done:

> - **`check-claims.py` does not exist.** It is referenced as the consequence of D-006 and
>   is the check that actually enforces the brand: every number on a page traceable to a
>   `VERIFIED` row. Write it before Phase 4 ships.

**Replace** the first two lines of the "Verification before you hand anything over"
checklist, which are currently manual, with the check that now performs them:

> - [ ] `python3 scripts/check-claims.py` passes — every number traces to a `VERIFIED`
>       row and carries a visible source line in its own visual unit

**Add** to hard rule 1 (the provenance rule), after "breaking it is the most expensive
mistake available in this repo":

> `python3 scripts/check-claims.py` enforces both halves of this rule. Pages declare
> their claims with `data-claim` (see `DESIGN.md` §8); an un-annotated page is still
> scanned heuristically, but heuristic mode can pass a number by coincidence, so
> annotate.

**Amend** the Nigeria funnel bullet in "Known drift" to record that it is now caught:

> - **Nigeria funnel figures** (~3,000 clicks / 890 starts / 560 completions) are on the
>   current live site with no `CLAIMS.md` row. Either trace them or leave them off —
>   `check-claims.py` fails on them today, so they cannot survive into the rebuild
>   unnoticed.

---

## 4. Proposed `CLAIMS.md` note — one real inconsistency the parser found

**C-004 is `WITHHELD`, but $0.32 is still printed as a value in two `VERIFIED` rows.**
C-012's Value cell reads "$0.32 vs $3.00 (GSS traditional) and $6.67" and C-013's reads
"$0.32 vs ~$0.10". So the register simultaneously withholds the cost-per-question figure
and publishes it twice.

The script resolves this the conservative way and prints what it did:

```
contested  0.32 appears in a banned row and in C-012, C-013 — banned wins
```

That matches `CONTENT.md` ("Per-question cost renders `—` until C-004 is resolved") and
matches the Method page copy, which quotes $6.30, $0.70, $20, $5, $3.00 and $6.67 and
never $0.32. But it is fragile as documentation. **Suggested fix, for you to make:**
restate C-012's value as "gold standard runs $3.00 (GSS traditional) and $6.67 (GSS
Follow-on) per question per respondent" and C-013's as "we are ~3× Prolific's ~$0.10",
so that neither `VERIFIED` row prints the withheld figure. Then the contested line
disappears and the register says one thing.

---

## 5. What the script found on the live site

`python3 scripts/check-claims.py index.html` → **11 failures**, exit 1.

| Line | Finding | Verdict |
|---|---|---|
| 222 | `3000`, `890`, `560` | **Real.** The Nigeria funnel, exactly as `AGENTS.md` predicted. No `CLAIMS.md` row, no source. |
| 220 | `10` largest cities, `1 million` residents, ages `13`–19 | **Real.** Study-design facts with no row. C-040-shaped: either trace them or drop them. |
| 220 | `8` | Noise — "TECNO DROID PAD 8 II", a product name in ad copy. Wants `data-claim="none"`. |
| 222 | `1`, `2` | Noise — a run-in numbered list mid-paragraph ("1. Beliefs…; 2. Career choices"). The allowlist only catches list numbering at the start of a line. |
| 387, 409 | `72` hours, under `13` | Privacy policy. Not claims about our work. `--exempt-id privacy` (or `data-claim-scan="off"` in the rebuild) drops both, leaving 9 failures, all in the Nigeria paragraph. |

`542` municipalities and `90` provinces (Italy, C-042) pass, and "aged between 13 and
**19**" passes by coincidence against C-011 — the documented weakness of heuristic mode.

**Also caught, in `build/` (another workstream, in progress as I write):**

- `build/coverage-regions.html` — regional totals `311,363` (MENA), `143,816`,
  `136,558`, `113,460`, `30,573`, `2,838` have **no `CLAIMS.md` row**. `AGENTS.md`
  already flags MENA-at-42% as an undecided positioning fact; the check now says the
  same thing mechanically. These need rows (they are derivable from the same query that
  produced the per-country table) before that section ships.
- `build/coverage-map.html` — `1,000` / `10,000` / `100,000` are the legend's magnitude
  steps, not claims. They want `data-claim="none"`, per the §8 amendment above.

---

## 6. Fixtures

In `scratchpad/fixtures/`, all run against the real `CLAIMS.md`.

| File | Expected | Result |
|---|---|---|
| `pass.html` | exit 0 | 20 ok/skip, 0 failures. This is the `CONTENT.md` Home copy deck, annotated. |
| `content-method.html` | Method page cost paragraph passes | All six cost figures resolve to C-012/C-013/C-014; the un-annotated stat cell correctly fails `provenance`. |
| `fail-unsourced.html` | unsourced | Nigeria funnel caught: 3000, 890, 560. |
| `fail-placeholder.html` | banned | C-040's `2,400` and the withheld `$0.32`, both fatal, one of them annotated as if that legitimised it. |
| `fail-provenance.html` | provenance | Two stat cells with no source line fail; the third, which has one, passes. |
| `fail-withheld.html` | banned | `1,097,153` **and** its rounded form "1.1 million" — rounding does not launder a withheld value. |
| `fail-phrase.html` | phrase | `chatroach`, "current platform", "older-platform", "database migration". |
| `fail-mixed-heuristic.html` | unsourced | Invented `68%` and `4.5` days caught; `841.7k` correctly matched to C-010's 841,660; years, heading numbers and the address skipped. |
| `claims-typo.md` | register | `WITHELD` typo → 2 loud register failures, exit 1, and the rows stay unpublishable rather than defaulting open. |

---

## 7. Judgement calls worth reviewing

1. **Rounding tolerance is capped at 2%** (`ROUNDING_TOLERANCE`). "841.7k" matches
   841,660 and "18 million" matches 17,979,910, but "1 million people" no longer
   matches C-015's 1,097,153. Without the cap, every large round number on the site
   collided with something in the register.
2. **Small integers from banned rows are not banned globally** (`BANNED_MIN_MAGNITUDE
   = 100`). C-041's "2 waves · 4 mo" would otherwise ban the digits 2 and 4 sitewide.
   Below the threshold a banned value is only enforced where an element declares that
   claim id. C-040's `2,400` is above it and is banned everywhere.
3. **Banned rows contribute every numeral in the row; publishable rows contribute the
   Value cell only.** C-004's Value now reads "Not published" while the $0.30/$0.32
   conflict sits in the source column — the withheld figure is named in the reason for
   withholding it. The asymmetry stops a definition's "n=137" from becoming a licence
   to print 137.
4. **The phrase denylist** (`DENY_PHRASES`, CLAIMS.md publication rule 2) is
   deliberately narrow: internal database and table names (`chatroach`, `cockroachdb`,
   `vprod`, `kubectl`, `vlab.<table>`, `study_confs`, `campaign_confs`, `adopt_reports`,
   `inference_data`, `study_id`, `userid`, `user_id`, `shortcode`), the split itself
   ("both platforms/schemas", "older/legacy/current platform"), the bare word "schema",
   and *qualified* migrations only ("database migration", "migrated from"). "Kubernetes",
   "Helm", "open source" and "the platform is open source" are sanctioned copy and are
   not matched; an unqualified "migration" is not matched either, because a survey about
   migration is legitimate work.
5. **Duplicate claim ids resolve by `Checked` date.** C-010 and C-011 each appear twice —
   a `PLACEHOLDER` row in Headline figures superseded by a `VERIFIED` row in Production
   figures. The script prints which row won.
6. **`C-\d+` references and ISO dates are not values.** Without this, C-015's "use
   C-010" would have banned the number 10 sitewide, and C-018's "2020-02-13" would have
   published the numbers 2 and 13.
