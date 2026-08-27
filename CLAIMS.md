# Claims Register

Every factual claim `vlab.digital` is permitted to make, with its source and
verification status.

**The rule:** no number, comparison, or superlative reaches a public page unless it
has a row here marked `VERIFIED`. If you need a figure that is not here, add a
`PLACEHOLDER` row, render `—` on the page, and tell the user what is missing. Never
invent a value — not even "for now."

**Why this file exists.** The entire brand proposition is that Virtual Lab does not
overclaim. `DESIGN.md` enforces that visually (the provenance rule: every figure
carries its source in the same visual unit). This file enforces it factually. A
plausible-looking number with no source is the single most damaging thing that can
reach this site, because it discredits every number beside it.

### Source or Definition — which column a table has, and why it matters

**Added 2026-08-26, and it is now load-bearing rather than cosmetic.** The tables in this
file differ in their fourth column, and that difference decides whether a figure on the
site must carry a visible citation:

| Fourth column | Means | On the page |
|---|---|---|
| **Source** | Where **somebody else** published it — Donati & Rao, a working paper, an IRB footnote, our own repos and docs | **Carries its citation**, in the same visual unit |
| **Definition** | How **we** computed it from **our** data | **Carries nothing** |

Nandan, 2026-08-26: *"We are the ones claiming the data. Nobody cares where it comes from.
They're assuming we have access to our own data."* A line reading "Virtual Lab production
database" under a Virtual Lab figure cites nothing a reader could check — and printing it
beside a real citation devalues the real one.

**`scripts/check-claims.py` reads this distinction from the table header**, not from the
markup, because whether a claim is somebody else's is a fact about the claim and a page
must not be able to talk its way out of a citation. **It fails safe:** exemption requires
a `Definition` column, so a new row added to a `Source` table is enforced by default.

**Adding a table?** Pick the column name deliberately. `Definition` on a third-party claim
silently removes its citation from every page that uses it.

**A definition is not an attribution and is never removed.** The box plots' caption lines
— what an *active day* is, what the box spans — stay, because they tell a reader something
about the number rather than about us.

**Status values**

| Status | Meaning |
|---|---|
| `VERIFIED` | Traced to a named source. Safe to publish. |
| `STALE` | Was verified; the underlying source has since moved. Re-check before use. |
| `PLACEHOLDER` | Needed but not yet obtained. **Must not be published.** |
| `WITHHELD` | Traceable or not, a decision has been taken that it does not go on the site. **Must not be published**, and unlike a placeholder it is never coming back without reopening the decision. |

---

## Headline figures

| ID | Claim | Value | Source | Status | Checked |
|---|---|---|---|---|---|
| C-001 | Studies run | 33 | Donati & Rao, abstract — reads "over 33"; publish as "33" or "33+", never a higher number | `VERIFIED` | 2026-08-20 |
| C-002 | Countries | 23 | Donati & Rao, abstract | `VERIFIED` | 2026-08-20 |
| C-003 | Mean absolute deviation from gold-standard benchmarks | 6.1 p.p. | Donati & Rao, Fig. `MAD-comparison` — weighted; 6.2 p.p. unweighted. vs. GSS 2024, CPS 2024, Pew 2023 — four GSS items are drawn from the 2022 wave, see below | `VERIFIED` | 2026-08-20 |
| C-004 | Cost per question per respondent (US) | **Not published** | Source contradicts itself: abstract says $0.30, Table `costs` and the Cost Considerations text compute $0.32 | `WITHHELD` | 2026-08-20 |
| C-005 | US validation sample size | 1,500 | Donati & Rao, abstract | `VERIFIED` | 2026-08-20 |
| C-006 | Comparison with a leading online panel (Prolific) | **Not published** | Traceable to Donati & Rao, Fig. `MAD-comparison`. Decided against — the site makes no comparative claim against another recruitment source. See below | `WITHHELD` | 2026-08-20 |
| C-007 | Comparison with LLM digital twins | **Not published** | Traceable to Donati & Rao, Fig. `MAD-comparison`; twins from Twin-2K-500 (Toubia et al.). Decided against — same rule as C-006 | `WITHHELD` | 2026-08-20 |
| C-008 | Prolific MAD, point estimate | **Not published** | Donati & Rao, Fig. `MAD-comparison` and the paragraph immediately following it — the values are in the prose, not in a table. Point estimate recorded below, deliberately out of the row | `WITHHELD` | 2026-08-20 |
| C-009 | Digital-twin MAD, point estimate | **Not published** | Donati & Rao, Fig. `MAD-comparison` and the paragraph immediately following it. Point estimate recorded below, deliberately out of the row | `WITHHELD` | 2026-08-20 |
| C-010 | Total respondents surveyed, all time | — | **Superseded — read the C-010 row under "Production figures" instead, which is `VERIFIED` at 841,660.** This row is the state before the database was queried on 2026-08-20; it is kept because the ID is permanent | `PLACEHOLDER` | — |
| C-011 | Typical field time | "typically two weeks" | **Superseded — read the C-011 row under "Production figures" instead, which is `VERIFIED` at 14 days planned · 19 days actual.** Was unsourced operator knowledge; the computed median it asked for now exists | `PLACEHOLDER` | — |
| C-012 | Cost vs. gold-standard probability surveys | **Gold standard runs $3.00 (GSS traditional) and $6.67 (GSS Follow-on)** per question per respondent; we are far below both | Donati & Rao, Table `costs`. Stated without our own operand — C-004 is `WITHHELD` | `VERIFIED` | 2026-08-20 |
| C-013 | Cost vs. Prolific | **We are ~3× more expensive** than Prolific's ~$0.10 per question per respondent | Donati & Rao, Table `costs` and Cost Considerations — the paper states the multiple in words. Stated without our own operand — C-004 is `WITHHELD` | `VERIFIED` | 2026-08-20 |
| C-014 | Advertising cost per participant, US study | $6.30 mean (range $0.70–$20 by stratum); $11.60 per participant including the $5 incentive | Donati & Rao, Cost Considerations | `VERIFIED` | 2026-08-20 |

**Two IDs appear twice in this file, and only one of each is live.** C-010 and C-011 have
a superseded `PLACEHOLDER` row above and a `VERIFIED` row under "Production figures". The
`VERIFIED` rows are the claims; the rows above are kept because a `C-nnn` number is
permanent and deleting one would make every reference to it ambiguous.
`scripts/check-claims.py` resolves the pair the same way — latest `Checked` wins, an
undated row loses to a dated one — and prints a `note` line naming each supersession on
every run. **If you are reading a row here to decide whether a figure may be published,
check you are not reading the superseded one.**

### C-003 is quote-only from 2026-08-25 — the site states no accuracy figure in its own voice

**Nandan, 2026-08-25:** *"I don't think we should put this 6.1 percentage points anywhere on
the front page. That really belongs in another page or maybe it doesn't belong anywhere on
the website. Now it can stay in the paper."* Settled at the narrower reading: **6.1 p.p.
appears on the site only inside the quoted abstract on the paper surface**, attributed to
Donati & Rao — exactly the treatment the withheld $0.30 gets. **The site makes no accuracy
claim in its own voice anywhere.**

**The reasoning, and it is not squeamishness.** A bare 6.1 p.p. is a figure a reader cannot
evaluate. Knowing whether it is good requires knowing that probability samples run about
3 p.p. and online opt-in samples 4.5–7.4 — and that context is precisely what D-023 closed
off. So publishing the number in our own voice asks a reader to be impressed by a value
while refusing them the yardstick. **The hero still claims "population-representative
samples"; what substantiates it is the published method and the citation**, which is how
the claim is made everywhere else in research.

**C-003 stays `VERIFIED` and is deliberately NOT made `WITHHELD`, and the reason is the
documented tolerance trap.** A withheld row contributes every numeral in it to the banned
set, matched at ±2%. **Banning 6.1 would ban every bare `6` on the site** — 6.1 × 0.98 =
5.98, so the integer 6 falls inside the window — and the site has six regions, six surfaces
and a §6. This is the same failure that took C-008 and C-009 out of their Value cells; see
that note. **The discipline here is therefore human, not mechanical:** the row is
publishable, and the rule that it is publishable *only as quotation* lives in this
paragraph and in `COPY.md`.

**What this changed on the page.** The Home validation ink band is gone, and with it Part 2
beat two. `assets/figures/mad-comparison.svg` is built and is now unused on Home; it belongs
to the paper surface if that surface ever states the figure in our own voice, which today it
does not.

### C-004 is `WITHHELD` — no cost-per-question figure in our own voice

The paper disagrees with itself. The abstract says **$0.30**; the Cost Considerations
section derives **$0.32** ($11.60 per participant ÷ questions) and Table `costs` prints
$0.32. Both are the same study.

**Resolved 2026-08-20 by Nandan: publish neither.** A figure our own source contradicts
is exactly the figure this register exists to keep off the page — printing either number
invites a reader to find the other one. This is not "render `—` until we decide"; the
decision is taken and the slot is closed. Reopening it requires the manuscript to be
corrected first.

**The knock-on is bigger than one number, and it lands on the Method page.** C-012 and
C-013 are both stated in *per-question* units, so printing either comparison prints the
withheld figure:

| | As recorded | Publishable? |
|---|---|---|
| C-012 | Gold standard at $3.00 / $6.67 per question, us far below | **Yes.** The GSS side stands alone; our operand is not printed. |
| C-013 | ~3× Prolific's ~$0.10 per question | **Yes.** The ratio stands; our operand is not printed. |
| C-014 | $6.30 advertising per participant, $0.70–$20 by stratum, $11.60 with the $5 incentive | **Yes, unaffected.** Per participant, not per question. |
| The paper's abstract, on Papers | **Yes — as attributed quotation only.** Verbatim, inside `data-claim-quote="C-055"`, with a visible attribution line, warned on every run. Never paraphrased, never quoted in part, never lifted out of the block. |
| The paper's cost table, anywhere | **No, permanently.** Every row is per question; reproducing it publishes C-004 four times over in our own voice. Quoting does not reach it. |

