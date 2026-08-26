# Copy

**Written 2026-08-22 against the D-027 spine.** This file supersedes the copy deck in
`CONTENT.md`, which was drafted against a nine-page sitemap that D-007 dissolved and is
now out of date — *Nandan, 2026-08-22: "ignore it entirely."* Do not merge the two decks;
`CONTENT.md` is history.

**What this is.** Actual copy, in the order the reader meets it, with every figure carrying
its claim id and its source line, and every image or generated artefact marked as a
numbered placeholder. It is copy for review, not markup — headings are marked `H1`/`H2`,
components are named from `DESIGN.md` §8, and nothing here has been fitted to a layout yet.

**What it was written under.** `DESIGN.md` §2 for voice, `CLAIMS.md` for every fact, D-027
for the order and the seam rules, D-007 for the surfaces, D-023 for what is not said.
American spelling (§2 rule 7).

**Placeholders use `[P-n]`** and are indexed at the end, with what each one is and where it
comes from. A placeholder is a slot for an image, a generated artefact, or a figure that is
not yet `VERIFIED` — it is never a stand-in for a number, which per hard rule 2 renders `—`.

---

## The site

**Collapsed to one page plus privacy on 2026-08-25.** D-007 derived six surfaces from the
narrative; four of them no longer have enough to say, and D-007's own test is that **a page
of blanks is worse than no page**.

| | Carries |
|---|---|
| **The page** | Opening (hero · totals · coverage · the two distributions · the client wall) · what it takes (recipe · math · paper · instrument) · the audit trail · the close |
| **Privacy** | Carried over near-verbatim. **Not linked from the page** (Nandan, 2026-08-25); it exists at its URL for anyone who needs it |

**Cut, each for its own reason:**

- **The brief form** — replaced by an email address, `info@vlab.digital`. No form to build, no
  submission handling, no spam surface.
- **What else you can build** — the two design patterns. Deferred; C-087 is `PLACEHOLDER`
  anyway and Pattern 2 cannot name its study.
- **What we have run** — no study cards for now. C-040 and C-041 are `PLACEHOLDER` in full and
  C-042 renders two dashes. **The client wall survives and moves into the opening**, where
  "we have done this a lot" is already the job.
- **The paper as its own page** — the page now carries the citation, the abstract and the
  link. What was left was BibTeX and a PDF download, and **there is no hostable PDF**: the only
  compiled edition is the blinded submission with no byline. Worth rebuilding the day a
  bylined PDF exists.

**Anchors, not pages.** `/#audit` and `/#paper` give a procurement reviewer or an academic a
URL to link, so splitting a section out later costs nothing and rewrites no copy.

---

---

# The page

---

## Part 1 · Opening

> *The reader's question: who are you, and have you actually done this?*

### 1.1 Hero

> `eyebrow` SURVEY SAMPLING VIA AD PLATFORMS
>
> `H1` **Population-representative samples, recruited through ad platforms.**
>
> `sub` You set the target distribution. We move ad budget between strata, hour by hour,
> until the achieved sample matches it. The method is published and the code is open.
>
> `.pri` Request a proposal  ·  `.sec` Read the paper

**[P-1] Hero readout** — recorded replay of a live stratum readout, bars filling toward
their target ticks. Recorded at launch, live as a fast-follow (D-013). Component:
stratum readout, `DESIGN.md` §8.

*Notes.* The hero states the mechanism, not the benefit (§2 rule 2), and the third
sentence is the provenance rule announcing itself before any number appears. No figure in
the hero — the totals band is four lines below it and two numbers in the first screen
compete.

### 1.2 Totals band

Component: stat row, four cells. Every cell carries its own source line.

> | 841,660 | 17,979,910 | 41 | 175 |
> |---|---|---|---|
> | RESPONDENTS | SURVEY RESPONSES | COUNTRIES | STUDIES FIELDED |
> | *Virtual Lab production database, August 2026* | *Virtual Lab production database, August 2026* | *Virtual Lab production database, August 2026* | *Virtual Lab production database, August 2026* |

`data-claim`: C-010 · C-016 · C-017 · C-019.

Prose beside the band:

> Since February 2020.

