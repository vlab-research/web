# Agent Guide: vlab.digital

The public website for Virtual Lab, LLC. This file tells you how to work in this
repo. Read it fully before writing markup, copy, or config.

**Current state, 2026-08-25: the copy is finished and the build has not started. That is the
next job.**

The site is now **one page plus an unlinked privacy policy**, and every word of it is written
in **`COPY.md`** with each figure traced to a `CLAIMS.md` row. The brand is built — fonts,
icons, mark, favicons, and now four figures. **Nothing is blocked.** What a scaffolding agent
needs is in "Picking this up", and the single most useful instruction is: **build what
`COPY.md` says, in the order it says it, and do not re-derive the structure.**

---

## Read these first, in this order

1. **`DESIGN.md`** — the visual and brand system. Tokens, type, motifs, components,
   voice. **This is the current design and it supersedes any document, mockup, or
   habit that conflicts with it.**
2. **`DECISIONS.md`** — what has been settled, why, and what is still open. Check
   here before asking the user a question; it may already be answered. Check here
   before making an assumption; it may be an open decision you are not allowed to
   make alone.
3. **`CLAIMS.md`** — every factual claim the site is permitted to make, with its
   source. **No number reaches a page without an entry here.**
4. **`COPY.md`** — the copy, written 2026-08-22 against the D-027 spine and the six
   surfaces D-007 derives. Every figure carries its claim id; images and generated
   artefacts are numbered placeholders, indexed at the end.
   **`CONTENT.md` is superseded** — Nandan, 2026-08-22: *"ignore it entirely."* It was
   written against the nine-page sitemap D-007 dissolved. Keep it for the rejected drafts
   and their reasons; never write from it.

Four documents, and then the parts of the repo that enforce them. **The documents are no
longer the whole of the specification** — three of the rules in them are now executable,
and where a script and a paragraph disagree the script is what actually runs:

5. **`scripts/README.md`** — the four scripts, when to run each, and what a non-zero
   exit means. `check-claims.py` is the provenance rule, `check-contrast.py` is §3, and
   `build-coverage-map.py` is the only thing permitted to write the coverage artefacts.
6. **`scripts/fixtures/`** — nine cases asserting how `check-claims.py` behaves, two of
   them covering attributed quotation. Read `quote-abstract.html` beside
   `fail-quote-unattributed.html` before widening anything about quotation.
7. **`_data/paper.json`** — the manuscript as structured data. **Read the
   `not_for_publication` note at the top of it before using any field**; several are
   `WITHHELD` claims, and exactly two of them render.

### Precedence

`DESIGN.md` wins over everything on visual and voice questions. `DECISIONS.md` wins
on scope and direction. `CLAIMS.md` wins on facts, absolutely — a number in a mockup,
in a previous draft, or in this file is not evidence; only `CLAIMS.md` is.

When a document is wrong, **fix the document in the same change** as the code. A spec
that has drifted from the build is worse than no spec, because the next agent will
trust it.

---

## Where the work stands

Four phases, each with a human gate. Do not start a phase whose gate has not closed.

| Phase | Output | Status |
|---|---|---|
| 1 · Brand | Positioning, palette, motifs, `DESIGN.md` | **Complete** — Aug 2026 |
| 2 · Framework | This documentation set | **Complete** — Aug 2026 |
| 3 · Content | Copy material + the claim register | **Complete** — 2026-08-22 |
| 3.5 · Narrative | The spine the site argues, and the sitemap derived from it | **Complete** — 2026-08-22. D-027 and D-007 |
| 4 · Copy | Every word of the page, against the spine | **Complete — 2026-08-25.** `COPY.md`. Nandan: *"the plan is in a pretty good place. Let's wrap this up for now and a future agent will begin to scaffold the site"* |
| 5 · Build | Eleventy scaffold, the design system in CSS, the page | **Not started. This is the next job.** Nothing blocks it |

**The gate rule:** each phase ends with a deliverable the user reviews and approves —
usually published as an Artifact so it can be seen rather than described. Do not
roll from one phase into the next on your own initiative. Present, then wait.

**A gate closes when the user says so, not when the questions run out.** Phase 3 has been
through several rounds of review and every round produced settled decisions — that is
review happening, not review finishing. Read the distinction in "Picking this up" below
before assuming the build may start.

---

## Picking this up — state as of 2026-08-25

**Read this section first, then the documents in the order above.** Everything
below is already recorded in its proper home; this is a map, not a second source. If you
read one thing and stop, read "Where the work actually stands" and "Known drift".

