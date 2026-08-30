# Decisions

The decision log for `vlab.digital`. Two halves: what is **settled** (do not
relitigate) and what is **open** (do not decide alone).

**Format.** `D-nnn` numbers are permanent. A decision that gets reversed is marked
`Superseded by D-nnn` and kept — the reasoning is worth more than the tidiness.

**If you are an agent:** check this file before asking the user a question and before
making an assumption. An `OPEN` decision is not yours to make; surface it, recommend,
and wait. A `SETTLED` decision is not yours to improve; if you think it is wrong, say
so in a sentence and follow it.

---

## Settled

> **Standing note, 2026-08-22: every placement clause below is contingent.** D-007 is open and
> the site has **no sitemap** — there is a design system and there is content material. Where
> a decision below says a thing goes *on Home*, *on the Papers page*, *on Platform*, or on any
> other page, **the substance is settled and the destination is not**: the page it names is
> from a structure that no longer exists. This affects D-013, D-015, D-016, D-019, D-020 and
> D-024. Do not read those clauses as a sitemap, and do not "restore" a page because a settled
> decision mentions one.

### D-001 — Primary audience is institutional buyers, academics second
**Status:** Settled · 2026-08-19

Funders, UN agencies, multilateral banks, foundations and M&E primes are the primary
conversion path. Academic PIs are the secondary track that feeds referrals and
co-authorships.

**Rationale.** Both audiences need the same reassurance — that the sample is
defensible — and differ only in what counts as proof: past performance for one, peer
review for the other. Ordering them means the page leads with named clients and
operating history, and puts the paper immediately after rather than first.

**Amended 2026-08-21 by D-024 — a category is added, and the ordering is unchanged.**

> Both audiences arrive with **two** questions, not one: *can this be done for my study*
> (feasibility) and *will the result hold up* (proof). D-001 orders the audiences; it does
> not order the questions. **Feasibility is answered first**, because a reader who does not
> believe the study can be run does not evaluate the evidence.

The rationale above describes the site's *proof* architecture exactly and was silent on
feasibility — which is why the sitemap, derived from a one-axis audience model, had no page
that answered a feasibility question. **The audience ordering is not touched**, and no third
audience is added: an intervention designer is a **role, not a market**, on staff at the M&E
primes, foundations and agency programme teams this decision already puts first, and their
proof standard is the PI's.

---

### D-002 — The site sells a managed service; the platform is proof
**Status:** Settled · 2026-08-19

We sell studies. The open-source platform is the credibility engine — transparency, no
black box — not the thing being purchased. Primary CTA everywhere is
**"Request a proposal."**

**Rationale.** The near-term revenue is client work. A self-serve SaaS funnel would
require pricing tiers, onboarding, and a dashboard ready for unaccompanied users.
Self-hosting stays visible and respected as a second path for the technical audience.

**Consequence.** No pricing page, no sign-up flow, no free tier. If that changes, this
decision is what has to be reopened first.

**Clarified 2026-08-21 by D-024, because the ambiguity let a gap open.** *"The open-source
platform"* above means **the recruitment optimiser**. It was written with one piece of
software in view, and there are two. **The survey instrument is part of the service being
sold, not part of the proof** — a buyer reads it as *scope*, the answer to what can be in the
study they are commissioning, and openness buys us little there because nobody audits a
questionnaire runtime. **The guardrail is the conversion action:** every page describing the
instrument converts to *Request a proposal*. The moment one converts to GitHub or to a
sign-up, it has become a product page and **this decision is reopened.**

---

### D-003 — Brand temperature: instrument-grade
**Status:** Settled · 2026-08-19

Dense, quiet, data-forward. Mono numerals, visible grid, near-monochrome, almost no
marketing language. Credibility through specificity. Not a research journal
(too dusty), not developer infrastructure (too hype).

---

### D-004 — Palette C, "Brass on cool paper"
**Status:** Settled · 2026-08-20

Ink chrome, teal data, brass accent and semantic, on a deliberately cool paper.
Full tokens in `DESIGN.md` §3.

**Rationale.** Considered four candidates. A ("Instrument") was correct but looked
like every serious research organisation. B ("Oxide") was the most differentiated —
every competitor in this market is blue — but oxide *chrome* makes every button and
nav item warm, which fights "reserved." D ("One Colour") was the most disciplined but
leaves navigation with too little to work with and would strain against any future
product surface. C keeps A's safety and spends its single point of boldness on an
accent nobody else has; the warm-metal-on-cold-ground clash is the instrument
reference made literal.

---

### D-005 — Colour does three jobs and nothing does two
**Status:** Settled · 2026-08-20

Chrome (ink), data (teal), accent + semantic (brass). Brass carries two jobs, which
works **only** because brass never appears inside a data fill.

**Rationale.** The Phase 1 draft had teal as both the link colour and the meaning of
"stratum on target." One hue carrying an aesthetic job and a semantic job means a
reader beside a chart has to guess which is which.

---

### D-006 — Build stack: Eleventy, version-pinned
**Status:** Settled · 2026-08-20

Eleventy. Pages stay as `.html` with front matter and a `layout:` line; the shell —
head, nav, footer — lives once in `_includes/base.html`; `_data/` holds study records
once per-study pages exist. Netlify runs `npx @11ty/eleventy` and publishes `_site`.
No component framework, no asset pipeline, no client-side router.

**Rationale.** The site needs exactly two things a plain directory of HTML cannot give
it: one definition of the shell across every page, and a data-driven loop for study
pages later. Eleventy is the smallest maintained tool that is those two things and
nothing else — the same shape as a hand-rolled include-expander, without us owning the
expander.

**This reverses the recorded recommendation, which was Astro.** That rationale rested
on Markdown authoring keeping the Phase 3 copy deck editable by a human. The site is
agent-edited from here and editing HTML directly is acceptable, so the premise is gone,
and with it the reason to accept a larger toolchain. Options considered:

| Option | For | Against |
|---|---|---|
| Static HTML + CSS, no framework | Nothing to maintain; every file is true as committed | The shell gets hand-copied per page and drifts — the exact decay `DESIGN.md` exists to prevent |
| **Eleventy** ✔ | HTML-first; layouts and `_data/` and nothing beyond them; Netlify-native; ships no client JS of its own | `node_modules` — accepted explicitly, version-pinned with a lockfile |
| Hugo | A single pinned binary, no dependency tree at all | Go templates and a content model to learn and then work around |
| Astro | Components, Markdown content collections, islands | More than a set of hand-designed pages needs; most of it would sit unused |

**Consequence.** Build-time validation is **not** delegated to the framework. The check
that matters — every number on a page traceable to a `VERIFIED` row in `CLAIMS.md` — is
a standalone script beside `check-contrast.py`, and would have been written whatever
the stack chosen.

**Out of scope:** folding in `docs.vlab.digital` (D-008). It may share this site later;
that is not a constraint on this decision.

---

### D-011 — Under-target is encoded by hue *and* pattern
**Status:** Settled · 2026-08-20

Hatched brass with an inset border, not brass alone.

**Rationale.** Costs nothing, survives greyscale printing and colour-blind readers.
For a company selling measurement accuracy, redundant encoding is the kind of detail a
methodologist notices — and colour then reinforces the state rather than carrying it.

**Consequence, recorded 2026-08-20: the hatch does not exist below about 24px.** At 16px
a 3px-period 135° hatch is sub-pixel and renders as flat brass at best. Building the
favicon exposed it. **The redundancy requirement stands and is met by a different second
channel at that size:** the under-target bar is brass *and* stops visibly short of the
target tick, while the on-target bar reaches it. Length is the encoding M2 is actually
about, so nothing is lost. `DESIGN.md` §6 M2 now states the size threshold rather than
leaving it to whoever next draws at icon scale.

---

### D-012 — Self-host the fonts; do not use the Google Fonts CDN
**Status:** Settled · 2026-08-20

**Rationale.** LG München I (Jan 2022) held that embedding Google Fonts transmits
visitor IP addresses to a US server without consent, in breach of GDPR. We sell to EU
institutions and our own privacy policy states EU hosting. Loading fonts from a US CDN
contradicts the page it sits beside.

**How.** *Done 2026-08-20.* The kit lives in `fonts/` at the repo root and is declared
in `css/fonts.css`. Nothing loads from a Google origin at runtime.

| Face | Weight | For | File(s) in `fonts/` | Origin |
|---|---|---|---|---|
| Zilla Slab | 300 | Display, wordmark | `ZillaSlab-300-{latin,latin-ext}` | Copied from proposals — byte-identical to Google's current build |
| Zilla Slab | 400 | `h3`, study-card titles, client wall | `ZillaSlab-400-{latin,latin-ext}` | Fetched |
| Source Sans 3 | 400, 600 | Body, UI, nav, buttons | `SourceSans3-400-600-{latin,latin-ext}` | Fetched — **one variable file per subset, carrying both weights** |
| Source Serif 4 | 400 | Abstracts, source lines | `SourceSerif4-400-{latin,latin-ext}` | Fetched |
| IBM Plex Mono | 400 | Numerals, table cells, code | `IBMPlexMono-400-{latin,latin-ext}` | Fetched |
| IBM Plex Mono | 500 | Eyebrows, labels, stat numerals | `IBMPlexMono-500-{latin,latin-ext}` | Fetched |

**271.7 kB** across both subsets; **130.9 kB** is the latin half, which is all an English
page fetches. Source Serif 4 300/700 and Source Sans 3 Bold sit in the proposals
directory, are not in §4, and were **not** carried over. Adding a weight is a `DESIGN.md`
§4 change first.

**Three things to know before touching this.** Google publishes Source Sans 3 only as a
variable font — there is no static instance to fetch and no subsetter installed here — so
one file per subset carries the weight axis and two `@font-face` rules point at it. That
is also the smaller option: 28.7 kB of variable latin serves both weights where two
statics would run to roughly 32 kB. The `unicode-range` values in `css/fonts.css` are
Google's own latin / latin-ext partitions, copied verbatim from the CSS2 API, so each
range matches the file it selects — **never hand-edit a range; refetch the pair
together.** And Source Serif was refetched rather than copied for exactly that reason:
the proposals copy predated Google's current latin partition by a few hundred bytes of
glyphs, which would have left those codepoints falling through to the fallback while the
range claimed to cover them.

**Note.** The design mockups published as Artifacts use the CDN because the Artifact
CSP permits no other font host. That is a constraint of the preview, not the spec.

---

