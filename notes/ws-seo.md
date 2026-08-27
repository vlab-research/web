# Search — what one page can and cannot win

**Written 2026-08-25** and **re-verified against the built site 2026-08-26**, after the
scaffold landed. Everything in §5 is still outstanding; the build added two findings that
change what the highest-value action is (§4.2) and one that corrects the brief (§4.3).

This is the first time SEO has been looked at in this repo. Grep for
`SEO`, `keyword`, `sitemap.xml`, `schema.org` across the whole documentation set returns
nothing: 250KB of planning and search was never a consideration. That is not an oversight
to apologise for — the site was built to be *proof*, and proof and *acquisition* are
different jobs — but it means everything here is new ground.

**A memo loses to all four documents** (`notes/README.md`). Nothing below overrides D-007,
D-023 or a word of `COPY.md`.

## What was asked, and what was settled

Nandan, 2026-08-25, asked the site to rank for recruitment-via-social-media and
recruitment-panel queries, especially with Africa / South Asia / Latin America attached;
also Qualtrics, Prolific, existing panels, recruiting for a study, medical studies, running
surveys online. And explicitly **not** to attract private-company market research, audience
insights or marketing work.

Four things were put to him in the same session and settled:

| Question | Settled |
|---|---|
| Reopen D-007 to add pages? | **No. One page stands.** |
| How far can we push D-023 for competitor queries? | **Intent, never the name.** D-023 intact |
| The medical cluster? | **Public health only** — no clinical trials |
| Do the technical work now? | **No — plan first.** This memo is that plan |

**The one-page answer is the constraint everything below is written under**, and it is
worth stating plainly what it costs, because a plan that pretends otherwise is useless.

---

## 1 · The register problem

The site's vocabulary is deliberate and correct. `DESIGN.md` §2 rule 2 — state the
mechanism, not the benefit — produced *population-representative samples · strata · target
distribution · optimization problem*, and D-027 ordered it. **None of it should change.**

But nobody types it. Buyers type *recruit survey respondents Nigeria*, *nationally
representative survey Kenya*, *WhatsApp survey data collection*, *Facebook ads survey
recruitment*. Two registers, both accurate, describing the same thing.

**The mistake available here is keyword-stuffing the hero**, and it would trade a settled,
hard-won voice for traffic that will not arrive anyway. The register bridge belongs in
three places that are **not** body copy and therefore not governed by §2:

1. **The `<title>` and `<meta name="description">`** — these are SERP artefacts, not page
   copy. A reader on the page never sees them.
2. **Structured data** — machine-addressed, invisible.
3. **`alt` text and figure descriptions** — required for accessibility anyway.

That is the whole of the on-page vocabulary opportunity under a one-page constraint. It is
narrower than it sounds and it is not nothing.

---

## 2 · Ranking realism — the table this memo exists for

Google ranks **pages**, not sites. `/#paper` and `/#audit` are anchors: they never rank
independently, never carry their own title or snippet, never accumulate their own links.
One page targets one intent cluster. Ranked honestly against the ask:

| Cluster asked for | One page? | Why |
|---|---|---|
| Branded — *Virtual Lab survey*, *vlab.digital* | **Yes, immediately** | Nothing competes |
| The method name — *adaptive survey sampling via ad platforms* | **Yes** | The phrase is ours; the paper anchors it |
| Ad-platform / social survey recruitment | **Plausible, 6–12 months** | Thin competition, academic-adjacent, the paper is topically authoritative |
| Survey recruitment in a named country | **Partial at best** | 37 country names are on the page, but see §4 — they are inside SVG, where they carry almost no weight. One page cannot rank for 41 countries |
| *Africa / South Asia / LatAm survey panel* | **No** | Needs region pages. Forfeited by the one-page decision |
| *Prolific alternative* | **No** | Needs an intent page. Forfeited |
| *Qualtrics*, *online surveys*, *survey panel* | **No, at any page count** | Head terms held by billion-dollar incumbents. Not winnable and not worth the attempt |
| Clinical trial recruitment | **Excluded by choice** | §6 |

