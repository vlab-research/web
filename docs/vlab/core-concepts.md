---
title: Core Concepts
---

Virtual Lab is built around the concept of a "study".

A study is a project for which you want to recruit people via digital ads. The goal of Virtual Lab is to create and optmize recruitment ads to recruit the best population possible for your study.

To do so, Virtual Lab needs to know a few things:

1. Where should people be directed after clicking on the recruitment ad? This is called a `Destination`.
2. What should the ads look like? This is called `Creative`.
3. How should the ads be targeted to different types of people? This is defined with `Variables` and `Strata`.
4. How much money can be spent on advertising and over what period of time? This is called `Recruitment`.
5. How will Virtual Lab know how many, and what type, of people have been fully recruited? This involves configuring a `Data Source` and defining a set of `Data Extraction` variables used to determine stratification.

## How a respondent is connected back to their ad

Virtual Lab creates exactly one ad per (creative, stratum) pair, and every ad
carries a **ref**: a short string that travels with anyone who clicks it and
comes back in their response data. The ref is what makes a respondent
attributable to a stratum, and therefore what the optimizer counts.

There are two ways a study can do this, and it is a per-destination choice:

- **The ref spells the stratum out.** `creative.X.gender.men.form.mnchweek`
  arrives as metadata on the respondent's record, and your export already has the
  columns. This is the default and how Virtual Lab has always worked.
- **The ref carries an opaque token.** Nothing about the stratum travels with the
  ad; Virtual Lab records what each ad meant when it created it, and you join the
  two afterwards from the [Ad Attributions](/docs/vlab/study-configuration/ad_attributions/)
  export.

The second exists because on some channels — click-to-WhatsApp in particular —
the ref sits in the respondent's own message where they can read and edit it. See
[Destinations](/docs/vlab/study-configuration/destination/#what-an-ads-ref-carries).
