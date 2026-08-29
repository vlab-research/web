# Agent Guide: vlab.digital

The public website for Virtual Lab, LLC. This file tells you how to work in this
repo. Read it fully before writing markup, copy, or config.

**Current state, 2026-08-26: the site is built and it runs.** Eleventy, the design system in
CSS, the page in `COPY.md`'s order, and privacy at its URL. `npm run serve` to see it,
`npm run check` for the three gates. **Two things on the page are deliberately held and are
not oversights** — the hero readout and the region totals; both are in "What is held" below,
with the one-line change that ships each. The next job is review, not construction.

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
6. **`scripts/fixtures/`** — **ten** cases asserting how `check-claims.py` behaves. Two
   cover attributed quotation: read `quote-abstract.html` beside
   `fail-quote-unattributed.html` before widening anything about quotation. Two cover
   **citation**: read `pass-own-record.html` beside `fail-provenance.html` before touching
   the provenance check — **if both ever pass, citation has stopped applying to
   anything.**
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
| 5 · Build | Eleventy scaffold, the design system in CSS, the page | **Built 2026-08-25.** Deploys from `netlify.toml`; three gates pass; two components held on decisions, not on work |
| 6 · Docs | `docs.vlab.digital` folded into this build at `/docs/` | **Built 2026-08-29.** D-008. 47 pages, Hugo retired, one shell for the property. One DNS step outstanding — see below |

**The gate rule:** each phase ends with a deliverable the user reviews and approves —
usually published as an Artifact so it can be seen rather than described. Do not
roll from one phase into the next on your own initiative. Present, then wait.

**A gate closes when the user says so, not when the questions run out.** Phase 3 has been
through several rounds of review and every round produced settled decisions — that is
review happening, not review finishing. Read the distinction in "Picking this up" below
before assuming the build may start.

---

## The documentation lives here now — 2026-08-29

**`docs/` is 47 Markdown pages served at `vlab.digital/docs/`.** They were a separate Hugo
site at `../docs.vlab.digital`; D-008 folded them in. **Read D-008, D-029 and D-030 before
touching anything under `docs/`** — between them they say what the docs inherit from this
design system, what they are exempt from, and what the search script is allowed to do.

**Four things about it that will otherwise cost you an hour each.**

- **Docs Markdown is NOT templated, and this is not a preference.**
  `docs/docs.11tydata.js` sets `templateEngineOverride: "md"`. The repo default is
  `markdownTemplateEngine: "njk"`, and Nunjucks over this content **fails the build**:
  Fly's message interpolation is written `{{hidden:name}}`, and documenting that syntax
  is much of what these pages are for. Turning Nunjucks back on to get one dynamic value
  will break six pages. Put dynamic things in the layout.
- **`.eleventyignore` says `/*.md`, and the leading slash is load-bearing.** A bare
  `*.md` matches at every depth and silently swallows all 47 docs pages.
- **`check-claims.py` skips `docs/`** (D-029) and so the bare run still means something.
  The provenance rule is **not** narrowed: a docs page that states an outcome figure is
  making a claim and gets scanned by naming the file.
- **`scripts/check-links.py` is new and it currently reports 9.** All nine are screenshots
  that were never committed — six `bails-*`, three `fly-monitor-*` — and were broken on the
  Hugo site too. `notes/ws-docs-screenshots.md` is the capture plan. **The expected count is
  9, not 0**, until those images land; treat any other number as a regression.

**One deploy step is outstanding, and the docs are not live at their old URL without it:**
add `docs.vlab.digital` as a domain alias on the Netlify site and point its DNS there.
`_redirects` carries the host-scoped 301s. Until that is done the old GitHub Pages site
still answers that host and the two diverge silently.

**How the pieces fit:** `docs/*.md` → `_includes/docs.html` (sidebar, breadcrumbs,
contents rail) → `_includes/base.html` (the shared head, mark and footer, with the
marketing CTA switched off by `docsSection`). The sidebar comes from the `docsTree`
collection in `eleventy.config.js`, ordered by front-matter `weight`. `docs-search-index.njk`
sits at the ROOT, beside `sitemap.njk`, because anything inside `docs/` would inherit the
Markdown override and emit JSON full of `<p>` tags.

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
| **The page** | Opening (hero · totals band · **client wall** · coverage · how fast a study fills · what the advertising costs) · what it takes (recipe · math · paper · instrument) · **the code is open source** · the close. **Reordered and re-cut 2026-08-26 — see below** |
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
on Home. The region-bucket question and D-021 travel *with* sections rather than
in front of them, and each has a recorded fallback, so none of them holds a build.

### The build, as it stands 2026-08-25

**`npm run serve` and look at it before you read another word of this.** Everything below is
easier to hold once you have seen the page.

