# WS · Paper — findings, proposed doc edits, and the two open questions

**Workstream:** mine `Donati, D. and Rao, N., "Adaptive Survey Sampling via Ad Platforms."`
into structured data; harden the validation figures.
**Date:** 2026-08-20 · **Nothing in `AGENTS.md` / `DESIGN.md` / `DECISIONS.md` /
`CLAIMS.md` / `CONTENT.md` was edited.** Everything proposed for those files is below.

## What shipped

| File | What it is |
|---|---|
| `_data/paper.json` | Every figure, quote and disclosure the paper carries, each tagged with the edition and file it came from, plus explicit `NOT STATED` markers where a value does not exist |
| `assets/figures/mad-comparison.svg` | The MAD comparison, redrawn. **Not M3** — see §3 |
| `scratchpad/specimen-paper.html` | Abstract at 62ch in Source Serif + the figure on paper and on an ink band, in all three theme states |

`python3 scripts/check-contrast.py` — 22 pairs, all pass (tokens untouched).

---

## 0 · The paper directory is not where `CLAIMS.md` says it is

`CLAIMS.md` cites `../../survey-sampling-with-ads/paper/…`, which from `vlab.digital`
resolves to `/home/nandan/Documents/vlab-research/survey-sampling-with-ads/paper` —
**that directory does not exist.** The repo is a sibling of `vlab-research`, not a member
of it:

```
/home/nandan/Documents/survey-sampling-with-ads/paper/     ← actual
```

From `vlab.digital` that is `../../../survey-sampling-with-ads/paper/`. The wrong path
appears twice (the "The paper, as a source" section and "Refreshing the placeholders").
Every future agent asked to re-check a figure will hit this first. **Fix both.**

Four editions sit there, not three:

| File | `\date{}` | Byline | Role |
|---|---|---|---|
| `survey-sampling-with-ads-Jul2026.tex` | September 15, 2025 | yes | working manuscript ("live", per the paper repo's `PLAN.md`) |
| `JMR_submission_09152025.tex` | September 15, 2025 | **none — blinded** | as submitted to JMR |
| `SSRN_09152025.tex` | September 15, 2025 | yes | SSRN edition |
| `survey-sampling-with-ads-Jan2025.tex` | September 15, 2025 | yes | fourth edition, undocumented, near-identical to SSRN |

(`survey-sampling-with-ads.tex` is a 2023 ancestor, a third the length. Ignore it.)

---

## 1 · The citation year — recommendation and evidence

### Evidence

1. **All four editions carry `\date{September 15, 2025}`.** Including the one named
   `Jul2026`. The "2026" is a *filename*, chosen by the authors as a working label; the
   document inside it dates itself 2025.
2. **The only compiled PDF of the current paper is `JMR_submission_09152025.pdf`.** Its
   title page reads `Adaptive Survey Sampling via Ad Platforms∗ / September 15, 2025`,
   **with no author names** — it is the blinded submission. There is no compiled
   SSRN or Jul2026 PDF in the repo.
3. **No SSRN ID, no DOI, no URL exists anywhere.** Searched every `.tex`, both `.bib`
   trees, and the paper repo's `.md` files. The `-blx.bib` files are biblatex control
   files, not entries. The bibliography contains five other Donati/Rao works and no entry
   for this one. **Nothing about this paper is publicly linkable from anything we hold.**
4. **The paper is not published and is not in press.** The paper repo's `PLAN.md` line 14:
   manuscript **JMR-25-0847**, a *"risky" major revision with a six-month extension
   granted*. Three reviewers plus an AE. A journal citation would be false.

### Recommendation

> **Short form, everywhere on the site: `Donati & Rao, 2025`.**
> **Full form on the Papers page:** Donati, D. and Rao, N. (2025). *Adaptive Survey
> Sampling via Ad Platforms.* Working paper.

Because: 2025 is the date the document prints on its own title page, in every edition,
including the one whose filename says 2026. Citing 2026 would cite a year the paper
does not carry.

**Two conditions attached, and they are not optional.**

- **A year without a link is half a citation on a site whose proposition is
  verifiability.** Before "2025" ships, someone has to establish what a reader can
  actually open. Two paths: (a) confirm the SSRN posting exists and get its URL —
  **I could not verify this locally and must not guess a URL**; or (b) D-016 lands as a
  landing page that hosts the PDF, and vlab.digital becomes the canonical link.
- **If we host a PDF, it cannot be the one that is already compiled.**
  `JMR_submission_09152025.pdf` is blinded — no byline. A hostable PDF has to be built
  from `SSRN_09152025.tex`. Flagging it because "the PDF already exists" is the obvious
  shortcut and it ships an author-less paper.

**Do not publish the `Jul2026` edition.** It is a live revision: it drops the
equal-variance assumption, adds per-stratum σ² to the allocation problem with a new KKT
derivation, and rewrites the future-work section. Publishing it publishes an in-flight
response to reviewers. Cite and host the SSRN edition. *Every figure the site uses is
identical across all three editions* (verified value by value), so this costs us nothing.

**Owner: Nandan.** The two conditions are the decision; the year is not really in doubt.

---

## 2 · C-004, the $0.30 / $0.32 conflict — evidence only, not resolved

Confirmed real, and it is exactly what `CLAIMS.md` describes.

| Edition | Abstract | Table `costs` | Cost Considerations text | Agree? |
|---|---|---|---|---|
| Jul2026 | **$0.30** | **$0.32** | **$0.32** | no |
| JMR_submission_09152025 | **$0.30** | **$0.32** | **$0.32** | no |
| SSRN_09152025 | **$0.30** | **$0.32** | **$0.32** | no |

**The three editions are byte-identical in both the abstract and the body of the Cost
Considerations section** (md5-checked; the SSRN edition differs only in using `\section`
where the others use `\section*` for the heading itself). So the conflict is not an artifact of one edition and cannot be
resolved by picking an edition. It is one unreconciled inconsistency, propagated.

Verbatim, the two sides:

- Abstract: *"…cost-effective in the U.S., with a total cost of **\$0.30** per question
  per respondent…"*
- Cost Considerations: *"Summing advertising costs and incentives, the cost per final
  participant was \$11.6, corresponding to a cost per question per respondent of
  approximately **\$0.32**."* Table `costs` prints **\$0.32**.

**One piece of evidence `CLAIMS.md` does not have.** A superseded abstract survives
commented out at line 94 of *every* edition, and reads *"mean absolute deviations ranging
around 6.3 p.p., and a cost per question per respondent around **\$0.30**."* The live
abstract inherited "$0.30" from that draft; the cost section was later rewritten to
compute $0.32 from $11.60, and the abstract was never brought along. That is an argument
for $0.32 being the current number, not a proof.

**The paper never states the question count that divides $11.60.** $11.60/$0.32 implies
~36 questions, $11.60/$0.30 implies ~39, and the described instrument (20 substantive
outcomes + 8 demographic items = 28) divides to $0.414. None of these reconstructions may
be published; they are recorded in `paper.json` as evidence only.

**Not resolved here, as instructed.**

### Knock-on from the coordinator's update (C-004 = "don't include that")

The withdrawal is cleaner than "render `—`", but it reaches further than the Method page,
and this workstream owns the place it reaches:

- **Every row of Table `costs` is denominated per question.** Meta $0.32, GSS $3.00, GSS
  Follow-on $6.67, Prolific $0.095. The Papers page spec in `CONTENT.md` says the page
  carries "the abstract, the MAD comparison figure, **the cost table**, BibTeX, and the
  download." **Reproducing the paper's cost table prints the withheld figure**, four
  times over. Either the cost table comes off the Papers page, or it is redrawn in
  per-participant units.
- **The abstract prints $0.30.** `CONTENT.md` requires it verbatim and forbids
  paraphrase; both are right. So the withheld number appears on the Papers page anyway,
  inside a quotation, and there is no honest way to remove it. This is fine and worth
  saying plainly: quoting the paper's own words is not us making a cost claim. But it
  means "no cost-per-question figure ships at all" cannot be enforced literally on the
  Papers page, and someone should decide that deliberately rather than discover it.
- **C-012 and C-013 are per-question comparisons and cannot survive intact.** The
  substitute figures are all `VERIFIED` and independent of C-004: advertising **$6.30**
  per participant, **$0.70–$20** by stratum, **$11.60** per participant including the $5
  incentive (C-014). The qualitative claim survives whole — *roughly 3× Prolific, far
  below a gold-standard probability survey* — because the paper states the multiple in
  words: *"the Meta sample was roughly 3 times more expensive than Prolific on a
  per-question basis."* Quote the multiple, drop the units.
- One number to keep off any rebuilt comparison: the paper's own per-respondent Prolific
  cost is **$2.66**, so $11.60 vs $2.66 is **4.4×**, not 3×. The 3× multiple is only true
  per question. Printing "$11.60 vs $2.66" beside "roughly 3×" contradicts itself.

*(The Method §5 rewrite belongs to the positioning workstream and `ws-positioning.md`; the
constraint above is the part that comes out of the paper.)*

---

## 3 · Does the paper report intervals? No. So the figure is not M3.

**It does not.** Searched all three editions for standard error, confidence interval,
error bar, bootstrap, CI, p-value and significance-in-the-statistical-sense: **zero hits
on any MAD.** The comparison is a bare figure (`presentation/Figures/mad_grouped_meta_prolific_llm.pdf`)
and the values live in prose beside it.

Confirmed independently and damningly by the paper repo's own `PLAN.md` line 14, which
records the JMR reviewers' consensus: *"**MAD comparisons have no inference.**"*

DESIGN.md §6 M3: *"Appears only where a real interval exists. Decorative use would be a
lie."* So M3 is prohibited here, and drawing it would be exactly the failure `CLAIMS.md`
exists to prevent — dressed as rigor.

**`CONTENT.md`'s Home §4 spec is therefore wrong** and needs an edit: it says
*"Interval rows (motif M3), our estimate in `--data`, comparators in `--ink-3`."*
Proposed replacement in §6 below.

### What was drawn instead

Bars on **one shared scale**, with an **M4 tick rule** carrying the 0–12 p.p. graduations
— the scale is real, so the ruler is honest. Our estimate `--data`, comparators
`--ink-3`, exactly as briefed for the colour roles. No tick sits inside the bars: **M2's
tick means *target*, and a MAD has no target**, so borrowing the M2 form would have
repeated the M3 lie in a different vocabulary. This is the "plain comparison" branch.

- `assets/figures/mad-comparison.svg`, tokens only, no literal hex (checked).
- Ships a `.inv` class: on an ink band `--data` → `--data-inv` and `--ink-3` →
  `--on-invert-2`, because `--data` on an ink band is 2.10:1 and `--ink-3` source lines
  are 4.00:1. Both traps are in §3 and both are in the file.
- `role="img"` with `<title>` and `<desc>`; numerals `font-variant-numeric: tabular-nums`.
- **Source line inside the figure**, per the provenance rule: *"Mean absolute deviation
  across all outcome variables, post-stratification weighted, against GSS 2024, CPS 2024
  and Pew 2023. Donati & Rao. Lower is closer. **No interval is reported.**"*

That last clause is a deliberate addition. A methodologist looking at three bars with no
error bars will wonder; saying why is more on-brand than leaving the gap. Cut it if the
Home band is too tight, but keep it on the Papers page.

---

## 4 · CLAIMS.md verification — every row that cites the paper

Values first. **Every point estimate in C-001–C-014 and C-054 is correct against the
manuscript, and every one of them is identical in all three editions.** No figure drift.
What follows is sourcing and framing drift, in descending order of how much it matters.

### Row by row

| ID | Value correct? | Note |
|---|---|---|
| C-001 | ✅ 33 | Abstract "over 33", body "33 studies across 23 countries". The register's cap ("33" or "33+", never higher) is right |
| C-002 | ✅ 23 | |
| C-003 | ✅ 6.1 wtd / 6.2 unwtd | Also Table `tab:mad_outcomes` at four decimals: 0.0608 / 0.0625 |
| C-004 | ✅ conflict as described | See §2 |
| C-005 | ✅ 1,500 | Abstract *and* Introduction |
| C-006 | ✅ 6.1 vs 7.1, "about 15% better" | **But see D-9 below — this row has an inference problem** |
| C-007 | ✅ 6.1 vs 11.1, "more than 45% better" | Twins = Twin-2K-500, `toubia2025twin` ✅ |
| C-008 | ✅ 7.1 wtd / 7.3 unwtd, n=1,197, Jun–Jul 2025 | Verbatim match |
| C-009 | ✅ 11.1 wtd / 12.0 unwtd | |
| C-012 | ✅ $0.32 vs $3.00 / $6.67 | |
| C-013 | ✅ ~3×, $0.32 vs ~$0.10 | Table prints **$0.095**; the *text* says "about $0.10" |
| C-014 | ✅ $6.30 / $0.70–$20 / $11.60 | Paper writes "$6.3" and "$11.6" |
| C-054 | ✅ AAAV1539, title footnote | |

### Drift, as a list

**D-1 — the path is wrong, twice.** §0 above. Highest practical cost of anything here.

**D-2 — "Table 4" does not exist.** "Refreshing the placeholders" sends the next agent to
*"Table 4"* for C-008/C-009. There is no Table 4 carrying them. The comparator estimates
are in **Figure `fig:MAD-comparison`** and the prose paragraph beneath it. The paper's
only MAD *table*, `tab:mad_outcomes`, is **Meta-only** and has no Prolific or twins column
— an agent following the instruction will find a table of the right shape with the wrong
contents. Correct pointer: *Figure `fig:MAD-comparison`, and the paragraph immediately
following it; the per-domain three-way values are in the paragraph preceding Figure
`fig:MAD-categories-comparison`.*

**D-3 — a fourth edition exists.** `survey-sampling-with-ads-Jan2025.tex`. Undocumented.

**D-4 — "the working manuscript is dated 2026" is false.** `CLAIMS.md`: *"the working
manuscript is dated 2026 and the submission 2025."* The working manuscript's `\date{}` is
**September 15, 2025**, the same as both submissions. Only its *filename* says 2026. This
sentence is the whole basis of the open citation-year question, and it is not accurate.
See §1.

**D-5 — benchmarks are not uniformly 2024/2023.** GSS 2024, CPS 2024, Pew 2023 are all
confirmed verbatim. But the paper adds: *"For items not collected in the 2024 wave, we use
the most recent prior wave with identical wording,"* naming **four items from GSS 2022**
(hours on the web; online health information search; perceived service quality in
restaurants; attitudes toward family life and women's full-time work). A source line
reading "vs. GSS 2024, CPS 2024, Pew 2023" is defensible. "All benchmarks are 2024" is not.
Worth a footnote on the Papers page and a clause in C-003.

**D-6 — the year appears in two places that are supposed to be year-free.** `AGENTS.md`
says every source line reads "Donati & Rao" with no year until settled. But C-054's source
column reads **"Donati & Rao (2025), title footnote"**, and `DESIGN.md` §2's provenance
example prints **"Donati & Rao, 2025"**. Harmless if §1 is accepted (2025 is the answer)
— but until it is called they are unsanctioned.

**D-7 — two different Prolific costs.** Table `costs` says **$0.095**; the text says
**"about $0.10"**. C-013 uses ~$0.10, which is the text. Fine, but DESIGN.md §2 rule 6 is
*"never round differently in two places"* — pin one and say which it is. (Moot on the
public site now that C-004 is withdrawn; still needed inside `CLAIMS.md`.)

**D-8 — C-006/C-007's caveat cites the wrong figure, and its weighting is inferred.**
The per-domain numbers in the caveat are **all correct** (Prolific 6.7 vs our 8.8 on
internet use; 6.2 vs 7.0 on social issues; twins 3.2 vs our 5.0 on SES; trust 10.5 — every
one verified). Two corrections:
   - They do **not** come from `fig:MAD-comparison`, which C-006/C-007 cite. They come
     from the prose around **`fig:MAD-categories-comparison`**, a different figure.
   - **The paper never labels those per-domain values weighted or unweighted.** Every
     Meta value matches the *weighted* column of `tab:mad_outcomes` to the stated
     precision and several do not match the unweighted column, so weighted is near
     certain — but it is our inference, not the paper's statement. `paper.json` records it
     as `"weighted -- INFERRED, NOT STATED"`. Don't print "weighted" beside them without
     an author's confirmation.

**D-9 — the largest exposure on the site, and it is on C-006.** ⚠️

`CLAIMS.md` calls the comparative claim *"the strongest asset the site has."* It is also
the one with a live problem.

The paper reports **no inference of any kind** on the MAD comparison (§3). The paper
repo's own `PLAN.md`, recording a **July 2026 research session**, states the number the
manuscript does not:

> **Report Meta−Prolific honestly: −0.62 p.p., 95% CI [−1.24, +0.08] — not significant
> weighted.** Significant unweighted (−0.69) and vs twins (−4.75).

So on the **weighted** figures the Home page leads with — 6.1 vs 7.1 — **the difference
from Prolific is not statistically distinguishable from zero**, by the authors' own
current analysis. The gap against digital twins (C-007) is robust; the gap against
Prolific is not. The same document records that the reviewers made this exact objection
and that the authors intend to re-issue every CI.

This is not drift in the ordinary sense — C-006 faithfully reports what the manuscript
says. It is worse: **the manuscript's claim is one the authors are already retreating
from, and we would be publishing it after that became known internally.** A buyer's
methodologist who reads the eventual revision finds us leaning on a difference the authors
withdrew.

The good news is that the paper's own ceiling sentence already handles it, and
`CLAIMS.md` already quotes it as the ceiling:

> *at least as representative as Prolific, and markedly closer than LLM digital twins.*

**"At least as representative as" is exactly what a CI of [−1.24, +0.08] supports.**
"~15% better" is not. Proposed: keep C-006 `VERIFIED` for the point estimates, and add a
publication rule that **the Prolific comparison ships as parity-or-better, never as a
percentage improvement**, with the reason recorded. C-007 needs no change. **Owner:
Nandan** — this is a judgment about how much of an internal document to let govern public
copy, and it is not mine to make.

**D-10 — C-042 cites the wrong paper.** The Italy / Covid-stereotypes row is sourced to
"the working paper", inside a register whose "The paper, as a source" section defines *the*
paper as *Adaptive Survey Sampling via Ad Platforms*. **Italy, "542 municipalities" and
"90 provinces" appear nowhere in any edition of it.** They come from a different working
paper — `index.html` attributes that study to *Donati D., Gars J., and Rao N.* Name it, or
C-042 is unsourced by the register's own standard.

**D-11 — heads-up, not drift.** `PLAN.md` states that the July 2026 session produced
results that *"change several published claims"*, and names one: the dynamic-improvement
figure, corrected to **26% weighted / 8.5% unweighted**, against the **41%** the
manuscript prints (0.103 → 0.061 from n=100 to n=1,500). **41% is not in `CLAIMS.md`
today.** It is a tempting number and it is already superseded. If anyone proposes adding
it, the answer is no.

---

## 5 · Proposed `CLAIMS.md` edits

Row replacements — source column only unless marked:

```
| C-003 | Mean absolute deviation from gold-standard benchmarks | 6.1 p.p. | Donati & Rao,
  Fig. `MAD-comparison` — weighted; 6.2 p.p. unweighted. vs. GSS 2024, CPS 2024, Pew 2023
  (four GSS items are drawn from the 2022 wave — see note) | `VERIFIED` | 2026-08-20 |

| C-004 | Cost per question per respondent (US) | **Withheld — not published** | Abstract
  says $0.30; Table `costs` and the Cost Considerations text compute $0.32. Resolved
  2026-08-20: no cost-per-question figure ships. | `WITHHELD` | 2026-08-20 |

| C-008 | Prolific MAD, point estimate | 7.1 p.p. weighted (7.3 unweighted) | Donati & Rao,
  Fig. `MAD-comparison` and the paragraph following it. n=1,197, fielded Jun–Jul 2025 |
  `VERIFIED` | 2026-08-20 |

| C-042 | Italy — Covid stereotypes | 542 municipalities · 90 provinces | **Donati, Gars &
  Rao (working paper)** — NOT *Adaptive Survey Sampling via Ad Platforms*, which does not
  mention Italy | `VERIFIED` | 2026-08-20 |
```

`C-004` needs a status value the table does not have. Proposed addition to the status
legend:

```
| `WITHHELD` | Sourced and true, but a decision has been taken not to publish it. Must not be published. |
```

That is a real category and it is not `PLACEHOLDER` (which means *not obtained*). C-015 is
already being used this way ("NOT FOR PUBLICATION") without a status to match.

**"The paper, as a source" — replacement text:**

```
Rows above cite the **September 2025** manuscript. All four editions in
`../../../survey-sampling-with-ads/paper/` carry `\date{September 15, 2025}`:

  survey-sampling-with-ads-Jul2026.tex   working manuscript, live revision, bylined
  JMR_submission_09152025.tex            as submitted to JMR — blinded, no byline
  SSRN_09152025.tex                      SSRN edition, bylined
  survey-sampling-with-ads-Jan2025.tex   fourth edition, near-identical to SSRN

**Every figure cited above is identical in all of them** (verified value by value,
2026-08-20), so the edition matters for what we *link*, not for what we *claim*. Cite
2025 — the date every edition prints. The "2026" in the first filename is a working label;
that file dates itself 2025.

**Do not cite a journal.** The manuscript is JMR-25-0847, under a major revision. No
SSRN ID, DOI or public URL exists in any edition or in the paper repository.
```

**"Refreshing the placeholders" — replacement for the first paragraph:**

```
**C-008, C-009 — comparator point estimates.** In
`../../../survey-sampling-with-ads/paper/survey-sampling-with-ads-Jul2026.tex`,
**Figure `fig:MAD-comparison`** and the paragraph immediately following it — the values
are in the prose, not in a table. There is no Table 4. The per-domain three-way values
behind the C-006/C-007 caveat are in the paragraph preceding Figure
`fig:MAD-categories-comparison`. `tab:mad_outcomes` is Meta-only; do not read comparators
out of it.
```

**Add to the C-006/C-007 note:**

```
**Publish the Prolific comparison as parity-or-better, never as a percentage.** The paper
reports no standard error, confidence interval or significance test on any MAD, and the
authors' own July 2026 analysis puts Meta−Prolific at −0.62 p.p., 95% CI [−1.24, +0.08] —
not significant weighted. The gap to digital twins is robust; the gap to Prolific is not.
The paper's own sentence is the ceiling and it is also the safe floor: *at least as
representative as Prolific, and markedly closer than LLM digital twins.*
```

---

## 6 · Proposed `CONTENT.md` edit — Home §4

The spec currently reads:

> Interval rows (motif M3), our estimate in `--data`, comparators in `--ink-3`

Replace with:

> Bar comparison on one shared 0–12 p.p. scale (`assets/figures/mad-comparison.svg`), our
> estimate in `--data`, comparators in `--ink-3`, M4 tick rule carrying the graduations.
> **Not M3.** The paper reports no interval, standard error or significance test on any
> MAD; M3 "appears only where a real interval exists" (DESIGN.md §6). On the ink band the
> figure takes `.inv`, which swaps to `--data-inv` and `--on-invert-2`.

And in the Papers spec, "the cost table" needs qualifying — see the knock-on in §2.

## 7 · Proposed `AGENTS.md` edit

"Known drift" currently reads: *"The citation year is unresolved — manuscript July 2026,
submission 2025."* The premise is wrong (D-4). Replace with:

> **The citation year is 2025** — every edition, including the one filenamed `Jul2026`,
> carries `\date{September 15, 2025}`. What is unresolved is what a reader can *open*:
> no SSRN ID, DOI or public URL exists. Source lines may read "Donati & Rao, 2025" once
> D-016 settles where the PDF lives. See `scratchpad/ws-paper.md` §1.

---

## 8 · Things `paper.json` deliberately records as missing

Never invent a figure. These are real gaps, marked as such in the file:

| Wanted | Status |
|---|---|
| BibTeX entry | **Constructed, not found.** No entry exists in either `.bib` tree. Its `year` is a placeholder and it has no `url` — do not publish it until §1 closes |
| Digital-twins sample size | **Not stated.** The paper says only "a similar number of synthetic respondents" |
| Number of questions in the cost denominator | **Not stated.** Recorded with the arithmetic reconstructions, all marked unpublishable |
| Any interval, SE or p-value on a MAD | **Does not exist** (§3) |
| SSRN ID / DOI / public URL | **Does not exist** in anything we hold |
| Weighting of the per-domain three-way values | **Inferred, not stated** (D-8) |
