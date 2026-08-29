---
title: Core Concepts
weight: 0
---

Survey in Fly consist of one or more "Forms". "Surveys" themselves are nothing more then a collection of forms with a name. Surveys are the unit for downloading data - you download data for one "survey" all together.

Forms are parts of a survey. They consist of questions that a participant will answer. Forms are each given an individual "shortcode", which identifies the form.

Forms can "stitch" to other forms, stringing forms together longitudinally.

Also, forms can be connected to other forms as "translations", so that you can run your survey in multiple languages and translate everything back to a single language for analysis.

## Channels

A form is not tied to a messaging app. The same form, under the same shortcode,
can be answered on **Facebook Messenger** or on **WhatsApp**, and one study can
recruit on both at once. Which one a respondent gets depends on how they arrived
— which page or which WhatsApp number the ad or link pointed at.

That is deliberate: you write and translate one survey, not one per app. But the
apps are not identical, and a few things that work on Messenger will stop a
WhatsApp survey outright. Read [Channels](/docs/fly/reference/channels/) before
writing a survey that will run on WhatsApp.

## Example 1: A multilingual longitudinal study

A multilingual longitudinal study might consist of four forms with the following shortcodes:

1. baselinespanish
2. baselinefrench
3. endlinespanish
4. endlinefrench

In this grouping, baselinespanish will probably be stitched with endlinespanish. If Spanish is the core languge of the researchers, they might want to translate all the French forms into Spanish so that the final survey data is downloaded entirely in Spanish.
