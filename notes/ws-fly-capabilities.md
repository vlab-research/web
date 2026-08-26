# Fly — verified capability inventory

**Prepared 2026-08-21.** Nothing in `vlab.digital` was edited. Every verdict below is
traced to source on **`fly@main`**, to a deployment manifest, or to a page in
`docs.vlab.digital/content/fly/`. Where the published docs and `main` disagree, `main`
wins and the disagreement is named.

**Method note, and it changes several answers.** The `fly-*` sibling directories are
**git worktrees of one repository**, not separate products (`git worktree list`). The
default branch is `main`; the working checkout sits on `feature/enable-dingconnect-staging`,
**one commit ahead of main** (a staging config line). `main` is alive: last commit
2026-08-20, 286 commits in ninety days. Three named features turned out to be on a
branch or in a config file rather than in the running system, and one documented feature
was deliberately removed from the product ten days ago.

---

## 1. What Fly is, in one paragraph

> Fly is the survey instrument on the other side of the ad. The questionnaire runs as a
> conversation inside Messenger or WhatsApp — the app the respondent already has — and the
> conversation persists, which is what the rest is built on: the instrument can pause for
> two days and resume, send airtime to a phone number mid-survey, play a video and record
> every play, pause and finish, assign a treatment arm by hash and branch on it, and carry
> one person from a baseline into an endline months later. A study runs each of its
> languages as its own linked form and exports them as one dataset. What Fly records is
> also what the recruitment optimiser reads back: it is where a recruited person becomes a
> row of data. It is open source, and it is the half of the method the website has never
> described.

*Written to `DESIGN.md` §1's shape: what it is, what it does, what it is not — mechanism
first, no adjective doing work a verb could do. The last clause is the one to cut if the
paragraph needs to be shorter; the first sentence is the one that has to survive.*

---

## 2. The eight capabilities Nandan named

Each entry: what it actually is · where the evidence is · status · claim type.

### 2.1 Timeouts — waiting and delayed follow-up

**What it is.** A question can stop the survey and restart it later. The wait is written
as `"relative"` (`"2 days"`, `"1 week"`), `"absolute"` (a UTC datetime), or as a **named
variable** the researcher can re-point from the dashboard after the study is live. A
sweeper service (`dean`) walks the state table every minute and re-enters anyone whose
wait has expired. A separate rule sends one friendly nudge to a participant who has gone
quiet — and it is switched on implicitly, by whether the form defines the
`label.buttonHint.default` message at all.

**Evidence.**
- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/fly/reference/timeouts.md`
- `/home/nandan/Documents/vlab-research/fly/dean/queries.go` — `Timeouts` (line ~270), `FollowUps` (line 286)
- `/home/nandan/Documents/vlab-research/fly/devops/migrations/01-init.sql:55` —
  `has_followup BOOL AS (messages::JSON->>'label.buttonHint.default' IS NOT NULL) STORED`
- `/home/nandan/Documents/vlab-research/fly/devops/values/production.yaml` — `dean` deployed

**Status: SHIPPED**, with one hard constraint that is the platform's, not ours: a message
sent more than 24 hours after the respondent's last activity requires a **pre-approved
template**, per messaging account and per language. That is not a footnote — it is the
thing that makes multi-wave design non-trivial, and it is what §2.9 below is about.

**Claim type: capability.**

### 2.2 Incentives paid through the platform

**What it is.** A question can pay the respondent without leaving the conversation.
The survey holds on an external wait; a payment service (`dinersclub`) calls the provider;
the result comes back as hidden fields the survey can branch on — success flag, error
message, provider error code — so a failed payment can re-ask for the phone number rather
than dead-ending.

**Evidence.**
- `/home/nandan/Documents/vlab-research/fly/dinersclub/reloadly.go` — mobile airtime top-ups
- `/home/nandan/Documents/vlab-research/fly/dinersclub/giftcards.go` — Reloadly gift cards
- `/home/nandan/Documents/vlab-research/fly/dinersclub/http_provider.go` — any provider reachable over HTTP, secrets injected from the dashboard's Generic Secrets
- `/home/nandan/Documents/vlab-research/fly/devops/values/production.yaml:175` —
  `DINERSCLUB_PROVIDERS: "fake,reloadly,giftcard,http"`
- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/fly/reference/incentive_payments.md`

**Status: SHIPPED for airtime, gift cards and generic HTTP.** Three qualifications, all of
which matter for what we may write:

1. **DingConnect (airtime, data bundles, utility top-ups) is merged to `main` but enabled
   in no environment.** `production.yaml` does not list it; the one commit the working
   checkout carries beyond `main` enables it *on staging*, and that commit's own message
   says "NOT DEPLOYED yet." Code-complete is not a capability. **Do not put airtime-plus-
   utility-top-ups on the site.**
2. **There is no Tremendous provider.**
   `/home/nandan/Documents/vlab-research/fly/dinersclub/tremendous_provider.go` is 170 lines
   in which every line after `package main` is commented out. Tremendous is a *documented
   recipe* for the generic HTTP provider, which is a real and useful thing, but it is not a
   fourth integration.
3. **Duplicate-payment protection is delegated to the provider and is defeated for gift
   cards.** `giftcards.go:33-39` overwrites any researcher-supplied idempotency key with a
   fresh UUID on every attempt, while `main.go:171` retries with backoff. This is an
   operational finding, not a website finding, but it is the reason not to write
   "payments are exactly-once."

**Claim type: capability.**