C-018 (2020-02-13). Source line on the prose: *Virtual Lab production database, August
2026.*

**The field-window line that used to sit here is gone.** It read *"half of those studies
finished fielding in under three weeks"* (C-011). Nandan, 2026-08-22: *"Fielded in three
weeks. I don't think that's really the right way to frame this."* He is right, and the
reason is structural rather than stylistic: **a field window is a design choice and
throughput is a capability.** A longitudinal panel and a one-week cross-section can recruit
at identical rates and report windows months apart — C-011's own IQR is 8 to 90 days, a
spread that wide means the median is not describing one thing. What replaces it is §1.2b.

*Notes.* Public copy says respondents, responses, countries, studies and nothing else: no
platform, no schema, no migration (C-019 publication rule 2). **If C-011 is ever restated
anywhere, the only sanctioned phrasing is "half of studies field in under three weeks"** —
the median *actual* window is 19 days, and **never "typically two weeks,"** which is the
planned figure and is not what ran.

### 1.3 Coverage

On paper ground, never an ink band (D-019, and Home is at its two-band limit).

> `H2` **Where the respondents are**

No claim, no source line — the heading names what the three artefacts below it show, and
they each carry their own figures and their own source lines.

**[P-2] Coverage map** — cropped choropleth, five opacity steps by order of magnitude,
covered-but-uncounted countries as a dashed outline (D-018). Generated by
`scripts/build-coverage-map.py`; never hand-drawn.

**[P-3] Region strip** — one horizontal bar, regions largest first, width carries value
and opacity carries rank. Generated. Spans attributed respondents only.

**[P-4] Region totals** — six cells at region scale. **Ships only if the region buckets
are confirmed** (`CLAIMS.md`, open, owner Nandan); the recorded fallback is that this
section publishes country figures and drops the regional layer entirely.

Prose under the artefacts:

> Country figures cover 738,608 of the 841,660 respondents. The rest belong to studies
> whose strata carry no country tag, and four covered countries have no count yet — they
> are drawn as coverage, never as zero.

C-010, and the per-country table. Source line: *Virtual Lab production database, August
2026; 37 of 41 countries counted.*

*Notes.*

**The lede was cut on 2026-08-22 and so was the field-office sentence.** The lede read
*"What a study needs is an ad platform and a messaging app."* Nandan: *"it's cute. If
there's something we actually wanna say there, let's say it. We don't need a messaging
platform. We could use a web form, so that doesn't seem very accurate."* **He is right on
the facts as well as the tone** — C-057 says a respondent answers in Messenger, WhatsApp
**or a web form**, and the web form is a study-level destination, so a messaging app was
never a requirement. The line was a *requirements* claim that the register does not
support. **This reverses a framing `AGENTS.md` recorded as settled**; the guide is updated
in the same change.

**C-032 is no longer published anywhere.** The row stays `VERIFIED` — there genuinely is no
field office in Nigeria, Jordan, Iraq or Bangladesh — but Nandan cut it: *"let's remove the
field office stuff. No need to say that."* It was always a fact in search of an argument,
and the argument it was reaching for is one of the two banned framings below.

**What replaced it is a plain heading and nothing else.** The section's substance is the
map, the strip and the totals; each carries its own figures and its own source line, and
the paragraph beneath them states the denominators. A heading that adds a claim on top of
three artefacts that already state their own is a heading looking for something to do.

**Two framings stay banned** and neither is affected by the cut: *strongest where panels
are weakest* and *where conventional fieldwork cannot go*. Both need rows `CLAIMS.md` does
not have, and D-023 forbids the comparison independently.

**Unchanged:** the four countries with no count and the 103,052 unattributed respondents
are **two different gaps** and may never be run together (`DESIGN.md` §8). Any share
carries its denominator or is not published as a share at all — MENA is 42.2% of attributed
respondents and 37.0% of the headline, and a page printing the first beside the second does
not reconcile.

---

### 1.4 How fast a study fills, and what the advertising costs

**Both box plots sit here, in one beat.** Nandan, 2026-08-25: *"both of the box plots should
be in a similar beat… these box plots early on set a really nice tone of hey, this is what
we do and we've done it a lot."*

> `H2` **How fast a study fills, and what the advertising costs**

