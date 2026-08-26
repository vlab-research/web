# Workstream: where the survey instrument goes

**Scope:** information architecture and page structure only. Brand naming and marks are a
second workstream; verified capability claims are a third. Dependencies on both are stated
in the last section and are **blocking**, not advisory.

**Status:** proposal, written to feed **D-024** (*How is Fly branded, and where does it live
on the site?* — OPEN, opened 2026-08-21, owner Nandan). Nothing here is decided. This is the
**site/IA study** of the three workstreams D-024 names; the other two write to
`ws-fly-capabilities.md` and `ws-fly-brand.md`, and where a question is theirs it is handed
back rather than answered.

**D-024 separates three tangled questions.** This document answers **question 2
(placement)** in full, takes a position on **question 3 (standing)**, and supplies one
structural constraint on **question 1 (naming)** without answering it. Direct answers are
collected in §11.

**A naming note that applies to this whole document.** D-024 asks whether "Fly" is a public
name at all, so writing it as one would pre-empt the brand workstream. Everything below
calls the thing **the instrument**, and the proposed page **‹Instrument›** — a placeholder
in angle brackets, never a recommended label.

**Constraint honoured throughout:** no figure appears anywhere in this document. Every
capability sentence below is **indicative copy**, marked as such, and is a description of
behaviour rather than a measurement. Where a number would be natural the text writes `—`
and the gap is listed.

---

## 0 · What the problem actually is

The site as specified in `CONTENT.md` explains, at length and well, **how a respondent is
recruited**. It says almost nothing about **what happens once they answer**, and nothing at
all about what a study can be *designed* to do.

Three places carry the whole of it today:

| Where | What it says | Words |
|---|---|---|
| Home §3, step **FIELD** | Channel (Messenger / WhatsApp / web form) and "the same thread reopens weeks or months later" | 2 sentences |
| `DESIGN.md` §6 M5 · Thread | "respondents are reached in a *conversation*… the same thread is still open four months later" | a motif, not a page |
| Platform page | nothing — it is an open-source / hosting / export page | 0 |

Everything else the instrument can do — assignment, timing, media, incentives, languages —
appears on the site **nowhere**.

**This is not a missing feature list.** `CONTENT.md`, "Content that should not survive",
already rules out the answer that suggests itself:

> The six-feature list (Recruit / Optimize / Survey / Retarget / Monitor / Secure) — a
> feature list is what you write when you do not know who is reading.

That rule is right and every structure below has to survive it. The gap is not "we have not
listed our features." The gap is that **a reader deciding whether their study design is
feasible here has no page to land on**, and the site has no surface that answers a
feasibility question at all. Everything on it answers a *proof* question.

---

## 1 · Does the sitemap change? Reading D-007 as written

D-007 settles **Home · Method · Studies · Platform · Papers · Privacy · Contact**. A change
is a reopening and has to be argued as one. So here is the argument, taken from D-007's own
text rather than around it.

**First, a correction to the brief's premise, in our favour.** The brief says a sitemap
change "is a reopening and must be argued as one." As of 2026-08-21 that is no longer quite
true: **D-007 has already been annotated**, and the annotation grants exactly the standing
this section was going to have to argue for —

> **Reopened in one respect, 2026-08-21: the count of seven is settled, its completeness is
> not.** D-024 asks where Fly … belongs on this site, **and one of the available answers is
> a page.** Nothing here is withdrawn … But do not cite "seven pages, settled" as a reason
> the question cannot be asked.

So the question is sanctioned and a page is named as an available answer. **What still has
to be argued is not permission but merit** — and the argument below is the one that does
that, so it is kept rather than shortened. Note what the annotation does *not* do: it does
not weaken D-007's reasoning, and per-study detail pages stay deferred untouched.

**D-007's rationale is not about the number seven.** Read it: every line of the rationale
is about *per-study detail pages*, and the reason is factual —

> `CLAIMS.md` has C-040 and C-041 as `PLACEHOLDER`, C-042 as the only verified study row…
> A detail page whose sample size, strata count and field time all render as `—` argues
> against us — on a site whose whole proposition is that its numbers are checkable, a page
> of blanks is worse than no page.

Seven is the **residue** of that argument, not a budget it defends. D-007 contains no
sentence arguing that the site should have few pages, that the nav is full, or that an
eighth page costs anything. What it defends is a **test**: *a page must not be a page of
blanks.*

**That test does not bite on an instrument page,** and this is the decisive point. A page
describing what the software does states **no figure at all**. There is nothing on it to
render as `—`, because its argument is not quantitative. D-007's own criterion, applied
honestly, admits it.

**The second test is the site's own page template**, in `CONTENT.md`:

> **Job:** one sentence. What this page is for. **If it needs two, it is two pages.**

That is the test that settles §2 below, and the site wrote it itself.

**So: yes, the sitemap should change, and the change is one line of the page inventory.**
It is carried by D-024 rather than by a fresh reopening of D-007, which is the cleaner route
and the one the record already lays out. Nothing in D-007's reasoning about per-study pages
is touched, and those stay deferred exactly as they are.

---

## 2 · What happens to the Platform page

**Platform's job, as specified:** *"prove there is no black box."* Audience: academic and
technical. Conversion action: **GitHub / docs**. Claims: C-050, C-051, C-052, C-053 — open
source, EU hosting, encryption, Auth0, export.

**An instrument capability list is a different page on all four axes.** Not "a different
emphasis" — a different reader, arriving with a different question, to be given a different
next step.

| | Platform, as written | An instrument page |
|---|---|---|
| **Question the reader arrives with** | *Can I trust what I cannot see?* | *Can my study be built here?* |
| **Reader** | Procurement / IT / security review; an academic replicator | A PI or an intervention designer costing a design |
| **What convinces** | The code is public and the data is theirs | The design they already have in mind maps onto the instrument |
| **Conversion** | GitHub, docs | **Request a proposal** (D-002 — we sell studies) |
| **Register** | Auditable. Verification. | Capability. Feasibility. |

**These do not belong on one page, and the site's own rules say so twice.** The template
says one job or two pages. Copy rule 1 says *"One conversion action per page. A page asking
for two things gets neither."* A merged page asks for GitHub **and** a proposal, and the
one-conversion rule is not a stylistic preference here — it is what stops the credibility
page from becoming a sales page, which is the exact failure mode D-002 exists to prevent.

