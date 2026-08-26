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
| C-003 | Mean absolute deviation from gold-standard benchmarks | 6.1 p.p. | Donati & Rao, Fig. `MAD-comparison` — weighted; 6.2 p.p. unweighted. vs. GSS 2024, CPS 2024, Pew 2023 | `VERIFIED` | 2026-08-20 |
| C-004 | Cost per question per respondent (US) | **Not published** | Source contradicts itself: abstract says $0.30, Table `costs` and the Cost Considerations text compute $0.32 | `WITHELD` | 2026-08-20 |
| C-005 | US validation sample size | 1,500 | Donati & Rao, abstract | `VERIFIED` | 2026-08-20 |
| C-006 | Closer to benchmarks than a leading online panel (Prolific) | 6.1 vs 7.1 p.p. — ~15% better | Donati & Rao, Fig. `MAD-comparison` | `VERIFIED` | 2026-08-20 |
| C-007 | Closer to benchmarks than LLM digital twins | 6.1 vs 11.1 p.p. — >45% better | Donati & Rao, Fig. `MAD-comparison`; twins from Twin-2K-500 (Toubia et al. 2025) | `VERIFIED` | 2026-08-20 |
| C-008 | Prolific MAD, point estimate | 7.1 p.p. weighted (7.3 unweighted) | Donati & Rao, Fig. `MAD-comparison`. n=1,197, fielded Jun–Jul 2025 | `VERIFIED` | 2026-08-20 |
| C-009 | Digital-twin MAD, point estimate | 11.1 p.p. weighted (12.0 unweighted) | Donati & Rao, Fig. `MAD-comparison` | `VERIFIED` | 2026-08-20 |
| C-010 | Total respondents surveyed, all time | — | Production DB — see "Refreshing" below | `PLACEHOLDER` | — |
| C-011 | Typical field time | "typically two weeks" | **Unsourced — operator knowledge.** Needs a computed median before publishing as a number. | `PLACEHOLDER` | — |
| C-012 | Cost vs. gold-standard probability surveys | $0.32 vs $3.00 (GSS traditional) and $6.67 (GSS Follow-on) | Donati & Rao, Table `costs` | `VERIFIED` | 2026-08-20 |
| C-013 | Cost vs. Prolific | **We are ~3× more expensive** — $0.32 vs ~$0.10 | Donati & Rao, Table `costs` and Cost Considerations | `VERIFIED` | 2026-08-20 |
| C-014 | Advertising cost per participant, US study | $6.30 mean (range $0.70–$20 by stratum); $11.60 per participant including the $5 incentive | Donati & Rao, Cost Considerations | `VERIFIED` | 2026-08-20 |

### C-004 is `WITHHELD` — no cost-per-question figure goes on the site

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
| C-012 | $0.32 vs $3.00 / $6.67 per question | **Not as a paired figure.** The GSS side stands alone; ours does not. |
| C-013 | ~3× Prolific, $0.32 vs ~$0.10 | **Not as a paired figure.** The ratio stands; the operands do not. |
| C-014 | $6.30 advertising per participant, $0.70–$20 by stratum, $11.60 with the $5 incentive | **Yes, unaffected.** Per participant, not per question. |

So the cost section is built on **C-014**, with the C-012 and C-013 comparisons kept as
*ratios* sourced to the paper's cost table rather than as printed operands. The honest
framing C-013 exists to protect — that we are not the cheap option — survives intact,
because it was never the absolute figure doing that work.

### C-013 is the trap in this section

We are **cheaper than gold-standard probability surveys and more expensive than
Prolific** — roughly 3× more. Any copy implying we are the cheap option is false and is
contradicted by our own paper, in a table, in public. The honest framing is the one the
paper uses: comparable in cost to a convenience panel, closer to the benchmarks than one.

### C-006 and C-007 hold in aggregate, not in every domain

Aggregate MAD favors us. **By domain it does not, everywhere:** Prolific is closer on
internet use (6.7 vs 8.8 p.p.) and on attitudes to social issues (6.2 vs 7.0 p.p.), and
digital twins are closer on socioeconomic status (3.2 vs 5.0 p.p. — the paper attributes
this to employment status being baked into the twin personas). Trust is the weakest
domain for everyone; we are at 10.5 p.p.