**[P-10] Throughput figure** — `assets/figures/throughput-box.svg`. Respondents recruited
per study on a day of active recruitment: median 140, middle half 69–300.

**[P-11] Advertising cost figure** — `assets/figures/ad-cost.svg`. Advertising cost per
respondent newly recruited: median $1.05, middle half $0.29–$1.57.

> Both are distributions across studies, not averages. The spread is the useful part.

`data-claim`: C-089, C-090, C-091. Each figure carries its own two source lines; the prose
above states no number either figure does not.

*Notes.*

**Why they belong together and belong here.** They answer the two questions a reader has the
moment the totals band lands — *how fast* and *how much* — and they answer them with
distributions rather than with adjectives. Split across the page they read as two facts;
side by side they read as **what running a study actually looks like, 44 to 129 studies'
worth of it.** That is the opening's job: *this is what we do, and we have done it a lot.*

**They are built as one pair on purpose.** Same form, same M3 interval on the same M4 tick
rule, same box-and-whisker convention, both generated from `scripts/data/*.json` by scripts
that refuse to draw a value outside their own axis. A reader who learns to read one has
learned to read the other.

**The advertising figure is not a price.** Not the incentive, not the survey platform, not
our fee. It states "advertising only" in its own source line and the prose beside it must
never undo that.

**Neither figure computes a delivery date or a quote.** *A 2,000-respondent study fills in
two weeks and costs $2,100* multiplies two medians and assumes no idle days and no other
line items. The median study has 11 active days inside a 19-day window (C-090, C-011).
**These set expectations; they do not price a study.**

**The floors are published, not hidden.** An *active day* is a study-day recruiting at least
20 respondents; the cost figure counts studies with at least 200 newly recruited respondents
whose respondents are at least 80% their own. Both thresholds are analyst's choices and both
appear in the source lines.

### 1.5 The client wall

Component: client wall, §8 — **rewritten 2026-08-25 for marks rather than type.** Nandan:
*"There's really no need for study names. That looks stupid. What we need is the logos
themselves. It can just be 'used by researchers from' for all logos. Use real logos."*

> `H2` **Used by researchers from**
>
> [World Bank] · [Columbia University] · [George Washington University] ·
> [Harvard University] · [University of Washington] · [Washington University in St. Louis]

**[P-9] Six institutional marks** — monochrome `currentColor` SVG, uniform **optical** height,
no colour, no mark larger than another, each with `role="img"` and a `<title>`. **Not
supplied and not in the repo.**

`data-claim`: C-020, C-024, C-025, C-094, C-095, C-096 — **all `VERIFIED`.**

*Notes.*

**One heading for all six.** "Used by researchers from" is true of the commissioned work as
well as the unpaid use, and it is the weaker claim, so it covers everything without a second
frame. No engagement text under any mark.

**The wall degrades, and that is now the shipping mechanism rather than a fallback.** A mark
that is cleared and supplied renders as a mark; anything else renders as the institution's
name in type in the same cell. **The page ships with any mix**, and marks drop in as they
arrive.

**Two things are needed before a mark renders, and they are separate.**

1. **The file.** Vector, from the institution's own brand portal — not traced, not redrawn,
   not fetched from a search result. **There is no logo asset anywhere in this repo or in
   `../proposals`**; every one has to be supplied.
2. **The permission.** **D-014 is live again**, and it went from "moot" to blocking this
   component the moment the wall stopped being type. A wall of marks on a commercial site
   implies a relationship, which is the use most university trademark policies restrict.

**All six institutions are now sourced.** Harvard, University of Washington and Washington
University in St. Louis were confirmed by Nandan on 2026-08-25 as **operator knowledge** —
the same source type as C-032 — and are `VERIFIED` as C-094 to C-096. **The names may be
published.** What each still needs is a mark and its clearance, which is D-014 and is a
separate question: a verified row licenses the *relationship*, never the *logo*.

**This is the site's one exception to hard rule 8** — a third-party mark is somebody else's
artwork and cannot be built from the four primitives. §8 records the exception and its limit:
this component only.

---

## Part 2 · What it takes, and what does it

> *The reader's question: what is actually involved in this?*