### Where the work actually stands, 2026-08-25

**The copy is done and the build has not started.** Read **`COPY.md`** first and treat it as
the specification — it holds the page section by section, in reading order, with the claim ids
and the source lines already attached, and a note under each block saying what it must not
say and which draft it replaced.

**The site is one page plus privacy.** D-007's six surfaces were collapsed on 2026-08-25:

| | |
|---|---|
| **The page** | Opening (hero · totals band · coverage · two distributions · client wall) · what it takes (recipe · math · paper · instrument) · the audit trail · the close |
| **Privacy** | Carried over near-verbatim, and **not linked**. It still needs `data-claim-scan="off"` on the legal copy |

**Cut, with reasons recorded in `COPY.md`:** the brief form (replaced by `info@vlab.digital`),
the design patterns, the study cards, and the paper as its own page. **None of the material
was deleted** — the claim rows all stand, and each cut says what would bring it back.

**Four things a scaffolding agent should not re-derive**, because each cost a day and is
written down: the page order, the fact that **6.1 p.p. appears only inside the quoted
abstract**, the fact that **the client wall is marks-with-degradation-to-type**, and the
seam that **Part 2 argues that software must exist without explaining what the software
does**.

**D-014 is the only decision blocking Phase 4.** D-013 stopped blocking it when the hero
settled to a recorded replay; D-019 stopped blocking it when the coverage section landed
on Home. The region-bucket question and D-021, D-022 travel *with* sections rather than
in front of them, and each has a recorded fallback, so none of them holds a build.

### If you are here to scaffold the site, read this and then `COPY.md`

**Nothing blocks you.** The order below is the shortest path from this repo to a deployed page.

1. **Skeleton.** Eleventy, version-pinned (D-006). `_includes/base.html` holds head, the three
   theme states, the inlined icon sprite, nav and footer. `netlify.toml` gains a build command
   publishing `_site`. **`.gitignore` already exists.** Done when a placeholder page deploys.
2. **The stylesheet, from `DESIGN.md` and not from `css/main.css`.** Tokens verbatim from §3,
   type scale §4, layout §5. **`css/main.css` is the legacy SPA's and its first line imports
   Google Fonts, which D-012 bans** — take nothing from it. Gate: `check-contrast.py`, plus
   all three theme states including unstamped.
3. **Components before pages** — §8: stat row, ink band, client wall, coverage section, the
   two figure slots, buttons, nav. Publishing them as an Artifact for review makes step 4
   assembly rather than design.
4. **The page**, in `COPY.md`'s order. Annotate every figure with `data-claim` as you go; an
   un-annotated page passes heuristically and a false pass is what the rule exists to prevent.
5. **Privacy**, carried over with `data-claim-scan="off"`, at its URL and unlinked.
6. **Cutover.** Retire the SPA, **remove the BrowserSync `document.write` tag currently
   shipping to production**, resolve D-009 (PostHog has no consent mechanism and sits beside
   our own policy), check `_redirects`, then delete the legacy CSS.

**Four things in `COPY.md` are load-bearing and are easy to flatten by accident:** the two box
plots sit **together** in one beat; the math is an **ink band** and the footer is the only
other one; the paper's abstract is **quoted, never paraphrased**; and the client wall
**degrades to type**, which is not a fallback but the shipping mechanism.

### Read D-027 first. It is the spine everything else serves.

**The site argues four things in order, each answering the question the one before it
raises** — *who are you and have you done this* · *isn't that a convenience sample* · *so how
does it actually work* · *what about my study*. Opening, then the difference, then **a walk
through one study from brief to dataset**, then the design patterns. Reference surfaces hang
off it.

**Amended 2026-08-25, and read the amendment in D-027 before using the four parts above.**
The **homepage is now parts 1 and 2 only**: the opening (hero · totals · coverage · two
distributions) and the problem (operational, on an ink band), then the close. **The walk is
off the page for now**, with its approved rewrite held in `COPY.md`. **Part 2's question
changed** from *isn't that a convenience sample* to *why don't I just do this myself*. And
**6.1 p.p. no longer appears in the site's own voice anywhere** — only inside the quoted
abstract. C-003 explains why, including why it is not `WITHHELD`.

**The single most useful test in the whole documentation set:** if a section stops answering
the question its part is for, it is in the wrong part. That catches more than any style rule.

