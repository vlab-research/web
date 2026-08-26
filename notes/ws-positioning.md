# Positioning memo — the MENA question, four decision packets, and Home

**For:** Nandan · **Written:** 2026-08-20 · **Status:** recommendations only. Nothing here
is decided; D-016, D-017, D-019 and D-020 stay OPEN and are yours.

**Provenance of every number below.** Two sources only, and each figure is tagged:
`[CLAIMS]` = a `VERIFIED` row in `CLAIMS.md`; `[COMPUTED]` = arithmetic on
`scripts/data/coverage.json` (`as_of` 2026-08-20), shown so it can be re-run. No figure
in this memo is estimated, illustrative, or carried over from a mockup.

---

# Part 1 — The MENA question

## 1.1 First: the 311,363 is right, the 42% is not

`AGENTS.md` says *"Middle East & North Africa at 311,363 respondents — 42% of the total."*

- **311,363 — correct.** `[COMPUTED]` Sum of the ten MENA countries in `coverage.json`
  that carry a count: JO 79,915 · IQ 75,209 · LB 49,529 · AE 48,373 · EG 22,786 ·
  IL 16,028 · LY 8,460 · KW 6,571 · SA 3,930 · MA 562. The eleventh, **PS, has no count**,
  so 311,363 is a **floor**, not a total.
- **42% — wrong as written, and wrong in a way that would be caught.** `[COMPUTED]`
  311,363 ÷ **738,608** (respondents attributable to a country) = **42.2%**.
  311,363 ÷ **841,660** (C-010, the headline respondent total `[CLAIMS]`) = **37.0%**.

The denominator is the whole problem. The site's headline number is 841,660. If a region
strip beside it says "42%", a reader who multiplies gets 353,497 and we have published two
numbers that do not reconcile — on the one site whose entire proposition is that its
numbers reconcile. `CLAIMS.md` already records why: **103,052 respondents are
unattributed** `[COMPUTED]` — studies whose strata carry no country tag, *not* countries
outside the 41.

**Publishable form of the share, either way you take it:**

> 311,363 respondents in the Middle East and North Africa — 42% of the 738,608 respondents
> we can attribute to a country, which is 88% of all respondents.

That sentence is long because the honest version is long. If it is too long for the
component, publish the count and drop the percentage. Do not publish a bare "42%".

## 1.2 The factual picture

**Respondents by region** `[COMPUTED]`, regions as defined in `coverage.json`:

| Region | Respondents | % of attributed (738,608) | % of all (841,660) | Countries | Uncounted |
|---|---:|---:|---:|---:|---|
| Middle East & North Africa | 311,363 | 42.2% | 37.0% | 11 | PS |
| Sub-Saharan Africa | 143,816 | 19.5% | 17.1% | 9 | — |
| Americas | 136,558 | 18.5% | 16.2% | 5 | — |
| South & Southeast Asia | 113,460 | 15.4% | 13.5% | 5 | — |
| Europe & Central Asia | 30,573 | 4.1% | 3.6% | 10 | MD, MK, XK |
| Pacific | 2,838 | 0.4% | 0.3% | 1 | — |
| **Attributed** | **738,608** | 100% | 87.8% | 41 | |
| Not attributable to a country | 103,052 | — | 12.2% | — | |

**Concentration** `[COMPUTED]`, over the 37 counted countries:

| | Respondents | % of attributed | % of all |
|---|---:|---:|---:|
| Largest country (US 103,475) | 103,475 | 14.0% | 12.3% |
| Top 3 (US, NG, JO) | 271,850 | 36.8% | 32.3% |
| Top 5 (+ IQ, BD) | 419,260 | 56.8% | 49.8% |
| Top 10 | 576,004 | 78.0% | 68.4% |

Countries above 10,000 respondents: **14**. Above 1,000: **34**. Herfindahl index across
counted countries: **0.079**, i.e. an effective portfolio of roughly **12.6 equal
countries**. Non-US respondents: **635,133**, 86.0% of attributed. `[COMPUTED]`

**Three things this table says that the "42%" line hides.**

1. **The region is four countries.** JO + IQ + LB + AE = **253,026** = **81.3% of MENA**
   `[COMPUTED]`. The regional label adds nothing that naming the four does not, and it
   buys a problem — see (2).
2. **The bucket includes Israel** (16,028). MENA excluding Israel is 295,335 `[COMPUTED]`.
   Region composition is an **editorial choice made in `coverage.json`**, not a fact from
   the production database, and this particular grouping is one that a buyer in Amman or a
   buyer in Tel Aviv will each read as a statement. Naming countries avoids the question
   entirely.
3. **No single country dominates.** 14.0% is the largest share of attributed respondents,
   12.3% of all. This is the strongest genuinely-supportable structural fact in the whole
   coverage dataset, and it is currently unpublished anywhere.

## 1.3 How this squares with the client list — it does not, and that is the finding

Mapping each engagement in `CLAIMS.md` C-020–C-031 onto the volume table `[COMPUTED]`:

| Client | Engagement `[CLAIMS]` | Country | Respondents | Volume rank |
|---|---|---|---:|---:|
| Upswell | HPV, Nigeria | NG | 88,460 | **2** |
| Upswell | DKT Ghana | GH | 9,307 | 15 |
| The World Bank | Girl Effect, Kenya, TVET | KE | 17,226 | 10 |
| iMedia Associates (Shujaaz) | Youth media, Kenya | KE | (same) | 10 |
| UNICEF ECARO | Bebbo, routine immunization | RS / BG | 7,669 / 7,563 | 17 / 18 |
| Columbia · GWU · Truth Initiative | Validation · vaping · youth tobacco | US | 103,475 | **1** |
| The Public Good Projects | Polio vaccine outcomes | not stated | — | — |
| EFSA | Food-risk perception, EU | not stated | — | — |
| Gavi · ITAD · Insight Research | Vaccine confidence · — · — | not stated | — | — |

