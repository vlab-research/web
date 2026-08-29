---
title: Timeouts
weight: 5
---

## Timeout Types

### Absolute timeout:

An absolute timeout fires at a certain time for all survey takers. You must write the time in a SQL-recognizable format, using UTC time, like so:

JSON:

```json
{
    "type": "wait",
    "responseMessage": "Please wait!",
    "wait": {
        "type": "timeout",
        "value": {
            "type": "absolute",
            "timeout": "2021-08-01 12:00"
        }
    }
}
```

A relative timeout fires after a certain amount of time has passed for each survey taker. You must write the duration of time to pass in SQL format, like so:

### Relative timeout:

JSON:

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

Where `timeout` is written as a **whole number and a unit**: `"1 minute"`,
`"3 hours"`, `"2 days"`, `"1 week"`.

### Variable timeout:

Finally, you can create a timeout variable, if you want to be able to adjust the exact timeout length or time later. This is very valuable! Often recommended instead of absolute timeout, just in case. Note you still need to create a `type` which is `absolute` or `relative`:

JSON:

```json
{
    "type": "wait",
    "responseMessage": "Please wait!",
    "wait": {
        "type": "timeout",
        "value": {
            "type": "absolute",
            "variable": "my_timeout_var"
        }
    }
}
```

You then go to the dashboard and under the survey settings (click on the shortcode), under "Timeouts" add a timeout with the name `my_timeout_var`, pick `absolute`, and select the date and time you would like it to fire.

## Timeouts over 24 hours

**Both Messenger and WhatsApp allow ordinary messages only within 24 hours of the
respondent's last message.** To send anything after that — survey results, prize
notifications, reminders, the next wave of a longitudinal survey — you need a
**Utility Message template**, pre-approved for the account the respondent is on.

| | Messenger | WhatsApp |
|---|---|---|
| Ordinary messages | within **24 hours** of the respondent's last message | within **24 hours** of the respondent's last message |
| Outside that window | a Utility Message template, and nothing else | a Utility Message template, and nothing else |
| If you forget | the send fails and shows up as an error | the message silently does not arrive |

> Meta retired every other out-of-window mechanism in early 2026 — Message Tags
> like `CONFIRMED_EVENT_UPDATE`, Recurring Notifications, and the one-time
> "Notify Me" opt-in. Utility Messages are the replacement for all of them and
> require **no opt-in** from the respondent on either channel. See
> [Notify and recurring notifications](/docs/fly/reference/questions/#notify-and-recurring-notifications-deprecated)
> if you are reading an older survey that uses one.

### 1. Create the template in the dashboard

In the dashboard, go to **Message Templates → Create Template**. Pick the account
— a Facebook page or a WhatsApp number — name the template in `snake_case`, pick
a language, and write the body. Use `{{1}}`, `{{2}}`, etc. for any values you
will fill in at send time (e.g. the respondent's name).

**Add buttons** if you want respondents to tap instead of typing — this is almost
always what you want, since free text after a long wait creates friction and is
hard to branch on. Up to 3 buttons; labels are locked at approval and stay
visible in the chat.

A template is identified by the tuple **(account, name, language)**. The same
name can exist on several accounts and in several independently-approved language
variants. **If your study runs on both a page and a WhatsApp number, register the
template on both** — a survey names a template, not a channel, and a send to an
account with no such template fails.

Messenger typically auto-approves in seconds. WhatsApp review is real and can
take minutes to hours, so create and approve your templates before the study
starts. Wait until the row shows **Approved** before using it.

### 2. Use it in the survey after a long wait

Set up your wait step as described above (any timeout over 24 hours), then make
the next field a `utility_message`. If the template has buttons, the field must
be a **Multiple Choice** question whose choices match the approved button labels
— buttons are NOT declared in the JSON, they come from the question's choices. If
the template is text-only, use a **Statement** question.

```json
{
  "type": "utility_message",
  "template": "results_ready",
  "language": "en_US",
  "params": ["{{hidden:name}}", "$5"]
}
```

**Fields:**

| Field | Required | Notes |
|-------|----------|-------|
| `template` | Yes | The template name you created in the dashboard. |
| `language` | Yes | The locale you approved for this template variant (e.g. `en_US`, `es_LA`, `ha`). Must match exactly. No silent default — a missing language is an error. |
| `params` | Only if the body has placeholders | Positional array of values substituted into `{{1}}`, `{{2}}`, etc. in template order. Supports `{{hidden:X}}` interpolation. Length must equal the placeholder count. |

The `params` array corresponds 1-to-1 with the `{{N}}` placeholders in the body:
the first element fills `{{1}}`, the second fills `{{2}}`, and so on. If your
template body has 3 placeholders, pass 3 params.

For full setup details — including how the Multiple Choice question's choices map
to the approved buttons and how to branch on a tap — see the
[Utility Message question type](/docs/fly/reference/questions/#utility-message).

::: warning

**This is not optional on either channel, and there is no fallback.** A wait of
more than 24 hours followed by an ordinary Statement means the survey stops
there — visibly on Messenger, where the send errors, and silently on WhatsApp,
where nothing appears in the chat and nothing looks wrong in the dashboard.

Check every wait longer than a day. See
[WhatsApp Surveys](/docs/fly/reference/whatsapp/#the-24-hour-rule).
:::