There is also a plain reading failure. "Prove there is no black box" is an argument you make
by **subtraction** — here is everything, look at it, nothing is hidden. A capability list is
an argument you make by **addition** — here is more, and more, and more. Running them
together produces a page whose second half undermines the tone its first half establishes.
The reader who came to audit us is handed a brochure halfway down.

**Conclusion: Platform keeps its job sentence, unchanged, in every structure below.** It
does not grow. If anything it is the page that most benefits from the instrument content
going elsewhere, because the temptation to bulk it out disappears.

---

## 3 · Where the research-specific features land, and whether D-001 needs revisiting

**D-001 orders two audiences:** institutional buyers first, academic PIs second, on the
reasoning that *"both audiences need the same reassurance — that the sample is defensible —
and differ only in what counts as proof."*

Several instrument capabilities — seeds, watch-tracking, timeouts, image collection,
incentives — land hardest on audience 2, and on intervention designers, who the site does
not name.

**My answer: D-001 does not need reopening. It needs one amendment, and the amendment is
not about ordering.**

Three reasons, and the third is the one that matters.

1. **An intervention designer is a role, not a market.** The people who design an arm-based
   intervention are on staff at an M&E prime, a foundation, a UN agency programme team — the
   institutional buyers D-001 already puts first. Adding them as a third audience row would
   double-count the same organisations and would push the site toward a segmentation it does
   not have a sales motion for. D-002 is unaffected: they buy a managed study like everyone
   else.

2. **Reordering would be wrong on D-001's own reasoning.** D-001's ordering claim is about
   *what counts as proof*, and the intervention designer's proof standard is the same as the
   PI's — peer review and a published method. They are inside audience 2 for proof purposes.

3. **What D-001 is genuinely missing is a category, not a row.** D-001 says both audiences
   need *"the same reassurance — that the sample is defensible."* That is true and it is
   incomplete. **Before a reader cares whether the sample is defensible, they have to
   believe their study can be run at all.** Feasibility precedes proof. D-001 describes the
   site's *proof* architecture perfectly and is silent on feasibility, which is exactly why
   there is no page for it — the sitemap was derived from an audience model with one axis.

**Recommended amendment to D-001** — an added paragraph, not a re-ranking:

> Both audiences arrive with two questions, not one: *can this be done for my study*
> (feasibility) and *will the result hold up* (proof). D-001 orders the audiences; it does
> not order the questions. Feasibility is answered first because a reader who does not
> believe the study can be run does not evaluate the evidence. The ordering of audiences is
> unchanged.

**Where the features land, then:** on a feasibility surface, aimed at audience 2 in the
first instance, written so that an institutional buyer's programme lead reads it without
friction. Not on Home, which is audience 1's proof page. Not on Method, which is audience
1-and-2's *sampling* proof page.

---

## 4 · The three structures

Compared as wholes. Each table is the complete sitemap with the per-page job sentence, so a
change can be read against everything it sits beside.

Job sentences shown **in bold** are new or changed; the rest are verbatim from `CONTENT.md`.

---

### Structure A — "Seven, held"

No sitemap change. The instrument is distributed across pages that already exist, and depth
lives in `docs.vlab.digital`.

| # | Page | Job | Audience | Conversion |
|---|---|---|---|---|
| 1 | Home | Convince an institutional buyer that our sample is defensible, and that the claim is checkable rather than asserted | Buyer · PI | Request a proposal |
| 2 | Method | **Let a technical buyer or a PI satisfy themselves that the sampling is sound, and that the instrument can carry their design, before they ever contact us** | Both | Request a proposal |
| 3 | Studies | Show operating history in a form a procurement reader can scan | Buyer | Request a proposal |
| 4 | Platform | Prove there is no black box | Academic / technical | GitHub, docs |
| 5 | Papers | Be the citable landing page for the method | Academic | Download, cite |
| 6 | Privacy | Legal reference | Legal / procurement | — |
| 7 | Contact | Collect a brief good enough to price | Buyer | Submit brief |

**Changes:** Home §3 step 3 relabelled and rewritten (see §6 of this document). Method gains
one section, *"What the instrument can carry"*, after §3 and before Weighting. Platform
unchanged. A `.brass` link on both points at docs.

**What it commits us to.** That `docs.vlab.digital` is the capability surface, and therefore
that **D-008 becomes a launch dependency** — a marketing page cannot send a buyer to a
documentation site whose relationship to the company is undecided. It also commits Method to
two jobs permanently, because there is nowhere else for the content to go later.

**What it costs.**
- Method's job sentence needs a second clause, which is the exact thing the page template
  forbids. The bolded job above is what it has to become and it reads as a compromise.
- Method already runs seven sections. The instrument section lands as an eighth, at position
  four, between *"Stratifying on variables the platform does not have"* and *"Weighting"* —
  i.e. it interrupts the sampling argument in the middle to talk about something else, then
  returns to it. That is the structural cost and it is not cosmetic.
- No landing target. A "can you do video treatments with a three-month follow-up" enquiry has
  no URL to arrive at, so it arrives as a question in the Contact form and is answered by a
  human, every time.
- The instrument reads as an afterthought because structurally it is one.

**Decisions reopened:** **none by number, and this is its one real advantage.** It answers
**D-024** question 2 with "no page", touches no settled decision, and strains the
`CONTENT.md` page template and copy rule 1 without formally reopening a `D-`. It promotes
**D-008** from an open question to a launch blocker.

---

### Structure B — "Eight: the instrument earns a page" ✔ recommended

One page added, between Method and Studies. Platform's job sentence is untouched.

| # | Page | Job | Audience | Conversion |
|---|---|---|---|---|
| 1 | Home | Convince an institutional buyer that our sample is defensible, and that the claim is checkable rather than asserted | Buyer · PI | Request a proposal |
| 2 | Method | Let a technical buyer or a PI satisfy themselves that the sampling is sound before they ever contact us | Both | Request a proposal |
| 3 | **‹Instrument›** | **Let a researcher establish that the study they have in mind can be run in a conversation** | **PI · intervention designer** | **Request a proposal** |
| 4 | Studies | Show operating history in a form a procurement reader can scan | Buyer | Request a proposal |
| 5 | Platform | Prove there is no black box | Academic / technical | GitHub, docs |
| 6 | Papers | Be the citable landing page for the method | Academic | Download, cite |
| 7 | Privacy | Legal reference | Legal / procurement | — |
| 8 | Contact | Collect a brief good enough to price | Buyer | Submit brief |

