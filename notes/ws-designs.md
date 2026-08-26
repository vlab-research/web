# ws-designs — a surface for study designs

**Workstream memo, 2026-08-22. This was briefly written into `DECISIONS.md` as a settled
decision (D-026) and was demoted the same day.** It is reasoning, not a decision — see
`notes/README.md`. **There is no Designs page, because there is no sitemap.**

**Why it was demoted, recorded because the mistake is worth not repeating.** It was closed on
a conversational *"this makes sense to me"*, which is thinner than a sitemap decision
deserves, and it was a **placement** question answered before any narrative existed. Nandan,
2026-08-22: *"The purpose of this pass was to brainstorm content ideas and research. It was
not to define what the end story is."* He is right, and the same criticism reaches the
eighth page and the seven before it.

**What survives, and it is most of the memo:** the analysis of how a designs surface relates
to Studies, the argument that a pattern is the transpose of an engagement, the observation
that only a pattern can carry a failure, the four candidate patterns, and the rule that a
design earns its slot by having been run. **All of it is input to the narrative pass. None of
it assigns anything to a page.**

The claim rows it produced — **C-084–C-088** — stay in `CLAIMS.md`. They are facts about work
we have done, they were verified, and they do not depend on any structure.

---

## The proposal, as it was written

*Kept verbatim below, including its "settled" framing, so the reasoning can be read as it
was made. **It is not settled.***

### Study designs as a surface

**Nandan, closing it:** *"We have a designs page. It can be called study designs… The whole
idea is there is method. There is technology. And with those tools, we create various
designs, and we want to talk about them."*

**That sentence is the decision and it is also the site's spine.** It is recorded in
`DESIGN.md` §1, because it is structure rather than a rationale for one page:

> **There is a method. There is a technology. And with those tools we build study designs.**

- **Method** — adaptive sampling. Ours. The paper is about it.
- **Technology** — the optimizer and the instrument. Ours. Fly is the named half (D-024).
- **Designs** — what a researcher builds with both. **Theirs**, which is why the page
  describes them rather than selling them.

**This is what answers the objection the page had to survive**, which was that *Method* and
*Designs* read as synonyms. They do not, once the site says the relationship out loud: one is
**how we draw a sample**, the other is **what you can build once drawing it is solved.**

#### What the page is

**Ninth page, after Instrument, converting to *Request a proposal*.** Job: *let a researcher
see the shape of a study they have not yet imagined, and recognise their own in it.*
Audience 2 first — PIs and intervention designers — with an institutional programme lead
reading it without friction.

**A fixed set of design patterns, never a stream.** No dates, no post list, no "latest".
Each pattern states the mechanism, what it makes possible, and the study we ran — cited where
the study is public, described without figures where it is not.

> **The rule: a design earns a slot when we have run it.** However good an idea is, it is not
> on this page until it has been fielded. This is `CLAIMS.md`'s discipline applied to method
> instead of to numbers, and it is the whole of what separates the page from an agency's
> "insights" section.

**Four patterns is the cap** until a fifth has been run.

#### Why a page and not a section on Studies

**Because Studies is already a designs page cut on the wrong axis for this reader.** Its
cards state *"population, design, and instrument"*, and every card drafted for it is a design
description. The two surfaces are transposes of one dataset:

| | **Studies** | **Study designs** |
|---|---|---|
| One entry is | an engagement | a pattern |
| Answers | *have you done this before?* | *what could I do?* |
| Reader | procurement, scanning for their scale and region | a PI recognising the shape of their own study |
| Ordered by | client and geography | mechanism |
| Figures | **central** — and the reason detail pages are deferred | **absent** — a pattern is described, not measured |
| Grows | one row per engagement, forever | barely; a pattern absorbs many studies |
| Can carry a failure | **no** | **yes** |

**A pattern is what several studies have in common.** Three consequences, and the third is
the one that decided it:

1. **No duplication to manage.** Neither surface owns the other's axis. One dataset, two
   views — D-019's reasoning about the map, applied to the study material. Each pattern names
   the studies that used it; each card can name its pattern. Entered once in `_data/`, which
   is what D-006 and D-007 already assume.
2. **D-007's figures problem does not travel.** Per-study detail pages are deferred because
   their sample sizes and field times are `PLACEHOLDER` and uncleared. **A pattern states no
   figure**, so the deferral does not reach it — the same reason the Instrument page was
   admissible, and per-study pages stay deferred untouched.
3. **It is the only surface that can carry a failure.** A procurement card reading *"this one
   did not work"* is incoherent; operating history is the page's job. But *"a cluster trial
   could not separate weak content from insufficient reach, so we ran a second,
   individual-level trial that guaranteed exposure"* is the most credible paragraph on the
   site. That is a **pattern**, not a study card. **This argument did not appear in the
   original recommendation and it is the strongest one.**

A section on Studies was the cheap alternative and fails the one-job rule — *"Job: one
sentence. If it needs two, it is two pages"* — which is the argument that moved the
instrument off Platform three decisions ago. Taking it here and refusing it there would make
the rule a preference.

#### The label — settled as `Designs` in nav, "Study designs" on the page

Nandan's words were *"it can be called study designs"*, and that is the page's title. **The
nav label is the shorter one, for a reason found on inspection rather than by preference:**
`Study designs` sits two items from `Studies` in the nav, both begin with the same five
letters, and a reader scanning a nav does not read to the end of a word. `Designs` has no
such collision, and D-024's rule is satisfied either way — it is a function, not a product
name.

**What carries the Method/Designs distinction is the page openers, not the labels.** A nav
label that needs a second word to be understood is already failing; the three-part frame in
`DESIGN.md` §1 is what makes the pair legible, and it has to be audible on Home and on both
pages.

#### The cost, recorded because it will be felt later

The site now aims **three** pages at audience 2 — Instrument, Study designs, Papers — against
four at audience 1, and nav carries **six links plus the CTA**, which is about the most §5's
860px collapse point holds comfortably. **If a page has to come off, the candidate is
Papers**, whose fold-into-Method question D-016 explicitly left open. Not proposed, and not
to be actioned by anyone but Nandan — recorded so the trade is visible when it is forced
rather than discovered then.

#### Sequencing — decided now, built last

**Not a Phase 4 blocker, and this one genuinely is not.** The eight other pages do not depend
on it and it can be added without rework. It is also the page whose content depends on
clearances we do not hold: **every named study needs D-007's per-engagement disclosure
check.** The malaria paper is public and citable; the others are not, on current information.
**Build it last, and ship it with the patterns whose evidence has cleared** — a page of two
patterns is a page; a page of four unclearable ones is not.

#### The claim rows this creates

**Design-pattern claims are a new kind for the register** — neither a figure nor a
capability, but a statement about work we have done. The closest precedent is C-042, a study
row sourced to a working paper. **C-084–C-088** were added when this closed; the pattern rows
carry their clearance status in the Source cell, and **a pattern whose row is not clear does
not ship, even though the page around it does.**

---