### D-018 — The coverage map is a cropped choropleth with hairline borders
**Status:** Settled · 2026-08-20

Countries where we have fielded a study are **filled in `--data`** at one of five
opacity steps by order of magnitude. Every other country is a **hairline outline in
`--rule`** — present as context, never filled. The frame is **cropped to the bounding
box of the covered countries.** Countries covered but not yet counted are a dashed
outline and are never drawn as zero.

Generated by `scripts/build-coverage-map.py` from `scripts/data/coverage.json` and a
vendored Natural Earth 1:110m boundary file. **Do not hand-edit the SVG.**

**Rationale.** The map has to answer one question — *where* — for a buyer who wants to
know whether we can reach their population. Literal geography answers it instantly and
nothing else tested did. The hairline treatment turned out to be load-bearing rather
than cosmetic: without the surrounding borders the covered countries lose the frame
that makes them read as places rather than as shapes.

**Considered and rejected**, in the order they were tried:

| | Why not |
|---|---|
| Partitioned lattice field; tile-grid cartogram | Abstracted away the one thing the graphic is for |
| Ranked bar ledger | Sorting by volume puts the US on top and buries the countries no panel provider reaches, which is the differentiator |
| Full-frame choropleth, filled ground | Empty countries occupied most of the picture |
| Non-contiguous cartogram (shapes scaled by respondents) | Displaced shapes still read as a map, so position becomes a lie; shape recognition fails for exactly the small countries it was meant to rescue |
| Cell cartogram (squares at centroids) | Honest and efficient, but discards the instant recognition that makes the map work |
| Dissolved coastline, with and without ground tone | Quieter, but removing the borders cost more legibility than the emptiness did |

**Consequence — this settles the §6 map question.** A choropleth carrying real values
with a legend is sanctioned. A dotted world map with arcs between cities, and any
rotating or wireframe globe, remain banned. `DESIGN.md` §6 now states the boundary
rather than leaving it to judgment.

**Cropping does less than expected, for a good reason.** The footprint spans Belize to
Papua New Guinea — roughly 235° of longitude. Cropping removes about a quarter of the
height and almost none of the width. The map is wide because the work is.

**Correction 2026-08-20 — the published legend labels were wrong.** The record read
`under 1,000 · 1,000+ · 10,000+ · 50,000+ · 100,000+`. The code that fills the map has
always been `int(log10(v))` clamped to 1–5, so the true steps are `under 100 · 100+ ·
1,000+ · 10,000+ · 100,000+`. Under the old labels Germany (23) and Ireland (206) sat in
one bucket labelled "under 1,000" at two different opacities, and every country from
1,000 to 9,999 — twenty of the forty-one, the largest bucket — was labelled "10,000+".
The labels are now **generated** from the same function that fills the shapes, so they
cannot drift again. The opacity steps, cropping and ghost borders are unchanged: this
corrects the record, not the decision.

### D-013 — Hero readout: recorded replay at launch, live as a fast-follow
**Status:** Settled · 2026-08-20 · *was OPEN; resolved by Nandan*

The homepage hero is a stratum-fill readout driven by a **recorded replay of a completed
study**. Live-from-production is a fast-follow, not a launch requirement.

**Rationale.** A replay is honest, carries no disclosure risk, and is indistinguishable
to a visitor. Live would be the most compelling thing the site could do, but it needs an
aggregate endpoint, a defined fallback for when nothing is recruiting, and a disclosure
decision about showing a client's fieldwork in progress. None of those should hold the
build. A read-only production endpoint had been offered, which is what reopened the
question; it is what makes the fast-follow cheap, not what makes live a launch blocker.

**Consequence.** The replay is a static fixture committed beside the page, taken from a
completed study whose figures are `VERIFIED` in `CLAIMS.md` **and** cleared for
disclosure — the same two tests a study must pass to earn a detail page (D-007). Build
the component so the fixture can be swapped for a live endpoint without a redesign: same
data shape in, same render out. **Phase 4 is no longer blocked on this.**

---

### D-020 — Home leads with a four-cell totals band, not a stat row
**Status:** Settled · 2026-08-20 · *was OPEN; resolved by Nandan*

The four-cell stat row (33 · 23 · 6.1 p.p. · 1,500) is dropped. Home carries a
**four-cell totals band** — **841,660 respondents · 17,979,910 survey responses · 41
countries · 175 studies fielded** — sourced from production, and the validation
comparison becomes its own moment further down the page.

**Revised 2026-08-20 by Nandan: four cells, with the study count.** The first settlement
was a three-number band; two things moved it. C-019 became `VERIFIED` at 175, so a study
count is publishable where it previously was not. And three cells is a design-system
deviation where four is not: `DESIGN.md` §8 specifies the stat row as **four cells** and
§5 fixes the 760px breakpoint as **stat row → 2×2**, a rule that only makes sense with
four. Three cells give 2 + 1 orphan at that breakpoint and would need a new responsive
rule; four cells are the component that already exists, tested and contrast-checked.

The contest for the fourth cell was **median field window (C-011, 19 days)** against
**studies fielded (C-019, 175)**, and Nandan took the study count.

**Rationale.** The stat row failed review on two grounds, both of which held up. The
scale numbers came from the paper rather than production and materially understated the
business (41 countries, not 23 — C-017). And a validation figure dropped into a grid of
operating figures is a category error: 6.1 p.p. is a deviation from a benchmark, and it
means nothing to a reader who cannot see the benchmark, the instrument or the scale
beside it. It needs a section, not a cell.

**Rationale corrected 2026-08-20 (D-023).** This paragraph previously argued that 6.1
p.p. "means something only beside Prolific's 7.1 and digital twins' 11.1." That reason is
now wrong — the site publishes no comparison with another recruitment source, and
C-006–C-009 are `WITHHELD`. The decision is unchanged, because the second ground never
depended on the comparators: what makes 6.1 legible is the benchmark it is measured
against and the scale it is drawn on, both of which live in the validation section and
neither of which fits in a stat cell.

**Consequence.** `CONTENT.md` Home §2 is rewritten. The band's figures are C-010, C-016,
C-017 and C-019; its source line is the production database and its `as_of` date, never
the paper — per `CLAIMS.md`, Donati & Rao is not a source for scale. The publication rules
bind here specifically: respondents, never "people reached" (C-015 is `WITHHELD`), and no
platform, schema or migration language on a public page — **175 is never explained by
naming a platform split**, on this band or anywhere else. Validation moves to its own
section, which is where a figure that needs its benchmark and its scale beside it
belongs.

**Consequence — field time has to land somewhere else on Home.** `CONTENT.md` copy rule 4
says field time is always stated where it is known, and C-011 is `VERIFIED`. Taking the
study count in the fourth cell means the **median field window (19 days) moves into the
prose beside the band**, not off the page. `CONTENT.md` Home §2 records where it sits.
Dropping it silently would put the deck in breach of its own copy rules on day one.

**Consequence — 17,979,910 will not fit, and the fix is not rounding.** Ten characters in
Plex Mono at up to 42px. Never "18M" or "18 million": `DESIGN.md` §2 rule 6 forbids two
roundings of one figure, and the exact number *is* the argument. Solve it with a size step
on that cell, or a `clamp()` floor tuned to the longest value in the row.

**Not taken: an eyebrow.** "OPERATING SINCE FEBRUARY 2020" (C-018) above the band was
drafted and would need a line added to the `DESIGN.md` §8 stat-row spec, which has no
eyebrow. C-018 sits in the adjacent prose instead, which costs nothing but adjacency and
leaves §8 alone.

**Settled since, in D-019: Home carries both.** The band is the Home answer to *how
much*; the map answers *where*. The two must not restate each other — see D-019 for how
they are differentiated, and `CONTENT.md` Home §5 for the copy that keeps them apart.

---

### D-023 — The site makes no comparative claim against another recruitment source
**Status:** Settled · 2026-08-20 · *was recorded as an open framing question under C-006*

**Nandan: "Don't lead with any gap, we'll leave that off the website entirely, no need to
compare."** No page compares Virtual Lab's representativeness with a panel provider, with
LLM digital twins, or with any other recruitment source. `CLAIMS.md` C-006, C-007, C-008
and C-009 are **`WITHHELD`** — decided against, not pending.

**Rationale.** The two comparisons the paper supports are not equally sound. The gap to
digital twins is robust. The gap to Prolific is not: the paper reports no interval on any
MAD, and the authors' own July 2026 analysis puts the difference at −0.62 p.p. with a 95%
CI of [−1.24, +0.08]. Publishing both would publish a comparison the authors are already
revising. Publishing only the twins gap would invite the reader to infer that the panel
comparison went the other way. Publishing the panel gap as parity-or-better would still
be a competitive claim resting on a figure under revision. **So the site does not compete
on the comparison at all** — it publishes its own accuracy against gold-standard
benchmarks and lets that stand on its own.

**Scope.** What is dropped is comparison against *other recruitment sources*, **in our
own voice**. That qualifier was added 2026-08-21 and is not a softening — see below.

- **Quoted source text is out of scope.** The Papers page reproduces the paper's abstract
  verbatim (D-016), and that abstract names Prolific and digital twins and says the method
  improves "on both". It ships. **Nandan, 2026-08-21, shown the sentence and asked
  directly: "keep it — quotation is quotation."** The same distinction that admits the
  withheld $0.30 admits this: D-023 governs what Virtual Lab asserts, and reproducing a
  source accurately is a different act from asserting its contents. The boundary is hard
  and is recorded in `CONTENT.md` and `CLAIMS.md` as well as here: **quoted only.** Never
  pulled out of the block, never restated in a heading, never summarised beneath it, never
  repeated in our own copy, never used to justify a comparative claim elsewhere. If any of
  that starts happening, reopen this decision — do not trim the quotation.
- **This corrects the premise this decision was settled on.** On 2026-08-20 D-023 was
  taken on the understanding that no comparison would appear anywhere on the site. That
  became false the moment the abstract was restored, and a settled decision resting on a
  false premise is how the decision gets reopened by someone who spots the contradiction
  before they find this paragraph.
- **The irony is worth recording.** The comparison the abstract carries is the
  *manuscript's* version — the one the authors' own newer analysis walks back, and whose
  weakness is the reason for this decision. We are not endorsing it; we are quoting a
  document a reader can open for themselves, which is the point of a citation page.