**‹Instrument› is a placeholder label, not a proposal.** The brand workstream owns it — see
§8. Full draft spec in §7.

**The seam is clean and it is the one the site already has.** Method answers *who answers*.
‹Instrument› answers *what happens to them, and when*. Studies answers *what came of it*.
Platform answers *why you can believe any of it*. Four pages, four questions, no overlap —
which is more than the current seven can say, because Platform currently answers a question
no page asks it in that order.

**What it commits us to.**
- Eight pages to keep true, forever. One more surface where a claim can go stale.
- Naming the instrument publicly in nav — a decision that belongs to the brand workstream
  and that this structure forces to be taken.
- Capability claims entering `CLAIMS.md`. Every sentence on the new page needs a row on the
  **C-050–C-053 pattern** — non-numeric, `VERIFIED`, sourced to the repository. That
  precedent exists (C-052: *"Open source, self-hostable on Kubernetes + Helm"*), so this is
  not a new mechanism, but it is roughly a dozen new rows the claims workstream must produce.

**What it costs.**
- **D-007 is reopened**, narrowly. Argued in §1.
- **One nav link.** The nav today carries **four** links plus the CTA — Method, Studies,
  Platform, Papers (Home is the wordmark, Contact is the CTA button, Privacy is footer). Five
  plus a CTA is comfortable at `DESIGN.md` §5's 860px collapse point. This objection is
  smaller than it sounds and the count is the answer to it.
- **The feature-list risk is real and permanent.** A page of capabilities decays into
  Recruit/Optimize/Survey/Retarget/Monitor/Secure unless something stops it. The mitigation
  is written into the spec in §7 as a rule, not left to taste.
- **D-015 has to be re-read.** It recommends *"one screenshot, on the Platform page, never on
  the homepage."* If ‹Instrument› wants a screenshot — of a thread, or of a survey
  definition — that is either a second screenshot or a relocation of the one. Not a
  reopening; a scope question D-015's author did not have this page in view for.
- **A Privacy consequence, and it is the sharpest cost in this document.** See §9.

**Decisions reopened / touched:** **D-024** answered (questions 2 and 3). **D-007** page
inventory amended by one line — under the standing D-007 already grants, not as a fresh
reopening. **D-001** amended, not reordered (§3). **D-015** re-scoped. **D-008** downgraded
from blocker to recommendation — the page ships with an outbound link whatever D-008 decides
about shared shells. **D-002** explicitly *not* touched, and this is deliberate: conversion
stays "Request a proposal", so the page sells a study, not a licence. See §11 on D-024
question 3.

---

### Structure C — "Seven, traded"

Structure B, with Papers folded into Method so the page count stays at seven.

| # | Page | Job | Audience | Conversion |
|---|---|---|---|---|
| 1 | Home | Convince an institutional buyer that our sample is defensible, and that the claim is checkable rather than asserted | Buyer · PI | Request a proposal |
| 2 | Method | **Let a technical buyer or a PI satisfy themselves that the sampling is sound, and cite the paper if they want to** | Both | Request a proposal |
| 3 | **‹Instrument›** | **Let a researcher establish that the study they have in mind can be run in a conversation** | PI · intervention designer | Request a proposal |
| 4 | Studies | Show operating history in a form a procurement reader can scan | Buyer | Request a proposal |
| 5 | Platform | Prove there is no black box | Academic / technical | GitHub, docs |
| 6 | Privacy | Legal reference | Legal / procurement | — |
| 7 | Contact | Collect a brief good enough to price | Buyer | Submit brief |

**What it commits us to.** The citation, byline, verbatim abstract, BibTeX and link all
becoming a block at the foot of Method.

**What it costs.** More than it buys, and I do not recommend it.
- **D-016 was settled on 2026-08-21 — yesterday — after being reversed once.** It closes with
  *"if Nandan still wants Papers folded into Method, that is his to say."* That is an offer to
  him, not a lever for us, and **using it to balance an arithmetic count is the wrong reason
  to take it.** A decision that has already flipped once should not be flipped a second time
  by a workstream with no stake in it.
- The `data-claim-quote` mechanism (`DESIGN.md` §8, hard rule 1) is specified to appear
  **exactly once on the whole site**, on a page whose entire job is faithful reproduction.
  Moving it inside a page that also argues a cost position makes the shield harder to reason
  about, and the shield is enforced code, not prose.
- Method would carry three arguments — sampling, cost, citation — on a page already at seven
  sections.

**Decisions reopened:** **D-016**, plus everything Structure B touches.

---

## 5 · Recommendation

**Structure B.** The reasoning that decides it, in four steps:

1. **D-007 does not resist it, and as of 2026-08-21 it says so itself.** Its rationale is
   entirely about per-study detail pages and `PLACEHOLDER` figures; seven is an outcome of
   that argument, not a constraint it defends. Its own annotation now names a page as an
   available answer to D-024.

2. **D-007's own rejection test admits the page.** *"A page of blanks is worse than no
   page."* The instrument page states **no figure**. It has no blanks to render, because its
   argument is behavioural rather than quantitative — which also makes it the cheapest page
   on the site to keep true.

3. **The site's own template decides §2 for us.** *"Job: one sentence. If it needs two, it is
   two pages."* Platform's job is a trust argument converting to GitHub. The instrument's is a
   feasibility argument converting to a proposal. Two jobs, two readers, two conversions, two
   pages. Structure A's only way round this is to write Method a two-clause job sentence, and
   a spec that breaks its own template on the day it is written will not hold.

4. **The cost is one nav link on a nav that carries four.** Everything else Structure B is
   accused of — maintenance, brand exposure, claim rows — is work the capability content
   creates wherever it lands. Structure A does not avoid that work; it hides it inside
   Method and inside a documentation site whose status is an open decision.

**The one thing that would change this recommendation** is the claims workstream returning a
capability inventory that is thin — five or six items, none of them distinctive. A page needs
enough to be a page. If the inventory comes back short, **fall back to Structure A**, and
the Method section it proposes is the correct place for it. That is a real branch and it is
not mine to close: it depends on their output, not on this analysis.