**Read the table as the cost of the D-007 decision, stated in advance.** Roughly half of
what was asked for is not reachable from one page. That is a legitimate trade — the page is
excellent and a thin page-farm around it would be worse — but it should be a known trade
rather than a discovered one. §8 defines the evidence that would reopen it.

---

## 3 · The reframe: a one-page site spends its SEO budget off-domain

This is the useful consequence of the constraint. You cannot out-*page* anyone, so you
out-**entity** them. `vlab.digital` is a small commercial domain with essentially no
authority; what it has instead is the thing that is genuinely hard to buy:

- **A published method with a name we coined.** SSRN 5495148, Donati & Rao.
- **A second paper on a high-authority `.org`.** C-084, the malaria paper, in the World Bank
  Reproducible Research Repository and OpenKnowledge.
- **An open-source org.** `github.com/vlab-research`, self-hostable, public.
- **Six institutional users**, all `.edu` or `.org` (C-020, C-024, C-025, C-094–C-096).

Those generate the `.edu`/`.org` citations that a commercial site of this size cannot
otherwise get, and that are worth more than any number of pages. **The off-domain list in
§7 is the highest-value work in this memo** and almost none of it is code.

---

## 4 · Four findings from the built site

Verified against `_site/index.html` on 2026-08-26, not inferred.

### 4.1 · `check-claims.py` skips `script` and `svg`

`SKIP_TEXT = {"script", "style", "template", "svg"}`. Two consequences, pulling opposite ways.

**JSON-LD is outside the provenance rule.** A `<script type="application/ld+json">`
containing `841660` is never scanned, never needs `data-claim`, and would sail past the one
mechanism this repo built to stop invented numbers. **Rule, and it is not optional: every
figure in structured data is generated from the same source as the visible page —
`scripts/data/coverage.json` and `CLAIMS.md` — and never typed by hand.** Structured data is
a page the crawler reads; it earns the same discipline as the page a human reads.

### 4.2 · The site has no geographic text at all — and this is the headline finding

**Parsed with `SKIP={script, style, svg}` over the built page: not one of the 41 country
names and not one of the 6 region names appears in the homepage's HTML text.** Every
geographic string on a site that has fielded studies in 41 countries is inside the SVG.

**One correction, and it matters — the regions improved on 2026-08-26.** The strip gained a
label band the same day this was written (Nandan: *"The bars per continent are missing the
continents"*), so the six region names now render as SVG `<text>`:

```
<text class="cs-lab" x="0.00" y="50.0">MIDDLE EAST &amp; NORTH AFRICA</text>
<text class="cs-lab" x="487.89" y="50.0">SUB-SAHARAN AFRICA</text>
```

**`<text>` is not `<title>`.** A `<title>` is a tooltip; `<text>` is rendered content, and
Google extracts it — below HTML body text, but far above nothing. So the regional position
is meaningfully better than this memo first recorded, and the ranking severity below is
reduced accordingly.

**The 37 country names are unchanged and are still `<title>` only** — tooltips, weighed at
close to nothing. And no geographic string of either kind is HTML text.

**The cause is a correctly-taken fallback, not a build error.** `COPY.md` marks the region
totals **[P-4]** *"ships only if the region buckets are confirmed (`CLAIMS.md`, open, owner
Nandan); the recorded fallback is that this section publishes country figures and drops the
regional layer entirely."* The buckets are still open, so the fallback fired. The built page
renders `cov-map` and `cov-strip` — both pure SVG — and the one component that would have put
region names on the page as **real HTML text** is the one that did not ship.

The generator already emits it, and it is text, not graphics:

```html
<span class="cs-n">143,816</span><span class="cs-r">Sub-Saharan Africa</span>
<span class="cs-n">113,460</span><span class="cs-r">South &amp; Southeast Asia</span>
```

**So the highest-value SEO action available on this site is closing an open claims question
that is already on Nandan's plate.** Confirming the region buckets ships [P-4], which puts
*Sub-Saharan Africa*, *Middle East & North Africa* and *South & Southeast Asia* into the page
as indexed text — the exact vocabulary the brief asked to rank for. It is not an SEO
intervention: it is a specified component, blocked on a data confirmation, that happens to
be worth more than everything else in §5 combined.