So the cost section is built on **C-014**, with the C-012 and C-013 comparisons kept as
*ratios* sourced to the paper's cost table rather than as printed operands. The honest
framing C-013 exists to protect — that we are not the cheap option — survives intact,
because it was never the absolute figure doing that work.

**One page reproduces the figure, and it is not an exception to any of the above.** The
Papers page carries the paper's abstract **verbatim, as attributed quotation**, and the
abstract states $0.30 per question. **A quotation is attributed speech, not a claim.**
This register governs what Virtual Lab asserts; reproducing what the paper says,
accurately, is the opposite of overclaiming, and a citation page that silently edited its
own paper's abstract would be the worse failure. Restored 2026-08-21 by Nandan — see
D-016 for the full record, including the reading it supersedes.

**The distinction is enforced, not asserted.** The block carries
`data-claim-quote="C-055"` — naming a `VERIFIED` row for the document being quoted — plus
a visible attribution line, and `scripts/check-claims.py` **reports the $0.30 at `warn`
level on every run**, naming C-004 as the row that withholds it. The shield stops a build
failing; it never stops a human seeing. See `DESIGN.md` §8, "Attributed quotation".

**What has not changed is everything else.** C-004 stays `WITHHELD` for every sentence the
site writes in its own voice, which is every sentence on the site except one quoted
paragraph. The cost table stays off the Papers page for a reason that survives the
reversal intact: **every row of it is per question, so reproducing it publishes the figure
four times over in a component whose job is to display values — that is not quotation.**

**Both rows were restated 2026-08-20 so that no `VERIFIED` row prints the withheld
figure.** They previously read "$0.32 vs $3.00 (GSS traditional) and $6.67" and "$0.32 vs
~$0.10", so the register simultaneously withheld the cost-per-question figure and
published it twice. `scripts/check-claims.py` caught it and resolved it the conservative
way — banned wins — but a register that says two things is documentation that cannot be
relied on. It now says one.

### C-013 is the trap in this section

We are **cheaper than gold-standard probability surveys and more expensive than
Prolific** — roughly 3× more. Any copy implying we are the cheap option is false and is
contradicted by our own paper, in a table, in public. The honest framing is **comparable
in cost to a convenience panel, and measured against gold-standard benchmarks** — the
paper's own framing continues "…and closer to the benchmarks than one", and **that half
does not ship**: it is the comparative claim D-023 withholds. Cost comparisons stay
because they are ratios from the paper's cost table and C-013 runs against us; an
accuracy comparison does not.

### C-006 to C-009 are `WITHHELD` — the site makes no comparison with another recruitment source

**Settled 2026-08-20 by Nandan: "Don't lead with any gap, we'll leave that off the
website entirely, no need to compare."** Recorded as D-023. All four rows are decided
against, not pending: they are not coming back without reopening that decision.

**The reason is that the two comparisons are not equally sound, and publishing one
without the other would be its own kind of claim.** The paper reports **no standard
error, confidence interval or significance test on any MAD** — searched across all four
editions, zero hits — so C-006 faithfully reported a point-estimate difference the
manuscript never tested. The authors' own July 2026 working session puts **Meta −
Prolific at −0.62 p.p., 95% CI [−1.24, +0.08] — not significant on the weighted
figures**, which are the ones a page would have led with, and records that the reviewers
raised this objection and that the authors intend to re-issue the comparison with
intervals. The gap to digital twins (C-007) is robust; the gap to Prolific is not.

So the register faced three options and took the fourth. Publishing both would publish a
comparison the authors are revising. Publishing only the twins gap would let the reader
infer that the panel comparison went the other way. Publishing the panel gap as
parity-or-better would be defensible and would still be a competitive claim resting on a
figure under revision. **The site does not compete on the comparison at all.** What it
publishes is its own accuracy against gold-standard benchmarks — C-003 — which is not a
claim about a rival and needs no rival to mean something.

**Scope, and it is narrower than "no comparison ever."** What is withheld is a
comparative claim about **representativeness against another recruitment source**.
Two things are deliberately outside it:

- **C-003 stays `VERIFIED` and publishable.** 6.1 p.p. against GSS, CPS and Pew is our
  own accuracy measured against gold-standard benchmarks, not a ranking against a rival.
  It is the substantiation of "the sample is defensible," which is the whole proposition;
  withholding it would leave the validation section with no evidence in it.
- **C-012 and C-013 stay `VERIFIED`.** They compare *cost*, they are stated as ratios
  sourced to the paper's own table, and C-013 runs **against** us — we are roughly 3×
  Prolific per question. An admission against interest is not a competitive claim, and
  removing it would leave the Method page claiming cost-effectiveness with the
  unflattering half deleted. If Nandan reads the decision as covering cost too, C-013 is
  the row to reopen first, because the Method cost section is built on it.

**A third thing is outside it, and it is the one that looks like a breach.** The paper's
abstract — reproduced verbatim on the Papers page since 2026-08-21, D-016 — contains the
sentence "improving on both the online panel provider and LLM-based approaches". That is
C-006 and C-007 in the authors' own words. **It ships only as part of the quoted
paragraph**, by the same reasoning that admits the withheld $0.30: a quotation is
attributed speech, not a claim, and the site still makes no comparative claim of its own.
**It may not be pulled out as a pull quote, restated in a heading, summarised in the clause
beneath the block, or repeated anywhere else on the site.** If any of that starts
happening, the abstract is being mined for claims rather than reproduced, and the response
is to reopen D-016 rather than to trim the quotation.

**What the manuscript's own figures were, kept for the record and not for the page.**
Aggregate MAD favoured us, but not in every domain: Prolific was closer on internet use
(6.7 vs 8.8 p.p.) and on attitudes to social issues (6.2 vs 7.0 p.p.), and digital twins
on socioeconomic status (3.2 vs 5.0 p.p. — the paper attributes this to employment status
being baked into the twin personas). Trust is the weakest domain for everyone; we are at
10.5 p.p. Those per-domain values come from the prose around Figure
`fig:MAD-categories-comparison`, not from `fig:MAD-comparison`, and **the paper never
labels them weighted or unweighted** — every one matches the weighted column of
`tab:mad_outcomes` to the stated precision, so weighted is near certain, but that is our
inference. None of this ships. It is here so that an agent who finds the figures in the
paper knows they were read and ruled out, rather than assuming they were missed.

**The comparator point estimates, for the record and not for any page.** Prolific **7.1
p.p. weighted (7.3 unweighted)**, n=1,197, fielded June–July 2025; digital twins **11.1
p.p. weighted (12.0 unweighted)**, with no n stated in the paper for that arm.

**Why they sit in prose rather than in the Value cells, which is not the C-004 pattern.**
A `WITHHELD` row contributes every numeral in the row to `check-claims.py`'s banned set,
and a banned value is matched with a tolerance of ±2% — so **banning 7.1, 11.1 and 12.0
also fails every bare 7, 11 and 12 on the site.** Tried once, it fired on three
privacy-policy section headings and on a legitimate country count. C-004 can keep $0.30
and $0.32 inside its row because dollar values at that precision collide with nothing;
these cannot. **The protection is not lost:** a page that declares `data-claim="C-006"`
through `"C-009"` fails on the claim id whatever the value, and a page that prints 7.1 or
11.1 without declaring anything fails as `unsourced`, because neither number has a
`VERIFIED` row.

**One thing these rows must never do is restate 6.1.** A value that is both banned and
publishable stays banned, so putting our own figure into a withheld row would ban C-003
across the entire site.

