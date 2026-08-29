---
title: WhatsApp Surveys
weight: 1.7
---

Fly runs surveys over WhatsApp as well as Messenger. The survey itself is the
same survey — same Typeform form, same shortcode, same export. What is different
is how a respondent gets into it, and what you are allowed to send them
afterwards.

Read [Channels](/docs/fly/reference/channels/) first for the
question-by-question differences. This page is about running a study on WhatsApp:
getting a number, getting people into the survey, and staying inside WhatsApp's
messaging rules.

## Getting a number

A WhatsApp survey runs on a **WhatsApp Business number** connected to your Fly
account. Unlike a Facebook page, you cannot currently connect one yourself: tell
us the study and we will set the number up and attach it to your account.

Two consequences worth knowing before you plan a study:

- **One number belongs to one Fly account.** Every survey you create is
  reachable on your number, and no two researchers can share one. A researcher
  with many Facebook pages still needs only one WhatsApp number.
- **A study cannot change channel once recruitment starts.** The channel an ad
  opens is fixed when its ad set is created and cannot be changed afterwards, so
  decide between Messenger and WhatsApp before you launch.

The **Connect → WhatsApp Business Account** button on the Accounts screen is a
preview of self-service connection and is not the supported route yet.

## How someone starts a WhatsApp survey

On Messenger, a link carries the survey's shortcode invisibly. **WhatsApp has no
equivalent.** The only thing that can carry a shortcode into a WhatsApp
conversation is the text of the respondent's own first message.

Everything below is a way of getting the right text into that message.

### The entry reference

The text Fly is looking for is:

```
form.<shortcode>
```

optionally followed by extra key/value pairs, exactly as on Messenger:

```
form.hpvintro.creative.3b.gender.men
```

which reaches your survey as the hidden fields `creative` and `gender`.

Rules, all of which matter:

- **It must be the entire message.** `form.hpvintro` starts the survey;
  `hi, form.hpvintro` does not. A leading `start ` is allowed
  (`start form.hpvintro`). Surrounding spaces are fine.
- **Only letters, digits, `_` and `-`** in the shortcode and in each key and
  value. A space or a `/` will not be recognised.
- **Case is preserved** for the shortcode and every value; only the word `form`
  itself is case-insensitive.
- Being the whole message is what stops a respondent's own mid-survey answer
  from accidentally restarting the survey. It is deliberately strict.

