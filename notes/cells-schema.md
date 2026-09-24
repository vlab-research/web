# The cell table: schema (2026-09-24)

The contract for `ws-bucketing.md` step 1. Every country group writes the same three files, and
the merge step (`scripts/pilot-maps/merge_cells.py`) joins them. **Read `country-recipe.md` and
`ws-inbound.md` §5.3 first**: the cleaning rules there all still apply.

## Files per country group `<G>`

| File | Tracked? | What |
|---|---|---|
| `scripts/data/cells/<G>.cells.json` | yes | one row per ad set (stratum) per recruitment round |
| `scripts/data/cells/<G>.criteria.json` | yes | one record per recruitment |
| `scripts/data/cells/<G>.places.json` | yes | one record per place key: its geometry, for maps |
| `scripts/pilot-maps/private/<G>.map.json` | **no (gitignored)** | recruitment id → study slugs and ids; cell → raw stratum id |
| `scripts/pilot-maps/countries/<G>/cells.py` | yes | the script that pulls (SELECT only) and writes the above; raw pulls go in `countries/<G>/raw/` (gitignored) |

**No study slug, study UUID, programme name, client name or topic word appears in a tracked
file.** Stratum ids go in the private map, because some of them carry topic words. The public
files use neutral recruitment ids and plain labels.

## Recruitment ids

Provisional: `<CC>-<YYYY>-<MM>` of the first spend day, with a letter suffix when two start in
the same month (`NG-2024-10a`). The merge step keeps them; they are neutral already.

A **recruitment** is one round of ads filling one set of quotas. Sibling studies that fed one
survey are one recruitment. One study run in two phases with different targeting may be two.
A multi-country study is **one recruitment per country**.

## `cells.json`: a list of rows

```json
{
  "rec": "KE-2025-05",
  "cell": "KE-2025-05/03",
  "country": "KE",
  "place": "KE:country-minus:10-cities-16km",
  "side": null,
  "ads": {"genders": "women", "age_min": 18, "age_max": 24, "interests": true},
  "person_override": null,
  "first": "2025-05-04", "last": "2025-07-17",
  "spend_days": 41,
  "spend_usd": 812.40,
  "impressions": 402113,
  "started": 1893,
  "qualified": 1210,
  "median_daily_spend": 18.20,
  "median_minutes_to_qualify": 14.2,
  "flags": ["interest_targeting"],
  "attribution": "ad_metadata"
}
```

- `place`: a key into `places.json`. `side` is `"inside"` or `"outside"` for the two halves of a
  radius-area design, else null.
- `ads.genders`: `"all"`, `"women"` or `"men"` (Meta targeting). `interests`: true when the ad
  set used Meta interests or behaviours, which changes who is reached.
- `person_override`: null, or a list of screening tags that apply to this cell only (when quota
  groups inside one recruitment screened for different people).
- **Measures**, with the definitions in `country-recipe.md` "The unit is the place":
  - `spend_usd`: Insights spend for the ad set, max per campaign × stratum × day, summed over
    days with spend > 0; campaigns shared across studies counted once. **USD accounts only**:
    a naira or rupee account (CPM test) is excluded, not converted, and listed in the
    exclusions.
  - `started`: people whose first record carries this ad set's metadata, first message inside
    the spend window (1 day before to 3 days after). Each person once per recruitment.
  - `qualified`: started and past the recruitment's **final** quota rule, recounted from
    `inference_data`.
  - `median_daily_spend`: median over the cell's spend days. Recorded; never shown beside a cost.
  - `median_minutes_to_qualify`: median of (time of the qualifying answer − first message) over
    the cell's qualified people.
- `attribution`: `"ad_metadata"` (the default and the method), or `"report"` where only an adopt
  report could split people by stratum (say why in `flags`).
- `flags`: free short tokens, e.g. `thin` (under 200 started), `one_day`, `pin_checked`,
  `interest_targeting`, `pooled_siblings`.

## `criteria.json`: a list of records