**Three seam rules, and they govern editing more than writing.** Part two states the problem
and the measurement and **never the mechanism** — the mechanism belongs to the walk, shown
rather than asserted. **The walk never forks**; the first *"or, alternatively…"* belongs in
part four. **The panel is walk beat four, so it is not also a design pattern.**

**D-007 is the sitemap derived from that spine** — six surfaces plus privacy, where nine were
on the table the same morning. One sub-question is deliberately left for the build: whether
the design patterns are the spine's tail or the surface after it. **Decide it by looking at
how the spine reads at length, not by arguing.**

**How this was arrived at matters more than the answer, because the process failed once
first.** The sitemap was originally settled before any narrative existed and copy was written
into it — structure as an input to content rather than an output of it. That produced three
sitemap changes in three days, each locally reasonable. It was reopened to **nothing** on
2026-08-22, four narratives were sketched and compared, and the sitemap was re-derived from
the one Nandan chose. **The rule that came out of it, in D-007:**

> **A sitemap change is never a side effect of a content decision.** If a decision about what
> to say also decides where it goes, the second half is not decided — it is assumed.

**`DESIGN.md` §1 states the spine the narrative should be built on**, and it is Nandan's
sentence, 2026-08-22: *there is a **method**, there is a **technology**, and with those tools
we build **study designs**.* It is why the sampling method and the designs built on it are not
the same subject, why the instrument is scope rather than proof, and the test for a misfiled
claim — a claim belongs to exactly one of the three.

**D-024 is settled in part.** Fly is named; the recruitment side is cited rather than branded;
a navigation label is a function, not a product name. Nothing in the visual system changed
except §6: M5 is Fly's identity, and the Banned list gains a literal-rendering line. **Its
placement half was withdrawn into D-007.** **Read it before writing a word about Fly** — four
of the capabilities everyone remembers came back wrong, and the discipline that matters is
that every sentence traces to a row.

**The forward rule, settled by Nandan in the same session, and it is broader than Fly.**
*Webpages should run 2–3 months ahead of live features* — a capability on a branch, merged
but not enabled, or otherwise near-shipping is publishable. **It applies to capabilities and
never to figures**: a number cannot be early, because there is nothing to be early *about*.
And it does not cover a feature that was **pulled** rather than postponed — respondent image
collection was built and deliberately removed, and it stays `WITHHELD`. The rule and its
limits are written into `CLAIMS.md`.

### What is built, and where it is

The documentation stopped being the only thing in this repo on 2026-08-20. A future agent
should expect these to exist and should not rebuild them:

| | |
|---|---|
| `fonts/` + `css/fonts.css` | The complete kit, self-hosted per D-012 — twelve `.woff2`, all seven face+weights, latin and latin-ext. Nothing loads from a Google origin |
| `assets/icons/` | The twelve §7 icons at 24×24, plus the `<symbol>` sprite `icons.svg`. **Inline the sprite**; `<use href="external.svg#id">` does not resolve cross-document |
| `assets/mark.svg` | The nav mark. Built to cell 6 / pitch 8 — a ratio §6 does not sanction. That is D-021 question 2, and it is drift until the decision lands |
| `assets/favicon.svg`, `favicon.ico`, `apple-touch-icon.png` | Built from M2, and the reason D-011 now states a size threshold: the hatch does not survive below ~24px |
| `assets/figures/mad-comparison.svg` | One bar on a 0–12 p.p. ruler. Redrawn 2026-08-20 when D-023 removed the comparators — **not** three bars, and not to be "restored" |
| `_data/paper.json` | The manuscript mined into structure — abstract verbatim, cost table, comparator figures, constructed BibTeX. **Several of its fields are `WITHHELD` claims.** Two fields render, both on Papers: `bibtex.entry`, and `abstract.verbatim` as quotation only |
| `build/` | Output of `scripts/build-coverage-map.py` — map, region strip, region totals, all three computed from `scripts/data/coverage.json` rather than typed. Generated, untracked, and safe to delete; re-run the script |
| `assets/figures/throughput-box.svg` | **New 2026-08-25.** Respondents recruited per study per active day — median 140, box 69–300. From `build-throughput-figure.py` + `data/throughput.json` |
| `assets/figures/ad-cost.svg` | **New 2026-08-25.** Advertising cost per respondent — median $1.05, box $0.29–$1.57. From `build-adcost-figure.py` + `data/ad-cost.json`. **Advertising spend only; never a price** |
| `assets/logos/` | **New 2026-08-25.** Eight authentic institutional SVGs. **Downloaded, not cleared** — every one needs permission for third-party use; see D-014 for what each source actually says |
| `.gitignore` | **New 2026-08-25**, and it finally guards `media/` |
| `scripts/` | **Six** scripts and a fixture suite. **Start at `scripts/README.md`** — it says what each one does, when to run it, and what a non-zero exit means. The two new ones build the figures above and **exit non-zero if a value falls outside the drawn axis**, so a figure cannot silently clip a claim |

