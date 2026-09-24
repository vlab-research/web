# Inbound data: from country pages to buckets (plan, 2026-09-24)

The next step after the country-page pilot (D-032; `ws-inbound.md` §7, v1–v7;
`country-recipe.md`). **Read this first to pick the work up.** Nothing here is on the site or
pushed. `master` is ahead of `origin` by the local commits of 2026-09-23 and 2026-09-24.

## Status, 2026-09-24 night: v11 (read this first)

Nandan on v10: **no dates on the pages** (they identify studies and imply a change over time we have
no evidence for); compare places all together. **The Kenya small-run/full-run story was withdrawn**:
those were different studies, and a test-vs-full claim needs better data (US, Nigeria). He liked the
multiples, **as an addition** to dollar maps of cost per qualified respondent (the v8 Indonesia and
Nigeria-states maps).
- **Place index** (`patterns.py` `place_index`): log cost per start = recruitment + place, weighted
  by starts, over non-specialised recruitments that ran 2+ solid places; recruitments are linked only
  when they share 2+ places (a single shared place carried Lagos's swing into a spurious 98×).
- **Dollars** per qualified and per start come from the same recruitments as the multiple, and are
  shown only when every place ran in every one of them; otherwise the multiple alone, with its map.
- Maps: dollar map first, multiples map on the place pattern; no map for fewer than 4 places or for
  overlapping places; groups of regions are shaded, not labelled region by region.

## Status, 2026-09-24 late: v10, three page patterns

Nandan, after v9: *"avoid data that is overly specific and focus on the more General data wherever
possible, even if … leaving some studies out"* (Bauchi was mostly parents of daughters; Minnesota's
ads aimed at particular communities). The rule now:
- **Level (dollars) only from `general` recruitments**, or from one named `common` group where a
  country has nothing else, with the group in the lede. `specialised` ones get one sentence.
- **Place differences as multiples inside one recruitment**, only between places with 200+ starts
  and $100+ of ads, never from rounds flagged `ad_arm_confounded_with_side`.
- **Tiers:** `merge_cells.py` `audience_tier` (interest targeting on more than a quarter of the spend, or any
  screen beyond basics and caregiver tags, is specialised); hand overrides in
  `scripts/data/tier-overrides.json` (the two Minnesota recruitments: Somali-language and
  multicultural ad versions added mid-run). 43 general, 37 common, 16 specialised.
- **Patterns** (`scripts/pilot-maps/patterns.py`, `PATTERN` dict): `general` (Kenya: full runs
  against short test runs, since run size moves cost per start 2 cents to $3.30), `group`
  (Indonesia), `place` (Nigeria: repeated same-place comparisons, the 2023 six states, and the
  Lagos flip). Review v10 shows those three plus a Tiers tab. **Next:** Nandan's reaction, then
  assign a pattern to every other country.
- The Kenya page carries a new "speed" module whose one-third figure needs a CLAIMS Definition row.

## Status, 2026-09-24 evening: step 1 done, pages generated (review v9)

- **The cell table exists**: `scripts/data/cells.json` (1,081 cells, 23 countries, 96 recruitments
  kept, 16 excluded, $338,760), with `recruitment-criteria.json`, `places.json` and `buckets.json`.
  Contract: `notes/cells-schema.md`. Built per group by `scripts/pilot-maps/countries/<dir>/cells.py`
  (`--fetch` re-pulls; slugs and question refs are read from the gitignored `private/<G>.map.json`).
- **`merge_cells.py`** validates, runs the leak check (study names from the private maps; the topic
  denylist is `private/denylist.txt`, gitignored because it names clients) and applies the bucket
  rules. **`pages.py`** generates every page from the table into `out/review.html` (gitignored: its
  For-review notes name studies). Run it with the geo venv; it needs the Natural Earth files that
  `fetch_ne.py` downloads.
- **Review v9** is the same Artifact URL below: one tab per country, **Who qualified** (the
  cross-country person slice) and **Buckets** (every recruitment, its tags and bucket, for step 2).
- **Decided in the build, for review:** the $100 floor marks a place "thin" rather than hiding it;
  recruitments whose "qualified" is not comparable (a later wave, under 3% or over 97% qualifying)
  count for place but not in the who slice; region maps shade single-region places only;
  minutes over 120 are external-survey sync time and count as unknown.