**Rebuilt 2026-08-25 on Nandan's structure.** The framing is deliberately **not** *"why don't
you do this yourself"* — that makes a claim about the reader. It states the job and lets them
do the arithmetic, which is `DESIGN.md` §2 rule 2 working properly.

Four beats: **the recipe · the math · the paper · the instrument.** They map onto §1's frame
exactly — the job, the method, the evidence, the technology.

### 2.1 The recipe — paper ground

> `H2` **What it takes to recruit respondents on social media**
>
> - **One ad set per stratum**, each targeting a different slice of the population.
> - **Spend adjusted continuously**, so every stratum fills toward the share you asked for
>   rather than the share that happens to be cheap.
> - **The allocation itself revisited as prices move** — some strata cost many times what
>   others do, and the budget has to go where it buys the most precision.
> - **Keeping the same person from answering twice.**
> - **Paying an incentive to each respondent**, in their own country and in a form they
>   can actually use.
> - **The same people found again months later** for an endline.
>
> Every one of those runs for as long as the study is in the field. The median study takes
> 61 budget reallocations; the longest ran to 1,308.

Source line: *Virtual Lab production database, August 2026; 109 studies.* `data-claim`: C-092.

*Notes.*

**No count on the ad sets, deliberately.** C-093 puts the median study at **six** strata and
p90 at eighteen, so "dozens of ad sets" is not a claim this register supports. "One ad set
per stratum" lets the reader multiply by their own design, which is the point of the reframe.

**"Keeping the same person from answering twice" is a requirement, not a capability claim.**
C-069 covers one run per form per **account** and its scope note is emphatic: **never write it
as a fraud or duplicate-prevention claim.** C-077 is `WITHHELD` for want of any measurement.
Stating the job here is safe; §2.4 answers with the mechanism and stops.

**The gap between "person" here and "account" in §2.4 is deliberate and visible.** The job is
about people; what the instrument enforces is per account. Closing that gap in the copy would
be the overclaim the register forbids, so the two lines are allowed to not quite meet.

**The incentive line was rewritten 2026-08-25.** It read *"Incentives delivered to people you
know only through the platform,"* which Nandan found confusing — it gestured at the
difficulty instead of naming it. The difficulty is that a respondent is identified by a chat
account and nothing else, so there are no bank details and no local presence; §2.4's airtime,
gift card and data bundle are the answer, and the recipe line now names the problem those
solve.

**The list must read as the job, not as our features.** It is ordered by when each thing
happens in a study, so it reads as a process. That is the difference between this and the
inventory D-027 was written to kill.

### 2.2 The math — ink band

**Ink band 1 of 2**, the footer being the other, separated by three sections. It marks the
turn from *here is the job* to *here is the method*, which is a better use of the site's one
contrast device than the statistic that used to sit here.

> `H2` **The third of those is an optimization problem**
>
> You are choosing how many respondents to recruit in each stratum. You want the smallest
> variance on your weighted estimate. You are bounded by what you can spend and by the sample
> you need.

> **[MATH-1]** argmin over n₁…n_H of Σ_h W_h²σ_h²/n_h, subject to Σ_h p_h n_h ≤ B and
> Σ_h n_h ≤ N_d

> Where **W_h** is the weight of stratum *h*, **σ_h** its outcome dispersion, **p_h** what it
> costs to recruit one more respondent there, **B** the budget and **N_d** the sample you
> need. It is convex, so it has one answer:

> **[MATH-2]** n_h* = (W_h σ_h / √p_h) ÷ (Σ_k W_k σ_k √p_k) × B

> Budget shifts toward strata that are higher-variance, and away from those that cost more
> per respondent.
>
> **p_h is not known in advance.** It has to be estimated while the campaign is running, from
> the campaign itself. That is why this is software and not a spreadsheet.

Source line: *Donati & Rao, 2025.* Math carries `data-claim="none"` — see the note.

*Notes.*

**The math is the current manuscript's, not the posted SSRN edition's.** The two differ: SSRN
minimizes Σ W_h²/n_h under an equal-variance assumption; the live revision drops that
assumption, which is what introduces σ_h and yields the closed form. **Nandan, 2026-08-25:
*"quote the current, the SSRN will update, it's ok if it's out of sync for a minute."*** So
this is published ahead of the posted paper deliberately. **It is the one place on the site
where that is true, and it has an expiry:** when the revision posts, the two agree; if the
revision changes again, this block changes with it.