### What closed

- **D-006 build stack — Eleventy**, version-pinned. Reverses an earlier Astro
  recommendation whose premise (Markdown for human authors) no longer holds.
- **~~D-007 sitemap~~ — reopened 2026-08-22, entirely.** See above. Per-study detail
  surfaces stay deferred, and that is **not** a placement clause: it is a rule about figures
  that are `PLACEHOLDER` and uncleared, and it holds under any structure.
- **D-024 — Fly is named**, the recruitment side is cited, not branded; its internal name
  stays in the schema. No mark, no colour, no thirteenth icon: Fly's signature is the radius
  §5 already reserved for the thread. **Placement withdrawn.**
- **D-018 coverage map — cropped choropleth** with hairline borders. Also settles where
  the line sits between a sanctioned coverage map and the banned globe; §6 now says it.
- **Phase 3 copy drafted** for the seven original clusters, plus the instrument material
  (2026-08-21) and the design-pattern material (2026-08-22). Artifact links in `DESIGN.md`
  §13 — **both predate the 2026-08-22 reopening and show material as though it were pages.**

### What changed underneath the facts

**`CLAIMS.md` gained a Production figures section**, and it matters more than the copy
deck. Scale claims now come from the production database, not from the paper:
**841,660 respondents · 17,979,910 responses · 41 countries · median field window 19
days.** The paper's "33 studies across 23 countries" describes studies *in the paper*
and understates the business; it is now the narrow claim, not the headline.

Three traps are written up there and are easy to walk into:

1. **C-004 is `WITHHELD`** — the abstract says $0.30 per question, the paper's own cost
   table computes $0.32, and the resolution was to publish neither **in our own voice**.
   Note the knock-on: C-012 and C-013 are stated in per-question units too, so the cost
   section is built on the per-participant figures in C-014 and keeps C-012/C-013 as
   ratios, not operands. **One page states the figure and it is not an exception:** Papers
   reproduces the paper's abstract verbatim as attributed quotation (D-016), which is
   somebody else's assertion, not ours — see hard rule 1 and `DESIGN.md` §8.
2. **C-013: we are not the cheap option.** Roughly 3× Prolific's cost per question, per
   our own published table. Cheaper than gold-standard probability surveys, not cheaper
   than a panel.
3. **C-006–C-009 are `WITHHELD`, and this is the trap that changed most.** The site makes
   **no comparison with another recruitment source** — no panel, no Prolific, no LLM
   digital twins, no "closer than" in any form (D-023). What we publish is C-003, our own
   deviation from GSS, CPS and Pew. Cost comparisons (C-012, C-013) are unaffected: they
   are ratios from the paper's own table and C-013 runs against us.

### Two contrast bugs were fixed, and the fix is in the script

`--data` on an ink band measured **2.10:1** — worse than the `--brass` failure that had
already shipped once — and `--ink-3` source lines on an ink band measured 4.00:1. §3
had prescribed the right value for the first without ever naming it as a token.
`--data-inv` now exists, and **both pairs are enforced in `check-contrast.py`** rather
than described in prose. 22 pairs, all passing.

### Two checker bugs were fixed, and a regression suite locks them down

Both were found on 2026-08-20, both in `check-claims.py`, and both are the same shape: a
row's *caveat prose* was read as its *status*.

1. **C-054's scope caveat "do not generalise" was read as a publication ban.** That held
   the whole row back, which made every numeral in it banned, which **banned the citation
   year 2025 site-wide** — on a register that mandates "Donati & Rao, 2025" in every source
   line. `pass.html` carries that source line, so the suite fails if it returns.
2. **A four-digit year harvested from a held-back row is never that row's claim value.**
   Excluding the whole Source column looks like the tidier fix and is wrong: C-004 names
   the $0.30 and $0.32 it withholds in exactly that cell, and losing them would unban the
   figure the register exists to withhold.

