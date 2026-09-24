# Inbound — turning the database into answers people search for

**Written 2026-09-23**, in one session with Nandan, after read-only exploration of both
production databases. It supersedes nothing in `ws-seo.md`; it is the step after it. The
decisions this session took are in **D-032**. This memo is the working behind them.

**A memo loses to all four documents** (`notes/README.md`). Every number below is
**exploration, not a claim** — none has a `CLAIMS.md` row, several are known to be
contaminated (§5), and none may be copied onto a page.

---

## 1 · What was decided in this session

| | Nandan, 2026-09-23 |
|---|---|
| **Scope** | Digital inbound tools only. **Conferences are a separate path** — flagged, not planned here |
| **The goal** | *"Converting our data into something valuable for the world. Something that people would really ask."* Cost is the lead question — *"It's different per country, and we can answer it per country, which is great for SEO"* |
| **Confidentiality** | **Not a constraint on this work.** *"I have no reason to believe that my clients are overly concerned about people learning about things from their study."* See D-032 for exactly what this does and does not lift |
| **Country pages** | Yes, and they should work for AI answer engines as well as search |
| **A handbook / guide to recruiting online** | Yes. Where it lives is open (§3) |
| **Sequence** | **Pilot two countries first — Nigeria and Bolivia**, one many-study country and one one-study country, so the page is tested at both ends of the range. Look at both, then decide what to build (§7) |

---

## 2 · The universe of content, by the reader's moment

Every surface answers a question a buyer has **at a particular moment**. Organise by that,
not by format.

| Moment | The reader's question | Layer | State |
|---|---|---|---|
| Feasibility / budget | *Can I reach this group in this country, how fast, for how much?* | **Reference data** — country pages, region pages, benchmarks, later an estimator | New |
| Design | *How do I do this properly?* | **Handbook** — the practice of recruiting online, for someone who has not chosen a tool | New |
| Execution | *How do I set up strata / a WhatsApp survey in your software?* | **Docs** — `/docs/`, 47 pages | Exists |
| Proof | *Is this rigorous, who has used it?* | **Evidence** — the paper, methods notes from the database, case studies | Paper only |
| Adoption | *What do I paste into my grant?* | **Kit** — methods-section boilerplate, budget justification, how to cite | New |

Two machine-facing layers under all of it:

- **Open data** — `/data/`: the pooled figures as CSV/JSON, versioned, ideally with a DOI.
  **The single source every country page, the JSON-LD and any estimator are generated
  from** — the `coverage.json` pattern, extended.
- **Agent access** — the MCP server, which already exists (`/#agents`). An agent can act,
  not just read.

Plus a **glossary**: short definitional pages (strata, target distribution,
post-stratification) that the handbook links to. Definition pages are what AI answers lean on.

---

## 3 · Handbook and docs — recommended separate, cross-linked (OPEN)

**Recommendation: `/handbook/` as its own section, on the same shell as `/docs/`, not a
section inside it.** Not decided.

- **Different reader.** Docs serve someone who chose us; the handbook serves someone who has
  chosen nothing. A sidebar of *bails, shortcodes, seeds* loses that reader.
- **Citability.** A neutral guide is cited — by people and by AI — far more than a manual.
- **The links are the conversion.** Every chapter ends *"Doing this in Virtual Lab →"* into
  the relevant docs page; docs link back to the handbook for the why.

**Borrowed from:** PostHog (Handbook and Guides separate from Docs), Stripe (Guides
separate from the API reference), and — closest to our audience — **J-PAL's Research
Resources**, neutral per-topic methods pages development researchers already use.

**A draft chapter list:** when ad recruitment is right, and when it is not · strata and a
target distribution · budget and sample size · ads: targeting, creative, language ·
channels: Messenger, WhatsApp, web form · incentives · consent, ethics, IRB · data quality ·
weighting and analysis · follow-up waves and panels · reporting your method.

**One constraint to resolve before chapter 1 is written:** D-023 bans comparison with
another recruitment source *in our own voice*, and a handbook naturally wants to say when
panels are the better choice. Needs a rule.

---

## 4 · Writing for AI answer engines — the rules

Each is tied to something already true of this repo.

1. **Every sentence stands alone.** Engines lift sentences out of context. *"Virtual Lab
   has recruited N respondents in Nigeria since 2023"* survives extraction; *"we've
   recruited N here"* does not.
2. **Facts in HTML text, never only in SVG.** `ws-seo.md` §4.2: today every country name on
   the site is inside SVG, where crawlers barely read it. **Every chart gets a data-table
   twin.**