| | |
|---|---|
| `package.json` | Eleventy **pinned at 3.1.6** with a lockfile (D-006). `build` · `serve` · `check` · `figures`. `type: module` |
| `eleventy.config.js` | Input is the **repo root**, so `_includes/base.html` and `_data/` sit where D-006 says. Passthrough: `css` `fonts` `assets` `robots.txt` `_redirects` |
| **`assets/logos/` is NOT published** | `eleventy.config.js` copies `assets/` subdirectory by subdirectory so the eight institutional marks never reach the build. **Not one is cleared (D-014)** — copying `assets/` wholesale would host eight third-party trademarks on our own domain, publicly fetchable, with no permission for any. Nothing references them; the wall renders as type. **When a mark clears, add its file to the passthrough list AND flip `cleared` in `_data/clients.js`** — two separate things |
| `.eleventyignore` | The documentation set, `notes/`, `scripts/`, `js/`, `img/`. `build/` `media/` `node_modules/` `_site/` come free from `.gitignore`, which Eleventy honours |
| `_includes/base.html` | Head, the inlined icon sprite, nav, footer, scroll-progress rule. **No analytics** — see D-009 below |
| `_includes/macros.njk` | **New 2026-08-26.** `lattice(id, inv)` and `objective()`. The M1 lattice takes an id because each instance needs its OWN `<pattern>` — one shared pattern in `<head>` would break the `.inv` colour swap, since `currentColor` inside a `<pattern>` resolves where the pattern is **defined**, not where it is used |
| `css/site.css` | `DESIGN.md` §3–§9 in section order, ~620 lines. Built from the document, **not** from `css/main.css`, which is deleted |
| `index.html` · `privacy.html` · `404.html` | The three pages. `privacy.html` permalinks to `/privacy/` and is **not linked from anywhere** |
| `_data/coverage.js` | Reads `build/*.html` and strips the generator's "Required CSS" comment. **Raises if `build/` is missing** rather than rendering an empty coverage section |
| `_data/inline.js` | The sprite, the mark, and the two figure SVGs, inlined whole so they take `currentColor` |
| `_data/clients.js` | The six institutions, each with `logo` **and** `cleared`. **A mark renders only when both are true**, and `cleared` is false on all six until D-014 closes |
| `netlify.toml` | `npm run build` → `_site`. That is `build-coverage-map.py` **and then** Eleventy: `build/` is untracked, so the deploy regenerates it |

**Retired in the same change, and all of it is recoverable with `git checkout`:** the SPA
`index.html`, `css/main.css`, `css/normalize*.css`, `js/` — and with them the **BrowserSync
`document.write` tag that was shipping to production** and the **PostHog snippet**. The
`_redirects` catch-all `/* /index.html 200` is gone too: it is what a client-side router
needs, and under Eleventy it would turn every 404, including a typo'd `/privacy`, into a
silent homepage. Four 301s replace it for the old SPA fragments.

### `_data/*.js` must export a FUNCTION, and this one cost an hour

**Both `_data/coverage.js` and `_data/inline.js` exported an object literal**, which Node
evaluates once at import and then pins in the ESM module cache for the life of the process.
**`eleventy --serve` therefore served whatever `build/` and `assets/figures/` held when the
server started**, no matter how many times a generator re-ran afterwards.

**The symptom was baffling and worth recognising again.** Nandan: *"I sometimes see 'the bar
spans the X respondents' underneath the strip bar. It then sometimes disappears, then comes
back."* It was not intermittent at all — a one-shot `npm run build` was always correct and
the long-running dev server was always stale, so which one he was looking at decided what he
saw. A repo-wide grep found the sentence only in a source comment, which made it look like a
ghost.

**Both files now export `() => ({ … })`.** Eleventy calls the function on every build, so the
files are re-read. **Any new `_data/*.js` that reads from disk must do the same** — an object
literal there is a latent version of this bug, and nothing in the checks will catch it.

**A generated artefact that looks stale is this, until proved otherwise.** Kill the dev
server, `rm -rf _site build`, `npm run build`, and compare — that is the two-command test.

### index.html is a page, not a notebook — keep it that way

**Halved on 2026-08-26**, 729 lines to 485, after Nandan: *"It's very hard to look at
index.html and edit."*

**The SVG was not the problem** — inline lattice and MathML were 25 lines. **Half the file
was commentary.** The reasoning belongs in `COPY.md`, `CLAIMS.md` and `DESIGN.md`, which
already held all of it; the page had grown a second copy.

**The rule going forward: a comment in `index.html` earns its place only if someone editing
that line would break something without it.** Everything else is a pointer. What stays inline
is the short form — *this is held and why*, *this claim has a scope note*, *this list of five
exclusions* — and the argument lives in the documents.

**Two mechanical wins in the same pass:** the M1 lattice and the objective function moved into
`_includes/macros.njk`, so a band is now one line.

**One thing was lost and restored, and it is a warning.** The compression was done with a
regex over comment blocks and it swallowed the **held reallocations figure** — markup *inside*
a comment. **The whole rebuild is uncommitted**, so git could not recover it; it was rewritten
from the session. Commit before running a sweeping edit over this file.

### What is held, and why — read this before "fixing" either

**Neither is unfinished work. Both are one line, and both are somebody's decision.**

**`index.html` carries no comments at all** (2026-08-26), so everything below is the only
record that these slots exist. Read it before concluding the page is missing something.

- **[P-1] The hero readout.** `COPY.md` §1.1 wants a recorded replay of a live stratum
  readout. The component's rows are `achieved / target` **per stratum** — real values from a
  real study — and **no `CLAIMS.md` row exists for any of them.** Rendering it today means
  inventing figures, which hard rule 2 forbids in exactly these words: *"Not as a placeholder,
  not 'to be replaced later,' not in a mockup."* So the hero ships as type on a lattice. It
  needs a recording from a study cleared for it, not a designer.
