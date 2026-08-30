---
title: "Recruitment"
weight: 3
---

The "recruitment" configuration describes how/where recruitment will take place. Every study needs to recruit from somewhere.

There are currently 3 types of recruitments:

1. [Simple](#simple)
2. [Pipeline Experiment](#pipeline-experiment)
3. [Destination Experiment](#destination-experiment)

## Shared Fields

Some fields are shared by all recruitment types:

- `Ad Campaign Name`: This is the name of the ad campaign that will be created for recruitment.
- `Objective`: This is the Facebook "objective" of the recruitment campaign. You can read about the various objectives [here](https://www.facebook.com/business/help/1438417719786914). Certain objectives allow for certain optimization goals. For example, if you want to optimize for "messages," you might pick "engagement" as the objective.
- `Optimization Goal`: The Facebook optimization goal, also called the "performance goal." You can read more about the goals [here](https://www.facebook.com/business/help/416997652473726). A study using a [Multi destination](/docs/vlab/study-configuration/destination/#multi-messenger-or-whatsapp) must set this to `CONVERSATIONS`.
- `Destination Type`: The type of destination that the ad will route people to. For example, if you're sending people to a web survey, pick "web."

  For **chat destinations this is now derived** from the destinations you
  configured — a Messenger destination opens Messenger, a WhatsApp destination
  opens WhatsApp, a Multi destination opens either. You no longer have to keep
  this field in step with them by hand, and a study whose stated type is a
  messaging one that none of its destinations provides is refused at save time
  rather than publishing ads that route half their clicks nowhere. See
  [Destinations](/docs/vlab/study-configuration/destination/#destinations-and-the-channel-an-ad-opens).
- `Minimum Budget`: The minimum budget used by ads. No ad will ever run with less than this and this will be used as the starting/default budget when recruitment begins.
- `Start Date`: The date in which the recruiting should start.
- `End Date`: The date on which the recruiting should end.

## Simple

This is the easiest of the recruiting strategies where the Virtual Labs platform will
routinely check your ad campaign and update the campaign accordingly to try and
achieve your recruiting goals.

You will need to provide the following fields:

- `Budget`: The amount you would like to spend in order to recruit your maximum sample.
- `Max Sample`: This is the maximum number of respondents to recruit.

## Destination Experiment

Use this when you want to create a multi-arm randomized experiment (A/B test on Facebook) where some of your sample is sent to different [destinations](/docs/vlab/study-configuration/destination/ "Destination Configuration").

This is also the way to **compare messaging channels**: one arm with a Messenger destination and one with a WhatsApp destination gives you a randomized channel assignment. A [Multi destination](/docs/vlab/study-configuration/destination/#multi-messenger-or-whatsapp) does not — Meta chooses the channel there, and not at random.

You will need to have the destinations configured and you will then need to set the following fields:

- `Ad Campaign Name Base`: The name of the ad campaign(s) that vlab will create and use for recruitment. If you have more than one campaign (i.e. Destination Experiment), it will append -1, -2, etc. to this name
- `Budget Per Arm`: How much you would like to spend per arm of your experiment
- `Max Sample Per Arm`: How big of a sample you would like to set for each arm
    of your experiment
- `Destinations`: The list of destinations that should be involved within the
    experiment

## Pipeline Experiment

In this design, we generate an A/B test on Facebook but instead of sending your sample to different destinations, we run the ads at different times (a pipeline experiment design). You can set up how long each arm runs, and how long they are offset from the start of the previous arm.

You will need to provide the following fields:

- `Ad Campaign Name Base`: The name of the ad campaign(s) that vlab will create and use for recruitment. If you have more than one campaign (i.e. Destination Experiment), it will append -1, -2, etc. to this name
- `Budget Per Arm`: How much you would like to spend per arm of your experiment
- `Max Sample Per Arm`: How big of a sample you would like to set for each arm
- `Arms`: How many arms of the experiment would you like to create
- `Recruitment Days`: How many days you would like the recruitment to run for
- `Offset Days`: How many days you would like to pause the recruiting for
