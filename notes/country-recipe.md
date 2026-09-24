# Country page recipe

How to turn one country's studies into a country page. Worked out on the Nigeria, Bolivia and
Indonesia pilot (D-032, `notes/ws-inbound.md` §7, v1–v4, 2026-09-23/24) with Nandan's review
at each step. **Read this, then `ws-inbound.md` §5.3's traps, before querying anything.**

## What a page is for

It answers **"what does it cost to recruit survey respondents in [country]?"** with numbers
another researcher can reuse to plan a study. It shows **only clean data we understand
exactly**, and only results that are interesting or reusable. Nandan: *"if the targeting
was kind of silly, then we shouldn't show it at all."* A page with one strong comparison
beats a page with five mixed ones. The v3 Nigeria page, three recruitments stitched
together, was judged *"a bit adhoc"*.

**The comparisons that work:**
- **Regions against regions in one study.** Whole states or provinces, same survey, same
  days. Nigeria 2023: Lagos $0.52 to Anambra $14.12.
- **Inside against outside radius areas in one study.** Bolivia's 13 city radius areas
  against the rest of the country; Indonesia's 120 radius areas against the rest of each
  province.
- **Demographic splits in one study**, as a table: age, gender.

Comparisons **across** studies (different surveys, years or eligibility) are weak. Use one
only when nothing better exists, and say that it shows direction, not a ratio.

## Data

Read-only production access is standing (`CLAIMS.md`). Run from anywhere:

```sh
kubectl exec -n vprod gbv-cockroachdb-0 -- /cockroach/cockroach sql --insecure \
  --format=tsv --database=vlab -e "<SELECT>"
```

**SELECT only, ever.** Queries: `scripts/data/country-queries.sql` (per-study spend,
respondents and ad days) and the appendix of `ws-inbound.md`.

| What | Where |
|---|---|
| Targeting per stratum | Latest `study_confs` row, `conf_type='strata'`: `facebook_targeting.geo_locations` / `excluded_geo_locations`, `question_targeting` (the quota rule), `quota` |
| Spend, ad days | `recruitment_data_events`: max per campaign × stratum × day, summed; drop campaigns shared across studies |
| **Per-group cost** | Latest `adopt_reports`, `report_type='FACEBOOK_ADOPT'`, per stratum: `lifetime_spent` ÷ `current_participants`. **Never `current_price_per_participant`**, which is Meta's marginal estimate, not an average |
| Account currency | `general` conf `ad_account`. Test with CPM: USD accounts run about $0.20–3; naira accounts 500+ |

**When a report and the quota rule disagree:** a study's quota rule (`question_targeting`) can change mid-study, and a report written before the change counts under the old rule. Check the rule's history. If the final rule differs from the one the latest report used, recount qualified people under the final rule, and verify the recount reproduces a report that did run under it. MENA did this: the Egypt figure went from 966 qualified to 3,696.

**Fetch the adopt report fresh, one study at a time** (`ORDER BY created DESC LIMIT 1`). A
correlated `max(created)` subquery over `adopt_reports` ran for over two minutes, and a
cached copy was a day stale.

## Definitions (do not change without Nandan)

- **Qualified respondent:** a person counted in the report's `current_participants`, meaning
  in a quota group and past the study's `question_targeting` rule (e.g. answered through to
  the phone-number question). **This is the denominator.** People who start and do not
  qualify are not counted, but the ads that reached them are.
- **Advertising cost:** the report's `lifetime_spent` ÷ qualified respondents, in USD. It
  excludes incentives, the platform and our fee.

## The eight rules

A study, or a group of sibling studies, reaches a page only if all eight pass:

1. USD ad account.
2. The report's spend reconciles with Insights spend (within about 5%).
3. At least 7 days of ads, counting **only days with spend above zero**. Insights writes rows on days with no spend, and counting rows overstated it: 169 against 156 for the US study, 20 against 12 for Bolivia (the MENA agent caught this, 2026-09-24).
4. At least $500 of ads and 200 qualified respondents.
5. A recruitment wave. Midlines, endlines and re-contacts are out.
6. Studies that fed one survey at the same time are combined: spend summed, each person
   counted once. Test for this by comparing respondent `user_id` sets.
7. **The targeting can be stated in one sentence, and it did what it said.** Check the pins:
   in the Bauchi pilot, the "Kirfi" target was a Meta *place* 67 km from Kirfi.
8. **The result can be explained.** A $45 figure with no known cause is out.

Every study that fails goes in the data file under `excluded_for_review`, with its reason.

## Vocabulary

- **Never "urban" or "rural"** in anything published. Official definitions vary, and the
  targeting rarely matches them. Stratum ids often say Urban/Rural; they are raw labels only.
- **Never "circles".** Nandan: too plain.
- **Whole state / whole province / whole country:** Meta `regions` or `countries`.
- **Radius area:** a Meta `custom_locations` pin plus a radius (0.63–50 miles, 1–80 km), or a
  Meta city plus a radius (10–50 miles; Meta rounds the lower end to 17 km, but 10 miles is
  16.1 km, which the MENA studies used). The two sides are **inside the radius areas** and **outside them**.
- Say "a state" only when the targeting was the whole state. If a stratum says "State:X" but
  targets radius areas, name the towns.

## Page structure

Copy it from `scripts/pilot-maps/review-page.tpl.html`, which is the source of truth for
the markup and the module text. In order:

1. Eyebrow `[Country] · Recruitment cost`, and H1 *What does it cost to recruit survey
   respondents in [Country]?*
2. **Lede that answers the question in one or two sentences**, with dates and numbers:
   answer-first, quotable standalone (`ws-inbound.md` §4).
3. A facts row: four cells, each with its own definition.
4. **Two "how it works" modules, verbatim from the template:** *Why the maps show radius
   areas* (location targeting on Meta), and *Cost per qualified respondent*. Each page stands
   alone, so every page carries them. Leave the radius-area module out only when the page
   has no radius areas.
5. Findings: an answer-first H2, a paragraph, a map, and a table behind the map.
6. *How the study was set up*: quotas, channel, incentive, qualified rule.
7. The CTA line, then a **"For review"** note: what was cleaned, what is uncertain, and study
   ids. It is removed before publishing.

A single study is described as *what happened in this study*, never as a benchmark for the
country.

## Maps

`scripts/pilot-maps/build_maps.py` holds the helpers: `Frame`, `path`, `text`, `circle`
(geodesic), `scalebar`, `cost_rows`, `svg`, `STYLE`, `places_near`, `name_point`,
`geonames`. Import it from the scratchpad copy, which has Natural Earth downloaded; the repo
copy's data is gitignored and `fetch_ne.py` fetches it. Match the existing maps:
- viewBox 760 wide;
- colours only as `var(--…)`;
- radius areas drawn geodesically at true radius, with insets where they are too small to
  see;
- town names only from Natural Earth or GeoNames within 5 km, labelled as orientation;
- cost rows under the map, which double as the legend;
- a `<title>` and `<desc>`.

Render to PNG once, look once, fix once.

## Outputs

Per country:
- `country-XX.json`, the same shape as `scripts/data/country-id.json`: `_meta` (rules,
  definitions, terms), the study facts, the groups, the checks, `excluded_for_review`;
- the map SVGs;
- a section fragment in the template's markup;
- a short report separating what was **verified** from what was **inferred**.