### 2.3 Random seeds / randomisation

**What it is.** Every participant carries a 32-bit integer derived by FarmHash from the
form shortcode plus their own id. Declaring a hidden field `seed_N` yields an arm in
1…N (`seed % N + 1`); `seed_N_V` re-hashes V times to give a second, independent
assignment with the same arm count. Ordinary Typeform logic jumps branch on it. Because
the seed is a **deterministic function of (form, participant)**, an analyst can
reconstruct assignment from the exported data rather than trusting it.

**Evidence.**
- `/home/nandan/Documents/vlab-research/fly/replybot/lib/typewheels/utils.js:49-57` —
  `randomSeed`: `farmhash.fingerprint32(form + userId)`
- `/home/nandan/Documents/vlab-research/fly/replybot/lib/typewheels/form.js:44-58` — `getSeed`
- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/fly/reference/seeds.md`

**Status: SHIPPED.** One point of language: it is *hash-based assignment*, reproducible by
construction, not a draw from a random number generator. That is the stronger and truer
description for a research audience, and it is the `DESIGN.md` §2 rule 2 move.

**Claim type: capability.**

### 2.4 Delivering videos, and tracking whether they were watched

**What it is.** The survey sends a button; the button opens a small hosted player
(`moviehouse`) that embeds a Vimeo video inside the messaging app's web view, with the
participant and account stamped into the link. The player emits events back into the
survey: play, pause, ended, seeked, volume change, playback-rate change, error, and a
**heartbeat every thirty seconds while playing**. The survey can either continue
immediately and use the events as analysis data, or hold on `moviehouse:play` until the
respondent actually starts the video.

**Evidence.**
- `/home/nandan/Documents/vlab-research/fly/moviehouse/README.md`, `moviehouse/src/`
- `/home/nandan/Documents/vlab-research/fly/dean/queries.go:158,175,249` — external waits on `moviehouse:*`
- `/home/nandan/Documents/vlab-research/fly/documentation/questions.md:100-140` — the on-`main` authoring form
- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/fly/reference/questions.md` §Videos — the event table

**Status: SHIPPED — with two caveats that must not be lost.**

1. **The ergonomic `{"type": "moviehouse"}` and `{"type": "link_tracking"}` question types
   the published docs describe as "new as of 18 August 2026" are not on `main`.** They
   arrive in commit `b5a4b99d feat(link_tracking,moviehouse): replybot owns first-party
   URLs` (2026-08-18), which lives only on `feature/conversation-identity`.
   `git grep -l link_tracking main` returns nothing. Today the same capability is authored
   the older way — a `webview` question whose URL the researcher composes. **The
   capability is real; the published documentation is ahead of the running system.**
   Nothing on the website should depend on the newer syntax, and nobody should conclude
   from the docs' date stamp that this shipped three days ago.
2. **Watch tracking is verified on Messenger. WhatsApp is unverified.** `moviehouse`'s own
   README describes a Messenger web view and Messenger Extensions; the published docs
   assert Fly "handles both." I could not confirm the WhatsApp path from source. Treat
   in-chat video *tracking* on WhatsApp as unverified until someone checks.

**Claim type: capability.**

### 2.5 Collecting images from respondents

**What it is: it is not a capability, and it was removed as a claim ten days ago.**

Fly can *notice* that a respondent sent a photo — a question type validates that an
attachment of the right kind arrived — but **it does not store the file**. What lands in
the export is a platform reference that expires: roughly seven days on WhatsApp, roughly
thirty on Messenger, after which it resolves to nothing.

**Evidence.**
- `/home/nandan/Documents/vlab-research/fly/planning/inbound-media.md` — "**Status:**
  Designed, **not built, deliberately deferred 2026-08-11.**" Commit `409c9307
  docs(inbound-media): defer the feature, **stop claiming we support it**"
- The production reason, from that document: across **5,125 surveys and 187,148 fields**,
  eighteen fields declare an upload question, **all eighteen belonging to four test
  surveys owned by `nandanmarkrao@gmail.com`. Zero belong to a researcher.** The entire
  history of inbound media answers is five rows.
- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/fly/reference/questions.md`
  §Upload — carries a red warning: "**Not currently supported — do not use this question
  type.**"
- The plumbing that survives (`replybot/lib/generic-validator.js` `validateUpload`,
  the normalizer media branch) was left in place *deliberately, to make re-adding it
  cheap* — it is not evidence of a live feature.

**Status: NOT A CAPABILITY. Deferred, with a stated reason** (building it creates a
permanent store of respondent photographs, with a backup obligation, a retention policy
and an erasure gap, for zero users).

**Claim type: capability — and it must be recorded as `WITHHELD`, not simply omitted**,
because a capability inventory that silently drops it invites the next agent to
rediscover the question type in the source and put it back.

### 2.6 Full multilingual support

**What it is.** A study runs each language as its own **form**, and the forms are linked:
one is marked the base language, the others point at it. When an answer arrives, it is
mapped into the base language **at the moment it is written**, into its own column
(`responses.translated_response`), so the export and the recruitment optimiser can both
read one language across every arm of a multilingual study. Fly's own eight system
messages — the rejection messages, the follow-up nudge, the survey-closed message — are
per-form and authored in Typeform, so a survey is not half-translated with English error
text underneath. An Excel authoring tool copies the logic from the base form into every
translation, so the branching cannot drift between languages.

**Evidence.**
- `/home/nandan/Documents/vlab-research/fly/devops/migrations/01-init.sql:58,85` —
  `surveys.translation_conf`, `responses.translated_response`
- `/home/nandan/Documents/vlab-research/trans/forms.go`, `trans/responses.go` — the mapping engine
- `/home/nandan/Documents/vlab-research/fly/scribble/response.go:91-180` — applied at ingest
- `/home/nandan/Documents/vlab-research/fly/formcentral/server.go:24-71` — validated **at survey-create time**, so a broken mapping is a 400, not a silent data problem
- `/home/nandan/Documents/vlab-research/fly/dashboard-server/utils/typeform/typeform.util.js:48-53` — system messages read from Typeform on import
- `/home/nandan/Documents/vlab-research/upload-typeform/` — real studies: Bulgarian + Serbian (`bebbo/`), English + Indonesian (`sigap/`), Armenian + Turkish, Arabic (`embed-uae/`)
- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/fly/core-concepts.md` — the worked four-form example