**The mismatch, stated plainly.** Two of the top three countries by volume — **Jordan
(79,915, rank 3) and Iraq (75,209, rank 4)** — appear in **no engagement named anywhere in
`CLAIMS.md`**. Nor do Lebanon or the UAE. Those four countries are **253,026 respondents,
34.3% of attributed and 30.1% of all respondents** `[COMPUTED]`, with zero client
attribution the site is permitted to make. Meanwhile the named engagements cluster at the
*small* end: Kenya is 10th, Ghana 15th, Serbia 17th, Bulgaria 18th.

Only two places agree: the **US** (rank 1, three named institutions) and **Nigeria**
(rank 2, Upswell).

**Why this is structural and not a gap to be filled.** The client wall answers *who
commissions the work*; the map answers *where the work lands*. Those distributions will
never match, because one contract can field in six countries, because volume follows
population and ad cost rather than contract value, and because some of the largest work is
not ours to name. A reader who sees both on the same page will notice the mismatch and has
nowhere to go with it. **This is the real content of D-019** — see Part 2.

I did not attempt to find out who commissioned the MENA work. If a client there is
nameable, that is a `CLAIMS.md` row and a disclosure check, not a copy decision.

## 1.4 Three positions, as actual copy

Each is drop-in for the coverage section heading and lede. Source lines per the provenance
rule (`DESIGN.md` §2) are shown as they would render — Source Serif italic `--ink-3`, in
the same visual unit as the figure.

---

### Position A — "The ledger"

> ## Where the respondents are
>
> 841,660 respondents across 41 countries since February 2020. The largest single country
> is 12% of the total; fourteen countries are above ten thousand. Where a study's strata
> carry no country tag we do not attribute it — 738,608 respondents are placed on this
> map, and the remaining 103,052 are counted in the total and not on it.
>
> *Virtual Lab production data, August 2026.*

**Claims used:** C-010, C-017, C-018 `[CLAIMS]`; 12%, 14 countries, 738,608, 103,052
`[COMPUTED]`.
**What it commits us to:** publishing the unattributed residual, forever. Every refresh has
to restate it.
**What it does not do:** it does not tell a buyer why they should care where we are strong.
It is a table with a voice.

---

### Position B — "What a study needs"

> ## What a study needs is an ad platform and a messaging app
>
> That is why the map looks like this. Forty-one countries since February 2020, and the
> four largest samples outside the United States are in Nigeria, Jordan, Iraq and
> Bangladesh. Median field window across all studies is nineteen days.
>
> *Virtual Lab production data, August 2026. Field window is time from first to last
> recruitment report, n=116.*

**Claims used:** C-017, C-018, C-011, C-010 `[CLAIMS]`; the four-country ordering
`[COMPUTED]` — **NG 88,460 · JO 79,915 · IQ 75,209 · BD 72,201**.
**What it commits us to:** nothing unsourceable. **Revised 2026-08-20 — see the correction
notice at 1.4a.** The earlier draft of this heading asserted "no field office in any of
them", which has no row in `CLAIMS.md`; this version states the *requirement* rather than
the *absence*, so it survives whichever way that question is answered.
**Why it is the interesting one:** it makes the footprint a consequence of the mechanism
rather than a boast, which is `DESIGN.md` §2 rule 2 exactly. It gets to *"places
conventional fieldwork cannot reach"* (§1) **without ever making the comparative claim** —
the reader makes it.

---

### Position C — "Not a regional shop"

> ## No single market carries this
>
> Fourteen countries have contributed more than ten thousand respondents each, and the
> largest one is twelve percent of the total. Roughly two in five attributed respondents
> are in the Middle East and North Africa — Jordan, Iraq, Lebanon and the United Arab
> Emirates — and the rest are spread across Sub-Saharan Africa, the Americas, South and
> Southeast Asia, Europe and the Pacific.
>
> *Virtual Lab production data, August 2026. Shares are of the 738,608 respondents
> attributable to a country, 88% of the total.*

**Claims used:** C-010 `[CLAIMS]`; every share `[COMPUTED]`.
**What it commits us to:** nothing unsourceable. It is fully defensible today.
**What it costs:** it argues with a fact instead of from one, and it reads slightly
defensive — a heading that denies something plants it. A buyer who wants Jordan learns that
Jordan is a fifth of a region rather than that we have 79,915 respondents there, which is
the number that would actually win that job.

---

## 1.4a Correction notice — two errors in the first draft of this memo

Both are mine, both are fixed above, and both are recorded rather than quietly patched,
because a memo arguing that wrong numbers must not ship does not get to silently fix its
own.

1. **Position B named the wrong four countries.** The first draft read *"the four largest
   samples outside the United States are in Jordan, Iraq, Lebanon and Bangladesh"* and its
   claims note repeated the error. It **omitted Nigeria (88,460), which is the largest
   sample outside the United States** and the second largest overall. Correct list, largest
   first: **Nigeria 88,460 · Jordan 79,915 · Iraq 75,209 · Bangladesh 72,201** `[COMPUTED]`.
   Lebanon (49,529) is sixth overall, not fourth-outside-US.
   **The correction improves the position.** The honest list opens with Nigeria — which is
   also the one high-volume country that *is* covered by a named engagement (Upswell,
   C-027) — so the sentence no longer reads as a MENA list, and the volume story and the
   client list agree in its first word.
2. **The heading asserted something unsourced.** *"No field office in any of them"* is a
   claim about our own operations with no row in `CLAIMS.md`. Replaced with a statement of
   what a study requires, which is a mechanism description and needs no row. The coordinator
   is putting the field-office question to Nandan; **the revised heading does not depend on
   the answer**, so it ships either way.

---

## 1.5 What each framing costs — and which ones we cannot source

**This is the most useful section of this memo. Read it before choosing.**

### "Strongest where panels are weakest" — **not publishable today**

It requires two claims we do not have:

1. **That panels are weak in those markets.** There is **no row in `CLAIMS.md`** — none —
   about panel coverage, panel sample availability, or panel quality anywhere outside the
   United States. The only panel comparison we own is C-006/C-008: Prolific, **n=1,197,
   fielded Jun–Jul 2025, against US benchmarks (GSS, CPS, Pew)**. Using a US-only
   methodological comparison to imply anything about Prolific's *coverage of Iraq* is not a
   stretch of the evidence, it is a different claim with no evidence at all.
2. **That we are strongest there.** A superlative. `DESIGN.md` §2 rule 4: no superlative
   survives without a citation in the same sentence. And it is arguably false on its own
   terms — our single largest country is the **United States** (103,475), the most
   panel-saturated market on earth. The frame contradicts our own data on the same page.

It also invites exactly the question the frame cannot answer: *compared to what, measured
how.* On this site, of all sites, that question gets asked.

### "Where conventional fieldwork cannot go" — **not publishable as a comparison**

Same problem, one step softer. `DESIGN.md` §1 says it internally, but §1 is a positioning
paragraph, not a source — `AGENTS.md` precedence is explicit that `CLAIMS.md` wins on
facts absolutely and that a statement in another repo document is not evidence. There is no
row on fieldwork feasibility, cost, or access in any market.
**Sourceable substitute:** state what a study requires (an ad platform and a messaging app)
and let the inference land. That is Position B.

### Characterising the markets — **not publishable, and a second risk**

"Fragile settings", "conflict-affected", "hard-to-reach populations", "humanitarian
contexts" applied to Iraq, Lebanon or Jordan: no row, no source, and each is a
characterisation of a client's operating context that may sit inside that engagement's
confidentiality terms. Two rules broken with one adjective.

### Naming who commissioned the MENA work — **not permitted**

No engagement in C-020–C-031 is located in MENA. There is nothing to name.

### "42% of respondents" — **arithmetic failure, not a claim failure**

Covered in 1.1. The number is real against the attributed denominator; the denominator must
be visible or the site contradicts itself.

### "A MENA specialist / our strength is the Middle East" — **sourceable but expensive**

This one *is* publishable — the volume supports it. It costs the World Bank/UNICEF/Gavi
buyer, whose named work is in Kenya, Nigeria, Serbia and the EU, and who is the primary
audience under D-001. It also ages badly against a single large contract elsewhere.

### What *is* publishable today, without qualification

C-010 841,660 · C-016 17,979,910 · C-017 41 countries · C-011 19-day median field window ·
C-018 operating since 2020-02-13 `[CLAIMS]`; and every per-country and per-region figure in
this memo `[COMPUTED]`, provided the denominator travels with any percentage.

## 1.6 Recommendation

**Take Position B as the coverage lede and fold Position A's residual disclosure into its
source line — it makes the footprint a consequence of the mechanism rather than a claim
about rivals, which is the only version of "strongest where panels are weakest" we can
actually source.** Do not adopt any panel-comparison or fieldwork-difficulty framing until
`CLAIMS.md` has a row that survives *compared to what, measured how* — and if you want that
frame, the cheapest route to it is one verified row on panel availability in three named
markets, not better copy.

*(Revised: Position B's heading no longer depends on the unverified field-office claim —
it states what a study requires rather than what we lack, so it ships whichever way that
question is answered. See 1.4a and Part 5.5.)*

---

# Part 2 — Decision packets

## D-019 — Where the coverage section goes

**The decision.** Coverage section (map + region strip + region totals) on the Studies
index, on Home, or both with a reduced Home version. **Blocks Phase 4.**

**What has changed since the recommendation was written.**

1. **The two-answers argument is the wrong argument for the right answer.** The recorded
   rationale is that map and client wall "answer a near-identical question in a different
   currency" and so weaken each other. Part 1.3 shows they answer **different questions
   whose answers openly disagree**: 30.1% of all respondents sit in four countries with no
   nameable client, while every named client sits in a country ranked 1, 2, 10, 15, 17 or
   18 by volume. That is a **stronger** reason to separate them, not a weaker one — but the
   recorded reason should be corrected, because someone will later notice the two sections
   are not redundant and reopen the decision on a false premise.
