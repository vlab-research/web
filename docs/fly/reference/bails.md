---
title: Bails
weight: 10
---

A *bail* is an automated rule that moves participants who match a condition from one form to another. Bails are how Fly re-enters users who are stuck, recovers users who errored out, sends everyone to an exit survey, or hands a specific list of users to specific forms.

You can see when a bail last ran, how many users it matched, and how many successfully moved — all from the dashboard's **Bails** page.

---

## When to use a bail

A few common scenarios:

- **Dropout recovery.** A participant answered the baseline two weeks ago and has not come back. Bail them off the unresponsive form into a "we miss you" follow-up form.
- **Error retry.** A participant is stuck in `BLOCKED` with a known-recoverable error code. Bail them back to the last working question.
- **End of study.** At a specific date and time (say, when the funder's contract ends), move every remaining user on a form into an exit survey.
- **Stuck-question recovery.** Bail users who have been sitting on the same question too long.
- **Direct outreach.** Upload a CSV of specific users and send each one to a specific form.

A bail can query across **any form you own** — not just one survey — so the same rule can rescue users from several baseline forms into one recovery form, for example.

---

## The Bails list

Navigate to **Bails** in the dashboard sidebar. You will see a table of every bail you have created:

![Bails list view](/docs/images/bails-list.png)

Columns:

| Column | What it shows |
|--------|---------------|
| **Name** | Links to the edit form. |
| **Type** | `Conditions` (cyan tag) or `User List` (purple tag). |
| **Enabled** | Inline toggle. Flip it to pause a bail without deleting it. |
| **Timing** | Color-coded tag: green = `Immediate`, blue = `Scheduled`, orange = `Absolute`. |
| **Destination** | The form shortcode matched users will be sent to (for conditions-type bails) or the destination of the first user in the list (for user_list-type). |
| **Last Execution** | Localized timestamp and `X matched, Y bailed`. `Never` if the bail has not run. |

Action buttons (per row, in order):

1. **Edit** — pencil icon, opens the form pre-populated with this bail.
2. **Duplicate** — copy icon, opens the create form with values copied and the name set to `Copy of <original>`. The duplicate is created **disabled**.
3. **History** — clock icon, opens the event history for this bail.
4. **Delete** — trash icon, with a confirmation popover (`Delete this bail system? Yes / No`).

Click **+ New Bail System** in the top-right to start from scratch.

---

## The two bail types

The create form lets you pick a type at the top of the page, just below *Basic Information*:

- **Conditions** — "Move everyone who matches X." Builds a SQL query against the `states` and `responses` tables, evaluated each time the bail is scheduled to run.
- **User List** — "Move these specific N users, possibly to different destinations." Reads a CSV you uploaded. No query is built.

Both types share the **Execution Timing** card. They differ in what fills the middle card:

- For **Conditions** you build a tree of simple conditions with AND / OR / NOT logic.
- For **User List** you upload a CSV of up to 1000 specific `(userid, pageid, shortcode)` rows.

Both types can be enabled / disabled, edited, duplicated, deleted, and have a full event history.

---

## Creating a conditions-type bail

Open the create form. You will see five cards in order: *Basic Information*, *Bail Type*, *Conditions*, *Execution Timing*, *Action*, plus a *Preview* panel at the bottom:

![Create form](/docs/images/bails-create-form.png)

The **Enabled** switch defaults to *off*. A bail you save with it off will be saved but will not run until you enable it.

### The Conditions card

The Conditions card holds a **Condition Builder** — a recursive tree editor. Start with one simple condition, then click *Add Another Condition (AND/OR)* to combine it with more.

Each simple condition is a small box with:

- A type dropdown (top-left)
- Fields that match the chosen type
- A delete button (top-right)

If the condition is the root of a compound group, it is wrapped in a card titled *AND* / *OR* / *NOT* with the operator as a small radio (and a one-line hint: `all conditions must match` / `any condition must match` / `negate this condition`).

### Simple condition types

There are seven simple condition types. Pick the one that best describes what you want to match.

| Type | Matches | Required fields |
|------|---------|-----------------|
| **Form** | `states.current_form` | a form shortcode (e.g. `intake_v1`) |
| **State** | `states.current_state` | a state-machine value (dropdown) |
| **Error Code** | the `code` field on the `error` JSON in `state_json` | a free-text string (e.g. `TIMEOUT`) |
| **Current Question** | `states.state_json.question` | a question reference |
| **Elapsed Time** | participants whose N-th week / day has passed since they answered a particular question | `Form`, `Question`, `Duration` |
| **Question Response** | participants who answered (or answered with) a particular response | `Form`, `Question Ref`, optional `Response` and a mode toggle |
| **Survey ID** | participants whose current form belongs to a specific survey | a survey UUID |

The dropdown for `state` shows exactly these values:

- `START` — newly created, no question yet
- `RESPONDING` — actively answering
- `QOUT` — question delivered, waiting for the user's reply (`QOUT` is the normal in-flight state for active participants)
- `WAIT_EXTERNAL_EVENT` — waiting for some external trigger (e.g. lab result, payment confirmation)
- `END` — finished, no more questions
- `BLOCKED` — halted, see the `error` field for why
- `ERROR` — an unhandled error occurred

#### Elapsed Time

Use this for "goodbye" or "dropout recovery" rules. Pick a specific response event and a duration; Fly matches participants who answered that question in the past, but more than the duration ago.

| Input | Meaning |
|-------|---------|
| **Form** | shortcode of the form the question lives on |
| **Question** | `question_ref` of the trigger answer |
| **Duration** | free-text like `4 weeks`, `2 days`, `30 minutes`, `1 hour`. Must be `<number> <unit>` — singular or plural both work. |

> The duration must be in the exact `<number> <unit>` format. `4 weeks` works; `4w`, `4 weeks ago`, or `1.5 hours` do not.

#### Question Response

Two modes — toggle between them:

- **Is answered (any response)** — matches every participant who answered the question at all, regardless of what they answered.
- **Equals specific response** — only participants who answered with the exact value you enter in the *Response* box.

Use this when you want to bail, for example, only participants who consented (answered yes) on a particular question.

#### Survey ID

Enter the **survey's UUID**, not a form shortcode — this matches every participant whose current form is any form belonging to that survey. Useful when you want to bail all participants off an entire study at once.

### Combining conditions: AND / OR / NOT

When you wrap a single condition in a group, you get a *compound condition* with one of three operators:

- **AND** — all child conditions must match
- **OR** — any child condition must match
- **NOT** — negates a single child condition

You can nest groups arbitrarily. The typical pattern is: *outer AND of (simple) and (an inner OR of several error codes), with possibly a NOT somewhere.*

![Compound conditions](/docs/images/bails-compound.png)

#### NOT has a single-child constraint

`NOT` takes **exactly one** child:

- The **Add Condition** and **Add Group** buttons are hidden inside a NOT group.
- Switching from AND / OR into NOT keeps only the first child; the rest are dropped.
- Switching from NOT back into AND / OR keeps the single child and lets you add more.
- Deleting the only child of a NOT replaces it with an empty form condition rather than collapsing the NOT wrapper.

You cannot negate an *Elapsed Time* or *Question Response* condition (directly, or inside a group). The form will save, but the backend will reject it when the executor next tries to run it. *Survey ID* is safe to negate.

### Execution Timing

Choose when the bail runs:

| Timing | When it fires | Extra fields shown |
|--------|---------------|--------------------|
| **Immediate** | Every minute, every tick of the Fly executor job. Idempotent — bots already handle duplicate bailouts, so re-running is harmless. | none |
| **Scheduled** | Once per day, at a specific time, in a specific IANA timezone, with a configurable tolerance window | Time of day (`HH:MM`), Timezone, Tolerance (minutes) |
| **Absolute** | One-shot — at a specific datetime, and then never again | Date + time, Timezone |

For **Scheduled**, the **Tolerance (minutes)** field controls how many minutes after the target time the executor can still fire the bail. The default is 30 — increase it if your executor runs less frequently than every minute, or decrease it if you want a tight firing window (for example, set it to `0` to require the executor to fire within the target minute itself).

> The time-of-day you enter is interpreted in the timezone you pick. Use a canonical IANA name like `America/New_York` (not `US/Eastern`).
>
> Scheduled timing is deduped per calendar day. Even if the executor fires several times within the tolerance window, only the first run will execute.

For **Absolute**, use **Absolute** for "study ends on June 30 at 5pm ET" type scenarios. Once it has fired, the bail is dead — re-creating it is how you run it again.

### Action (where matched users go)

For conditions-type bails, the **Action** card has two fields:

- **Destination Form** — the form shortcode that matched users will be sent to. Required.
- **Metadata (JSON)** — optional JSON blob that gets passed to botserver alongside the bailout. Use it to carry context like `{"reason": "dropout_4weeks"}` that your survey can branch on.

> If the JSON in the Metadata box is malformed, the dashboard silently falls back to an empty object. Double-check by previewing and reading the SQL output if your metadata matters.

### Preview before you save

Click **Preview Matching Users** at the bottom of the form to run the query without executing it:

![Preview matching users](/docs/images/bails-preview.png)

You will see:

- A count of users that would be bailed
- A sample of up to 5 user IDs (with their page IDs)
- A **Show SQL** toggle that reveals the exact query (and its parameter values) that the executor would run

> If the preview says `0 users`, double-check your conditions: typos in shortcodes or `question_ref`s, an unfilled duration field, or nesting NOT inside an unsupported condition are the usual causes.

Always preview before enabling a new bail, especially one with non-trivial conditions.

---

## User List bails

When you want to bail a specific set of users (and possibly send different users to different destinations), use the user list type. There is no query — Fly reads the list and acts on it literally.

### When to use it

- A researcher exports a list of IDs from another tool and "imports" them into Fly.
- You want to send batch A to follow-up survey `v1` and batch B to follow-up `v2` from the same bail.
- You want to re-enroll a specific subset of past participants in a new round.

### The CSV format

The CSV has three required columns:

```csv
userid,pageid,shortcode
abc123,page_abc,survey_a
def456,page_def,survey_b
```

- **userid** — the participant's Fly user ID
- **pageid** — the messaging account that participant is associated with: a Facebook Page ID on Messenger, or the WhatsApp number's account id on WhatsApp
- **shortcode** — the form shortcode *this specific user* should be bailed to (per-row destination)

The header row is optional. The CSV can have 1–1000 rows. For larger batches, split into multiple bails.

### Creating one

1. Open the create form.
2. Choose **User List (CSV)** in the *Bail Type* card.
3. In the **User List** card, drag-and-drop your CSV or use the upload control:

![User List uploaded](/docs/images/bails-user-list.png)

Validation errors (wrong column count, empty fields, etc.) are shown inline below the table. The first row's `shortcode` populates the Destination column on the list view as a placeholder.

> When you switch to user list mode, the form auto-sets timing to **Absolute** with the current datetime and timezone UTC. Pick a different timing if you want it scheduled or immediate.

---

## Editing, duplicating, deleting

- **Edit** opens the form pre-populated with the current definition. Save changes with the same button (now labeled *Update*). Toggling **Enabled** off here pauses the bail.
- **Duplicate** opens the create form with all values copied and the name set to `Copy of <original>`. The duplicate is created **disabled** — turn it on deliberately.
- **Delete** is irreversible. The bail is removed from the database; its past events stay in `bail_events` for audit (with `bail_id` set to `NULL`).

---

## Event history

Every execution — success or error — produces a row in the event log.

![Event history](/docs/images/bails-events.png)

The **Event History** page (per bail) shows:

| Column | What it shows |
|--------|---------------|
| **Timestamp** | Localized, most-recent-first. |
| **Event Type** | `execution` (green) or `error` (red) tag. |
| **Users Matched** | How many users the query returned (or how many were in the user list). |
| **Users Bailed** | How many actually got moved. *May be lower than matched if botserver rejected some* — this still counts as execution, not error. |
| **Error** | Plain-text error message if event_type is `error`. |
| *(row button)* | **Details** — opens a single-event page with the exact `definition_snapshot` that was active when this event ran (so you can audit what the bail looked like then, even if it has since been edited), plus the full list of user IDs that were successfully bailed in that execution. |

---

## Troubleshooting

> **My bail has not run even though it is enabled.**
> Check the timing configuration. The most common causes:
>
> 1. A **Scheduled** bail with an invalid timezone name (e.g. `US/Eastern` instead of `America/New_York`) silently never fires. There is no error event recorded for this case.
> 2. A **Scheduled** bail with the wrong `time_of_day` format; it must be `HH:MM`.
> 3. An **Absolute** bail whose `datetime` is in the future — it will not fire until that time.
> 4. An **Immediate** bail with a condition whose `definition_snapshot` is invalid: see the most recent event row for an `error` event type.
>
> Go to the **Bails → History** page and inspect the most recent event's type and message.

> **My bail saved but keeps failing with `error`.**
> The most common backend validation errors:
>
> - Invalid duration string (use `<number> <unit>`, e.g. `4 weeks`, not `4w`).
> - NOT wrapping an `Elapsed Time` or `Question Response` condition — these cannot be negated.
> - User-list bail with empty or malformed CSV rows.

> **My bail matched users but did not actually bail them.**
> - If `users_matched > users_bailed` in the event, botserver rejected some users (for example, because the participant is no longer reachable). This is recorded as a successful `execution` event, not an error.
> - For user_list bails, make sure every row has a non-empty `userid`, `pageid`, and `shortcode`.

> **Preview shows 0 users.**
> Typos in `form` shortcodes or `question_ref`s are by far the most common cause. Open *Show SQL* in the preview to inspect the exact query and parameters Fly is sending.

---

## Limits and caveats

- A user-list bail can hold **at most 1000** rows.
- A single execution is capped at **100,000** users (a SQL `LIMIT 100000` plus a configurable executor-level limit).
- Immediate bails fire every minute; the executor throttle is shared across all of yours.
- Bails are scoped per Fly user — you cannot see or act on bails belonging to another user.