**Math notation is not a claim and `DESIGN.md` §8 did not cover it.** The exponents and
subscripts are notation, so both blocks carry `data-claim="none"`. §8 is updated in this
change.

**Nothing here is an AI claim** (hard rule 3) — it is convex optimization, named as such,
with the objective function printed. That is the strongest possible form of the true claim.

### 2.3 The paper — paper ground

> `H2` **The method is published**
>
> **Adaptive Survey Sampling via Ad Platforms**
> Dante Donati · Columbia Business School and CESifo
> Nandan Rao · Virtual Lab and Universitat Autònoma de Barcelona

Then the abstract, quoted verbatim inside `data-claim-quote="C-055"`, with its visible
attribution line — the same block already built for Surface 3. Then, in our own voice and
**outside** the quotation:

> The abstract describes the thirty-three studies analyzed in the paper. Our operating
> history is larger and is reported under *What we have run*.

> `.sec` Read the paper on SSRN →

*Notes.*

**This is the second use of `data-claim-quote` on the site, and hard rule 1 says a second use
is a signal to stop and ask.** Asked and answered — Nandan, 2026-08-25: *"It's ok to contain
abstract. Dont stress."* D-016 is amended accordingly.

**It also closes the open question §2.2 left behind.** The H1 claims *population-representative
samples*; with the abstract on the page, that claim is substantiated **on the same page**, in
the authors' own words, without the site stating an accuracy figure in its own voice. **6.1
p.p. therefore does appear on the homepage — as quotation, never as our sentence.** It may
not be pulled into a heading, a pull quote, or the clause beneath the block.

**Open, and small: does Surface 3 still earn a page?** It now holds the same quotation plus
BibTeX. Fold it in or keep it; nothing waits on the answer.

### 2.4 The instrument — paper ground

> `H2` **The rest of it is the instrument**
>
> The questionnaire runs as a conversation in the messaging app the respondent already
> uses — Messenger or WhatsApp — one question at a time, in their language.
>
> A form cannot be entered twice from the same account. Incentives are paid inside the
> conversation: mobile airtime, a gift card, a data bundle. A study can pause and resume, so
> one respondent takes a baseline and an endline in the same thread without re-enrolling —
> though reopening a conversation after the platform's messaging window closes needs a
> template that platform approved, per account and per language.
>
> At the end you take a CSV or read a keyed API, with every message exchanged alongside the
> responses.
>
> The instrument is called Fly, and it is open source.

`data-claim`: C-056, C-057, C-068, C-069, C-061, C-062, C-059, C-071, C-060, C-074, C-072,
C-052. No figures, so no source line.

*Notes.*

**Each paragraph answers a recipe line from §2.1**, in the same order: uniqueness, incentives,
follow-up, then delivery. That is what keeps it from being a feature list.

**"A form cannot be entered twice from the same account" is the exact limit of C-069.** It
says nothing about one person holding two accounts, and it must never be written as fraud or
duplicate prevention.

**Fly is named once, in the last line.** Not in the nav, where a label is a function rather
than a product name (D-024). Its visual signature is the thread, §6 M5 — no mark, no color,
no thirteenth icon.

**Still excluded and still easy to restore by mistake:** image collection (C-066, built then
pulled), Instagram (C-058, the docs site is wrong), "full multilingual support" (C-067 —
closed-ended answers only), and any form-builder implication (C-082 — surveys are authored in
Typeform; Fly imports and runs them).

**This absorbs most of what the walk carried.** Recorded so a future pass does not rebuild
the walk and say these things a second time.

---

## The close

> `H2` **Tell us what you need to measure**
>
> Tell us who you need to measure it among, where, and by when, and we will come back with a
> design, a timeline and a price.
>
> `.pri` info@vlab.digital

Paper ground, not a band. §8: the footer is the second ink band and promoting the close would
put two bands adjacent.

*Notes.* **The brief form is gone** (Nandan, 2026-08-25) and the conversion action is an
email address. It costs nothing to build, has nothing to handle and cannot break; the four
things a proposal needs — who, where, what, when — are in the sentence above it, so a reader
who writes in has been told what to say.

