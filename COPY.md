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
| **The page** | Opening (hero · totals · **the client wall** · coverage · how fast a study fills · what the advertising costs) · what it takes (recipe · math · paper · instrument) · **the code is open source** · the close |
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

**Anchors, not pages.** `/#code` and `/#paper` give a procurement reviewer or an academic a
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

`data-claim`: C-010 · C-016 · C-017 · C-019.

Prose beside the band:

> Since February 2020.

C-018 (2020-02-13).

**No source lines here, and this row is why the rule changed.** Every cell used to carry
*"Virtual Lab production database, August 2026"* — the same sentence four times across one
band, plus a fifth under the prose. Nandan, 2026-08-26: *"Remove all the mentions of
Virtual Lab production database. That's ridiculous. Nobody puts that on a website. We are
the ones claiming the data. Nobody cares where it comes from."*

**The provenance rule is stronger for it.** `DESIGN.md` §2 now reads: a number resting on
somebody else's document carries that citation; a figure from our own operating record
carries nothing. Four cells repeating who we are was the provenance rule **performed
rather than applied**, and it devalued the one real citation on the page — *Donati & Rao,
2025*, under the math — by making provenance look like a house style.

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

> `H2` **We have recruited in 41 countries:**

**Changed 2026-08-26** from *"Where the respondents are"*, on Nandan's wording. **The
heading now carries a claim, which the previous one deliberately did not** — 41 is C-017,
so it takes `data-claim="C-017"`. No source line: first-party, per §2 as amended.

The note this replaces argued that a heading stacked on artefacts that already speak is
"a heading looking for something to do." That was right about a heading with no claim in
it. This one states the fact the map illustrates, and the map stops having to be read
before the reader knows what it is about.

**Note the tension, and it is decided rather than overlooked:** the heading says 41 and
the map draws **37**, because the four covered-but-uncounted countries came off the same
day. C-017 is the true count of countries we have recruited in; the map shows the ones we
have counts for. Nandan ruled on exactly this trade when he cut the four.

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
> whose strata carry no country tag.

C-097. No source line — our own record, §2 as amended.

**The four uncounted countries are gone from the copy and from the map.** Nandan,
2026-08-26: *"Why are there still four countries not yet counted? If that's true, just
leave them off entirely. Those are small details nobody cares about."* MD, MK, PS and XK
used to draw as dashed outlines, with their own legend state and this sentence explaining
them — **three pieces of chrome for four countries whose only property is that a query has
not been run.** They now fall through to the same hairline as every other country we have
not surveyed.

**Not drawing a country is not calling it zero**, which is the rule `coverage.json` still
carries and still means. The data records them; the drawing does not.

**The denominator survives and is not the same kind of detail.** The map is drawn from
country figures, and those cover 738,608 of the headline 841,660 — a reader who assumed
otherwise would read every segment of the region strip as a larger share than it is.

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

### 1.4 How fast a study fills · What the advertising costs

**TWO SECTIONS, one figure each. Settled 2026-08-26, and it reverses the one-beat rule
below.** Nandan: *"'How fast a study fills, and what the advertising costs' — doesn't work
well as a title. Let's think about how to change that. Maybe they each need their own
title."* Three structures were put up; he chose two separate sections.

> `H2` **How fast a study fills**  —  [P-10]  —  *"A distribution across studies, not an
> average. The spread is the useful part."*
>
> `H2` **What the advertising costs**  —  [P-11]  —  no prose

**What changed underneath the original rule.** The one-beat instruction was given on
2026-08-25, when the plots sat **side by side at 557px** — they read as a pair because they
shared a line, and one heading over both was the only way to title them. Widened to the
full measure and stacked, each fills the page and the compound heading was one heading
doing two jobs.

**The pairing survives the split**, and it was never the heading that made it: same form,
same M3 interval on the same M4 tick rule, same box-and-whisker convention, adjacent on the
page. A reader who learns to read one has learned to read the other.

**The prose moved and went singular.** *"Both are distributions across studies, not
averages"* now reads *"A distribution across studies, not an average"* and sits under the
**first** figure only — it teaches the convention, and the convention carries. The second
figure gets none: its own first source line already says *advertising spend only, not the
incentive, not the survey platform, not our fee*, and a sentence beside it restating that
would be the page undoing in its own voice what the figure says.

