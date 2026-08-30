---
title: "Destinations"
weight: 4
---

Every study needs a destination: where do the recruitment ads send the people who
click them? Destinations need to be connected to Virtual Lab so that it not only
knows where to send people, but also knows how to collect information about those
who become study participants, and knows how to optimize the ads.

Virtual Lab supports a set of destinations, and is written so that it is easy to
add a new one. When configuring your study you can create one or more
destinations, and each needs a unique name (key) that you refer to it by
elsewhere.

## Fields every destination has

- `name`: The name of the destination, used to refer to it in other
  configuration screens.
- `Where does this ad's stratum data end up?`: what the ad's *ref* carries — see
  [What an ad's ref carries](#what-an-ads-ref-carries) below. Leave it alone if
  you do not know what it means; the default is the way Virtual Lab has always
  worked.

The chat destinations (Messenger, WhatsApp, Multi) also share:

- `Initial Shortcode`: The shortcode of the first Fly form people should be sent
  to.
- `Welcome Message`: What the respondent sees before the conversation starts.
- `Additional Metadata`: Optional extra key-value pairs — written as JSON, e.g.
  `{"wave": "2"}` — added to every ad's ref and to its attribution record. Use it
  for facts about the destination that are not stratification variables.

## Messenger

A Fly Messenger survey destination. This creates Messenger ads for when you want
the respondent to be directed into a Fly survey on Facebook Messenger.

- `Initial Shortcode`
- `Welcome Message`: When someone clicks your ad they are directed to a Messenger
  chat with this initial message.
- `Button Text`: The button they tap in the chat, in response to the welcome
  message, to start the survey.
- `Additional Metadata` *(optional)*

## WhatsApp

A click-to-WhatsApp destination. This creates ads that open a WhatsApp chat with
your study's number, with the first message already typed for the respondent.

- `Initial Shortcode`: **letters, digits, `_` and `-` only.** A shortcode is
  shareable by design — someone may type it into WhatsApp by hand — so it has to
  be typeable, not merely encodable. Anything else is refused when you save.
- `Welcome Message`: Shown above the compose box on the WhatsApp welcome screen.
  It is not part of the routing, and it is not the prefilled message.
- `WhatsApp Phone Number`: **the number itself**, e.g. `+1-541-920-2635` — not a
  `phone_number_id`. Required. Meta treats it as optional and falls back to
  whichever number on the page happens to be "primary", so leaving it out means
  recruiting into a number you did not choose.
- `Additional Metadata` *(optional)*

There is **no Button Text**. WhatsApp has no quick-reply button; what the
respondent gets is a prefilled compose box, and the text in it is what routes
them into your survey.

::: warning

**On WhatsApp the routing token is the respondent's own first message.** Virtual
Lab sets it as the ad's autofill text. Two things follow:

- The respondent can **read and edit it** before pressing send. If your ad's ref
  carries stratum values, they can see themselves described as
  `gender.men.age.25_34`. That is an ethical question, not a technical one, and
  it is a reason some studies choose the opaque ref described
  [below](#what-an-ads-ref-carries).
- If anything replaces that text, the respondent lands in the wrong survey with
  no error anywhere. See
  [WhatsApp Surveys](/docs/fly/reference/whatsapp/) for what that looks
  like from Fly's side.
:::

## Multi (Messenger or WhatsApp)

One ad that opens **either** Messenger or WhatsApp, with Meta choosing per
respondent based on which app it predicts they are most likely to reply from.

- `Initial Shortcode`: one shortcode, for both arms — never one per channel.
- `Welcome Message`
- `Button Text`: the Messenger arm's button.
- `WhatsApp Phone Number`: as above.
- `Additional Metadata` *(optional)*

Two constraints:

- Your recruitment **Optimization Goal must be `CONVERSATIONS`**. Saving fails
  otherwise, naming both fields.
- **Your survey must work on both channels.** You cannot know which channel a
  given respondent gets, so every WhatsApp limit applies. See
  [Channels](/docs/fly/reference/channels/).

::: warning

**Do not use a multi destination to compare channels.** Meta assigns the channel
by predicted responsiveness, not at random, and channel correlates with who
people are. The two groups are not comparable and nothing in the data records how
anyone was assigned.

To compare Messenger against WhatsApp, use two single-channel destinations in a
[Destination Experiment](/docs/vlab/study-configuration/recruitment/#destination-experiment).
:::

Attribution is unaffected: one ad, one stratum, one attribution record, whichever
channel a respondent lands on. But **the channel itself is only recoverable from
the response data** (Fly records it as `platform`), never from the ad.

The WhatsApp arm of a multi ad is newer than the rest of this and has been
verified less thoroughly than the Messenger arm. On the first study that uses
one, watch arrivals on both channels before scaling the budget.

## Web

- `Url Template`: The URL of the web survey, with `{ref}` wherever you want the
  Virtual Lab ref inserted into the URL.

## App

- `Facebook App ID`: The app ID for Facebook.
- `Deeplink Template`: The deeplink template to link to the app, with `{ref}`
  wherever you want the Virtual Lab ref inserted.
- `App Install State`: The app install state, as per Facebook.
- `User Device`: The targeted devices.
- `User OS`: The targeted install states.

## What an ad's ref carries

Every recruitment ad carries a **ref**: a string that comes back to Virtual Lab
when someone clicks it. The ref is how a respondent is connected back to the ad
that recruited them, and therefore to their stratum.

The destination form asks one question about it:

> **Where does this ad's stratum data end up?**
>
> - *In the data itself — gender and region arrive as columns*
> - *Looked up afterwards, from the ad-attributions export*

### In the data itself (the default)

The ref spells out the stratum:

```
creative.StaticHausa.gender.men.Age.25_34.form.mnchweek
```

Every value travels with every message, and arrives as metadata on the
respondent's record. Your export already has `gender` and `Age` as columns and
there is nothing to join.

This is how Virtual Lab has always worked, and it is what a study with no setting
saved does. Choose it when:

- your Fly survey **branches on ad metadata** — logic jumps that read `creative`
  or `gender` need the values present in the conversation; or
- you want the simplest possible export.

### Looked up afterwards

The ref carries a short opaque token instead:

```
r.AQhtbmNod2Vla6QffA6T
```

Nothing about the respondent's stratum travels with the ad. Virtual Lab records
what each ad meant when it created it, and you join the two afterwards using the
[Ad Attributions](/docs/vlab/study-configuration/ad_attributions/) export. Choose it when:

- the ref is **visible to the respondent** — it is, on WhatsApp — and you would
  rather not describe people back to themselves;
- your stratum values contain characters that do not travel well; or
- you simply do not need the values inside the survey.

::: warning

**Choosing this also requires a matching Data Extraction setting.** The two are
independent settings and neither checks the other, so it is possible to save one
without the other — and a study that thins its ref without reading the ad lookup
has *no* stratification data at all. Every stratum counts zero and the optimizer
spends on nothing.

Set both, or neither. See
[Data Extraction](/docs/vlab/study-configuration/data_extraction/#pattern-3-looking-up-the-ad)
for the read half.
:::

### Changing it on a live study

Changing this setting changes the ad, so **every ad in the study is rewritten on
the next reconciliation run**: real spend, possibly another round of Meta review,
and the learning phase starting over. Live posts people have already shared start
pointing at the new link. The dashboard warns you before saving.

Respondents who already arrived keep the attribution they came with. Respondents
who arrived *before* the change are not retro-fitted to the new mechanism, which
is the other reason to decide this before recruitment starts rather than during
it.

## Destinations and the channel an ad opens

You do not set the channel separately. The ad set's destination type is derived
from the destinations you configured:

| Destination | Channel the ad opens |
|---|---|
| Messenger | Messenger |
| WhatsApp | WhatsApp |
| Multi | Messenger *or* WhatsApp |
| Web, App | whatever the recruitment conf's `Destination Type` says |

Two consequences:

- A [Destination Experiment](/docs/vlab/study-configuration/recruitment/#destination-experiment)
  can now have a Messenger arm and a WhatsApp arm, which was previously
  impossible.
- **A running study cannot change channel.** Ad sets are matched by name and
  persist for the study's lifetime, so the channel is fixed once recruitment
  starts.

All the creatives within one stratum must agree on the channel — Virtual Lab
refuses to build a study whose creatives disagree, rather than publishing half
its ads to the wrong place.