2. **A new, unrecorded consequence: the Studies index heading breaks.** The Phase 3 deck
   opens Studies with *"Thirty-three studies across twenty-three countries since 2020"*
   (C-001, C-002 `[CLAIMS]` — the paper's narrow claim). Put the coverage map on that page
   and the heading says 23 countries while the map beside it shows **41** (C-017). Two
   verified numbers, both true of different populations, contradicting each other above the
   fold. **This is a hard prerequisite:** landing coverage on Studies requires rewriting
   that heading to the operating figures first.
3. **D-020 thins Home.** If the stat row goes, Home's only quantitative operating moment is
   the totals band. That is an argument for a reduced Home coverage strip — but see below.

**Options and what each commits us to.**

| Option | Commits us to |
|---|---|
| **Studies index only** *(recorded rec)* | Rewriting the Studies heading off C-001/C-002 onto C-017 before ship. Home carries no map, so the totals band must carry the geography — the word "countries" is doing all the work. |
| **Home only** | Publishing the 12.2% unattributed residual in the highest-traffic position on the site, and finding room for the denominator caveat in a reduced component. A reduced strip that drops the caveat is the one version I would rule out. |
| **Both, reduced on Home** | Two maintenance surfaces for one dataset — every refresh touches both. Also: a Home strip plus a client wall puts the Part 1.3 mismatch on the page with no copy to explain it. |

**Where I think the recommendation is now wrong: it is not, but its reason is.** Keep
"Studies index". Re-record the rationale as *the two sections answer different questions
whose answers conflict, and the conflict needs a page with room to explain it* — and add
the heading rewrite as a stated prerequisite.

---

## D-020 — What replaces the four-cell stat row on Home

**The decision.** Drop the stat row; what, if anything, takes its place.

**What has changed since the recommendation was written.** The recommendation is a
**three**-number band — respondents · responses · countries. Three reasons that is now
wrong:

1. **C-011 has landed.** The Phase 3 deck's own note says *"When C-011 lands, field time
   replaces the fourth cell."* C-011 is `VERIFIED` as of 2026-08-20 — **14 days planned ·
   19 days actual**, n=116. The only reason the fourth cell was ever weak was that the
   number in it (1,500, a validation sample masquerading as operating scale) was wrong. The
   fix was never *fewer cells*; it was *the right fourth number*, and we now have it.
2. **`CONTENT.md` copy rule 4 requires it.** *"Field time is always stated where it is
   known."* It is known. A Home band that omits it while the copy rules mandate it is drift
   on day one.
3. **Three cells is a design-system deviation and four is not.** `DESIGN.md` §8 specifies
   the stat row as **four cells**, and §5 fixes the 760px breakpoint as **stat row → 2×2**
   — a rule that only makes sense with four. A three-cell band needs a new component and a
   `DESIGN.md` edit; a four-cell band is the component that already exists, tested and
   contrast-checked.

**The band, as it would render.** Numbers in Plex Mono `clamp(32px,3.6vw,42px)`, unit
suffix at `.46em` in `--ink-2`, labels mono uppercase `--ink-2`, **source lines in Source
Serif italic `--ink-3` — mandatory** (§8):

> `OPERATING SINCE FEBRUARY 2020`
>
> | | | | |
> |---|---|---|---|
> | **841,660** | **17,979,910** | **41** | **19** days |
> | RESPONDENTS | SURVEY RESPONSES | COUNTRIES | MEDIAN FIELD WINDOW |
> | *Virtual Lab production data, August 2026* | *Virtual Lab production data, August 2026* | *Virtual Lab production data, August 2026* | *First to last recruitment report, n=116* |

**Every figure:** C-010 · C-016 · C-017 · C-011 (actual, not planned) · C-018 for the
eyebrow. All `VERIFIED` `[CLAIMS]`.

**Rule checks on that band.**

- **"RESPONDENTS", never "people reached."** C-015 (1,097,153) is marked NOT FOR
  PUBLICATION. The band must never use the word "reached" even as a label variant.
- **No platform language.** Publication rule 2. The source line says *Virtual Lab
  production data* — it does not name a database, a schema, or two platforms. It must not
  become "across our platforms," which would leak the same fact in prose.
- **Never cite Donati & Rao here.** `CLAIMS.md` is explicit: the paper sources validation
  claims and nothing else. The old row's *"Donati & Rao"* source lines were part of what was
  wrong with it.
- ~~**C-019 (study count) stays off.**~~ **SUPERSEDED 2026-08-20 — see Part 4.** C-019 is
  now `VERIFIED` at **175**. A study count *is* publishable, which changes the fourth-cell
  contest from "field window or nothing" to "field window against 175 studies." Argued in
  Part 5.3.
- **Rounding.** 17,979,910 is ten characters and will be tight in the 2×2 at 760px. Solve
  it with a size step, **not** by writing "18M" — §2 rule 6 forbids two roundings of one
  figure, and an exact number is the point.
- **The eyebrow is a §8 addition.** The stat row spec has no eyebrow. If you take it, add
  one line to `DESIGN.md` §8 in the same change; otherwise move "since February 2020" into
  the adjacent prose.

**Does the band need a fourth number, and is it publishable?** Yes and yes: **median field
window, 19 days, C-011, `VERIFIED` today.** The two other candidates are **C-018** (
`VERIFIED`, better as the eyebrow than as a cell — a date is not a magnitude and sits badly
in a row of counts) and **C-019** (**not publishable**, definition unfixed).

**Where I think the recommendation is now wrong: the number of cells.** Drop the stat row's
*contents* — that judgement was right and both stated reasons hold. Do not drop the *
component*. Four cells, with field window in the fourth.

---

## D-016 — Where the paper lives

**The decision.** SSRN link only, a hosted PDF, or a full landing page with abstract,
figures, BibTeX and download.

**What has changed since the recommendation was written.**

1. **D-007 already killed option one.** A Papers page exists in the settled seven-page
   sitemap. `DECISIONS.md` records this under D-007's consequences; D-016's option list has
   not caught up. The live question is **depth**, not location.
2. **The citation year is unresolved, and it blocks BibTeX specifically.** Manuscript July
   2026, submission 2025, three editions on disk. A BibTeX block with the wrong year does
   not just sit there being wrong — it propagates into other people's reference lists and
   cannot be recalled. This is the one component of the landing page that is genuinely
   blocked, and it is severable from the rest.
3. **Two unrecorded costs nobody has priced.**
   - **Figures cost real build time.** `AGENTS.md` hard rule 8: all graphics are inline SVG
     from the four primitives; no raster illustration. "Figures" on the Papers page means
     **rebuilding** the MAD comparison and the cost table in the design system, not
     screenshotting them from the PDF.
   - **The cost table is permanently off the page in per-question form.** **Revised
     2026-08-20:** C-004 is not `STALE` pending a call — it is **`WITHHELD`**, Nandan's
     decision, and no cost-per-question figure ships unless the manuscript is corrected.
     This is not a blocker to wait out; it is a permanent shape constraint on the Papers
     page. See Part 4.1.
4. **The Papers page is on the primary path.** The Home hero's secondary CTA is *"Read the
   paper."* Whatever lands there is not a back-of-house artefact.

**Options and what each commits us to.**

| Option | Commits us to |
|---|---|
| Hosted PDF only | Nothing ongoing. Forfeits the inbound-link asset for the academic half of D-001. |
| **Landing page, staged** | Ship abstract (verbatim, per `CONTENT.md`) + download + MAD figure rebuilt in SVG now; **BibTeX block added the day the citation edition is settled**. The cost table is **not** a later stage — under `WITHHELD` it never ships in per-question form. |
| Full landing page now | Either publishing a citation year we have not settled, or shipping a page with two visible gaps in its most-cited components. |

**Where I think the recommendation is now wrong: it is under-specified, not wrong.**
"Landing page" is right and I would keep it. What is missing from the record is that it has
**one staged dependency and one permanent exclusion**: the citation year gates the BibTeX
block and will clear; **C-004 `WITHHELD` gates the cost table and will not.** Record the
staging *and* the exclusion, or a future agent reads "pending" and reintroduces a figure
Nandan has ruled out. The Papers page ships without a per-question cost, permanently, and
the Method page carries the cost conversation instead — see Part 5.2.

---

## D-017 — Does the jobs posting return?

**The decision.** A Senior Software Engineer posting from the current site: keep, drop, or
replace with something lower-maintenance.

**What has changed since the recommendation was written.**

1. **The copy deck has already voted.** `CONTENT.md` lists the jobs posting under *"Content
   that should not survive."* The decision is being treated as settled in one document
   while it is OPEN in another — that is exactly the drift `AGENTS.md` warns about, and it
   should be resolved in one direction or the other rather than left.
2. **The sitemap has no room for it.** D-007 settles seven pages, none of them Careers. A
   real posting needs somewhere to live; giving it one reopens a settled decision for a
   single job ad.
3. **The brand argument is stronger than the recorded one.** The record weighs "scale and
   momentum" against "staleness." On *this* site the asymmetry is worse than that: a
   visitor who emails about a role that closed learns that our public statements are not
   maintained. Every number on this site asks to be trusted on the strength of the same
   promise. A stale job ad is cheap to leave up and expensive in exactly our currency.

**Options and what each commits us to.**

| Option | Commits us to |
|---|---|
| **Drop it** *(recorded rec)* | Nothing. Reversible in an afternoon if you start hiring. |
| One line in Contact / footer — *"We hire occasionally: info@vlab.digital"* | Nothing dated, nothing to go stale, no new page. Signals a company that exists without asserting a vacancy. |
| Live posting | An owner and a removal date, in writing. Without both, do not take this option. |

**Where I think the recommendation is now wrong: it is not.** Drop it. The only addition
worth recording is that this is **not binary** — the footer line is a zero-maintenance way
to keep the signal — and that `CONTENT.md` should stop pre-supposing the outcome until you
call it.

---

# Part 3 — The Home page as a whole

## 3.1 Revised section order

Assumes D-020 lands as recommended (four-cell totals band replacing the stat row) and D-019
lands as recommended (no coverage section on Home).

| # | Section | Component (§8) | Purpose — the buyer question it answers | Claims used |
|---|---|---|---|---|
| 1 | Hero | Hero + `.pri` / `.sec` buttons | *What do you do?* — mechanism in two sentences | None. Mechanism only, no figures |
| 2 | Operating scale | **Stat row (4 cells)** — paper ground | *Are you real, and at what scale?* | C-010, C-016, C-017, C-011 · C-018 in eyebrow |
| 3 | Validation | **Ink band #1** + interval rows (M3) | *Is the sample defensible?* — the strongest asset we own | C-003, C-006, C-007, C-008, C-009; C-005 in the source line |
| 4 | How a sample is built | Three steps (§7 icons) + stratum readout | *How does it work, and can I audit it?* | None — mechanism. Readout content governed by D-013 |
| 5 | Studies | Study cards ×3 + `[All studies →]` | *Have you done work like mine?* | C-042 only; C-040/C-041 are `PLACEHOLDER` and render nothing |
| 6 | Client wall | Client wall, 12 cells | *Who else trusted you?* | C-020–C-031; logos gated on D-014 |
| 7 | Close | CTA — **paper ground, not a band** | Convert | None |
| 8 | Footer | **Ink band #2** | — | None |

**One ordering call I am flagging rather than making.** D-020's record puts validation
immediately after the hero. Above I have it at 3, behind the totals band, on the grounds
that scale is the cheaper read and the hero already states the mechanism. If you would
rather validation land second, swap 2 and 3 — the ink-band rules survive either way (the
band's neighbours are paper in both orders). The one order I would rule out is validation
after the mechanism section, which buries the site's best asset below the fold.

## 3.2 Ink band audit — Home is already at its limit

**`DESIGN.md` §8 lists the footer as an established ink band.** The Phase 3 deck says *"One
ink band only, on the validation section"* — **and does not count the footer.** With the
footer counted, Home runs **2 of a maximum 2**.

- **Adjacency:** clean as ordered. Band 3 sits between the totals band (paper) and the
  mechanism section (paper). Band 8 sits behind the Close (paper).
- **Two live risks:**
  - **The Close must stay on paper.** Making section 7 a band puts it adjacent to the
    footer *and* takes Home to three. Tempting, because a CTA on an ink band is the
    strongest button treatment in the system (`.oninv`). Do not.
  - **A Home coverage strip cannot be a band.** If D-019 later lands as "both, reduced on
    Home," the strip must be paper, or something else has to give up its band.
- **Fix the deck:** `CONTENT.md`'s Home components line should read *"Two ink bands:
  validation and the footer — the page is at its limit,"* so the next agent does not spend
  the budget twice.

## 3.3 Two sections answering one question in different currencies

D-019's argument applies elsewhere on Home. Three instances, in order of severity:

1. **Sections 5 and 6 — Studies cards next to the Client wall, and they are adjacent.**
   Both answer *have you done this before?* — one in designs, one in institutions. This is
   the D-019 pattern almost exactly, and worse in one way: with C-040 and C-041
   `PLACEHOLDER`, **two of the three study cards carry no figures at all**, so a weak
   evidence block sits immediately above twelve named institutions and loses the comparison.
   **D-007's own reasoning applies here and nobody has applied it:** it dropped per-study
   pages because *"a page of blanks is worse than no page"* on a site whose proposition is
   checkable numbers. Three cards where two are blank is a smaller version of the same
   mistake. **Options:** cut Home to a single card (Italy, C-042, the one that is verified)
   plus `[All studies →]`; or drop the cards from Home and let the client wall carry the
   track-record slot alone. I lean to the first — one complete card outperforms three where
   two are hollow — but this is a `CONTENT.md` change and therefore yours.
2. **Sections 2 and 5 — the totals band against the study cards.** Aggregate scale versus
   instance detail; the same question at two altitudes. Not adjacent and not in conflict.
   Leave it; noted so it is not rediscovered as a problem.
3. **Sections 1 and 4 — the hero against "How a sample is built."** The hero states the
   mechanism in two sentences; section 4 states it in three steps. Same question, same
   currency — repetition rather than conflict. If the page runs long, section 4 is the
   compression candidate, not the validation band.

## 3.4 One consequence of dropping the stat row nobody has recorded

C-005 (1,500, the US validation sample) currently occupies the fourth cell. Under the
revised band it has no home on Home — and it should not have one, because it is a
*validation* figure sitting in an *operating* row, which is the category error that made
the old row wrong in the first place. **It belongs in section 3's source line:** *"Mean
absolute deviation across all outcome variables, post-stratification weighted, n=1,500,
against GSS 2024, CPS 2024 and Pew 2023. Donati & Rao."* That keeps it published, in the
right section, under the right source.

---

# Rules I checked this memo against

- No number invented. Every figure tagged `[CLAIMS]` or `[COMPUTED]`; the computations run
  against `scripts/data/coverage.json` and reproduce.
- No copy proposed implies we are the cheap option (C-013), closer on every measure
  (C-006/C-007), or "IRB-approved" unqualified (C-054).
- No AI claim anywhere. Position B attributes the footprint to the mechanism, not to
  intelligence.
- No repo document edited. No git state mutated. No database queried. `media/` untouched.
- D-016, D-017, D-019 and D-020 remain OPEN. Everything above is a recommendation.

---
---

# Part 4 — Settled state as of 2026-08-20, and what it moved

Four decisions closed after Parts 1–3 were drafted. Recorded here rather than rewritten
into the packets above, so the reasoning that led to each is still legible.

| | Settled | What it moves in this memo |
|---|---|---|
| **C-004** | **`WITHHELD`** — a fourth status. No cost-per-question figure ships unless the manuscript is corrected. | **Strengthens D-016.** The cost table is not a deferred stage, it is a permanent exclusion. Method §5 must be rebuilt without a per-question operand — Part 5.2. |
| **C-019** | **`VERIFIED` at 175** (119 + 56). Publishable. Phrasing may never explain the 175 by naming a platform split. | Supersedes "no honest way to publish a study count." Unblocks the Studies opener — Part 5.1. Adds a fourth-cell contender — Part 5.3. |
| **D-020** | **Settled: drop the stat row, three-number band.** My four-cell case goes back to Nandan as a reopen. | Both variants drafted, side by side — Part 5.3. I have assumed nothing. |
| **D-013** | **Settled: recorded replay at launch.** | Home §4's stratum readout is now fully specified; no open dependency in Part 3's table. |

**One consequence of C-019 that needs a decision it has not had.** With the Studies index
saying **175** and the Papers page saying **over 33**, the site publishes two study counts.
Both are `VERIFIED` and both are true of different populations — C-001 counts studies *in
the paper*, C-019 counts studies that recruited. A reader who notices will read it as an
inconsistency unless the Papers page says which population it is counting. **One clause
fixes it, on the Papers page, not the Studies page:** *"…the thirty-three studies described
in this paper."* Without that clause, publishing 175 creates the contradiction that
Part 2/D-019 was written to prevent, just on a different pair of pages.

---

# Part 5 — `CONTENT.md` replacement blocks

Drop-in ready. Provenance rule observed throughout: every figure carries its source in the
same visual unit, source lines in Source Serif italic `--ink-3` (§8). Tags as before —
`[CLAIMS]` = `VERIFIED` row, `[COMPUTED]` = arithmetic on `scripts/data/coverage.json`.
**No repo document has been edited.** These are proposals for you to place.

---

## 5.1 Studies index — the opener

**Replaces:** *"Thirty-three studies across twenty-three countries since 2020, run by us
and by external research teams on the same platform. / Donati & Rao."*

**Why it had to go:** the paper's narrow claim (C-001, C-002) used as the operating claim,
understating the business by 41 countries to 23 — and the specific thing that made the
coverage map unplaceable on this page, because the heading would have said 23 above a map
showing 41.

> # Studies
>
> 175 studies across 41 countries since February 2020, run by us and by research teams
> using the open-source platform.
>
> *Virtual Lab production data, August 2026.*

**Claims:** C-019 (175) · C-017 (41) · C-018 (February 2020) · C-052 (open source) —
all `VERIFIED` `[CLAIMS]`.

**Rule checks.**

- **Source is production, never the paper.** `CLAIMS.md` is explicit that Donati & Rao
  sources validation claims and nothing else. The old source line was the error, not just
  the numbers.
- **No platform-split language.** The line does not explain how 175 is reached, and must
  not. If anyone later asks the copy to justify the number, the answer is a `CLAIMS.md`
  definition note, not a public sentence.
- **"the open-source platform" is C-052, not the internal split.** Publication rule 2 bans
  disclosing that our data lives across two systems; it does not ban the word "platform",
  which the site has a whole page for. If you would rather avoid the collision entirely,
  the shorter version below loses nothing this page needs.
- **⚠ One clause I could not source.** *"run by us and by research teams"* — third parties
  running their own studies on the platform is asserted in the current deck and has **no
  row in `CLAIMS.md`**. It is a good, differentiating fact if true. Either add a row, or
  ship the shorter version:

> # Studies
>
> 175 studies across 41 countries since February 2020.
>
> *Virtual Lab production data, August 2026.*

**Recommendation:** ship the short version now, add the clause back the day it has a row.
The long version's only added value is the third-party claim, which is precisely the part
without a source.

**Prerequisite discharged:** with this opener in place, the D-019 blocker identified in
Part 2 is cleared and the coverage section can land on this page — 41 in the heading, 41 on
the map.

---

## 5.2 Method §5 — "What it costs, honestly", full rewrite

### The problem, stated precisely

C-012 and C-013 are both denominated **per question per respondent**. C-012 is *$0.32 vs
$3.00 and $6.67*; C-013 is *$0.32 vs ~$0.10*. **Printing either comparison in its registered
form prints the withheld figure as an operand.** The section as drafted cannot ship.

### Does the section survive without a per-question figure? Yes.

**Its job is not to state our unit cost.** Its job, in the deck's own words, is that *"a
buyer will find the cost table in the paper. It is better that they find it here first."*
What makes that job work is the **admission** — we are roughly three times a convenience
panel — not the decimal. The admission is fully publishable: **C-013 is already registered
as a ratio**, in words, *"roughly 3× more expensive"*, and that ratio is what a buyer
remembers. So the section survives, and in my judgement it survives at close to full
strength. What it loses is the ability to let a buyer price a survey from the page, which
this section was never for — that is what "Request a proposal" is for.

### The block

> ## What it costs, honestly
>
> Recruiting in the US validation study cost **$6.30** per participant in advertising,
> ranging from **$0.70** for urban young medium-educated men to **$20** for urban mid-age
> low-educated men. With the $5 incentive, **$11.60** per participant.
>
> *Donati & Rao, Cost Considerations.*
>
> Set against a gold-standard probability survey, that is far below what the same data
> costs to collect. Set against a convenience panel like Prolific, it is roughly three
> times more. Both comparisons are in the paper's cost table, and we would rather you read
> them there than take our summary of them.
>
> *Donati & Rao, cost table.*
>
> We are not the cheap option. We are the option that is closer to the benchmarks than the
> cheap one, in places a probability survey cannot go.
>
> **We do not publish a per-question cost.** The manuscript states two different figures
> for it — one in the abstract, one in the cost table — and until that is corrected we will
> not pick the one that flatters us.

**Claims:** C-014 ($6.30 · $0.70–$20 · $11.60, `VERIFIED`) · C-013 ("roughly three times",
the registered ratio wording, `VERIFIED`) · C-012 (comparison stated without operands,
cited to the table) · C-004 `WITHHELD`.

### The last paragraph is optional and it is the most on-brand sentence on the site

**For:** it turns a withheld figure from an absence a sharp reader will notice into a
demonstration of the exact discipline we are selling. A buyer who opens the cost table and
finds $0.32 while the site quotes nothing will wonder what else we left out — unless we
told them why. And "we will not pick the one that flatters us" is the whole proposition in
eleven words.

**Against:** it publicises an unresolved error in our own paper, on the page where an
academic reader is deciding whether to cite it. It also invites a follow-up question we
answer with silence.

**Recommendation: keep it, and let Nandan strike it.** If it goes, everything above it
still ships — the block is written so the paragraph detaches cleanly.

### The stronger option, if you want a number back — and what it would take

**The two ratios are robust to the very conflict that withheld the figure** `[COMPUTED]`:

| | Under $0.30 | Under $0.32 | Publishable rounding |
|---|---:|---:|---|
| vs GSS traditional ($3.00) | 10.0× | 9.4× | "roughly ten times less" |
| vs GSS Follow-on ($6.67) | 22.2× | 20.8× | "ten to twenty times less" (conservative under both) |
| vs Prolific (~$0.10) | 3.0× | 3.2× | **"roughly three times more"** — already registered as C-013 |

The $0.30/$0.32 dispute is a 6% difference; every one of these ratios rounds to the same
published words under either reading. **A ratio therefore requires no resolution of C-004
and prints no withheld figure.**

**But it is arithmetic on a withheld operand, and I am not treating that as pre-approved.**
C-013's ratio is publishable today because the register states it in ratio form. The
gold-standard ratios are **not** in the register in that form and would need **a new
`VERIFIED` row** — a derived-ratio row, with the robustness table above as its note — before
a word of it ships. That is a `CLAIMS.md` change and Nandan's call. Until then the block
above states that comparison in words, which costs the section very little.

---

## 5.3 The totals band — both variants, side by side

Numbers in Plex Mono `clamp(32px,3.6vw,42px)`; unit suffix `.46em` in `--ink-2`; labels
mono uppercase `--ink-2`; **source lines Source Serif italic `--ink-3`, mandatory** (§8).

### Variant A — three cells (**as settled, D-020**)

> `OPERATING SINCE FEBRUARY 2020`
>
> | | | |
> |---|---|---|
> | **841,660** | **17,979,910** | **41** |
> | RESPONDENTS | SURVEY RESPONSES | COUNTRIES |
> | *Virtual Lab production data, August 2026* | *Virtual Lab production data, August 2026* | *Virtual Lab production data, August 2026* |

**Claims:** C-010 · C-016 · C-017 · C-018 (eyebrow). All `VERIFIED`.

### Variant B — four cells (**the reopen**)

> `OPERATING SINCE FEBRUARY 2020`
>
> | | | | |
> |---|---|---|---|
> | **841,660** | **17,979,910** | **41** | **19** days |
> | RESPONDENTS | SURVEY RESPONSES | COUNTRIES | MEDIAN FIELD WINDOW |
> | *Virtual Lab production data, August 2026* | *Virtual Lab production data, August 2026* | *Virtual Lab production data, August 2026* | *First to last recruitment report, n=116* |

**Claims:** as Variant A, plus C-011 — **actual, not planned**. All `VERIFIED`.

### Variant B′ — four cells, studies instead of field window

Now available because C-019 is `VERIFIED` at 175. Recorded so the contest is visible; **I do
not recommend it.**

> | **175** | **841,660** | **17,979,910** | **41** |
> |---|---|---|---|
> | STUDIES | RESPONDENTS | SURVEY RESPONSES | COUNTRIES |

**Why not.** `CONTENT.md` copy rule 4 — *"field time is always stated where it is known"* —
and the deck's own reasoning that field time is *"the number a buyer facing a collapsed
timeline is actually shopping for."* 175 is impressive; 19 days is decision-relevant. If
Variant B′ is taken, the Studies opener (5.1) then prints 175 twice on two pages, which is
not wrong but spends the number twice.

### The two issues that apply to **both** variants

**1 · The eyebrow is a §8 addition.** The stat-row spec has no eyebrow. C-018 is
`VERIFIED` and "since February 2020" earns its place — a band of counts with no time frame
is a weaker claim than one with. If you take the eyebrow, **add one line to `DESIGN.md` §8
in the same change** (`AGENTS.md`: fix the document with the code). If you would rather not
touch §8, move "since February 2020" into the adjacent prose and lose nothing but adjacency.

**2 · 17,979,910 will not fit, and the fix is not rounding.** Ten characters in Plex Mono at
up to 42px. **Never "18M" or "18 million"** — `DESIGN.md` §2 rule 6 forbids two roundings of
one figure, and the exact number *is* the argument. Fix it with a size step on that cell,
or a `clamp()` floor tuned to the longest value in the row.

**A sizing point that cuts for Variant B.** `DESIGN.md` §5 fixes the 760px breakpoint as
**stat row → 2×2**. Four cells give a clean 2×2. **Three cells give 2 + 1 orphan**, which
the documented breakpoint does not describe — so Variant A needs either a new responsive
rule in §5 or a deliberate 3→1 stack. Variant B needs nothing: it is the component that
already exists, at the breakpoint that already exists, contrast-checked. That is a
build-cost argument on top of the editorial one, and it was not in the record when D-020
was called.

---

## 5.4 Home — the components line and the study-card block

### 5.4.1 The components line

**Replaces:** *"Components: hero + stat row · mechanism steps · stratum readout · ink band
(1) · study cards · client wall · CTA. One ink band only, on the validation section."*

> **Components:** hero · totals band · mechanism steps · stratum readout · ink band ·
> study card · client wall · CTA.
> **Ink bands: two — the validation section and the footer. The page is at its limit.**
> `DESIGN.md` §8 counts the footer as an established ink band. Adding a third, or promoting
> the closing CTA to a band (which would also make it adjacent to the footer), breaks §8.
> If a coverage strip ever lands on Home it is on paper ground.
> **Claims used:** C-010, C-011, C-016, C-017, C-018, C-042, C-020–C-031, and C-003,
> C-005, C-006–C-009 in the validation band.

### 5.4.2 The study-card block

**Replaces:** *"Three cards, then `[All studies →]`."*

**Why.** With C-040 and C-041 `PLACEHOLDER`, two of the three cards render no figures at
all — and they sit immediately above twelve named institutions. D-007's own reasoning
applies and has not been applied here: it deferred per-study pages because *"a page of
blanks is worse than no page"* on a site whose proposition is checkable numbers. Three
cards where two are hollow is the same mistake at smaller scale, and it is the weaker half
of the Part 3.3 currency clash.

> One card, then `[All studies →]`. The card is the study whose figures are `VERIFIED`;
> the index carries the rest. A second card is added the day a second study clears both
> verification and disclosure — not before.

**The card, as it would render** (§8 study card: kicker geography in brass mono uppercase
with year right-aligned in `--ink-3` mono; title Zilla Slab 20px; abstract Source Serif
15px; facts row pinned above a hairline, values mono 17px, labels mono 9.5px uppercase):

> `ITALY`                                                                        `2020`
>
> ### Covid-19 and stereotypes
>
> Respondents recruited across 542 municipalities and 90 provinces using geographic
> targeting, then surveyed at weekly and bi-weekly intervals through the pandemic. A few
> questions per contact, over many contacts, held attrition low.
>
> ---
>
> | **542** | **90** | **—** |
> |---|---|---|
> | MUNICIPALITIES | PROVINCES | FIELD TIME |
>
> *Donati D., Gars J., and Rao N., working paper.*

**Claims:** C-042, `VERIFIED`.

**⚠ The dash is not an oversight, and it exposes a real conflict.** `DESIGN.md` §8 says of
the study card: *"Always include field time. It is the number a buyer facing a collapsed
timeline is actually shopping for."* **There is no verified field time for the Italy
study.** C-011's 19-day median is an aggregate across 116 studies and cannot be attributed
to this one; the study is longitudinal and its window is certainly not the median. So:

- Per hard rule 2, the cell renders **`—`** and a **`PLACEHOLDER` row goes into
  `CLAIMS.md`** for Italy field time. That is the compliant answer and it is what I have
  drafted.
- But a dash in the cell §8 calls load-bearing, on the only study card on the home page, is
  a poor first impression of a card component.
- **Two ways out, both yours:** compute the Italy field window and promote it to `VERIFIED`
  (best — it is one query away and the study is published, so disclosure is not at issue);
  or qualify §8 to *"always include field time where it is verified; a card with no verified
  field time is a candidate for the index, not the home page"* — which, taken literally,
  would remove this card from Home and leave the client wall carrying the track-record slot
  alone.

**My recommendation: get the Italy field window verified.** It is the cheapest of the three
and it makes the strongest single card on the site complete. Until then, ship the dash — it
is honest, and honest gaps are the brand.

---

## 5.5 Position B's heading, in a form that survives either answer

Already applied in Part 1.4 and repeated here for the coordinator's question:

> ## What a study needs is an ad platform and a messaging app
>
> That is why the map looks like this. Forty-one countries since February 2020, and the
> four largest samples outside the United States are in Nigeria, Jordan, Iraq and
> Bangladesh. Median field window across all studies is nineteen days.
>
> *Virtual Lab production data, August 2026. Field window is time from first to last
> recruitment report, n=116.*

**It states a requirement, not an absence.** *"No field office in any of them"* asserts a
fact about our staffing with no row in `CLAIMS.md`; *"what a study needs is…"* describes the
mechanism, which is what `DESIGN.md` §2 rule 2 asks for anyway. **If the field-office answer
comes back yes, nothing changes** — the requirement is still the requirement, and the
heading is stronger for making the reader draw the inference rather than being handed it.
**If it comes back no, nothing changes either.** The question stops being load-bearing.

**Claims:** C-017 · C-018 · C-011 `[CLAIMS]`; country ordering `[COMPUTED]`.
