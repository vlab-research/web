---
title: Question Types
weight: 4
---

Every question in a Fly survey is written in Typeform. Simple questions are just
Typeform question types — you pick "Short Text" and you are done. Everything
richer (a video, a tracked link, a wait, a payment) is configured by putting a
small block of JSON in the Typeform question's **Description** box.

This page lists every question type Fly supports, with a complete example of
each. Copy the examples as they are written here.

A survey can run on Messenger or on WhatsApp, and a few of the types below
behave differently — or fail outright — on one of them. Those differences are
called out where they arise, and collected in one place under
[Channels](/docs/fly/reference/channels/).

## Where you write question settings

**In the Typeform question's Description box.** There is nowhere else. The Fly
dashboard does not have a question editor — its "create survey" flow just picks
one of your existing Typeform forms, gives it a shortcode, and imports it. To
change a question you edit it in Typeform and re-import the form.

Open the question in the Typeform editor, find the **Description** field
underneath the question title, and paste the JSON in:

```json
{"type": "webview", "url": "https://www.who.int/hpv", "buttonText": "Read more"}
```

Three things about that box are not obvious, and they cause most of the problems
researchers run into.

### The `type` key replaces the Typeform question type

If the JSON in the Description box has a `"type"`, that is the question type Fly
uses, and Typeform's own question type is ignored. A Typeform **Statement**
whose description says `{"type": "moviehouse", "videoId": "164118668"}` is a
video question, not a statement.

This means Typeform's question type only decides how the question looks *in the
Typeform editor*. When a type below says "In Typeform, pick Statement", that is
a convention for keeping your form readable — the `"type"` in the description is
what actually decides the behaviour.

Settings that do **not** change the question type — `validate`, `keepMoving`,
`wait`, `responseMessage` — are written without a `"type"` key, and the Typeform
question type is kept.

### It has to be valid JSON, or it is ignored in silence

If the Description box does not parse, Fly does not warn you and does not fail.
It keeps the question as its plain Typeform type and throws your whole
configuration away. A video question quietly becomes a statement.

Before saving, check that every string is in double quotes, every key/value pair
is separated by a comma, and the braces balance. If a question is behaving as if
its description were not there, a JSON error is the first thing to suspect.

### Typeform turns pasted URLs into links

When you paste `https://www.who.int/hpv` into a Typeform description, Typeform
may rewrite it as `[www.who.int/hpv](https://www.who.int/hpv)`. Fly unwraps that
back to the plain URL for you, so a pasted link is safe — **as long as it is
inside double quotes**, which it always is when you write JSON. This is the main
reason to write JSON here rather than anything looser.

### Referring to other answers

Question titles and descriptions can both refer to values you already have:

- `{{hidden:id}}` — a hidden field
- `{{field:some_ref}}` — the answer to an earlier question

These are substituted before the description is read, so you can build values
out of them. Inside a URL they are escaped for you, so an answer containing a
space or an `&` will not break the link. See
[Hidden Fields](/docs/fly/reference/hidden/) for the full list of what
you can refer to and the transforms you can apply.

## Every question type at a glance