- ~~**[P-4] The region totals.**~~ **The figures ship; the cells do not.** *"We need the region
  amounts!"* settled the bucketing question that had held them since the build began — and
  the cells that first carried them were withdrawn the same day as redundant with the strip
  directly above (*"I prefer the strip"*). **The amounts moved into the strip's labels.** **C-098 is
  the row, and adopting it adopts the sensitivity that kept it back:** the MENA bucket
  includes Israel, and that grouping is an editorial choice made in `coverage.json`, not a
  fact from the database. **Two of the six are floors** — MENA and Europe & Central Asia each
  contain a covered country with no computed count — and that is recorded in C-098 and
  published nowhere.
- **The client wall** renders all six as **type**, because D-014 has cleared no mark. The
  files are in `assets/logos/`. Flip `cleared` in `_data/clients.js` per institution as
  permissions land; the wall is built to look deliberate at any mix.
- **D-009 · no analytics ship.** PostHog was on every page of the SPA with no consent
  mechanism, on the same origin as our own privacy policy. The decision is open and its own
  recommendation is cookieless and EU-hosted, so nothing is loaded until it closes. This is
  the reversible direction.

### The provenance rule was amended, 2026-08-26 — read this before writing a source line

**Nandan:** *"Remove all the mentions of Virtual Lab production database. That's
ridiculous. Nobody puts that on a website. We are the ones claiming the data. Nobody cares
where it comes from. They're assuming we have access to our own data."*

**He is right and the rule is sharper for it.** A number resting on somebody else's
document carries that citation in the same visual unit. **A figure from our own operating
record carries nothing.** The totals band was the case that made it obvious: four cells
repeating *"Virtual Lab production database, August 2026"* across one row, plus a fifth
under the prose beside it. That is the provenance rule **performed rather than applied**,
and it actively devalued the one real citation on the page — *Donati & Rao, 2025*, under
the math — by making provenance look like a house style instead of an argument.

**Where the line falls is read from `CLAIMS.md`, never from the markup**, because whether
a claim is somebody else's is a fact about the claim and a page must not be able to talk
its way out of a citation. A register table whose fourth column is **`Definition`** says
how we computed a number from our own data and is exempt; one whose fourth column is
**`Source`** says where somebody else published it and is not. **It fails safe:** exemption
requires the `Definition` column, so anything unmarked, mis-parsed or newly added to a
`Source` table still demands its citation.

**A definition is not an attribution and was not removed.** The box plots keep their
caption lines — *"an active day is a study-day recruiting at least 20 respondents"*,
*"box: 25th to 75th percentile"* — because those tell a reader how to read the figure.
**The test: does the line say something about the number, or only about us?**

**Two fixtures pin the two halves**, and neither is sufficient alone:
`pass-own-record.html` (first-party, no source line, exit 0) and `fail-provenance.html`
(Donati & Rao figures, no source line, exit 1). **If both ever pass, citation has stopped
applying to anything.** Ten cases now, not nine.

Full statement in `DESIGN.md` §2; the register convention in `CLAIMS.md`; hard rule 1
above carries the short form.

### The 2026-08-26 review pass, in order — read before re-deriving any of it

**Each of these is Nandan's call, made looking at the built page, and three of them reverse
something a document recorded as settled.** They are cheap to undo and expensive to
re-argue.

| | |
|---|---|
| **Self-attribution, everywhere** | Removed. This is the provenance-rule amendment above — the biggest change in the session |
| **The four uncounted countries** | Off the map entirely, chrome and all |
| **Top navigation** | Gone; the mark and the one CTA remain |
| **The coverage prose** | *"Country figures cover 738,608 of the 841,660 respondents…"* — *"We dont need this."* A reconciliation between two internal denominators, on a section whose job is to show where the respondents are. **The region strip's caption said the same sentence and went with it** — keeping it there would have reinstated by the back door what was removed from the front. **C-097 is now published nowhere**; the row stays `VERIFIED`, like C-032 |
| **The coverage heading** | *"Where the respondents are"* → **"We have recruited in 41 countries:"**. It now **carries a claim** (C-017) where the old one deliberately carried none. Note the decided tension: the heading says 41, the map draws 37 |
| **The region strip's missing labels** | *"The bars per continent are missing the continents."* Names added, greedily placed on three baselines with leader ticks. **Names only, never values** — the bucketing still has no row |
| **The box plots** | *"beautiful but too small."* **Redrawn at 1160 units, not scaled up** — see below |
| **The figures' heading** | Split into **two sections**, one figure each. **Reverses the one-beat rule** COPY.md records from 2026-08-25 |
| **The client wall** | **Moved directly under the totals band.** The band says how much we have run; the wall says who trusted us to run it |
| **"There is no black box"** | Rewritten as **"The code is open source"** — two paragraphs and a GitHub link, anchor `/#code`. *"Those are really the only two points."* **Ethics left the site with it** — see below |

| **The recipe's closing sentence** | Cut. *"The median study takes 61 budget reallocations; the longest ran to 1,308."* **A third box plot is meant to replace it and is blocked on two numbers** — see below |