`scripts/test-check-claims.py` runs **nine cases** over the fixtures in
`scripts/fixtures/`. Two of the nine cover attributed quotation: `quote-abstract.html` is
the Papers abstract (exit 0, one warn on the withheld $0.30), and
`fail-quote-unattributed.html` is the same attribute used as a loophole in three shapes
(exit 1). Run it after touching the checker or the register's status vocabulary — the
checker is the rule, so a broken checker is a broken rule.

### The `data-claim-quote` mechanism, in one place

`data-claim-quote="C-nnn"` marks a container as **attributed quotation** — somebody else's
words, reproduced verbatim, whose numerals are that author's figures and not our claims.
It exists because a citation page that silently edited its own paper's abstract would be a
worse failure than either version of a contested number. Three constraints are enforced,
not described: a `VERIFIED` row for the document being quoted, a visible attribution line,
and a `warn` on every withheld value it shields, on every run.

**It is expected on exactly one page — the abstract on Papers (D-016) — and nowhere else
on the site.** A second use is a signal to stop and ask, not a pattern to copy. Full
statement in hard rule 1, markup in `DESIGN.md` §8, reasoning in D-016.

### Closed 2026-08-20 and 2026-08-21, in this session

| | |
|---|---|
| C-004 | **Publish no cost-per-question figure.** Now `WITHHELD`, with a knock-on to the Method cost section — see `CLAIMS.md` |
| C-019 | **175 studies** — 119 current-platform plus 56 older campaigns. Publishable, but never explained with platform language |
| D-020 | **Four-cell totals band** on Home — 841,660 respondents · 17,979,910 survey responses · 41 countries · 175 studies fielded. The old stat row is dropped; median field window (C-011) moves into the prose beside the band |
| D-013 | **Recorded replay at launch**, live as a fast-follow. Phase 4 is no longer blocked on it |
| D-023 | **No competitor comparison, anywhere on the site.** C-006, C-007, C-008 and C-009 are now `WITHHELD` — decided against, not pending. Home §4 is rebuilt around C-003 alone, `DESIGN.md` §2 rule 5 no longer prefers the comparative, and `assets/figures/mad-comparison.svg` is redrawn as one bar on the same ruler. **Amended 2026-08-21** to read *in our own voice*, once the abstract was restored — the amendment is a boundary, not a softening |
| D-019 | **Coverage section goes on Home**, on paper ground; the Studies index carries no map. Section order and the §8 adjacency check are in `CONTENT.md` Home |
| D-016 | **Papers carries the citation, the link, and the paper's abstract quoted verbatim** — title, byline, abstract inside `data-claim-quote="C-055"`, citation, BibTeX, link. **No cost table, no figures.** *Restored 2026-08-21, reversing the previous day's "no abstract" reading — the reasoning is in D-016 and matters more than the outcome* |
| C-055 | The paper's public URL, now **`VERIFIED`** — `https://ssrn.com/abstract=5495148`, supplied by Nandan as co-author, **not independently verified** (SSRN 403s every non-browser client). Citation year settled at **2025** and now published: source lines read "Donati & Rao, 2025". BibTeX constructed in `_data/paper.json`. **C-055 is load-bearing twice over** — it is the link, and it is the row the quoted abstract is attributed to |

### Waiting on Nandan — and none of it blocks the build

| | |
|---|---|
| **D-014** | **The logos.** Eight authentic files are in `assets/logos/`; **not one is cleared.** Every institution requires permission for third-party use, and World Bank, Harvard and WashU explicitly bar implying affiliation — which a logo wall is. WashU's own policy describes this exact case and allows **text only**. D-014 quotes each source. **The wall degrades to type, so the page ships regardless** |
| **D-025** | **May the privacy policy be amended?** Three things the instrument does are not described in it. Still open **even though the policy is now unlinked** — unlinked is not unamended |
| **SSRN edition** | **Which edition is posted?** The only compiled PDF we hold is the blinded submission with no byline. The page cites and links the paper, so if that is what was uploaded a reader gets an author-less document under a byline we printed. Ten seconds for him, unanswerable from here |
| **Region buckets** | The six regional totals still have no row because the bucketing is editorial. Fallback recorded: publish country figures, drop the regional layer |
| D-022 | Whether the region strip draws the unattributed respondents as a ghost segment |
| D-021 | Two motif rules; question 2 is live drift in `assets/mark.svg` |
| D-017 | Jobs posting |

**Closed in the 2026-08-25 session, so do not reopen them by accident:** the copy itself; the
sitemap (one page); C-094 to C-096 (the three universities, on operator knowledge); the walk
coming off the page; 6.1 p.p. becoming quote-only; and the client wall becoming marks rather
than type-with-engagements.