**Superseded, kept for the reasoning.** Nandan, 2026-08-25: *"both of the box plots should
be in a similar beat… these box plots early on set a really nice tone of hey, this is what
we do and we've done it a lot."* That tone is still the job of these two sections; they are
still adjacent and still early.

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

### 1.5 The client wall — **sits directly under the totals band**

**Moved 2026-08-26.** Nandan: *"Let's move the brand row up to right after the big numbers
to begin with (850k respondents, 17M responses)."* It was the last beat of the opening,
after coverage and the two distributions.

**Under the band it does a different and better job.** The band says how much we have run;
the wall says who trusted us to run it. Scale and credential in one breath, before the page
asks anyone to read a map or a box plot — which is the opening's whole assignment, *who are
you and have you actually done this*, answered twice in the first screen and a half.

The section keeps its number here so the copy and the page still refer to one thing.

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

### Part 2 — rebuilt 2026-08-26 as one list plus two callbacks

**Nandan:** *"Let's start with the full list, then have some way to hark back to the list
with the sections that follow where we reference the numbers and the items in the list.
Maybe for each item in the list, we have a short name for it, and therefore, we can
reference it."* Four structures were mocked; he chose the recap list.

**This supersedes §2.1–§2.4 below**, which are kept for their reasoning and their traps.
Nothing in the material was cut: the instrument prose became the platform section and its
feature list.

#### The list — one section, six steps, each with a handle · **INK BAND**

**The list is the ink band, from 2026-08-26.** Nandan: *"I suspect the recipe should be dark
background, tbh."* §8 allows two bands per page and never adjacent, so this **moved** rather
than being added — the math came off the band in the same change. It is the better
arrangement in both directions: the list is the pivot of the page, the moment it stops
saying what we have done and starts saying what the work *is*, so it is the thing worth
marking; and the equations read calmer on paper than reversed out of ink, where two dense
math blocks and a lattice competed for the same space.

Adjacency: paper above, paper below, footer far below. On the band the step list swaps every
role to its inverted token — `--ink-3` measures 4.00:1 there and `--ink` disappears outright.

> `H2` **What it takes to recruit respondents on social media**
>
> | | | |
> |---|---|---|
> | 01 | STRATA | **One ad set per stratum**, each targeting a different slice of the population, based on the appropriate stratification variables. |
> | 02 | ALLOCATION | **Spend allocated among strata**, so every stratum fills toward the share you asked for rather than the share that happens to be cheap. |
> | 03 | PRICES | **The allocation itself revisited as prices move** — prices for each stratum need to be estimated individually, live, to know how to reallocate spend to buy the most precision in your final estimator. |
> | 04 | UNIQUENESS | **Verifying the identity of each respondent** — because otherwise everyone on the internet will answer your survey many times over. |
> | 05 | INCENTIVES | **Paying an incentive to each respondent**, in their own country and in a form they can actually use. |
> | 06 | FOLLOW-UP | **The same people found again months later** for an endline survey, where appropriate. |

**Rewritten by Nandan, 2026-08-26**, and step 04 is the one to read twice.

**Step 04 lifts C-069's scope note.** It had read *"Keeping the same person from answering
twice"*, deliberately neutral because the register said the row *"must never be written as a
fraud or duplicate-prevention claim"*. It now says **verifying the identity** and gives the
reason. That was raised before it was written and Nandan wrote it himself, which is the
decision; **`CLAIMS.md` carries the lift**, on the rule he set at C-066 — update the register
in the same breath.

**C-077 did not move, and this is the line to hold.** Any **measured or comparative** claim
about fraud, duplicates or identity verification **against another recruitment source** is
still `WITHHELD`, because no measurement exists and D-023 forbids the comparison
independently. The description is sanctioned; **a number or a rival attached to it is not.**

**The handles must earn their keep.** A handle is decoration unless the copy uses it
afterwards. The recap is the minimum use; the prose should use them as words too, which is
why the band now closes on *"The price per stratum is not known in advance"*.

**~~UNIQUENESS is deliberately neutral~~ — superseded 2026-08-26**, see step 04 above. The
handle is unchanged; what changed is the line beside it.

#### Cut by Nandan, 2026-08-26 — four things, recorded so they are not restored by accident