### 4.3 · Latin America is not supportable, and the brief should change

The brief asked for **Africa, South Asia and Latin America**. The register supports two of
the three. Region totals, computed from `scripts/data/coverage.json`:

| Region | Respondents | Countries |
|---|---:|---:|
| Middle East & North Africa | 311,363 | 11 |
| Sub-Saharan Africa | 143,816 | 9 |
| Americas | 136,558 | 5 |
| South & Southeast Asia | 113,460 | 5 |
| Europe & Central Asia | 30,573 | 10 |
| Pacific | 2,838 | 1 |

**The Americas figure does not mean what the brief assumes.** Broken out:

| | |
|---|---:|
| United States | 103,475 |
| Haiti | 16,545 |
| Honduras | 6,933 |
| Jamaica | 6,006 |
| Belize | 3,599 |

**76% of the Americas is the United States**, and what remains is 33,083 respondents across
two Caribbean and two Central American countries. **There is no South America — no Brazil,
Mexico, Colombia, Peru or Argentina.** Targeting *Latin America* would put a claim on the
site that `CLAIMS.md` cannot support, on a site whose entire proposition is that its claims
are checkable. It also wins the one thing worse than no traffic: traffic that converts at
zero.

**Recommendation: drop Latin America from the target set and spend it on Africa and South
Asia, where the numbers are genuinely strong.** If Latin America matters commercially, that
is a business-development question about where to field next, not a search question.

**A related note the bucket decision now carries.** Because [P-4]'s labels become the page's
only geographic text, **the bucket names are search terms**. *"Americas"* is accurate and
matches nothing anyone types; it also silently averages the US with Haiti. That is a
`CLAIMS.md` decision with an SEO consequence attached, and it should be taken knowing both.

### 4.4 · The paper's own keywords name the audience we are avoiding

`_data/paper.json` carries the manuscript's keyword line, identical in all three editions:

> Ad Platforms · APIs · **Consumer Insights** · Online Sampling · Survey Research

**"Consumer Insights" is on this memo's own banned list** (§6) — it is the exact audience the
brief said not to attract. The keywords are the authors' and they are not wrong on a journal
submission; the market-research framing is genuinely where a methods paper finds readers.

**The rule that resolves it is D-023's, applied to a surface it was not written for.**
Structured data is our own voice, not a quotation — nothing obliges us to reproduce a
keyword line, and emitting it would be us telling Google we are relevant to consumer
insights. So `_data/schema.js` publishes **no `keywords` field at all** and uses its own
`knowsAbout` list instead. Recorded because the shortcut — *the paper says it, so it is
sourced* — is exactly the move that would undo the negative filter, and it would have looked
like good provenance discipline while doing it.

### 4.4 · The page is not thin, which is the good news

1,130 indexable words on the homepage. For a one-page site that is a real document, not a
brochure — comfortably enough to rank for the clusters §2 marks as winnable. **The
constraint on this site is breadth, not depth.** That is worth knowing, because it means the
fix for §2's forfeited half is more pages, and never more words on this one.

## 5 · On-domain work — the whole list

Ordered by leverage. **None of it touches `COPY.md`, D-007 or D-023.**

**Items 5.2, 5.4 and 5.5 shipped on 2026-08-26** — Nandan: *"work on the structured stuff.
That doesn't change copy at all, and it's a freebie."* What shipped is marked below. 5.0 and
5.1 are his; 5.3 is blocked on an asset and 5.6 needs a DNS record.

### 5.0 Confirm the region buckets — and it is not really an SEO task

Per §4.2 this outranks everything below it. It is an open `CLAIMS.md` question owned by
Nandan, it unblocks a component `COPY.md` already specifies, and it is the only action on
this list that puts the brief's own vocabulary into the index. Read §4.3 before choosing the
labels.

### 5.1 `<title>` and meta description — the highest-leverage strings on the site

Currently `"Virtual Lab — population-representative samples, recruited through ad
platforms"`. 79 characters; the SERP truncates near 60, so the mechanism clause — the part
doing the work — is the part that gets cut.