- **Known weak spots:** US-2023-08's "qualified" is completion of an outside survey and is not caught
  by the rule; the Irish account's currency is unverified; LAC and KE-2026-07 were still fielding.
  Each agent's verified/inferred report is summarised in the recruitment `notes`.

## Where things stood before the table (v8)

- **The review page**: https://claude.ai/artifact/BggyuQGoib8zPi8ZWdGDkq (private, v8). It has
  tabs for Nigeria, Bangladesh, Pakistan, Indonesia, Kenya, United States, Iraq, Egypt, Morocco,
  Bolivia and Rules.
  - It is assembled by `scripts/pilot-maps/assemble.py` from
    `scripts/pilot-maps/review-page.tpl.html` plus each country's `section*.html` and SVGs.
  - **Edit the template or the sections, never the assembled page.**
  - `assemble.py` still points at the session scratchpad (`SP`); re-point it to run from the
    repo.
- **The data**: `scripts/data/country-*.json`, one per country; each carries rules, definitions,
  terms and `excluded_for_review`. The per-country agent code, SQL, SVGs and sections are in
  `scripts/pilot-maps/countries/<CC>/`. The map helpers are in
  `scripts/pilot-maps/build_maps.py`; `fetch_ne.py` downloads Natural Earth and GeoNames, which
  are gitignored.
- **Nigeria and Kenya are rebuilt as place pages** (pooled across recruitments). The other
  seven still follow the earlier one-study design and wait for the bucketing below.
- **The spend-intensity analysis is done**: `ws-spend-intensity.md`. Doubling a stratum's daily
  spend raises cost per starter by about 32% (22–43%); +46% in radius areas.
- **Raw pulls, the Natural Earth downloads and the analysis panels** lived in the session
  scratchpad and are gone after the session. Every script re-pulls read-only (`--fetch`, or
  `pull.sh`).

## What Nandan decided along the way (in order; the later ones win)

1. **Clean data we understand exactly**, and only interesting or reusable results. Odd
   targeting stays off the page.
2. **No "urban"/"rural", no "circles".** Use *whole state*, *radius area*, *inside the radius
   areas* and *outside them*, defined on every page.
3. **Each page stands alone**, with "how it works" modules at the top: location targeting on
   Meta; what the numbers count.
4. **Voice: our recruiting record, never a client's study.** The unit of speech is a
   "recruitment", and it may stay ambiguous whether there was one or several. No topics or
   programme names. Ambiguity is allowed, falsehood never.
5. **The unit is the place, not the study.** Pilots, short runs and full studies all count.
   Study boundaries are for cleaning only.
6. **Headline: ad cost per person who started**, which measures the place. Beside it, cost per
   qualified respondent, with who qualified written out.
7. **Now: bucket everything along separate dimensions** (below).

## The plan: one table, sliced by dimension

Nandan, 2026-09-24: *"what we next need to do is match them up to figure out which studies are
similar and which are not, and how do we sort of create a bucketing … the bucketing is what
matters … We don't necessarily need the full cross-sectional analysis … but it's not bad to
slice the data by these dimensions individually."*

### 1. One table of cells: `scripts/data/cells.json`

**One row per ad set (stratum) per recruitment round, across every country.** Fields:
- **Ids:** a neutral `recruitment_id` (R-001…), `cell_id`, country. Study slugs go only in a
  gitignored or scratch mapping, **never in the public repo**. Slugs name clients (hard rule 4).
- **Place:** geometry type (country / region / city+radius / radius-area set /
  country-minus-X), a canonical place key (e.g. `NG:region:Lagos`,
  `NG:radius:Abuja-4km-24`), and whether it is inside or outside.
- **Targeting:** Meta gender, and age band.
- **Criteria:** a link to the recruitment's criteria record (§2).
- **Measures:** dates, days with spend > 0, spend (USD), people who started (by ad metadata at
  first message), qualified (under the final quota rule), median daily spend.
- **Flags:** thin, dominated by one round, pin checked, attribution method.

### 2. Criteria registry: `scripts/data/recruitment-criteria.json`

**One record per recruitment, as structured fields, not prose:**
- the Meta age range and gender;
- screening conditions as tags: `caregiver_child_age:9-14`, `has_whatsapp`,
  `language:hausa`, `adult_18plus`, `lives_in_country`, …;
- the qualifying point (question n of N);
- median minutes to qualify;
- language(s);
- channel (Messenger / WhatsApp / web);
- incentive, if known.