- **C-003 is unaffected and stays publishable.** 6.1 p.p. against GSS, CPS and Pew is our
  own measurement against gold-standard benchmarks, not a ranking against a rival. It is
  the substantiation of "the sample is defensible," and without it the validation section
  has no evidence in it at all.
- **C-012 and C-013 are unaffected.** They compare cost, as ratios from the paper's own
  table, and C-013 runs against us — roughly 3× Prolific per question. An admission
  against interest is not a competitive claim. If the scope is ever read wider, C-013 is
  the row to reopen first, because the Method cost section is built on it.

**Consequences, all applied 2026-08-20.** `CONTENT.md` Home §4 is rebuilt around C-003
alone and its per-domain caveat paragraph is deleted — that paragraph existed to qualify
a comparison we no longer make. `DESIGN.md` §2 rule 5 no longer instructs future agents to
prefer the comparative. `assets/figures/mad-comparison.svg` was redrawn as a single bar on
the same 0–12 p.p. ruler. The Papers page carries no MAD figure at all (D-016).

**What this costs, stated plainly so nobody rediscovers it as an argument to reopen.**
The comparison was the site's strongest single sentence, and the validation section is
weaker without it. The replacement argument is not "6.1 is a good number" — nobody can
judge that unaided — it is that the deviation was *measured, weighted and published
against benchmarks we did not choose after the fact*, which is the same proposition as the
rest of the site. Do not reintroduce a comparator to make the number look better.

---

### D-019 — The coverage section goes on Home
**Status:** Settled · 2026-08-20 · *was OPEN and blocking Phase 4; resolved by Nandan*

The coverage section (map + region strip + region totals) lives on **Home**. The Studies
index carries **no map**. There is no reduced second copy anywhere.

**It is on paper ground, not an ink band.** `CONTENT.md` Home already runs two ink bands —
the validation section and the footer — which is the `DESIGN.md` §8 limit. **The resulting
Home order is: hero · totals band · how a sample is built · validation (ink band) ·
coverage (paper) · studies · client wall · close · footer (ink band).** The two bands sit
at positions 4 and 9 with four sections between them, so §8's "never adjacent" rule holds.
The closing CTA still may not be promoted to a band: it would be both a third band and
adjacent to the footer.

**Rationale, on plain layout grounds.** The map answers *where*, which is the question the
totals band raises and cannot answer — a reader who has just seen "41 countries" wants to
know which ones, and the answer is one scroll away rather than one click away. The Studies
index is a scannable list of cards for a procurement reader; a full-width map at the top of
it delays the cards without adding a fact the cards do not carry. *Both, reduced on Home*
was rejected for the cost recorded when this was open: two maintenance surfaces for one
dataset, where every refresh has to touch both.

**Ruled out on evidence, and it still binds:** a reduced Home strip that drops the
denominator caveat. The 12.2% unattributed residual travels with any share, and the
highest-traffic position on the site is the worst place to omit it.

**Consequence — the band and the map must not restate each other.** Both are quantitative
and both are now on Home. The totals band carries the four scale figures (C-010, C-016,
C-017, C-019) and the prose beside it carries C-018 and C-011. **The coverage lede
therefore drops "forty-one countries since February 2020" and the median field window**,
which the band and its prose have already stated forty lines above, and carries only what
the band cannot: the distribution — the four largest samples outside the United States,
and the regional layer. Countries as a *count* belong to the band; countries as *places*
belong to the map. Copy in `CONTENT.md`, Home §5.

**The prerequisite recorded when this was open is now moot, and one thing that came out of
it stays.** Landing the map on Studies would have put the paper's "23 countries" in that
page's heading above a map showing 41; the heading was rewritten to 175 studies across 41
countries to discharge it. With no map on Studies the contradiction cannot arise — **but
the rewritten opener stays**, for an independent and better reason: the old one used the
paper's narrow claim (C-001, C-002) as an operating scale figure and understated the
business by eighteen countries. That was wrong on its own terms, map or no map.

**Do not reintroduce the client-mismatch reasoning.** An earlier draft argued the map and
the client wall "answer different questions whose answers openly disagree." Struck
2026-08-20 by Nandan: a client we cannot name is a confidentiality term, not a
discrepancy. It is now doubly irrelevant, since both sections sit on the same page and
neither claims the two distributions should match.

**One open item travels with the section and does not block the build.** The six regional
totals still have no `CLAIMS.md` row, because the region *bucketing* is an editorial choice
in `coverage.json` rather than a database fact. `CLAIMS.md` records the fallback: either
the buckets are confirmed and the six totals get a row, or the section ships with country
figures and no regional layer. Because that fallback exists, this is a content question on
Home, not a Phase 4 blocker.

---

### D-016 — The Papers page cites, links, and quotes the abstract verbatim
**Status:** Settled · 2026-08-21 · *reverses the reading taken on 2026-08-20; the earlier

**Amended 2026-08-25 — the abstract also appears on the homepage.** Nandan, asked because
hard rule 1 says a second use of `data-claim-quote` is a signal to stop and ask: *"It's ok to
contain abstract. Dont stress."*

**It does more work there than on Surface 3.** The homepage H1 claims *population-representative
samples*, and 6.1 p.p. was removed from the site's own voice the same day (C-003). The quoted
abstract substantiates the H1 **on the page that makes it**, in the authors' words, without
the site asserting an accuracy figure itself. **So 6.1 p.p. is on the homepage — as
quotation, never as our sentence**, and it may not be pulled into a heading, a pull quote, or
the clause beneath the block.

**Hard rule 1's "expected on exactly one page" now reads two**, both quoting the same
abstract and the same row. **A third use is still a stop-and-ask.**

**Left open, and nothing waits on it:** whether Surface 3 still earns a page once the homepage
carries the citation and the quotation. It would keep the BibTeX and the download.
record is kept below, because the reasoning is worth more than the tidiness*

**The page is** title · authors and affiliations · **the abstract, reproduced verbatim as
attributed quotation** · the citation · BibTeX · a link to whatever a reader can open.
**No cost table and no figures.** Copy in `CONTENT.md`, Papers.

**Nandan, shown the trade-off explicitly: restore the abstract, verbatim.**

**Rationale — and it is a distinction, not an exception.** A quotation is attributed
speech, not a claim. C-004 governs **what Virtual Lab asserts**. Reproducing what the
paper says, accurately, is the opposite of overclaiming; and a citation page that
**silently edited its own paper's abstract** would be the worse failure by some distance —
it is the one page whose entire job is to represent the source faithfully to a reader who
came to check it. The withheld figure is not laundered by this: it stays withheld in every
sentence the site writes in its own voice, which is every sentence on the site except one
quoted paragraph.

#### How this was decided twice, and why the first reading was wrong

**2026-08-20.** Asked how to handle an abstract that states $0.30 per question while C-004
is `WITHHELD`, Nandan said *"Don't put any of that stuff."* That was read as *no abstract*,
and the page was reduced to citation and download. The rationale recorded at the time
argued that quoting the paper's own words is not us making a cost claim — *"it is still
true, but it means the site would publish the withheld figure on the one page an academic
reader is deciding whether to trust"* — and concluded: **"an exception written into a rule
is how the rule stops being enforceable."**

**That argument is superseded, and the sentence above is the part that was wrong.** What
was built is not an exception to the rule; it is the rule applied to a different act.
Asserting a figure and quoting a source that asserts it are two different things, and a
register that cannot tell them apart cannot host a citation page at all. The 2026-08-20
reading also read a general instruction out of an answer to a narrow question: "that
stuff" was the cost material, and the cost material is still off the page.

**The reason is recorded here in full, and not just the outcome, deliberately.** A stale
rationale is how a settled decision gets reopened on a false premise — the next agent
reads "an exception is how the rule stops being enforceable", finds an abstract on the
page, and removes it as drift. It is not drift. It is this decision.

#### The enforcement, which exists and is tested

The distinction is checkable rather than argued, because `scripts/check-claims.py`
implements it. `data-claim-quote="C-nnn"` on a container marks its subtree as attributed
quotation: numerals inside are exempt from the banned-value check and from claim checks.
**The shield is deliberately narrow, and all three constraints are enforced, not
described:**

1. The container must name a **`VERIFIED` `CLAIMS.md` row for the document being quoted**
   — here **C-055**, the paper's SSRN URL. A quotation cannot be attributed to nothing, to
   a free-text string, or to a withheld row.
2. It must carry a **visible attribution line**, checked exactly as a figure's source line
   is.
3. Every withheld value it shields is **reported at `warn` level on every run**, naming
   the value and the row that withholds it. **The shield stops a build failing; it never
   stops a human seeing.**

Fixtures: `scripts/fixtures/quote-abstract.html` is the legitimate case (exit 0, one
warn), `fail-quote-unattributed.html` is the same attribute used as a loophole in three
shapes (exit 1). Suite: `python3 scripts/test-check-claims.py`.

**It is expected to appear once on the whole site.** A second use is a signal to stop and
ask, not a pattern to copy — see `DESIGN.md` §8.

#### What is still off the page, and why quoting does not reach it

- **The cost table.** Every row is denominated per question — ours, GSS traditional, GSS
  Follow-on, Prolific — so reproducing it publishes C-004 four times over, in a component
  whose entire job is to display values. **That is not quotation; that is publishing the
  figure in our own voice with the paper cited as an excuse.** This half of the 2026-08-20
  decision is unaffected and its reasoning still holds. Permanent under `WITHHELD`, not a
  deferred stage; the cost conversation lives on Method, in per-participant units.
- **The MAD figure**, per D-023, unchanged. The comparison it was built to carry is not
  published anywhere, and reproducing our own single deviation on a citation page adds
  nothing that Home's validation section — which has the benchmark and the ruler beside it
  — does not do better.
- **The abstract's comparative sentence is quoted, never used.** It reads "improving on
  both the online panel provider and LLM-based approaches", which is C-006 and C-007,
  `WITHHELD` under D-023. It ships only inside the quoted paragraph, by the same reasoning
  that admits the $0.30. It may not be pulled out, restated in a heading, summarised
  beneath the block, or repeated anywhere else. If that starts happening, the abstract is
  being mined for claims rather than reproduced, and the answer is to reopen this decision
  rather than to trim the quotation.

#### The "which population" clause comes back

The abstract's "over 33 studies across 23 countries" (C-001, C-002) sits against the
Studies index's 175 studies across 41 countries (C-019, C-017). One clause, in our own
voice, reconciles them: *the abstract describes the thirty-three studies analysed in the
paper; our operating history is larger and is reported on the Studies index.*