**The address renders as the button and as text**, so it is copyable as well as clickable.
`mailto:` is the href; the visible label is the address itself, never "Email us."

---

## Part 3 · The walk — off the homepage

**Removed 2026-08-25.** Nandan: *"I think part 3 should disappear for now. Let's just focus on
getting part two right. Then we're done with homepage."*

**Largely superseded rather than merely postponed.** §2.4 now carries the instrument, the
incentives and the follow-up; §2.2 carries the allocation. What the walk added beyond those
was narrative order and the respondent's point of view. **If it returns, it returns as
something the current Part 2 does not already say** — otherwise it is the duplication D-027
was written to prevent.

**The approved five-beat plan is kept** — you define the target and write the questionnaire ·
the ads run and the budget moves · someone answers · four months later the thread reopens ·
the study closes and you take the data — about 290 words, narrating rather than cataloguing.

---

---

# The audit trail

Folded in from the old Surface 5, 2026-08-25. Reached for by a procurement or IT reviewer,
so it is a section with its own anchor (`/#audit`) rather than a page.

> `H2` **There is no black box**
>
> **Open source** — the platform is public on GitHub and self-hostable on Kubernetes with
> Helm. `github.com/vlab-research`
>
> **Hosted in the EU** — production runs on Google Cloud, `europe-west`.
>
> **Encrypted** — in transit over TLS, and at rest.
>
> **Authentication** — Auth0.
>
> **Your data leaves whenever you want** — CSV export with preprocessing options, and a keyed
> REST API. Every message exchanged with every respondent is exportable alongside the
> responses.
>
> **Ethics** — the US validation study described in the paper was approved by the Columbia
> University IRB, protocol AAAV1539.

`data-claim`: C-052, C-050, C-051, C-053, C-074, C-072, C-054.

*Notes.*

**C-054 is the trap.** The approval covers **the validation study described in the paper and
nothing else**. "IRB-approved" without that scope is exactly the overclaim the register
exists to prevent, so the scope sits in the sentence rather than in a footnote.

**No data-protection capability claim appears here.** The instrument has no documented PII
policy, retention rule or erasure path; the privacy policy is a **company policy, not a
product feature**, and the two must not be blurred.

**Open source is stated twice on the page** — once in §2.4's closing line about Fly and once
here. That is deliberate: the first is about the instrument, the second about the platform,
and C-052 covers both. If one has to go, the §2.4 line goes.

---

---

# Cut on 2026-08-25, with reasons

**Kept here so nothing is re-derived from scratch, and so nothing returns by accident.**

**What else you can build** — the two design patterns, C-084 to C-088. Pattern 1 (delivering
a treatment into the feed) is fully sourced to the malaria paper. Pattern 2 (randomizing where
the treatment travels) may be described but its client, country and figures may not be named.
C-087 stays `PLACEHOLDER`. **All the material stands; only the surface is gone.**

**What we have run** — study cards. C-042 renders two dashes (no fielding year, no field
window), and C-040 and C-041 are `PLACEHOLDER` in full. **Two queries would fix most of it**
and they are the cheapest remaining wins: C-043 is one read-only query for the Italy field
window, and C-040/C-041 need their figures traced to campaign configs.

**The brief form** — replaced by `info@vlab.digital`.

**The paper as its own page** — rebuild it when a bylined PDF exists. Today the only compiled
edition is the blinded submission, so hosting one would hand a reader an author-less paper.

**Privacy stays built and stays unlinked** (Nandan, 2026-08-25). It still needs
`data-claim-scan="off"` on the legal copy when it is carried over, and **D-025 is still open**
— three things the instrument does are not described in it. Unlinked does not mean unamended:
if the policy is wrong, it is wrong at its URL too.

---

---

# Placeholder index

