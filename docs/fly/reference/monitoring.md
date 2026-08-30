---
title: Monitoring
weight: 11
---

The **Monitor** tab is where you watch a survey's participants as they move through it. It shows you which state every respondent is currently in, lets you filter down to the ones you care about (stuck, errored, waiting, completed), and lets you drill into a single participant's full question-and-answer transcript to diagnose what went wrong.

You reach it from the **Surveys** sidebar: click a survey, then click the **Monitor** tab at the top of the survey screen.

![Monitor tab entry](/docs/images/fly-monitor-tab.png)

The Monitor tab has two sub-tabs — **Summary** and **Respondents** — and a third **Participant Detail** view that opens when you click a row.
---

## The Summary sub-tab

The Summary view is the at-a-glance health check for a survey.

![Monitor summary](/docs/images/fly-monitor-summary.png)

At the top, a row of statistics shows the **total participant count** and one statistic per state, with a color-coded tag next to each state name. Clicking any statistic filters the Respondents list to that state.

Below that, the **State Breakdown by Form** table shows `form × state × count` rows — one row per (form shortcode, state) combination. Click any count to open the Respondents list pre-filtered to that form and state.

Use the Summary to answer questions like "how many people have finished?" or "is a large chunk of my participants stuck in `ERROR` or `WAIT_EXTERNAL_EVENT`?" before diving into the Respondents list.

---

## The Respondents sub-tab

The Respondents view is a filterable, paginated table of every participant in the survey. This is where you go hunting.

![Monitor respondents](/docs/images/fly-monitor-respondents.png)

### Filters

Four filters across the top, plus a reset button:

| Filter | What it does |
|--------|---------------|
| **State** | Dropdown — restricts the list to one state machine value (`START`, `RESPONDING`, `QOUT`, etc.). See [Participant states](#participant-states) below for what each one means. |
| **Form** | Free-text — matches a form shortcode exactly (e.g. `intake_v1`). |
| **Error Tag** | Free-text — substring match on the participant's error tag. Typing `FB` matches `FB`, and typing `INTERNAL` matches `INTERNAL`. Picking this filter clears the State filter, since error tags only appear on `ERROR`/`BLOCKED` participants. |
| **User ID** | Free-text — substring match on the participant's id: a Facebook PSID on Messenger, or a phone number (international form, no `+`) on WhatsApp. Use this when a specific participant reported a problem. |

Changing any filter resets the page to 1. Page sizes are 10, 20, 50, or 100.

### Columns

| Column | What it shows |
|--------|---------------|
| **User ID** | The participant's id — a Facebook PSID on Messenger, a phone number on WhatsApp. Click to open the [Participant Detail](#participant-detail) view. |
| **State** | The participant's current state, shown as a color-coded tag. |
| **Form** | The form shortcode the participant is currently on. |
| **Last Updated** | When this participant's state was last written to the database. Sort by this to find participants who haven't progressed in a while. |
| **Error Tag** | A red tag showing the error classification, only present when the participant is in `ERROR` or `BLOCKED`. `-` otherwise. See [Error tags](#error-tags). |
| **Stuck on Question** | `Yes` (orange) if the participant has answered the same question 3 or more times in a row — a sign of validation failures, confusing wording, or translation issues. `No` (green) otherwise. |
| **Timeout Date** | When a `WAIT_EXTERNAL_EVENT` participant's wait is due to expire. `-` for other states. |

Click any row (not just the User ID link) to open that participant's detail view.

---

## Participant detail

The detail view is the deep dive into one participant. It is laid out as a stack of cards:

1. **State Details** — the key-value summary: User ID, Page ID, Current State (color tag), Current Form, Last Updated, Form Start Time, and (when present) Error Tag, FB Error Code, Stuck on Question, and Timeout Date.
2. **Forms** — the list of form shortcodes the participant has traversed, in order. The last entry should match the Current Form. Multiple entries indicate a multi-stage / follow-up survey.
3. **Error Details** *(only shown if the participant is in `ERROR` or `BLOCKED`)* — the full error block from the state: Error Code, Error Type, Error Tag, Message, FB Trace ID, and a structured Details blob. This is the most useful card for diagnosing delivery failures.
4. **Wait Condition** *(only shown if the participant is in `WAIT_EXTERNAL_EVENT`)* — what the participant is waiting for: the wait type (e.g. `timeout` or `external`), its value, and when the wait started. Use this together with the Timeout Date column to decide whether a wait has overstayed.
5. **Question & Answer Transcript** — every question asked and answer received, in order. Repeated rows with the same question reference are the signature of a validation loop.
6. **Raw State JSON** — a collapsible, formatted dump of the entire state object for advanced debugging.

---

## Participant states

Every participant is in exactly one state at a time. The state is the machine's view of where the participant is in the survey flow. States are shown as color-coded tags throughout the Monitor tab.

| State | Color | Meaning |
|-------|-------|---------|
| `START` | blue | The participant has been created but has not started answering questions yet. Usually brief. |
| `RESPONDING` | green | The state machine is actively processing the participant's last message. This is a **transient** state — it is the moment between receiving a reply and sending the next question. You will rarely see participants parked here. |
| `QOUT` | cyan | **"Question out"** — a question has been sent to the participant and the bot is waiting for their reply. This is the normal in-flight state for any active participant. Most "currently taking the survey" participants are in `QOUT`. |
| `END` | gray | The participant has completed the survey flow. No more questions will be asked. |
| `BLOCKED` | red | A Facebook platform error occurred while sending a message (the user blocked the page, deleted their account, the page token expired, or Facebook rate-limited the send). The participant is halted but **often recoverable** — see [BLOCKED vs USER_BLOCKED](#blocked-vs-user_blocked) and [Error tags](#error-tags). |
| `ERROR` | red | An internal or unhandled error occurred (state transition bug, IO failure, form lookup failure, network error). The participant is halted. Some `ERROR` tags are auto-retried by Dean. |
| `WAIT_EXTERNAL_EVENT` | orange | The participant is paused, waiting for something external to happen — a payment confirmation, a timeout to elapse, or a follow-up trigger. The **Wait Condition** card in the detail view tells you what it is waiting for, and the **Timeout Date** column tells you when the wait expires. |
| `USER_BLOCKED` | magenta | The **system** has blocked this participant for spamming (see below). This is not a Facebook error — it is a Fly-initiated block. |

### QOUT vs RESPONDING

These two are the most commonly confused:

- **`RESPONDING`** is the brief moment when the bot is *processing* an incoming reply and deciding what to do next. It is transitional; a healthy participant passes through it within milliseconds on the way to `QOUT`.
- **`QOUT`** is the steady-state where a question is *out with the participant* and the bot is waiting for them to reply. A participant who is "in the middle of the survey and we're waiting on them" is in `QOUT`.

If you see a participant parked in `RESPONDING` for a long time (check the **Last Updated** column), something is wrong — the bot should have moved them to `QOUT` or another state quickly. The `RESPONDING` filter is mostly useful for finding these stuck-mid-processing cases, not for counting "active" participants. Use `QOUT` for that.

### BLOCKED vs USER_BLOCKED

These sound similar but have completely different causes and recovery paths:

- **`BLOCKED`** is caused by a **Facebook platform error**. The bot tried to send a message and Facebook returned an error: the recipient blocked the page, the recipient's account was deleted, the page access token expired, or Facebook rate-limited the send. The specific failure is in the **Error Details** card (error tag `FB`, with an [FB Error Code](#facebook-error-codes)). Many `BLOCKED` participants are recoverable — Dean automatically retries the ones with transient codes, and you can write a [bail](/docs/fly/reference/bails/) to rescue specific `BLOCKED` cohorts.

- **`USER_BLOCKED`** is caused by **Fly's own spam detection**. Dean's spam query blocks participants who have answered the same question 25 times in a row, or who have accumulated too many pending external events (an out-of-memory guard). When this fires, Dean sends a `block_user` event that **resets the participant's state** and pins them in `USER_BLOCKED` so they can no longer receive messages or start new forms. Participants in `USER_BLOCKED` are deliberately **not** retried by Dean's spam query, and a `USER_BLOCKED` participant will ignore incoming messages, external events, and referrals. Recovering a `USER_BLOCKED` participant requires a manual state restore — it is not something a bail alone will fix. If you see a spike in `USER_BLOCKED`, look at whether a question is broken enough to drive real participants into a 25-times-repeat loop.

---

## Error tags

The **Error Tag** column (and the Error Details card) classifies *why* a participant is in `ERROR` or `BLOCKED`. The tag is a short string; filter on it with the Error Tag filter to find everyone who failed the same way.

| Tag | State it puts the participant in | Meaning |
|-----|-----------------------------------|---------|
| `FB` | `BLOCKED` | A Facebook Graph API error occurred while sending a message. The accompanying [FB Error Code](#facebook-error-codes) tells you which one. This is the tag to look at for delivery failures. |
| `STATE_ACTIONS` | `ERROR` | An error occurred while executing the side effects of a state transition — sending the message, looking up the form, fetching the page token, etc. The message and stack are in the Error Details card. **Auto-retried by Dean.** |
| `STATE_TRANSITION` | `ERROR` | The state machine threw an exception while deciding what to do with an event — usually a bug in the survey definition or the machine itself. The state and event that triggered it are captured in the error details. |
| `INTERNAL` | `ERROR` | An internal IO failure (page token lookup, form lookup). **Auto-retried by Dean.** |
| `NETWORK` | `ERROR` | A network-level failure talking to Facebook or another upstream service. **Auto-retried by Dean.** |
| `CORRUPTED_MESSAGE` | `ERROR` | An incoming event could not be parsed (e.g. missing timestamp). Usually a malformed webhook payload rather than a participant problem. |
| `FORM_NOT_FOUND` | `ERROR` | The form shortcode for the participant's current form could not be resolved to a survey version. Often means the form was deleted or the shortcode is misspelled. |
| `FIELD_NOT_FOUND` | `ERROR` | The form does not contain a field it refers to — a jump target, or the question the participant was sitting on when the form was edited. |
| `INTERPOLATION_ERROR` | `ERROR` | A `{{hidden:...}}` or `{{field:...}}` reference in a question could not be resolved. |
| `REF_DECODE` | `ERROR` | The participant arrived with a recruitment reference that could not be read, so Fly does not know which survey they wanted. Almost always a problem with the ad, not the survey — see [Channels](/docs/fly/reference/channels/). |

### Which errors Dean retries automatically

Dean periodically sweeps the `states` table and retries participants in `ERROR` whose error tag is in its retry set, and participants in `BLOCKED` whose FB error code is in its retry set. The current production retry configuration is:

- **From `ERROR`:** the tags `NETWORK`, `INTERNAL`, and `STATE_ACTIONS`.
- **From `BLOCKED`:** the FB error codes listed in [Facebook error codes](#facebook-error-codes) below.

Retries use exponential backoff (visible as the `next_retry` timestamp in the detail view's raw state JSON) and are capped at a maximum number of attempts. Tags like `STATE_TRANSITION`, `CORRUPTED_MESSAGE`, and `FORM_NOT_FOUND` are **not** auto-retried — they indicate a problem that needs a human fix (a survey bug, a deleted form, a malformed payload). For those, fix the root cause and then use a [bail](/docs/fly/reference/bails/) to re-enroll the affected participants.

---

## Facebook error codes

When the error tag is `FB`, the **FB Error Code** field (column in the list, field in the detail card) is the numeric error code Meta's Graph API returned. WhatsApp send failures arrive through the same field, with WhatsApp's own codes. These are the codes you will most often see, and whether Dean auto-retries them from `BLOCKED`:

| Code | Meaning | Auto-retried by Dean? |
|------|---------|:---:|
| `10` | Permission denied — the page lacks the permission needed to message this recipient. | No |
| `190` | Access token expired or invalid. The page connection needs re-authentication in Connected Accounts. | Yes |
| `551` | Recipient is not currently reachable on Messenger (e.g. they haven't interacted with the page in the last 24 hours and no utility template applies). | Yes |
| `613` | Rate limit — too many calls to the Graph API in a short window. Transient; backing off fixes it. | Yes |
| `2022` | Invalid recipient — the recipient cannot receive messages (deleted or deactivated account, or blocked the page). | Yes |
| `80006` | Temporary send failure on Facebook's side. Transient. | Yes |
| `-1` | No Facebook error code was available — typically an HTTP-level failure (DNS, connection reset, timeout) rather than a Graph API response. | Yes |

For codes that Dean does **not** retry (notably `10`), the participant stays in `BLOCKED` until you intervene. The usual fixes are:

- For `190` (token expired): re-connect the Facebook Page under **Connected Accounts**, then bail the `BLOCKED` participants back into the survey.
- For `10` (permissions): grant the page the required permissions (e.g. `pages_messaging`), then bail the participants back in.
- For `2022` (account deleted / page blocked): the participant is genuinely unreachable. There is nothing to do — they will remain in `BLOCKED`. Filter them out when measuring completion.

See [Bails](/docs/fly/reference/bails/) for how to re-enroll recoverable `BLOCKED` participants in bulk.

---

## Common workflows

### Find participants stuck on a question
Filter by **State = `QOUT`** and sort by **Last Updated** ascending, or filter for **Stuck on Question = Yes** (the `stuck_on_question` flag fires when the same question has been answered 3+ times). Open the detail view and read the **Question & Answer Transcript** — repeated rows with the same question reference usually mean validation rules are rejecting valid answers, the question text is confusing, or a translation is broken.

### Find Facebook delivery failures
Filter by **State = `BLOCKED`** (optionally add an **Error Tag** of `FB`). Open a few detail rows and read the **FB Error Code**. Group by code to estimate how many participants are unreachable for a real reason (`2022`) vs how many are recoverable (`190`, `613`, `551`). For the recoverable ones, fix the root cause and [bail](/docs/fly/reference/bails/) them back in.

### Find participants who have been waiting too long
Filter by **State = `WAIT_EXTERNAL_EVENT`** and look at the **Timeout Date** column. Any participant whose timeout date is in the past should already have been advanced by Dean's timeout sweep — if they are still waiting, Dean may be down or misconfigured. Open the **Wait Condition** card to see what they are waiting for (a payment, a timeout variable, an external trigger). See [Timeouts](/docs/fly/reference/timeouts/) for how waits are defined.

### Find spam-blocked participants
Filter by **State = `USER_BLOCKED`**. These are participants Fly itself blocked. A few is normal; a spike usually means a question is so broken that real participants are re-answering it 25 times. Investigate the affected form's questions before trying to recover the users.

### Check that ad clickers are arriving in the right survey
Before letting a recruitment budget run, open the Monitor tab on the survey you are advertising and confirm that participants are appearing at all. If they are not, they are most likely landing on [the default form](/docs/fly/reference/default_response/) instead — which shows up as arrivals on shortcode `305`, not as errors, because a misrouted participant is not an errored one. A cluster of `REF_DECODE` errors is the other symptom of the same problem.

### Investigate one participant's full history
Type (or paste) their user id into the **User ID** filter. Open the detail view and read the **Question & Answer Transcript** top to bottom — it is the complete ordered record of what the bot asked and what the participant answered, which is what you need when a participant reports a problem.

---

## What you are looking at, and what you are not

A few things worth keeping in mind when reading the Monitor tab:

- **The data is observational, not real-time.** The `states` table is a denormalized dump written after each state transition. It is updated within seconds of a participant's event under normal load, but it is not a live transcript — a participant who just replied may still show the previous state for a moment.
- **Rows are scoped to your surveys.** The backend resolves which states belong to the survey you are viewing by form shortcode and version. A participant on a now-killed version of a form still appears under the survey that owned that version when they started.
- **`END` is forever (for that form).** A participant in `END` has finished the current survey flow. They will only reappear in `QOUT` or `RESPONDING` if a bail moves them to a new form or a follow-up is triggered.
- **The Monitor tab is read-only.** You cannot change a participant's state from here. To act on what you find — retry, re-enroll, move to a different form — use a [bail](/docs/fly/reference/bails/).