**~~One query is now the most valuable thing anyone can do to this repo.~~ Run, 2026-08-26 —
and the repo has production database access, which nothing here recorded.** `kubectl` is
configured against `gke_toixotoixo_europe-west1-b_toixo`, namespace `vprod`, and
`kubectl exec -n vprod gbv-cockroachdb-0 -- /cockroach/cockroach sql --insecure --database=vlab`
runs read-only SQL. **Every figure in this register can be re-derived rather than taken on
trust.**

The result: **p10 = 13, p25 = 28**, and every other value reconciled with what C-092 already
said — median 61, p75 165, max 1,308, 17,596 across 109 studies. That reconciliation is the
useful half: it confirms the `report_type` filter is right and the row had not drifted. The
third box plot is drawn and on the page.

**Two CockroachDB traps, now in `scripts/data/reallocations.json`:** `percentile_cont` needs a
**FLOAT** ordering column or it fails outright with *unknown signature*, and `count(DISTINCT …)`
still must not share a `SELECT` list with it.

**Superseded, kept because the reasoning still governs the next figure:** The recipe's
closing sentence is gone and its point is not: the honest axis for this work is **frequency,
not cardinality**, which is the framing C-093's note in `CLAIMS.md` exists to protect
(*"researchers juggling hundreds of ad sets"* is not supported — the median study has six
strata). A third box plot of **budget reallocations per study** is the replacement.

**It is blocked on p10 and p25, and nothing else.** C-092 carries median 61, p75 165, p90
351 and max 1,308; a box plot's box spans p25–p75 and its whiskers span p10–p90, so two of
the five values do not exist. Hard rule 2 forbids inventing either, so
`scripts/build-reallocations-figure.py` **exits 1 and names them.** The generator is
complete and has been dry-run against substituted values — geometry, wrapping, axis labels
and the axis guard all behave. `scripts/data/reallocations.json` carries the query and both
traps that have produced a wrong number here before.

**`index.html` carries no comments, so the wiring lives here.** Once `p10` and `p25` land:

1. `python3 scripts/build-reallocations-figure.py` — it exits 0 and writes
   `assets/figures/reallocations-box.svg`.
2. Add to `_data/inline.js`, beside the other two figures:
   `reallocations: read("assets/figures/reallocations-box.svg"),`
3. In `index.html`, inside the optimization section and **directly after the paragraph
   beginning "The price per stratum is not known in advance"** — that paragraph describes
   the loop, and this is how often the loop turns:

   ```
   <div class="figs">
     <figure class="fig">{{ inline.figures.reallocations | safe }}</figure>
   </div>
   ```

**Not beside the other two box plots.** Those answer the opening's questions — *how fast*
and *how much*; this one answers the recipe's, *what the work actually consists of*.

**Do not draw a variant that fits the data we have.** The three box plots are deliberately
one figure in three units, so a reader who learns to read one has learned to read all of
them. Inventing an asymmetric form for this dataset spends that to ship a week early.

**The rewrite costs one thing and it is worth naming.** *"There is no black box"* was six
terms and their definitions; four of the six are gone. Three of those cost nothing — the
CSV/API export is already said better in §2.4 in the reader's own terms, and Auth0 was a
vendor name doing no work. **The fourth was the IRB line, and ethics is now absent from the
site.** C-054 stays `VERIFIED` and unpublished. `DESIGN.md` §1's audience table lists ethics
among what the **priority-1 audience** — institutional buyers — needs from a page; four of
its five items are still there and that one is not. **If it returns it returns with its
scope attached** (the validation study described in the paper, and nothing else), and as a
third-party claim it **carries a citation** under §2 as amended.

**"Secure" is not written as an adjective anywhere in the replacement.** It is written as
*encrypted in transit and at rest* (C-051), because a vague security word is the sentence
§2's voice test throws out: could a reviewer ask us to substantiate this, and would we have
the citation?

**The box plots are the one to understand rather than copy.** "Full width" was implemented
by **redrawing the figures at W=1160 in the generators**, not by letting a 620-unit drawing
stretch. These SVGs carry their own type at absolute sizes — 13px labels, 15px numerals,
12px source lines — so scaling a 620 drawing across 1116 CSS px multiplies every one of
them by 1.8 and lands the axis labels between `h3` and `h2` on a scale `DESIGN.md` §4 fixes
exactly. Widening the viewBox keeps the type at its designed size and spends the room on
the ruler, which is where it is worth having. **1160 matches `STRIP_W`, so every full-width
drawing on the page is set out on one measure.**

**Two reversals worth their reasoning, because both look like inconsistency and are not.**
The one-beat rule was given when the plots sat side by side at 557px, where they read as a
pair *because they shared a line*; stacked at full measure, a compound heading was one
heading doing two jobs, and the pairing survives on form — same M3 interval, same M4 tick
rule, adjacent. And the coverage heading was written to carry no claim on the argument that
a heading stacked on artefacts that already speak is "looking for something to do" — true of
a heading with no claim in it, and not of one that states the fact the map illustrates.

### Part 2 was rebuilt 2026-08-26 — one list, two callbacks

**Four structures were mocked and reviewed before this was chosen**, and two earlier
attempts were rejected outright: splitting the list in half, and a two-column job-left /
answer-right layout. **Do not re-propose either.** The two-column one failed a specific
test — below 900px it collapses into the split-list version anyway, so it bought a desktop
affordance while spending the ink band and forcing the copy to fit a 320px column.