The title has three jobs at once: match the search register, qualify the buyer so a brand
manager self-deselects from the snippet, and stay in voice. **Direction, not final copy —
this is the one string where search register meets §2, so it needs Nandan's sign-off:**

> `Survey respondent recruitment in 41 countries — Virtual Lab`

The description is where the negative filter does most of its work: name researchers,
funders and agencies explicitly; name the regions; carry the paper. Never *market research*,
*consumer insights*, *audience insights*, *brand tracking*, *voice of customer*.

### 5.2 Structured data — the entity play — **SHIPPED 2026-08-26**

Invisible, copy-free, and the most direct way to tell Google *this is a research
organisation, not a martech vendor*:

- `Organization` — `knowsAbout` (survey methodology, stratified sampling, survey research),
  `sameAs` → GitHub, `areaServed` → **the 41 countries, generated from
  `scripts/data/coverage.json`**. This is how the geography reaches the index as data rather
  than as SVG tooltips (§4, finding 2), and it costs no design change.
- `ScholarlyArticle` — authors, title, SSRN URL. Ties the domain to the paper as an entity.
- **Deliberately not** `ProfessionalService` or any marketing-adjacent type. The type
  vocabulary is itself a signal.

### 5.3 `og:image` — a regression, **still open and blocked on an asset**

`_includes/base.html` carries `og:title`, `og:description` and `og:url` and **no
`og:image`**. Commit `92e25f7` added one to the legacy SPA; the rebuild dropped it. Every
share of this site currently renders blank.

**Deliberately not shipped with the rest, for two reasons.** The tag is one line; the image
is not. A social card is raster — the platforms do not render SVG for `og:image` — so it
cannot come from the four primitives the way everything else on this site does, and
`assets/apple-touch-icon.png` is the only precedent (a committed static asset, which is the
right pattern: `netlify.toml` promises `scripts/` is stdlib Python needing nothing
installed, and a rasterizer in the build would break that promise).

**And the brand faces are not installed system-wide**, so any local rasterization renders
Zilla Slab as a fallback and ships off-brand type. Closing that needs `fonttools` to convert
the woff2 kit, which is a toolchain decision.

**What it actually needs is a design call, not a script**: a 1200×630 card is a composition —
mark, wordmark, and which line of type, if any. That is `DESIGN.md`'s to answer. Shipping a
guess would be worse than the current blank, because a social card is the one asset nobody
reviews again once it looks fine.

### 5.4 `sitemap.xml` and the `robots.txt` directive — **SHIPPED 2026-08-26**

`sitemap.njk` emits `/sitemap.xml` from `collections.all`, and `robots.txt` points at it.

**It lists one URL, and that is the decision worth recording.** `/404.html` is not content.
`/privacy/` is deliberately unlinked — Nandan, 2026-08-25: it *"exists at its URL for anyone
who needs it"* — and **a sitemap entry is a positive request to index**, which is the
opposite of that intent. It carries no `noindex`, so anyone holding the URL still gets the
page; it is simply not advertised. Both already set `eleventyExcludeFromCollections`, so the
collection does the right thing on its own. **If the policy is ever linked, revisit it.**

### 5.5 Search Console — clean under D-009, **needs a DNS record from Nandan**

**Verify by DNS TXT, not by meta tag or script.** Search Console is server-side: no
client-side code, no cookie, no consent question, so it does not touch D-009 or sit beside
our own privacy policy the way PostHog did. It is also the only way to measure any of this,
which makes it a prerequisite for §8 rather than a nice-to-have.

### 5.6 Already fixed, recorded so nobody re-fixes it

`_redirects` held the SPA catch-all `/* /index.html 200`, which served the homepage at
HTTP 200 for **every** URL on the domain — infinite soft-404s and wholesale duplicate
content. It was replaced on 2026-08-25 with four explicit 301s from the old SPA fragments.

---

## 6 · The two exclusions, and why each is right

**Competitors — D-023 holds, and it holds for a reason the crawler complicates.**
D-023 bans comparative claims against another recruitment source *in our own voice*;
C-006–C-009 are `WITHHELD`, decided-against rather than pending. The settled route is
**intent, never the name**: the underlying need — panel coverage gaps outside the US, UK and
EU — is answerable without naming anyone, and Google matches intent rather than strings.
Under one page that route is mostly forfeited anyway (§2), which makes the collision
academic for now.