### Known drift — re-derived 2026-08-25 by running the checks

`python3 scripts/check-claims.py` reports **23 findings**, and the walker skips
`scripts/fixtures/`, so all 23 are real. They fall in three places:

- **11 in `index.html`** — the **legacy SPA**, which is being replaced, not fixed. The Nigeria
  funnel figures and study-design facts have no rows, and two privacy numerals need
  `data-claim-scan="off"`. **Scaffolding the new site retires all eleven.**
- **9 in `build/coverage-regions.html`** — the six per-region totals and their country counts.
  **A decision, not a bug:** the figures are sums of a verified table; the *bucketing* is
  editorial and has no row. Fallback recorded.
- **3 in `build/coverage-map.html`** — the legend's magnitude labels. **A cheap spec drift:**
  §8 says they carry `data-claim="none"` and `build-coverage-map.py` emits no `data-claim` at
  all. **Fix the generator, never the output.**

`test-check-claims.py` — 9/9. `check-contrast.py` — 22 pairs, all pass.
`build-coverage-map.py` — clean, 41 countries, 6 regions.

**Two rules that no checker can enforce, so they are yours to hold:**

1. **6.1 p.p. may appear only inside the quoted abstract.** C-003 is deliberately left
   `VERIFIED` rather than `WITHHELD`, because a withheld row bans its numerals at ±2% and
   **banning 6.1 would ban every bare `6` on the site**. See C-003.
2. **The client wall's names are verified; its logos are not.** A verified row licenses the
   relationship, never the mark.

**Still true and still worth knowing:** `build/` is generated and now git-ignored; the
generated artefacts have generators and **hand-editing one desynchronises the sprite**; and
`notes/` is nine workstream memos that are not a source of truth.

### One positioning fact, now examined — and one number in this file was wrong

**Corrected 2026-08-20.** This section previously read "Middle East & North Africa at
311,363 respondents — **42% of the total**." The count is right; the share was not.
311,363 ÷ 738,608 (respondents attributable to a country) = **42.2%**. But
311,363 ÷ 841,660 (C-010, the published headline) = **37.0%**. The gap is the 103,052
unattributed respondents. A page that prints "42%" beside a headline of 841,660 does not
reconcile, on the one site whose whole proposition is that its numbers reconcile.
**Any share must carry its denominator, or publish the count alone.** MENA is also a
floor — PS has no count — and the region bucket is an editorial choice made in
`coverage.json`, not a fact from the database.

**One line of argument was examined and rejected.** An earlier draft of this section
observed that the highest-volume countries carry no client we may name, and concluded
that the client wall and the coverage map "answer different questions whose answers will
never agree." **Struck 2026-08-20 by Nandan.** If we surveyed people, we surveyed them; a
client we cannot name is a confidentiality term, not a discrepancy, and neither surface
claims the two distributions should match. Do not reintroduce it — in D-019 or anywhere
else. D-019 has since settled the coverage section onto Home, where it sits on the same
page as the client wall; that makes the struck argument irrelevant as well as wrong.

**Two framings are not publishable, and the reason is the same for both.**
*"Strongest where panels are weakest"* and *"where conventional fieldwork cannot go"*
both need a row `CLAIMS.md` does not have. The only panel evidence we ever owned is
C-006/C-008 — Prolific, US benchmarks — and using a US methodological comparison to imply
anything about panel *coverage of Iraq* is a different claim with no evidence at all. It
is also arguably false on our own data: our largest single country is the US. **Both
framings are now doubly banned:** those rows are `WITHHELD` under D-023, so the site
compares itself with no other recruitment source at all. A third variant was caught in
the Method cost copy on 2026-08-20 — *"in places a probability survey cannot go"* — and
removed for the same reason.

**~~The framing is settled: state what a study requires, and let the reader draw the
inference.~~ Reversed 2026-08-22 by Nandan, and the reversal is instructive.** The coverage
lede read *"What a study needs is an ad platform and a messaging app."* Nandan: *"it's cute.
If there's something we actually wanna say there, let's say it. We don't need a messaging
platform. We could use a web form, so that doesn't seem very accurate."*