**The structure now:** one list of six steps, each carrying a **handle**, and the sections
after it point back with a **recap** of number and handle.

| | |
|---|---|
| **The list** | *What it takes to recruit respondents on social media.* Six steps: STRATA · ALLOCATION · PRICES · UNIQUENESS · INCENTIVES · FOLLOW-UP |
| **01–03** | *Those three are one optimization problem.* Ink band, recap, the two math blocks, `Donati & Rao, 2025` |
| **The paper** | *The method is published.* Byline, abstract quoted verbatim, the separation clause, SSRN link |
| **04–06** | *Those three are a chatbot survey platform.* Recap, prose, the M5 thread beside it, an eight-cell feature list |

**The handles must earn their keep**, and this is the rule to hold when editing: a handle is
decoration unless the copy uses it afterwards. If a section reads identically with the names
deleted, the list has grown a column for nothing. The band's closing line was rewritten to
*"Prices are not known in advance"* for exactly this reason.

**UNIQUENESS is not "one per person", deliberately.** The list says *person*; C-069 supports
per **account** only, and its scope note forbids writing it as fraud or duplicate prevention.
The neutral handle keeps the gap visible instead of quietly closing it.

**The step numbers carry `data-claim="none"`.** They are list counters. The predecessor used
a CSS counter and had no text node; these are real text and would otherwise report
`unannotated` — which is how they were caught.

### The ink band moved to the step list, and the paper folded into the math

**Two changes on 2026-08-26 that interact, so make them together or not at all.**

**The band moved.** Nandan: *"I suspect the recipe should be dark background."* §8 allows
**two bands per page, never adjacent** — this page's are the list and the footer — so the
math came off the band in the same change rather than the page growing a third. It reads
better both ways: the list is the pivot, the moment the page stops saying what we have done
and starts saying what the work *is*; and the equations are calmer on paper than reversed out
of ink, where two dense math blocks and a lattice fought for the same space. **On the band
the step list swaps every role to its inverted token** — `--ink-3` is 4.00:1 there and
`--ink` vanishes.

**The math was cut to one equation and one constraint, 2026-08-26.** The **sample bound**
(Σ n_h ≤ N_d) went — *"keep it just to a budget constraint as the only constraint"* — and so
did the **closed form** for n_h*. Both were true; both were in the way. The closed form was
the mathematically satisfying part and the least useful, and it **delayed the sentence the
section exists to reach**: that the price per stratum is unknown, has to be learned from the
running campaign, and that every estimate changes the allocation which changes what you learn
next. **That loop is the argument for software**, and it is stronger than the algebra that
was standing in front of it. Do not restore either block without a reason that outranks that.

**The paper folded in.** *"Let's combine the optimization problem and the read the paper into
one section."* They were two sections saying one thing: the math **is** the method, and the
paper **is** the math published. **Then flattened the same day** — *"make it one section
with the paper itself. So it's all one thing."* The first pass kept an `H3` behind a
hairline, which was still a seam; there is nothing for a seam to divide. One sentence carries
the reader across and the paper's own title is the only heading inside the section.
**`/#paper` sits on that title**, so the anchor lands on the citation and not on the
equations.

### C-066 was reversed, and this is how a ban gets lifted

**The photo capability was `WITHHELD` in the strongest terms this register uses** — *built,
then deliberately pulled*, citing a commit reading *"stop claiming we support it"*, and
naming itself **the limit of the forward rule rather than an exception to it**: *"Never
publish, in any form, until it is built."*

**Nandan lifted it on 2026-08-26** — *"Forget the ban"*, then *"or rather, update the
register."* That second message is the important one and it is the rule for next time:
**the register is changed in the same breath as the page.** A page that publishes what
`CLAIMS.md` withholds is the precise failure the register exists to catch, and
**`check-claims.py` would not have caught this one** — the claim carries no numeral, so
nothing mechanical was ever going to notice. C-066 is now `VERIFIED` with the reversal, its
date and its author recorded on the row.

**One edge is still open and it is a buyer's question.** The old row recorded that the file
itself is never stored and that what is kept is **a platform reference that expires**. So
*"a respondent can send a photo"* and *"you receive the photos"* are different claims, and
only the first is on the page. Confirm what a researcher actually receives before writing the
second anywhere — a buyer who expects files and gets expiring links has been misled by
omission.

### The paper is not the company's origin story, and three changes say so

**Nandan, 2026-08-26:** *"we don't want people to think we wrote the paper to start a
company. They're two separate things, and that needs to be understood."*

The misreading is that a paper was published and then monetised — academic-flavoured
marketing, which would discredit both halves. The true order is the opposite and C-018
carries it. Three changes, all the same point:

1. **The hero eyebrow went.** It read *SURVEY SAMPLING VIA AD PLATFORMS* — the paper's
   subject and very nearly its title. *"That's the name in the paper. Not the company."*
2. **The hero's "Read the paper" button went.** A CTA is a thing we want you to do, so the
   paper sitting beside *Request a proposal* made it one of two offers. **The SSRN link at
   the foot of the paper section stays** — a citation's destination is not a CTA.
3. **A clause after the abstract states the sequence:** *"The company did not begin with it:
   Virtual Lab has been fielding studies since February 2020, and the paper validates a
   method that was already running."*

