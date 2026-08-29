---
title: Channels
weight: 1.6
---

A Fly survey is written once and can run on more than one messaging app. The
questions, the logic, the timeouts, the payments and the exported data are the
same whichever app a respondent is using — but the apps themselves are not the
same, and a handful of differences will stop a survey that works on one from
working on the other.

This page is the list of those differences. Read it before you write a survey
that will run on WhatsApp.

## The channels

| Channel | Status | A respondent is identified by |
|---|---|---|
| **Messenger** | Live | a Facebook page-scoped id (PSID) — different on every page |
| **WhatsApp** | Live | their phone number, in international form without the `+` |
| **Instagram** | Not available | — |

Instagram appears in a few places in this documentation and in the dashboard.
There is no way to run a survey on it today: nothing receives Instagram
messages. Treat it as not supported.

**A survey does not choose its channel.** A form has a shortcode, and the same
shortcode can be started on either channel. What decides the channel is how the
respondent arrived — which page or which WhatsApp number they were sent to. One
form can therefore serve a Messenger arm and a WhatsApp arm of the same study at
once, and the channel each respondent used is recorded with their answers.

::: note

The channel is recorded as the hidden field `platform`, with the value
`messenger` or `whatsapp`. You can branch on it in Typeform logic like any other
hidden field, and add it as a column when you export. See
[Hidden Fields](/docs/fly/reference/hidden/).
:::

## The differences that break surveys

These are the ones worth checking before you launch. Everything in this section
is a **send failure or a hard limit**, not a matter of taste.

### Number of choices

| Platform | Choices | How it looks |
|---|---|---|
| Messenger | up to 13 | quick replies above the keyboard |
| WhatsApp | 1–3 | buttons under the message |
| WhatsApp | 4–10 | a tappable list |
| WhatsApp | **more than 10** | **the message fails to send** |

An 11-point Opinion Scale (0–10) is eleven options and will fail on WhatsApp.
Use 0–9 or 1–10.

**If your survey may ever run on WhatsApp, keep every Multiple Choice, Dropdown,
Picture Choice, Rating and Opinion Scale question to 10 options or fewer.**

### Button labels on links and videos