**It was wrong on the facts, not only on the tone**, and the register already said so:
**C-057** gives the channels as Messenger, WhatsApp **or a web form**, the web form being a
study-level destination. A lede asserting what a study *requires* was therefore a
requirements claim with no row behind it — the "state what a study requires" framing is
attractive precisely because it sounds modest, and it smuggled in a constraint that does
not exist. **The replacement is a plain heading, "Where the respondents are," carrying no
claim at all**: the map, the strip and the totals each state their own figures with their
own source lines, and a heading stacked on top of three artefacts that already speak is a
heading looking for something to do. Copy in `COPY.md`, **Spine §1.3**.

**C-032 was cut in the same breath** — *"let's remove the field office stuff. No need to say
that."* The row stays `VERIFIED` and is published nowhere. The four largest samples outside the United
States are **Nigeria · Jordan · Iraq · Bangladesh**, in that order; an earlier draft of
that list omitted Nigeria, which is the largest of the four.

**C-032 is operator knowledge:** there is no field office in any of those four countries,
confirmed by Nandan 2026-08-20. It is `VERIFIED` and available — **and as of 2026-08-22 it
is published nowhere**, cut with the lede above. It licenses the fact, not a comparison, and
it does not resurrect either banned framing.

---

## Hard rules

1. **The provenance rule.** Every number on the public site carries its source in the
   same visual unit — same card, same weight as the label. If you cannot cite it from
   `CLAIMS.md`, it does not go on the page. This is the whole brand proposition;
   breaking it is the most expensive mistake available in this repo.

   `python3 scripts/check-claims.py` enforces both halves of this rule. Pages declare
   their claims with `data-claim` (see `DESIGN.md` §8, "Claim annotation"); an
   un-annotated page is still scanned heuristically, but heuristic mode can pass a number
   by coincidence, so annotate. **Run `python3 scripts/test-check-claims.py` whenever you
   touch the checker or the register's status vocabulary** — the checker is the rule, so a
   broken checker is a broken rule.

   **One exemption exists and it is not an exception to the rule.** `data-claim-quote="C-nnn"`
   marks a container as **attributed quotation** — somebody else's words, reproduced
   verbatim, whose numerals are that author's figures and not our claims. It requires a
   `VERIFIED` row for the document being quoted and a visible attribution line, and every
   withheld value it shields is **reported at `warn` on every run**. It is expected on
   exactly one page — the abstract on Papers (D-016). **A second use is a signal to stop
   and ask, not a pattern to copy.** Paraphrase inside a quote block is not quotation and
   the checker cannot tell the difference: quote, or write outside the block.

2. **Never invent a figure.** Not as a placeholder, not "to be replaced later," not in
   a mockup. If a real value is missing, write `—` and add a `PLACEHOLDER` row to
   `CLAIMS.md`. Plausible fake numbers survive into production; visible gaps do not.

3. **Never claim AI.** The optimiser is convex optimisation over ad budgets. Saying so
   is the stronger claim and the true one.

4. **Client names are not free.** Displaying an institutional logo usually requires
   written permission (see D-002). Text mentions of past work are lower risk but still
   check `DECISIONS.md` before adding a name that is not already on the site.

5. **Colour comes from tokens, never literals.** A new colour requires a change to
   `DESIGN.md` first, agreed with the user. Same for a new typeface.

6. **Run the contrast check before publishing anything with a new colour pair.**
   `python3 scripts/check-contrast.py`. It exists because this exact bug already
   shipped once — brass on an ink band read 2.43:1 in light mode and looked perfect in
   dark. See `DESIGN.md` §3, "The `--brass-inv` trap."

7. **Three theme states, not two.** Explicit light, explicit dark, and **unstamped**
   (system default) — which is what most visitors get. Never declare a colour whose
   only definition sits inside a media query or a `[data-theme]` block.

8. **All graphics are inline SVG** built from the four primitives (bar, tick, cell,
   bracket). No icon fonts, no chart libraries, no raster illustration. If a needed
   drawing cannot be made from the primitives, that is a signal the concept does not
   belong on the page — raise it rather than reaching outside the system.

---

## Things about this repo you should not have to discover the hard way

- **The working directory is 244 MB; the repository is not.** `media/` — 226 MB of raw
  field photographs — is untracked and has never been committed, so it is also backed
  up by nothing. `.git` is 9.9 MB. Never `git add media/`, and see D-010 before adding
  anything else large.
- **The current site is a hand-rolled SPA.** `index.html` holds every page as a `div`,
  switched client-side by Navigo 8 loaded from unpkg. `css/main.css` is hand-written.
  There is no build step. The target architecture is Eleventy (D-006) — do not extend
  the SPA; it is being replaced, not carried forward.
