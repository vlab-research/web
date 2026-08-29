# Workstream memos

Working notes from parallel investigations. Each memo is a record of **how a question was
looked into** — the evidence found, the options weighed, what was recommended.

**None of this is a source of truth.** Precedence is unchanged and absolute:

> `DESIGN.md` wins on visual and voice · `DECISIONS.md` wins on scope and direction ·
> `CLAIMS.md` wins on facts · `CONTENT.md` holds the copy.

A memo loses to all four. If a memo and a governing document disagree, the document is
right and the memo is stale — **do not "fix" the document to match the memo.**

## Why they are kept

Because the reasoning is worth more than the conclusion. `DECISIONS.md` records what was
settled and why in a few paragraphs; these hold the working — the options that were tried
and rejected, the numbers that were computed, the sources that were read. When someone
proposes reopening a settled decision, the memo is usually where the answer already is.

They are also the evidence behind **D-024** (Fly), which **closed on 2026-08-21**. Three of
them were commissioned specifically to inform it, and the decision states where they
disagreed rather than averaging them.

## What is here

| Memo | Question it investigated |
|---|---|
| `ws-fonts.md` | Self-hosting the type kit (D-012) |
| `ws-icons.md` | Drawing the §7 icon set, the mark and the favicon from the four primitives |
| `ws-claims.md` | Designing `check-claims.py` and the `data-claim` convention |
| `ws-coverage.md` | Rebuilding the region strip and totals into the coverage generator |
| `ws-paper.md` | Mining the manuscript; citation year; verifying every paper-sourced claim |
| `ws-positioning.md` | The MENA concentration question; decision packets; the Home page |
| `ws-fly-capabilities.md` | What Fly actually does, verified against source and docs |
| `ws-fly-brand.md` | How the two technologies should be named and marked |
| `ws-fly-ia.md` | Where Fly lives in the sitemap |
| `ws-designs.md` | Whether there is a surface for study designs, and how it relates to Studies — **briefly settled as D-026 and demoted the same day** |
| `ws-privacy-reconciliation.md` | The privacy policy read clause by clause against the capability register — the gate D-024 set on two sections of the instrument page |
| `ws-seo.md` | What one page can and cannot win in search, and where the budget goes instead |

## Several are already superseded — check the date before trusting a recommendation

Memos are written at a moment and are not updated when a decision lands afterwards.
Known cases, all written **2026-08-20**:

- **`ws-positioning.md`** treats C-004 as `STALE` and C-019 as unpublishable. Both were
  settled later that day: C-004 is `WITHHELD`, C-019 is `VERIFIED` at 175. It also argues
  for a *three*-cell totals band and then for four; the settled answer is four, with the
  study count (D-020).
- **`ws-paper.md`** predates D-023 and discusses publishing the comparison against Prolific
  and digital twins. That comparison is withheld. It also reports the paper path as wrong;
  it is not — see `CLAIMS.md`, which anticipates that mis-resolution.
- **`ws-positioning.md` §1.4** names the wrong four countries in one draft position and
  carries its own correction notice further down. The corrected list is NG · JO · IQ · BD.

**The `ws-fly-*.md` memos are now partly superseded, and in the two places that matter they
were overruled by each other.** D-024 closed on 2026-08-21 and is the answer:

- **`ws-fly-brand.md`** recommends Fly be named *"once, in a heading on the Platform page"*
  with nothing in nav. **The page won.** Its Option C is otherwise the settled decision —
  name Fly, cite the recruitment side, no mark, no colour, radius as the signature. It also
  places Fly *inside* the credibility engine; **the IA memo's reading was taken instead** —
  Fly is scope, on the managed-service side of D-002.
- **`ws-fly-ia.md`** defers naming to the brand workstream and writes every capability
  sentence as *INDICATIVE*. **None of that indicative copy is the copy** — `CONTENT.md`
  holds the page, written against the register. Its fallback branch (*"if the inventory
  comes back thin, fall back to a Method section"*) never triggered: twenty rows.
- **`ws-fly-capabilities.md`** drafts C-056–C-077 and is the closest to source of the three.
  Two of its rows were changed on Nandan's rulings: **web forms are sayable** at the study
  level (C-057), and **the forward rule** — pages may run 2–3 months ahead of live features —
  moved data-bundle and utility top-ups from `PLACEHOLDER` to publishable (C-062). Its
  §2.7–2.8 comparative material stays `WITHHELD`; the forward rule does not reach a
  measurement nobody has taken.

**`ws-docs-screenshots.md` is not a workstream memo and is the one exception here.** It is a
capture plan carried over from the old docs repo when D-008 folded it in — the six `bails-*`
screenshots that `docs/fly/reference/bails.md` references and nobody has taken. It is here
rather than in `docs/` because it is instructions for a person, not a page. It stops being
needed the day `scripts/check-links.py` reports 0.

## The rule for adding one

A memo goes here when it holds reasoning a future reader would otherwise have to redo.
It does not go here to record a decision — that belongs in `DECISIONS.md`, and a memo
that is really a decision in hiding is how this directory would start competing with the
documents it is subordinate to.