**Status: SHIPPED, but "full" overclaims and must not be used.** Three limits:

1. **Only closed-ended answers are mapped across languages.** `trans/forms.go`'s registry
   of translators has exactly one entry, `multiple_choice`. Free text passes through in
   whatever language it was written. For most analysis this is most of the value — but
   "translate everything back to a single language" is not what the code does.
2. **Translation is applied at ingest, so changing the configuration after fielding does
   not retro-translate.** There is no backfill path in any repository.
3. Number parsing is genuinely multilingual — Arabic-Indic, Extended Arabic-Indic,
   Devanagari, Bengali, Thai numerals and Arabic decimal/thousands separators are all
   accepted and recorded as ordinary digits (`trans/forms.go:64-70`,
   `translate-typeform/validator.js:113-215`). This is a small, specific, checkable thing
   and it is worth more on a page than the word "multilingual."

**Honest phrasing:** *"Each language is its own form. Closed-ended answers are mapped back
to one base language as they are recorded, so a four-language study exports as one
dataset."*

**Claim type: capability.**

### 2.7 Better completion rates from social-media ads — **COMPARATIVE**

**Verdict: there is no measurement. Anywhere.** See §4.

### 2.8 Better ID verification by leveraging the social platform's verification — **COMPARATIVE**

**Verdict: there is no measurement, and the mechanism is weaker than the phrase suggests.**
See §4.

---

## 3. What Nandan did not name — and should have

Ordered by how much a social scientist would care.

### 3.1 Bails — attrition management as a first-class object

**This is the most under-sold thing in the product.** A *bail* is a standing rule that
moves every participant matching a condition from one form to another. Conditions compose
into AND/OR/NOT trees over seven primitives: which form they are on, which state they are
in, which error code halted them, which question they are sitting on, **how long it has
been since they answered a particular question**, whether they answered a particular
question (or answered it with a particular value), and which survey they belong to.

Rules fire immediately (every minute), on a daily schedule in a named IANA timezone with a
tolerance window, or once at an absolute datetime. **Every rule can be previewed before it
runs** — a count, a sample of matched user ids, and a toggle that shows the exact SQL.
Every execution writes an event carrying *the definition of the rule as it stood at that
moment*, so a rule edited later does not rewrite the history of what was done to whom.
There is also a CSV mode: up to a thousand named participants, each with their own
destination form.