- **There is a live BrowserSync `document.write` script tag** at the bottom of
  `index.html` pointing at `http://HOST:3000`. It is development leftover shipping to
  production. Remove it in the rebuild.
- **PostHog is loaded on every page** with no consent mechanism (see D-009). This sits
  awkwardly beside our own privacy policy.
- **The privacy policy is genuinely good** and recently updated (2026-05-15). It is the
  one piece of existing content worth carrying over close to verbatim. Do not
  regenerate it; move it.
- **`build/` is generated.** `scripts/build-coverage-map.py` writes there. It is not
  committed; add `build/` to `.gitignore` when one exists (there is no `.gitignore` in
  this repo at all yet, which is its own small problem).
- **`scripts/fixtures/` is full of pages designed to fail.** Nine of them, deliberately,
  and they are inside the tree `check-claims.py` used to walk by default, which made a
  bare run exit 1 no matter how healthy the site was. **Fixed 2026-08-21:** the walker
  skips `scripts/fixtures/`, so a bare `python3 scripts/check-claims.py` now reports only
  real drift — 25 findings, down from 52. Use `test-check-claims.py` to judge the checker
  itself; a gate that can never pass is a gate nobody runs.
- **The generated artefacts have generators, and the generators are now in `scripts/`.**
  `assets/icons/` and the sprite come from `build-icons.py`; `_data/paper.json` from
  `build-paper-json.py`; `build/` from `build-coverage-map.py`; the review page from
  `build-review.py`. **Never hand-edit generated output** — editing one icon file
  desynchronises the sprite, and the next run silently reverts you. Change the generator.
- **`notes/` is nine workstream memos, ~42,000 words, and is not a source of truth.**
  It records how questions were investigated, including reasoning that later decisions
  overturned. `notes/README.md` states the precedence. Never cite a memo against a
  governing document.
- **`build/` is generated and untracked.** `python3 scripts/build-coverage-map.py`
  recreates it. Deleting it costs one command.
- **Deployment is Netlify** (`netlify.toml`, `_redirects`).
- **The brand already existed in the proposals repo** before the website caught up:
  `../proposals/src/vlab_proposals/static/style.css` and `static/fonts/` hold the
  wordmark, colours and three of the four `.woff2` files. The website inherits from
  the proposals, not the other way round. **The fonts no longer need it:** the website
  has its own complete kit in `fonts/` + `css/fonts.css` (D-012). The proposals copy
  carries weights §4 does not use — do not sync the two directories.

---

## Verification before you hand anything over

Run through this list. Do not report work complete until every line passes or you have
said explicitly which one does not and why.

- [ ] `python3 scripts/test-check-claims.py` passes — all nine cases, meaning the
      checker itself still works
- [ ] `python3 scripts/check-claims.py <the files you changed>` is clean — every number
      traces to a `VERIFIED` row and carries a visible source line in its own visual unit.
      **Name the files.** The bare command also walks `scripts/fixtures/`, which is nine
      pages built to fail, so it exits 1 by design and always will; the number to compare
      against is the one in "Known drift", not zero
- [ ] `python3 scripts/check-contrast.py` passes — 22 pairs
- [ ] `python3 scripts/build-coverage-map.py` runs clean if coverage data changed
      (it exits non-zero and prints a banner for any country it cannot draw, or for a
      country that is in no region or in two — never ignore either)
- [ ] Page renders correctly in **all three** theme states (light, dark, unstamped)
- [ ] `body` sets an explicit `background` from a token
- [ ] No colour, font, or radius outside the `DESIGN.md` tokens
- [ ] Wide content scrolls inside its own container; the body never scrolls sideways
- [ ] Keyboard focus is visible on every interactive element
- [ ] Decorative SVG has `aria-hidden="true"`; meaningful SVG has `role="img"` + `<title>`
- [ ] Motion respects `prefers-reduced-motion`
- [ ] No new claim was introduced that is not in `CLAIMS.md`
- [ ] Any spec drift is fixed in the doc, in this change
- [ ] If you changed what the repo contains — a new script, a new generated directory, a
      new asset kind — **"Picking this up" and the repo tour above say so.** These
      documents are the handover; a state that lives only in a session is a state the next
      agent has to re-derive

---

## When you disagree with the spec

Say so, in one or two sentences, then follow it. If it is important enough to change,
propose the change as an edit to `DESIGN.md` or a new entry in `DECISIONS.md` and let
the user decide. Do not quietly build the better version — the value of this system is
that a page built six months from now still matches one built today.