- **The throughput figure's prose**, *"A distribution across studies, not an average. The
  spread is the useful part."* Both figures now stand on their own source lines.
- **The math's source line**, *"Donati & Rao, 2025."* The paper is directly beneath it, so
  the line cited the same document twice in three lines. **`DESIGN.md` §8 is updated: if the
  math is ever separated from the paper again, the source line comes back.**
- **The separation clause**, *"The paper analyzes thirty-three studies. The company did not
  begin with it…"* — written two messages before it was cut, to answer *"we don't want people
  to think we wrote the paper to start a company."* **The concern it answered is not on the
  page any more.** The order still argues it implicitly — the totals band and *since February
  2020* come long before the paper — but nothing states it. Worth a second look.
- **"Ours is called Fly, and it is open source."** Replaced by *"We built a chatbot survey
  platform to facilitate online recruitment, surveying, and interventions."*
  **Fly is now named nowhere on the page.** D-024 settled that Fly *may* be named, not that
  it must, so this breaks no rule — but it was a decision worth making deliberately, and the
  only surviving occurrence is inside an SVG comment that ships to the browser and is visible
  to nobody.

#### 01–03 · the optimization problem, **and the paper** — paper ground

> `H2` **Those three are one optimization problem**
>
> `recap` 01 STRATA · 02 ALLOCATION · 03 PRICES

**Simplified 2026-08-26 to one equation and one constraint.**

> You are choosing how many respondents to recruit in each stratum. You want the smallest
> variance on your weighted estimate, and you are bounded by what you can spend.
>
> **[MATH-1]** argmin over n₁…n_H of Σ_h W_h²σ_h²/n_h, subject to Σ_h p_h n_h ≤ B
>
> Where **W_h** is the weight of stratum *h*, **σ_h** its outcome dispersion, **p_h** the
> price of one more respondent there, and **B** the budget.
>
> **The price per stratum is not known in advance.** It has to be learned while the campaign
> is running, from the campaign itself — and every new estimate changes the allocation, which
> changes what you learn next. That loop is why this is software and not a spreadsheet.

**Two things were cut, and the reasons differ.**

- **The sample bound**, Σ n_h ≤ N_d. Nandan: *"remove the bound for the number of people.
  Keep it just to a budget constraint as the only constraint."* It was true and it was noise
  — a reader who has grasped that budget is finite does not need a second inequality to see
  the problem is constrained, and it made the line wrap on a phone.
- **The closed form**, the second block giving n_h* explicitly. *"No need to present the
  closed form solution. Jump straight to saying that p_h is not known."* It was the
  mathematically satisfying part and the least useful: it answers a question nobody reading a
  company page is asking, and it **delayed the sentence the section exists to reach**.

**That sentence is now the section's destination, and it was rewritten to land harder.** It
read *"p_h is not known in advance"*; it now names the thing — **the price per stratum** —
and closes the loop rather than stopping at the estimate: *every new estimate changes the
allocation, which changes what you learn next.* That feedback is the argument for software,
and stating it is stronger than the algebra that was standing in front of it.

**Superseded, kept for the record:**

> *(cut)* **[MATH-2]** n_h* = (W_h σ_h / √p_h) ÷ (Σ_k W_k σ_k √p_k) × B
>
> *(cut)* Budget shifts toward strata that are higher-variance, and away from those that cost
> more per respondent.

Source line: *Donati & Rao, 2025.* Math carries `data-claim="none"`.

#### The paper is inside that section, flat — no seam at all

**Combined 2026-08-26, then flattened the same day.** Nandan: *"Let's combine the
optimization problem and the read the paper into one section"*, and then *"make it one
section with the paper itself. So it's all one thing."*

The first pass made it one `<section>` with an `H3` behind a hairline — which was still a
seam, just a quieter one. **The math IS the method and the paper IS the method published, so
there is nothing for a seam to divide.** What carries the reader across is one sentence,
*"The method is published, and the validation with it"*, and the only heading inside the
section is the paper's own title.

**`/#paper` sits on that title**, so an academic following the link lands on the citation
rather than on the equations.

#### And the paper is separate from the company

> The paper analyzes thirty-three studies. **The company did not begin with it:** Virtual
> Lab has been fielding studies since February 2020, and the paper validates a method that
> was already running. Our operating history is the band at the top of this page.