The `buttonText` of a [tracked link, video or plain
link](/docs/fly/reference/questions/#tracked-links) is capped at
**20 characters on WhatsApp**, and a longer one does not get truncated — the
whole message is rejected and the respondent's survey stops with an error.

Messenger has no such cap. **A `buttonText` that has worked on Messenger for
years can stop a WhatsApp survey the first time it is sent.**

### Phone, email and SMS links

`tel:`, `mailto:` and `sms:` destinations work on WhatsApp **only** through a
[tracked link](/docs/fly/reference/questions/#tracked-links)
(`"type": "link_tracking"`), which turns them into an ordinary web link that
redirects. A hand-written
[`webview`](/docs/fly/reference/questions/#plain-links) pointing
straight at `tel:` is an error on WhatsApp.

On Messenger both forms work. Use `link_tracking` and the question works on both.

### Captions on attachments

On **WhatsApp**, an attachment question's Typeform title is sent as the caption
and appears with the image, video or document. On **Messenger** there is no
caption and the title is not shown at all — if the text matters, send it as a
separate Statement before the attachment.

For documents, the **filename is what a WhatsApp respondent sees**. Name the file
properly before uploading it to the Media library.

`attachment_id` — the old way of referencing a file pre-uploaded to a Facebook
page — does nothing on WhatsApp and will fail to send. Use a
[Media Library](/docs/fly/reference/media/) URL instead.

### Messaging after 24 hours

Both platforms restrict what you may send to someone who has not written to you
recently, and both solve it the same way: a **pre-approved template**, created
in the dashboard's **Message Templates** tab and used with a
[`utility_message`](/docs/fly/reference/questions/#utility-message)
question.

**The window is 24 hours on both.** What differs is how the template gets
approved, and what a mistake looks like:

| | Messenger | WhatsApp |
|---|---|---|
| Ordinary messages | within **24 hours** of the respondent's last message | within **24 hours** of the respondent's last message |
| Outside that window | a Utility Message template, and nothing else | a Utility Message template, and nothing else |
| Approval | usually instant | a real review; minutes to hours, and stricter about wording |
| Counted against a sending quota | no | yes — see [WhatsApp](/docs/fly/reference/whatsapp/#how-many-messages-you-can-send) |
| If you forget the template | the send fails and shows up as an error | the message silently does not arrive |

So any [wait](/docs/fly/reference/timeouts/) longer than 24 hours, any
follow-up nudge and any delayed payment result needs an approved template on
**either** channel. A survey whose long waits are followed by ordinary statements
stops there for every respondent — noisily on Messenger, silently on WhatsApp.

::: note

**On Messenger this used to be avoidable, and no longer is.** Message Tags,
Recurring Notifications and the one-time "Notify Me" opt-in were all retired by
Meta in early 2026. A pre-approved template is now the only way to reach a
Messenger respondent outside the window, exactly as on WhatsApp. See
[Notify and recurring notifications](/docs/fly/reference/questions/#notify-and-recurring-notifications-deprecated).
:::

### Features that exist on one channel only

| Feature | Messenger | WhatsApp |
|---|---|---|
| [Handoff](/docs/fly/reference/questions/#passing-thread-control-handoff) to another app | Yes | **No** — WhatsApp has no thread control |
| Persistent [Button Choice](/docs/fly/reference/questions/#button-choice) | Yes | Behaves as an ordinary 3-option question |
| Sharing a location or a contact card | — | Received but ignored; there is no question type for it |

### Receiving files from respondents

Not supported on either channel. See
[Upload](/docs/fly/reference/questions/#upload-receiving-files-from-respondents).

## The differences that do not matter

Worth stating so you do not go looking for them:

- **Question types.** Every question type other than `handoff` behaves the same
  way. You do not write a WhatsApp version of a question.
- **Media.** One [Media Library](/docs/fly/reference/media/) URL works
  on every channel and every connected account. There is no per-channel upload.
- **Hidden fields, logic jumps, seeds and validation.** Identical.
- **Timeouts, bails and payments.** Identical, subject to the 24-hour rule above.
- **Exports.** One export contains every respondent, whichever channel they came
  through, with `platform` available as a column.
- **Custom messages.** The Typeform messages listed under
  [Messages](/docs/fly/reference/messages/) are used on both.

## How respondents start a survey

This is the biggest practical difference between the two, because on WhatsApp
there is no link you can simply hand out that carries a shortcode invisibly.

| | Messenger | WhatsApp |
|---|---|---|
| A link you can share | `m.me/<page>?ref=form.<shortcode>` | `wa.me/<number>?text=form.<shortcode>` — but the respondent sees the text and can edit it |
| From an ad | the ad's welcome message carries the reference invisibly | the ad **prefills the respondent's first message** with the reference, and that is the only carrier |
| By hand | not really possible | anyone can type `form.<shortcode>` to the number |

The consequence on WhatsApp is that **the entry reference must be set as the
ad's autofill message**, and if it is not, every person who clicks the ad starts
[the default form](/docs/fly/reference/default_response/) instead of
your survey — with no error anywhere. This is the single easiest and most
expensive way to misconfigure a WhatsApp study.

The full account is on [WhatsApp Surveys](/docs/fly/reference/whatsapp/).

## One ad, either channel

Virtual Lab can create a **multi-destination ad** that opens either Messenger or
WhatsApp, with Meta choosing per respondent. One ad, one survey shortcode, and
respondents arriving on both channels.

Two things follow, and both matter for survey design:

1. **Your survey must work on both channels** — every limit on this page applies,
   because you do not know which channel any given respondent will get.
2. **You cannot use it to compare channels.** Meta assigns the channel by
   predicted responsiveness, not at random, so the two groups are not comparable.
   To compare channels, run two separate destinations in a destination
   experiment. See
   [Destinations](/docs/vlab/study-configuration/destination/).

## A pre-launch checklist for a WhatsApp survey

1. No question offers more than 10 choices.
2. Every `buttonText` is 20 characters or fewer.
3. Every `tel:`, `mailto:` or `sms:` destination uses `link_tracking`, not
   `webview`.
4. Every wait longer than 24 hours is followed by a `utility_message` with an
   approved template on the number's account.
5. No `handoff` questions on the path a WhatsApp respondent takes, and no
   `notify` questions anywhere — it is retired on Messenger too.
6. Attachment titles read as captions, and document filenames read as filenames.
7. The ad's autofill message is the entry reference, verbatim.
8. You have started the survey yourself, from a real phone, before spending
   anything. See [Testing](/docs/fly/reference/testing/).