**Note carefully what that clause does not claim, because both are easy to add by accident.**
Not independence of authorship — the byline directly above reads *Nandan Rao · Virtual Lab*,
so the company is in the paper and implying otherwise would be the very failure the clause
exists to prevent. And **not peer review**: `_data/paper.json`'s editions are an SSRN working
paper and a JMR *submission*. "Peer reviewed" is not ours to say.

### Two things came off the page the same day

- **The four uncounted countries.** *"If that's true, just leave them off entirely. Those
  are small details nobody cares about."* MD, MK, PS and XK had a dashed-outline state, a
  legend entry and a sentence of prose — **three pieces of chrome for four countries whose
  only property is that a query has not been run.** They are now dropped in
  `build-coverage-map.py` at collection, which matters: deleting the outline alone would
  have left them in `covered_ids`, which is what the ghost pass skips, so they would have
  rendered as **invisible holes in the world** and still framed the viewBox. They now fall
  through to the same hairline as every other country we have not surveyed, and the map
  states no country count in its label. **Not drawing a country is not calling it zero** —
  `coverage.json` still records all four and still says never render them as zero.
- **The top navigation.** *"It's okay if we don't have any top navigation. It's a one page
  site."* The bar carried *The paper* and *Audit trail*, two links that scrolled you down
  the page you were already on. What is left is the mark and the one CTA. **The anchors
  still exist** — `/#paper`, `/#code` — so a procurement reviewer or an academic has a URL
  to link; they are simply not advertised.

### Three bugs the build found, all fixed in the generator or the checker

**None was in the copy, and each had been shipping or would have shipped.**

1. **Both figure source lines were silently truncated.** `build-throughput-figure.py` and
   `build-adcost-figure.py` emitted each provenance line as one unwrapped `<text>` at 12px in
   a 620-unit viewBox, and an outer `<svg>` clips at its own bounds. The throughput figure
   stopped at *"Whiskers: 10th"* with no closing value; the ad-cost figure lost *"not our
   fee"* entirely — **the figures looked finished while failing the one rule they exist to
   demonstrate.** Both now wrap and grow the viewBox, and both **exit non-zero** on a word
   wider than the box, the same shape of guard as the axis one.
2. **The coverage legend's magnitude labels** carried no `data-claim`. This was already
   recorded as drift and the fix was already identified — in the generator, never the output.
   Done. It mattered more than it looked: on a page that annotates its own figures, an
   un-annotated numeral escalates from `unsourced` to `unannotated`.
3. **`check-claims.py` was scanning inputs instead of outputs.** Once pages became Eleventy
   templates, the bare walk read their `{# #}` comments — section numbers, motif ids — and
   reported ten findings that existed on no page. It now skips front-matter templates and
   `_includes/`, walks `_site/` when it exists, and **prints a note naming every template it
   skipped** so a skip is never silent. Ten fixtures still pass.

**One value was added to the register: C-097**, respondents attributable to a country,
738,608 of 841,660. It was already stated and sourced in `CLAIMS.md`'s per-country section but
had no id, so the one sentence `COPY.md` §1.3 requires could not be annotated. **Bookkeeping,
not a new claim** — and deliberately *not* a precedent for the regional totals, whose
objection is the bucketing.

### Two `DESIGN.md` corrections, made in the same change as the code

- **§8 client wall: three columns, not four.** The wall is now exactly six institutions; six
  in four columns leaves two dead cells, and a wall whose last row is half empty reads as a
  wall that lost two logos.
- **§10's 44px touch target and §8's 11px/19px button padding disagreed** — that padding
  computes to 42px. Neither number moved: `@media (pointer: coarse)` lifts block padding to
  12px, so the drawn button is unchanged and the floor is met where a finger is. **A pointer
  query, never a width query.**

### What the page does not have, and it is worth knowing

**None of the twelve §7 icons appears on any page.** The sprite is built, inlined and
resolving, and `COPY.md` calls for an icon nowhere. Forcing them in was tried and rejected:
the recipe's six beats and the old audit trail's six rows each had two or three items with no
icon in the set, and a half-iconned list is worse than a plain one. **This is a fact to
decide about, not a gap to quietly close** — either the copy grows a place for them or §7
covers a set the site does not currently use.

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
| `assets/favicon.svg`, `favicon.ico`, `apple-touch-icon.png` | **M1 from 2026-08-26** — the nav mark's nine cells on an ink tile, which is the footer lock-up cropped square. It was M2, and that is still why D-011 states a size threshold: the hatch does not survive below ~24px. **`favicon.svg` is the source; the other two come from `scripts/build-favicon.py` and are never hand-edited.** Geometry is chosen for the 16px grid — cell 8, gap 2, margin 2 in a 32 viewBox, so every cell is exactly 4 device px and every gap exactly 1. Nudging any of those four numbers reintroduces half-pixels |
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