**One thing Nandan should know regardless.** The quoted abstract already puts *Prolific* and
*digital twins* into Google's index on the homepage. **Google does not read quotation
marks.** D-023's distinction — asserting versus quoting — is a real editorial distinction
and it is the right one; it simply has no counterpart in a crawler. This is true today, it
is an asset rather than a problem, and it is exactly the kind of premise-shift the decision
itself warns about (*"a settled decision resting on a false premise is how the decision gets
reopened by someone who spots the contradiction"*). Recorded, not acted on.

**Medical — public health only, and the split is real.** *Recruiting for a medical study*
is two markets. Ours is **behavioural and public-health research**, and the register
supports it: C-022 (Gavi, vaccine confidence), C-030 (The Public Good Projects, polio
outcomes), C-084 (the World Bank malaria paper). The other is **clinical trial patient
recruitment** — a brutally competitive, IRB- and HIPAA-adjacent space where `CLAIMS.md` has
no row that would support a single sentence. Chasing it would buy the most expensive traffic
available and the wrong buyer at the end of it.

**And the general rule for the negative filter, which is the honest version:** *you cannot
stop an impression.* There is no mechanism that keeps a brand manager from seeing the site.
What is controllable is (a) vocabulary — the banned-word list in §5.1, which the site
currently and admirably obeys; (b) qualification in the snippet, so the wrong reader
deselects before clicking; (c) entity signals, so Google files the domain under research
rather than martech; and (d) the CTA, where an email address with no form and no pricing is
already a superb filter. **The filter is at the inbox, not at the SERP.** Any plan promising
otherwise is selling something.

---

## 7 · Off-domain — the highest-value work, and almost none of it is code

Per §3, this is where a one-page site's budget goes. Each is a person-task with an owner:

1. **`github.com/vlab-research` org profile** — link `vlab.digital`. The org README is a
   high-authority page that currently does not point home.
2. **`docs.vlab.digital`** — link back. **And a real question worth opening separately:
   a subdomain splits authority; `vlab.digital/docs/` would consolidate it.** That is an
   infrastructure decision with its own costs and it is not this memo's to make.
3. **SSRN 5495148** — ensure the listing and author affiliations carry `vlab.digital`.
4. **Google Scholar and ORCID profiles** for both authors, with the affiliation linked.
5. **The World Bank repositories** — C-084 is already catalogued on two high-authority
   `.org` domains. Whether either can carry a link is worth asking.
6. **The six institutions** — project and centre pages at Columbia, Harvard, GWU, UW, WashU
   and the World Bank. These are the `.edu` links that actually move a domain this size.
   Note this is **adjacent to but not the same as D-014**: a link is not a logo, and asking
   for one does not need trademark clearance.

---

## 8 · The tripwire — what would reopen D-007, stated as evidence rather than argument

D-007 is settled and this memo does not reargue it. But the one-page decision was taken
before any search data existed, and it should be revisited on data rather than on someone's
next opinion. **The signal, once Search Console has six months of history:**

> Impressions accumulating on geographic or panel-coverage queries at **average position
> 15–40 with near-zero clicks**.

That pattern is Google saying *relevant but thin* — it has decided the domain belongs in the
result set and has nothing substantial enough to rank. It is the specific evidence that the
forfeited half of §2's table is reachable, and it is the only thing that should reopen the
page count.

Absent that signal, one page is the right answer and this memo's §5 and §7 are the work.

---

## 9 · What this memo does not do

- **It changes no copy.** §5.1 proposes a direction for two strings that are not page copy,
  and flags them for sign-off rather than writing them.
- **It settles nothing.** Per `notes/README.md`, a memo that is a decision in hiding is how
  this directory starts competing with the documents it is subordinate to. If the `<title>`
  direction, the docs-subdomain question or the tripwire are adopted, each belongs in
  `DECISIONS.md`.
- **It has not been implemented.** Nandan, 2026-08-25: plan first. Nothing in §5 has shipped
  except §5.6, which was already fixed by someone else.
