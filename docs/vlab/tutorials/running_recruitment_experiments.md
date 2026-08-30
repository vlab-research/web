---
title: Recruitment Experiments
weight: 4
---

It can be useful to run a recruitment experiment in order to have an unconfounded measure of:

1. Differences in the performance of recruitment creative.
2. Diffrences in the performance of different incentives, which involve both creative and survey differences.

In order to do both of these things, Virtual Lab allows you to recruit via a "Destination Experiment."

## Creating the Destinations

The first thing you will need to do is select "Destination Experiment" as the recruitment type in the [Recruitment tab in the study configuration](/docs/vlab/study-configuration/recruitment/).

In this example, I am selecting two different forms in Fly as two destinations for the experiment. If you only want to test the creative, and you want the creative to go to the same survey, you can simply make the shortcode the same (or if it was a web survey, the URL the same):

![](/docs/images/vlab-dest-exp-destinations.png)

---

## Setting up the Destination Experiment

Now go back to the "Recruitment" tab and make the recruitment type "Destination Experiment." You'll notice you can now select the destinations to include in the experiment. Select both of them!

![](/docs/images/vlab-dest-exp-recruitment-step-1.png)

Fill out the rest of the fields according to [the documentation](/docs/vlab/study-configuration/recruitment/).

---

## Setting up the A/B test in Facebook

That's all you have to do in vlab! Set the strata/creatives to have all the creatives you want for each strata (all creatives for each strata in the simplest case). Virtual Lab will automatically split the creatives so that those associated with the different destinations are spread across the created campaigns.

Virtual Lab does not currently create the actual A/B test. So once Virtual Lab has created the campaigns in Facebok, you can go into Facebook and create an A/B test. The simplest way is to go to the ads manager, select the two newly-created campaigns, and select "a/b test" (the chemical beaker icon). This will allow you to create a new A/B test on the campaign level, which is what you want.

And that's it!