**It sits outside the quoted block.** Editing the abstract to fix a problem of ours is
exactly what verbatim forbids, and a clause of ours inside a quote block would inherit a
shield it did not earn — paraphrase inside a quotation is not quotation, and the checker
cannot tell the difference.

#### Unchanged by this reversal

**The citation year is settled: 2025, and it is published.** All four editions carry
`\date{September 15, 2025}`. The manuscript is JMR-25-0847, under a major revision, so no
journal may be named — this cites the working paper, and the BibTeX entry is `@misc` with
`howpublished = {Working paper}` for exactly that reason.

**The link landed 2026-08-20.** Nandan supplied the SSRN URL as co-author: **C-055,
`VERIFIED`** — `https://ssrn.com/abstract=5495148`. Source lines read **"Donati & Rao,
2025"** across `CONTENT.md`, and the BibTeX entry is **constructed, not found**, in
`_data/paper.json`. BibTeX was never blocked on the year; it was blocked on having no
`url`, and it now has one. **C-055 now carries a second job:** it is what the quotation is
attributed to, so it is no longer just the link — see `CLAIMS.md`.

**The URL is `VERIFIED` on the author's word and that is the whole of its provenance.**
Nobody here has read the SSRN landing page: SSRN sits behind Cloudflare and returns 403 to
any non-browser client. A co-author is authoritative for where his own paper is posted,
which is why the row is not a `PLACEHOLDER` — but **no posted date, revision date, page
count or SSRN version may be recorded**, because none has been seen.

**Still open for Nandan, and still a ten-second check: which edition is on SSRN?** The
only compiled PDF in the paper repository is `JMR_submission_09152025.pdf`, which is
**blinded and carries no byline**. If that is what was uploaded, a reader clicking our
download link gets an author-less document beneath our printed byline.
`SSRN_09152025.tex` is the bylined edition. Unanswerable from here.

**Two constraints survive unchanged.** Whatever is hosted cannot be the compiled PDF that
already exists: it is the **blinded** JMR submission and carries no byline, so a hostable
PDF has to be built from the SSRN edition. And the `Jul2026` working manuscript must not be
published at all — it is a live revision responding to reviewers.

#### One question this closes in practice

While the page was citation-and-download it was five lines long, and D-007's rejected
**"SSRN link only"** option was close enough that *"does this still earn a page, or does it
become a citation block on Method?"* was recorded as live. **The premise of that question
was the thinness, and the thinness is gone.** A page carrying the abstract, the citation,
BibTeX and the link is a page; it is also where the Home hero's secondary CTA — "Read the
paper" — has to land. Recorded as answered in effect, not as a new decision: if Nandan
still wants Papers folded into Method, that is his to say.

---

### D-024 — Fly is named; the recruitment side is cited, not branded
**Status:** Settled in part · 2026-08-21 · **split 2026-08-22**

> **What is settled here is naming, standing and the visual consequence. The placement half
> — "it earns the eighth page" — has been withdrawn into D-007**, which is now open and
> carries no page count at all. This entry was the case that produced D-007's process rule:
> it bundled three questions, and the placement answer rode along with the naming one instead
> of being argued. **Read every "page" below as "surface", and treat none of it as deciding
> where anything goes.**

**Nandan, closing it: "Accept as recommended."** Stated as four rulings, then the evidence
that decided each, then what it costs.

1. **Fly is named on the site.** It is the survey instrument — the questionnaire runs as a
   conversation inside a messaging app — and it is a separable artefact somebody can clone,
   `helm install` and meet without ever meeting us. **A name is earned by separability.**
2. **The recruitment side is not named.** It is "the optimizer" / "adaptive sampling", and
   it is **cited** — *Donati & Rao, 2025*. Its internal name `adopt` stays in the schema
   beside `chatroach` and `hermes`. You cannot obtain it without buying a study, so there
   is nothing for a public name to point at. **"Virtual Lab" keeps its overload** — company,
   managed service, and recruitment system — and the overload is now declared honest rather
   than tolerated silently.
3. **~~Fly gets a page, eighth, between Method and Studies.~~ Withdrawn 2026-08-22 into
   D-007.** That Fly needs a surface of its own is a finding the narrative pass should carry
   forward; that the surface is a page in a particular slot was never argued.
4. **Wherever it appears, a navigation label is a function, not a product name.** Fly carries
   the prose and the docs; a nav label says what the thing is for. A reader scanning a nav who
   does not already know the name cannot tell what the link is for. The same rule governs the
   three mechanism-step labels, which stay verbs: a proper noun in the third slot asks a
   reader to learn a name before they have learned the mechanism.

**Applied to the documentation nav, 2026-08-30 — ruling 4, and the docs were breaking
it.** The two top-level sections were labelled **Virtual Lab** and **Fly**: two product
names, which ruling 4 forbids in a nav. They are now **Study Recruitment** and **Fly
Surveys**. Nandan proposed both.

**The first was the worse offence.** A sidebar item reading *Virtual Lab*, sitting under a
brand mark reading *Virtual Lab · Docs*, on a site owned by *Virtual Lab, LLC* — ruling 2
declares that overload honest, and it is, but it becomes unreadable at exactly the moment
a reader has to choose between two tools. It also produced the page title
*"Virtual Lab — Virtual Lab Documentation"*.

**The asymmetry is the decision, not an oversight.** One label carries a product name and
the other does not, because rulings 1 and 2 say precisely that: Fly is named because it is
separable, and the recruitment side is not because you cannot obtain it without buying a
study. *Fly Surveys* also satisfies the register rule — the name carries its job in the
same breath, and a nav is often a first mention.

**The product names survive in prose**, on the section page each label opens and in the
landing list. That is the split ruling 4 describes: the label says what the thing is for,
the prose says what it is called — which is also what lets a reader match the label to the
header of the dashboard they are logged into.

**Standing — Fly is scope, not proof, and D-002 holds.** D-002's sentence, *"the
open-source platform is the credibility engine … not the thing being purchased"*, was
written with **one** piece of software in view: the optimiser. Two are in play and they do
opposite jobs. The optimiser being open *is* the credibility argument; a PI does not audit
a questionnaire runtime, and if Fly were closed the site's proposition would not move. What
Fly answers is *what can be in the study I am commissioning* — a specification of the
deliverable — which puts it on the **managed-service side** with Studies and Method, not on
the proof side with Platform and Papers. **The guardrail is the conversion action, and it is
the test of this ruling:** the page converts to *Request a proposal*. The moment it converts
to GitHub or to a sign-up it has become a product page and **D-002 is reopened.** This means
the site describes capabilities of software it is not selling as software — normal for a
managed service, and exactly what Method already does for the optimiser.

**Placement — withdrawn, and what is worth keeping from the argument.** Two tests were
established here and they are now recorded in D-007 for the narrative pass: content that
states **no figure** is not caught by the *"page of blanks"* test, and a surface whose job
sentence needs two clauses is two surfaces. What was **not** established is that the
instrument's material belongs in a page, in a slot, between two other pages. That was
assumed. **The finding that survives is narrower and still useful: the open-source argument
and the capability argument have different readers and different conversion actions, and
running them together produces a surface whose second half undermines the first.**

**The mechanism steps stay three, and the third is the instrument.** Wherever the
three-step sequence appears, the third step is **SURVEY**, not FIELD, and takes the §7
*Survey* icon it was always specified to take — the label had drifted to a logistics word
while the design system already knew the step was the instrument. The reopened thread is
drawn **inside** the third step with M5, **not** promoted to a fourth step: the first three steps are three
systems doing three things, and a wave is the same system running again — there is no fourth
mechanism to lead with. The "two systems" framing — a recruiter and an instrument, billed
equally at the top of Home — is **not available**, because it asks a buyer to evaluate an
architecture, which is the software-vendor framing D-002 rejects.

**Visual consequence — nothing new is drawn, and this is the settled part.** Fly's signature
is **radius**. §5 already reserves rounded corners for the thread alone and §6 M5 already
calls it *the one thing that separates us from every panel provider* — the system spent its
single radius exception on this product before the product was named. **No mark, no colour,
no thirteenth icon**; Fly uses `#icon-survey` and `#icon-waves`, two of the twelve icons that
already served it. Two things were built and rejected on evidence rather than taste:

- **A fourth brand hue is arithmetically impossible.** Any hue dark enough to pass AA on
  `--paper` lands within a **1.04–1.20 luminance ratio** of both `--data` and `--brass` —
  indistinguishable from both in greyscale, so a Fly colour would print as either "on target"
  or "under target" on a funder's black-and-white photocopy. D-011 forbids it.
  `scripts/check-fourth-hue.py`. `check-contrast.py` is unchanged; 22 pairs still pass.
- **Two marks fail at favicon size.** Rendered at 16 / 22 / 48px beside `assets/mark.svg`, a
  thread mark reads soft and round against a dense orthogonal lattice: **two companies, not
  two products.** The very exclusivity of radius that makes it a good *signature within* the
  system makes it a bad *sibling mark beside* it. `scratchpad/fly-mark-d*.svg` stay in the
  scratchpad as the record of what was rejected.

**Register — the warm name is confined, not resolved.** "Fly" is permanently warmer than
D-003, and this decision manages that rather than pretending otherwise. It appears in the
README, the docs, and on its own page and its prose. It does **not** appear in an
institutional proposal PDF, where the phrase is "our survey platform". It is **never set as
display type** — a body or mono scale word, because "Fly" at Zilla Slab 300/70px is a
consumer app. On first mention it always carries its job in the same breath. And **§6 Banned
gains one line**, because the risk a warm name carries is that somebody eventually draws it:
*no literal rendering of a product name — no insect, no wing, no paper plane, no envelope.
Fly is drawn as M5 or it is not drawn.*

#### Where the three workstreams disagreed, and how it was decided

Recorded because averaging them would have hidden two real arguments.

1. **Standing — they contradict outright.** `ws-fly-brand.md` §7 places Fly *inside* the
   credibility engine; `ws-fly-ia.md` §11 places it on the service side. **The IA memo is
   right**, and its argument is testable where the brand memo's is assertion: openness is
   load-bearing for the optimiser and nearly worthless for a questionnaire runtime, and the
   conversion action makes the position falsifiable. The brand memo's line was written to
   show its option does not reopen D-002 — a conclusion both memos share — rather than to
   analyse which side of it Fly sits on.
