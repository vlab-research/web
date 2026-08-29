---
title: Ad Attributions
weight: 19
---

Virtual Lab creates exactly one ad per (creative, stratum) pair. **Ad
Attributions** is the record of what each of those ads meant: which creative,
which stratum, which survey, and every stratification value it was published
with.

It exists for two reasons, and both are about analysis rather than
configuration:

1. It is the table that makes a **looked-up ref** work — the setting under
   [Destinations](/docs/vlab/study-configuration/destination/#what-an-ads-ref-carries) where the
   ad carries a short token instead of spelling out the stratum.
2. It gives you, for any study, an exact ad-by-ad record you can join your
   survey export against — including for ads that no longer exist.

## The Ad Attributions step

Open your study's configuration and go to **Ad Attributions**. It is a read-only
table: one row per ad Virtual Lab has created for this study, with a download
button.

There is nothing to configure here. Rows appear as ads are created and are never
edited afterwards.

| Column | What it is |
|---|---|
| `ad_id` | The ad's id on the network. Useful for lining a row up against Meta's own reporting. |
| `network` | The ad network the id belongs to. `facebook` for both Messenger and WhatsApp ads — they are both Meta ads in one id namespace. |
| `ref_token` | The opaque token that ad's ref carries, and the key the lookup joins on. Empty for ads whose ref spells out the stratum instead. |
| `creative` | The creative name. |
| `form` | The shortcode the ad recruits into. |
| *(your variables)* | One column per stratification variable — `gender`, `Age`, `Region`, and anything you added as Additional Metadata. |
| `created` | When the row was written. |

## Downloading it

The download button on the step gives you the same rows as a CSV. You can also
fetch it directly, which is usually what you want from an analysis script:

```
GET https://<your-vlab-host>/{org_id}/studies/{slug}/ad-attributions.csv
```

It takes a Virtual Lab API key, and uses the same organisation and study routing
as every other study endpoint.

## Joining it to your survey data

The point of the export is that it is one sentence:

> **Left-join your survey export on the join key, and your stratum columns come
> back, named as they always were.**

The join key depends on which ref mode the study used:

- **`ref_token`** for a study whose ads carry a token. In your Fly export this
  arrives as the metadata column `vt` — add it under *Metadata to add as columns
  when pivoting* on the [export screen](/docs/fly/reference/downloading-data/).
- **`ad_id`** for lining rows up against Meta's reporting. Fly also records an
  `ad_id` for respondents whose arrival carried one, but it is **not** a
  complete record — Meta only sends it for some Messenger arrivals — so do not
  use it as your primary join.

A study whose ads spell the stratum out inline needs no join at all: the columns
are already in the export. The Ad Attributions table is still written for it, and
is still useful as a record of exactly which ads ran.

## Three things to know about the rows

### They are frozen at creation

A row is a snapshot of what the ad meant **when it was created**, not a pointer
to your current configuration. If you rename a stratum value or change a
creative's metadata next month, the rows written before that keep the old values
— which is correct: those are the values the respondents who clicked that ad were
recruited under.

Nothing refreshes a row, and nothing can. This is the whole reason the table
exists rather than being reconstructed on demand.

### Deleted ads are included

Virtual Lab removes ads that fall out of the desired set as a study runs, but
respondents keep arriving from removed ads — a page post can be shared and
re-shared indefinitely. So the export includes every ad ever created for the
study, live or not, and there is no "is it still running" column.

If you filtered to live ads you would silently lose rows you need, and the
respondents behind them would look unattributed rather than unexported.

### Columns are the union of every row

If you change what a creative or a stratum carries mid-study, later rows have a
different set of keys from earlier ones. The export shows the union of all of
them, in the order they were first seen, with blanks where a row does not have
that key. Both shapes survive.

## When a token has no row

A respondent arriving with a token that matches no row is always a bug: Virtual
Lab created an ad and lost the record of what it meant, so every respondent that
ad recruited is dropped from the stratum counts and the optimizer reallocates
budget away from a stratum that is recruiting perfectly well.

It is reported as an extraction error on the study, and it is
**self-healing** — Virtual Lab recomputes a study's whole history on every run,
so once the missing row exists, every prior run's attribution is fixed too.

A respondent arriving with **no token at all** is not an error. Shortcodes are
shareable by design and a study can perfectly well recruit people who never
clicked an ad; they simply have no ad to be attributed to.