---

## 6 · The mechanism spine: three steps, four steps, or two systems?

This is the highest-leverage question in the brief, and my answer is **three steps — the
count is right and the third step is wrong.**

**What is there now** (`CONTENT.md` Home §3, "How a sample is built"):

> **STRATIFY** — you define the population as a table…
> **OPTIMIZE** — each stratum gets its own ad set. Budget moves between them hourly…
> **FIELD** — Respondents answer in Messenger, WhatsApp, or a web form built for poor
> connections. The same thread reopens weeks or months later for a follow-up wave.

**Three observations, in the order they change the answer.**

**1 · The icon set has already answered this, and the copy drifted away from it.**
`CONTENT.md` Home §3 says *"icons from §7 (Stratify, Optimize, **Survey**)"* while the
labels read STRATIFY / OPTIMIZE / **FIELD**. `DESIGN.md` §7 names the third icon *Survey*
and draws it as **the thread** — the M5 motif, the one form §6 calls *"the one thing that
separates us from every panel provider."* **The design system already knows the third step
is the instrument.** The copy is the thing that reduced it to a logistics word. This is
existing drift, small, and fixing it is free.

**2 · Renaming FIELD → SURVEY is the whole structural change, and it costs nothing.**
"Field" is the verb of the sampling world — it describes the *act of running* a study and
says nothing about what the study *is*. "Survey" names the instrument. The step's copy
already talks about the instrument (channels, reopened threads); it simply is not weighted or
labelled as a stage of equal standing with the other two. Relabel it, give it the same
paragraph budget as OPTIMIZE, and append a tertiary `.brass` link to ‹Instrument›. **No new
section. No new ink band. Nothing comes off Home.** See §7's *Home consequence*.

**3 · Why not four steps, and why not two systems.**

| Option | Argument for | Why not |
|---|---|---|
| **Four: Stratify / Optimize / Survey / Follow up** | The reopened thread is genuinely a distinct moment in time, and M5 exists to draw it with a `+4 months` dashed rule | **A wave is a property of the instrument, not a stage beside it.** The first three steps are three different *systems* doing three different things; "follow up" is the same system running again. Splitting it makes the row asymmetric — three mechanisms and one repetition — and copy rule 2 (*lead with the mechanism*) is what exposes it: there is no fourth mechanism to lead with. The wave belongs **inside** step 3, where M5 draws it. |
| **Two systems: a recruiter and an instrument** | Honest about the architecture. It is genuinely two pieces of software with two jobs, and it would give the instrument equal billing at the top of the page | **It sells two products, and D-002 says we sell one thing.** *"We sell studies. The open-source platform is the credibility engine — not the thing being purchased."* A buyer reading "two systems" on the homepage is being asked to evaluate an architecture, which is the software-vendor framing D-002 rejects. It also breaks the sentence the site is built on — *"You set the target distribution. We reallocate ad budget hourly until the achieved sample matches it"* — which is one continuous mechanism, not a handoff between two products. **Reopening D-002 is the price and the price is too high.** |

**The recommendation, stated as the rule a future agent should follow:**

> Home §3 stays **three steps**, because a study has three stages and the reader is being
> shown a study, not an architecture. The third step is renamed **SURVEY**, takes the §7
> *Survey* icon it was always specified to take, and carries the instrument at the same
> weight as the other two. The reopened thread is drawn **inside** step 3 with M5, not
> promoted to a fourth step. The two-systems framing is available if D-002 is ever reopened
> and is not available before then.

**One knock-on for the brand workstream.** If the instrument ships under a product name,
whoever writes step 3 will be tempted to make the label the product name. **Do not.** The
three labels are verbs describing what happens to a sample; a proper noun in the third slot
breaks the parallelism and asks the reader to learn a name before they have learned the
mechanism. The product name, if there is one, belongs in the step's prose and in the page,
not in the step label and not in nav — see §8.

---

## 7 · Draft page spec — ‹Instrument›

**In the `CONTENT.md` per-page template. All copy below is INDICATIVE — it exists to show
the shape and register of each section, and every sentence of it must be replaced or
confirmed by the claims workstream before a word is built. No figure appears anywhere; where
one would be natural the text writes `—` and the gap is listed at the end.**

---

## ‹Instrument›

**Job:** let a researcher establish that the study they have in mind can be run in a
conversation.
**Audience:** academic PI and intervention designer (audience 2, per D-001 as amended in §3
of this document) · institutional programme lead second.
**Conversion action:** Request a proposal. **One only** — per D-002 and copy rule 1, this
page does not convert to GitHub, to docs, or to a sign-up. The docs link is a tertiary
`.brass` link in the close, never a button.
**Components used:** hero (no readout) · thread diagram (M5) · two-column capability prose ·
one ink band · CTA. **Ink bands: one, plus the footer — at the §8 limit, never adjacent.**
**Claims used:** `—` · **entirely dependent on the claims workstream.** Expected shape is the
C-050–C-053 pattern: non-numeric capability rows, `VERIFIED`, sourced to the repository. See
§8.

### Sections, in order

**1 · Lede** — paper ground, no figure.

> *INDICATIVE*
>
> **eyebrow** THE SURVEY INSTRUMENT
>
> # The survey runs inside a conversation, and the conversation stays open.
>
> Respondents answer in Messenger, WhatsApp, or a web form built for poor connections —
> whichever the study calls for. The thread is not a delivery channel that closes when the
> last question is answered. It is where the study lives for as long as the study runs.

*Why this and not a channel list: the channels are the least interesting true thing on the
page, and leading with them makes the instrument sound like a chatbot vendor. The persistent
thread is the structural fact everything below depends on, so it is stated first and the
channels arrive inside it.*

**2 · Assignment** — arms and seeds.

> *INDICATIVE*
>
> ## Arms are assigned from a seed, so the assignment reproduces.
>
> Randomisation is seeded, which means the arm a given respondent was assigned to can be
> regenerated exactly, by us or by anyone holding the seed and the code. Assignment is a
> property of the study definition, not of a run.

*This section is deliberately first among the capabilities, and the reason is brand rather
than feature ranking: a seeded assignment is the same proposition as the rest of the site —
checkable rather than asserted. It is the one instrument capability that argues in the site's
own voice. If the claims workstream can substantiate it, it earns the top slot; if it cannot,
this section is cut and section 3 leads.*