`scripts/test-check-claims.py` runs **ten cases** over the fixtures in
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
| **D-014** | **The logos — now the only thing between the wall and marks.** The page is built and renders all six as type. Eight authentic files are in `assets/logos/`; **not one is cleared.** Every institution requires permission for third-party use, and World Bank, Harvard and WashU explicitly bar implying affiliation — which a logo wall is. WashU's own policy describes this exact case and allows **text only**. D-014 quotes each source. **The wall degrades to type, so the page ships regardless** |
| **D-025** | **May the privacy policy be amended?** *The policy is now carried over and live at `/privacy/`, unlinked, with `data-claim-scan="off"` on the legal copy.* Three things the instrument does are not described in it. Still open **even though the policy is now unlinked** — unlinked is not unamended |
| **SSRN edition** | **Which edition is posted?** The only compiled PDF we hold is the blinded submission with no byline. The page cites and links the paper, so if that is what was uploaded a reader gets an author-less document under a byline we printed. Ten seconds for him, unanswerable from here |
| **Region buckets** | The six regional totals still have no row because the bucketing is editorial. Fallback recorded: publish country figures, drop the regional layer |
| D-021 | Two motif rules; question 2 is live drift in `assets/mark.svg` |
| D-017 | Jobs posting |

**Closed in the 2026-08-25 session, so do not reopen them by accident:** the copy itself; the
sitemap (one page); C-094 to C-096 (the three universities, on operator knowledge); the walk
coming off the page; 6.1 p.p. becoming quote-only; and the client wall becoming marks rather
than type-with-engagements.

### Known drift — re-derived 2026-08-25 **after** the build

**`python3 scripts/check-claims.py` now reports ZERO findings**, for the first time since the
checker was written. It was 23 at the start of the 2026-08-25 build and 9 after it. The last
9 were the region totals, and they went not by being fixed but by being **decided**: C-098
gives the regional figures a row, so the artefact that had always failed now passes and
ships. **A clean bare run is the new baseline — if it is ever non-zero again, something
actually drifted.**

The twenty-three went three different ways, and the distinction is worth keeping:

- **11 in `index.html`** — the legacy SPA. **Retired**, not fixed, exactly as planned.
- **3 in `build/coverage-map.html`** — the legend's magnitude labels. **Fixed in
  `build-coverage-map.py`**, never in its output.
- **9 in `build/coverage-regions.html`** — the region totals. **Decided**, not fixed: C-098.

**The two pages that ship are clean**, and this is the invocation that says so:

```
npm run build && python3 scripts/check-claims.py _site/index.html _site/privacy/index.html
```

Eight values trace and carry their source lines; **one `warn`**, and it is the expected one —
the abstract's `$0.30`, shielded as attributed quotation and reported anyway, on every run,
per D-016.

`test-check-claims.py` — 10/10. `check-contrast.py` — 22 pairs, all pass.
`build-coverage-map.py` — clean, 41 countries, 6 regions. Both figure generators — clean.

**One limit of the checker, now that figures are on the page.** `check-claims.py` does not
scan text inside `<svg>`, so the two box plots and all three coverage artefacts are **not**
machine-checked. They carry their own `data-claim`, their own source lines and their own
axis guards, and the guards are what actually protect them — but do not read a clean run as
having verified them. It is also why the region strip passes while stating six figures that
have no row.

**Two rules that no checker can enforce, so they are yours to hold:**

1. **6.1 p.p. may appear only inside the quoted abstract.** C-003 is deliberately left
   `VERIFIED` rather than `WITHHELD`, because a withheld row bans its numerals at ±2% and
   **banning 6.1 would ban every bare `6` on the site**. See C-003.
2. **The client wall's names are verified; its logos are not.** A verified row licenses the
   relationship, never the mark.

**Still true and still worth knowing:** `build/` is generated and git-ignored — and is now
**regenerated on every deploy**, because `netlify.toml` runs the generator before Eleventy;
the generated artefacts have generators and **hand-editing one desynchronises the sprite**;
and `notes/` is nine workstream memos that are not a source of truth.

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

1. **The provenance rule.** Every number on the public site needs a `VERIFIED` row in
   `CLAIMS.md`, and **a number resting on somebody else's document carries that citation
   in the same visual unit** — same card, same weight as the label. If you cannot trace
   it from `CLAIMS.md`, it does not go on the page. This is the whole brand proposition;
   breaking it is the most expensive mistake available in this repo.

   **A figure from our own operating record carries no source line** (2026-08-26).
   Nandan: *"We are the ones claiming the data. Nobody cares where it comes from."*
   "Virtual Lab production database" under a Virtual Lab figure cites nothing a reader
   can check, and **printing it beside "Donati & Rao, 2025" devalues the real citation.**
   The line is read from the register, never from the markup: a table whose fourth column
   is **Definition** is ours and is exempt; a table whose fourth column is **Source** is
   somebody else's and is not. It **fails safe** — exemption requires the `Definition`
   column. Full statement in `DESIGN.md` §2; the two fixtures that pin both halves are
   `pass-own-record.html` and `fail-provenance.html`.

   **A definition is not an attribution.** The box plots keep their caption lines —
   *"an active day is a study-day recruiting at least 20 respondents"* — because that is
   what lets a reader read the figure. The test: **does the line say something about the
   number, or only about us?**

   **It does not reach `docs/` (D-029, 2026-08-29).** The provenance rule governs
   *claims* — figures offered as evidence for what Virtual Lab can do. Reference
   documentation asserts nothing: its numerals are JSON payloads, HTTP codes, timeouts
   and field weights. **The rule itself is unnarrowed** — a docs page stating an outcome
   figure is making a claim wherever it is printed, needs a `VERIFIED` row, and is scanned
   by naming the file.

   `python3 scripts/check-claims.py` enforces both halves of this rule. Pages declare
   their claims with `data-claim` (see `DESIGN.md` §8, "Claim annotation"); an
   un-annotated page is still scanned heuristically, but heuristic mode can pass a number
   by coincidence, so annotate. **Run `python3 scripts/test-check-claims.py` whenever you
   touch the checker, the register's status vocabulary, or a table's column names** — the checker is the rule, so a
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