3. **Answer first.** Headings are the questions people type (*"How much does it cost to
   recruit survey respondents in Nigeria?"*); the first paragraph answers.
4. **Every figure carries its date and its definition inline** — *"as of September 2026"*,
   *"advertising spend, not a price"* — because context is exactly what extraction strips.
5. **One source of truth.** Page, JSON-LD and downloadable CSV generated from one data file.
   JSON-LD is outside `check-claims.py` (`ws-seo.md` §4.1), which is why it must be
   generated, never typed.
6. **Schema:** `Dataset` on country pages and `/data/`; `Article` on handbook chapters.
7. **Cheap and unproven:** Markdown twins and `/llms.txt`. Worth the hour; there is no
   evidence the major crawlers use them, so they are not the plan.
8. **Already right:** `robots.txt` admits every crawler including AI ones; Eleventy serves
   static HTML with no JavaScript needed to read it.

---

## 5 · What the database can answer

Explored read-only, 2026-09-23. Two databases (`CLAIMS.md`, "Refreshing the placeholders",
has the access line): **`vlab`** (current platform, studies and configs, 2022→) and
**`chatroach`** (the older platform, and **every response from both**).

### 5.1 · Where each thing lives

| Data | Location | Shape |
|---|---|---|
| Studies | `vlab.studies` | 203 rows; `slug`, `org_id` |
| Study config | `vlab.study_confs` | Append-only; take the latest row per `(study_id, conf_type)`. Types: `strata`, `recruitment`, `general`, `destinations`, `variables`, `audiences`, `creatives`, `data_sources`, `inference_data` |
| Strata | `conf_type='strata'` | List of `{id, metadata, facebook_targeting, question_targeting, quota}`. `id` is e.g. `Gender:Women,Division:Dhaka,Age:Age all`; **country is in `facebook_targeting.geo_locations`** |
| Recruitment settings | `conf_type='recruitment'` | `start_date`, `end_date`, `budget`/`budget_per_arm`, `destinations`, **`incentive_per_respondent`** (newer studies only) |
| Daily ad delivery | `vlab.recruitment_data_events.data` | Facebook Insights, `campaign → stratum → {spend, impressions, reach, cpm, cpc, ctr, unique_clicks, actions[]}`, per day |
| **Price per stratum** | `vlab.adopt_reports`, `report_type='FACEBOOK_ADOPT'` | Per stratum: `current_participants`, **`current_price_per_participant`**, `lifetime_spent`, `desired_percentage`, `current_percentage`. 117 studies. **The richest single source for "what does it cost to reach group X"** |
| Cost and respondents over time | `adopt_reports`, `cost_over_time` / `respondents_over_time` | Daily series, 47 studies |
| Respondent variables | `vlab.inference_data` | One row per user × variable: `Gender` (65 studies), `Age` (43), `State`, `Division`, `City`, `Location`, `education`, `language`… **Case varies by study** (`Gender` / `gender` / `Genders`) |
| Responses | `chatroach.responses` | 18.2M rows, question by question: `shortcode`, `question_idx`, `timestamp`, `platform` |
| Final state per respondent | `chatroach.states` | `current_state`: END 470k · QOUT (screened out) 420k · BLOCKED 165k · ERROR 41k. `platform` recorded for ~60k (messenger 45k, whatsapp 15k) — **NULL for most**, which historically means Messenger |
| Older-platform price per stratum | `chatroach.adopt_reports` | 51 campaigns, `{budget, goal, price, respondents, spend}` per stratum — **spend in ad-account currency, see 5.3** |

### 5.2 · Questions, and whether we can answer them

| Question | Source | Answerable? |
|---|---|---|
| **What does it cost to recruit in [country]?** | Insights spend + respondents | **Yes**, ~20 countries on the current platform |
| **What does it cost to reach [women / older / rural] there?** | `FACEBOOK_ADOPT` price per stratum | **Yes — the headline finding.** E.g. one recent study: men $5.55, women $9.31 |
| How long does it take? | Daily respondents | Yes, every country |
| Who did we reach, versus target and versus census? | `inference_data` + strata `quota` | Target: yes. Census: needs external data (UN WPP), cited as **Source** |
| Completion and screen-out rates | `chatroach.states` | Yes, with work to attribute states to studies |
| Where do people drop off; how long is too long? | `responses.question_idx` | Yes |
| Follow-up wave response | Responses across waves | Yes |
| Time of day people answer | `responses.timestamp` | Yes, easily |
| Messenger vs WhatsApp | `states.platform`, `recruitment.destinations` | Partial, mostly recent |
| Does an incentive help, and how much? | `incentive_per_respondent` | Thin — **but an experiment is live in the LAC healthy-diets programme** (Argentina, Bolivia, Honduras; Argentina's creatives cross incentive framing with Messenger/WhatsApp). A methods note in waiting |

### 5.3 · Traps found — each would put a wrong number on a page

1. **Currency.** Spend is recorded **in the ad account's currency**, not dollars. Older
   platform: India comes out at "$4,649 per respondent" — that is rupees. **It also happens
   on the current platform:** the `cohort-2-pilot*` studies in Nigeria show ~$15–28k spend
   on 9 respondents and `incentive_per_respondent = 4000` — naira. Every spend figure needs
   the account currency and a conversion at the spend date. Account currency is available
   from Meta (`vlab` MCP `meta_adaccounts`).
2. **Shared campaigns → double-counted spend.** Several studies point at the same campaigns
   (`test`, `fly_test`, `cohort-2-pilot-3/4` all ~$24.8k). `ad-cost.json` already dedupes:
   campaigns under more than one `study_id` are dropped.
3. **Umbrella studies → double-counted respondents.** Identical respondent counts across
   sibling studies (`short-a-hpv-nigeria` / `short-b-hpv-nigeria` both 3,727;
   `hpv-nigeria` / `hpv-nigeria-scale-up` both 1,319). Assign each respondent to one study
   first — the `throughput.json` and `ad-cost.json` queries already do.
4. **Test and smoke studies.** `test`, `fly_test`, `*-smoke`, `*-pilot` with single-digit
   respondents. Need an exclusion rule, not eyeballing.
5. **Zero-spend studies with respondents** (`vl-pulse-nigeria-smoke`: 6,797 respondents,
   $0) — re-contacts or organic traffic. They inflate any spend ÷ respondents ratio's
   denominator.
6. **A country average is the wrong unit.** Nigeria runs roughly $0.04–$8.89 across studies
   (`ad-cost.json`). Lead with the spread and the per-stratum cost, never a mean.
7. **Coverage has moved.** Argentina, Bolivia and Honduras (current platform) have studies
   since August 2026 and are **not in `coverage.json`**, which is from August. C-017's 41 is
   a floor that is now likely low, and `ws-seo.md` §4.3 ("no South America") is out of date.

### 5.4 · Countries, roughly — NOT claims

Current platform, single-country studies, **raw and contaminated by 5.3's traps 1–5**. For
shape only.

| Tier | Countries |
|---|---|
| **Deep** — many studies, per-stratum prices | Nigeria (52 studies, 2023–26) · US (13) · Bangladesh (14) · Kenya (8) · Ghana (7) · Pakistan (4) |
| **Recent, large, one or two studies** | Iraq · Egypt · Saudi Arabia · Morocco · Jordan (2025–26, each ~18–26k respondents) · Indonesia · Serbia · Bulgaria · Kyrgyzstan |
| **New, small, live** | Bolivia · Argentina · Honduras (Aug–Sep 2026) |
| **Older platform only** — respondents fine, spend needs currency work | Lebanon · Haiti · Zambia · Libya · Kuwait · Laos · Jamaica · Chad · Cameroon · Congo · Djibouti · Gambia · Papua New Guinea · Ukraine · Romania · Belize |

---

## 6 · The country page — a draft spec to test, not settle

Two templates at the two ends of the range, which is what the pilot exists to test:

- **Benchmark** (many studies): cost per respondent as a distribution across studies; cost
  **by group** (gender × age × region, from per-stratum prices); time to fill; who was
  reached against target; channels; languages; topics; years active.
- **Case** (one or two studies): the same sections, stated as *what happened in this study*
  rather than as a norm. **A single study must not be presented as a benchmark.**

Both: answer-first heading; a data table behind every chart; a dated, defined figure in
every sentence; a link to the handbook chapter that explains the driver (e.g. *why women
cost more to reach*); a link to the raw CSV; `Dataset` JSON-LD from the same file; one CTA.

**Every figure still needs a `VERIFIED` `CLAIMS.md` row** (hard rule 1). Country figures are
our own operating record, so they sit in a **`Definition`** table and carry no source line —
but the definition itself (what counts as a respondent, which studies are excluded, which
currency conversion) is what makes them defensible and must be on the page.

---

## 7 · The plan

**Pilot: Nigeria and Bolivia.** Nandan: *"a one study country and a many study country …
Then we see how those look. We take a look at everything and decide what to build from
there."*

| | Nigeria | Bolivia |
|---|---|---|
| Why | The deepest dataset we have — the benchmark template at full strength | The other end: new, small, two sibling studies (`lac-healthy-diets-bolivia`, `…-channel`), both **September 2026** |
| Studies (raw) | 52 on the current platform, 9 campaigns on the older one | 2 |
| Stratification | Mostly Gender × State; some Age, LGA | Gender × Location (urban/rural) |
| What it will stress | Cleaning (every trap in 5.3 appears in Nigeria) and the per-group cost story | Whether a one-study page reads as honest rather than thin |
| Watch | Currency on the naira accounts | **Still fielding** — recruitment runs to about 2026-09-29. Pull after it closes, or date the page |

**Steps, each ending in something Nandan looks at:**

1. **Clean and query.** One reproducible query per country page section, with the 5.3
   exclusions written into it, saved into `scripts/data/` beside the existing figure data.
   Output: `scripts/data/country-ng.json`, `country-bo.json`.
2. **Register.** `CLAIMS.md` rows for every figure the two pages state.
3. **Build both pages locally** at `/countries/nigeria/` and `/countries/bolivia/`, not
   linked, not in the sitemap. **Not deployed until reviewed** — `master` deploys production.
4. **Review together**, then decide: which template(s), which countries, whether the
   handbook comes next, whether `/data/` ships with them.

**Not in the pilot:** the estimator, the handbook, `/data/`, llms.txt, the older-platform
currency work (Nigeria's older campaigns can be left out of cost and kept in counts).

---

## 8 · Open

- Handbook location (§3), and the D-023 rule for comparing with panels.
- Whether older-platform countries get cost figures (needs currency work) or respondent
  counts only.
- The page-level definition of a respondent: first-time recruit (as `ad-cost.json`), any
  completed survey, or any started conversation. It changes every cost figure.
- Whether country pages are reached from the homepage — a D-007 question the pilot will
  inform, not answer.

---

## Appendix · Queries used in exploration

Helper, run from the repo root (read-only, always):

```sh
kubectl exec -n vprod gbv-cockroachdb-0 -- /cockroach/cockroach sql --insecure \
  --format=tsv --database=<vlab|chatroach> -e "<SELECT>"
```

**Latest config per study** (`vlab`):

```sql
WITH l AS (SELECT study_id, conf_type, max(created) m FROM study_confs GROUP BY 1,2)
SELECT c.study_id, c.conf_type, c.created, c.conf::string
FROM study_confs c JOIN l ON l.study_id=c.study_id AND l.conf_type=c.conf_type AND l.m=c.created
WHERE c.conf_type IN ('strata','recruitment','general','destinations','variables');
```

**Spend and delivery per study × campaign × stratum** (`vlab`) — max per day, never sum
within a day (`temp=true` rows are cumulative snapshots):

```sql
WITH x AS (
  SELECT e.study_id, c.key AS camp, s.key AS strat,
         coalesce(s.value->>'date_start', e.period_start::date::string) AS d,
         max((s.value->>'spend')::float8) AS spend,
         max((s.value->>'impressions')::float8) AS imp,
         max((s.value->>'unique_clicks')::float8) AS clicks
  FROM recruitment_data_events e, jsonb_each(e.data) AS c, jsonb_each(c.value) AS s
  WHERE jsonb_typeof(c.value)='object' AND jsonb_typeof(s.value)='object'
    AND s.value->>'spend' IS NOT NULL
  GROUP BY 1,2,3,4)
SELECT study_id, camp, strat, count(*) days, min(d), max(d), sum(spend), sum(imp), sum(clicks)
FROM x GROUP BY 1,2,3;
```

**Latest per-stratum price report per study** (`vlab`):

```sql
WITH l AS (SELECT study_id, max(created) m FROM adopt_reports
           WHERE report_type='FACEBOOK_ADOPT' GROUP BY 1)
SELECT a.study_id, a.created, a.details::string
FROM adopt_reports a JOIN l ON l.study_id=a.study_id AND l.m=a.created
WHERE a.report_type='FACEBOOK_ADOPT';
```

**Respondents per study** (`vlab`): `SELECT study_id, count(DISTINCT user_id), min(timestamp),
max(timestamp) FROM inference_data GROUP BY 1;` — **raw; umbrella studies double-count
(5.3 trap 3).**

**Older platform, latest price report per campaign** (`chatroach`): the same shape against
`adopt_reports` keyed on `campaignid`; countries from `campaign_confs.conf` by the C-017
regexp.

**Country per study:** every ISO code under `"country"` / `"countries"` in the latest
`strata` conf. Studies naming more than one country (4 on the current platform) are left out
of per-country figures.