2. **Placement — incompatible as written.** The brand memo's Option C specifies *"nav:
   nothing; Fly named once, in a heading on the Platform page"*. **The IA memo is right**,
   because the brand memo **assumed** the Platform placement rather than arguing it, and
   never tests it against Platform's job sentence or copy rule 1 — which the IA memo does at
   length.
3. **The combination is stronger than either memo priced it, and neither costed it.** The
   brand memo's own strongest objection to its recommendation is that it *"caps Fly — a name
   that appears once on a Platform page will never be adopted by outside researchers."* **On
   a page of its own that cap is much looser**, so this decision buys most of what the
   rejected "name both engines" option was for, and still costs **no second proper noun**.
4. **The IA memo's one open branch is closed.** It says fall back to a Method section *"if
   the capability inventory comes back thin — five or six items, none of them distinctive."*
   It came back at **twenty verified rows**. The branch does not trigger.

#### Rejected, and what it would take to reopen

- **Name both engines** (`adopt` + Fly, typeset not logotyped) — the serious alternative, and
  it costs one word. Rejected because **the two are not peers**: `docs/vlab/study-configuration/data_sources.md`
  lists *"Fly, Qualtrics, and Typeform"* as interchangeable destinations the optimiser drives,
  Fly's services are namespaced `fly-*` while the recruitment side holds the bare namespace,
  and a symmetric architecture would assert a relationship the software does not have.
  Reopen if outside adoption of Fly becomes a strategy rather than a possibility; `adopt` is
  the candidate, because it is already true.
- **Fly standalone** — own mark, domain, docs, favicon set, GitHub org. **Reopens D-002**: a
  product with a mark and a domain is a product being sold, and the first *"can we license
  Fly?"* email arrives within a month. It also faces two problems that need counsel rather
  than design — **Fly.io** occupies the name in developer infrastructure, and `fly/LICENSE`
  names **The World Bank Group** and **Curious Learning: A Global Literacy Project Inc.**
  alongside "fly contributors". And it would move `github.com/vlab-research`, invalidating
  C-052. **Not reversible once taken**, which is why it is not.
- **Fly kept internal** — the status quo, which was never neutral: `docs.vlab.digital`'s nav
  says "Fly" and the site never would, so our own link hands a technical buyer a name we do
  not use.

#### What this changes elsewhere

| | |
|---|---|
| **D-007** | ~~Page inventory gains one line.~~ **Withdrawn 2026-08-22** — D-007 is open and there is no page inventory. Per-study detail pages stay deferred on their own merits |
| **D-001** | Gains a paragraph: feasibility is answered before proof. **Audience ordering unchanged** |
| **D-002** | Gains one sentence: "the platform" in it means the recruitment optimiser |
| **D-015** | Re-scoped, not reopened: its single screenshot was specified before this page existed |
| `DESIGN.md` §6 | M5 gains one line — this motif is the visual identity of Fly. Banned gains the literal-rendering ban. **§3, §5, §7 unchanged** |
| `CLAIMS.md` | **C-056–C-077** merge from `notes/ws-fly-capabilities.md`. C-052's scope re-checked, since "the platform" now means two things to a reader |
| `CONTENT.md` | The new page spec; Home §3 step 3 rewritten |
| `docs.vlab.digital` | Retitle the second top-level section **"Virtual Lab" → "Recruitment"**, which removes the collision where "Virtual Lab" is both parent and one of two children — one line of front matter, no new noun in the world. Drop the indigo `#4F46E5` node-network logo, which §6 bans anyway. **D-008** |
| `fly` repo | README H1 gains the endorsement line; `dashboard-client/public/index.html` stops setting `<title>Virtual Lab</title>` |
| Proposals | No change. `adopt` never surfaces; a proposal says "our survey platform" |

#### Two gates sit between this decision and a built page

Both are real and neither is optional.

1. **The capability rows land in `CLAIMS.md` first.** *The page's sections are its claims* —
   roughly twenty rows on the C-050–C-053 pattern: non-numeric, `VERIFIED`, sourced to the
   repository. A capability asserted without a row is the same failure as an invented number,
   only harder to spot because it carries no digits.
2. **The privacy policy is read against that inventory before the video and incentive
   sections publish. Done 2026-08-21** — `notes/ws-privacy-reconciliation.md`. Ten of the
   sixteen publishable rows are comfortably inside the policy; three are not, and all three
   are already true today. **What remains is a decision, not a review: D-025**, whether the
   policy may be amended at all, given `CONTENT.md`'s "structural edits only" rule.
   **Sections 1, 2, 4, 6, 7 and 8 of the page are unaffected either way.**

**Four of the eight capabilities described when this entry was opened came back wrong**, and
the corrections are in `CLAIMS.md`: image collection does not exist, "full multilingual
support" overstates it, watch-tracking is verified on Messenger only, and DingConnect is
enabled in no environment. Both comparative claims are `WITHHELD` — no measurement exists.
**Do not restore any of them from the opening paragraph of this entry or from memory.**

**Not a Phase 4 blocker, and it never was** — D-014 remains the only decision blocking the
build. It was opened before the build rather than after because placement is a sitemap
question, and a sitemap question answered after the pages exist is answered by rework. That
instinct was right and the execution was not: the placement half was answered by assumption
rather than by argument, and it was withdrawn on 2026-08-22.

---

---

### D-007 — The sitemap, derived from the narrative
**Status:** Settled · 2026-08-22 · *settled 2026-08-20 as seven pages, amended to eight and
nine, reopened entirely on 2026-08-22, and closed the same day by derivation from D-027*

**This entry no longer argues a page count. It records what D-027's narrative produces.**
The order of operations that produced it is the substance of the decision: **material, then
narrative, then sitemap, then specs** — the reverse of how the first three days ran.

| Surface | What it carries | Why it is a surface |
|---|---|---|
| **The spine** | Parts 1–3 of D-027: the opening, *what is different*, and the walk | **Beats one to ten are a single continuous read.** Breaking them is what would turn the narrative back into an assembly |
| **What else you can build** | Part 4 — the design patterns | *See the open sub-question below* |
| **The paper** | Citation, verbatim abstract, BibTeX, link | D-016 settled its contents |
| **What we have run** | Study cards; coverage detail beyond the opening's map | Reached for, not walked through |
| **The audit trail** | Open source, self-hosting, EU infrastructure, export | Reached for by a procurement or IT reviewer |
| **The brief form** | Collect a brief good enough to price | The conversion action |
| **Privacy** | Legal reference | Carried over near-verbatim |

**Six surfaces plus privacy, against the nine that were on the table that morning.**

**One sub-question stays open and it is small.** *What else you can build* is either the tail
of the spine or the first surface after it. **Decide it while building, on how the spine
reads at length** — it is one line of a template either way, and it is exactly the kind of
question that should be answered by looking at the thing rather than by arguing about it.

**Two things this does not change.**

- **Per-study detail surfaces stay deferred**, on their own terms and not as a placement
  clause: a study earns one when its figures are `VERIFIED` **and** cleared against that
  engagement's confidentiality terms. Field time is required.
- **The tests this question produced still apply** to anything added later — *a page of blanks
  is worse than no page*; one job and one conversion per surface; content stating no figure is
  not caught by the blanks test.

#### The process rule this produced, which outlives the answer

> **A sitemap change is never a side effect of a content decision.** If a decision about what
> to say also decides where it goes, the second half is not decided — it is assumed. Placement
> gets its own entry, taken after a narrative exists.

D-024 is the case that produced it: it bundled naming, placement and standing, and the naming
half was argued while the placement half rode along. That entry was split, the sitemap was
reopened to nothing, and this is what replaced it.

**Every placement clause elsewhere in this file is now resolved against the table above**,
rather than against the seven-page structure they were written for. Where a settled decision
says *on Home*, read *in the opening*; where it says *on the Platform page*, read *the audit
trail*.

---

### D-027 — The narrative spine
**Status:** Settled · 2026-08-22 · **this is the entry the sitemap is derived from, and the
one to read before writing any copy**

**Nandan:** *"I think this is a very strong narrative. Let's record this and consider this
phase finished."*

**Four parts, each answering the question the part before it raises.** That sequence is the
decision. It is not an ordering of our material — it is an ordering of a reader's questions,
and **the moment a part stops answering the question before it, the site has gone back to
being an inventory.**

| Part | The question it answers |
|---|---|
| **1 · Opening** — the claim, and the volume behind it | *Who are you, and have you actually done this?* |
| **2 · What is different about an ad-recruited sample** | *Isn't that just a convenience sample?* |
| **3 · The walk** — one study, start to finish | *So how does it actually work?* |
| **4 · What else you can build** | *That's one study — what about mine?* |
| *Reference* | *Show me.* |

#### The beats

**1 · Opening.** The hero — *population-representative samples, recruited through ad
platforms* — then the totals band, then the coverage map and region strip. **The map moves up
into the opening**: a count of countries invites it immediately, and volume and reach belong
in the same breath. Nandan's framing: *we're recruiting samples from ad platforms, and we've
done it a bunch.*

**2 · What is different.** **Two beats, not five.** *The problem with ad-recruited samples* —
you can only target on variables the platform exposes, and you cannot hold a stratification
in balance while the campaign runs. Then the ink band: *every recruitment method deviates
from the truth; ours is measured.* The objection lands where an informed reader raises it,
which is immediately after the coverage map.

**3 · The walk.** Second person throughout. You describe the population → budget moves
between strata until the achieved sample matches the target → they answer in a conversation →
months later the same thread reopens → you get the data. **Every capability appears at the
moment it is used, and nothing is introduced as a category.**

**4 · What else you can build.** The design patterns. Two, not three — see the seam rules.

**Reference.** The paper · what we have run · the audit trail · the brief form. **Not steps a
reader walks through; things they reach for.**

#### Amended 2026-08-25 — the homepage is parts 1 and 2 only

**Three changes, all Nandan's, all in one session, and they compound:**

1. **The walk comes off the homepage.** *"I think part 3 should disappear for now. Let's just
   focus on getting part two right. Then we're done with homepage."* The material and its
   approved five-beat rewrite are held in `COPY.md` under Part 3; nothing is deleted.
2. **Part 2 is no longer "what is different about an ad-recruited sample."** It is *why don't
   I just do this myself* — a **logistical and operational** problem, not a statistical one.
   The old beat named two real problems and never said why either was fatal, so a competent
   reader answered *"then weight it"* and moved on.
3. **The measurement beat is gone and 6.1 p.p. leaves the site's own voice**, surviving only
   inside the quoted abstract on the paper surface. Reasoning in `CLAIMS.md` under C-003.