**Nandan, 2026-08-26:** *"we don't want people to think we wrote the paper to start a
company. They're two separate things, and that needs to be understood."*

**The misreading it guards against** is that a paper was published and then monetised —
which would make the site academic-flavoured marketing and discredit both halves. The true
order is the opposite, and C-018 carries it: studies were running in production for years
before the paper was written.

**Note what the clause does not claim.** Not independence of authorship — the byline
directly above reads *Nandan Rao · Virtual Lab*, so the company is in the paper and
pretending otherwise would be the very thing the clause exists to prevent. And **not peer
review**: the editions in `_data/paper.json` are an SSRN working paper and a JMR
*submission*, so "peer reviewed" is not ours to say.

**Two other things went the same day, for the same reason.**

- **The hero eyebrow.** It read *SURVEY SAMPLING VIA AD PLATFORMS* — the paper's subject and
  very nearly its title. *"That's the name in the paper. Not the company. The company does
  need some distance from the paper."* The H1 leads instead.
- **The hero's "Read the paper" button.** *"Maybe we shouldn't have the 'read the paper'
  CTA."* A CTA is a thing we want you to do, so putting the paper beside *Request a proposal*
  made it one of two offers, one of them somebody's academic work. **The SSRN link at the
  foot of the paper section stays** — that is not a CTA, it is where a citation goes.

#### 04–06 · the survey platform

> `H2` **Those three are a chatbot survey platform**
>
> `recap` 04 UNIQUENESS · 05 INCENTIVES · 06 FOLLOW-UP
>
> Ours is called Fly, and it is open source. The questionnaire runs as a conversation inside
> the messaging app the respondent already uses — Messenger or WhatsApp — one question at a
> time, in their own language.
>
> It asks, the respondent answers, and the thread stays open. Months later the same
> conversation reopens for an endline, with no one re-enrolling.

**[P-12] The thread** — `assets/figures/thread.svg`, M5 as a drawing, beside the prose.
Nandan asked for it: *"maybe it does need to be some sort of SVG diagram that sort of
describes a chat or shows a chat. Right? Chat bubbles or something like that with the
questions or the way the list pops up in WhatsApp or Messenger."* §6 M5 had reserved exactly
this use. It reads **MONTHS LATER**, not §6's *"+4 months"* — C-041 is a real four-month
follow-up and is `PLACEHOLDER`.

Then the **feature list**, eight cells in two columns: answers come from an account, not a
link · incentives inside the thread · pause and resume · actions recorded, not just answers ·
conditional logic · answer validation · randomized arms · photos from respondents.

**Revised 2026-08-26, on four notes from Nandan.**

- **Cut: "Reopening a closed window"** (C-060) — *"This one is redundant."* It was the caveat
  to *Pause and resume* and read as one. C-060 stays `VERIFIED` and is published nowhere.
- **Cut: the script list.** Answer validation named Arabic-Indic, Devanagari, Bengali and
  Thai numerals — *"No need to quote every script that we can accept numerals in. That's too
  specific."*
- **Added: linksniffer and moviehouse**, both by name. C-065 is the link sent as a button
  with the click recorded; C-064 is video in the thread with play, pause, seek and completion
  recorded. **C-064's scope note is load-bearing:** verified on Messenger with *no WhatsApp
  path found in source*, and the row says do not name a platform — say what the instrument
  does. Hence *"inside the thread"*, naming neither.
- **Added: photos from respondents.** C-066 had been `WITHHELD` in the strongest terms this
  register uses — *"never publish, in any form, until it is built"* — and **Nandan reversed
  it: _"Forget the ban… update the register."*** Done; `CLAIMS.md` carries the reversal, so
  the page and the register agree.

**Three more revisions the same day.**

- **Video and links merged into one cell.** *"Describe the video and the links not as two
  separate features, but as sort of one feature, which is 'track what the user does,
  including external links and video watching'."* They were two rows of the same idea — the
  instrument records **behaviour and not only answers** — and splitting them made each read
  as a minor integration rather than as the thing they jointly are.
- **Cut: "Every message kept"** — *"that feels like table stakes."* **Note the consequence,
  because it is bigger than one cell: data export now appears nowhere on the page.** The
  audit-trail rewrite had already dropped *"Your data leaves whenever you want"*, and the old
  §2.4 prose that said *"at the end you take a CSV or read a keyed API"* was replaced by this
  section. C-072 and C-074 are `VERIFIED` and published in no place at all. Table stakes are
  still a procurement question.