```json
{
  "rec": "KE-2025-05",
  "country": "KE",
  "first": "2025-05-04", "last": "2025-07-17",
  "round": "baseline",
  "ads": {"genders": ["women", "men"], "age_min": 18, "age_max": 24, "interests": true},
  "screen": ["age:18-24", "lives_in:KE", "consent"],
  "who_qualified": "aged 18–24; reached the end of the questions",
  "qualify_rule": "answered the phone-number question",
  "qualify_point": {"question": 38, "of": 40},
  "median_minutes_to_qualify": 14.2,
  "channel": "messenger",
  "languages": ["en", "sw"],
  "incentive": {"amount": 1.0, "currency": "USD", "form": "airtime"},
  "started": 6513, "qualified": 4120,
  "notes": "plain words; no topics"
}
```

- `round`: `pilot`, `baseline`, `midline-fresh`, `endline-fresh`, `screener`, `cross-section`,
  `panel-wave` (re-contacts are **out**, and do not get a record).
- `qualify_point`: the position of the qualifying question in the form (count questions the
  respondent sees on the main path; say how you counted in `notes`). Null if unknown.
- `channel`: `messenger`, `whatsapp`, `instagram`, or `web`.
- `incentive`: null if none; `{"amount": null, ...}` if there was one of unknown size.

### Screening tags (controlled vocabulary)

These are the conditions a person had to meet to count as qualified, **beyond** finishing to the
qualifying point. Use these; add a new tag only when none fits, and define it in your report.

| Tag | Meaning |
|---|---|
| `age:<a>-<b>` | a screened age band (not the ad age) |
| `gender:women` / `gender:men` | screened by answer, not by ad set |
| `lives_in:<CC or region>` | a residence check |
| `consent` | agreed to take part (nearly all; include it when it is a question) |
| `caregiver:child_age:<a>-<b>` | parent or caregiver of a child in that age band |
| `caregiver:child_gender:girl` / `:boy` | the child's gender |
| `parent_any` | any parent or caregiver |
| `has_phone` / `has_whatsapp` | owns one / uses it |
| `gave_phone` | gave a phone number (usually for payment) |
| `language:<code>` | answered in, or chose, a language |
| `occupation:<x>` | e.g. `student`, `health_worker`, `farmer` |
| `pregnant_or_recent_birth` | |
| `behaviour:<x>` | a behaviour screen (e.g. `behaviour:smoker`). **Sensitive: it can reveal the topic.** It stays in the data, and the page says "a specific behaviour" |
| `attention_check` | passed one |
| `quota_group:<x>` | a quota assignment that is itself a screen |

## `places.json`: a map from place key to geometry

```json
{
  "NG:region:Lagos": {"country": "NG", "type": "region", "label": "Lagos State (whole)",
                      "regions": ["Lagos"]},
  "KE:radius:81-towns-2-9km": {"country": "KE", "type": "radius_set",
                      "label": "Inside 81 radius areas (2–9 km)",
                      "pins": [[-1.2921, 36.8219, 5.0]]},
  "KE:outside:81-towns-2-9km": {"country": "KE", "type": "radius_outside",
                      "label": "Kenya outside the 81 radius areas", "complement_of": "KE:radius:81-towns-2-9km"},
  "KE:country-minus:10-cities-16km": {"country": "KE", "type": "country_minus",
                      "label": "Kenya except 10 cities (16 km)", "pins_excluded": [[...]]},
  "KE:country": {"country": "KE", "type": "country", "label": "Kenya, whole country"}
}
```

- `type`: `country`, `region` (one or more whole Meta regions: `regions` lists them by the Meta
  name), `radius_set` (pins with radii: `pins` is `[lat, lon, radius_km]`), `radius_outside`
  (the complement of a radius set inside a country or regions), `country_minus` (country with
  excluded regions or pins), `city_radius` (Meta cities with radius: give each as a pin).
- **Place keys are geometry, not labels.** Two recruitments pool into one place only if the
  geometry is identical or near-identical (same regions; same pins within 1 km and the same radii).
  A whole region and a radius area inside it are two places.
- Check every pin is where it claims (GeoNames within 5 km) and say so in the report.

## The report each agent returns

Short. **Verified** (queried and checked) separately from **inferred**. Per recruitment: kept or
excluded, and why. New screening tags, with definitions. Anything a reader of the numbers would
need to know.