**What survives intact, and it is most of the entry.** The opening is unchanged in substance
and improved in order — hero, totals, coverage, then the two distributions, the last of these
being new. **Seam rule 1 still holds** and now does more work than before: Part 2 argues that
software has to exist without explaining what the software does. Seam rules 2 and 3 are
dormant while the walk is off the page and apply again the moment it returns.

**What this costs, stated plainly.** The homepage's H1 claims *population-representative
samples* and the page no longer substantiates it — the evidence is a click away, in the
paper. That is defensible, and it is how the claim is made in research generally, but it is
a real change to a site whose proposition is that its numbers are checkable. **Recorded as
open in `COPY.md` §2.2 rather than resolved.**

**The order of operations rule from D-007 was followed:** this is a content decision that
also moved structure, so the structural half is written down here rather than assumed.

#### The three seam rules, and they are the whole of the risk

1. **Part 2 states the problem and the measurement, and never the mechanism.** The mechanism
   belongs to the walk, where it is shown rather than asserted. If the ink-band section starts
   explaining the optimizer, the reader hears the same thing twice in two registers and the
   walk loses its job.
2. **The walk never forks.** It tolerates exactly one story. The first time a beat acquires
   *"or, alternatively…"*, that variation belongs in part 4 — which exists precisely so the
   walk never has to branch.
3. **The panel is a beat, so it is not a pattern.** Walk beat four *is* the longitudinal
   design, which means it cannot also be one of the design patterns. This removes the overlap
   between the instrument material and the designs material that three earlier passes kept
   rediscovering.

#### What this cut, and why the result is shorter than its parts

**Technology as a category is gone.** The walk shows the software in use, so a part named
after it would describe what the reader has just watched. That single cut is what makes the
combination shorter than either narrative it came from, and it is what finally dissolves the
Platform-versus-instrument seam that D-024 spent a day on.

**Three of the five method beats are gone.** Stratifying on untargetable variables survives as
one clause inside walk beat two. Weighting and the cost comparison go to the paper.

**Almost nothing new has to be written.** One beat is new — the hand-off at the end of the
walk, which has to return to the deviation figure without restating it. Everything else is
copy that already exists and has already been through review.

#### How this was arrived at, because the process is the point

Four narratives were sketched and compared: *the sample is defensible* (the implicit one,
which is what left the survey platform invisible), *method-technology-designs*,
*what you can run now*, and *one study end to end*. Nandan chose the second and fourth and
asked whether they could be combined given their specific strengths — the opening from one,
the walk from the other. **This entry is that combination.** Working artifacts:

- Four options: `https://claude.ai/code/artifact/59d546c0-bcd8-4794-9076-233f25ef6352`
- B and D sketched: `https://claude.ai/code/artifact/c19dfa43-ad8c-4aa9-adeb-631aadddcc34`
- The combined spine: `https://claude.ai/code/artifact/6c3aa80c-39ff-49cd-8d19-8607a0c28a52`

**The rule that produced it, from D-007:** *a sitemap change is never a side effect of a
content decision.* This is the reverse — **the narrative first, and the sitemap derived from
where it breaks.** D-007 records that derivation.

---

### D-028 — The site ships light; dark is kept dormant, not deleted
**Status:** Settled · 2026-08-27 · *reverses the "three theme states" half of the old §3
theme rules; the rest of §3 is untouched*

**Nandan:** *"it shows up in dark mode in many browsers, I dont like that"* — and, on how far
to go: *"I don't wanna navigate some toggle, and let's just ship default light mode. We can
keep the dark mode dormant there to not rip the code out. Why not."*

**The site renders light for everyone.** The `@media (prefers-color-scheme: dark)` block is
gone from `css/site.css` and from the DESIGN.md §3 token block. Nothing on the site stamps
`data-theme`, so an unstamped root — every page served — resolves to the light palette.

**Rationale.** The design was drawn in light and the dark palette was built to match it. The
site now follows the drawing rather than the visitor's OS. That is the whole reason; there is
no claim here about what any visitor wants.

**Three consequences worth writing down.**

1. **`color-scheme: only light`, not plain `light`.** Deleting the media query alone would
   have made this *worse* on Android: Chrome's Auto Dark Theme auto-darkens pages that do not
   declare dark support, so the fix needs the declaration. `only` is what disables the UA
   adjustment — plain `light` does not.

2. **What still overrides us is not fought.** Dark Reader and its kin, and Windows
   forced-colors, re-tint the page regardless. Both are a user darkening their entire
   machine. No further work is warranted there, and attempts to defeat them break the
   accessibility case that forced-colors exists for.

3. **Dormant means kept, and kept checked.** The `:root[data-theme="dark"]` block stays in
   `css/site.css` and in DESIGN.md, and `scripts/check-contrast.py` still verifies both
   palettes. **A new colour therefore still needs its dark value chosen alongside its light
   one.** The cost of that discipline is small; the point of it is that restoring dark stays
   a one-block edit rather than a re-design. It also has one live consumer today —
   `scripts/build-review.py` stamps `data-theme` itself and keeps its own copy of the tokens,
   so its light/dark/system toggle is unaffected by any of this.

**Superseded rule.** `AGENTS.md` hard rule 7 read *"three theme states, not two."* It now
reads that the site ships light and dark is dormant. The surviving half of the old rule still
binds: **never declare a colour whose only definition sits inside a `[data-theme]` block** —
that block is now one nothing on the site matches at all.

**To reverse this,** restore the media query in `css/site.css` §3 and drop `only light`. Both
sites of the edit carry a comment pointing here.

---

### D-008 — `docs.vlab.digital` folds into this site, at `/docs/`
**Status:** Settled · 2026-08-29 · *opened as "shared nav, separate shell", and that is what
it settled as — the surprise was how much cheaper it turned out to be than the entry assumed*

**The documentation is now 47 Markdown pages in `docs/`, rendered by this repo's Eleventy
build, served at `vlab.digital/docs/`, sharing one head, one font kit, one stylesheet and
one footer with the marketing page.** Hugo is gone. The old repo stays as the history
archive; nothing is deleted from it.

| | Before | After |
|---|---|---|
| Generator | Hugo 0.147 + vendored geekdoc | Eleventy 3.1.6, the same one |
| Repo | `../docs.vlab.digital` | `docs/` here |
| Deploy | GitHub Pages via Actions | Netlify, the same build |
| URL | `docs.vlab.digital` | `vlab.digital/docs/`, with 301s |
| Shell | geekdoc's | `_includes/base.html`, shared |

**Why Eleventy rather than keeping Hugo — and the reason is not that Hugo is worse.** The
thing being shared is `_includes/base.html`, `css/site.css`, `_data/site.js` and `fonts/`.
Those are Eleventy artefacts. Sharing them under Hugo means writing the head, the mark, the
footer and the font loading a second time in Go templates and keeping the two in step by
hand — which is **D-006's own argument against a plain directory of HTML**, applied across
two engines instead of across two pages. The shell has to have one definition or it is not
shared, it is copied.

**The Hugo lock-in was four shortcodes.** `ref` ×116, `hint` ×27, `toc` ×14, `toc-tree` ×5,
and front matter of `title`/`weight`/`draft`/`date`/`author`. No mermaid, no tabs, no
columns, no raw HTML, no custom layouts — `layouts/` held a `.gitkeep`. That was the whole
surface, and it is why this cost a day rather than a month.

**`ref` was resolved to real URLs once, permanently, rather than reimplemented.** All 116.
The content no longer carries a templating idiom and now renders as ordinary Markdown
anywhere. That gives up the one thing `ref` did — failing the build on a broken link — so
**`scripts/check-links.py` replaces it, and covers more**: it validates every internal href,
every `<img src>`, and every `#fragment` against the ids on the page it points at, which
`ref` never checked at all.

**What docs do not inherit.** The nav's *Request a proposal* button. A reader looking up a
field name is not in the market for a proposal, and a conversion action over a reference
page is exactly the "software tool" pull D-002 exists to avoid. They get a way back to the
site instead. That is the "separate shell" half of the original recommendation, and it is
one `{% if docsSection %}` in `base.html`.

**Consequences elsewhere, each with its own entry:** D-029 (the two `DESIGN.md` rules that
cannot reach documentation) and D-030 (the first client-side JavaScript on the property).

**One deploy step is outstanding and this decision is not live without it:** add
`docs.vlab.digital` as a domain alias on the Netlify site and point its DNS there.
`_redirects` carries the host-scoped 301s and says so.

**Rejected: `git subtree` to preserve the docs repo's 60 commits.** That repo vendors an
11 MB Hugo theme across 232 tracked files, and the subtree would have carried all of it into
this repo's history permanently — roughly doubling a 9.9 MB `.git` to import the history of
a theme being deleted. D-010's "keep the history" is about not rewriting *ours*; it is not a
reason to import somebody else's. The old repo is the archive, and it costs nothing to keep.

---

### D-029 — The provenance rule and the raster ban do not reach the documentation
**Status:** Settled · 2026-08-29 · *the two `DESIGN.md` rules that D-008 collided with*

**Neither rule is narrowed. Both are scoped to what they were written about.**

**1. Hard rule 8 — "all graphics are inline SVG from the four primitives" — is carved out
for `docs/`.** The docs carry 39 screenshots and **a capture of the Fly UI is the
documentation**; there is no version of that made from a bar, a tick, a cell and a bracket.
The ban holds everywhere else on the property, and `.eleventyignore` still excludes `img/`.

Two things worth knowing. **The screenshots are of a UI that contradicts this design
system** — D-015 records that Fly's dashboard ships a Create-React-App favicon, Ant Design
`#1890ff` and `font-family: Avenir`. That is unavoidable in documentation and is a second
argument for eventually rebranding that dashboard. `css/docs.css` gives every capture a
hairline and a paper mat so it reads as a *specimen on* the page rather than as part of it.
**And nine of them do not exist** — six `bails-*` and three `fly-monitor-*`, missing on the
Hugo site too. `notes/ws-docs-screenshots.md` is the capture plan.

**2. `check-claims.py` skips `docs/` and `_site/docs/`.** The provenance rule governs
**claims** — a figure offered as evidence for what Virtual Lab can do. Reference
documentation asserts nothing: its numerals are JSON payloads, HTTP codes, timeout values,
field weights and API examples, and there is nothing for a reader to check because nothing
is being claimed. Pointing the checker at 47 such pages yields hundreds of findings, and
**a gate that reports hundreds of non-problems is the dead gate `scripts/fixtures/` already
taught this repo not to build.**