**3 · What can be delivered, and what comes back**

> *INDICATIVE*
>
> ## A treatment can be delivered in the thread, and watching is recorded.
>
> Video is delivered in the thread rather than at a link, and the platform records what was
> watched — a behavioural measure alongside the self-report, on the same respondent, in the
> same session. Images, audio and documents are delivered the same way.

*Do not turn this into a media-format list. The argument is that the instrument produces a
second class of measurement, not that it supports several file types.*

**⚠ One capability from the brief was removed from this section, and it must not be
reinstated without a `CLAIMS.md` row.** The brief lists *image collection* among Fly's
capabilities. `docs.vlab.digital/fly/reference/questions/` documents the opposite under
*"Upload (receiving files from respondents)"*: Fly **records that a photo was sent and does
not store the file**, and the platform reference expires after roughly a week on WhatsApp
and a month on Messenger. **Sending** media to a respondent is fully supported; **collecting
and retaining** it is documented as not supported. This is a capability question and belongs
to the claims workstream — but it is written here because a sentence claiming respondent
image collection would be a **false capability claim on the public site**, which is a
larger failure than a missing one. Until that workstream rules, this page says nothing about
respondent-submitted media.

**4 · Time** — the ink band. M5 thread motif with the dashed `+ N months` rule.

> *INDICATIVE*
>
> ## A study is not one sitting.
>
> Questions can wait. A response window can be held open, a follow-up can be scheduled days
> or months out, and the same thread reopens where it left off — the respondent does not
> re-enrol, re-consent to a new instrument, or start again.

*This is the ink band because it is the section that separates the instrument from a form.
**The visual vocabulary already exists and does not need inventing** — D-024 records that
`DESIGN.md` §6 M5, the thread, "already describes Fly", and that it is the one motif the
system permits a radius above 2px. §6 M5 is specified for exactly this — "a dashed rule with a `+4 months` label
conveys the longitudinal point." **The label on the dashed rule must be a real interval from
a real study or it must be omitted:** M5 is a motif, but an interval printed on it reads as a
measurement. Until the claims workstream supplies one, draw the rule unlabelled.*

**5 · Incentives**

> *INDICATIVE*
>
> ## Respondents can be paid in the thread.
>
> Incentives are disbursed through the platform — small payments and mobile top-ups —
> without asking a respondent to leave the conversation, create an account, or supply bank
> details.

*Ties to a fact the site already publishes: `CONTENT.md` Method §5 states the US validation
study's `$5` incentive (C-014). **Do not restate that figure here** — it is a study cost, not
an instrument capability, and copy rule 6 in `DESIGN.md` §2 forbids the same figure appearing
twice in different framings. This section carries no figure at all.*

**6 · Language**

> *INDICATIVE*
>
> ## The instrument runs in the respondent's language.
>
> An instrument is authored once and fielded in multiple languages, so a multi-country study
> is one design rather than several.

*The natural figure here is a count of languages and it is `—`. See the gaps list. A count is
also the weaker sentence: "one design, several languages" is a design fact a PI can act on;
"N languages" invites the reader to check whether theirs is on the list.*

*This is also **the one section with no documentation to link to.** Multilingual behaviour is
real and is spread across five separate documentation pages with no page of its own — see
§10. Every other section here has a stable deep-link; this one has none, so its prose has to
stand alone.*

**7 · Close** — paper ground.

> *INDICATIVE*
>
> ## Tell us the design and we will tell you whether it runs.
>
> `[Request a proposal]`
>
> `Instrument documentation →`  ← tertiary `.brass` link, not a button

### The rule that stops this becoming a feature list

**Written into the spec deliberately, because taste will not hold it.** `CONTENT.md` already
bans the six-feature list. This page is one bad edit away from becoming it. Three rules:

1. **Every section answers a design question a researcher actually arrives with**, and is
   ordered by how early in a study design that question comes up. It is not ordered by
   subsystem and it is not ordered by impressiveness.
2. **Every heading is a declarative sentence stating a mechanism** — never a noun phrase, and
   never a rhetorical question (`DESIGN.md` §2 rule 7). "Arms are assigned from a seed" is a
   heading; "Randomization" is a feature-grid cell.
3. **No icon grid.** The moment these six sections become six §7 icons in two rows, the page
   has become the thing `CONTENT.md` deleted. The §7 icons appear on this page **only** in the
   Home mechanism-step sense, i.e. not at all.

### Open questions

- **The page name and the nav label** — brand workstream. See §8.
- **Every claim on the page** — claims workstream. Nothing here is `VERIFIED`.
- Whether section 2 (assignment) survives, which decides the section order.
- Whether D-015's single screenshot moves here or a second is permitted.
- The Privacy consequence in §9, which is a gate on sections 3 and 5.

---

### Home consequence — what comes off Home to make room

**Nothing, because nothing is being added.** Home stays at **nine sections and two ink
bands**, unchanged: hero · totals band · how a sample is built · **validation (ink band)** ·
coverage (paper) · studies · client wall · close · **footer (ink band)**. Bands at positions
4 and 9, four sections apart, §8's never-adjacent rule holds exactly as D-019 records it.

**The whole Home change is inside §3, step 3:**

- Label **FIELD → SURVEY**, taking the §7 *Survey* icon the section was already specified to
  use — this closes existing drift rather than creating change.
- The step's prose grows to roughly the length of the OPTIMIZE step and names what the
  instrument does, at the level of the mechanism. `—` figures throughout; the detail is on
  ‹Instrument›.
- One tertiary `.brass` link at the end of the step block. Not a button — Home has one
  conversion action and it is *Request a proposal*.

> *INDICATIVE — replaces the current FIELD paragraph*
>
> **SURVEY**
> Respondents answer in Messenger, WhatsApp, or a web form built for poor connections. The
> instrument can assign arms from a seed, deliver a video in the thread and record what was
> watched, pay an incentive, and run in the respondent's language. The same thread reopens
> weeks or months later for the next wave.
>
> `How the instrument works →`

**Explicitly rejected, and recorded so it is not re-proposed:**

- **A tenth section for the instrument.** Home is at its documented limit and the section
  would sit between coverage and studies, breaking a run the D-019 order was argued into.