Ads created by Virtual Lab may instead carry a short opaque reference that looks
like `r.AQhtbmNod2Vla6QffA6T` — this is the same thing in a compact form and is
handled automatically. See
[what an ad's ref carries](/docs/vlab/study-configuration/destination/#what-an-ads-ref-carries).

### 1. A click-to-WhatsApp ad

This is the production path, and the one place a WhatsApp study usually goes
wrong.

When someone clicks a click-to-WhatsApp ad, WhatsApp opens with a **message
already typed into their compose box**. That prefilled text comes from the ad,
and it is the only carrier of the shortcode — the referral information WhatsApp
attaches to the click contains nothing that names your survey.

::: warning

**The ad's autofill message must be the entry reference, and nothing else.**

If the ad prefills a friendly greeting — "Hi, I'd like to know more" — then
every single person who clicks it starts
[the default form](/docs/fly/reference/default_response/) instead of
your survey. Nothing errors. Those respondents answer whatever the default form
asks and look like completions, while your study shows almost no arrivals.

If you create your ads through Virtual Lab this is set for you. If you or an
agency create them by hand, this is the field to check first, and to check on a
real phone before spending anything.
:::

Two more things about ad clicks:

- **The respondent can edit the prefilled text before sending it**, and some do.
  A study will always have a few arrivals that lost their reference this way.
- **Click-to-WhatsApp works on mobile only.** Someone clicking your ad on
  WhatsApp Web or Desktop arrives without the ad context.

### 2. A `wa.me` link

For a link you can put in an email, a poster or a WhatsApp message:

```
https://wa.me/<number>?text=form.<shortcode>
```

`<number>` is your WhatsApp number in international form with no `+`, spaces or
dashes. Tapping the link opens a chat with the message prefilled; the respondent
presses send.

- **Only `text=` survives.** Any other query parameter you add — `ref=`,
  `id=`, anything — is silently dropped before it reaches us. There is nowhere
  else to put a reference.
- **Percent-encode `&` and `#`** if a value ever contains one, or the message is
  silently cut short at that character.
- **On a desktop browser** the link shows an interstitial page and needs a second
  click.
- **The respondent sees and can edit the text.** If you are carrying targeting
  values in the reference, they can read them.

A QR code that opens a chat is the same mechanism with a different wrapper, and
carries no extra information.

### 3. Typing it

Anyone can start a survey by sending `form.<shortcode>` to the number by hand.
This is how you test, and it is why shortcodes must stay typeable — a hand-typed
space is a literal space and will not match.

### What a WhatsApp number does *not* do

A message to the number that is **not** an entry reference and does not belong to
a conversation in progress gets **no reply at all**. Someone who writes "hello"
to the number is ignored.

That is deliberate — a WhatsApp business number is not a broadcast channel — but
it does mean a respondent who mistypes the reference gets silence rather than
help. Expect a small number of arrivals to be lost this way, and make the entry
reference easy to send correctly rather than easy to type from memory.

## Testing a WhatsApp survey

Before an ad exists, and before any money is spent:

1. Create your form and give it a shortcode as usual.
2. From your own phone, open `https://wa.me/<number>?text=form.<shortcode>`, or
   just send `form.<shortcode>` to the number.
3. Answer the survey.

That exercises the whole path — WhatsApp, Fly and back — and is the only way to
find the channel-specific failures on the
[Channels](/docs/fly/reference/channels/) list before your respondents
do. Watch the [Monitor tab](/docs/fly/reference/monitoring/) while you
do it.

**Fly does not let anyone take a survey twice.** To test the same form again, use
the reset reference your administrator gave you, exactly as on Messenger. See
[Testing](/docs/fly/reference/testing/).

To test the ad itself, there is no substitute for clicking a real ad on a real
phone and **reading the compose box before pressing send**. That text is the
whole configuration.

## The 24-hour rule

WhatsApp only allows a business to send an ordinary message **within 24 hours of
the respondent's last message**. Outside that window, only a **pre-approved
template** will send. There is no exception and no fallback: an ordinary message
sent outside the window does not arrive.

Messenger now has the same rule — Meta retired its opt-in alternatives in early
2026 — so this is not a WhatsApp tax you can design around by choosing the other
channel. What is different here is that a mistake is **silent**: on Messenger the
failed send shows up as an error in the
[Monitor tab](/docs/fly/reference/monitoring/), on WhatsApp the message
simply never arrives.

Everything in a Fly survey that reaches out to a quiet respondent is affected:

| What | Inside 24h | Outside 24h |
|---|---|---|
| The next question after their answer | fine | — |
| A [wait](/docs/fly/reference/timeouts/) of an hour or two | fine | — |
| A wait of 2 days, a week, a month | — | **needs a template** |
| The friendly follow-up nudge to a quiet respondent | fine | **needs a template** |
| A payment result that arrives late | fine | **needs a template** |

So a multi-wave WhatsApp survey looks like this:

```
[wave 1 questions]
       ↓
[wait — 3 days]
       ↓
[utility_message]  ← an approved template, not a statement
       ↓
[wave 2 questions]  ← the respondent's reply reopens the 24-hour window
```

The respondent's tap or reply on that template message reopens the window, and
the rest of the wave proceeds normally.

### Templates

Create templates in the dashboard's **Message Templates** tab, and use them with
a [`utility_message`](/docs/fly/reference/questions/#utility-message)
question. The setup is the same on both channels; what WhatsApp changes:

- **Review is real.** Messenger usually approves in seconds; a WhatsApp template
  can take minutes to hours, and can be rejected for wording Messenger accepts.
  Create and approve your templates before the study starts, not during it.
- **Sample values are required** for every `{{1}}`, `{{2}}` placeholder.
- **Buttons stay visible** in the chat and their labels are locked at approval —
  your question's choices must match them exactly, in the same order.
- A template is registered per messaging account. If a study runs on both a
  Facebook page and a WhatsApp number, **register the same template name on
  both** — the survey names a template, not a channel. The **Duplicate** action
  in the template list copies one to another account so the shapes stay in
  agreement.
- **Approved templates cannot be edited.** Delete and recreate to change wording.
  A name freed by deleting an *approved* template stays reserved for 30 days; a
  rejected one can be reused immediately.

## How many messages you can send

Only messages sent **outside** the 24-hour window count against WhatsApp's
quota — that is, template messages. Survey starts and the whole back-and-forth
of an active conversation are free.

A new number starts at **250 unique recipients per 24 hours** outside the window,
rising to 2,000 and beyond as the number builds a delivery history at good
quality. In practice:

- A study whose respondents answer promptly consumes almost none of it.
- A study that leans on long waits and follow-up nudges can exhaust 250 per day
  at a few hundred respondents.

If your design sends a template to every respondent on a schedule, tell us the
expected volume before you start, so the number is on a high enough tier.

There is also a hard rate of **one message every 6 seconds to the same person**,
which matters only if a survey tries to send several messages in a burst.

## What is not supported on WhatsApp

- **Receiving photos, files or voice notes from respondents.** See
  [Upload](/docs/fly/reference/questions/#upload-receiving-files-from-respondents).
- **Shared locations and contact cards.** They arrive and are ignored.
- **[Notify](/docs/fly/reference/questions/#notify-and-recurring-notifications-deprecated)
  questions and one-time notifications.** These never existed on WhatsApp, and
  Meta retired them on Messenger in early 2026. Use a template on both.
- **[Handoff](/docs/fly/reference/questions/#passing-thread-control-handoff)
  to another app.** WhatsApp has no thread control.
- **More than 10 choices on a question**, and a link button label longer than 20
  characters — both are send failures. See
  [Channels](/docs/fly/reference/channels/).