The sources are the survey form (Fly), the strata `question_targeting` (the quota rule and its
history), and the Meta targeting. Much of this was already dug up per country: see each
`country-*.json` and the For review notes.

### 3. Buckets, derived from the registry and reviewed by Nandan before use

- **Place:** two slices, *whole regions* (a filled map) and *radius areas* (drawn areas), plus
  whole country. This already exists for Nigeria and Kenya.
- **Type of person:** two parts, because they act at different steps.
  - **Who the ads were shown to** (gender, age band). This moves cost per starter.
  - **Who qualified** (the screening tags plus survey length). This moves the **share of
    starters who qualify**.
  - Expected buckets, to be confirmed from the data: *any adult*, *young adults*,
    *caregivers of children in an age band* (a large group across NG, BD and PK), *women only*,
    *specific subgroups*.
- **Speed / daily spend:** record it per cell, **leave it off the pages for now**, and never
  print it beside a place's cost (see the trap in `ws-spend-intensity.md`).

**The payoff:** cost per qualified ≈ cost per starter (from the place slice) ÷ share who
qualify (from the person slice). A reader can combine the two slices to estimate their own
study. Present it as a rule of thumb, not a claim.

### 4. How to present a slice

- Each figure carries its **range across rounds** and its **number of rounds**. Nigeria and
  Kenya showed that pooling reorders places by how hard each round pushed: Lagos was cheapest in
  the 2023 same-round comparison and is mid-pack pooled.
- **Same-round comparisons stay the fair way to compare places**, shown as their own figure.
- A **spend floor per place**, about $100, so a few days of $14 spend cannot set a headline.
  Proposed, not yet agreed.
- Person-type slices can pool **across countries**, which opens a second family of pages:
  *"What does it cost to recruit caregivers of adolescent girls / young adults?"*

## Next steps

1. **Build the registry and the cell table across all countries.** Probably one agent per
   country group, working from `country-recipe.md` and this file, followed by a merge step that
   checks ids and deduplicates people across countries and platforms.
2. **Propose the person buckets** from the registry, as a short review artifact for Nandan.
3. **After review**, regenerate the country pages from the cell table (place slice +
   person slice + ranges), and draft one cross-country person-type page.
4. **Then** step 2 of the original plan: `CLAIMS.md` Definition rows for whatever ships,
   the slug scrub, the build into Eleventy, unlinked, and review before any push.

## Open questions for Nandan

1. **Places:** show each as a range across rounds, plus same-round comparisons? Is the
   $100 spend floor right?
2. **Spend intensity:** add a third "how it works" module, *spending faster in the same place
   costs more per person*? It needs a `CLAIMS.md` Definition row.
3. **Bangladesh endline:** it recruited a fresh sample with ads ($0.24, whole divisions). The
   place design now includes fresh-sample endlines (Nigeria's do). Confirm.
4. **Pakistan:** the place gap is unexplained, and 1 km vs 5 km radii are confounded with place.
   **Morocco:** 13% qualify, with 48% stopping at or before consent. Enough?
5. **US:** the state groups track 2023 recreational-cannabis states. OK to keep the topic off the
   page?
6. **Still fielding:** Kenya closes 25 Sep, Bolivia about 29 Sep. Re-pull after.
7. **Facts to confirm:**
   - Did `kenya-tvet` (Sep 2026, $5k budget, no recorded spend) run?
   - What incentive did Iraq's respondents get (config $1; the text promises dinars)?
   - The 2024–25 Kenya runs cost $0.02–0.07 per start with no impressions recorded. Real?

## Traps learned this session (also in `country-recipe.md`)

- Currency: naira accounts, detected by CPM.
- Shared campaigns and umbrella studies.
- Ad days counted from rows rather than days with spend > 0.
- Stale adopt reports: fetch one at a time, `ORDER BY created DESC LIMIT 1`.
- Quota rules that change mid-study: recount under the final rule (Egypt went from 966 to 3,696).
- `current_price_per_participant` is Meta's marginal estimate, not an average.
- Stratum labels that do not match the targeting ("State:X" meaning radius areas).
- Mis-placed pins (Kirfi, the Abuja/Kuje pin), and Mecca targeted as "Jeddah".
- The ad arm confounded with the side of a radius line (Nigeria, April 2025).
- A gender label that comes from the ad set, not from an answer.
- Personal data in raw pulls (phone numbers): keep only ad labels.