- **A change to the hero.** The hero deck is three sentences and `CONTENT.md` records **two**
  drafts already rejected from it. The hero sells the differentiator, and per D-001 the
  differentiator for audience 1 is the sampling. The instrument makes the sample *usable*; it
  is not what makes it *distinctive* to the primary reader. **This is a judgment and it has a
  trigger for revisiting:** if the claims workstream substantiates a capability that is
  genuinely unavailable elsewhere, the hero deck is worth re-opening on that specific
  sentence. Not before.
- **Promoting the instrument to an ink band.** Third band. Breaks §8.

**If more Home presence is ever wanted, there is exactly one removable section and it is not
mine to remove.** Home §6 — the single study card — is already flagged in `CONTENT.md` as
fragile: it renders `—` in the field-time cell that `DESIGN.md` §8 calls load-bearing, and
`CONTENT.md` itself records Nandan's two ways out, one of which *"removes this card from Home
and leaves the client wall carrying the track-record slot alone."* **If that resolution goes
the second way, a section frees up on Home.** That is a live question with an existing owner
(C-043) and this workstream should not touch it.

---

### Platform page — unchanged, plus one line

Job sentence, audience, conversion action, claims and all four bullets stay **exactly as
`CONTENT.md` has them**. Two additions only:

- A tertiary `.brass` link to the documentation site, alongside the GitHub link. Consistent
  with its stated conversion action, which is already *"GitHub / docs"* — the docs half of
  that has no link today.
- A note in the spec: **capability content does not go here.** Written down so the next agent
  looking at a short page does not bulk it out with the instrument list, which is the exact
  failure §2 argues against.

---

## 8 · Dependencies on the other workstreams

**Stated as blocking. This workstream cannot close any of them.**

### On the brand workstream

1. **The page name.** ‹Instrument› is a placeholder. The candidates and what each costs:
   *Instrument* (fits D-003's "instrument-grade" temperature exactly; slightly abstract on
   first read), *Survey* (plainest, but collides with the step-3 label recommended in §6 and
   with the word "survey" used generically all over the site), *the product name*.
2. **My one IA position on naming, and it holds whatever they decide: the nav label is a
   function, not a product name.** A reader scanning nav who does not already know the
   product name cannot tell what the link is for, and a nav is the one place on a site where
   a reader will not spend a second guessing. The product name can carry the page — heading,
   prose, docs — while nav says what it is. This is a structural argument, not a branding
   preference, which is why it is stated here rather than deferred.
3. **Whether the platform is named publicly at all.** This is upstream of the whole
   structure: if the answer is that the site never names a product, Structure B still holds
   (the page is *The survey instrument*) but every heading on it changes.
4. **Step 3's label** on Home §3 — recommended SURVEY, and recommended **not** to be a proper
   noun (§6).

### On the claims workstream

1. **Every sentence on the ‹Instrument› page needs a `CLAIMS.md` row.** The pattern to follow
   is **C-050–C-053**, which are already non-numeric capability rows sourced to the repository
   and the privacy policy. Roughly a dozen new rows are implied. This is the largest single
   dependency and the page cannot be built without it.
2. **Incentives: the distinction is settled by the documentation, but the wording is not.**
   `docs.vlab.digital/fly/reference/incentive_payments/` documents it as a **software**
   capability that integrates **four named third-party disbursers** — Reloadly (mobile
   top-up), DingConnect (airtime, data, utility), Tremendous (gift cards), and a generic
   HTTP endpoint. So it is an ‹Instrument› section, not a Method one, and section 5 of the
   spec stands. **What the claims workstream still owns** is whether the public page names
   those providers. Naming them is more specific and therefore more on-brand; it also
   publishes a supply-chain fact with a privacy consequence (§9) and pins us to vendors we
   may change. Recommend describing the capability without naming providers on the marketing
   page, and letting the documentation carry the names — but that is their call, not mine.

3. **The instrument is authored in Typeform, and a page about "the survey instrument" must
   not misrepresent that.** `docs.vlab.digital/fly/reference/creating-a-survey/` documents
   surveys as imported from Typeform (or authored in Excel and uploaded). Nothing in the
   draft spec claims otherwise, and nothing in it should start to — a reader who arrives
   expecting a form builder and finds an import step has been misled by our page, not by the
   product. **Recommend the page describe what the instrument *does* and stay silent on
   where questions are typed**, which is a documentation matter. Flagging it because it is
   the most likely place for well-meant copy to invent a capability.
4. **Is any capability genuinely unavailable elsewhere?** The answer decides the hero
   question in §7 and nothing else. Note the constraint it runs into: **D-023 forbids
   comparison with another recruitment source**, so even a substantiated uniqueness claim
   cannot be published as *"unlike panels…"*. It could only be published as a plain statement
   of what the instrument does, which is what the spec already writes.
5. **The gaps, where a figure would be natural and none exists.** Every one renders `—` today
   and none may be estimated:
   - Number of languages supported — `—`
   - Countries or networks where mobile top-ups can be disbursed — `—`
   - Payment ceiling or floor per respondent — `—`
   - Maximum follow-up interval, or the longest one actually fielded — `—`
     *(needed for the M5 dashed-rule label in section 4; until it exists the rule is drawn
     unlabelled)*
   - Number of studies that used arms, video, or media — `—`
   - Video length or file-size limits — `—`
   - **Not a gap but a contradiction, and higher priority than any of the above:**
     **respondent image collection.** The brief lists it; the documentation says the file is
     not stored. One of the two is wrong and the page cannot be written until it is settled.
     See the ⚠ note in section 3 of the spec.
6. **Two capabilities need a check against `DESIGN.md` §6's banned list before they are
   drawn**, not before they are written: the watch-tracking section will attract a play-button
   or a timeline graphic, and the incentive section will attract a coin. §6 bans *"funnels
   narrowing to a coin"* and names the coin as **the banned thing**. Any figure on this page
   is built from the four primitives or it is not built.

### On neither workstream — mine, and unresolved

**‹Instrument› carries no figure, so `check-claims.py` has almost nothing to check on it.**
That is a comfortable position and a slightly false one: the page will be the site's largest
body of unverifiable-by-script assertion. The checker enforces the provenance rule for
numbers; capability sentences pass it silently. **Worth raising with Nandan as a small
process question** — whether a page of non-numeric claims needs a review step the script
cannot provide.