| What you want | In Typeform, pick | In the Description box |
|---|---|---|
| A free text answer | Short Text / Long Text | nothing |
| A number | Number | nothing, or `validate` |
| An email address | Email | nothing |
| A phone number | Phone Number | nothing |
| A date | Date | nothing |
| A list of choices | Multiple Choice | nothing |
| Up to 3 persistent buttons | Multiple Choice | `{"type": "button_choice"}` |
| A picture or dropdown list | Picture Choice / Dropdown | nothing |
| Yes or No | Yes/No | nothing |
| Accept or decline | Legal | nothing |
| A 1–5 or 1–10 scale | Opinion Scale / Rating | nothing |
| A message with no question | Statement | nothing |
| An opening message | Welcome Screen | nothing |
| To end the survey | Ending / Thank You Screen | nothing |
| To send an image, video, audio or document | Statement | `{"type": "attachment", ...}` |
| A link whose clicks you record | Statement | `{"type": "link_tracking", ...}` |
| A video whose watching you record | Statement | `{"type": "moviehouse", ...}` |
| A plain link to someone else's page | Statement | `{"type": "webview", ...}` |
| To pause the survey | Statement | `{"type": "wait", ...}` |
| To message after 24 hours | Statement or Multiple Choice | `{"type": "utility_message", ...}` |
| To ask permission to message later — **deprecated**, [use a template](#utility-message) | Statement | `{"type": "notify"}` |
| To move to another form | Statement | `{"type": "stitch", ...}` |
| To send money | Statement | `{"type": "wait", "payment": {...}}` |
| To hand the chat to another app | Statement | `{"type": "handoff", ...}` |

## Short Text and Long Text

A free text answer. Whatever the respondent types is accepted.

In Typeform, pick **Short Text** or **Long Text**. Nothing goes in the
description. The two behave identically in a chat — the difference only exists
in Typeform.

## Number

Accepts a number and nothing else. If the respondent types anything that is not
a number, they are asked the question again.

In Typeform, pick **Number**. Nothing needs to go in the description.

Numbers written in non-Latin numerals — Arabic-Indic (`٤٢`), Devanagari (`४२`),
Bengali, Thai and others — are understood and recorded as ordinary digits, so
you do not need to ask respondents to switch keyboards.

To restrict what counts as a valid answer, add a `validate` block. Note there is
no `"type"` key here: you are adding a rule to a Number question, not changing
what kind of question it is.

```json
{"validate": {"min": 18, "max": 120, "integer": true}}
```

| Setting | Effect |
|---|---|
| `min` | Answers below this are rejected. |
| `max` | Answers above this are rejected. |
| `integer` | `true` rejects anything with a decimal part. |
| `locale` | How to read grouping and decimal marks — `"en-US"` (default) reads `1,234.5`; `"de-DE"` reads `1.234,5`. |

The message a respondent gets when their answer is rejected is set for the whole
survey, not per question — see [Messages](/docs/fly/reference/messages/).

## Email

Accepts a valid email address and nothing else.

In Typeform, pick **Email**. Nothing goes in the description.

## Phone Number

Accepts a real, dialable phone number.

In Typeform, pick **Phone Number**. Nothing goes in the description.

**The number must carry its country code.** `+2348012345678` is accepted;
`08012345678` is not, because Fly has no way to know which country it belongs
to. Say so in the question text — "Please include your country code, e.g.
+234…" — or you will lose answers.

When you pass a phone answer to a payment provider, use the `|e164` transform
(`{{field:phone|e164}}`) so trailing text the respondent typed does not travel
with the number. See [Hidden Fields](/docs/fly/reference/hidden/).

## Date

Sends the question and accepts the respondent's reply as text.

In Typeform, pick **Date**. Nothing goes in the description.

**Fly does not check the format.** Whatever the respondent types is accepted and
recorded exactly as typed, so ask for the format you want in the question text
("Please write the date as DD/MM/YYYY") and expect to clean the answers
afterwards. If you need a checked answer, ask for day, month and year as three
Number questions instead.

## Multiple Choice

A list of choices the respondent picks from by tapping.

In Typeform, pick **Multiple Choice**. Nothing goes in the description. The
answer recorded is the choice's **label** — the text the respondent saw.

**How many choices you can have depends on the platform:**

| Platform | Number of choices | How it looks |
|---|---|---|
| WhatsApp | 1–3 | Buttons under the message |
| WhatsApp | 4–10 | A tappable list |
| WhatsApp | more than 10 | **The message fails to send** |
| Messenger | up to 13 | Quick replies above the keyboard |

If your survey runs on WhatsApp, keep every Multiple Choice question to **10
choices or fewer**. The same limit applies to Dropdown, Picture Choice, Rating
and Opinion Scale — see [Channels](/docs/fly/reference/channels/).

**If any choice is longer than about 15 characters**, tapping becomes unreliable
and the labels get cut off. Use letters as the choices and put the real text in
the question:

```
Which region do you live in?
-A. North Central (Middle Belt)
-B. North East
-C. North West
-D. South East
-E. South South (Niger Delta)
-F. South West
```

and then make the Typeform choices `A`, `B`, `C`, `D`, `E`, `F`. The `-` and the
`.` around the letters are optional but make the message easier to read.

## Button Choice

The same as Multiple Choice, but on Messenger the options are sent as buttons
that stay in the conversation instead of quick replies that vanish as soon as
one is tapped.

In Typeform, pick **Multiple Choice**, and put this in the description:

```json
{"type": "button_choice"}
```

Limits:

1. **Three buttons maximum** — this is a Facebook limit. With more than three
   options, use Multiple Choice.
2. Button labels are cut off at 20 characters.
3. The message text is limited to 640 characters.

On WhatsApp a Button Choice question is identical to a Multiple Choice question
with three options, since WhatsApp already sends three-option questions as
buttons.

## Dropdown and Picture Choice

Both behave exactly like Multiple Choice in a chat: the choice labels are sent
as tappable options and the label is recorded as the answer. **Pictures are not
sent** — only the labels — so use Picture Choice only if you are also using the
same form outside Fly.

In Typeform, pick **Dropdown** or **Picture Choice**. Nothing goes in the
description. The platform limits under Multiple Choice apply.

## Yes/No

A two-option question. The answer recorded is `Yes` or `No`.

In Typeform, pick **Yes/No**. Nothing goes in the description.

## Legal

A two-option question for consent. The answer recorded is `I Accept` or
`I don't Accept`.

In Typeform, pick **Legal**. Nothing goes in the description. Branch on the
answer with a Typeform logic jump in the usual way.

## Opinion Scale and Rating

A numbered scale sent as tappable options.

In Typeform, pick **Opinion Scale** or **Rating**, and set the number of steps
there. Nothing goes in the description.

The options are the numbers themselves: a 5-step scale sends `1 2 3 4 5`. If you
turn Typeform's "start at 1" setting off, it sends `0 1 2 3 4` instead. The
answer recorded is the number the respondent tapped.

**On WhatsApp, a scale can have at most 10 steps.** An 11-point scale (0–10) is
11 options, which is over WhatsApp's limit and will fail to send. Use 0–9 or
1–10.

## Statement

A message that is sent without asking anything. The survey moves straight on to
the next question.

In Typeform, pick **Statement**. Nothing goes in the description.

If you want a statement to pause the survey rather than continue, that is a
[Wait](#wait), which is a different question type — a `wait` added to a plain
Statement is ignored.

## Welcome Screen

The first message of the form. It is sent as a question with a single button,
labelled with whatever button text you set in Typeform (`Continue` if you set
none). The respondent taps it to begin.

In Typeform, add a **Welcome Screen**. Nothing goes in the description.

## Ending (Thank You Screen)

The last message. It is sent, and then the respondent's survey is marked
complete.

In Typeform, add an **Ending** / Thank You Screen. Nothing goes in the
description.

Only the **first line** of the ending's text is sent — Typeform adds its own
boilerplate below it, and that is dropped. Keep the whole message on one line.

## Attachments: Image, Video, Audio, Document

An attachment question sends a file to the respondent. All four kinds share one
shape — only `attachment.type` changes:

```json
{"type": "attachment",
 "keepMoving": true,
 "attachment": {
    "type": "image",
    "url": "https://media.vlab.digital/a/550e8400-e29b-41d4-a716-446655440000/welcome.png"
 }
}
```

In Typeform, pick **Statement**.

The `url` is what you get by uploading the file in the dashboard's **Media** tab
and clicking to copy it — see [Media Library](/docs/fly/reference/media/).
The same URL works on WhatsApp, Messenger and Instagram; there is nothing
per-platform to configure.

`keepMoving: true` sends the attachment and moves straight on to the next
question without waiting for a reply. Leave it out if you want the respondent to
answer something before the survey continues.

### The four types

| `type` | Formats | Maximum size |
|---|---|---|
| `image` | JPEG, PNG | 5 MB |
| `video` | MP4, 3GPP | 16 MB |
| `audio` | AAC, M4A, MP3, AMR, OGG | 16 MB |
| `file` | PDF, DOCX, XLSX, PPTX | 100 MB |

Note that documents use `"type": "file"`, not `"document"`:

```json
{"type": "attachment",
 "keepMoving": true,
 "attachment": {
    "type": "file",
    "url": "https://media.vlab.digital/a/1f2e3d4c-5b6a-4978-8695-a4b3c2d1e0f9/consent-form.pdf"
 }
}
```

On WhatsApp, the **filename in the URL is what the respondent sees** when the
document arrives — so name the file properly before you upload it.

GIF and WebP images are not supported: convert them to PNG, JPEG, or MP4.

### Captions

On **WhatsApp**, the Typeform question title is sent as the caption, so it
appears with the image, video or document. On **Messenger and Instagram** the
platform supports no caption and the title is not shown — if the text matters
there, send it as a separate Statement.

### Using your own URL

Any public HTTPS URL works in place of a Media library one:

```json
{"type": "attachment",
 "keepMoving": true,
 "attachment": {
    "type": "image",
    "url": "https://example.org/my-image.png"
 }
}
```

It has to stay publicly reachable for the life of the survey, and it has to
respect the formats and limits above — neither of which we can check for you
until the moment we send. Uploading to the Media library avoids both problems
and sends faster.

::: warning

**`attachment_id` is deprecated.** Older surveys pre-uploaded a file to a
Facebook page and referenced it by id:

```json
{"attachment": {"type": "image", "attachment_id": "3656576331230635"}}
```

That still works on Messenger for surveys that already use it, but it does
**nothing on WhatsApp** — that message will fail to send on any WhatsApp number.
It is also no longer any faster: files in the Media library are pre-uploaded to
your connected accounts automatically. Use a Media library URL instead.
:::

## Upload (receiving files from respondents)

::: warning

**Not currently supported — do not use this question type.**

Fly can record that a respondent sent a photo or file, but it does not store the
file itself. What lands in your exported data is a reference that expires at
WhatsApp (7 days) or Messenger (about 30 days), after which it resolves to
nothing and the file is unrecoverable.

If collecting files from respondents matters for your study, talk to us before
designing around it.
:::

## Tracked links

Sends a link as a button and records who clicked it and when. You write the
destination; Fly builds the rest of the link.

In Typeform, pick **Statement**, and put this in the description:

```json
{
  "type": "link_tracking",
  "url": "https://www.who.int/hpv",
  "buttonText": "Read about HPV",
  "keepMoving": true
}
```

That is the whole question.

::: note

**`link_tracking` is new as of 18 August 2026.** Surveys written before this
date send links a different way — see [Plain links](#plain-links) — and they
keep working exactly as they do now.
:::

::: warning

**Do not put an account id, page id, phone number id or user id anywhere in a
tracked link.** There is nowhere for one to go, and nothing to copy from another
survey. Fly already knows which participant it is talking to and on which
account, and it puts that into the link itself. Anything of that kind that you
add by hand is ignored at best, and at worst attaches the click to the wrong
conversation.
:::

| Setting | Required | What it does |
|---|---|---|
| `url` | Yes | Where the button sends the respondent. Write the full address, in quotes. |
| `buttonText` | No | The label on the button. **20 characters maximum.** On Messenger a longer label is cut off; on WhatsApp the message fails to send. Defaults to `View website`. |
| `keepMoving` | No | `true` sends the message and continues to the next question immediately. |
| `wait` | No | Hold the survey until the respondent clicks. See [below](#waiting-for-a-click-or-a-play). |
| `responseMessage` | No | What to reply with if the respondent types something instead of tapping the button. |

The question title is the message text; `buttonText` is the button under it.

### Phone, email and SMS buttons

`tel:`, `mailto:` and `sms:` destinations work the same way and are recorded the
same way. Write the whole thing in the `url`:

```json
{
  "type": "link_tracking",
  "url": "tel:+2340700220112",
  "buttonText": "Call the helpline",
  "keepMoving": true
}
```

```json
{
  "type": "link_tracking",
  "url": "mailto:support@example.org",
  "buttonText": "Email us",
  "keepMoving": true
}
```

Whether the respondent's phone actually opens a dialler or a mail app is up to
their phone. The click is recorded either way.

**This is the only way to send one of these on WhatsApp.** A tracked link becomes
an ordinary web address that redirects, which WhatsApp accepts; a `tel:` written
straight into a [plain link](#plain-links) does not send there at all.

## Videos

Plays a video and records what the respondent does with it — every play, pause,
seek and finish, plus a signal every 30 seconds while it is playing. You write
the video id; Fly builds the rest.

In Typeform, pick **Statement**, and put this in the description:

```json
{
  "type": "moviehouse",
  "videoId": "164118668",
  "buttonText": "Watch the video",
  "keepMoving": true
}
```

::: note

**`moviehouse` is new as of 18 August 2026.** Surveys written before this date
send videos a different way — see [Plain links](#plain-links) — and they keep
working exactly as they do now.
:::

::: warning

**Do not put an account id, page id, phone number id or user id anywhere in a
video question.** There is nowhere for one to go, and nothing to copy from
another survey. Fly knows which participant is watching and on which account.
A hand-written id is how video events end up attached to the wrong conversation
— sometimes to a conversation that does not exist, in which case that
respondent's survey stops dead and never recovers.
:::

The `videoId` is the number in the Vimeo address: `https://vimeo.com/164118668`
is `164118668`. **Keep it in quotes**, as above.

| Setting | Required | What it does |
|---|---|---|
| `videoId` | Yes | The Vimeo video id, in quotes. |
| `buttonText` | No | The label on the button. **20 characters maximum** — on WhatsApp a longer label makes the message fail to send. Defaults to `View website`. |
| `keepMoving` | No | `true` sends the message and continues to the next question immediately. |
| `wait` | No | Hold the survey until the respondent plays the video. See [below](#waiting-for-a-click-or-a-play). |
| `responseMessage` | No | What to reply with if the respondent types something instead of tapping the button. |

You do not choose which video player to use, and you do not need to know whether
the survey is running on WhatsApp or Messenger. Fly handles both.

### What a video records

| Event | Happens when |
|---|---|
| `moviehouse:play` | The respondent starts, or resumes, the video |
| `moviehouse:pause` | They pause it |
| `moviehouse:ended` | The video reaches the end |
| `moviehouse:seeked` | They jump to another point |
| `moviehouse:heartbeat` | Every 30 seconds while the video is playing |
| `moviehouse:volumechange` | They change the volume |
| `moviehouse:playbackratechange` | They change the speed |
| `moviehouse:error` | The video fails to load or play |

All of these are recorded whether or not you wait on any of them, so you can
analyse watching behaviour afterwards without changing the question.

## Waiting for a click or a play

A tracked link or a video can hold the survey until the respondent actually
clicks or actually plays. Replace `keepMoving` with a `wait`:

```json
{
  "type": "moviehouse",
  "videoId": "164118668",
  "buttonText": "Watch the video",
  "responseMessage": "Please watch the video before continuing.",
  "wait": {
    "type": "external",
    "value": {"type": "moviehouse:play"}
  }
}
```

and for a link:

```json
{
  "type": "link_tracking",
  "url": "https://www.who.int/hpv",
  "buttonText": "Read about HPV",
  "responseMessage": "Please open the link before continuing.",
  "wait": {
    "type": "external",
    "value": {"type": "linksniffer:click"}
  }
}
```

Leave the `value` as short as it is written above. `{"type": "linksniffer:click"}`
matches the click on this question's own button, and `{"type": "moviehouse:play"}`
matches a play of this question's own video. There is nothing else to fill in.

::: warning

**A respondent who never clicks never continues.** A `wait` holds the survey on
this question until the click or the play happens: if the respondent closes the
message, ignores it, or their phone refuses to open the link, they stop here.

So use a `wait` only where the click really is required, and plan for the people
who never do it — a [Bail](/docs/fly/reference/bails/) picks up
everyone who has been sitting on the same question too long and moves them
somewhere else. Otherwise use `keepMoving: true` and use the recorded clicks and
plays to analyse who engaged.
:::

**Set `keepMoving` or `wait`, never both.** They ask for opposite things — one
continues immediately, the other holds the survey until the respondent acts — so
every question uses one or the other.

## Plain links

For a link to a page that is not ours, and whose clicks you do not need
recorded, use `webview`. It sends exactly the address you write, with nothing
added:

```json
{
  "type": "webview",
  "url": "https://asiapacific.unwomen.org/en/countries/india",
  "buttonText": "Visit UN Women",
  "extensions": false,
  "keepMoving": true
}
```

In Typeform, pick **Statement**.

`keepMoving`, `responseMessage` and `buttonText` mean the same as they do above.
There is no click to wait on, because nothing is recorded — if you want to know
who clicked, use a [tracked link](#tracked-links) instead.

Set `extensions` to `true` only if the page you are linking to uses Messenger
Extensions **and** its domain is whitelisted in your Facebook app. If it is not
whitelisted, the button will not open. For most links, `false` is correct. It has
no effect on WhatsApp.

**On WhatsApp a plain link must be an ordinary web address.** `http://` and
`https://` work, and an address with no scheme at all is treated as `https://`.
Anything else — `tel:`, `mailto:`, `sms:` — fails to send; use a
[tracked link](#tracked-links) for those. The 20-character limit on `buttonText`
applies here too, and a longer label is a send failure rather than a truncation.

::: warning

**A `webview` is never tracked, even if it points at one of our own addresses.**
If you write a `webview` whose address happens to be a Fly link or video service,
Fly sends it exactly as you typed it: it does not attach the respondent, does not
know which account the conversation is on, and does not correct an address that
has stopped working. Use [`link_tracking`](#tracked-links) or
[`moviehouse`](#videos) to get any of that.
:::

## Wait

Pauses the survey and picks it up later. This is how multi-wave surveys are
built.

In Typeform, pick **Statement**, and put this in the description:

```json
{
    "type": "wait",
    "responseMessage": "Please wait!",
    "wait": {
        "type": "timeout",
        "value": {
            "type": "relative",
            "timeout": "2 days"
        }
    }
}
```

The question title is sent as a message, then the survey stops until the timeout
fires. `responseMessage` is what a respondent gets if they write in while
waiting.

Write a relative timeout as **a whole number and a unit**: `"1 minute"`,
`"3 hours"`, `"2 days"`, `"1 week"`.

For absolute timeouts, timeouts you can change from the dashboard after the
survey is live, and everything to do with waits longer than 24 hours, see
[Timeouts](/docs/fly/reference/timeouts/).

## Waiting for an external event

Besides timeouts, a wait can be held until something happens outside the chat: a
link click, a video play, a payment result.

```json
{
  "type": "wait",
  "wait": {
    "type": "external",
    "value": {"type": "moviehouse:play"}
  }
}
```

The `value` describes which event you are waiting for. Every key you put in it
has to match the event exactly, so **write as little as you can get away with**.
`{"type": "moviehouse:play"}` waits for any play; adding `"id": "164118668"`
narrows it to that one video and will match nothing if the id is off by a
character.

For a click, `{"type": "linksniffer:click"}` on its own is what you want. If you
do add a `"url"`, write the complete destination — `https://` and the whole path,
exactly as it appears in the question.

## Notify and recurring notifications (deprecated)

::: warning

**Do not use these in new surveys.** Meta retired every opt-in-based way of
messaging a Messenger respondent outside the 24-hour window during early 2026:

| Mechanism | In a survey | Status |
|---|---|---|
| Message Tags (`CONFIRMED_EVENT_UPDATE`, …) | — | Retired April 2026 |
| Recurring Notifications / Marketing Messages | `{"type": "notification_messages"}` | Retired February 2026 |
| One-time notifications ("Notify Me") | `{"type": "notify"}` + `notifyPermission` | Retired |
| **Utility Message templates** | **`{"type": "utility_message"}`** | **The current mechanism** |

A [Utility Message](#utility-message) is now the way to reach a respondent after
the window closes, on Messenger and WhatsApp alike. It needs **no permission from
the respondent at all** — just a template approved for your account, which is
usually instant on Messenger.
:::

The rest of this section is kept so that an older survey can be read and
understood. It is not a recommendation.

### What `notify` did

A `notify` question sent Facebook's built-in "Notify Me" request, which asked the
respondent for permission to send them **one** message later. In Typeform it was
a **Statement** with:

```json
{"type": "notify"}
```

Each permission was good for a single message. Fly stored the permissions it
collected and spent one when it needed to write to somebody outside the 24-hour
window — but only if the wait asked for one:

```json
{
    "type": "wait",
    "responseMessage": "Please wait!",
    "wait": {
        "type": "timeout",
        "notifyPermission": true,
        "value": {
            "type": "relative",
            "timeout": "2 days"
        }
    }
}
```

Because it was only one message, that message had to be a **question** — the
respondent had to answer before anything else could happen, which reopened the
window. A long wait therefore looked like this:

1. a `notify` question
2. a `wait` with `notifyPermission: true`
3. a question — "would you like to answer a few more questions?"
4. a statement that stitches to the next form

It also required the permission to be enabled on the Page, under
**Page Settings → Advanced Messaging → one-time notification**.

`{"type": "notification_messages"}` was the recurring version of the same idea:
the respondent opted in once and could then be messaged on a schedule.

### What to write instead

Replace the whole four-step pattern above with a wait and a template:

```
[Wait — timeout: 2 days]
       ↓
[Utility Message]  ← a Multiple Choice question if the template has buttons
       ↓
[the rest of the survey]
```

The respondent's tap on the template reopens the 24-hour window, exactly as their
answer to the notify follow-up question used to. The difference is that nobody has
to agree to anything first, and it works the same way on WhatsApp.

See [Utility Message](#utility-message), and
[Timeouts](/docs/fly/reference/timeouts/#timeouts-over-24-hours) for the
wait itself.

## Utility Message

Sends a **pre-approved message template**. Use this for anything that has to
reach the respondent after the 24-hour messaging window has closed — survey
results, prize notifications, reminders, the second wave of a longitudinal
survey.

It works on **both Messenger and WhatsApp**, and the question you write is
identical on both. What differs is where the template is approved and how strict
the platform is about the window:

| | Messenger | WhatsApp |
|---|---|---|
| Needed for | messages more than 24 hours after the respondent's last activity | the same — and **nothing else sends** outside that window |
| Approval | usually instant | a real review, minutes to hours, and stricter about wording |
| Opt-in from the respondent | none | none |
| Buttons | stay visible in the chat | stay visible in the chat |

> Utility Messages are the current replacement for every mechanism Meta retired
> in early 2026 — Message Tags (`CONFIRMED_EVENT_UPDATE`, etc.), Recurring
> Notifications, and the one-time
> [Notify](#notify-and-recurring-notifications-deprecated) opt-in. On Messenger
> they are now the only way to message somebody after the window closes.

### 1. Create the template in the dashboard

Go to **Message Templates** in the dashboard and pick the account the template is
for — a Facebook page, or a WhatsApp number. A template is identified by the
tuple **(account, name, language)**: the same name can exist on several accounts
and in several language variants, each approved independently.

| Field | Constraint |
|-------|-----------|
| Name | `snake_case` — lowercase letters, digits, underscores. Unique per (account, language). |
| Language | Must be an exact supported locale (`en_US`, `es_LA`, `ha`, …). |
| Body | Up to **1024 characters**. Use `{{1}}`, `{{2}}`, … for positional placeholders. Numbering must start at `{{1}}` and be sequential. |
| Buttons | Optional. Up to **3 buttons**. Each label is **≤ 20 characters** and unique within the template. Buttons stay visible in the chat until the respondent taps one. |

If your body contains placeholders, the dashboard prompts for a **sample value**
per placeholder. Reviewers see the body with these values substituted in — that
is how they judge whether the content is genuinely utility and not promotional.
Samples are **not** used at send time; real values come from `params` in your
question's description. WhatsApp requires them for every placeholder.

::: note

**A survey names a template, not a channel.** If your study runs on both a
Facebook page and a WhatsApp number, register the same template name on **both
accounts** — otherwise the send fails for whichever respondents are on the
account that has no such template.

The template list is sorted by name, so the registrations of one name sit next to
each other and an *approved here, rejected there* split is visible at a glance.
Use the **Duplicate** action on a row to copy a template to another account: it
pre-fills the name, language, body and buttons, so nothing is retyped.

The **placeholder count, the button count and the button order must match across
every account** where a name is registered. Your survey supplies one `params`
array and one set of choices to all of them, so a mismatch is invisible until a
send fails. Body *wording* may differ freely — and often has to, since WhatsApp
rejects phrasing Messenger accepts.

Sample values are not copied by Duplicate; re-enter them.
:::

> **Approved templates cannot be edited.** To change wording or buttons, delete
> and recreate. A name freed by deleting an **approved** template stays reserved
> for 30 days; a **rejected** template's name can be reused immediately.

### 2. Add the question in Typeform

- **Text-only template** → use a **Statement** question.
- **Template with buttons** → use a **Multiple Choice** question whose choices
  match the template's approved button labels (same labels, same order, same
  count). Typeform's own logic editor reads those choices to drive branching.

Put this in the question's description:

```json
{
  "type": "utility_message",
  "template": "results_ready",
  "language": "en_US",
  "params": ["{{hidden:name}}", "$5"]
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `type` | Yes | Always `utility_message`. |
| `template` | Yes | The template name you created in the dashboard. |
| `language` | Yes | The exact locale of the approved variant (e.g. `en_US`, `es_LA`, `ha`). There is no default — a missing `language` is an error. |
| `params` | Only if the body has placeholders | Positional list of values substituted into `{{1}}`, `{{2}}`, …. Supports `{{hidden:X}}` interpolation. Its length must equal the placeholder count exactly. |

Note there is nothing platform-specific in the question. Fly sends the right
shape for whichever account the respondent is on.

### Branching on a button tap

Make the Multiple Choice's choice labels **exactly match** the approved
template's button labels — same labels, same order, same count. The value your
Typeform logic sees on a tap is then the same string as the label the respondent
pressed:

```
[Multiple Choice question]   description: {"type": "utility_message", "template": "results_ready", ...}
                             choices: [ "Yes", "No" ]
       ↓
   logic jump:
     if answer equals "Yes" → [show results]
     if answer equals "No"  → [thank and end]
```

If the labels do not match, or the count differs from the template's button
count, the send fails.

### Typical survey flow

Utility messages are usually sent after a long wait — that is when the 24-hour
window matters:

```
[Consent questions]
       ↓
[Wait - timeout: 3 days]
       ↓
[Utility Message] "Your {{1}} results are in, {{2}}!"   ← sent outside the 24h window
       ↓
[the rest of the wave]   ← their reply reopens the 24-hour window
```

See [Timeouts](/docs/fly/reference/timeouts/) for timeout setup, and
[WhatsApp Surveys](/docs/fly/reference/whatsapp/#the-24-hour-rule) for
what the window means in practice on WhatsApp.

### Common rejection and send errors

| What you see | What it usually means |
|---|---|
| Template stays `PENDING` indefinitely | On Messenger, refresh the page; if still stuck after an hour, delete and recreate. On WhatsApp, review genuinely takes time — wait before recreating. |
| Rejected: "promotional" / `TAG_SHOULD_BE_MARKETING` | The body was classified as marketing. Rewrite it to be transactional — confirmations, reminders, results — and remove calls-to-action like "Claim now!". |
| Rejected: missing sample values | A `{{N}}` placeholder in the body has no sample value. Provide one in the dashboard form, or remove the placeholder. |
| Send fails with "template not found" | The `(template, language)` pair in your description does not match an approved template **on the account that respondent is on**. Check the spelling, the language variant, and whether the template exists on both accounts. |
| Send fails with "placeholder count mismatch" | The `params` list length does not match the number of `{{N}}` placeholders in the body. Count and align. |
| Button-tap question has fewer or more choices than the approved template | The Multiple Choice's choice count must equal the approved button count exactly. |
| The message never arrives, and nothing errors on WhatsApp | Check whether the send was actually outside the window and whether a template was used at all — an ordinary statement after a long wait silently does not arrive on WhatsApp. |

## Stitch

Moves the respondent from this form to another one. Everything after the stitch
happens in the new form.

In Typeform, pick **Statement**, and put this in the description:

```json
{"type": "stitch",
 "stitch": {"form": "FORM_SHORTCODE"}}
```

where `FORM_SHORTCODE` is the shortcode of the form you want to move to.

The `"type"` must be `stitch`. A Statement that carries a `stitch` but no `type`
is treated as an ordinary statement and the stitch never happens.

You can also set hidden fields on the way in. They are merged into whatever the
respondent already carries, so the new form can branch on them:

```json
{"type": "stitch",
 "stitch": {"form": "FORM_SHORTCODE",
            "metadata": {"arm": "treatment", "wave": "2"}}}
```

## Payment

Read about payment question types under
[Incentive Payments](/docs/fly/reference/incentive_payments/).

## Passing Thread Control (Handoff)

**Messenger only.** WhatsApp has no equivalent of Facebook's handover protocol,
so a handoff question does nothing there — keep it off any path a WhatsApp
respondent can take.

Hands the conversation to another Facebook app (a "secondary receiver" in
Facebook's handover protocol), and picks the survey back up when that app hands
control back.

In Typeform, pick **Statement**, and put this in the description:

```json
{
  "type": "handoff",
  "handoff": {
    "target_app_id": "123456789",
    "mode": "wait",
    "metadata": {"check": "my_handoff"}
  }
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `type` | Yes | Always `handoff`. |
| `handoff.target_app_id` | Yes | The Facebook app ID of the app to hand control to. |
| `handoff.mode` | No | `wait` (the default and only supported value) — the survey waits for control to come back, then resumes. |
| `handoff.metadata` | No | Delivered to the other app when control is passed. |

### How it works

1. The question title is sent to the respondent as a message.
2. Control of the conversation passes to `target_app_id`.
3. The survey waits.
4. When the other app hands control back, the survey resumes at the next
   question.

You do **not** add a `wait` — waiting for the handback is automatic. Declare
`type: handoff` and the `handoff` block, and nothing else.

### Values coming back from the other app

Any `metadata` the other app includes when it hands control back becomes hidden
fields prefixed `e_handover_metadata_`. If the returning app sends
`{"status": "ok", "answer": "blue"}`, later questions can use
`{{hidden:e_handover_metadata_status}}` and
`{{hidden:e_handover_metadata_answer}}`. The app id that regained control is
available as `{{hidden:e_handover_target_app_id}}`.

### What the other app needs

It must be configured as a **Secondary Receiver** on the Facebook Page, and to
hand control back it calls Facebook's `pass_thread_control` API with
`target_app_id` set to the Fly app ID.
