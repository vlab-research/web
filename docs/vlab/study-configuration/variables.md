---
title: Variables
weight: 12
---

Variables are used for targeting ads for stratified recruiting.

Stratified recruitment optimizes for the joint distribution of respondents defined by a set of categorical Variables. As a categorical variable, each Variable has a set of values it can take called "Levels".

For example, one might create a Variable called "age" along with three Levels: "18-30", "31-50", "51-65".

To create Variables and Levels, we use what we call "Template Adsets" within a "Template Campaign". For each Variable, you select the Properties from Facebook that correspond to the variable. For each Level, you must select an Adset in your Ad Account that corresponds to that Level in the defined Properties.

This can be made most clear with examples. First, create an empty Template Campaign in your Ad Account. The optimization does not matter. The template campaign will hold Adsets you will use to define targeting, the ads will never themselves run.

1. If you want to target age, you might create a Variable called "age" with the Properties "Minimum Age" and "Maximum Age". You will then create 3 adsets within your template campaign, corresponding to 3 desired Levels, each one targeting the group of interest using the Ads Manager to define the targeting (i.e. on adset targeting 18-30, one targeting 31-40, one targeting 51-65).

[Example Video]

2. If you want to target location, where you divide a country into two Levels: "capital region" and "everything else". You would create a Variable called "location" with the Properties "Geo Locations" and "Excluded Geo Locations". You would then create two Adsets in your template campaign. One would target the captial city. The other would _exclude_ the capital city. You then create 2 Levels associated with each of those two Adsets.

[Example Video]

## Adding targeting information across all strata

Often, we want to add targeitng information that isn't stratified, it's the same across all strata. Examples might include:

1. You are not stratifying by geography, but want to target a whole country.
2. You are not stratifying by age, but only want to target a narrow age band (i.e. 18-24).
3. You want to exclude respondents from a previous study via a custom audience.

There are two ways to solve this problem:

1. Add the targeting to _all_ your templates and select the appropriate properties in each variable.
2. Create a new variable (i.e. "geography" or "age" or "additional"), give it just one level (i.e. "all"), and pick all the appriopriate properties.