| | What | Where | Source / status |
|---|---|---|---|
| **P-1** | Hero readout — recorded replay | 1.1 | Component exists in spec (§8, stratum readout); recording to be made. Recorded at launch, live as a fast-follow (D-013) |
| **P-2** | Coverage map | 1.3 | **Generated** — `scripts/build-coverage-map.py`. Exists in `build/` |
| **P-3** | Region strip | 1.3 | **Generated** — same script. D-022 open: whether the unattributed remainder draws as a ghost segment |
| **P-4** | Region totals, six cells | 1.3 | **Generated, but gated.** Region buckets have no `CLAIMS.md` row; owner Nandan. Fallback recorded: ship country figures, drop the regional layer |
| **P-5** | ~~Deviation figure~~ | **unused** | Built and correct — `assets/figures/mad-comparison.svg`. Nothing renders it now that 6.1 is quote-only. **Do not delete** |
| **P-11** | Advertising cost figure | 1.4 | **Built** — `assets/figures/ad-cost.svg`, from `build-adcost-figure.py`. Box plot across 44 studies |
| **P-10** | Throughput figure | 1.4 | **Built** — `assets/figures/throughput-box.svg`, from `build-throughput-figure.py`. Box plot: M3 interval on an M4 tick rule |
| **P-9** | Six institutional marks | 1.5 | **Not supplied.** No logo asset exists in this repo or `../proposals`. Needs the file *and* clearance — **D-014 is live again** |

**No placeholder stands in for a number.** Where a figure has no `VERIFIED` row the page
renders `—` (hard rule 2); the placeholders above are images, generated artefacts and one
recording.

---

# What this copy deliberately does not say

- **No comparison with another recruitment source, anywhere** — no panel, no LLM digital
  twins, no "closer than" in any form (D-023). The one place a comparison appears is inside
  the quoted abstract on Surface 3, as somebody else's sentence.
- **No cost-per-question figure in our own voice** (C-004). The walk's cost readout is
  per participant.
- **No AI** (hard rule 3). The optimizer is convex optimization, and beat 2 says so.
- **No claim about fraud, duplicates, identity verification or completion rates** — no
  measurement of any of them exists (C-076, C-077).
- **No image or file collection** (C-066 — built, then pulled).
- **No Instagram** (C-058 — the docs site is wrong about this).
- **No "full multilingual support"** (C-067 — closed-ended answers only).
- **No form builder** (C-082 — surveys are authored in Typeform; Fly imports and runs).
- **No platform, schema or migration language**, anywhere, for any figure (C-019
  publication rule 2).
- **No "33 studies across 23 countries"** outside the quoted abstract (C-001, C-002).
- **No IRB claim beyond the validation study** (C-054).
- **No regional share without its denominator** — and no share at all until the buckets
  have a row.
- **No delivery date computed from the throughput median** — *"a 2,000-respondent study
  fills in two weeks"* divides a headline by a median and assumes no idle days. The median
  study has 11 active days inside a 19-day window (C-089, C-090, C-011).

---

# Open, 2026-08-25

**One of these blocks the page. The rest do not.**

1. ~~**The three unsourced universities.**~~ **Closed 2026-08-25** — confirmed as operator
   knowledge, C-094 to C-096 are `VERIFIED`, and all six names may be published. **No copy is
   blocked.** What remains is D-014: the marks and their clearance.
2. **Which SSRN edition is posted.** Ten seconds for Nandan. The page cites and links the
   paper; if the blinded submission was uploaded, a reader gets an author-less document under
   a byline we printed.
3. **The region buckets.** Confirm them and the six regional totals ship with a row; decline
   and coverage publishes country figures only. Fallback recorded either way.
4. **D-025, the privacy policy.** Still open, and still open even though the policy is now
   unlinked — three things the instrument does are not described in it.
5. **D-022** — whether the region strip draws the unattributed respondents as a ghost segment.
6. **D-021** — two motif rules, one of them live drift in `assets/mark.svg` (cell 6 / pitch 8,
   a ratio §6 does not sanction).
7. **The homepage math is ahead of the posted paper**, deliberately and with an expiry. Revisit
   when the revision posts.
8. **Two cheap wins whenever studies return:** C-043 is one read-only query for the Italy field
   window; C-040 and C-041 need their figures traced to campaign configs.

**Reopened the same day:** **D-014**. The wall moved from type to real marks, so logo
clearance is live again and now blocks the client wall — though not the page, which ships with
the wall degraded to type. **Each mark needs two separate things: the vector file, and the
permission.**