**The rule keeps its full force, and the test is unchanged:** *does the line say something
about the number, or only about us?* **If a docs page ever states an outcome figure** — a
response rate, a cost, a sample achieved — **it is a claim wherever it is printed**, it needs
a `VERIFIED` row, and it is scanned by naming the file, which `check-claims.py` has always
accepted as an argument.

**No colour was added.** The warning callout is `--brass`, which §3 already assigns the
semantic job; the note callout is neutral. Prism's theme uses the three existing hues doing
their three existing jobs — ink is chrome, teal is every literal **value**, brass is
keywords. `check-fourth-hue.py` was not needed and `check-contrast.py` grew from 22 measured
pairs to 38, all passing in both themes.

**One `DESIGN.md` addition was unavoidable and it is a scale, not a colour.** §4's display
sizes assume a page with three headings; `questions.md` has twenty-nine `h2`s, and 42px
Zilla Slab twenty-nine times is a poster rather than a document. Same four faces, same
weights, tighter steps. Recorded in §4 as the documentation scale.

---

### D-030 — The docs ship client-side JavaScript; nothing else does
**Status:** Settled · 2026-08-29 · Owner: Nandan · *decided against the recommendation, which
was to defer it*

**`/docs/` loads `docs.js`, a search box. It is the only JavaScript on the property.**

The recommendation was to ship the sidebar tree first and add search only if it was missed —
47 pages is navigable, and this is the first script on a site that had none. **Nandan chose
to build it in**, on the grounds that search is genuinely useful in reference material and
that removing a capability the Hugo site already had is a regression for the people using it.

**What that is allowed to mean, and these are the constraints, not a description:**

- **`/docs/` only.** `base.html` gates both the script and `css/docs.css` on `docsSection`,
  so the marketing pages' payload does not grow by one byte.
- **No library, no bundler, no CDN.** ~230 lines of vanilla JavaScript, copied to the output
  verbatim. D-006's "no asset pipeline" holds, and D-012's reasoning about self-hosting —
  we sell to EU institutions and our privacy policy states EU hosting — applies to a script
  origin exactly as it applies to a font origin.
- **One request, same-origin, on first focus.** `/docs/search-index.json` is 200 kB raw and
  63 kB gzipped, and **it is not fetched on page load**. A reader who never searches never
  pays for it.
- **No cookie, no storage, no beacon, nothing reported anywhere.** **D-009 (analytics) stays
  open and this does not touch it.** Search runs entirely in the reader's browser; we cannot
  see what anyone searched for, and nothing here is a step toward being able to.
- **It degrades honestly.** The search box ships `hidden` and the script unhides it, because
  an input that accepts text and does nothing is worse than no input.

**The index is generated from the rendered pages** (`docs-search-index.njk`), not from the
Markdown, so it cannot describe a page the site does not serve and its deep links use the
ids `markdown-it-anchor` actually emitted.

**If a second script is ever proposed for this property, this entry is the precedent and the
limit — not the opening of a door.** Anything that observes the reader rather than serving
them is D-009's question, and D-009 is open.

---

---

## Open

Nobody may resolve these except the user. Recommendations are recorded so the
conversation starts from a position, not from zero.

### D-025 — May the privacy policy be amended, and how far?
**Status:** OPEN · Owner: Nandan · **opened 2026-08-21** · *gates two sections of the
Instrument page, and nothing else on the site*

**`CONTENT.md` says the privacy policy is carried over near-verbatim and that "the only
permitted edits are structural."** That rule was written to stop a marketing hand rewriting
legal copy, and it is a good rule. It also means **nobody but Nandan can close the gap the
capability register just exposed.**

**The review has been run**, clause by clause, against every publishable row:
`notes/ws-privacy-reconciliation.md`. **Ten of the sixteen rows are comfortably inside the
policy as written.** Three are not, and **all three are already true today** — publishing a
page about the instrument does not create them, it makes them discoverable by a procurement
reviewer, who is audience 1.

1. **Video engagement and link clicks.** §2.2's fourth category is *"message metadata such as
   timestamps, message direction, delivery status, and chatbot state"* — every item a
   property of the message **we sent**. A play/pause/seek trail with a heartbeat is a record
   of what the **participant did with the content**, which is the whole point of C-064: the
   instrument produces a *second class of measurement*, behavioural, beside the self-report.
   Calling that "metadata" describes something narrower than the page beside it.
2. **Incentive disbursement, and this is the one to fix first.** Paying a respondent needs a
   destination — a phone number for an airtime top-up, an email for a gift card. **§2.2 does
   not describe a disbursement** (it contemplates a phone number only for SMS), **§3 names no
   such purpose**, and **§5 lists no such recipient**: its four categories are the researcher,
   infrastructure providers, platforms the researcher connected, and legal requests, and a
   top-up provider is none of them.
3. **The transcript is slightly broader than "survey responses"** (C-072) — it includes what a
   participant typed that was not an answer, which is exactly where an unanticipated special
   category arrives.

**Recommendation: yes, amend, and narrowly.** One clause in §2.2 for engagement events; three
short additions for disbursement (a §2.2 category, a §3 purpose, a §5 recipient); one
broadened phrase for volunteered messages. **No legal base changes** — §4 already rests on
consent for participant data — and the policy gets *more* accurate about what we already do,
which is the same argument the rest of this site is built on. The rule in `CONTENT.md` should
be read as *no marketing edits*, not *no corrections*; a policy that under-describes real
processing is not protected by being left alone.

**One sub-question that is genuinely open even if the answer above is yes: are the
disbursement providers named in §5?** Naming them is more transparent, more on-register, and
what a procurement reviewer expects of a subprocessor list. It also publishes a supply-chain
fact and pins us publicly to vendors we may change. **The Instrument page names no provider
either way** — that is already in its spec — so this decides the policy only.

**If the answer is no**, nothing stalls: sections 3 and 5 of the Instrument page are written
down to what the policy already covers, and sections 1, 2, 4, 6, 7 and 8 are unaffected. The
cost is the watch-trail — the more interesting capability, and the one a PI designing a
media-exposure study is actually shopping for.

**Not a Phase 4 blocker.** D-014 remains the only decision blocking the build, and the
Instrument page can be built with two sections written conservatively and revised later.

**One thing found by the same review is out of scope here and is flagged rather than
folded in.** §5 of `notes/ws-privacy-reconciliation.md` records a contradiction between the
policy's *"we do not knowingly process … government identifiers"* and a project scope of work
that has us collecting and transmitting parent photo IDs. **It is not a website question and
no page should mention it**; it needs Nandan and plausibly counsel. It is named here only so
that closing D-025 does not read as having closed it.

---

### D-021 — Two motif rules the coverage work exposed
**Status:** OPEN · Owner: Nandan · *low stakes, but they should be written down*

Building the coverage graphics surfaced two places where `DESIGN.md` §6 relies on
judgment where it could state a rule. Neither is urgent; both get cheaper to fix now
than after a second designer has guessed.

1. **Should M2 require a real target?** §6 already says M3 "appears only where a real
   interval exists — decorative use would be a lie." The same argument applies to the bar
   and target tick: on a graphic with no target, the tick is decoration. **Recommend:
   yes, extend the rule to M2.**

   **Evidence, 2026-08-20 — a worked example for, and a scope limit against.** The
   rebuilt region strip is a bar with **no** target tick, because "respondents by region"
   has no target to compare an achieved fill against, and it looks right without one.
   That is the practical case for the rule. But the *Optimize* icon (§7) is specified as
   three bars plus a target tick, and an icon has no data, so the rule as written would
   ban the icon §7 asks for. **Recommend the rule be scoped to figures, not icons** — an
   icon is a glyph of a mechanism, not a reading of one.
2. **Does the lattice hold at other scales?** §6 fixes cell 8 / pitch 18. The coverage
   work used 5.6 / 12.6, preserving the 4:9 ratio. "The same lattice at every scale"
   appears to permit this. **Recommend: say so explicitly — the ratio is fixed, the
   pitch is not.**

   **Evidence, 2026-08-20 — the recommendation is right for fields and wrong for the
   mark.** Two things landed on this. The 5.6 / 12.6 pitch came from a scratch session's
   ink-band treatment that **did not survive into the settled coverage section**, which
   uses no lattice at all — so nothing in the current build depends on the answer. And
   drawing the nav mark showed the ratio is not universal: §6 fixes 4:9, §8 sets the mark
   at 22px with nine cells, and those are not jointly satisfiable at a legible size. Nine
   cells at 4:9 in 22px gives cell 4 / pitch 9 — a scatter of 4px dots that reads as faint
   texture beside the wordmark and disappears at 16px. The mark ships at **cell 6 / pitch
   8** (3:4), which also lands exactly on 22 and holds down to 12px. Five variants were
   rendered side by side at 16 / 22 / 44px before choosing.

   **The distinction worth writing into §6 if this is taken:** 4:9 is a **tiling** ratio.
   It governs the lattice as a *field*, where the cells must disappear at a glance. The
   mark is not a field — it is nine discrete cells that must survive at 16px — and it
   needs its own ratio. §6 is unchanged pending this decision; the mark is currently
   built to a ratio §6 does not sanction, which is the drift this entry exists to close.

The third question from that review — where the line sits between a sanctioned coverage
map and a banned globe — is **resolved in D-018** and written into §6.

---

### D-022 — Should the region strip show the unattributed respondents?
**Status:** SETTLED · 2026-08-26 · **No. Leave it. Do not reopen.**

**Nandan:** *"This is ridiculous. Don't worry about that at all. Nobody is gonna count up
the numbers. It really doesn't matter. It's okay that they don't add up. Forget it."*

The strip spans the **738,608** respondents attributable to a country; the other **103,052**
belong to studies whose strata carry no country tag. No ghost segment, no caption, no note.
**The two figures do not reconcile on the page and that is accepted.**

**The old recommendation carried a trigger and it has been overtaken.** It read *"revisit if
the strip ever appears without its source line"* — and the source line was removed on
2026-08-26, so by its own terms this was due for another look. It got one, and the answer
was no. **The trigger is now void; do not let it fire again.**

**Why this is right and not merely a shortcut.** Nobody sums a stacked bar against a figure
three sections above it. The ghost segment would have put an eighth of the strip into a
category a buyer cannot act on, and invited the reading that we lost track of those
respondents rather than that they were recruited without country strata — a worse impression
than the one it fixes.