- **"One run per account" expanded — to the mechanism, not to the claim asked for.** Nandan:
  *"what we're saying is 'identity verification built in' — leverage the platforms identity
  verification to prevent fraud."* **The register anticipated this and answers it in C-077's
  own text: _"Publish the one-run-per-account row above, which is the mechanism."_**

**Why the stronger wording did not go in, and why this is unlike C-066.** Two rows block it.
C-069's scope note says it *"must never be written as a fraud or duplicate-prevention
claim"*; C-077 withholds fraud, duplicates and identity verification because **no measurement
exists** — traceable only to a sales call where the speaker calls it an assumption and offers
the figure as a guess, and **the signed scope of that same engagement sells manual photo-ID
review instead**, which points the other way.

C-066 was a real capability we simply were not advertising, and lifting it cost nothing but a
register update. This would be an **efficacy claim nobody has measured**, on the one site
whose whole proposition is that it does not overclaim. So the cell states what is true —
*a respondent answers inside the Messenger or WhatsApp account they already use, and a form
cannot be entered twice from the same account* — and lets the reader draw the inference,
which is §2 rule 2 working properly. **If the stronger wording is wanted it is Nandan's call,
as C-066 was — and it needs C-069 and C-077 changed in the same breath, not the page alone.**

**What the photo cell does not say, and this is the open edge.** The old C-066 row recorded a
mechanism: the file itself is never stored, and what is kept is a **platform reference that
expires**. So *"a respondent can send a photo"* and *"you receive the photos"* are different
claims, and only the first is on the page. **Confirm what a researcher actually receives at
the end of a study before writing the second anywhere** — a buyer who expects files and gets
expiring links has been misled by omission.

`data-claim`: C-056, C-057, C-068, C-069, C-061, C-062, C-059, C-071, C-060, C-079, C-081,
C-063, C-072, C-074, C-052. No figures, so no source line.

*Notes.*

**"More literally" was the instruction.** Nandan: *"we need to describe everything a little
more literally. Right now, it's a bit salesy and punchy, but really, you just wanna say steps
four to six. We have a chatbot survey platform that does these things, and then maybe have a
separate feature list for it."* The heading now says what the thing **is**; the list says what
it **does**; neither reaches for a benefit.

**The feature list is a reference block, not the spine.** D-027 killed a feature inventory as
the site's *structure*. This is eight sourced capabilities under a section that has already
said what the platform is for — which is a different object.

**Five traps travel with it and each has burned a draft:** no image collection (C-066, built
then pulled), no Instagram (C-058 — the docs site is wrong), no *"full multilingual support"*
(C-067 — closed-ended answers only), **nothing may imply a form builder** (C-082 — surveys are
authored in Typeform; Fly imports and runs them), and the **web form is a study-level
destination**, so never write that Fly runs one.

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

# The code is open source

**Rewritten 2026-08-26, replacing "There is no black box."** Nandan: *"I don't think most
of the information there is very interesting. Let's just make that a section on 'The code
is open source' — where we point people to the GitHub repository and we explain that we run
things for them in a secure hosted environment, hosted in the EU. Those are really the only
two points."*

Anchor moved from `/#audit` to `/#code`; `_redirects` points the old SPA's `/software` at it.

> `H2` **The code is open source**
>
> The whole platform is public on GitHub — the optimizer that moves the budget between
> strata, and the instrument that carries the questionnaire. It self-hosts on Kubernetes
> with Helm, and you are welcome to run it yourself.
>
> Most people would rather we ran it. Studies we operate run on our own infrastructure in
> the European Union, encrypted in transit and at rest.
>
> `.brass` github.com/vlab-research →

`data-claim`: none — no figures in the section, so no source line. The claims underneath it
are C-052, C-050 and C-051.

*Notes.*

**"Secure" is not written as an adjective.** It is written as what it is — *encrypted in
transit and at rest*, C-051 — because a vague security word is exactly the sentence §2's
voice test throws out: *could a reviewer ask us to substantiate this, and would we have the
citation?* One clause carries the point Nandan asked for and is fully sourced.