Never write "closer on every measure." The paper's own phrasing is the ceiling: *at
least as representative as Prolific, and markedly closer than LLM digital twins.*

**On C-006 and C-007:** the comparative claim is the strongest asset the site has and
is stronger than the absolute one. "6.1 p.p. — closer than Prolific, closer than LLM
digital twins" belongs directly under the stat row, not buried in the paper page.
**As of 2026-08-20 the point estimates are verified** and can be published beside it.

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
| C-015 | People reached, all time | 1,097,153 | Distinct `userid` in `chatroach.states` — entered a survey, may not have answered. **NOT FOR PUBLICATION — use C-010.** Recorded only to explain why `states` exceeds `responses`. | `WITHELD` | 2026-08-20 |
| C-016 | Survey responses, all time | **17,979,910** | Row count, `chatroach.responses` | `VERIFIED` | 2026-08-20 |
| C-017 | Countries | **41** | Union of country targeting across both platforms, `vlab.study_confs` + `chatroach.campaign_confs` | `VERIFIED` | 2026-08-20 |
| C-011 | Field window, median | **14 days planned · 19 days actual** | Planned: `end_date − start_date` on the latest recruitment conf, n=137. Actual: first-to-last `adopt_reports` per study, n=116, IQR 8–90 days | `VERIFIED` | 2026-08-20 |
| C-018 | Operating since | **2020-02-13** | Earliest response in `chatroach.responses` | `VERIFIED` | 2026-08-20 |
| C-019 | Studies fielded, all time | **175** | 119 distinct `study_id` in `vlab.adopt_reports` (2022-07-29 → 2026-08-20) **+** 56 `chatroach.campaigns` rows. Definition settled by Nandan 2026-08-20 — see below | `VERIFIED` | 2026-08-20 |

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

### C-001 and C-002 are now the narrow claims

The paper's "over 33 studies across 23 countries" describes *studies in the paper*.
Production shows 41 countries and 175 studies. Both are true of different populations.
Use the paper's numbers only when citing the paper; use C-017 and C-019 for operating
scale. Any page that still reads "33 studies across 23 countries" as a scale claim —
the Studies index opener does — is understating the business and needs replacing.

---

## The paper, as a source

**Donati, D. and Rao, N., "Adaptive Survey Sampling via Ad Platforms."**
Dante Donati (Columbia Business School and CESifo) · Nandan Rao (Virtual Lab and
Universitat Autònoma de Barcelona).

Rows above cite the **July 2026** manuscript at
`../../survey-sampling-with-ads/paper/survey-sampling-with-ads-Jul2026.tex`. Two other
editions sit beside it (`JMR_submission_09152025`, `SSRN_09152025`) — **check which
edition a figure came from before citing a year on the public site.** The register
previously said "Donati & Rao (2025)"; the working manuscript is dated 2026 and the
submission 2025. Resolve the citation year against whatever is publicly linkable before
the Papers page ships.

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

---

## Studies referenced in mockups

Study-level figures used in the Phase 1 mockups were **illustrative**. Before any of
them appears on the live site, each needs a row here traced to the campaign config or
the production database.

| ID | Study | Figures used in mockup | Status |
|---|---|---|---|
| C-040 | Nigeria — HPV demand | n=2,400 · 8 strata · 11 d field time | `PLACEHOLDER` |
| C-041 | Serbia / Bulgaria — Bebbo parenting app | 2 waves · 2 countries · 4 mo follow-up | `PLACEHOLDER` |
| C-042 | Italy — Covid stereotypes | 542 municipalities · 90 provinces | `VERIFIED` — current site copy, from the working paper |

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

**C-008, C-009 — comparator point estimates.** In
`../../survey-sampling-with-ads/paper/survey-sampling-with-ads-Jul2026.tex`, Table 4.
Read the value, do not infer it from the abstract.

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
- **Per-country respondents** — join `vlab.inference_data` (distinct `user_id` per `study_id`) to the country extracted per study.

**C-040, C-041 — study-level figures.** Same access. Disclosure check still applies.

**Disclosure check before publishing any study-level figure:** sample sizes and field
timings for a named client may be covered by that engagement's confidentiality terms.
Verify per study; a figure being technically available is not permission to publish it.