What that buys a researcher, concretely: dropout recovery ("answered the baseline four
weeks ago, has not come back → move to a re-engagement form"), end-of-study exit surveys
that fire on the funder's contract date, recovery of participants halted by a platform
error once the cause is fixed, and re-enrolment of a named subset into a new wave.

- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/fly/reference/bails.md`
- `/home/nandan/Documents/vlab-research/fly/exodus/`, `/home/nandan/Documents/vlab-research/fly/documentation/bail-systems.md`
- `/home/nandan/Documents/vlab-research/fly/devops/migrations/06-exodus-bails.sql`, `12-bail-event-bailed-userids.sql`, `15-bail-survey-id.sql`

**Status: SHIPPED.**

### 3.2 Longitudinal design is the native shape, not an add-on

A *survey* is a collection of *forms*; a form ends by **stitching** to another, optionally
merging hidden fields on the way in (`{"arm": "treatment", "wave": "2"}`) so the next form
can branch on where the participant came from. Response rows carry `parent_shortcode` and
`parent_surveyid`, so a chain reconstructs in the data. Combine stitch with a wait and a
bail and you have baseline → four-month gap → endline → recovery of the people who did not
come back, entirely inside the instrument. The repository's own one-line description of
itself is *"a survey platform designed for longitudinal studies in poor network conditions
and low powered devices"* (`fly/README.md`).

`CLAIMS.md` C-011 already records the consequence without naming the cause: the field-window
median has a long right tail, "p75 = 90 days," **from longitudinal studies**.

**Status: SHIPPED.**

### 3.3 The loop back to recruitment — the thing most relevant to the current site

Fly is not a downstream tool the sampler hands off to. **The answers are the sampler's
input.** Virtual Lab reads Fly as a *data source* and extracts *variables* from it: which
stratum a respondent belongs to, and which question ref means "finished." The ad optimiser
reallocates budget against those extractions. The ad's `ref` parameter carries the stratum
metadata into the conversation at the first message, and it comes back out in the export
as columns beside the responses — including which creative the respondent arrived through.

A researcher can choose to trust Meta's targeting for stratum assignment, or **override it
with what the respondent says in the survey** — the docs call these Pattern #1 and Pattern
#2 and treat the second as the more rigorous one.

- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/vlab/study-configuration/data_extraction.md`
- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/vlab/study-configuration/data_sources.md`
- `/home/nandan/Documents/vlab-research/fly/documentation/referral-form-resolution.md`

**Status: SHIPPED.** This is the sentence that closes the site's current gap: the site
describes recruitment, and stops at the click. This is what the click is for.

### 3.4 Field monitoring — the study operations surface

A researcher watching a live study sees, per participant: current state, current form,
last update, the error classification if halted, when a wait expires, and a
**stuck-on-question flag** that fires when the same question has been answered three or
more times in a row — the signature of a broken validation rule, a confusing translation
or a mis-worded item. Clicking through gives the **full ordered question-and-answer
transcript** for that person. Aggregates roll up as form × state × count.

Underneath, transient failures are retried automatically with exponential backoff
(network, internal IO, send-side action errors); non-transient ones are deliberately not
retried because they need a human. Participants who answer the same question twenty-five
times running are blocked as spam.

- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/fly/reference/monitoring.md`
- `/home/nandan/Documents/vlab-research/fly/documentation/dashboard-study-health.md`, `study-error-alerting.md`
- `/home/nandan/Documents/vlab-research/fly/dean/queries.go` — `Errored`, `Blocked`, `Respondings`, `Spammers`

**Status: SHIPPED.**

### 3.5 The conversation is recorded, in full

Two separate records exist. A curated `chat_log` — every visible message, bot and
participant, with direction, timestamp, question ref and form — and a raw `full_messages`
stream with event-type filters (conversation, referrals, bails, payments, external
tracking, retries, system) and an optional UTC time window. Both export as CSV.

For a research audience this is an audit trail for the instrument itself: what was actually
asked, in what order, and what the participant actually typed, separable from the cleaned
response table.

- `/home/nandan/Documents/vlab-research/fly/documentation/chat-message-logging.md`
- `/home/nandan/Documents/vlab-research/fly/documentation/full-messages-export.md`
- `/home/nandan/Documents/vlab-research/fly/devops/migrations/08-chat-log.sql`

**Status: SHIPPED.** One operational caveat worth knowing before promising anything:
export files are **transient** — the download link expires after seven hours and the object
is deleted after three days by a storage lifecycle rule
(`fly/documentation/exports-storage.md`).

### 3.6 Data out — export preprocessing and a REST API

The export screen is not a dump button; it carries the decisions a researcher would
otherwise make by hand, and names their consequences: keep final answers only (a chat lets
someone answer twice when their first answer fails validation), drop duplicated users
entirely, add duration columns, drop anyone missing a variable that all real respondents
carry (the test-user filter), pivot long to wide, and attach metadata as columns —
including which creative recruited them and the stratification variables defined in the
study config.

There is also a keyed REST API: list surveys, cursor-paginated JSON responses, CSV
download. It is the same API the recruitment platform uses to pull responses.

- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/fly/reference/downloading-data.md`
- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/fly/reference/api/`
- `/home/nandan/Documents/vlab-research/fly/exporter/README.md`, `/home/nandan/Documents/vlab-research/vlab_prepro/`

**Status: SHIPPED.**

### 3.7 Question types, validation and consent

Text, number (with min/max/integer/locale rules), email, phone (E.164 enforced —
a number without its country code is rejected), date (**not** format-checked; recorded as
typed), multiple choice, persistent button choice, dropdown, picture choice, yes/no,
opinion scale, rating, statement, welcome and ending screens, attachments in four kinds.

**Consent is a first-class question type:** Typeform's *Legal* type records `I Accept` or
`I don't Accept` and branches like any other answer, which is the mechanism behind the
screening funnels in real studies. Fly's rejection messages are per-form and translatable
(§2.6), so a respondent who fails validation in Hausa is not answered in English.

Answers interpolate into later questions and into payment payloads, with a transform pipe:
`{{field:phone|e164}}` normalises a phone answer before it reaches a payment provider,
while the raw answer stays in the data for the audit trail.

- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/fly/reference/questions.md`
- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/fly/reference/hidden.md`
- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/fly/reference/messages.md`

**Status: SHIPPED.** Note the platform ceilings, because they constrain instrument design
and a researcher will want to know before they write the questionnaire: WhatsApp sends
1–3 options as buttons, 4–10 as a list, and **fails to send above ten** — so an
eleven-point 0–10 scale does not work on WhatsApp.

### 3.8 Media library

Upload once, get one URL, use it everywhere. Behind it, Fly pre-uploads a copy to every
connected messaging account in the background and sends by reference, falling back to the
URL if the pre-upload has not happened or has expired. Accepted formats and size limits
are set to the **strictest** of the platforms Fly sends on, so anything the library accepts
will send.

Two caveats that belong in any customer-facing sentence: the URLs are unguessable but
**public and permanent** — anyone with the link can open the file, forever — and there is
**no delete**, because deleting an asset would silently break live surveys pointing at it.

- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/fly/reference/media.md`
- `/home/nandan/Documents/vlab-research/fly/media-proxy/`, `devops/migrations/24-media-assets.sql`

**Status: SHIPPED.**

### 3.9 Handoff to another application

A question can pass control of the conversation to another Facebook app and resume when
control comes back, with whatever metadata the other app returns arriving as hidden fields
the survey can branch on. Niche, but it is the escape hatch for anything the instrument
cannot do itself, and no competitor documentation I have seen offers it.

- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/fly/reference/questions.md` §Passing Thread Control

**Status: SHIPPED.**

### 3.10 Study lifecycle details a researcher will ask about

- **End time.** A survey shuts at a datetime; anyone who writes in afterwards gets a
  defined closing message rather than silence.
- **Default page response.** Anyone who messages the page without coming through an ad
  gets a designated form (shortcode `305`) — which is how you stop uninvited people
  entering the sample.
- **Testing.** Any form can be opened by a link built from the page and the shortcode, and
  a seed can be forced in the URL to test each arm. Retaking requires an operator-held
  reset link.

- `/home/nandan/Documents/vlab-research/docs.vlab.digital/content/fly/reference/settings.md`, `default_response.md`, `testing.md`

**Status: SHIPPED.**

---

## 4. The two comparative claims

### 4.1 "Better completion rates from social-media ads"

**No measurement exists. In any repository.**

What exists:

| Where | What it says | What it is |
|---|---|---|
| `proposals/projects/jorge-castaneda-latam-survey/…Notes by Gemini.md:212` | "we get significantly higher completion rates and cheaper acquisition rates by moving it over to the messenger platform" | **Nandan, on a sales call, 2026-07-29.** No n, no method, no comparison group. Comparator is SurveyMonkey. |
| `proposals/projects/jorge-castaneda-latam-survey/latam-survey-proposal.yaml:73` | leaving the instrument in SurveyMonkey "would increase the ad cost by roughly two to four times" | **Unsourced figure in a client-facing proposal.** The 2–4× appears nowhere else in any repo. Note it converts a completion claim into a cost multiple, which hides the denominator. |
| The paper, all four editions | grep for completion / attrition / response rate / drop-out: **zero hits on the comparative claim** | The paper runs the Prolific arm and reports it **on cost only**. `survey-sampling-with-ads-Jul2026.tex:123` is a to-do — "Optimize for survey completions (right now is CTR on survey)" — i.e. completions are not even the optimisation target today. |
| `proposals/countries/AR.md:66` | the client's own prior campaign found Argentina "the *worst* on completion" | **Points the other way**, and is about a SurveyMonkey link campaign, so it establishes a bad baseline with no measured Virtual Lab arm beside it. |
| `vlab.digital/index.html` (live site) | ~3,000 clicks / 890 starts / 560 completions, Nigeria | **A real measurement with an n** — and a *non-comparative* one. Already flagged in `AGENTS.md` as having no `CLAIMS.md` row. 560/890 is 63% start-to-complete; there is no second arm. |

**The mechanism phrasing that is true without the comparison.** The instrument is inside
the app the respondent is already using when they see the ad — there is no page to load,
no link to follow out of the app, and no form to abandon. What that structurally removes
is the hand-off between the ad and the questionnaire: the respondent never leaves. Whether
that yields more completes than a link to a web form is **not something we have measured**,
and the honest page says the first part and stops.

If a figure is ever wanted, the study that would produce it is small and obvious: run one
recruitment campaign into two destinations — the chat instrument and a hosted form — with
the same questionnaire and the same strata, and report click→start→complete for both. Until
then this is a `WITHHELD` row, not a `PLACEHOLDER`, because nothing is pending.

### 4.2 "Better ID verification, leveraging the platform's own verification"

**No measurement exists, and the speaker labelled it a theory at the time.**

The single source is a sales call
(`proposals/projects/katelyn-romm-r01/…Notes by Gemini.md`), where the client describes
fraud with other recruitment vendors — *"people just trying to pretend to be 10 different
people"* (line 126) — recalls having seen less of it on a previous Virtual Lab study
(line 140, recollection, no data), and Nandan explains why, explicitly hedged: *"my
general assumption of what why we have less fraud usually or the theory behind it"*
(line 144), *"we're just leveraging Meta's own identity process… we're just picking up on
it"* (line 150), *"It's not 100%. But usually, you know, 80 90"* (line 158 — offered as a
guess, in speech).

**It did not survive into the deliverable.** The signed scope
(`katelyn-romm-r01.yaml:9`) sells *"collection of parent photo ID for manual fraud
verification by the Client"* — i.e. the paid design assumes the platform-identity
inheritance is **not** sufficient. The same call proposes three further controls for the
same reason, including an ID-scan provider integration that is explicitly *considered, not
built*.

**What the mechanism actually is, stated precisely.**

- Fly receives a **page-scoped identifier** (a Facebook PSID) and a display name. That is
  the whole inherited identity surface — `replybot/lib/typewheels/form.js:62`: *"Anything
  on the user object (id, name, first_name, last_name)."* **No age, no verified-name
  attestation, no phone, no account-age or trust signal.** Everything else — age,
  eligibility, the phone number an incentive is paid to — is self-reported in the chat.
- Participant state is keyed on the **pair** (participant, account):
  `states PRIMARY KEY (userid, pageid)`.
- The state machine refuses to restart a form the pair has already entered.
  `replybot/lib/typewheels/machine.js:285-305`, `_hasForm` at line 92: `state.forms` is an
  append-only list of every form this pair has entered, and a repeat click either re-sends
  the outstanding question or is silently dropped.

**What that rules out, and what it does not.** It reliably blocks the same account
re-taking the same form on the same account — a structural guarantee a bare web link does
not have. **It does nothing about one person running several accounts**, which is exactly
the failure the client described. Fly's own documentation concedes the gap: the export
option `drop_duplicated_users` exists for *"people who somehow found a way to cheat the
system"* — a post-hoc dedup pass whose existence says the runtime guard is not trusted to
be complete, and which dedups on the same identifier and therefore misses the same thing.

**And there is an open defect that argues against making any identity claim right now.**
`fly/planning/conversation-identity.md` — *"Status: confirmed, reproduced on demand, plan
agreed 2026-08-16. **Not started.** Severity: kills live conversations permanently; leaks
data across researchers."* A conversation is properly identified by (platform, account,
user); replybot keys it by user alone, so the same person arriving on two different
accounts can be handed the wrong conversation. Publishing "our identity handling is better"
in the same month as that document would be indefensible if anyone ever read it.

**Mechanism phrasing that is true.** *"A respondent arrives already signed in to the
account they used to click the ad, and the platform keeps them attached to it: one account
cannot restart a questionnaire it has already begun."* That is checkable, it is in the
code, and it makes no claim about anybody else.

### 4.3 The D-023 tension — named, not decided

**D-023's scope, as written:** the site makes no comparative claim *"about
representativeness against another **recruitment source**"*, in our own voice. C-006–C-009
are `WITHHELD` on that basis.

**The argument that a completion claim falls outside it.** A completion rate compares two
*instruments* — a chat questionnaire and a web form — not two sources of respondents. The
recruitment source in the LatAm comparison is identical on both sides: the same Meta ads,
the same strata, the same money. Only what happens after the click differs. On a literal
reading, D-023 does not reach it, and reading it as though it did would ban us from
describing our own product's mechanics.

**Three arguments that it falls inside it, or close enough to matter.**

1. **The only place the claim is actually made expresses it as ad cost per complete** —
   "two to four times the ad cost." That is a claim about the yield of the recruitment
   funnel, which is a claim about recruitment, whatever the instrument at the end of it.
2. **The register does not separate the two concepts anywhere.** C-006's comparator,
   Prolific, is simultaneously a panel (a recruitment source) and a survey instrument. If
   the completion claim is outside D-023 because it is about instruments, then a Prolific
   comparison is arguably outside it too — and that plainly is not the intent.
3. **D-023's rationale does not depend on the scope word at all.** It was settled because
   the comparison rested on a figure the authors are revising. A completion comparison
   rests on **no figure whatsoever** — a strictly worse position than the one D-023
   withheld.

**Consequence, which is the useful part.** *The scope question is not blocking anything
today.* Both comparative claims fail hard rule 2 and the `CLAIMS.md` rule long before
D-023 is reached: there is nothing to publish. What Nandan actually has to decide — and
only he can — is the **conditional**: if a completion-rate measurement is ever produced,
does D-023 bar publishing it? If the answer is "D-023 is about recruitment sources and a
completion rate is about the instrument," then D-023 should say so explicitly, because
right now a reasonable agent can read it either way. If the answer is "no comparative
performance claim of any kind," then D-023's scope sentence is under-written and should be
widened.

The ID-verification claim needs no such analysis: its comparator is *"other recruitment
vendors"* — panels. That is squarely inside D-023 **and** has no evidence. It is withheld
twice over.

---

## 5. Proposed `CLAIMS.md` rows

Next free id is **C-056** (highest in use is C-055; C-033–C-039 and C-044–C-049 are gaps
and are left alone). Format follows the Headline figures table.

**Two register mechanics were respected while drafting these.** First, the status
vocabulary is fixed at `VERIFIED` / `STALE` / `PLACEHOLDER` / `WITHHELD`, and
`check-claims.py` depends on it — so a *partial* capability is recorded as `VERIFIED` with
its scope stated in the Source cell, exactly the C-054 pattern, and never as a new status.
Second, **numerals are kept out of `WITHHELD` rows**, because a withheld row contributes
every numeral in it to the banned set at ±2% tolerance — the trap already documented under
C-006.

### Capability claims

| ID | Claim | Value | Source | Status | Checked |
|---|---|---|---|---|---|
| C-056 | What Fly is | The survey instrument: the questionnaire runs as a conversation inside a messaging app | `fly/README.md`; `docs.vlab.digital` → `content/fly/core-concepts.md`; source on `fly@main` | `VERIFIED` | 2026-08-21 |
| C-057 | Channels Fly delivers on | **Messenger and WhatsApp** | `fly/hermes/src/handlers.rs` (`/webhooks`, `/whatsapp`); `fly/message-worker/{messenger_client.go,whatsapp_client.go,translator_whatsapp.go}`; `fly/devops/values/production.yaml`. **Scope: these two only — see C-058** | `VERIFIED` | 2026-08-21 |
| C-058 | Instagram, web and SMS as survey channels | **Not published** | Instagram is a stub returning "not yet implemented" (`fly/message-worker/stub_clients.go`); `websurvey/` is untracked and was explicitly reverted in 2021; `sms-sender/` is an untracked one-way CLI that sends a link back into Messenger. **Published docs assert Instagram — they are wrong; do not copy them** | `WITHHELD` | 2026-08-21 |
| C-059 | Delayed follow-up | A survey can pause and resume — after a fixed interval, at a set time, or at a time the researcher re-points while the study is live | `docs` → `content/fly/reference/timeouts.md`; `fly/dean/queries.go` (`Timeouts`, `FollowUps`); `dean` deployed in `production.yaml` | `VERIFIED` | 2026-08-21 |
| C-060 | Contact after the messaging window closes | Requires a template approved by the platform, per account and per language | `docs` → `content/fly/reference/timeouts.md`; `fly/documentation/utility-messages.md`, `whatsapp-templates.md`; `fly/devops/migrations/13-message-templates.sql` | `VERIFIED` | 2026-08-21 |
| C-061 | Incentives paid inside the conversation | **Mobile airtime top-ups and gift cards**, plus any provider reachable over HTTP | `fly/dinersclub/{reloadly.go,giftcards.go,http_provider.go}`; `fly/devops/values/production.yaml:175` (`DINERSCLUB_PROVIDERS`). **Scope: those three. Not "any incentive anywhere"** | `VERIFIED` | 2026-08-21 |
| C-062 | Airtime, data bundles and utility top-ups via DingConnect | **Not published** | `fly/dinersclub/dingconnect.go` is merged to `main` and tested, but the provider is enabled in **no** environment — `production.yaml` omits it and the staging enablement commit says "NOT DEPLOYED". Publishable only once it is enabled and a payment has been made | `PLACEHOLDER` | 2026-08-21 |
| C-063 | Randomised assignment to arms | Each participant's arm is a hash of the form and the participant, so assignment reproduces from the exported data | `fly/replybot/lib/typewheels/utils.js` (`randomSeed`, FarmHash fingerprint); `fly/replybot/lib/typewheels/form.js` (`getSeed`); `docs` → `content/fly/reference/seeds.md` | `VERIFIED` | 2026-08-21 |
| C-064 | Video delivered in-chat, with watching recorded | Play, pause, seek, completion and a heartbeat while playing are all recorded as events; the survey can hold until the video is played | `fly/moviehouse/`; `fly/dean/queries.go`; `fly/documentation/questions.md`. **Scope: verified on Messenger. WhatsApp unverified — see §2.4** | `VERIFIED` | 2026-08-21 |
| C-065 | Links whose clicks are recorded | A link is sent as a button and the click is recorded against the participant | `fly/linksniffer/` (deployed, `production.yaml`); `fly/documentation/questions.md` | `VERIFIED` | 2026-08-21 |
| C-066 | Collecting photographs or files from respondents | **Not published** | Designed and **deliberately deferred** — `fly/planning/inbound-media.md`, commit `409c9307 "stop claiming we support it"`. The file itself is never stored; what is kept is a platform reference that expires. **Never publish, in any form, until it is built** | `WITHHELD` | 2026-08-21 |
| C-067 | Multilingual studies | Each language is its own linked form; closed-ended answers are mapped to one base language as they are recorded, so a multilingual study exports as one dataset | `fly/devops/migrations/01-init.sql` (`translation_conf`, `translated_response`); `trans/forms.go`, `trans/responses.go`; `fly/scribble/response.go`; `fly/formcentral/server.go`. **Scope: closed-ended answers only — free text is not mapped. Never write "full multilingual support"** | `VERIFIED` | 2026-08-21 |
| C-068 | Questionnaire messages in the respondent's language | Fly's own rejection, nudge and closing messages are set per form, not fixed in English | `docs` → `content/fly/reference/messages.md`; `fly/replybot/lib/generic-validator.js`; `fly/dashboard-server/utils/typeform/typeform.util.js` | `VERIFIED` | 2026-08-21 |
| C-069 | One run of a form per account | A participant cannot restart a form the same account has already entered | `fly/replybot/lib/typewheels/machine.js` (`REFERRAL` branch, `_hasForm`); `states PRIMARY KEY (userid, pageid)`. **Scope: one account. Says nothing about one person holding several accounts — see C-077** | `VERIFIED` | 2026-08-21 |
| C-070 | Attrition handling | Standing rules move participants who match a condition — including "has not answered for N weeks" — from one form to another, with the matched set previewable before the rule runs | `docs` → `content/fly/reference/bails.md`; `fly/exodus/`; `fly/documentation/bail-systems.md`; migrations `06`, `12`, `15` | `VERIFIED` | 2026-08-21 |
| C-071 | Longitudinal studies | Forms chain to one another and carry metadata forward, so one participant runs a baseline and an endline months apart inside one study | `docs` → `content/fly/core-concepts.md`, `content/fly/reference/questions.md` §Stitch; `fly/README.md`. Consistent with C-011's long right tail (p75) | `VERIFIED` | 2026-08-21 |
| C-072 | The record of a study | Every message exchanged with every participant is recorded and exportable, alongside the response data | `fly/documentation/chat-message-logging.md`, `full-messages-export.md`; `fly/devops/migrations/08-chat-log.sql` | `VERIFIED` | 2026-08-21 |
| C-073 | Live field monitoring | Per-participant state, error classification and full transcript, with a flag for participants stuck repeating one question | `docs` → `content/fly/reference/monitoring.md`; `fly/documentation/dashboard-study-health.md`; `fly/dean/queries.go` | `VERIFIED` | 2026-08-21 |
| C-074 | Getting the data out | CSV export with preprocessing options, plus a keyed REST API | `docs` → `content/fly/reference/downloading-data.md`, `content/fly/reference/api/`; `fly/exporter/README.md`; `vlab_prepro/` | `VERIFIED` | 2026-08-21 |
| C-075 | Survey answers drive recruitment | The recruitment optimiser reads the survey's own answers to assign strata and decide who counts as recruited | `docs` → `content/vlab/study-configuration/data_extraction.md`, `data_sources.md`; `fly/documentation/referral-form-resolution.md` | `VERIFIED` | 2026-08-21 |

### Comparative claims

| ID | Claim | Value | Source | Status | Checked |
|---|---|---|---|---|---|
| C-076 | Completion rate against another survey mode | **Not published** | **No measurement exists.** Traceable only to a sales call (`proposals/projects/jorge-castaneda-latam-survey/…Notes by Gemini.md`) and an uncited multiple in `latam-survey-proposal.yaml`. The paper reports the Prolific arm on cost only. The client's own prior campaign points the other way. See the D-023 tension in the working note | `WITHHELD` | 2026-08-21 |
| C-077 | Fraud, duplicate respondents or identity verification against another recruitment source | **Not published** | **No measurement exists.** Traceable only to a sales call (`proposals/projects/katelyn-romm-r01/…Notes by Gemini.md`) in which the speaker labels it an assumption and a theory and offers the figure as a guess. The signed scope of that engagement sells manual photo-ID review instead. Comparator is "other recruitment vendors" — inside D-023. Publish C-069, which is the mechanism | `WITHHELD` | 2026-08-21 |

**Deliberately without a row:** the question-type catalogue, validation rules, the media
library, thread handoff, the export preprocessing options and the study lifecycle settings
(§3.6–§3.10). Each is real and each is sourced above, but they are *descriptions of an
interface*, not assertions a reviewer would ask us to substantiate — and a register that
grows a row per menu item stops being the thing the site's whole proposition rests on. If
any of them reaches a page as a claim rather than as prose, it needs a row then.

**Note for whoever merges these.** C-052 already reads *"Open source, self-hostable on
Kubernetes + Helm"*, sourced to `github.com/vlab-research`. That row covers Fly too — no
new open-source row is proposed, but C-052's scope should be checked once Fly is named on
a page, since a reader will now understand "the platform" to mean two things.

---

## 6. Could not verify — listed rather than omitted

1. **In-chat video tracking on WhatsApp.** The published docs assert Fly handles both;
   `moviehouse/README.md` describes a Messenger web view and Messenger Extensions. No
   WhatsApp path confirmed in source. C-064 is scoped to Messenger until someone checks.
2. **Whether WhatsApp is receiving in production right now.**
   `fly/devops/values/production.yaml:743-744` states that `WHATSAPP_VERIFY_TOKEN` "is NOT
   yet present in the vprod secret — `GET /whatsapp` verification returns 401 until it is
   added." That blocks (re)subscribing the webhook, not steady-state delivery, and
   `fly/planning/conversation-identity.md` records a Click-to-WhatsApp ad entry reproduced
   against production on 2026-08-16. The code is deployed and WhatsApp images have been
   deployed to production. **Whether a live WhatsApp study is fielding today is an
   operator question, not a source question.** C-057 is written as a capability, which is
   safe either way; anything stronger needs Nandan.
3. **Any completion, attrition, fraud or duplicate figure of any kind.** Exhausted:
   all four paper editions, the docs site, `fly/planning/` (~231 files), `fly/documentation/`,
   `proposals/`, `sampling-paper/`, `analyze/`, `power/`. Nothing measured exists.
4. **The Nigeria funnel** (~3,000 clicks / 890 starts / 560 completions) is a real
   measurement, is on the live site, and still has no `CLAIMS.md` row — already known
   drift in `AGENTS.md`. It is the closest thing we own to a completion figure and it has
   no comparison arm. Tracing it is a separate job; note that it is study-level and
   therefore subject to the disclosure check.
5. **PII handling and consent policy as *platform* claims.** The Legal question type
   records consent and branches on it — a real mechanism, and one deliberately left
   without a row below, because "the instrument can record consent" is a sentence about a
   question type, not a claim a reviewer would ask us to substantiate. But there is no
   documented PII policy, retention rule or erasure path in the Fly documentation. Two
   incidental mentions only. The privacy policy in `vlab.digital` is a company policy, not
   a Fly feature. **Do not write a data-protection capability claim without new work.**
6. **How many studies actually used timeouts, seeds, video or payments.** Answerable from
   the production database — a query per feature — and out of scope here, because the task
   forbids running one. The `inbound-media` document is the precedent for how much a usage
   count changes the picture: it is what turned "we support uploads" into "we deferred it."
7. **Quota logic.** Quotas live on the recruitment side (strata, target distribution), not
   in Fly. Fly's contribution is the *finished* signal and the stratum variables it feeds
   back. No Fly-side quota mechanism exists and none should be claimed.

---

## 7. Two documentation defects found on the way, for whoever owns the docs site

Neither is a `vlab.digital` problem, and I changed nothing. Recording them because both
are the kind of thing that gets copied onto a marketing page.

1. **`docs.vlab.digital` asserts Instagram support** in `content/fly/reference/media.md`
   ("every platform Fly supports — WhatsApp, Messenger and Instagram") and in
   `content/fly/reference/questions.md`. On `main`, the Instagram client is a stub that
   returns *"Instagram messaging not yet implemented"*, and there is no inbound path at
   all. **The public documentation overclaims a channel.**
2. **`docs.vlab.digital` documents two question types that are not on `main`.**
   `link_tracking` and the current-generation `moviehouse` type are stamped "new as of
   18 August 2026" but live only on `feature/conversation-identity`. The underlying
   capability is real and reachable by the older syntax; the syntax in the docs is not.
   (`fly/documentation/platform-abstraction.md` has the mirror-image problem: it still
   says there is no platform abstraction on `main`, which stopped being true when the
   WhatsApp work merged.)