**The second paragraph is `DESIGN.md` §1 doing its job**, and it is what stops *"running
this yourself is hard"* from contradicting *"here is the source"*: **solving the operational
problems is what the software does; running the software is what we do.** Anyone may run it
themselves and the site says so plainly rather than hedging it.

**Dropped, and what happened to each:**

- **The CSV export and the keyed API** (C-074, C-072). **Nothing is lost** — §2.4 already
  says it better and in the reader's own terms: *"At the end you take a CSV or read a keyed
  API, with every message exchanged alongside the responses."*
- **Auth0** (C-053). A vendor name doing no work on a marketing page.
- **The IRB line** (C-054). See below; this is the one that costs something.

**Ethics is now absent from the site, and that is the one thing this rewrite costs.**
C-054 stays `VERIFIED` and is published nowhere. `DESIGN.md` §1's audience table lists
**ethics** among what an institutional buyer — the priority-1 audience — needs from a page,
alongside named clients, operating history, compliance and references. Four of those five
are still on the page; ethics is not.

**If it comes back, it comes back with its scope attached.** The approval covers **the US
validation study described in the paper and nothing else** — protocol AAAV1539, Columbia
IRB, cited to Donati & Rao's title footnote, which makes it a third-party claim that
**carries a citation** under §2 as amended. *"IRB-approved"* without that scope clause is
precisely the overclaim the register exists to prevent, and it is the trap C-054 has been
flagged for since it was written.

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
| **P-3** | Region strip | 1.3 | **Generated** — same script; region names added 2026-08-26. D-022 settled 2026-08-26: no ghost segment, and the figures need not reconcile on the page |
| **P-4** | Region totals, six cells | 1.3 | **Generated, and SHIPS from 2026-08-26.** C-098 gives the regional figures a row, settling the bucketing question that gated it all build |
| **P-5** | ~~Deviation figure~~ | **unused** | Built and correct — `assets/figures/mad-comparison.svg`. Nothing renders it now that 6.1 is quote-only. **Do not delete** |
| **P-11** | Advertising cost figure | 1.4 | **Built** — `assets/figures/ad-cost.svg`, from `build-adcost-figure.py`. Box plot across 44 studies |
| **P-10** | Throughput figure | 1.4 | **Built** — `assets/figures/throughput-box.svg`, from `build-throughput-figure.py`. Box plot: M3 interval on an M4 tick rule |
| **P-9** | Six institutional marks | 1.5 | **Not supplied.** No logo asset exists in this repo or `../proposals`. Needs the file *and* clearance — **D-014 is live again** |

**No placeholder stands in for a number.** Where a figure has no `VERIFIED` row the page
renders `—` (hard rule 2); the placeholders above are images, generated artefacts and one
recording.

### What actually renders, 2026-08-25 — the page is built

| | State on the built page |
|---|---|
| **P-1** Hero readout | **Held.** Its rows are `achieved / target` per stratum — real values with **no `CLAIMS.md` row**, so drawing it means inventing figures and hard rule 2 forbids that in terms. The hero ships as type on an M1 lattice. It needs a **recording from a study cleared for it**, which is a clearance question before it is a design one |
| **P-2** Coverage map | **Renders.** Generated, inlined, `[annotated]` and clean |
| **P-3** Region strip | **Renders, and now carries the amounts** — labels read `311,363 · MIDDLE EAST & NORTH AFRICA`. It is the only regional artefact on the page; the cells were withdrawn as redundant with it. C-098 |
| **P-4** Region totals | **Not on the page.** Shipped 2026-08-26 and withdrawn the same day as redundant with the strip directly above it — *"I prefer the strip."* **The amounts moved into the strip's labels**, so the figures ship and the cells do not. C-098 is still the row |
| **P-9** Six institutional marks | **Renders as type**, all six. The files exist in `assets/logos/` and **not one is cleared** (D-014). `_data/clients.js` holds `logo` and `cleared` separately, and a mark renders only when both are true |
| **P-10 · P-11** The two box plots | **Render, side by side, in one beat**, as specified. **Both were silently truncating their own source lines** — see `AGENTS.md`; fixed in the generators |
| **P-5** Deviation figure | Still unused, still built, still not to be deleted |

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
5. ~~**D-022**~~ — **settled 2026-08-26: no ghost segment.** The strip spans the attributed respondents and the page does not reconcile the difference.
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