---

## 9 · One consequence that is not an IA question but is created by this IA

**Publishing the capability list makes the Privacy page visibly incomplete, and `CONTENT.md`
forbids fixing it.**

`CONTENT.md` says Privacy is *"carried over near-verbatim"* and that *"the only permitted
edits are structural."* The policy's §2.2, *"From participants"*, lists what is collected:
platform identifiers, survey responses, message metadata, consent records, limited profile
data. It does **not** mention:

- **Images submitted by participants.** Nothing in §2.2 covers respondent-supplied media.
- **Video engagement telemetry.** Recording *what was watched* is behavioural data about a
  participant and is not "message metadata such as timestamps, message direction, delivery
  status, and chatbot state."
- **Incentive disbursement.** §2.2 states *"we do not ask researchers to collect, and we do
  not knowingly process, payment card data or government identifiers"*, and §5, *How we share
  information*, names Google Cloud, Auth0 and connected messaging/advertising platforms —
  **no payments processor or top-up provider appears anywhere in the document.** The
  documentation names four: **Reloadly, DingConnect, Tremendous, and a generic HTTP
  endpoint.** Disbursing a mobile top-up requires sending a phone number to a third party
  for a purpose the policy's §2.2 does not describe and to a recipient its §5 does not list.
  This is the sharpest of the three and it is already true today, whether or not we publish a
  page about it — publishing the page is what makes it visible.

**Why this is in scope for an IA workstream.** The site's entire proposition is that its
statements reconcile with each other. A marketing page describing a data-collection
capability that the company's own privacy policy does not list is precisely the class of
contradiction this documentation set exists to prevent — and it is discoverable by any
procurement reviewer, who is audience 1.

**Recommendation, and it is a gate on sections 3 and 5 of the page spec, not on the
structure:** the privacy policy is reviewed against the verified capability inventory
**before** those two sections publish. Either the policy is updated by whoever owns it, or
those capabilities are described at a level the policy already covers. `CONTENT.md`'s
"structural edits only" rule would need relaxing for the first, which makes it Nandan's, not
ours. **Sections 1, 2, 4, 6 and 7 are unaffected and can proceed.**

---

## 10 · `docs.vlab.digital` — how much of the job is already done

**Recommendation only. D-008 is OPEN and is Nandan's.**

### What is actually there

`docs.vlab.digital` is **live, current, and much larger than the open decision assumes.**
It is a Hugo site on the stock `hugo-geekdoc` theme, deployed to GitHub Pages by a GitHub
Action, with **45 markdown files and roughly 3,100 lines of content**, last substantively
extended **2026-08-18** — three days ago. It documents **two products**: `/fly/` (the survey
instrument) and `/vlab/` (the recruitment optimiser).

**It is written for researchers designing surveys, not for developers or self-hosters.**
There is no installation page, no architecture page and no environment-variable reference
anywhere in it; the instructions are "open the dashboard, click this tab, paste this JSON",
illustrated with product screenshots. That matters for D-008 more than the shell question
does: the docs are already addressing the same person the ‹Instrument› page is for.

### Coverage against the capability list in the brief

| Capability | Documented? | Deep link |
|---|---|---|
| Timeouts / delayed follow-up | **Yes, thoroughly** — absolute, relative and variable timeouts, plus the >24h messaging-window problem | `/fly/reference/timeouts/`, `/fly/reference/questions/` |
| Incentive payments | **Yes, thoroughly** — four disbursers, plus a full worked tutorial | `/fly/reference/incentive_payments/` |
| Randomisation with seeds | **Yes** — assignment, multiple independent seeds, and the formula to reconstruct assignment in analysis | `/fly/reference/seeds/` |
| Video delivery with watch-tracking | **Yes, and recently rewritten** — the recorded playback events are enumerated | `/fly/reference/questions/#videos` |
| Media delivery (image, audio, document) | **Yes** | `/fly/reference/media/` |
| Image **collection** from respondents | **Documented as not supported** — see §7 ⚠ | `/fly/reference/questions/` |
| Multilingual | **Partial — the weakest area.** Real, but spread across five files with **no page of its own** and no walkthrough | — |
| Instrument authoring generally | **Yes — the single richest page in the repo**, ~25 question types with examples | `/fly/reference/questions/` |

**Anchors are stable and the URL structure mirrors the content tree**, so deep-linking from
a marketing page is viable today, without touching the docs repo.

### So: how much of the job is done?

**The reference half is done, and it is better than what this workstream could produce.
The positioning half does not exist at all and cannot be delegated.**

Three findings, in order of how much they change the calculus:

1. **There is no overview, landing or positioning page anywhere in the docs.** The root
   `_index` is twelve lines: two one-line product descriptions and a "work in progress,
   please contribute" link. The two section indexes are bare table-of-contents shortcodes.
   Nothing in the repo answers *what this is for* or *why you would choose it* — every page
   answers *how do I do X*, written for somebody who has **already decided to use the
   product**. That is exactly the content the ‹Instrument› page has to supply, and it is why
   *"just point at the docs"* is not on its own an answer.

2. **The register is a genuine mismatch, and it runs in our favour on quality.** The
   2026-era pages are markedly good — second person, plain English, explicit failure modes.
   *"You upload a file, you copy the URL it gives you back, and you paste that URL into your
   survey. That is the whole feature."* That cadence is close to `DESIGN.md` §2's voice
   already. But it is **procedural**, and procedure answers a question the marketing reader
   has not asked yet. **The marketing site writes the *why*; the docs keep the *how*.** That
   division is clean and it is what makes Structure B cheap: the ‹Instrument› page can be
   short, because everything it would otherwise have to explain is one link away.

3. **The visual and origin mismatch is real, and it is what D-008 is actually about.** Stock
   geekdoc, a 40-line CSS override that only changes header colours, a different origin,
   a different generator, a different deployment. A reader clicking through from the
   marketing site experiences a visible context switch.

### Recommendation on D-008

**The recorded recommendation — "shared nav, separate shell" — is still right, and this
work strengthens it rather than changing it.** Two additions:

- **Do not attempt to fold the docs into the Eleventy site.** They are 45 files on a
  maintained Hugo theme with search, a generated sidebar and a working CI deploy. D-006
  already put this out of scope; nothing found here argues for reopening it. **Adopting the
  docs would put the site's largest body of prose inside a repo governed by `CLAIMS.md`**,
  and the docs are full of illustrative values that would fail `check-claims.py` on sight.
  That is a much bigger consequence than the shell question and it should be stated before
  anyone proposes a merge on aesthetic grounds.
- **The cheapest version of "shared nav" is a link and a logo, and it is worth doing.** The
  docs already carry the Virtual Lab logo. A single back-link to `vlab.digital` in the docs
  header, plus consistent outbound links from Method, ‹Instrument› and Platform, delivers
  most of what the recommendation is reaching for at near-zero cost.

**What this does to the structures in §4.** It is the reason Structure B downgrades D-008
from a blocker to a recommendation: the ‹Instrument› page is a *positioning* page that links
out for detail, so it works whether or not the shells are ever unified. **Structure A does
not have that property** — it pushes the capability content itself onto the docs, which
means the docs would have to grow a positioning layer they do not have, in a repo that is not
governed by `CLAIMS.md`. That is a second, quieter argument for Structure B, and it only
became visible once the docs were actually read.

### One thing to hand to whoever owns the docs

**The two capability gaps found here are documentation gaps first and marketing gaps
second**, and closing them in the docs is cheaper than writing around them on the marketing
site:

- **Multilingual has no page.** It is a real capability, referenced in five places, walked
  through in none. It is also the one ‹Instrument› section with no link to offer.
- **Image collection.** Whatever the truth is, the marketing site and the documentation must
  agree before either says anything.

Neither is this workstream's to fix, and neither is in this repo.

---

## 11 · Direct answers to D-024's three questions

D-024 asks three questions and warns against reading them as a shortlist of answers. Taken
in the order that makes them answerable — **standing decides placement, and placement
constrains naming** — not in the order they are listed.

### Question 3 · Standing — *does Fly sit on the proof side of D-002, or move the line?*

**Neither. It sits on the other side of a line D-002 draws but does not name, and D-002
holds unchanged.**

D-002 says: *"We sell studies. The open-source platform is the credibility engine —
transparency, no black box — not the thing being purchased."* That sentence was written with
**one** piece of software in view: the optimiser. Two are actually in play, and they do
opposite jobs.

| | The optimiser | The instrument |
|---|---|---|
| What it is to a buyer | **Proof.** You can audit how the sample was built | **Scope.** It is what the study you are buying can contain |
| What being open buys us | Everything — it is the whole credibility argument | Little; a PI does not audit a questionnaire runtime |
| If it were closed | The site's proposition collapses | Nothing much changes |

**The instrument is not the credibility engine and should not be sold as one.** It is a
specification of the deliverable — the answer to *what can be in the study I am
commissioning*. That places it on the **managed-service** side of D-002, with Studies and
Method, not on the proof side with Platform and Papers.

**So D-002 is not reopened, and the test of that is the conversion action.** The ‹Instrument›
page converts to **Request a proposal**, like every service page on the site. The moment it
converts to GitHub or to a sign-up, it has become a product page and D-002 *is* reopened.
**Recommend D-002 gain one clarifying sentence** — that "the platform" in it means the
recruitment optimiser, and that the survey instrument is part of the service being sold, not
part of the proof — because the ambiguity is what let the gap open in the first place.

**One consequence worth stating plainly, because it is the most likely objection.** This
answer means the site will describe capabilities of software it is not selling as software.
That is normal for a managed service and it is what Method already does for the optimiser.
The guardrail is the conversion action, and it is a single line in the spec.

### Question 2 · Placement — *a page, Platform, Method, or a thread through several?*

**A page.** Structure B, argued in §1–§5. In short:

- **Not Platform** — different reader, different question, different conversion; the site's
  own template and copy rule 1 both say two jobs is two pages (§2).
- **Not Method** — Method's job is that the *sampling* is sound. The instrument is not
  sampling, and inserting it makes Method interrupt its own argument to talk about something
  else and then resume (§4, Structure A).
- **Not a thread through several pages** — that is Structure A's real shape and it produces
  no landing target, so every feasibility enquiry arrives as a question in the Contact form.
- **And also a thread**, in one specific place: **Home §3 step 3**, which is renamed and
  rewritten but adds no section and no band (§6, §7).

### Question 1 · Naming — *public product name, internal name, or described but unbranded?*

**Not mine, and I am not answering it.** The brand workstream owns it. One structural
constraint from this side, which holds whichever way they go:

> **The nav label is a function, not a product name.** A reader scanning a nav who does not
> already know the product name cannot tell what the link is for, and a nav is the one place
> on a site where nobody spends a second guessing. A product name can carry the page —
> heading, prose, docs — while the nav says what it is.

And one knock-on the brand workstream should be handed: **the Home §3 step label must not
become a proper noun** (§6). The three labels are verbs describing what happens to a sample;
a product name in the third slot breaks the parallelism and asks the reader to learn a name
before they have learned the mechanism.

---

## 12 · What must not happen next

**`AGENTS.md` and `CONTENT.md` both now say it, and this document does not create an
exception to it:**

> Do not add a Fly page, a Fly name, or a Fly claim to any document before this decision
> closes.

**Nothing in this file is copy.** Every quoted block is marked *INDICATIVE* and exists to
show the shape and register of a section so the structure can be judged. **None of it may be
lifted into `CONTENT.md`**, and no capability sentence in it is publishable — none has a
`CLAIMS.md` row, one of them (respondent image collection) is contradicted by our own
documentation, and the page it belongs to does not exist as a decision yet.

**The order of operations, if Structure B is taken:**

1. Nandan closes **D-024** — standing, placement, naming.
2. The claims workstream produces capability rows on the C-050–C-053 pattern. **The page
   cannot be drafted before this**, because its sections are its claims.
3. The privacy review in **§9** runs against that inventory. It gates two sections of the
   page, not the structure.
4. `D-007`'s page inventory gains one line; `D-001` gains the feasibility paragraph in §3;
   `D-002` gains the clarifying sentence in §11; `D-015` is re-scoped.
5. `CONTENT.md` gains the page spec and the rewritten Home §3 step 3.
6. `DESIGN.md` §7's icon list and `CONTENT.md` Home §3 stop disagreeing about whether the
   third step is called *Survey* or *Field* — the smallest item on this list and the only
   one that is a pure bug fix.