7. **The site ships light; dark is dormant.** D-028 removed the
   `prefers-color-scheme` block, so an unstamped root — every page served — is light,
   and `:root` carries `color-scheme: only light` to stop Chrome's Auto Dark Theme
   re-tinting it on Android. The dark palette is kept and still contrast-checked, so
   give a new colour its dark value at the same time as its light one. Never declare a
   colour whose only definition sits inside a `[data-theme]` block — nothing on this
   site matches it.

8. **All graphics are inline SVG** built from the four primitives (bar, tick, cell,
   bracket). No icon fonts, no chart libraries, no raster illustration. If a needed
   drawing cannot be made from the primitives, that is a signal the concept does not
   belong on the page — raise it rather than reaching outside the system.

   **`docs/` is carved out, and only `docs/` (D-029, 2026-08-29).** Documentation carries
   39 UI screenshots, because a capture of the Fly dashboard **is** the documentation and
   there is no version of one made from a bar and a tick. `css/docs.css` mats every capture
   in a hairline so it reads as a specimen on the page. The ban holds everywhere else, and
   `.eleventyignore` still excludes `img/`.

9. **`/docs/` ships JavaScript. Nothing else does, and D-030 is the limit rather than the
   precedent.** One search script, `/docs/` only, no library, no CDN, one same-origin fetch
   on first focus, no cookie and no storage and nothing reported anywhere. **D-009
   (analytics) is still open and this does not touch it.** A second script is a question for
   the user, not a decision for you.

---

## Things about this repo you should not have to discover the hard way

- **The working directory is 244 MB; the repository is not.** `media/` — 226 MB of raw
  field photographs — is untracked and has never been committed, so it is also backed
  up by nothing. `.git` is 9.9 MB. Never `git add media/`, and see D-010 before adding
  anything else large.
- **~~The current site is a hand-rolled SPA.~~ Retired 2026-08-25.** It held every page as a
  `div`, switched client-side by Navigo 8 from unpkg. `index.html`, `css/main.css`,
  `css/normalize*.css` and `js/` are deleted; **all of it is recoverable with
  `git checkout <path>`** if something turns out to have been carried over wrong. Eleventy
  (D-006) replaces it.
- **~~There is a live BrowserSync `document.write` script tag~~ — gone**, with the SPA that
  carried it. It pointed at `http://HOST:3000` and had been shipping to production.
- **~~PostHog is loaded on every page~~ — no analytics ship at all** as of 2026-08-25. The
  snippet went with the SPA and nothing replaced it, because **D-009 is open** and its own
  recommendation is cookieless and EU-hosted. Loading nothing is the reversible direction;
  adding a tracker to a page that sits beside our privacy policy is not.
- **The privacy policy is genuinely good** and recently updated (2026-05-15). It is the
  one piece of existing content worth carrying over close to verbatim. Do not
  regenerate it; move it.
- **`build/` is generated**, git-ignored, and **regenerated on every deploy** —
  `netlify.toml` runs `npm run build`, which is `build-coverage-map.py` and then Eleventy.
  `_data/coverage.js` raises if it is missing rather than rendering an empty coverage
  section, which is the intended behaviour: a deploy should fail loudly, not ship a page
  with a hole where the map was.
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
- **`docs/` is content, not documentation-about-the-repo.** It is the 47-page public
  documentation set (D-008) — the only Markdown in this repo that is a *page*. The
  specification is the root `.md` files; `notes/` is the memos; `docs/` is the product.
  Its screenshots are in `docs/images/`, the only raster images published anywhere.
- **`docs/docs.js` is the only client-side JavaScript on the property** and is copied to
  the output verbatim — no bundler, no minifier, what you read is what runs (D-030).
- **`docs-search-index.njk` is at the repo ROOT for a reason.** Beside `sitemap.njk`, and
  for the same reason it is: it is a machine artefact, not a page. Moving it into `docs/`
  makes it inherit `templateEngineOverride: "md"` and emit JSON full of `<p>` tags.
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

- [ ] `python3 scripts/test-check-claims.py` passes — all **ten** cases, meaning the
      checker itself still works
- [ ] `python3 scripts/check-claims.py <the files you changed>` is clean — every number
      traces to a `VERIFIED` row and carries a visible source line in its own visual unit.
      **Name the files.** The bare command also walks `scripts/fixtures/`, which is nine
      pages built to fail, so it exits 1 by design and always will; the number to compare
      against is the one in "Known drift", not zero
- [ ] `python3 scripts/check-contrast.py` passes — **38 pairs** (22 until D-029 added the
      two grounds documentation introduces, `--surface` under code and `--sunk` under callouts)
- [ ] `python3 scripts/check-links.py` reports **9**, not 0 — every internal link, image
      and `#fragment` in `_site/` resolves except the nine screenshots that were never
      committed (`notes/ws-docs-screenshots.md`). Any other number is a regression
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