**The denominators are still in `CLAIMS.md`** — C-097 and C-098 — for anyone who ever needs
them. **The provenance rule is not weakened by this.** Every figure on the page still traces
to a `VERIFIED` row; what is declined is an on-page reconciliation *between two of our own
figures*, which was never what that rule was for.

---

### D-009 — Analytics and consent
**Status:** OPEN · Owner: Nandan

PostHog loads on every page of the current site with no consent mechanism. This sits
awkwardly beside our own privacy policy and beside D-012's reasoning.

**Options:** drop analytics entirely; keep PostHog with a consent banner; or move to a
cookieless, EU-hosted analytics product that needs no banner.

**Recommendation:** cookieless and EU-hosted. A consent banner on a site whose pitch is
methodological rigour and data ethics costs more than the data is worth.

**State as of the build, 2026-08-25: the site ships no analytics at all.** The PostHog
snippet went with the legacy SPA and nothing replaced it. **This does not close the
decision** — it is the reversible direction while the decision is open. Loading nothing
costs a few weeks of traffic data; loading a US-hosted tracker with no consent mechanism on
the same origin as a privacy policy that states EU hosting is the thing D-012 spent a court
ruling arguing against. `_includes/base.html` carries a comment saying so at the point where
a snippet would go, so the absence reads as a decision rather than an oversight.

---

### D-010 — Repo history
**Status:** OPEN · Owner: Nandan

**Corrected 2026-08-20 — the original premise was wrong.** The 244 MB is the *working
directory*, not the repository. `media/` — 226 MB of raw field photographs — is
**untracked and has never been committed**. `.git` is 9.9 MB in total. The only weight
in history is `img/` at 8.5 MB, of which `img/raw/` is 7.0 MB; the largest committed
blob is `img/raw/mnm-phone.jpg` at 2.8 MB.

**Options:** keep the history as it stands; or rewrite it to strip `img/raw/`.

**Recommendation, revised:** keep the history. There is nothing worth stripping — 9.9 MB
is an ordinary repo, and the fresh-start option was solving a problem that does not
exist. `media/` needs no git operation at all, only somewhere to live: being untracked,
it is currently backed up by nothing. Drop `img/raw/` from the working tree if the
rebuild does not use it; its blobs stay in history at ~7 MB, which is not worth a
rewrite.

**Unchanged, and the reason this stays open:** the photographs may be irreplaceable
field documentation. **Archive before deleting anything.**

---

### D-014 — Which client marks are cleared for logo use?
**Status:** OPEN · **blocks Phase 4** · Owner: Nandan

**Live again, 2026-08-25, and now it blocks the client wall rather than the build.** It had
been declared moot the same day, on the reasoning that a type-only wall renders no logo and
so needs no clearance. **That reasoning was correct and its premise is gone:** Nandan asked
for real logos — *"What we need is the logos themselves… Use real logos."*

**What is needed, per institution:** the mark itself in a usable vector form, and whatever
permission its owner requires. The World Bank, and every university on the list, publishes
brand guidelines that restrict third-party use; several require written approval for use that
implies a relationship, which is exactly what a wall on a commercial site does.

**The recommendation from the original entry still holds and is now the mechanism, not a
fallback:** build the wall so it degrades. A cleared mark renders as a mark; an uncleared or
unsupplied one renders as type in the same cell. **The page ships either way**, and marks drop
in as they clear.

**Note the interaction with C-094 to C-096.** Three of the five universities have no source at
all. **A logo asserts a relationship more strongly than a name in type does**, so the
evidentiary bar goes up rather than down for exactly the institutions we can least support.

World Bank, UNICEF, Gavi and EFSA typically require written permission to display
their marks, and some contracts forbid it outright. Columbia, GWU, Truth Initiative
and Shujaaz are lower risk but unconfirmed.

**Recommendation:** build the client wall to degrade — cleared marks render as logos,
uncleared ones stay as type in the same grid — so the decision can land after the
build rather than blocking it.

---

#### Sourcing run, 2026-08-25 — the files exist; the permissions do not

**Eight authentic SVGs are in `assets/logos/`.** Nothing traced, redrawn or generated; where a
conversion was needed it was a mechanical EPS→SVG of the institution's own vector file.

| Mark | File | Source |
|---|---|---|
| World Bank ("THE WORLD BANK") | `world-bank.svg` | Wikimedia Commons. **The Bank's own URL now serves the Group mark instead** |
| World Bank Group | `world-bank-group-official.svg` | worldbank.org, current official |
| Columbia | `columbia.svg` | visualidentity.columbia.edu, public theme asset |
| George Washington | `gwu.svg` | GW's own public logo pack, EPS→SVG |
| Harvard (horizontal) | `harvard.svg` | Wikimedia Commons |
| Harvard (stacked) | `harvard-stacked-official.svg` | harvard.edu. **Reverse/knockout — wordmark is white, invisible on paper ground** |
| Washington | `uw.svg` | washington.edu brand site, EPS→SVG. **UW publishes no SVG** |
| WashU | `washu.svg` | washu.edu homepage, current 2024 mark |

**Every one of the six requires permission of some kind for third-party use. Not one page
carries language permitting an unaffiliated organisation to display the mark.** The recurring
trigger across World Bank, Harvard and WashU is *implying endorsement or affiliation* — and a
wall of institutional marks on a commercial site is, by construction, a claim of relationship.

- **World Bank:** *"You may not use any such trademark… without the prior written consent of
  the relevant member institution(s)"*, and may not use them to *"represent or imply an
  association or affiliation."*
- **Columbia:** *"Personal use of University trademarks is prohibited. University trademarks
  should only be used for official University business."* The parent brand mark — which
  `columbia.svg` is — sits behind a special-permission request to Columbia Creative.
- **George Washington:** *"non-GW entities may only use the GW logos with permission granted
  by a sponsoring department and the Office of Communications and Marketing."*
- **Harvard:** outside entities need *"the prior written approval of the Provost"* for the
  University-level name or the Veritas shield where use may reasonably imply endorsement or
  sponsorship. A **®/™ designation is required** and the saved files do not carry one.
- **Washington:** approval required from Trademarks and Licensing. **Their published rules
  address merchandise, not third-party web display** — that gap is recorded rather than read
  across.
- **Washington University in St. Louis** — *the most directly on point, because its policy
  describes this exact use case:* marks *"should not appear on commercial websites"*, and the
  route it does allow for a customer list is **text only, in writing, and not "partner"**:
  *"must use, in text only, the complete, correct name… use the name only in a clearly marked
  list of customers… Permission is valid only if granted in writing from MarComm."*

**Public domain is not permission.** Both Commons files carry `{{Trademarked}}` beside their
PD tags. The PD tag resolves **copyright**; trademark is the operative right for a logo wall
and Commons grants nothing there.

**A design conflict that survives even with permission, and it is ours.** §8 sets the wall in
**monochrome `currentColor`, no colour**. UW's rules state *"Logos may not appear in any
colors other than University color palette,"* and most of the others prohibit recolouring
too. **So the monochrome treatment is itself something that would have to be approved** — or
§8 gives way and the wall renders six full-colour marks, which is a different-looking
component than the one specified.

**Two sourcing caveats, recorded because they affect how much weight the above carries.**
Harvard's policy text was read through Internet Archive captures — `trademark.harvard.edu`
returns 403 to automated clients — and no live re-read was possible. And UW's terms for web
display were not found at all.

**What this does not decide.** Whether to display any of these is Nandan's call as the owner,
and it is a commercial-risk judgment rather than a documentation one; **this entry records
what the sources say, not what to do.** It may be worth counsel. **The page does not wait on
it:** the wall degrades to type, all six names are `VERIFIED` (C-020, C-024, C-025, C-094 to
C-096), and marks drop in individually as any of them clear.

### D-015 — Dashboard screenshots
**Status:** OPEN · Owner: Nandan

The current site leans on dashboard screenshots. They are credible, but they date fast
and pull the page toward "software tool" when we are selling a managed service (D-002).

**Recommendation:** one screenshot, on the Platform page, never on the homepage.

**Re-scoped 2026-08-21 by D-024 — still open, and the recommendation now has a second
candidate location.** The recommendation above was written when Platform was the only page
a screenshot could belong to. There is now an ‹Instrument› page, and the strongest image on
it is not a dashboard at all: it is **a thread**. So the question is really three:

- **Whether "one screenshot" survives** as a total, or becomes one per page.
- **If it stays at one, which page gets it.** A dashboard argues *there is no black box*
  (Platform). A thread argues *this is what a respondent sees* (‹Instrument›). They are
  different arguments to different readers.
- **Whether a thread capture is a "screenshot" for this decision's purposes at all.** It
  dates far more slowly than a dashboard — a Messenger conversation looks like a Messenger
  conversation — and it does not pull toward "software tool", which is the specific harm
  this entry was opened about.

**One constraint, from `DESIGN.md` §6, applies to any capture on the instrument page and is
not negotiable:** never with faces, avatars, or illustrated people. And note that Fly's
dashboard is **unbranded and mis-branded at once** — Create-React-App favicon and manifest,
Ant Design `#1890ff`, `font-family: 'Avenir'`, `<title>Virtual Lab</title>` — so a dashboard
capture today shows **none** of this design system. That is a cost of the dashboard option
and an argument for the thread.

---

### D-017 — Does the jobs posting return?
**Status:** OPEN · Owner: Nandan

A Senior Software Engineer posting is on the current site. It signals scale and
momentum — or staleness, the moment someone emails about a role that is not open.

**Recommendation:** drop it unless actively hiring — but note this is **not binary**, and
that `CONTENT.md` is already presupposing the outcome while the decision is open.

- **A footer line is the zero-maintenance middle.** "We hire occasionally:
  info@vlab.digital" signals a company that exists without asserting a vacancy that can
  go stale. No new page, nothing dated.
- **The asymmetry is worse here than the original note suggested.** A visitor who emails
  about a role that closed learns that our public statements are not maintained — and
  every number on this site asks to be trusted on precisely that promise. A stale job ad
  is cheap to leave up and expensive in our own currency.
- **A live posting needs an owner and a removal date, in writing.** Without both, do not
  take that option.
- **The sitemap had no room for it** when this was written, and now there is no sitemap at all (D-007, reopened 2026-08-22). The point stands in a different form: a careers surface has to earn its place in the narrative like anything else, and nothing about it is load-bearing for the argument.
