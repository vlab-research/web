# ws-fly-brand — brand architecture for the two technologies

Workstream note. **Proposed only — nothing here has been written into `DESIGN.md`,
`DECISIONS.md`, `AGENTS.md`, `CLAIMS.md` or `CONTENT.md`.** Other agents were working
in those files concurrently. The proposed decision entry at the end is drafted as
`D-024` (next free number; `DECISIONS.md` currently ends at D-023) and has **not** been
added to the file.

Assets built for this note, all in `scratchpad/`:

| File | What |
|---|---|
| `fly-mark-d.svg` | A standalone Fly mark, 22px box, M5 only. Built because Option D turns on it. |
| `fly-mark-d-alt.svg` | The same idea on the parent mark's grid — three rows, cells fused into threads. |
| `fly-mark-b-lockup.svg` | **Not a Fly mark.** A revised *company* mark: the nine-cell lattice with its bottom row fused into a thread. What Option B implies visually. |
| `marks-sheet.png` | All three rendered at 16 / 22 / 48px beside `assets/mark.svg`, upscaled for inspection. |
| `fourth-hue.py` | The contrast + greyscale arithmetic behind "no product colour". Runnable. |

---

## 1 · The question, restated

Virtual Lab has two technologies. The site describes one of them.

1. **The recruitment side.** Adaptive sampling across ad platforms; convex optimization
   reallocating ad budget hourly to hit a target stratification. This is what the paper
   is about and what every page currently says. **It has no name of its own.**
2. **Fly.** The chat-based survey platform. Respondents answer in Messenger, WhatsApp
   or a web form. **It has a name and no presence on the site.**

The asymmetry is the actual problem. "Virtual Lab" currently denotes three things at
once — the company, the managed service, and the sampling engine — and any architecture
that treats the two technologies symmetrically has to break that overload first. Most of
the work below is deciding whether breaking it is worth what it costs.

---

## 2 · What is already true, before any decision

### The design system already contains Fly, and nobody noticed

`DESIGN.md` §6 **M5 · Thread** reads:

> Offset rounded rectangles. The one non-statistical motif, and the one thing that
> separates us from every panel provider: respondents are reached in a *conversation*,
> in an app they already use, and the same thread is still open four months later.

That is a description of Fly, written into the design system as a motif before the
product was ever named on the site. It is not a decorative flourish; §6 calls it *the
one thing that separates us from every panel provider*. And it is load-bearing in a
second way: **§5 says radius is 2px or 0, everywhere, "never more" — except the thread.**

> Radius is `2px`, everywhere, or `0`. Never more. Rounded corners belong to the thread
> motif alone.

So the system has already granted the conversation its own geometry, and granted it
nothing else. **This is the single most important fact in this note**, and it decides
the visual half of the question before we start: *Fly's differentiator in this system
is radius, not hue and not a mark.* That axis is already reserved, already exclusive,
already free, and already written down. Anything we add on top is a second payment for
something we have paid for.

### The icon set already splits, and the split is one-sixth

Of the twelve icons in `assets/icons/`:

| Serves | Icons |
|---|---|
| The recruitment side | Stratify · Optimize · Recruit · Weight · Precision · Coverage · Interval |
| Fly | **Survey** (the thread — the set's only round cap/join) · **Waves** (longitudinal re-contact) |
| Neither / both | Open source · Monitor · Export |

Two of twelve. That is an honest measure of how much of the current system serves Fly,
and it is roughly right for Option A and roughly wrong for everything else.

Note that `Survey` is already the odd one out of the twelve by construction, not just by
subject: per `ws-icons.md` it is *"the set's only `round` cap/join."* The set is already
telling us which of these two things is different.

### What "one paragraph" says, and what it leaves out

`DESIGN.md` §1 defines Virtual Lab as producing *"population-representative survey data
in places and at speeds conventional fieldwork cannot reach — and publishes the method
so buyers can check it."* That sentence covers both technologies without naming either.
It survives every option below unchanged, which is a useful sanity check: nothing here
requires re-founding the brand.

---

## 3 · What is already true in the code, and it changes the question

A survey of `../fly` and `../docs.vlab.digital` turned up five facts that are worth more
than any argument below, because they are the state of the world the brand has to
describe rather than invent.

### 3.1 · The recruitment side is not nameless. It is called `adopt`.

There is a database user and a table named `adopt` — `chatroach.adopt_reports`, with
`GRANT`s scoped exactly to what a sampler needs (read `responses`, `campaigns`,
`campaign_confs`; write its own reports). Introduced in `devops/migrations/01-init.sql`
and **still being extended in 2026** (`06-exodus-bails.sql` grants it read on `bails`).
It is a Python package in a sibling repo. It reads as **AD-OPT**.

It appears in **zero** user-facing surfaces: not in the docs, not in a UI, not in prose.

So the asymmetry in the brief is real but differently shaped than it looked. It is not
*"one has a name and one does not."* It is:

| | Named in code | Named in docs | Named on the site |
|---|---|---|---|
| Survey platform | `fly` | **`Fly`** — a top-level nav section | no |
| Recruitment | `adopt` | no — "the recruitment optimization tool" | no |

Both have internal names. **Fly is one step further out than `adopt` is, and one step
short of the website.** Every option below is a decision about whether to move each of
them one step in or one step out.

### 3.2 · The two-product architecture already exists, in the docs, and its central name is already colliding

`docs.vlab.digital/content/_index.md` — the canonical existing statement, written by us:

> This is the documentation for using the tools created by Virtual Lab:
> 1. **Virtual Lab**: the recruitment optimization tool.
> 2. **Fly**: a chatbot survey tool optimized for longitudinal surveys and incentive
>    reimbursement.
> These two tools are often used together, but can also be used separately.

The docs nav has exactly two top-level sections: **Fly** and **Virtual Lab**. So the
status quo is not "one technology acknowledged" — it is *Option B, already shipped, in
the one place both products are documented*, and it contains the exact name collision
the brief warned about: **"Virtual Lab" is simultaneously the parent and one of the two
children.** Fly's own dashboard makes it worse — `dashboard-client/public/index.html`
sets `<title>Virtual Lab</title>`, so the Fly UI calls itself Virtual Lab.

**Doing nothing is therefore not neutral.** It leaves a broken architecture standing in
the one artefact a technical buyer actually reads.

### 3.3 · The two are not peers. One consumes the other.

`docs/content/vlab/study-configuration/data_sources.md`:

> Virtual Lab supports several external platforms as data sources: **Fly, Qualtrics, and
> Typeform.**

And `connected-accounts/fly.md` treats Fly as a *connected account type*. Infrastructure
agrees: Fly's services are all namespaced `fly-*` (`fly-botserver`, `fly-dashboard-api`)
on `fly.vlab.digital`; **the recruitment side holds the bare namespace.**

This is decisive and it is not a matter of taste. The recruiter is the system; Fly is one
destination it can drive, alongside two competitors' products. **A symmetric "two engines"
brand architecture is architecturally false** — it would describe a relationship the
software does not have. Whatever we do, Fly is a component of the thing, not its twin.

### 3.4 · "Fly" is a member of an internal naming joke, not a product name

The monorepo's services are: **hermes · dean · dinersclub · exodus · scribble ·
moviehouse · linksniffer · formcentral · botspine · facebot · smoke-echo**, plus retired
**naughtybot · scratchbot · botscribe · dumper** still sitting disabled in the Helm chart.
The database is **chatroach**.

Single-word, faintly literary or jokey English nouns. **"Fly" is the same species of name
as "naughtybot."** It is a tier above them — it is the repo, it has a README positioning
line, it has a docs section — but its etymology is a developer's shorthand, and there is
**no origin story for it anywhere in either repo** (grepped: no "named after", no
"drosophila", no "fly on the wall"; first commit 2018-06-02, README's current text 2021).

This cuts both ways and both matter:

- **Against elevating it.** Promote `fly` to a customer-facing brand and you have promoted
  one member of a joke family. The next question is why `hermes` is not also a brand, and
  there is no principled answer.
- **For keeping it.** A name with no story is a name with no baggage. It has survived
  eight years and everyone in the company already says it. Renaming it would cost more
  than it is worth and would be the least instrument-grade thing on this list.

### 3.5 · Fly's own README is already better positioning than anything we would write

> Fly is a survey platform designed for **longitudinal studies in poor network conditions
> and low powered devices**.

That is `DESIGN.md` §2 rule 2 exactly — mechanism, not benefit — and it was written in
2021 by someone not doing brand work. It should be the seed of any Fly copy, not replaced.

### 3.6 · The one existing "identity" is not ours and should die regardless

`docs.vlab.digital/static/images/logo.png` — an abstract circle-and-orbits / node-network
mark in **indigo `#4F46E5`** (Tailwind indigo-600), with a full generated favicon set. Its
`site.webmanifest` has `"name": ""`. The same stylesheet also carries a *different*
unrelated navy, `--header-font-color: #00236aff`. **A node-network mark is on §6's banned
list** ("neural-network node graphs… anything implying AI"), and neither blue is a token.

This is a D-008 item, not a brand-architecture item, but it is free to fix and it is the
only finished visual identity either product currently has.

---

## 4 · The colour question, answered with arithmetic before it is asked

Every option below is tempted by a product colour. `DESIGN.md` §3 and D-005 are emphatic
that colour does exactly three jobs — chrome, data, accent+semantic — and nothing does
two. A product colour is a **fourth** job, and the brief is right that it needs an
argument rather than an assertion. Here is the argument, and it goes the other way.

**It is not one token, it is four.** §3's structure means any new hue needs a light
value, a lifted dark value, an `-inv` value for ink bands, and a tint if it may ever fill
a shape. That is the same footprint as the entire data job.

**And it fails the greyscale test that D-011 already imposes.** M2 requires state to
survive greyscale printing and colour-blind readers. Run `scratchpad/fourth-hue.py`:

```
moss            #3F6B4A  on paper-L 5.57  |  vs --data 1.17   vs --brass 1.01
slate-violet    #5A4E7A  on paper-L 6.77  |  vs --data 1.04   vs --brass 1.20
clay            #8A4B3C  on paper-L 6.03  |  vs --data 1.08   vs --brass 1.07
```

Any fourth hue dark enough to pass AA on `--paper` lands within **1.04–1.20 luminance
ratio** of `--data` and `--brass` — that is, **indistinguishable from both in greyscale.**
So a Fly colour would print as either "on target" or "under target" on a funder's
black-and-white photocopy of a proposal. The palette has no room left; that is what a
three-job palette *means*.

**And it is unnecessary, because the system already gave Fly an axis.** §5: *"Radius is
2px, everywhere, or 0. Never more. Rounded corners belong to the thread motif alone."*
Radius is a free, exclusive, already-reserved, already-written-down differentiator, and
it survives greyscale perfectly.

> **Under every option below, Fly's visual signature is radius, not hue.** No new token
> is proposed. `check-contrast.py` is unchanged and still passes 22 pairs.

---

## 5 · Four architectures

Each is stated as though it had been chosen, then costed.

---

### Option A · Masterbrand absolute — Fly stays internal

**Structure.** One brand. Fly is an implementation name, like `hermes` or `chatroach`.
The website never says it.

| Where | What it is called |
|---|---|
| In full | "Virtual Lab's survey platform" |
| Running prose | "Respondents answer in Messenger, WhatsApp or a web form." |
| Nav | nothing; the Platform page covers it |
| GitHub README | `# fly` — lowercase, a repo name, with a subtitle: "survey runtime for Virtual Lab studies" |

**Recruitment side.** Still "Virtual Lab". `adopt` stays in the schema. The overload
stands, unexamined.

**Visual.** Nothing new. Fly is present as M5 and as `#icon-survey` / `#icon-waves` — the
two of twelve icons that already serve it.

**Commits us to.** Nothing. **Forecloses:** any recognition of Fly outside the company;
any strategy in which other researchers adopt Fly and cite us for it.

**Operational cost:** zero — but a **live liability**. The docs nav says "Fly" and the
website never will, so a technical buyer who follows our own link lands on a name we do
not use. On a site whose entire proposition is that its public statements are maintained
and checkable, that is a small wound in exactly the wrong place. Option A does not
preserve the status quo; it *widens the gap* the status quo already has.

**The sentence a buyer reads.**
> "You set the target distribution; we reallocate ad budget hourly until the achieved
> sample matches it, and the people it reaches answer in a chat thread they already use."

Accurate, and the only sentence here that asks the buyer to learn no names — but it
demotes an eight-year platform with payments, video and multilingual waves to "a chat
thread," which is the sentence's real cost.

---

### Option B · Endorsed pair — both engines named, typeset not logotyped

**Structure.** Two named components under one masterbrand. The recruitment side takes a
name; `adopt` is the incumbent candidate (§6). Neither gets a logo — **product names in
this system are typeset, never logotyped.** That is the discipline that makes B cheap.

| Where | What it is called |
|---|---|
| In full, first mention | "Fly, our survey platform" / "Adopt, our recruitment optimizer" |
| Running prose | "Fly" and "Adopt" bare thereafter |
| Nav | not a nav item — D-007 settles seven pages; the Platform page gains two named sub-sections |
| GitHub README | `# Fly` with an endorsement line: "The survey platform behind Virtual Lab studies." |

**Recruitment side.** Named. "Virtual Lab" retreats to being the company and the managed
service — which fixes the docs collision cleanly and is the strongest thing B has going
for it.

**Visual.** No marks, no colours. Each component inherits one glyph from the existing
twelve: **Optimize** (three bars + target tick) for the sampler, **Survey** (the thread)
for Fly. The icon set already anticipated this split; nothing is drawn.

Optionally the *company* mark absorbs the pair — `fly-mark-b-lockup.svg` renders the
nine-cell lattice with its bottom row fused into a thread: two rows of stratification
design, then the conversation it ends in. It reads well at 16px (see `marks-sheet.png`).
**Changing the company mark is a larger decision than naming and is not proposed here** —
it is drawn only to show what B implies.

**Commits us to.** Keeping two proper nouns consistent across the site, the docs, every
README, and every proposal PDF, forever. Two things to explain in every sales call.
**Forecloses:** the simplicity of one name; and it hands a procurement reader two nouns
neither of which is purchasable (D-002 says we sell studies).

**Operational cost:** one word, plus consistency. No mark, no domain, no favicon, no
split docs. This is the *cheap* version of naming and it should be understood as the
serious alternative to the recommendation.

**The fatal objection.** §3.3. Fly and the recruiter are **not peers** — the recruiter
drives Fly, Typeform *or* Qualtrics. A symmetric architecture asserts a relationship the
software does not have, and the first technically literate reader who opens the docs will
see it. B can only be made true by first making the products peers, which is an
engineering decision, not a branding one.

**The sentence a buyer reads.**
> "Adopt decides whose attention to buy; Fly is where they answer."

Crisp — the best sentence of the four — and it is describing a company we are not.

---

### Option C · Deliberate asymmetry — Fly is named, the method is cited

**Structure.** Exactly one named component, and the asymmetry is the *argument* rather
than a defect to be designed around. **A name is earned by being a separable artefact
somebody can run.** Fly is: you can clone it, `helm install` it, point Qualtrics-shaped
integrations at it, and meet it without meeting us. The recruitment side is a **method**,
and methods are named by their papers. Its name is *Donati & Rao, 2025* — which is worth
more to both of our audiences than any noun we could invent.

| Where | What it is called |
|---|---|
| In full, first mention | "our survey platform, Fly" |
| Running prose | "Fly" thereafter — and whole pages go by without needing it |
| Nav | nothing; Fly is named once, in a heading on the Platform page |
| GitHub README | `# Fly — the survey platform behind Virtual Lab studies` |

**Recruitment side.** Never named publicly. It is "the optimizer", "adaptive sampling",
"the method" — and it is *cited*, not branded. `adopt` stays in the schema where it
belongs, exactly as `chatroach` does.

**"Virtual Lab" keeps its overload, and the overload is declared honest**: the company and
the recruitment system are the same thing, because the recruitment system is not
separately obtainable. The docs collision is fixed **without inventing a word** — retitle
the docs' second top-level section from **"Virtual Lab"** to **"Recruitment"**. Nav becomes
`Recruitment · Fly`. One line of Hugo front matter, collision gone, no new noun in the
world. *(This is the single cheapest fix identified in this note.)*

**Visual.** Nothing new at all. No mark, no colour, no icon. Fly's signature is radius
(§4 above) and its glyphs are the existing `#icon-survey` and `#icon-waves`. The M5 rule
in §6 is promoted from "a motif we use on the channel section" to "the visual identity of
the named component", which requires **no edit to §6 except one addition** (§8 below).

**Commits us to.** Explaining the asymmetry to every new hire and every agent, forever —
which is precisely what a `DECISIONS.md` entry is for. **Forecloses:** the sampler ever
being licensed or marketed separately without reopening this. It also caps Fly: a name
that appears once on a Platform page will never be adopted by outside researchers.

**Operational cost:** near zero. No second mark, no second domain, no favicon set, no
docs split, no GitHub reorganisation, no proposal-template change (`adopt` never surfaces,
and a proposal PDF says "our survey platform" or, for a technical annex, "Fly"). C-052's
verified source `github.com/vlab-research` is untouched.

**The sentence a buyer reads.**
> "The optimizer decides who we still need; Fly is where they answer."

One common noun beside one proper noun — the asymmetry made audible. That is either the
sentence's flaw or its point, and it is its point: it tells the reader, in its grammar,
that one of these is a method and the other is a machine.

---

### Option D · House of brands — Fly standalone

**Structure.** Fly is a product with its own identity, own mark, own domain, own docs.
Virtual Lab endorses it in a footer.

| Where | What it is called |
|---|---|
| In full | "Fly" |
| Running prose | "Fly" from the first word; "from Virtual Lab" in the footer only |
| Nav | a top-level **Fly** item — which breaks D-007's seven pages — or its own site |
| GitHub README | `# Fly — open-source chat surveys`, Virtual Lab in the licence and footer |

**Recruitment side.** **Must** be named, or Virtual Lab is left as a holding company whose
one branded asset is the *smaller* of its two technologies. So D includes B's naming cost
and adds to it.

**Visual.** A mark is required, so one is built: **`scratchpad/fly-mark-d.svg`** — two
offset rounded bars in the same 22px box as `assets/mark.svg`, `h=8`, `rx=4` (half height;
the one radius §5 permits above 2px), rows at `y=2`/`y=12`, spans `0–15` and `7–22` so the
7px overlap *is* the shared thread. Heavier than the lattice's 6px module deliberately: at
16px favicon a 6px bar renders 4.4px and the rounded ends vanish, 8px renders 5.8px and
holds. `currentColor` only. A grid-native alternative is at `fly-mark-d-alt.svg`.

**Rendering both at 16 / 22 / 48px beside the parent mark (`marks-sheet.png`) is the
finding that matters, and it argues against D.** The parent mark reads dense, orthogonal,
instrument. The thread mark reads soft, round, warm. **At 16px they do not read as two
products of one company — they read as two companies.** The very exclusivity of radius
that makes it a good *signature within* the system makes it a bad *sibling mark beside*
it. `fly-mark-d-alt.svg` narrows the gap by using the parent's exact grid, but at 16px
three stacked pills read as a hamburger menu, or as M2. Neither is safe.

**No colour** — §4 above; D wants one most and can have one least.

**What it commits us to, in full:**

- A second mark, plus favicon set (`.svg`, `.ico` at 16/32/48, `apple-touch-icon` at 180)
  — `ws-icons.md` records what that cost the first time.
- A second domain or subdomain, DNS, TLS, a second Netlify site.
- **Split docs.** D-008 stops being a two-way question (site ↔ docs) and becomes three-way.
- **GitHub.** The org is `vlab-research` and **C-052 cites it as a `VERIFIED` source**. A
  standalone Fly wants its own org; moving it invalidates a claim row and every inbound link.
- **Every proposal PDF acquires a naming decision** — whether to tell a funder buying a
  study the name of the software. Today that question does not exist.
- **An RFP asking "what platform do you use" now has two answers.**
- **Trademark.** Two hard problems, both external. (i) `Fly.io` is an established
  developer-infrastructure brand; "Fly" plus "platform" is a crowded, probably
  unregistrable space, and unsearchable. (ii) `fly/LICENSE` names **The World Bank Group**
  and **Curious Learning: A Global Literacy Project Inc.** alongside "fly contributors" as
  copyright holders. Building an exclusive commercial brand on a codebase co-copyrighted
  by a multilateral institution needs counsel before it needs a designer. *Neither point
  is settled here; both need a real search before any decision that depends on them.*
- **It reopens D-002.** A product with a mark, a domain and a docs site is a product being
  sold. The first "can we just license Fly?" email arrives within a month, and D-002 —
  no pricing page, no sign-up, no free tier — has to be re-argued. **This is a much larger
  decision than naming and must not be taken as a side effect of one.**

**And it fights D-003 hardest.** "Fly" is the warmest word in this system; D gives it the
loudest possible placement.

**The sentence a buyer reads.**
> "Fly runs the survey; Virtual Lab makes sure the right people take it."

Read it twice. It inverts the hierarchy — Virtual Lab becomes the service wrapper around
the product, "makes sure" is the vaguest verb on this page, and the sentence sells the
thing D-002 says we do not sell. **The sentence is the test, and D fails it.**

---

## 6 · If the recruitment side is to be named — the shortlist

**Only Options B and D need this section.** It is included so that "name it" is costed
rather than gestured at, and because one candidate already exists and is free.

The test each candidate must pass: *set it in IBM Plex Mono uppercase in a source line
under a number, and read it aloud to a methodologist.* A name that implies a
methodological claim we cannot substantiate fails on `CLAIMS.md` grounds, not taste.

| Candidate | For | Against |
|---|---|---|
| **`adopt` / ADOPT** ← incumbent | **It already exists** and has since 2018: a DB user, a table, a Python package, still extended in 2026. Reads as AD-OPT, which is literally true and claims nothing more. Set in mono caps it reads as an instrument's model designation, which is exactly D-003. Costs nothing to adopt because it is already the name. | Collides with a common English verb with strong unrelated connotations. Unsearchable. "Virtual Lab's Adopt engine" is an awkward sentence. |
| **Stratum** | Names the unit the whole method operates on; in-system (M1 is the cell lattice). | Generic, unprotectable, and reads academic-dusty — the exact register §2 warns off. |
| **Tare** | The instrument word for zeroing a balance before weighing. Cold, precise, unmistakably in register, pairs with `Weight` in the icon set. | Obscure enough that it needs explaining, and a name that needs explaining is not doing its job. |
| **Ballast** | Keeps the sample trimmed as it fills. Instrument-grade, memorable, no SaaS taint, and nobody in this market is near it. | It is a metaphor, and D-003 prefers mechanisms to metaphors. |
| **Cast** | Would complete a fly-fishing pair with Fly for free, and the pair would be memorable. | **The fly-fishing reading is not real** — §3.4, there is no origin story; "Fly" comes from the same joke drawer as `naughtybot`. Building a name on a retconned etymology is the least honest option here. Also heavily overloaded (broadcast, casting, type casting). |
| **Quota** ✗ | — | **Reject on methodological grounds.** Our method is not quota sampling; it minimises the variance of a post-stratification weighted estimate. A methodologist reads the name as a claim about the method, and it is the *wrong* claim. This is a `CLAIMS.md`-shaped objection, not a stylistic one. |
| **Lattice** ✗ | — | Reject: M1 *is* the company mark. Naming the sampler "Lattice" makes the company's mark the sampler's mark and deepens the overload B exists to fix. |

**If B is chosen, the recommendation within B is `adopt`** — not because it is the best
word available, but because it is *already true*, and inventing a better one creates a
permanent gap between the public name and the schema. On a site that will not invent a
number, inventing a noun for something that already has one is off-register.

---

## 7 · Recommendation — **Option C**

**Name Fly. Do not name the recruitment side. Say why, once, in `DECISIONS.md`, and stop
re-deciding it.**

### The reasoning that decides it

1. **The software architecture already chose.** §3.3: the recruiter drives Fly,
   Typeform *or* Qualtrics. Fly is a component, not a twin. Option B asserts a symmetry
   that the codebase, the docs and the hostnames all contradict, and B's lovely sentence
   — *"Adopt decides whose attention to buy; Fly is where they answer"* — describes a
   company we would then have to become. C describes the one we are.

2. **A name is earned by separability, and only one of the two is separable.** You can
   clone Fly, `helm install` it, and meet it without ever meeting us. You cannot obtain
   the recruitment system without buying a study — D-002 says so. Naming exactly one of
   them is not an inconsistency to be tidied; it is an accurate map of where names are
   needed.

3. **The recruitment side already has the strongest name available and it is a citation.**
   "Donati & Rao, 2025" outranks any invented noun for *both* audiences in §1 — a funder
   reads peer review, a PI reads a citation. A codename would be strictly weaker than
   what we already have, and would sit oddly next to §2's rule that specificity comes
   from the benchmark rather than from branding.

4. **The design system already paid for this and the receipt is in §5 and §6.** M5 exists,
   is called *the one thing that separates us from every panel provider*, and is granted
   the only exception to the radius rule. Option C simply **promotes M5 from a motif to
   the identity of a named component** — no new mark, no new token, no new icon, no new
   file. The empirical check in `marks-sheet.png` says the same thing from the other
   direction: a separate Fly *mark* stops reading as a sibling at 16px. **Radius is the
   right amount of difference. A mark is too much.**

5. **It costs nothing and fixes the live bug.** The docs collision — "Virtual Lab" as both
   parent and child — is repaired by retitling one Hugo section to **"Recruitment"**. Nav
   becomes `Recruitment · Fly`. No new noun enters the world.

### The strongest argument against

**C permanently caps Fly, and Fly may be worth more than the cap.** The inventory is not
small: Messenger, WhatsApp and Instagram; timeouts; incentive payments through four
providers including mobile airtime top-ups; deterministic seeded randomisation; video
delivery with watch-tracking; respondent file upload; multilingual longitudinal waves;
bail systems; a public REST API. That is a serious piece of software, and there is a real
strategy — adoption by outside researchers → citations → credibility → studies — that
Option C's "named once on the Platform page" makes impossible. **Option B buys that
optionality for the price of one word**, and B's cost is genuinely one word: no mark, no
domain, no favicon, no split docs.

The counter is that the adoption strategy is not currently anyone's plan, that D-002 says
what we sell, and that C is reversible — moving from C to B later costs a naming exercise
and a docs retitle. **Moving from D back to C is not reversible**, because a mark, a
domain and a docs site cannot be quietly withdrawn. So C is the option that keeps the
most doors open per unit spent, which is the right shape for a decision nobody is being
forced to make this week.

### The D-003 tension, addressed rather than smoothed

"Fly" is the warmest word in this system, and that is real. It is not fixed by pretending
otherwise; it is managed by **placement and by one ban**:

- **Placement.** Under C, "Fly" appears where the register is loosest — a README, the
  docs, one heading on a Platform page written for a technical audience. It does **not**
  appear in an institutional proposal PDF, where the phrase is "our survey platform".
  The warmth is an asset with developers and a liability with a funder; C is the only
  option that puts it in front of the first and never the second.
- **Never set it as display type.** Fly appears at body or mono scale. "Fly" at Zilla
  Slab 300 / 70px is a consumer app; the system should forbid it.
- **Always give it its job in the same breath** on first mention — "Fly, our survey
  platform" — so it reads as a machine name, not a mascot.
- **The ban that is currently missing.** §6's banned list has no line covering the real
  risk of a warm name, which is that somebody eventually draws it. **Propose adding to
  §6 Banned:** *"No literal rendering of a product name — no insect, no wing, no paper
  plane, no envelope. Fly is drawn as M5 or it is not drawn."* This is the only §6 edit
  the recommendation requires, and it is the one that protects the decision from being
  eroded by a well-meaning future hand.

### What C means concretely, as a checklist

| | |
|---|---|
| `DESIGN.md` §6 M5 | Add one line: this motif is the visual identity of Fly. |
| `DESIGN.md` §6 Banned | Add the literal-rendering ban above. |
| `DESIGN.md` §7 | No change. Fly uses `#icon-survey` and `#icon-waves`; no thirteenth icon. |
| `DESIGN.md` §3 / §5 | No change. No token, no radius change. `check-contrast.py` untouched, 22 pairs still pass. |
| `assets/` | No new file. `fly-mark-*.svg` stay in the scratchpad as the record of what was rejected. |
| `CONTENT.md` Platform | Fly named once, in a heading, with the job in the same breath. Copy is the content workstream's, not this note's. |
| `docs.vlab.digital` | Retitle section "Virtual Lab" → "Recruitment"; drop the indigo `#4F46E5` node-network logo for `assets/mark.svg`; fix the empty `site.webmanifest`. All D-008. |
| `fly` repo | README H1 gains the endorsement line. `dashboard-client/public/index.html` `<title>` changes from "Virtual Lab" to "Fly". |
| Proposals | No change. `adopt` never surfaces; a proposal says "our survey platform". |
| `CLAIMS.md` | No change. C-052's `github.com/vlab-research` is untouched — which is a cost D would have incurred and C does not. |

### Does the recommendation touch D-002 or D-003?

- **D-002 — no.** Option C is the only one of the four that cannot be read as putting a
  product on sale. Fly stays inside the credibility engine, which is what D-002 says the
  platform is. **Option D reopens D-002 and this note says so explicitly**; Option B
  brushes against it by giving a buyer two proper nouns, neither purchasable.
- **D-003 — it touches it, deliberately, and does not reverse it.** The name Fly is
  warmer than the system, permanently. C does not resolve that tension; it confines it,
  by placement and by a ban on ever drawing it. That confinement is the *substance* of
  the recommendation, not a caveat attached to it. If Nandan wants the tension gone
  rather than confined, the only honest route is renaming Fly — which is Option A plus a
  rename, costs more than it is worth (§3.4), and is not recommended.

---

## 8 · Proposed `DECISIONS.md` entry — **NOT ADDED TO THE FILE**

`D-024` is the next free number (`DECISIONS.md` currently ends at D-023). Drafted for
Nandan to accept, amend or reject. **Do not paste this in without his decision.**

```markdown
### D-024 — Fly is named; the recruitment side is cited, not branded
**Status:** PROPOSED · Owner: Nandan

Virtual Lab has two technologies. **Exactly one of them is a name.**

- **Fly** is the survey platform. It is named on the site, in the docs and in the repo,
  because it is a separable artefact somebody can run without ever meeting us.
- **The recruitment side is not named.** It is "the optimizer" / "adaptive sampling",
  and it is *cited* — Donati & Rao, 2025. Its internal name `adopt` stays in the schema,
  where `chatroach` and `hermes` also live.
- **"Virtual Lab" means the company and the managed service**, and — because the
  recruitment system is not separately obtainable — the recruitment system too. The
  overload is accepted deliberately rather than tolerated silently.

**Rationale.** The software already decided: Virtual Lab drives Fly, Typeform *or*
Qualtrics as interchangeable destinations, so the two are not peers and a symmetric
architecture would assert a relationship that does not exist. A name is earned by
separability. And the recruitment method's best available name is its citation, which
outranks any invented noun for both audiences in `DESIGN.md` §1.

**Visual consequence — no new anything.** Fly's signature is **radius**, which `DESIGN.md`
§5 already reserves for the thread alone and §6 M5 already calls the one thing that
separates us from every panel provider. **No mark, no colour, no thirteenth icon.** A
product colour was tested and rejected on arithmetic: any fourth hue passing AA on
`--paper` sits within 1.04–1.20 luminance of `--data` and `--brass` and is therefore
indistinguishable from both in greyscale, which D-011 forbids. Marks were built and
rendered (`scratchpad/fly-mark-d*.svg`, `marks-sheet.png`); at 16px a thread mark and the
lattice mark read as two companies, not two products.

**Register.** "Fly" is warmer than D-003 and stays confined by placement: README, docs,
one Platform heading. Never in an institutional proposal, never as display type, always
with its job in the same breath on first mention. §6 Banned gains: *no literal rendering
of a product name — no insect, no wing, no paper plane.*

**Consequence.** `docs.vlab.digital` retitles its "Virtual Lab" section to
**"Recruitment"**, which removes the existing collision where "Virtual Lab" is both the
parent and one of two children, without inventing a word. Fly's dashboard `<title>` stops
saying "Virtual Lab". `github.com/vlab-research` is unchanged, so C-052 is unaffected.

**Rejected, and what it would take to reopen.**
- *Both engines named* (`adopt` + Fly, typeset not logotyped) — the serious alternative.
  Costs one word and buys the option of outside adoption of Fly. Reopen this if Fly
  adoption by other researchers becomes a strategy rather than a possibility.
- *Fly standalone* — own mark, domain and docs. **Reopens D-002**, which is a much larger
  decision than naming: a product with a mark and a domain is a product being sold. Also
  faces two external problems that need counsel, not design — Fly.io occupies the name in
  developer infrastructure, and `fly/LICENSE` names The World Bank Group and Curious
  Learning as copyright holders alongside "fly contributors".
- *Fly kept internal* — the status quo, which is not neutral: the docs nav says "Fly" and
  the site never would, so our own link hands a technical buyer a name we do not use.

Working note: `scratchpad/ws-fly-brand.md`.
```

---

## 9 · Found while doing this, not brand architecture, needs an owner

Recorded here because they were discovered by this workstream and would otherwise be lost.
**None of them is decided here.**

1. **`CONTENT.md` Home §3 says respondents answer "in Messenger, WhatsApp, or a web form
   built for poor connections."** The web-form channel looks **vestigial**: `fly/websurvey`
   is a built Svelte bundle last touched 2021-11-10, surveys are authored in **Typeform**
   and imported (`@vlab-research/translate-typeform`), and the docs mention a web survey
   only as a *Virtual Lab destination type*, not a Fly channel. Either the sentence is
   describing a Typeform-hosted form as though it were ours, or the channel is live and
   the repo hides it. **A claim about a delivery channel is a claim.** For the content
   workstream and Nandan, not for me.
2. **Instagram is a third supported channel** (`message-worker`, docs `fly/reference/media.md`)
   and appears nowhere in the copy deck.
3. **Fly's dashboard is unbranded and mis-branded at once** — `<title>Virtual Lab</title>`,
   default Create-React-App favicon and `manifest.json` ("React App" / "Create React App
   Sample"), Ant Design defaults (`#1890ff`), `font-family: 'Avenir'`. If a dashboard
   screenshot ever ships under D-015, it will show none of this design system.
4. **`fly/replybot/assets/logo.jpg`** is a 512×512 NASA-style galaxy image committed in
   2018 and referenced by no UI. Dead asset.
5. **`docs.vlab.digital` `custom.css`** carries two unrelated blues — logo indigo
   `#4F46E5` and header navy `#00236a` — neither a token, and the logo is a node-network
   mark, which §6 bans outright. D-008.
6. **`docs.vlab.digital/content/vlab/tutorials/connecting_fly.md` is a stub** whose entire
   body is *"Tutorial in progress."* The one page documenting how the two technologies
   join is empty. That is a content gap with brand consequences: whatever architecture is
   chosen, this is the page that has to demonstrate it.