**A consequence for the one MAD figure that remains:** because no interval exists,
**motif M3 may not be used to draw it** (`DESIGN.md` §6 — M3 "appears only where a real
interval exists"). `assets/figures/mad-comparison.svg` was redrawn 2026-08-20 as a single
bar carrying C-003 on the same 0–12 p.p. ruler; see `CONTENT.md`, Home §4.

---

## Production figures — operating scale

**Source for every row: Virtual Lab production CockroachDB, cluster `vprod`, queried
read-only 2026-08-20.** Queries are recorded under "Refreshing" so any of these can be
re-run and the date bumped. These are *operating* claims and belong to the production
database; the paper is the source for *validation* claims and nothing else. Do not cite
Donati & Rao for scale.

| ID | Claim | Value | Definition | Status | Checked |
|---|---|---|---|---|---|
| C-010 | Respondents, all time | **841,660** | Distinct `userid` in `chatroach.responses` — answered at least one question | `VERIFIED` | 2026-08-20 |
| C-015 | People reached, all time | 1,097,153 | Distinct `userid` in `chatroach.states` — entered a survey, may not have answered. **NOT FOR PUBLICATION — use C-010.** Recorded only to explain why `states` exceeds `responses`. | `WITHHELD` | 2026-08-20 |
| C-016 | Survey responses, all time | **17,979,910** | Row count, `chatroach.responses` | `VERIFIED` | 2026-08-20 |
| C-017 | Countries | **41** | Union of country targeting across both platforms, `vlab.study_confs` + `chatroach.campaign_confs` | `VERIFIED` | 2026-08-20 |
| C-011 | Field window, median | **14 days planned · 19 days actual** | Planned: `end_date − start_date` on the latest recruitment conf, n=137. Actual: first-to-last `adopt_reports` per study, n=116, IQR 8–90 days | `VERIFIED` | 2026-08-20 |
| C-018 | Operating since | **2020-02-13** | Earliest response in `chatroach.responses` | `VERIFIED` | 2026-08-20 |
| C-019 | Studies fielded, all time | **175** | 119 distinct `study_id` in `vlab.adopt_reports` (2022-07-29 → 2026-08-20) **+** 56 `chatroach.campaigns` rows. Definition settled by Nandan 2026-08-20 — see below | `VERIFIED` | 2026-08-20 |
| C-097 | Respondents attributable to a country | **738,608** of 841,660 | Sum of the per-country table below — 37 of 41 countries. Attribution method is `C-017`'s: stratum country targeting joined to response shortcodes on both schemas. The remaining 103,052 belong to studies whose strata carry **no country tag**, not to countries outside the 41. Counts are floors, not exact — see "Two limits on this table" below. **Added 2026-08-25**, when the coverage prose was built: the figure was already stated and sourced in that section but had no id, so the one sentence COPY.md §1.3 requires could not be annotated. **This is bookkeeping, not a new claim** — and it is not a precedent for the regional totals, whose objection is the *bucketing*, which is editorial. Country attribution is not | `VERIFIED` | 2026-08-20 |
| C-098 | Respondents by region | **MENA 311,363** · **Sub-Saharan Africa 143,816** · **Americas 136,558** · **South & Southeast Asia 113,460** · **Europe & Central Asia 30,573** · **Pacific 2,838** | Sums of the per-country table below, bucketed by `regions` in `scripts/data/coverage.json` and computed at build time by `build-coverage-map.py`. **Released for publication by Nandan Rao, 2026-08-26** — *"we need the region amounts!"* — which settles the bucketing question that had held this back since the build began. **Two of the six are floors; read the note below before quoting any of them** | `VERIFIED` | 2026-08-26 |

### The 41 countries

`AE BD BG BZ CG CM DE DJ EG GH GM HN HT ID IE IL IN IQ JM JO KE KG KW LA LB LY MA MD
MK NG PG PK PS RO RS SA TD UA US XK ZM`

**Respondents per country — 37 of 41 countries, 738,608 of 841,660 (87.8%).**
Attributed by joining stratum country targeting to response shortcodes on both schemas;
`C-017` records the method.

| | | | | | |
|---|---|---|---|---|---|
| US 103,475 | NG 88,460 | JO 79,915 | IQ 75,209 | BD 72,201 | LB 49,529 |
| AE 48,373 | EG 22,786 | PK 18,830 | KE 17,226 | HT 16,545 | IL 16,028 |
| ID 14,584 | ZM 11,923 | GH 9,307 | LY 8,460 | RS 7,669 | BG 7,563 |
| KG 7,235 | HN 6,933 | KW 6,571 | LA 6,202 | JM 6,006 | RO 5,024 |
| DJ 4,284 | TD 4,122 | SA 3,930 | CM 3,701 | BZ 3,599 | UA 2,853 |
| PG 2,838 | CG 2,519 | GM 2,274 | IN 1,643 | MA 562 | IE 206 |
| DE 23 | | | | | |

**No count yet: MD, MK, PS, XK.** Coverage is verified; the respondent figure is not.
Render these as coverage without a number — never as zero.

**Two limits on this table.** Counts are summed per country across both schemas, so a
person who took part on each would be counted twice; the overlap is expected to be
negligible but the totals are floors, not exact. And the 103,052 unattributed
respondents belong to studies whose strata carry no country tag, not to countries
outside the 41.

**Unresolved: the per-region totals have no row, and two workstreams disagree about
whether they need one.** The coverage section renders six regional figures — MENA,
Sub-Saharan Africa, Americas, South & Southeast Asia, Europe & Central Asia, Pacific.
They are **sums of the rows above**, computed at build time from
`scripts/data/coverage.json` rather than stored, which is the argument that they are
already sourced. But `scripts/check-claims.py` matches values, not derivations, so it
fails on every one of them, and the register does not currently say a regional figure is
publishable.

**Not resolved here, because the bucketing is the real question and it is not ours.**
Region composition is an **editorial choice made in `coverage.json`**, not a fact from the
database: the MENA bucket includes Israel, and a buyer in Amman and a buyer in Tel Aviv
will each read that grouping as a statement. A `VERIFIED` row would settle that choice by
implication. **Before the coverage section ships, either the buckets are confirmed and the
six totals get a row, or the section publishes country figures and drops the regional
layer.** Owner: Nandan. Note that each regional figure is also a **floor** wherever its
region contains a country with no count.

### Publication rules for scale figures

1. **Publish respondents (C-010), never people reached (C-015).**
2. **Never mention platforms, schemas or migrations in public copy.** The split between
   `vlab` and `chatroach` is an implementation detail of ours, not a fact about the work.
   Public copy says respondents, responses, countries — nothing else.

### C-019 — the definition, now settled

`vlab.studies` holds 194 rows, but only 119 have recruitment reports; the rest are tests
and abandoned configs. The older platform adds 56 campaigns. The defensible range was
therefore 119 to 175, depending on whether older-platform campaigns count as "studies"
and whether a study that recruited briefly counts.

**Settled 2026-08-20 by Nandan: 175** — 119 plus the 56 older campaigns. A study that
recruited is a study, and work does not stop counting because the software underneath it
was replaced.

**Publishing it is constrained by publication rule 2 below.** The definition above names
two platforms, and public copy may not. On a page, 175 is *studies fielded since 2020*,
sourced to the production database and its `as_of` date — never explained by a platform
split, never sourced to Donati & Rao, whose "over 33" counts only the studies described
in the paper.

### C-011 supersedes the "typically two weeks" line

The operator estimate was close but slightly optimistic. Planned windows have a median
of 14 days; what actually ran has a median of **19 days**, with a long right tail from
longitudinal studies (p75 = 90 days). **Publish the actual, not the planned.** "Half of
studies field in under three weeks" is true; "typically two weeks" is not quite.

### Recruitment throughput — C-089 and C-090, added 2026-08-22

**Source: Virtual Lab production CockroachDB, cluster `vprod`, queried read-only
2026-08-22.** Query in "Refreshing the placeholders". Added because the field window
(C-011) is a **design choice** and throughput is a **capability** — a longitudinal panel
and a one-week cross-section have very different windows and can recruit at the same rate.
Nandan, 2026-08-22: *"Fielded in three weeks. I don't think that's really the right way to
frame this."*

| ID | Claim | Value | Definition | Status | Checked |
|---|---|---|---|---|---|
| C-089 | Respondents recruited per study on an active recruitment day | **median 140** · IQR **69–300** · p10 41 · p90 531 | Distribution **across 129 studies**, each represented by its own median active day. An *active day* is a study-day on which at least **20** respondents were recruited | `VERIFIED` | 2026-08-22 |
| C-090 | Active recruitment days per study | **median 11 days**, over which the median study recruits **2,483** respondents | Same population as C-089 | `VERIFIED` | 2026-08-22 |

**Definitions, and they are load-bearing.**

- **"Recruited on day D"** = the date of a respondent's **first response within that
  study**, UTC. Verified rather than assumed: `vlab.inference_data.timestamp` **is** the
  respondent's first response timestamp — p10, p50 and p90 of the difference against
  `chatroach.responses` are all exactly `0` across n=18,970 respondents belonging to
  exactly one study.
- **The ≥20 floor is an analyst's choice and must be published as one.** It strips days
  where a study was idle, ramping or trickling, so C-089 describes *a day of active
  recruitment*, not an average day in the field. **It is not sensitive:** at a ≥10 floor
  the median is 121 and the IQR 47–268, against 140 and 69–300 at ≥20.
- **C-089 is the distribution across studies, not across study-days.** The study-day
  distribution is lower — median 88, IQR 41–257 over 2,484 study-days — because long slow
  studies contribute many days each and drag the pool down. **Weight each study once**;
  that is the number a buyer applies to their own study.

**The trap in this section, and it is a data defect rather than a judgment call.**
`vlab.inference_data` writes a respondent into **every study of an umbrella group**. Six
studies named *Embed Jordan · Iraq · UAE · Egypt · Morocco · KSA* each report an identical
**5,253** respondents on 2026-01-07; 26,031 distinct people generate 133,110
study-respondent pairs across those six rows. Platform-wide this is a **1.67× inflation** —
480,091 study-respondent pairs against 287,049 distinct respondent-days. **Every figure in
C-089 and C-090 assigns each respondent to one study per day.** Uncorrected, the study-day
median reads 77 instead of 64 on the current platform and every total inflates by two
thirds. **Any future re-run must apply the same de-duplication or it will not be comparing
like with like.**

**Three floors travel with these rows.**

1. **Coverage is 78.5%.** 660,699 of the 841,660 respondents (C-010) sit on qualifying
   days. **46 of the 175 studies never had a day with 20 attributable recruits** — small
   studies, pilots, and studies whose respondents cannot be attributed.
2. **Attribution differs by platform, and one method had to be abandoned.** The current
   platform uses `inference_data`, which is unambiguous. Shortcode attribution is
   **unusable** there — 57 of its 140 entry shortcodes are shared across studies. The older
   platform uses campaign stratum shortcodes, of which 8 of 107 map to more than one
   campaign.
3. **The two platforms overlap 2022-12-09 to 2023-04-19** and a respondent is not
   de-duplicated across them.

**One split a single pooled number hides, and it is real.** The older campaigns recruited
**faster** — median campaign-day 208, p90 1,139 — against the current platform's 64 per
study-day. C-089 pools both, so it averages over a genuine change in how studies are run.
**Not published as a trend**, in either direction: nothing here establishes why, and a
"we got slower" reading is as unsupported as its opposite.

### Advertising cost per respondent — C-091, added 2026-08-25

**Source: Virtual Lab production CockroachDB, cluster `vprod`, queried read-only
2026-08-25.** Query in `scripts/data/ad-cost.json`. Added on Nandan's instruction: *"We
shouldn't use the costs from the US validation study... what we want to show is ad costs
just in advertising spend itself."*

| ID | Claim | Value | Definition | Status | Checked |
|---|---|---|---|---|---|
| C-091 | Advertising cost per respondent newly recruited, per study | **median $1.05** · IQR **$0.29–$1.57** · p10 $0.09 · p90 $3.67 · full range **$0.04–$8.89** | Distribution **across 44 studies**. Facebook Insights `spend` for the study's campaigns, over the respondents that study recruited for the first time | `VERIFIED` | 2026-08-25 |

Pooled: **$166,243** of advertising over **163,555** newly recruited respondents.

**This is advertising spend and nothing else.** Not the incentive, not the survey platform,
not our fee. **It is not a price and must never be published as one** — a page that lets a
buyer read $1.05 as what a respondent costs them has misled them by a factor nobody here
has computed. Every rendering states "advertising only" in the same visual unit.

**The unit is the study, and country was tried first and rejected.** Nandan, 2026-08-25:
*"in Nigeria, for example, some studies were much cheaper and some more expensive."*
Correct, and decisively so: **Nigeria's twenty studies run from $0.04 to $8.89** while the
country average is $4.74. The country figure was an average over a 222× spread, and it
reported the most expensive country in the set as though that were a fact about Nigeria
rather than about which studies we happened to run there. **A country average here destroys
exactly the information a buyer needs.** The rejected country values are kept in
`ad-cost.json` under `context_not_published` so the reasoning can be re-checked; they do
not render.

**Definitions, and the denominator is the one that took two attempts.**

- **Newly recruited** = a respondent whose **first appearance in any study** is in this one.
  The first attempt counted every respondent a study held, which is wrong: **a baseline and
  its endline share a panel**, so the endline showed near-zero cost per respondent for
  people the baseline paid to recruit. That defect is what sent the analysis to country
  level; fixing the denominator is what brought it back to the study.
- **Spend** is the maximum reported cumulative `spend` per campaign, stratum and
  ad-platform day. The max, not the sum: `recruitment_data_events` carries settled daily
  rows (`temp=false`) **and cumulative intra-day snapshots** (`temp=true`), so summing every
  row double-counts — $830,038 against a true $483,847 across all countries.
- **Campaigns appearing under more than one `study_id` are dropped** — 7 of 157. Summing
  them per study counted the same spend twice.

**Three exclusions, all of them published in the figure's own source line or here.**

1. **At least 200 newly recruited respondents**, so a pilot that recruited nine people
   cannot produce a headline cost.
2. **At least 80% of a study's first-appearance respondents must be uniquely its own.** This
   removes **umbrella study groups** — sets of rows sharing one respondent set, of which the
   six *Embed* studies are the clearest case. The split is cleanly bimodal: **57 studies are
   above 80%, 55 are below 20%, and almost nothing sits between**, which is what makes the
   threshold a description of the data rather than a choice about it. Without it, *Embed
   UAE* reports **$103.65** per respondent — $30,161 of real spend over 291 respondents the
   join could not attribute.
3. **Current platform only.** `recruitment_data_events` begins **2022-07-26**; the older
   campaigns carry no spend rows in this schema.

**Nigeria is 61% of all advertising spend** and holds both extremes of the range. Not
published as a statement about Nigeria, and no explanation is offered that the register
cannot source — the expensive end is state-level HPV and MNCH work.

### Operating the campaign — C-092 and C-093, added 2026-08-25

**Source: Virtual Lab production CockroachDB, cluster `vprod`, queried read-only
2026-08-25.** These exist because Part 2's problem is operational rather than statistical:
*"really it's a logistical and operational challenge and a reliability of getting what they
want"* (Nandan, 2026-08-25).

| ID | Claim | Value | Definition | Status | Checked |
|---|---|---|---|---|---|
| C-092 | Budget reallocations per study | **median 61** · p75 165 · p90 351 · max **1,308** · 17,596 across 109 studies | Count of `report_type='FACEBOOK_ADOPT'` rows in `vlab.adopt_reports`. One row is one reallocation across every stratum, carrying each stratum's current budget, participants, price per participant and desired share | `VERIFIED` | 2026-08-25 |
| C-093 | Strata per study | **median 6** · p75 11 · p90 18 · max **120** · 1,413 across 135 studies | Length of the latest `strata` conf array per study in `vlab.study_confs` | `VERIFIED` | 2026-08-25 |

**C-092 was wrong once and the error is instructive.** Counting every row of `adopt_reports`
gives a median of 84, but the table holds three report types — `FACEBOOK_ADOPT` (17,596),
`cost_over_time` (7,244) and `respondents_over_time` (7,226). **Only the first is a
decision; the other two are monitoring.** Always filter by `report_type`.

**C-093 kills a framing before it reaches a page.** "Researchers juggling hundreds of ad
sets" is not supported: **the median study has six strata**, and only the top decile passes
eighteen. The honest axis is **frequency, not cardinality** — six cells rebalanced sixty-one
times over a nineteen-day median window (C-011). Any copy reaching for "hundreds of ad sets"
is reaching for a number this register does not have.

**Neither row says a human could not do this.** They say what the work is. A claim about
what a researcher can or cannot manage by hand would need evidence about researchers, which
we do not have.

### C-092 needs two more percentiles before it can be drawn

**Open, 2026-08-26, and it is one read-only query.** C-092 carries **median · p75 · p90 ·
max**. The site's box-plot form needs **p10 · p25 · median · p75 · p90** — the box spans the
interquartile range and the whiskers span the tenth to the ninetieth — so **p10 and p25 are
missing** and the figure cannot be drawn.

Nandan, 2026-08-26: *"If we want to include a box plot of budget reallocations, we can. That
may be nice. Try that as a third box plot."* Everything except the two values is built:
`scripts/data/reallocations.json` holds the query, and
`scripts/build-reallocations-figure.py` is complete and **exits 1 until they exist**.

**This is not a `PLACEHOLDER` row and C-092 does not change status.** What it already
records is `VERIFIED` and publishable; what is missing is two further percentiles of the
same distribution. Adding them extends the row, it does not replace it.

**Do not estimate them from the ones we have.** Percentiles are not derivable from other
percentiles, and a median of 61 against a p75 of 165 says nothing reliable about where the
25th falls.

### C-091 and C-014 do not contradict each other, and a page must not let them look as if they do

C-014 is **$6.30 of advertising per participant in the paper's US validation study**.
C-091's distribution has a **median of $1.05** across 44 production studies. Both are
`VERIFIED` and describe **different populations** — one US study with tight stratification,
against four years of production work in mostly cheaper countries.

**This is the C-004 shape and it is the trap to watch.** A reader who opens the paper and
then reads the site should not find two advertising figures differing sixfold with no scope
attached. **Whichever is published carries its population in the same visual unit.** With
the unit now the study rather than the country, the site publishes no US-specific figure at
all, which removes the sharpest form of the collision — but the range still contains values
far below $6.30 and the scope line is what does the work.

### How C-089 and C-011 reconcile, which is the reason to publish both

The median study has **11 active days** inside C-011's **19-day** median window. Roughly
six days in ten in the field are recruiting days, and the gap is idle time — approvals,
pauses, waves, weekends.

**This is the sentence that must never be written:** *a 2,000-respondent study fills in two
weeks at the median rate*. It divides a headline by a median, assumes no idle days, and is
contradicted by the 11-in-19 figure above. **Throughput sets an expectation; it does not
compute a delivery date.**

### C-001 and C-002 are now the narrow claims

The paper's "over 33 studies across 23 countries" describes *studies in the paper*.
Production shows 41 countries and 175 studies. Both are true of different populations.
Use the paper's numbers only when citing the paper; use C-017 and C-019 for operating
scale. Any page that reads "33 studies across 23 countries" as a scale claim is
understating the business. The Studies index opener did; it was replaced 2026-08-20 with
175 studies across 41 countries, sourced to production.

**Where these two rows appear: on the Papers page, inside the quoted abstract, and
nowhere else.** The abstract reads "over 33 studies across 23 countries" and is reproduced
verbatim as attributed quotation (D-016, restored 2026-08-21). Nothing on the site states
either number in its own voice.

**That makes the "say which population this counts" clause mandatory again**, and it is
the reason it exists. One clause, in our own voice and **outside the quoted block**, sits
immediately beneath it: *the abstract describes the thirty-three studies analysed in the
paper; our operating history is larger and is reported on the Studies index.* It must stay
outside the block — editing the abstract to fix a problem of ours is exactly what verbatim
forbids, and a clause of ours inside a quotation would inherit an exemption it did not
earn. Copy in `CONTENT.md`, Papers.

### One operating claim that is not a database figure

Recorded in this section because it is an operating fact about how the work is
delivered, and because the coverage copy leans on it.

| ID | Claim | Value | Source | Status | Checked |
|---|---|---|---|---|---|
| C-032 | Field presence in the four largest non-US samples | **No field office in any of them** | **Operator knowledge.** Nandan Rao, confirmed 2026-08-20 | `VERIFIED` | 2026-08-20 |

The four countries are the four largest samples outside the United States in the
per-country table above, largest first: **NG · JO · IQ · BD**. An earlier draft of that
list omitted Nigeria — the largest of the four — and named Lebanon instead; the corrected
list is the one above.

**Not published anywhere, as of 2026-08-22.** Nandan: *"let's remove the field office
stuff. No need to say that."* The row stays `VERIFIED` because the fact is true and may be
wanted again; what was withdrawn is its use in copy. It was always a fact in search of an
argument, and the argument it reached for is one of the banned framings below.

**This row licenses the fact, not a frame.** It does not support "where conventional
fieldwork cannot go" or any comparison with panels or field agencies; those need rows
this register does not have — and since D-023 the site makes no comparison with another
recruitment source in any case. See the note under C-006, and the framing rules in
`AGENTS.md`.

### C-098 settles the region buckets, and inherits two things it must carry

**The regional totals were held from the day the build started**, and not because the
arithmetic was in doubt — they are sums of a `VERIFIED` table. They were held because
**the bucketing is an editorial choice**, made in `scripts/data/coverage.json` rather than
derived from the database, and this register had no row saying a regional figure was
publishable. Nandan settled it on 2026-08-26: *"we need the region amounts!"*

**The sensitivity that kept it back has not gone away, and adopting the row adopts it.**
Recorded in this file before the row existed: **the MENA bucket includes Israel**, and a
buyer in Amman and a buyer in Tel Aviv will each read that grouping as a statement. Nothing
about publishing the figures resolves that — it commits to it. **If the grouping is ever
questioned, the answer is to change `coverage.json` and re-run, not to argue the point.**

**Two of the six are floors.** MENA contains Palestine and Europe & Central Asia contains
Moldova, North Macedonia and Kosovo — all covered, none with a computed count — so those two
totals are **at least** the figure shown. The page used to say so, in a per-cell marker and a
note; **both went on 2026-08-26** with the four countries themselves, because an apparatus
explaining a gap the reader cannot see is explaining nothing. **The fact lives here instead.**
It is not published, and a page that ever needs to be exact about MENA or Europe & Central
Asia must come back to this row first.

**The country count in each cell counts only countries with a value**, so the number and the
count describe the same set. MENA reads 10 countries, not 11.

**No source line.** C-098 sits in a `Definition` table — our own record — so §2 as amended
requires no citation. That is also why the old *"Region totals sum to 738,608 of 841,660…"*
line is gone: it was never a citation, it was a reconciliation between two internal
denominators.

### C-069's scope note was lifted on 2026-08-26, and C-077 was not

**The page now says this**, in the step list, in Nandan's own words:

> **Verifying the identity of each respondent** — because otherwise everyone on the internet
> will answer your survey many times over.

**That is the wording C-069's scope note forbade** — *"must never be written as a fraud or
duplicate-prevention claim"* — and it was raised before it was written. Nandan wrote it into
the page himself and asked for the change to be committed, which is the decision; the row is
updated here so the register and the page agree, on the rule he set when C-066 was reversed:
**update the register in the same breath.**

**What is now published:** the *mechanism plus its rationale*. One run per form per account,
and the reason that matters — an open web survey can be answered repeatedly by anyone.

**What C-077 still withholds, and it did not move:** any **measured or comparative** claim
about fraud, duplicate respondents or identity verification **against another recruitment
source**. No measurement exists; it is traceable only to a sales call in which the speaker
labels it an assumption and offers the figure as a guess, and the signed scope of that
engagement sells manual photo-ID review instead. **D-023 forbids the comparison
independently.** So: no rate, no percentage, no "better than", no named competitor.

**The line to hold from here.** *"Verifying the identity of each respondent"* is now
sanctioned as a description of what the platform account does. **A number attached to it is
not**, and neither is a comparison. If either is wanted, that is a measurement someone has to
run, and until they do it is the one thing this register exists to prevent.

### C-066 was reversed on 2026-08-26, and the reversal has a condition attached

**It was `WITHHELD` in the strongest terms this register uses.** The row read *"designed,
then deliberately deferred"*, cited a commit whose message is *"stop claiming we support
it"*, and named itself **the limit of the forward rule rather than an exception to it**:
*"Never publish, in any form, until it is built."*

**Nandan reversed it, 2026-08-26: _"Forget the ban."_** He is the operator and the decision
is his; the row is now `VERIFIED` and the capability is on the page. This entry exists so
that the reversal is a decision on the record rather than drift, because a page that
publishes what the register withholds is the exact failure the register exists to catch —
and `check-claims.py` would **not** have caught this one, since the claim carries no numeral.

**One thing is unresolved and it is a buyer's question, not a lawyer's.** The old row
recorded a mechanism: **the file itself is never stored — what is kept is a platform
reference that expires.** If that is still true, then *"respondents can send a photo"* and
*"you receive the photos"* are different claims, and only the first is supported. The copy on
the page states the first and nothing more.

**Before this is written any wider — a study card, a proposal, an email — confirm what a
researcher actually receives at the end of a study.** If the images are exportable, C-072 and
C-074 should say so and the cell can be strengthened. If a reference expires, that belongs in
the sentence, because a buyer who expects files and receives links has been misled by
omission.

### Instrument capability claims — Fly

**Merged 2026-08-21, when D-024 closed.** Fly is the survey instrument — the questionnaire
runs as a conversation inside a messaging app — and it is now **named on the site** and has
a page. These rows are what that page is allowed to say. They were produced by a workstream
that traced every one to source on `fly@main`, to a deployment manifest, or to
`docs.vlab.digital`; the working is in `notes/ws-fly-capabilities.md`.

**These are capability rows, not figures.** They follow the **C-050–C-053 pattern**:
non-numeric, `VERIFIED`, sourced to the repository. `check-claims.py` cannot check a
sentence the way it checks a numeral — a capability claim carries no digits — so the
discipline these rows impose is human, and the Source cell is where it lives. **Read the
scope note in a Source cell as part of the claim, not as a footnote to it.**

#### The forward rule — the site may run ahead of `main`, and how far

**Settled by Nandan, 2026-08-21:** *"Just because a feature isn't currently built doesn't
mean we shouldn't advertise it. If it's in a feature branch, or mostly done, it will be done
soon. Webpages should be 2–3 months ahead of live features."*

So a capability on a branch, merged but not yet enabled, or otherwise near-shipping **is
publishable**, and the rows below apply that. Three limits keep it from dissolving the
register:

1. **It applies to capabilities, and never to figures.** A number cannot run ahead of its
   measurement — there is nothing to be 2–3 months early *about*. Every rule in this file
   about numerals stands exactly as written.
2. **"Not built yet" is not the same as "pulled".** A feature that was designed, built and
   then **deliberately removed** is not ahead of the roadmap, it is behind a decision — and
   the decision is the evidence. C-066 is the case, and it stays `WITHHELD`.
3. **The row says where it actually is.** A row published ahead of production carries that
   in its Source cell, so the gap is visible to us even though it is invisible on the page.
   If the branch dies, the row is what tells the next person which sentence to pull.

#### Capability rows

| ID | Claim | Value | Source | Status | Checked |
|---|---|---|---|---|---|
| C-056 | What Fly is | The survey instrument: the questionnaire runs as a conversation inside a messaging app | `fly/README.md`; `docs.vlab.digital` → `content/fly/core-concepts.md`; source on `fly@main` | `VERIFIED` | 2026-08-21 |
| C-057 | Channels a respondent can answer in | **Messenger, WhatsApp, or a web form** | Messenger and WhatsApp are Fly's own: `fly/hermes/src/handlers.rs`; `fly/message-worker/{messenger_client.go,whatsapp_client.go}`; `fly/devops/values/production.yaml`. **The web form is a study-level destination, not a Fly channel** — the optimiser drives Typeform and Qualtrics as destinations (`docs` → `content/vlab/study-configuration/data_sources.md`), and Nandan settled the wording on 2026-08-21. **Never write that Fly runs a web form** | `VERIFIED` | 2026-08-21 |
| C-058 | Instagram as a survey channel | **Not published** | The outbound translator exists but the client is a stub returning a not-implemented error (`fly/message-worker/stub_clients.go`, `translator_instagram.go`), and there is **no inbound path at all**. This is early work, not near-shipping, so the forward rule does not reach it. **`docs.vlab.digital` asserts Instagram support in two places and is wrong — do not copy it** | `WITHHELD` | 2026-08-21 |
| C-059 | Delayed follow-up | A survey can pause and resume — after a fixed interval, at a set time, or at a time the researcher re-points while the study is live | `docs` → `content/fly/reference/timeouts.md`; `fly/dean/queries.go` (`Timeouts`, `FollowUps`); `dean` deployed in `production.yaml` | `VERIFIED` | 2026-08-21 |
| C-060 | Contact after the messaging window closes | Requires a template approved by the platform, per account and per language | `docs` → `content/fly/reference/timeouts.md`; `fly/documentation/utility-messages.md`, `whatsapp-templates.md` | `VERIFIED` | 2026-08-21 |
| C-061 | Incentives paid inside the conversation | **Mobile airtime top-ups and gift cards**, plus any provider reachable over HTTP | `fly/dinersclub/{reloadly.go,giftcards.go,http_provider.go}`; `fly/devops/values/production.yaml` (`DINERSCLUB_PROVIDERS`). **Scope: those three. Not "any incentive anywhere"** | `VERIFIED` | 2026-08-21 |
| C-062 | Data bundles and utility top-ups as incentives | Available alongside airtime and gift cards | `fly/dinersclub/dingconnect.go` — merged to `main` and tested; enabled on a staging branch. **Published under the forward rule: the provider is not yet enabled in production.** Pull this row if the integration is abandoned rather than shipped | `VERIFIED` | 2026-08-21 |
| C-063 | Randomised assignment to arms | Each participant's arm is a hash of the form and the participant, so assignment reproduces from the exported data | `fly/replybot/lib/typewheels/utils.js` (`randomSeed`, FarmHash fingerprint); `fly/replybot/lib/typewheels/form.js` (`getSeed`); `docs` → `content/fly/reference/seeds.md` | `VERIFIED` | 2026-08-21 |
| C-064 | Video delivered in-chat, with watching recorded | Play, pause, seek, completion and a heartbeat while playing are all recorded as events; the survey can hold until the video is played | `fly/moviehouse/`; `fly/dean/queries.go`; `fly/documentation/questions.md`. **Verified on Messenger; no WhatsApp path found in source.** Do not name a platform in the copy — say what the instrument does | `VERIFIED` | 2026-08-21 |
| C-065 | Links whose clicks are recorded | A link is sent as a button and the click is recorded against the participant | `fly/linksniffer/` (deployed, `production.yaml`); `fly/documentation/questions.md`. The current-generation syntax lives on a feature branch; the capability is reachable on `main` by the older syntax | `VERIFIED` | 2026-08-21 |
| C-066 | Collecting photographs from respondents | **A question can ask for a photo and the respondent sends one** | `fly/planning/inbound-media.md`. **Released for publication by Nandan Rao, 2026-08-26** — *"Forget the ban"* — reversing the 2026-08-21 `WITHHELD`. Operator knowledge, the same source type as C-032 and C-094–C-096. **Read the retention note below before writing another word about it** | `VERIFIED` | 2026-08-26 |
| C-067 | Multilingual studies | Each language is its own linked form; closed-ended answers are mapped to one base language as they are recorded, so a multilingual study exports as one dataset | `fly/devops/migrations` (`translation_conf`, `translated_response`); `trans/forms.go`, `trans/responses.go`; `fly/scribble/response.go`; `fly/formcentral/server.go`. **Scope: closed-ended answers only — free text is not mapped. Never write "full multilingual support"** | `VERIFIED` | 2026-08-21 |
| C-068 | Questionnaire messages in the respondent's language | Fly's own rejection, nudge and closing messages are set per form, not fixed in English | `docs` → `content/fly/reference/messages.md`; `fly/replybot/lib/generic-validator.js` | `VERIFIED` | 2026-08-21 |
| C-069 | One run of a form per account | A participant cannot restart a form the same account has already entered | `fly/replybot/lib/typewheels/machine.js` (`REFERRAL` branch, `_hasForm`). **Scope: one account. It says nothing about one person holding several accounts.** ~~must never be written as a fraud or duplicate-prevention claim~~ — **that clause was lifted by Nandan Rao, 2026-08-26; read "C-069's scope note was lifted" below before writing this anywhere** | `VERIFIED` | 2026-08-26 |
| C-070 | Attrition handling | Standing rules move participants who match a condition — including "has not answered for N weeks" — from one form to another, with the matched set previewable before the rule runs | `docs` → `content/fly/reference/bails.md`; `fly/exodus/`; `fly/documentation/bail-systems.md` | `VERIFIED` | 2026-08-21 |
| C-071 | Longitudinal studies | Forms chain to one another and carry metadata forward, so one participant runs a baseline and an endline months apart inside one study | `docs` → `content/fly/core-concepts.md`, `content/fly/reference/questions.md` §Stitch; `fly/README.md`. Consistent with C-011's long right tail | `VERIFIED` | 2026-08-21 |
| C-072 | The record of a study | Every message exchanged with every participant is recorded and exportable, alongside the response data | `fly/documentation/chat-message-logging.md`, `full-messages-export.md` | `VERIFIED` | 2026-08-21 |
| C-073 | Live field monitoring | Per-participant state, error classification and full transcript, with a flag for participants stuck repeating one question | `docs` → `content/fly/reference/monitoring.md`; `fly/documentation/dashboard-study-health.md`; `fly/dean/queries.go` | `VERIFIED` | 2026-08-21 |
| C-074 | Getting the data out | CSV export with preprocessing options, plus a keyed REST API | `docs` → `content/fly/reference/downloading-data.md`, `content/fly/reference/api/`; `fly/exporter/README.md`; `vlab_prepro/` | `VERIFIED` | 2026-08-21 |
| C-078 | What a survey can contain | The ordinary question types: free text, numbers, email, phone, dates, single-choice lists, dropdowns, picture choice, yes/no, consent, opinion and rating scales, statements and endings | `docs` → `content/fly/reference/questions.md`; `fly/replybot/lib/typewheels/`. **Scope: what a respondent can be asked. Platform limits on how choices render are documentation, not copy** | `VERIFIED` | 2026-08-22 |
| C-079 | Conditional logic | A question can branch on any earlier answer or hidden value — and/or conditions, nested as deep as the design needs, with equality, comparison and contains tests — and send the respondent anywhere in the form | `fly/replybot/lib/typewheels/form.js` (`jump`, `getCondition`, and the operator table in `funs`); logic is authored in Typeform and executed by Fly | `VERIFIED` | 2026-08-22 |
| C-080 | Piping | A question can quote an earlier answer or a hidden value in its own text, with transforms applied and chained | `docs` → `content/fly/reference/hidden.md`; `fly/replybot/lib/typewheels/form.js`. Values are escaped where they land inside a URL | `VERIFIED` | 2026-08-22 |
| C-081 | Answer validation | Invalid or out-of-range answers are rejected and the question is asked again; the rejection wording is set per survey, and therefore per language | `docs` → `content/fly/reference/questions.md` (`validate`), `messages.md`; `fly/replybot/lib/generic-validator.js`. Numerals written in Arabic-Indic, Devanagari, Bengali and Thai scripts are read as numbers | `VERIFIED` | 2026-08-22 |
| C-082 | Where a survey is authored | **In Typeform** — written there directly, or written in a spreadsheet and uploaded to it. Fly imports the form and runs it | `docs` → `content/fly/reference/creating-a-survey.md`. **Scope, and it is the one that matters: Fly has no question editor of its own. Copy must never imply a form builder we do not have** | `VERIFIED` | 2026-08-22 |
| C-083 | One design, every language | A study written in a spreadsheet carries the base language's logic into every translation automatically, so the design is programmed and tested once | `docs` → `content/fly/reference/creating-a-survey.md`; `vlab-research/upload-typeform`. Strengthens C-067, which is about how answers are recorded; this is about how the design is built | `VERIFIED` | 2026-08-22 |
| C-075 | Survey answers drive recruitment | The recruitment optimiser reads the survey's own answers to assign strata and decide who counts as recruited | `docs` → `content/vlab/study-configuration/data_extraction.md`, `data_sources.md`; `fly/documentation/referral-form-resolution.md` | `VERIFIED` | 2026-08-21 |

#### Study-design rows — the patterns the Designs page is built from

**Added 2026-08-22 when D-026 closed.** These are a **new kind of row**: not a figure and not
a capability, but a statement about **work we have done**. The closest precedent is C-042, a
study row sourced to a working paper. The rule the page is built on — *a design earns a slot
when we have run it* — is enforced here rather than in the copy: **a pattern whose row is not
clear does not ship, even though the page around it does.**

**Read the Source cell for clearance, not just for provenance.** Every named study on that
page needs D-007's per-engagement disclosure check, and the Source cell is where that status
lives.

| ID | Claim | Value | Source | Status | Checked |
|---|---|---|---|---|---|
| C-084 | The malaria paper, as a citable source | Donati, D., Rao, N., Orozco-Olvera, V., and Muñoz-Boudet, A. M., *Can Facebook Ads Prevent Malaria? Two Field Experiments in India*, World Bank Policy Research Working Paper 10967, 2024 | World Bank Reproducible Research Repository, catalogue entry for this paper, and the OpenKnowledge repository. Verified 2026-08-22. **Publish the year, not the month** — the reproducibility catalogue and a secondary listing disagree on it, and nothing needs the month | `VERIFIED` | 2026-08-22 |
| C-085 | Delivering a treatment into the feed | An intervention can be delivered through the ad platform to a randomised list, so that exposure is **guaranteed rather than assigned** — which separates a weak treatment from an unreached one | C-084's second, individual-level trial, run for exactly this reason after the cluster trial could not separate the two; our own technical proposal for the World Bank online-RCT work describes it as a method we pioneered and have used repeatedly. **This is a consequence of recruiting online and is not a Fly capability — never write it as one** | `VERIFIED` | 2026-08-22 |
| C-086 | Randomising when respondents share the treatment | Where an online sample can pass an intervention between its members, respondents who are connected are randomised at the level of the group they are connected within, and isolated respondents individually | The analysis plan of a media-campaign trial we ran, which specifies exactly this two-stage design and its rationale — network effects via phone and email sharing. **Clearance: the study is not cleared for naming on current information. The pattern may be described; the client, the country and every figure may not** | `VERIFIED` | 2026-08-22 |
| C-087 | Geographic cluster randomisation with contamination buffers | Clusters drawn from population density, with buffer zones sized to keep neighbouring clusters from contaminating one another | Described as an established method in our own technical proposal for the World Bank online-RCT work. **Not yet confirmed as fielded**, and the page's rule is that a design earns its slot by having been run. Promote when an engagement that used it is identified and cleared | `PLACEHOLDER` | 2026-08-22 |
| C-088 | A panel that reopens months later | One respondent runs a baseline and an endline inside a single study, in the same thread, without re-enrolling | The mechanism is C-071. The engagement is C-041, already named in this register as a two-wave study with a follow-up interval. **Clearance: the engagement is nameable; its figures are `PLACEHOLDER` and do not render** | `VERIFIED` | 2026-08-22 |

**C-085 is the row most likely to be written wrongly, and the error is a category error.**
Delivering a treatment in the feed is a consequence of **recruiting online** — it works
because the ad platform can be pointed at a list, and it would work with any survey
instrument on the other end. It is not something Fly does. A page that files it under the
instrument has misattributed the mechanism, which is the specific failure `DESIGN.md` §1's
three-part frame exists to prevent: **method, technology, and the designs built with both are
three different things, and a claim belongs to exactly one of them.**

**C-087 is `PLACEHOLDER` on purpose and it is the rule working.** The technique is real and
we describe it in proposals; what is missing is a fielded study to attach it to. Under D-026
that is precisely the difference between a pattern and an idea, and the register is where
that line is held rather than in someone's judgment about the copy.

---

### Comparative rows — both withheld, and the forward rule does not touch them

| ID | Claim | Value | Source | Status | Checked |
|---|---|---|---|---|---|
| C-076 | Completion rate against another survey mode | **Not published** | **No measurement exists.** Traceable only to a sales call and an uncited multiple in a proposal file. The paper reports the panel arm on cost only, and the client's own prior campaign points the other way | `WITHHELD` | 2026-08-21 |
| C-077 | Fraud, duplicate respondents or identity verification against another recruitment source | **Not published** | **No measurement exists.** Traceable only to a sales call in which the speaker labels it an assumption and offers the figure as a guess; the signed scope of that engagement sells manual photo-ID review instead. Comparator is another recruitment source, so **D-023** forbids it independently. Publish the one-run-per-account row above, which is the mechanism | `WITHHELD` | 2026-08-21 |

**Why the forward rule does not rescue these two, and the distinction is the important one
in this file.** A capability can be 2–3 months early because the thing being described is
*work in progress*, and a branch is evidence about a future the company controls. **A
comparison is a measurement**, and there is no branch on which a measurement is nearly
done — nobody has run it. Publishing one early would not be optimism about a roadmap; it
would be an invented figure, which is the single thing this register exists to prevent.

**Four of the eight capabilities described in conversation when D-024 opened came back
wrong.** Recorded because they will otherwise be restored from memory: *image collection*
does not exist (C-066); *"full multilingual support"* overstates it (C-067 — closed-ended
only); *watch-tracking* is verified on Messenger (C-064); and *micropayments* is precise in
the wrong direction — what exists is airtime top-ups, gift cards and an HTTP hook (C-061).

**C-078–C-083 were added on 2026-08-22, and the reason is worth recording**, because the
inventory had deliberately excluded them one day earlier as *"descriptions of an interface,
not assertions a reviewer would ask us to substantiate."* That judgment assumed a reader who
already knows we run surveys. **Nandan's correction: nobody knows we have a survey platform
at all** — so the ordinary things a survey platform does are not background, they are the
claim that has to land before any distinctive capability means anything. The register's own
rule anticipated this: *if one of them reaches a page as a claim rather than as prose, it
needs a row then.* It has, so they do.

**C-082 is the trap in this group.** Surveys are authored **in Typeform**; Fly's dashboard
imports a form and runs it, and has no question editor. Every row above is true *of a study
run on Fly* — the logic, the piping, the validation are all executed by Fly — but a page
that describes them without C-082 in view will drift into implying a form builder we do not
have, and a researcher who arrives expecting one has been misled by us rather than by the
product. **Whether the page names Typeform is an editorial choice; whether the page may
imply a Fly form builder is not.**

**Still deliberately without a row:** the media library, thread handoff, the export
preprocessing options and the study lifecycle settings. Each is real and each is sourced in
the working note, but a register that grows a row per menu item stops being the thing the
site's whole proposition rests on.

**C-052 now covers two things to a reader.** It reads *"Open source, self-hostable on
Kubernetes + Helm"*, sourced to `github.com/vlab-research`. That was written when "the
platform" meant one piece of software. It is still true of both, and no second open-source
row is added — but check its wording against any page where Fly is named, because a reader
will now hear it as a claim about the instrument too.

**Still unverifiable, and not to be written without new work:** any completion, attrition,
fraud or duplicate figure of any kind (exhausted — four paper editions, the docs site, the
planning and documentation directories, proposals and analysis repos; nothing measured
exists); a WhatsApp path for in-chat video; how many studies actually used timeouts, seeds,
video or payments — answerable from the production database, one query per feature, and
subject to the disclosure check; and any **data-protection capability claim**, because Fly
has no documented PII policy, retention rule or erasure path. The privacy policy in this
repo is a company policy, not a Fly feature.

---

## The paper, as a source

**Donati, D. and Rao, N., "Adaptive Survey Sampling via Ad Platforms."**
Dante Donati (Columbia Business School and CESifo) · Nandan Rao (Virtual Lab and
Universitat Autònoma de Barcelona).

Rows above cite the working manuscript at
`../../survey-sampling-with-ads/paper/survey-sampling-with-ads-Jul2026.tex`. From this
repository that path resolves to `/home/nandan/Documents/survey-sampling-with-ads/paper/`
— the paper repo is a sibling of `vlab-research`, not a member of it. It is written
relative here because that is what every other path in this repo does; the absolute form
is recorded because one workstream mis-resolved the relative one and reported the
directory missing.

**Four editions sit there, not three**, and **all four carry `\date{September 15, 2025}`**:

```
survey-sampling-with-ads-Jul2026.tex   working manuscript, live revision, bylined
JMR_submission_09152025.tex            as submitted to JMR — blinded, no byline
SSRN_09152025.tex                      SSRN edition, bylined
survey-sampling-with-ads-Jan2025.tex   fourth edition, near-identical to SSRN
```

(`survey-sampling-with-ads.tex` is a 2023 ancestor, a third the length. Ignore it.)

**Every figure cited above is identical in all of them** — verified value by value,
2026-08-20 — so the edition matters for what we *link*, never for what we *claim*.

**The register previously said the working manuscript is dated 2026. It is not.** Only
its *filename* says 2026; the document dates itself September 2025, as the other three
do. That sentence was the whole basis of the open citation-year question.

**The citation year is settled: 2025.** Every edition carries `\date{September 15, 2025}`,
so there is nothing left to resolve about the year, and it is recorded here rather than
left to a future reader to re-derive. The manuscript is **JMR-25-0847, under a major
revision**, so no journal may be named — the citation is to the working paper, not to a
journal.

**The link landed 2026-08-20.** No SSRN ID, DOI or public URL exists in any edition or
anywhere in the paper repository; the URL below came from the author directly:

| ID | Claim | Value | Source | Status | Checked |
|---|---|---|---|---|---|
| C-055 | Public URL for the paper (SSRN) | `https://ssrn.com/abstract=5495148` | **Supplied by Nandan Rao, co-author, 2026-08-20.** Long form: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5495148`. **Not independently verified** — see the note below. **Also the row the quoted abstract is attributed to** — see below | `VERIFIED` | 2026-08-20 |

**C-055 is load-bearing twice over, and the second job is new as of 2026-08-21.** It is
the link a reader clicks, and it is **the row the Papers page attributes the quoted
abstract to** — `data-claim-quote="C-055"` names the document being quoted, which is what
makes the quotation a quotation rather than an unattributed exemption. `check-claims.py`
requires a `VERIFIED` row there and fails the page on anything else: a free-text string, an
unknown id, or a withheld row. **So C-055 is no longer just a link.** If it ever moved to
`STALE` or `WITHHELD`, the Papers page would stop building, and that is the intended
behaviour — a quotation whose source we can no longer stand behind should not ship.

**How C-055 was obtained, stated plainly because the row is `VERIFIED` on a person's
word.** Nandan Rao supplied it as a co-author of the paper, which makes him an
authoritative source for where his own paper is posted — that is why the row is
`VERIFIED` and not `PLACEHOLDER`. **Nobody here has read the SSRN landing page.** SSRN
sits behind Cloudflare and returns 403 to any non-browser client, so neither `WebFetch`
nor `curl` can reach it; the abstract id, the page's own metadata and the title as SSRN
prints it are unconfirmed from this side. If the link ever 404s, the fix is to ask the
author, not to search for a replacement id.

**Do not record a posted date, a revision date, a page count, or an SSRN version number.**
None of those has been seen by anyone here, and writing one down would be inventing a
figure — the exact failure this register exists to prevent.

**Open, and it is a ten-second check for Nandan that is unanswerable from here: which
edition is the SSRN PDF?** The only compiled PDF in the paper repository is
`JMR_submission_09152025.pdf`, which is **blinded and carries no byline**. If that is what
was uploaded, a reader who clicks through from our Papers page gets an author-less
document with our byline printed above the link. `SSRN_09152025.tex` is the bylined
edition and is what *should* be there. Confirm before the Papers page ships.

**The citation year, 2025, is now publishable, and source lines carry it.** With the link
in hand a citation is openable, so **"Donati & Rao, 2025"** is the form everywhere the
paper is cited — the year was never in doubt, only the half-citation was. The pass across
`CONTENT.md` was made 2026-08-20.

**The homepage math is the live revision's, not SSRN's, and this is deliberate.** The two
editions state different objectives — SSRN minimizes $\sum_h W_h^2/n_h$ under an
equal-variance assumption; the Jul2026 revision drops that assumption, introducing
$\sigma_h$ and yielding a closed-form allocation. **Nandan, 2026-08-25:** *"quote the
current, the SSRN will update, it's ok if it's out of sync for a minute."*

**This is the only place on the site that publishes ahead of the posted paper, and it has an
expiry.** When the revision posts, the two agree. If the revision changes again before it
posts, the homepage block changes with it. **It does not license publishing the Jul2026
edition itself** — the hosting and citation rules below are unchanged, and the constraint
that a hostable PDF be built from `SSRN_09152025.tex` still stands.

**Two constraints on whatever is linked.** The only compiled PDF of the current paper is
`JMR_submission_09152025.pdf`, which is **blinded and carries no byline** — hosting it
ships an author-less paper, so a hostable PDF has to be built from `SSRN_09152025.tex`.
And **do not publish the `Jul2026` edition**: it is a live revision responding to
reviewers, dropping the equal-variance assumption and rewriting the future-work section.
Cite and host the SSRN edition.

**Declared in the paper and therefore safe to state:** Columbia IRB AAAV1539 for the
validation study (C-054), and that one author holds ownership in Virtual Lab LLC. The
competing-interest disclosure is a credibility asset — the paper makes it, so should we.

---

## Clients and engagements

Named in `accounting/invoices/` and `accounting/purchase-orders/`. Being a real client
is a fact; **displaying a logo is a permission question — see D-014.**

| ID | Organisation | Engagement | Status | Logo cleared? |
|---|---|---|---|---|
| C-020 | The World Bank | Girl Effect, Kenya, TVET | `VERIFIED` | Unknown — D-014 |
| C-021 | UNICEF (Regional Office for Europe & Central Asia) | Bebbo, routine immunization | `VERIFIED` | Unknown — D-014 |
| C-022 | Gavi | Vaccine confidence | `VERIFIED` | Unknown — D-014 |
| C-023 | EFSA | Food-risk perception, EU | `VERIFIED` | Unknown — D-014 |
| C-024 | Columbia University | Research partner, IRB (AAAV1539) | `VERIFIED` | Unknown — D-014 |
| C-025 | George Washington University | Vaping / AIM2 | `VERIFIED` | Unknown — D-014 |
| C-026 | Truth Initiative | Youth tobacco | `VERIFIED` | Unknown — D-014 |
| C-027 | Upswell | HPV, Nigeria; DKT Ghana | `VERIFIED` | Unknown — D-014 |
| C-028 | iMedia Associates (Shujaaz) | Youth media, Kenya | `VERIFIED` | Unknown — D-014 |
| C-029 | ITAD | — | `VERIFIED` | Unknown — D-014 |
| C-030 | The Public Good Projects | Polio vaccine outcomes | `VERIFIED` | Unknown — D-014 |
| C-031 | Insight Research LLC | — | `VERIFIED` | Unknown — D-014 |

### Researchers' institutions — C-094 to C-096, `VERIFIED` 2026-08-25

**Confirmed by Nandan Rao, 2026-08-25:** *"My confirmation is enough. Trust me. Those
researchers used it."* **Operator knowledge is a source type this register accepts** — C-032
is the precedent, verified on the same basis — so all three rows are `VERIFIED` and
publishable.

| ID | Claim | Value | Source | Status | Checked |
|---|---|---|---|---|---|
| C-094 | Researchers from Harvard University have used the platform | Yes | **Operator knowledge.** Nandan Rao, confirmed 2026-08-25 | `VERIFIED` | 2026-08-25 |
| C-095 | Researchers from the University of Washington have used the platform | Yes | **Operator knowledge.** Nandan Rao, confirmed 2026-08-25 | `VERIFIED` | 2026-08-25 |
| C-096 | Researchers from Washington University in St. Louis have used the platform | Yes | **Operator knowledge.** Nandan Rao, confirmed 2026-08-25 | `VERIFIED` | 2026-08-25 |

**The row and the copy say the same thing on purpose.** The wall reads *"Used by researchers
from"*; these rows say researchers from those institutions **used the platform**. Neither says
the institution was a client, commissioned work, or endorses us. **That equivalence is what
makes the claim checkable** — if the heading ever changes, these rows have to be re-examined
against the new wording.

**What this does not cover.** These three are not in `accounting/` and are not derivable from
production — `vlab.orgs.name` holds Auth0 identifiers rather than institution names — so there
is no engagement, no country, no figure and no date attached to any of them. **Nothing beyond
the sentence in the Claim column may be said about them.**

**Columbia (C-024) and George Washington (C-025) reach the wall by a different and stronger
route** — both are `VERIFIED` engagements in `accounting/`. The World Bank (C-020) likewise.
On the wall all six sit under one heading, which is the weakest claim true of all of them.

**Clearance is a separate question and is not settled by this.** D-014 governs whether a
**mark** may be displayed; these rows govern whether the **relationship** may be stated. A
verified row does not license a logo.

---

## Studies referenced in mockups

Study-level figures used in the Phase 1 mockups were **illustrative**. Before any of
them appears on the live site, each needs a row here traced to the campaign config or
the production database.

| ID | Study | Figures used in mockup | Status |
|---|---|---|---|
| C-040 | Nigeria — HPV demand | n=2,400 · 8 strata · 11 d field time | `PLACEHOLDER` |
| C-041 | Serbia / Bulgaria — Bebbo parenting app | 2 waves · 2 countries · 4 mo follow-up | `PLACEHOLDER` |
| C-042 | Italy — Covid stereotypes | 542 municipalities · 90 provinces | `VERIFIED` — **Donati D., Gars J., and Rao N., working paper.** Not *Adaptive Survey Sampling via Ad Platforms*, which does not mention Italy |
| C-043 | Italy — Covid stereotypes, field window | — | `PLACEHOLDER` — the study card renders `—`. C-011's 19-day median is an aggregate across 116 studies and may not be attributed to this one; the study is longitudinal and its window is certainly not the median. One query away, and the study is published, so disclosure is not at issue |

---

## Infrastructure and compliance claims

| ID | Claim | Source | Status |
|---|---|---|---|
| C-050 | Production infrastructure hosted in the EU (Google Cloud `europe-west`) | Privacy policy, 2026-05-15 | `VERIFIED` |
| C-051 | Encryption in transit (TLS) and at rest | Privacy policy | `VERIFIED` |
| C-052 | Open source, self-hostable on Kubernetes + Helm | `github.com/vlab-research` | `VERIFIED` |
| C-053 | Auth via Auth0 | Privacy policy | `VERIFIED` |
| C-054 | Ethical clearance, Columbia IRB AAAV1539 | Donati & Rao (2025), title footnote | `VERIFIED` — applies to the validation study, **not** to all work. Do not generalise. |

**C-054 is a trap.** The IRB approval covers the US validation study described in the
paper. Phrasing it as "IRB-approved" without that scope would be an overclaim of
exactly the kind this file exists to prevent.

---

## Refreshing the placeholders

**C-008, C-009 — comparator point estimates. `WITHHELD` since 2026-08-20 (D-023); this
entry is kept so the reading can be re-verified, not so the values can be refreshed for
publication.** In
`../../survey-sampling-with-ads/paper/survey-sampling-with-ads-Jul2026.tex`, **Figure
`fig:MAD-comparison` and the paragraph immediately following it** — the values are in the
prose, not in a table. **There is no Table 4.** The per-domain three-way values behind the
C-006/C-007 caveat are in the paragraph preceding Figure `fig:MAD-categories-comparison`.
`tab:mad_outcomes` is Meta-only and carries no Prolific or twins column: an agent reading
comparators out of it will find a table of the right shape with the wrong contents. Read
the value, do not infer it from the abstract.

**C-010, C-011, C-015–C-019 — production figures.** CockroachDB in the `vprod`
namespace. Query from inside the cluster, never port-forward, and **read-only, always**:

```
kubectl exec -n vprod gbv-cockroachdb-0 -- ./cockroach sql --insecure --database=<db> --execute="<SELECT>"
```

Databases: `chatroach` (older platform, holds all response data) and `vlab` (current
platform, holds studies and configs). Coordinate with the user before every run.

- **C-010, C-015, C-016, C-018** — `SELECT count(*), count(DISTINCT userid), min(timestamp), max(timestamp) FROM responses;` in `chatroach`, and `count(DISTINCT userid) FROM states` for reach.
- **C-017** — extract `"country"`/`"countries"` codes from `vlab.study_confs.conf` and `chatroach.campaign_confs.conf` with `regexp_extract(conf::string, '"countr(?:y|ies)":\s*\[?\s*"([A-Z]{2})"')`, then union. First-match-per-row, so it undercounts multi-country studies — 41 is a floor.
- **C-011** — planned: `end_date − start_date` from the latest `conf_type='recruitment'` per study. Actual: `max(created) − min(created)` per `study_id` in `vlab.adopt_reports`, filtered to studies with more than five reports.
- **C-019** — `count(DISTINCT study_id)` in `vlab.adopt_reports`; `count(*)` in `chatroach.campaigns`.
- **C-091 — advertising cost per respondent.** Full query in
  `scripts/data/ad-cost.json` (`query` field). Spend lives in
  `vlab.recruitment_data_events.data` as Facebook Insights keyed
  campaign → stratum → `spend`. **Take the max per campaign/stratum/day, never the sum**
  (`temp=true` rows are cumulative intra-day snapshots), and **de-duplicate at campaign
  level** (7 campaigns appear under two studies). Country comes from a `strata` conf
  regexp; studies naming two countries are excluded.
- **C-089, C-090 — recruitment throughput.** Full query in
  `scripts/data/throughput.json` (`query` field) and reproduced in
  `scripts/build-throughput-figure.py`. Pools both platforms: current via
  `vlab.inference_data`, older via `chatroach.campaign_confs` stratum shortcodes joined to
  `responses.shortcode`. **Assign each respondent to one study per day before counting** —
  see the umbrella-group defect under C-089. **CockroachDB quirk that produced a wrong
  number once:** `count(DISTINCT x)` returns garbage when it sits in the same `SELECT` list
  as `percentile_cont()` — it reported 2,350 distinct studies out of 2,350 rows. Compute
  distinct counts in their own query.
- **Per-country respondents** — join `vlab.inference_data` (distinct `user_id` per `study_id`) to the country extracted per study.

**C-040, C-041 — study-level figures.** Same access. Disclosure check still applies.

**Disclosure check before publishing any study-level figure:** sample sizes and field
timings for a named client may be covered by that engagement's confidentiality terms.
Verify per study; a figure being technically available is not permission to publish it.
