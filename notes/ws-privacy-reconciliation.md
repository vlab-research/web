# The privacy policy read against the capability register

**Prepared 2026-08-21.** The gate D-024 names, run: every row in `CLAIMS.md`'s Fly section
compared clause by clause against the privacy policy as published at `/privacy`
(`index.html`, *Last updated 2026-05-15*).

**This is a memo. It decides nothing** — see `notes/README.md`. The policy is Nandan's and
`CONTENT.md` says it is carried over near-verbatim with *"structural edits only"*, so every
recommendation below is a request for a ruling rather than a change anyone may make.

**Scope note, and it is the reason this memo exists rather than a paragraph in the page
spec.** Three of the findings are **already true today**. They are not created by publishing
an instrument page; they are made *discoverable* by it, which is a different and smaller
claim — but the reader who discovers them is a procurement reviewer, and procurement
reviewers are audience 1.

---

## 1 · What §2.2 covers, and what the instrument actually records

§2.2 *From participants* lists five categories: platform-assigned identifiers, survey
responses, **message metadata** (*"timestamps, message direction, delivery status, and
chatbot state"*), consent and permission records, and limited profile data.

| Register row | What is recorded | Covered by §2.2? |
|---|---|---|
| C-063 assignment from a seed | The arm, derived from a hash of form and participant | **Yes**, in substance — it is study configuration applied to a response, and it creates no new participant field |
| C-059 · C-060 timing | Timeouts, scheduled follow-ups, template permissions | **Yes** — *chatbot state* and *consent and permission records* both reach it squarely |
| C-070 attrition rules | Which form a participant was moved to and why | **Yes** — chatbot state |
| **C-064 video watch-tracking** | Play, pause, seek, completion, and a heartbeat while playing | **No.** See §2 |
| **C-065 link clicks** | That this participant opened this link, and when | **No.** See §2 |
| **C-061 · C-062 incentives** | A disbursement to a phone number or an email, through a third party | **No.** See §3 — the sharpest of the three |
| C-072 the full transcript | Every message exchanged, not only the answers | **Partly.** See §4 |
| C-067 · C-068 language | Which linked form a participant ran | **Yes** — study configuration |
| C-074 export / API | No new collection; a route out for data already described | **Yes** |
| C-075 answers drive recruitment | Responses read back to assign a stratum | **Yes** — it is a use of survey responses, and §3 already describes managing recruitment campaigns |

**Ten of the sixteen publishable rows are comfortably inside the policy as written.** The
gaps are three, and they are not of equal size.

---

## 2 · Video engagement and link clicks are behavioural data, and *"message metadata"* is
not a home for them

§2.2's fourth category is *"message metadata such as timestamps, message direction, delivery
status, and chatbot state."* Every item in that list is a property of **the message we
sent**. A play/pause/seek trail is a record of **what the participant did with the content**,
sampled while they did it — the heartbeat exists precisely to measure attention over time.
A link click is the same shape: it is an action taken by the participant, not a delivery
status of ours.

**Why the distinction is not pedantic.** C-064's whole argument on the page is that the
instrument *"produces a second class of measurement"* — behavioural, alongside the
self-report. A policy that lists the self-report and calls the behavioural stream "metadata"
is describing something narrower than the marketing page beside it, and the site's entire
proposition is that its public statements reconcile.

**The cheapest honest fix** is one clause in §2.2's list — *engagement events for media and
links delivered in the survey (for example that a video was played or a link opened, and
when)*. It is additive, it changes no legal base (§4 already relies on consent for
participant data), and it is the smallest edit that makes the page and the policy agree.

**The alternative, if the policy may not be touched:** write sections 3 of the instrument
page at a level §2.2 already covers — the instrument can *require* a video to be played
before continuing, without the page claiming a record of how it was watched. That is a real
loss. The watch-trail is the more interesting capability and the one a PI designing a
media-exposure study is actually shopping for.

---

## 3 · Incentive disbursement appears nowhere, and this is the one to fix first

Three separate absences, compounding:

1. **§2.2 does not describe a disbursement.** Paying a participant requires a destination —
   a phone number for an airtime top-up, an email address for a gift card. §2.2 contemplates
   a phone number only *"where SMS is used with the participant's consent"*, which is a
   different purpose from paying them.
2. **§5 does not list a recipient.** *How we share information* names the researcher's
   institution, infrastructure providers (Google Cloud, Auth0), connected messaging/social/
   advertising platforms, and legal requests. **A top-up or gift-card provider is none of
   those four.** It is not infrastructure and it is not a platform the researcher connected.
3. **§3 does not name the purpose.** The list of uses has no disbursement entry.

So disbursing an incentive means **sending a participant's phone number to a third party,
for a purpose §3 does not describe, to a recipient §5 does not list.** That is already what
the software does (C-061), for whichever studies use it — **the gap predates any page.**

**Recommended fix, and it is three short additions rather than a rewrite:** a disbursement
category in §2.2, a purpose line in §3, and a fourth bullet in §5 for payment and top-up
providers. Whether the providers are **named** in §5 is a real choice: naming them is the
more transparent and more on-register option and is what a procurement reviewer expects of a
subprocessor list; it also pins us publicly to vendors we may change. **The instrument page
names no provider either way** — that is already written into its spec.

---

## 4 · The transcript is broader than "survey responses", by a little

C-072 records *every message exchanged*, which includes what a participant typed that was
**not** an answer — an off-script reply, a rejected answer, a question back to the bot.
§2.2 names *"survey responses to questions authored by the researcher"*, which is narrower
than that in a plain reading, and §2.3's special-category warning is written against
responses too.

**Small, and worth one word rather than a paragraph:** *survey responses and other messages
a participant sends in the conversation*. Recorded here because a free-text message a
participant volunteers is exactly where an unanticipated special category arrives.

---

## 5 · Found while doing this, and it is not a website question

**Verified directly, 2026-08-21, in `../proposals/projects/katelyn-romm-r01/katelyn-romm-r01.yaml`.**

The policy, §2.2, closing line:

> *"We do not ask researchers to collect, and we do not knowingly process, payment card data
> or **government identifiers**."*

That project's scope of work:

> *"Recruit parents and administer screening questions via chatbot, including **collection of
> parent photo ID** for manual fraud verification by the Client."*
> *"**Provide eligible leads and associated photo ID data** to the Client team for outreach,
> consent, and assent of parents and adolescents."*

**A photo ID is a government identifier in any ordinary reading, and the second line has us
transmitting it.** Two things make this more than a wording problem:

- **It may also collide with C-066.** Fly deliberately does not store inbound media — it
  keeps an expiring platform reference and not the file. So *how* the photo IDs reach the
  client is an operational question this memo cannot answer, and the two possible answers
  have different privacy consequences.
- **It concerns minors' parents in a study about adolescents**, so §11 is in scope as well.

**This is not for the website and no page should mention it.** It is recorded because it was
found by a review whose job was reconciling public statements with what the software does,
and it is the largest inconsistency that review turned up. **It needs Nandan and, plausibly,
counsel — not a copy edit.**

---

## 6 · What is being asked for, in one place

| # | Ask | Who | Blocks |
|---|---|---|---|
| 1 | May §2.2, §3 and §5 be amended at all? `CONTENT.md` says structural edits only | Nandan | Everything below |
| 2 | Add an engagement-events category (§2.2) | Nandan | Instrument page §3 |
| 3 | Add disbursement: a §2.2 category, a §3 purpose, a §5 recipient | Nandan | Instrument page §5 |
| 4 | Are the disbursement providers **named** in §5? | Nandan | Nothing on the page — it names none either way |
| 5 | Broaden "survey responses" to cover volunteered messages (§2.2) | Nandan | Nothing — it is a correctness fix |
| 6 | The photo-ID contradiction in §5 above | Nandan · counsel | Not the website |

**If the answer to 1 is no**, sections 3 and 5 of the instrument page are written down to
what the policy already covers, and the page still runs: sections 1, 2, 4, 6, 7 and 8 are
untouched by all of this.
