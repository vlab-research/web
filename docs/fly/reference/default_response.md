---
title: Default Page Response
weight: 7
---

What happens when someone opens a chat with your Facebook Page, or messages your
WhatsApp number, without a survey reference?

Fly answers them with a **default form**, which has the special shortcode `305`.
Create any form with the shortcode `305` and it becomes the default for anyone who
arrives without a reference.

You might want to tell people something along the lines of "Sorry, if you saw an
ad for a survey, please go back and click on the ad." This helps prevent people
from starting your survey who you're not advertising to.

However, you can put any survey you want under the `305` shortcode.

## It is also where misrouted people land

This is the part worth understanding before you launch a study.

If a recruitment ad's reference is missing or mangled, Fly does not know which
survey the person wanted — so it starts them on the default form. **Nothing
errors.** They get whatever `305` says, answer it, and finish. In the data they
look like completions of the default form rather than like a failure.

That is the most expensive failure mode in a chat survey, because it is
invisible: your study shows almost no arrivals while the ad spends normally.

It happens most easily on **WhatsApp**, where the ad's prefilled message is the
only carrier of the reference. See
[WhatsApp Surveys](/docs/fly/reference/whatsapp/#1-a-click-to-whatsapp-ad).

Two practical consequences:

- **Make `305` say something.** If it is a single "sorry, wrong place" message,
  a spike in people finishing it is a signal you can actually read. If it is a
  real survey, misrouted respondents are silently mixed into someone's data.
- **Check arrivals early.** After turning an ad on, confirm that people are
  arriving on *your* shortcode, not on `305`, before letting the budget run.

## What the default form does not do

A message that names no survey will not restart or replace a conversation
someone already has. If a respondent who is part-way through your survey — or who
has already finished it — taps "Get Started" again, or sends a message that
carries no reference, they are left where they are rather than being moved onto
the default form.

This is deliberate: being silently moved onto a different survey is worse than
nothing happening. It does mean a respondent who has finished and comes back gets
**no reply at all**. If you want a re-engagement path, build it explicitly — an
ad, a link with a real `form.<shortcode>` reference, or a
[bail](/docs/fly/reference/bails/).
