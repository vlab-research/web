# Virtual Lab — Design System

Authoritative brand and design spec for `vlab.digital`. If you are an agent building
any part of this site, read this file before writing markup, and follow it over your
own defaults. Where this document and the code disagree, this document is wrong —
fix it here in the same change.

Established: design sprint, August 2026. Phase 1 of 4 (Brand → **DESIGN.md** → Content → Build).

---

## 1. What Virtual Lab is, in one paragraph

Virtual Lab produces population-representative survey data in places and at speeds
conventional fieldwork cannot reach — and publishes the method so buyers can check it.
We sell **managed studies**. The open-source platform is the credibility engine, not the
product being purchased.

**Three things, in this order, and the site is organised on them** *(Nandan, 2026-08-22,
recorded here because it is structure rather than positioning)*:

> **There is a method. There is a technology. And with those tools we build study designs —
> and we want to talk about them.**

- **The method** is adaptive sampling: the target distribution, the hourly reallocation, the
  variance being minimised. It is what the paper is about, and it is **ours**.
- **The technology** is the software the method needs — the optimizer that runs it and the
  instrument that carries the questionnaire. Named on the site as **Fly** (D-024).
- **The designs** are what a researcher builds with both: an arm-based media experiment, a
  panel that reopens months later, a trial clustered on who shares a treatment with whom.
  They are **the researcher's**, not ours, which is why they are described rather than sold.

**And the division of labour between them, Nandan 2026-08-25, recorded because it settles a
question that looked like a contradiction:**

> **Solving the operational challenges is what the software does. Running the software is
> what we do.**

**There is no tension between "running this yourself is hard" and "the platform is open
source and self-hostable."** The difficulty is what the software exists to remove; operating
it is the service being sold. Anyone is welcome to run it themselves — **and the site says
so plainly.** How many have is operator knowledge, it is not a selling point in either
direction, and it does not go on a page.

The distinction is load-bearing in two places. It is why *Method* and *Designs* are not
synonyms — one is how we draw a sample, the other is what you can build once drawing it is
solved — and it is why the instrument is described as **scope** rather than as proof (D-002,
as clarified). **Any page that blurs these three has a structural problem, not a copy
problem.**

### Audience, in priority order

| | Who | What convinces them | What they need from the page |
|---|---|---|---|
| **1** | Institutional buyers — global-health funders, UN agencies, World Bank, foundations, M&E primes | Past performance | Named clients, operating history, compliance, ethics, references |
| **2** | Academic PIs with grant money | Peer review | The paper, the validation numbers, replicability, the source code |

Both need the same reassurance — *the sample is defensible*. They differ only in what
counts as proof. Every page carries both, in that order.

---

## 2. Voice

**Serious, reserved, accurate, knowledgeable — but digital and technical, not academic-dusty.**

The test for any sentence: *could a reviewer ask us to substantiate this, and would we
have the citation?* If not, cut it.

### The provenance rule — non-negotiable

**A number that rests on somebody else's document carries that citation in the same
visual unit.** Not a footnote, not a link at the bottom — the citation sits directly
under the figure in the same card, at the same weight as the label. This is the single
most important rule in this document. Our whole proposition is that we do not overclaim;
the design must demonstrate it before the copy claims it.

```
33                          6.1 p.p.
STUDIES RUN                 MEAN ABS. DEVIATION
Donati & Rao                vs. GSS, CPS, Pew
```

**A figure from our own operating record carries nothing.** *Amended 2026-08-26, and it
is the sharpest the rule has been.* Nandan: *"We are the ones claiming the data. Nobody
cares where it comes from. They're assuming we have access to our own data."*

He is right, and the rule is **stronger** for it rather than weaker. "Virtual Lab
production database, August 2026" under a Virtual Lab figure is not a citation. It cites
nothing a reader could go and check; it restates who is speaking, which the page already
said at the top. Four stat cells each repeating it read as a form filled in rather than a
claim defended — and worst of all, **printing it beside "Donati & Rao, 2025" devalues the
real citation by making provenance look like a house style instead of an argument.**

```
841,660                     33
RESPONDENTS                 STUDIES RUN
                            Donati & Rao, 2025
```

**Where the line falls, and it is not a judgment call at the page.** It is read from
`CLAIMS.md`, because whether a claim is somebody else's is a fact about the claim:

| Register table | Fourth column | Needs a citation |
|---|---|---|
| Headline figures, the paper, the instrument, the patterns | **Source** — where somebody else published it | **Yes** |
| Production figures | **Definition** — how *we* computed it from *our* data | **No** |

`scripts/check-claims.py` enforces exactly this and **fails safe**: exemption requires a
`Definition` column, so anything unmarked, mis-parsed or newly added to a `Source` table
still demands its citation. Two fixtures assert the two halves —
`pass-own-record.html` (first-party, no source line, must pass) and
`fail-provenance.html` (Donati & Rao figures, no source line, must fail). **If both ever
pass, citation has stopped applying to anything.**

**A definition is not an attribution, and is never removed.** The two box plots keep
their caption lines, because *"an active day is a study-day recruiting at least 20
respondents"* and *"box: 25th to 75th percentile"* are what let a reader read the figure
at all. The test is simple: **does the line tell the reader something about the number,
or only about us?**

### Do / don't

| Don't | Do |
|---|---|
| "Leverage the targeting power of digital advertising…" | "You set the target distribution. We reallocate ad budget hourly until the achieved sample matches it." |
| "…become properly-represented strata." | "6.1 percentage points from GSS, CPS and Pew on matched questions." |
| "Unlock unprecedented insight into any population." | "175 studies across 41 countries since February 2020. Half of them field in under three weeks." |
| "AI-powered sampling intelligence." | "The optimiser is open source. Read it before you buy." |

### Rules

1. Active voice. A control says what happens; the resulting state says it happened.
2. Prefer the mechanism to the benefit. "Budget reallocates hourly" beats "smarter recruiting."
3. Never claim AI. It is convex optimisation, and saying so is the stronger claim.
4. No superlative survives without a citation in the same sentence.
5. Specific beats absolute — and the specificity comes from the benchmark, not from a
   rival. "6.1 percentage points from GSS, CPS and Pew on matched questions" is worth
   more than any adjective, because it names the instrument, the yardstick and the
   number a reader can check. **The site makes no comparative claim against another
   recruitment source** (D-023, and C-006–C-009 are `WITHHELD`): no panel, no LLM
   digital twins, no "closer than" of any kind. A measured deviation from a
   gold-standard benchmark is a stronger sentence than a ranking anyway — a ranking is
   only ever as good as whoever we ranked ourselves against.
6. Numbers in prose use the same figures as the data layer. Never round differently in two places.
7. British/American spelling: **American**. (The company is a US LLC.)

---

## 3. Color

### The three jobs

Colour does exactly three jobs on this site, and **nothing does two of them**.

| Job | Carried by | Appears as |
|---|---|---|
| **Chrome** | Ink `#1F272E` | Nav, primary buttons, body text, borders on active elements |
| **Data** | Teal `#1D5F6E` | Stratum fills, chart series, map density, the live dot |
| **Accent / semantic** | Brass `#7A5C1E` | Links, kickers, nav underline, focus rings, **and "under target"** |

Brass carries both the accent job and the semantic job, which works *only* because
brass never appears in a data fill. If you ever put brass inside a bar, that separation
is broken — use a teal tint instead.

### Tokens — copy this block verbatim

```css
:root{
  /* surfaces */
  --paper:#F1F4F5;   --surface:#FFFFFF;   --sunk:#E5EBED;   --invert:#1F272E;
  /* text */
  --ink:#1F272E;     --ink-2:#4A555E;     --ink-3:#79858D;
  /* structure */
  --rule:#CFD9DD;    --rule-2:#AEBCC2;
  /* accent + semantic */
  --brass:#7A5C1E;   --brass-2:#96742C;
  /* data */
  --data:#1D5F6E;    --data-2:#9DB6BC;
  /* on inverted ground */
  --on-invert:#EDF1F2; --on-invert-2:#A9B8BF; --rule-invert:#33404A;
  --brass-inv:#C9A250; /* brass ON an ink band — identical in BOTH themes */
  --data-inv:#4E9DB0;  /* data  ON an ink band — identical in BOTH themes */
  /* lattice ground opacity */
  --lat-op:.042;     --lat-op-inv:.065;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#13181C;   --surface:#1C2227;   --sunk:#262E34;   --invert:#0C1013;
    --ink:#E6EBEE;     --ink-2:#B2BEC6;     --ink-3:#808E97;
    --rule:#2A343B;    --rule-2:#414F58;
    --brass:#C9A250;   --brass-2:#DBB768;
    --data:#4E9DB0;    --data-2:#4A6871;
    --on-invert:#E6EBEE; --on-invert-2:#94A3AB; --rule-invert:#232C33;
    --brass-inv:#C9A250; --data-inv:#4E9DB0;
    --lat-op:.055;     --lat-op-inv:.065;
  }
}
:root[data-theme="dark"]{
  /* identical to the media block above — repeat it, do not @import or alias */
}
```

### Theme rules

- Three states, not two: explicit `data-theme="dark"` / `"light"`, and **unstamped**
  (system default) where only `prefers-color-scheme` applies. All three must resolve.
- **Never declare a colour only inside a media query or `[data-theme]` block.** Define
  it on bare `:root`, redefine the *token* in the other two. A colour whose only
  definition sits behind `[data-theme]` never applies to the unstamped majority.
- `body` sets an explicit `background: var(--paper)`. A transparent body borrows the
  host's ground and the page renders one theme's text on the other theme's surface.
- Dark is a designed palette, not an inversion. Note brass **lifts** to `#C9A250` and
  teal lifts to `#4E9DB0` to hold contrast — inverting `#7A5C1E` would give mud.

### Contrast — measured, not estimated

Computed with the WCAG 2.x relative-luminance formula. Re-run the check if any token moves.

**Light theme, on `--paper` `#F1F4F5`:**

| Token | Hex | Ratio | Verdict |
|---|---|---|---|
| `--ink` | `#1F272E` | 13.69:1 | AAA |
| `--ink-2` | `#4A555E` | 6.90:1 | AA |
| `--ink-3` | `#79858D` | 3.42:1 | **Large text / non-text only** |
| `--brass` | `#7A5C1E` | 5.63:1 | AA |
| `--data` | `#1D5F6E` | 6.52:1 | AA |

**Dark theme, on `--paper` `#13181C`:**

| Token | Hex | Ratio | Verdict |
|---|---|---|---|
| `--ink` | `#E6EBEE` | 14.88:1 | AAA |
| `--ink-2` | `#B2BEC6` | 9.42:1 | AAA |
| `--ink-3` | `#808E97` | 5.30:1 | AA |
| `--brass` | `#C9A250` | 7.46:1 | AAA |
| `--data` | `#4E9DB0` | 5.76:1 | AA |

**On an ink band (`--invert`), in either theme:**

| Token | Ratio (light `#1F272E` / dark `#0C1013`) | Verdict |
|---|---|---|
| `--brass-inv` `#C9A250` | 6.32:1 / 7.98:1 | AA |
| `--on-invert-2` | 7.42:1 / 7.36:1 | AA |

### The `--brass-inv` trap — read this before building an ink band

An ink band is **dark in both themes**. `--brass` is not: it is `#7A5C1E` in light and
`#C9A250` in dark. Putting `--brass` on an ink band therefore gives **2.43:1 in light
mode** — a hard failure, and an easy one to miss because it looks correct in dark mode.

**On an ink band, brass is always `--brass-inv`.** Links, icons, terminal accents,
footer hover — all of them.

**The same trap applies to `--data`, and it is worse.** `--data` `#1D5F6E` on a light-mode
ink band measures **2.10:1** — a more severe failure than the brass one. On an ink band,
data is always **`--data-inv`** `#4E9DB0` (4.88:1 light, 6.16:1 dark).

**And to source lines.** §8 sets the stat-row source line in `--ink-3`, which is **4.00:1**
on an ink band and fails AA. On an ink band the source line is `--on-invert-2` (7.42:1).
Both pairs are in `scripts/check-contrast.py`; the script is the enforcement, not this
paragraph.

`--ink-3` is for eyebrows, captions, and axis labels. If you catch yourself setting a
paragraph in it, use `--ink-2`.

### Bans

- No gradients. Anywhere. Including "subtle" ones.
- No shadow deeper than `0 1px 0 rgba(31,39,46,.05)`. Elevation is expressed by hairlines.
- No colour outside these tokens. A new colour requires a change to this file first.
- No semantic red/green. On-target and under-target are the only two states this site
  encodes, and they are teal and hatched-brass.

---

## 4. Typography

Four faces, each with exactly one job. Four is one more than usual and deliberate:
on a site whose subject is measurement accuracy, numerals earn a typeface of their own.

| Face | Weight | Job | Never used for |
|---|---|---|---|
| **Zilla Slab** | 300 (400 for small headings) | All display type, the wordmark | Body copy, UI labels |
| **Source Sans 3** | 400 / 600 | Interface, body copy, buttons, nav | Numerals in a data context |
| **Source Serif 4** | 400 | Study abstracts, the paper abstract, long-form method prose | Anything interactive |
| **IBM Plex Mono** | 400 / 500 | **Every numeral**, eyebrows, labels, table cells, code | Running prose |

Zilla Slab against IBM Plex Mono is the pairing that does the work — a humanist slab
against an engineering mono. It is why the page reads as an instrument rather than as a
research journal (Zilla alone) or a developer tool (mono alone).

### Scale

```css
h1  { font: 300 clamp(42px,6vw,70px)/1.02 "Zilla Slab"; letter-spacing:-.018em }
h2  { font: 300 clamp(28px,3.6vw,42px)/1.10 "Zilla Slab"; letter-spacing:-.012em }
h3  { font: 400 20px/1.30 "Zilla Slab" }
body{ font: 400 16.5px/1.6 "Source Sans 3" }
.sub{ font-size:18px; line-height:1.55 }        /* hero deck only */
small,.caption{ font-size:13px }
.eyebrow{ font: 500 11px "IBM Plex Mono"; letter-spacing:.15em; text-transform:uppercase }
.stat .n{ font: 400 clamp(32px,3.6vw,42px)/1 "IBM Plex Mono"; letter-spacing:-.025em }
```

### Rules

- `font-variant-numeric: tabular-nums` on **every** numeral, without exception.
- `text-wrap: balance` on all headings.
- Running text caps at ~65ch. Hero decks at ~50ch. Abstracts at ~62ch.
- Uppercase always carries `letter-spacing`, minimum `.11em`.
- Headings are Light (300). Bold Zilla Slab does not appear on this site.
- Every stack declares a real fallback: `"Zilla Slab", Georgia, serif` /
  `"Source Sans 3", "Helvetica Neue", Arial, sans-serif` /
  `"IBM Plex Mono", ui-monospace, monospace` /
  `"Source Serif 4", Georgia, serif`.
  *The fourth stack was missing — the bullet named three for four faces. Note that
  Georgia now backs both Zilla Slab and Source Serif 4, so a page that loses both
  webfonts also loses the display/prose contrast between them. Open: whether the Zilla
  fallback should move to a distinct slab or system serif.*

### Font hosting — self-host, do not use the Google CDN

All seven face+weight combinations are in `fonts/` and declared in `css/fonts.css` —
latin and latin-ext woff2, `font-display: swap`, 271.7 kB in total. Link `css/fonts.css`;
**never link a `fonts.googleapis.com` stylesheet from a page.** File table in D-012.

Reason: a German court (LG München I, Jan 2022) held that embedding Google Fonts transmits
visitor IP addresses to a US server without consent, in breach of GDPR. We sell to EU
institutions and our privacy policy states EU hosting. Loading fonts from a US CDN
contradicts the page it sits next to.

*(The design mockups published as Artifacts use the Google CDN because the Artifact CSP
permits no other font host. That is a constraint of the preview, not the spec.)*

---

## 5. Layout

- Container: `max-width: 1180px`, `padding: 0 32px`.
- **Everything is left-aligned.** No centred headlines, no centred hero, no centred CTA.
- Sections separate with a `1px solid var(--rule)` top border. The grid is visible —
  structure is part of the argument.
- Vertical rhythm: `84px` standard section padding, `56px` for compressed bands.
- Sibling groups lay out with flex/grid + `gap`. Never per-element margins that collapse.
- Wide content (tables, code, charts) gets its own `overflow-x: auto` container. The
  body never scrolls sideways.
- Radius is `2px`, everywhere, or `0`. Never more. Rounded corners belong to the thread
  motif alone.
- Breakpoints: `960px` (hero stacks), `900px` (two-col → one), `860px` (nav collapses,
  three-col → one), `760px` (stat row → 2×2).

---

## 6. Motifs

Five recurring forms, all built from four primitives: **a horizontal bar, a vertical
tick, a square cell, a bracket**. Anything that needs drawing — icon, divider,
background, diagram — is built from those and nothing else. That constraint is what
keeps illustrations drawn two years apart by different hands looking like one company.

### M1 · Cell lattice — *load-bearing*

A stratification design **is** a grid: gender × region × age is literally a matrix of
cells, some full, some empty.

```html
<svg class="lat" aria-hidden="true">
  <defs><pattern id="latX" width="18" height="18" patternUnits="userSpaceOnUse">
    <rect width="8" height="8" fill="currentColor"/></pattern></defs>
  <rect width="100%" height="100%" fill="url(#latX)"/>
</svg>
```
```css
.lat{position:absolute;inset:0;width:100%;height:100%;
     color:var(--ink);opacity:var(--lat-op);pointer-events:none}
.lat.inv{color:var(--on-invert);opacity:var(--lat-op-inv)}
```

- Cell 8px, pitch 18px. Do not alter the ratio — it is the same lattice at every scale.
- Opacity comes from `--lat-op` / `--lat-op-inv` only. Never hard-code it. On paper it
  must read as texture on inspection and as nothing at a glance.
- Each instance needs a unique `<pattern id>`.
- Parent needs `position:relative; overflow:hidden`; content above it needs `position:relative`.
- **Used on:** hero, ink bands, CTA, footer, 404, loading states, country coverage map, the mark.

### M2 · Bar and target tick — *load-bearing, the signature*

Achieved fill against a target tick, per cell of the design. The literal output of the
optimiser and the literal thing a buyer purchases.

- **The tick sits at the same x-position across an entire stack.** A reader scans one
  vertical line and sees every short cell instantly. Never re-scale bars individually —
  that is what makes it a system rather than a chart.
- On target: solid `var(--data)`.
- Under target: hatched brass, `repeating-linear-gradient(135deg, var(--brass) 0 3px,
  transparent 3px 6px)` with `box-shadow: inset 0 0 0 1px var(--brass)`.
- **Hue and pattern both encode the state.** Redundant by design: it survives greyscale
  printing and colour-blind readers. A methodologist reading the page notices.
- **Below about 24px the hatch is dropped.** A 3px-period hatch is sub-pixel at 16px and
  renders as flat brass at best. At that size the state is carried by hue **and by the
  bar's length against the tick** — under-target stops visibly short, on-target reaches
  it. The redundancy requirement of D-011 is met by length rather than by pattern; it is
  never met by hue alone.
- Any stack of bars carries a legend naming both states.
- **Used on:** hero, study cards, dashboard, proposal PDFs, favicon.

### M3 · Interval — *specialist*

`├──■──┤`. An estimate is never a number, it is a number and its uncertainty.
The centre mark is a **cell**, not a dot — a circle is not one of the four primitives,
and the icon set draws it as a cell, so the motif does too.

- Appears **only where a real interval exists**. Decorative use would be a lie.
- Our estimate uses `--data`; comparators use `--ink-3`.
- **Used on:** benchmark comparisons, the paper page, any figure with error.

### M4 · Tick rule — *specialist*

A hairline carrying graduated ticks — a ruler edge. Major graduations reach higher than
minor ones. The cheapest way to make an empty margin read as an instrument face rather
than as whitespace.

- **Used on:** section edges, study timelines, scroll progress, longitudinal wave diagrams.

### M5 · Thread — *specialist*

Offset rounded rectangles. The one non-statistical motif, and the one thing that
separates us from every panel provider: respondents are reached in a *conversation*,
in an app they already use, and the same thread is still open four months later.

- Rounded (`rx` = half height). This is the only place radius exceeds 2px.
- **Never** with faces, avatars, or illustrated people.
- A dashed rule with a `+4 months` label conveys the longitudinal point.
- **Used on:** channel explanation, longitudinal story, WhatsApp/Messenger section.

**M5 is the visual identity of Fly** — the survey instrument respondents answer in, named
on the site by **D-024** (settled 2026-08-21). The motif was written into the system before
the product was named, and it holds the system's single exception to the 2px radius rule:
**Fly's signature is radius.** That is the whole of it. **There is no Fly mark, no Fly
colour and no thirteenth icon** — a fourth hue was tested and fails D-011's greyscale rule
by arithmetic, and a second mark rendered at 16px reads as a second *company*. Fly's glyphs
are the two §7 icons that already served it, *Survey* and *Waves*. The bans above apply
unchanged, and one more is added below.

### Banned — never, in any form

- Rotating wireframe globes. Dotted world maps with arcs between cities. **This one
  matters most — it is the first thing every competitor reaches for.**

  **Where the line is** (settled in D-018, because §6 previously banned maps in one
  breath and sanctioned a "country coverage map" in another): a **choropleth carrying
  real values with a legend is allowed** — it is a chart that happens to be shaped like
  a map. A globe, an arc, a pulsing dot, or any map drawn for atmosphere rather than to
  encode a number is not. The test is whether removing the data would leave the graphic
  intact. If it would, it is decoration and it is banned.
- Speech bubbles with faces, avatar clusters, illustrated people.
- Neural-network node graphs, circuit traces, anything implying AI.
- Upward-right arrows, funnels narrowing to a coin, magnifying glasses. **The banned
  thing is the coin** — the conversion metaphor. Three centred bars narrowing downward
  (§7, *Recruit*) are a population narrowing to a sample, which is the true mechanism and
  is sanctioned. The two forms are adjacent enough that the distinction is stated here
  rather than left to judgment.
- Gradients, glassmorphism, drop shadows, glows.
- Stock photography of people holding phones.
- **No literal rendering of a product name — no insect, no wing, no paper plane, no
  envelope. Fly is drawn as M5 or it is not drawn.** Added 2026-08-21 with D-024. The risk
  a warm name carries is not that it is used; it is that somebody eventually **draws** it,
  and the drawing is what turns a machine name into a mascot. The same line governs type:
  **"Fly" is never set as display type** — body or mono scale only, because the word at
  Zilla Slab 300/70px is a consumer app, not an instrument.

---

## 7. Icons

24×24 grid · 1.75px stroke · square caps · `fill="none"` unless the icon is cells ·
`stroke="currentColor"` always · no rounded joins except the thread.

Built from the same four primitives. If a needed icon cannot be built from bars, ticks,
cells and brackets, that is a signal the concept does not belong on the page.

| Icon | Construction |
|---|---|
| Stratify | Three bars, descending lengths |
| Optimize | Three bars + a full-height target tick at right |
| Recruit | Three centred bars narrowing downward |
| Survey | Two offset rounded bars (thread) |
| Weight | A rule with three cells of differing size **seated on it**, ascending |
| Waves | A baseline with three verticals of differing height |
| Open source | Two facing brackets `[ ]` |
| Precision | Two rules, a centre cell, two end ticks |
| Coverage | Six cells at two opacities |
| Monitor | An axis with a polyline |
| Export | A grid with one column rule emphasised |
| Interval | Two brackets with two crossbars |

**Two constructions were corrected by drawing them, 2026-08-20.** *Weight* and
*Precision* were specified with **dots**, and a circle is not one of the four primitives
— at 24px three stroked circles on a rule read as chain links, not as weights. Both use
**cells** instead. And "three cells threaded on a rule, centred" produces a squat object
that reads as a bolt or a dart; the cells are **seated on** the rule, bottoms aligned,
with the rule extending past them at both ends, which reads immediately as mass on a
beam. Eight variants were rendered at 24 and 56px before choosing.

*Weight* now shares a silhouette family with *Waves* (a baseline with three verticals).
They are distinguished by fill — Waves is hairline strokes reaching much higher, Weight
is solid cells in the lower band. If both ever appear in the same row, revisit.

**The set is built, not described.** Twelve icons in `assets/icons/*.svg` at 24×24, plus
a `<symbol>` sprite `assets/icons/icons.svg` with ids `#icon-<slug>`. Every coordinate is
a multiple of 0.5; content lives in an 18×18 optical box, x and y in [3, 21], so square
caps never touch the viewBox edge. The three-bar icons share rows y = 6 / 12 / 18. No
`<title>`; decorative use carries `aria-hidden="true"` at the call site.

**The sprite must be inlined.** `<use href="external.svg#id">` does not work
cross-document in Chrome or Safari. `icons.svg` is written to be dropped straight after
`<body>` (`width="0" height="0" style="display:none" aria-hidden="true"`), after which
`<use href="#icon-stratify"/>` resolves. This is also what hard rule 8 wants.

**`--` cannot appear inside an XML comment.** Token names in SVG comments are written
without the leading dashes, or the file will not parse.

Icons take `var(--brass)` in step/feature contexts, `var(--ink)` in navigation.

---

## 8. Components

### Ink band — *use this for the moments that matter*

An inverted section: `background: var(--invert)` with `.lat.inv` behind it. This is the
site's one contrast device and its strongest visual moment. It marks a section as
important. **Use it sparingly — no more than two per page, never adjacent.**

```html
<section class="band inv">
  <svg class="lat inv" aria-hidden="true">…</svg>
  <div class="wrap pad"> … position:relative content … </div>
</section>
```

On an ink band: headings `--on-invert`, prose `--on-invert-2`, links and icons
**`--brass-inv`** (never `--brass` — see §3), hairlines `--rule-invert`, primary buttons
flip to `--on-invert` ground with `--invert` text.

Established uses: the platform/open-source section, the footer. Candidates: a pricing
band, a "how a study runs" walkthrough, the paper page header.

### Nav

Sticky, 66px, translucent paper with `backdrop-filter`, 1px bottom rule. Lattice mark
(22px, nine cells, five filled) + "Virtual Lab" in Zilla Slab 300. Primary CTA is a small
solid ink button, always rightmost, always "Request a proposal."

**There are no nav links.** *Settled 2026-08-26.* Nandan: *"It's okay if we don't have any
top navigation. It's a one page site."* The bar carried two anchors — *The paper* and
*Audit trail* — which scrolled you down the page you were already on: a table of contents
wearing a navigation's clothes. **The anchors still exist** (`/#paper`, `/#code`) so a
procurement reviewer or an academic has a URL to link; they are simply not advertised.

The link treatment is kept here — *Source Sans 14.5px `--ink-2`; active link `--ink` with
a 2px brass underline flush to the bottom rule* — and applies the day this site has a
second surface to navigate **to**. It is not in `css/site.css` until then.

### Buttons

| Variant | Treatment | Use |
|---|---|---|
| `.pri` | Solid `--ink`, `--paper` text | One per view. The conversion action. |
| `.sec` | 1px `--rule-2` border, `--ink` text | Secondary path (read the paper, all studies) |
| `.brass` | Brass text, no padding, trailing `→` | Tertiary / inline navigation |
| `.oninv` | Solid `--on-invert` on an ink band | Primary inside an ink band |

11px/19px padding, 2px radius, 14.5px 600 weight. Transitions on colour only, 150ms.

### Stat row

Four cells, 1px gaps over a `--rule` background, top and bottom rules. Number in Plex
Mono at `clamp(32px,3.6vw,42px)`, unit suffix at `.46em` in `--ink-2`. Label in mono
uppercase `--ink-2`. Mark the number `data-claim="C-00n"` — see "Claim annotation" below.

**Source line in Source Serif italic `--ink-3` — mandatory for a third-party figure, and
absent for our own** (§2, amended 2026-08-26). On an ink band it is `--on-invert-2`;
`--ink-3` fails contrast there — see §3. Mark it `data-claim-source`.

**The totals band on the page carries none**, because all four cells are our own
operating record. It previously repeated *"Virtual Lab production database, August 2026"*
four times across one row, which is the failure mode this amendment exists to stop: the
provenance rule performed rather than applied.

### Stratum readout

Surface card, 1px rule, hairline-separated header and footer. Header: study identifier
(mono eyebrow) left, live indicator right. Rows are
`grid-template-columns: minmax(96px,142px) 1fr auto` — label, track, `achieved / target`
in mono. Legend below the stack. Footer explains the mechanism in one sentence.

### Study card

Surface card. Kicker row: geography in brass mono uppercase, year in `--ink-3` mono
right-aligned. Title in Zilla Slab 20px. Abstract in **Source Serif** 15px. Facts row
pinned to the bottom above a hairline: value in mono 17px, label in mono 9.5px uppercase.

**Always include field time.** It is the number a buyer facing a collapsed timeline is
actually shopping for.

### Client wall

**Rewritten 2026-08-25, reversing this section's previous rule.** It used to read: *"a named
engagement is worth more to a procurement reader than a logo alone,"* and it specified
institution in Zilla Slab with the engagement beneath it. **Nandan, 2026-08-25:** *"There's
really no need for study names. That looks stupid. What we need is the logos themselves. It
can just be 'used by researchers from' for all logos."*

**One heading, one row of marks, no engagement text.**

- **Heading: "Used by researchers from."** One frame for every mark, including commissioned
  clients — it is the weaker claim and it is true of all of them.
- **Three columns, 1px gaps, paper cells, min-height 108px.** *Corrected 2026-08-25 during the build.* This read **four columns** from the days when the wall's length was open; the wall is now exactly six institutions (COPY.md §1.5), and six in four columns leaves two dead cells in the second row. A wall whose last row is half empty reads as a wall that lost two logos — which is the one thing a client wall must not suggest. Three columns × two rows is a full rectangle at every mix of mark and type. Two columns at 860px, one at 640px.
- **Marks are monochrome `currentColor` SVG**, set in `--ink` at the same **optical** height,
  not the same bounding-box height. A wordmark and a shield at identical box heights do not
  read as equals; normalize by eye and record the per-mark scale.
- **No colour, no drop shadow, no mark larger than another.** Unchanged, and it is what keeps
  a wall of foreign brands looking like one system rather than a sponsor page.
- **Each mark carries an accessible name** — `role="img"` with a `<title>` naming the
  institution — because a monochrome mark is not self-describing to a screen reader.
- **Degrade to type.** A mark that is not cleared, or not supplied, renders as the
  institution's name in Zilla Slab 400 17px in the same cell. The wall must look deliberate
  with any mix of the two.

**This is the site's one exception to hard rule 8**, and it is narrow. Hard rule 8 says all
graphics are inline SVG built from the four primitives; **a third-party logo is somebody
else's artwork and cannot be**. The exception covers institutional marks on this component
and nothing else — it does not license illustration, iconography or decoration from outside
the system anywhere else on the site.

**Logos are a permission question before they are a design question — D-014, and it is live
again.** Displaying an institutional mark usually requires written permission, and university
trademark policies are generally stricter than agencies'. A wall of type needed no clearance;
a wall of marks does. See hard rule 4 and D-002.

### Coverage section### Coverage section

Three artefacts, always built together by `scripts/build-coverage-map.py` from
`scripts/data/coverage.json`. Never hand-edit the output; refresh the data and re-run.

**It lives on Home, on paper ground** (D-019). Home is at the two-ink-band limit —
validation and the footer — so the coverage section is never a band, and the Studies
index carries no map.

**1 · Map.** Cropped choropleth, per D-018. Covered countries fill `--data` at five
opacity steps by order of magnitude (`.26 / .40 / .56 / .76 / 1`); everything else is a
`--rule` hairline at `.7`; countries covered but not counted are a dashed `--data`
outline, **never a zero fill**. Frame is the bounding box of covered countries.

The legend names all six states, and the five step labels are **thresholds by order of
magnitude, not round marketing numbers**: `under 100 · 100+ · 1,000+ · 10,000+ ·
100,000+`, plus `covered, count pending`. Generate them from the same function that
fills the shapes; do not write them by hand. (The previously published labels were wrong
— see D-018.) The legend's magnitude labels are scale marks, not claims, and carry
`data-claim="none"`.

**2 · Region strip.** One horizontal bar (M2 without a target tick — there is no target
for "respondents by region"), regions largest first. Segment **width** carries the value;
segment **opacity** carries the rank, on a six-step ramp `.95 / .78 / .62 / .48 / .34 /
.22` over a `--rule` ground showing through as 1px gaps. Bar height 30px, full width.
Inline SVG, not flex `<div>`s — hard rule 8.

**It carries a label band, added 2026-08-26.** Nandan: *"The bars per continent are missing
the continents."* They were: the region names lived only in the `aria-label` and in each
segment's `<title>`, so they reached a screen reader and a hover and nobody else. **The
strip was drawn as the top half of a pair** whose bottom half — the six region cells — named
the regions, and those are held on the bucket question. A bar with no labels is not half a
component; it is an unreadable one.

- **Names only, never values.** The bucketing is editorial and has no `CLAIMS.md` row, so
  the six figures stay off the page. A name is not a figure, and the widths are drawn from
  a `VERIFIED` table.
- **Mono 10px uppercase, `--ink-2`, letter-spacing `.13em`** (§4: uppercase always tracks).
- **Labels are placed greedily onto three candidate baselines**, each taking the first that
  clears the last label already on it. Alternating by index was the first attempt and it ran
  *"SOUTH & SOUTHEAST ASIA"* straight into *"PACIFIC"*. Four of six segments hold their own
  name; Europe & Central Asia is 4% of the bar and the Pacific is 0.4%.
- **A leader tick in `--rule-2` joins every label to its own segment**, which is what makes
  pushing a label away from its segment safe.
- **`preserveAspectRatio="none"` is gone.** It kept the bar 30px at any width and stretched
  everything else horizontally, which is why this drawing could never carry a word of type.
  Uniform scaling costs a pixel of bar height at full measure and buys labels that are not
  smeared.

**3 · Region totals.** Six cells, 1px gaps over `--rule`, top and bottom rules — the stat
row at region scale, so these stay HTML rather than SVG. Number in Plex Mono
`clamp(22px,2.2vw,28px)`, region in mono uppercase `--ink-2`, country count in Source
Serif italic `--ink-3`. A region containing a country with no count carries
`floor — N not yet counted` in `--brass` **in the cell**, and the block below it explains
why in prose.

**The bar and the cells span the attributed respondents, not the whole.** 103,052 of
841,660 belong to studies whose strata carry no country tag (`CLAIMS.md`). Each of the
three source lines states its own denominator; none of them may imply the regions sum to
the headline figure, and none may run the two gaps together — the missing 103,052 is the
unattributed studies, **not** the four countries that are covered but not yet counted.
Whether the strip draws the unattributed remainder as a ghost segment is **D-022, open**.

Source line mandatory on each of the three, as for any figure — see "Claim annotation"
below. All colour is `var(--…)`; there is no literal hex anywhere in the emitted markup,
so all three inherit the page theme and hold in all three theme states.

**~~Drift, recorded 2026-08-21: the generator emits no `data-claim` attribute at all.~~
Fixed 2026-08-25 in `build-coverage-map.py`, where it belonged.** The legend's six labels now
carry `data-claim="none"` and the map reports `[annotated]` and clean. The spec was right and
the generator had not caught up; the output was never hand-edited. Two notes worth keeping:
the fix mattered more once a page annotated its own figures, because an un-annotated numeral
on an annotated page escalates from `unsourced` to `unannotated`; and the region totals were
**not** fixed the same way, because their problem is not annotation — it is that the bucketing
has no row. See `AGENTS.md`, "Known drift".

### Step list, and the recap that points back into it

**Added 2026-08-26.** Part 2 states its job as **one list of six steps**, and the sections
that follow **point back into it** rather than restating it. Four structures were mocked and
Nandan chose this one.

**Every step carries a handle** — a short mono name beside its number: *Strata · Allocation ·
Prices · Uniqueness · Incentives · Follow-up*. Three columns at full measure: number (38px),
handle (132px), text. Number and handle in **IBM Plex Mono 500 / 11px / `.13em` uppercase**,
number in `--ink-3`, handle in `--ink`. Hairline between rows, top and bottom.

**The recap** is the pointer: number and handle only, no description, directly under the
section heading, capped at 320px. **Same two tokens as the list it points at**, so a reader
reads it as a reference rather than as a second list. On an ink band the numbers go
`--on-invert-2` and the handles `--on-invert` — `--ink-3` measures 4.00:1 there and `--ink`
disappears outright.

**The handles must earn their keep.** A handle is decoration unless the copy uses it
afterwards; if a section would read identically with the names deleted, the list has grown a
column for nothing. The recap is the minimum use — the prose should use them as ordinary
words too, which is why the band's closing paragraph reads *"Prices are not known in
advance"* rather than *"p_h is not known in advance."*

**One handle is doing careful work.** The list says **person**; C-069 only supports per
**account**, and its scope note forbids writing it as a fraud or duplicate-prevention claim.
**Uniqueness** is deliberately neutral: it keeps the gap visible instead of quietly closing
it, and the two lines are allowed to not quite meet.

**Below 640px the handle moves above the text** in the second column. A 132px name column
and a readable measure do not both fit on a phone, and the handle is what the recap points
at, so it keeps its own line rather than being squeezed.

**The step numbers are list counters and carry `data-claim="none"`** — see "Claim
annotation". The predecessor used a CSS counter and so had no text node to scan; these are
real text and would otherwise report as `unannotated`.

### The thread — M5 as a drawing

**Added 2026-08-26**, `assets/figures/thread.svg`. Nandan asked for something showing what a
respondent actually sees — *"chat bubbles or something like that with the questions or the
way the list pops up in WhatsApp or Messenger"* — and §6 M5 already reserved exactly this:
*used on: channel explanation, longitudinal story, WhatsApp/Messenger section.*

- **Offset rounded rectangles, `rx` = half height.** The one place radius exceeds 2px.
- **The survey speaks in `--sunk` with `--ink` text; the respondent answers in `--ink` with
  `--paper` text**, right-aligned. Both invert correctly with their tokens, and an `.inv`
  variant swaps them for an ink band, where `--sunk` and `--ink` are near invisible.
- **A dashed `--rule-2` rule labelled `MONTHS LATER`** carries the longitudinal point.
  **§6 M5 specifies "+4 months" and this deliberately does not use it:** C-041 is a real
  four-month follow-up and is `PLACEHOLDER`, so a number there could be read as our
  specification rather than as an illustration. The point does not need the number.
- **The question and choices are illustrative** — not from a study, not a claim. Every
  numeral carries `data-claim="none"`: the indices are indices, and the reply is the index
  the respondent picked.
- **Never with faces, avatars or illustrated people**, and no literal rendering of the
  product name. Fly is drawn as M5 or it is not drawn.
- **Hand-authored, not generated.** It encodes no data, so there is nothing for a generator
  to read — the precedent is `assets/mark.svg`. **A double hyphen cannot appear inside an
  XML comment** (§7): its comment names tokens without their leading dashes, and this file
  hit that trap on its first write.

**It sits beside the prose it illustrates**, in the page's only two-column block. That is
prose beside an illustration, not job beside answer — the arrangement rejected for the step
list, whose mapping had to survive a phone. This one does not: stacked below 900px, the
thread simply follows the words.

### Feature list

**Added 2026-08-26.** A `<dl>` at the foot of the platform section: two columns, 1px gaps
over `--rule`, top and bottom rules — **the stat row's construction at a smaller scale**.
Term in mono 10px uppercase `--ink-2`; definition in Source Sans 14.5px `--ink-2`. One
column below 900px.

**It is a reference block, not the spine.** D-027 killed a feature inventory as the site's
structure; this is eight sourced capabilities under a section that has already said what the
platform is for. **Four traps travel with it**, and each has burned a draft before: no image
collection (C-066, built then pulled), no Instagram (C-058, and the docs site is wrong), no
*"full multilingual support"* (C-067 — closed-ended answers only), and **nothing may imply a
form builder** (C-082 — surveys are authored in Typeform; Fly imports and runs them). A
fifth: the **web form is a study-level destination**, so never write that Fly runs one.

### Forms

Label in mono 10px uppercase `--ink-3` above the field. Input on `--paper` ground with
`--rule-2` border, 2px radius, 15px Source Sans. Focus: 2px brass outline with 1px
offset *and* brass border. Submit is full-width `.pri` inside the box.

### Claim annotation

Applies to every component above that carries a figure. **Any element carrying a figure
declares which claim it is**, so the provenance rule can be *checked* rather than
reviewed. Six attributes, no classes, no JavaScript:

| Attribute | Meaning |
|---|---|
| `data-claim="C-003"` | This element's numerals are the value of C-003. Space-separate several ids. |
| `data-claim="none"` | This numeral is deliberately not a claim — a list counter, a year in a kicker, a legend's scale mark, a street number. |
| `data-claim-source` | This element is the visible source line. |
| `data-claim-unit` | This element is the visual unit — the widest element a value may draw its source line from. |
| `data-claim-scan="off"` | Stop scanning numerals inside this element. Legal copy only. Banned values are still checked inside it. |
| `data-claim-quote="C-055"` | The words inside are somebody else's, reproduced verbatim, attributed to the `VERIFIED` row named. Their numerals are that author's figures, not our claims. |

```html
<div class="cell" data-claim-unit>
  <div class="num" data-claim="C-003">6.1<span class="unit">p.p.</span></div>
  <div class="label">MEAN ABS. DEVIATION</div>
  <div class="src" data-claim-source>vs. GSS, CPS, Pew</div>
</div>
```

Without `data-claim-unit` the unit is the nearest `figure`/`li`/`td`/`section` or
`.cell`/`.card` ancestor, and **only that one counts** — a source line elsewhere on the
page is not provenance. With it, the search widens to that element and stops there, which
is how one `<figcaption>` legitimately serves every row of one figure.

`python3 scripts/check-claims.py` enforces this. It is not optional decoration: the
stat row's source line is mandatory in this section, and this is the mechanism that makes
"mandatory" mean something. **Annotate every page.** An un-annotated page is still
scanned, heuristically, against every numeral in the register — but heuristic mode can
pass a number by coincidence, and a false pass is exactly what this rule exists to
prevent.

### Math notation

**Added 2026-08-25**, when the homepage gained the optimization block. Displayed math is
**notation, not a figure**: the exponents, subscripts and indices in $W_h^2\sigma_h^2/n_h$
are structure, and a numeral inside them is not a value anyone can check against
`CLAIMS.md`.

- **The whole math block carries `data-claim="none"`.** Not `data-claim-scan="off"`, which is
  reserved for legal copy.
- **The surrounding prose is not exempt.** If a sentence beside the math states a value, that
  value needs a row like any other.
- **The block carried a source line until 2026-08-26**, when the paper moved directly
  beneath it. The math is somebody's published formulation and must be cited as such — but
  with the title, byline, abstract and SSRN link now immediately below, a *"Donati & Rao,
  2025"* line between the two cited the same document twice in three lines. The citation is
  the paper block. **If the math is ever separated from it again, the source line comes
  back.**
- **No new typeface.** Math is set in the existing serif and mono; a math face would be a
  §4 change and rule 5 applies.
- **Render as MathML**, not as an image: it inherits `currentColor`, so it holds in all three
  theme states and on an ink band, and it stays selectable and accessible.

### Attributed quotation — `data-claim-quote`

**A quotation is attributed speech, not a claim.** `CLAIMS.md` governs what Virtual Lab
asserts; reproducing what a source says, accurately, is the opposite of overclaiming. That
one sentence is the whole justification, and it is why the paper's abstract may state
$0.30 per question on the Papers page while C-004 withholds that figure from every
sentence the site writes in its own voice.

```html
<blockquote data-claim-quote="C-055">
  <p>This paper introduces and validates a new methodology …</p>
  <p class="src" data-claim-source>Abstract, quoted verbatim.
     Donati &amp; Rao, 2025. https://ssrn.com/abstract=5495148</p>
</blockquote>
```

The shield is deliberately narrow, and `check-claims.py` enforces all three constraints
rather than describing them:

1. **It must name a `VERIFIED` `CLAIMS.md` row for the document being quoted.** Not
   nothing, not a free-text string like `"the paper"`, not a withheld row. A quotation is
   attributed to something or it is not a quotation.
2. **It must carry a visible attribution line**, checked exactly as a figure's source line
   is — same unit, same rule.
3. **Every withheld value it shields is reported at `warn` level on every run**, naming
   the value and the row that withholds it. The shield stops a build failing; it never
   stops a human seeing.

**Paraphrase inside a quote block is not quotation, and the checker cannot tell the
difference.** The exemption belongs to the container, so anything written inside inherits
a shield it did not earn. Quote, or write outside the block.

**Expect this attribute exactly once on the whole site** — the abstract on the Papers page
(D-016). **A second use is a signal to stop and ask, not a pattern to copy.** If a second
page needs to quote a source, that is a content decision for Nandan before it is a markup
decision, because the interesting question is never whether the markup validates.

---

## 9. Motion

Three things move on this site. Nothing else.

1. **Stratum bars fill once** on scroll-in, via `IntersectionObserver` (threshold `.3`),
   `1.15s cubic-bezier(.22,.9,.3,1)`, staggered 90ms. Disconnect after firing.
2. **Scroll progress** — a 2px brass tick rule pinned to the top (motif M4 doing real work).
3. **Hover** — colour only, 150ms.

Every one of these is disabled under `prefers-reduced-motion: reduce`; bars jump straight
to final width. No scroll-jacking, no parallax, no fade-up-on-scroll, no counters ticking
up. Restraint here is what separates instrument-grade from templated.

---

## 10. Accessibility, performance, assets

- Visible focus on everything interactive: 2px brass, 3px offset.
- Decorative SVG carries `aria-hidden="true"`; meaningful SVG carries `role="img"` + `<title>`.
- Semantic headings in order. One `h1` per page.
- State is never carried by colour alone — see M2's hatch rule.
- Touch targets ≥ 44px. **This and §8's button padding disagreed and both are right**
  — 11px/19px computes to a 42px box. Resolved in the build, not by moving either number:
  the drawn button is unchanged, and `@media (pointer: coarse)` lifts the block padding to
  12px, giving 44px exactly where a touch target is a touch target. The nav mark and the
  footer links take the same treatment. **A pointer query, never a width query:** a narrow
  window on a laptop is not a finger.

**All graphics are inline SVG built from the primitives.** No raster illustration, no
icon font, no chart library. Charts are hand-built from bars, ticks and brackets.

The working directory is **244 MB**, mostly photographs — an untracked `media/` of raw
field snapshots that has no business in a web repo. (The committed repository is 9.9 MB;
see D-010.) The new build ships images
only where a photograph is genuinely the right answer, and those are compressed and
sized. The motif system exists partly so that is rare.

---

## 11. Open decisions

**Moved.** Open decisions live in **`DECISIONS.md`**, which is the single source of
truth for what is settled and what is not. Do not record a decision here.

**The narrative is settled — D-027 — and the sitemap is derived from it in D-007.** Six
surfaces plus privacy. Where an entry below or in `DECISIONS.md` names a page from the old
seven-page structure, read it against D-007's table: *on Home* means **in the opening**, *on
Platform* means **the code-is-open-source section** (`/#code`, and it was "the audit trail" until 2026-08-26).

Blocking Phase 4: **D-014** (cleared client marks). D-013 settled to a recorded replay at
launch; D-020 settled the totals band to four cells — respondents · responses · countries ·
studies fielded; D-019 settled that there is **one** coverage surface and one maintenance
surface; D-023 removed every comparative claim against another recruitment source.

**Settled 2026-08-21: D-024** — Fly is named, the recruitment side is cited rather than
branded. **Its placement half was withdrawn on 2026-08-22 into D-007, which is open: the site
has no sitemap.** **Nothing in this document changed except §6**: M5 is now the visual identity of Fly, and
the Banned list gains the literal-rendering line. **§3, §5 and §7 are untouched** — no
token, no radius change, no thirteenth icon, and `check-contrast.py` still passes 22 pairs.
Fly's signature is the radius §5 already reserved for the thread.

---

## 12. Facts and figures

**Moved.** Every publishable number lives in **`CLAIMS.md`** with its source and
verification status. `DESIGN.md` tells you a figure must carry its provenance;
`CLAIMS.md` tells you what the figure is and whether you are allowed to use it.

**No number reaches a page without a `VERIFIED` row there.**

---

## 13. Reference

- Entry point for agents: **`AGENTS.md`**
- Decisions: **`DECISIONS.md`** · Facts: **`CLAIMS.md`** · Copy: **`CONTENT.md`**
- Scripts, and what a non-zero exit means: **`scripts/README.md`**
- Contrast check: `python3 scripts/check-contrast.py` — 22 pairs
- Claims check: `python3 scripts/check-claims.py <files>` (markup convention in §8, "Claim
  annotation"). **Name the files.** The bare command also walks `scripts/fixtures/`, which
  is nine pages built to fail, so it exits 1 by design
- Claims-check regression suite: `python3 scripts/test-check-claims.py` (fixtures in `scripts/fixtures/`)
- Coverage section: `python3 scripts/build-coverage-map.py` (data in `scripts/data/`) —
  emits the map, the region strip and the region totals in one run
- Icons, mark, favicon: `assets/icons/`, `assets/mark.svg`, `assets/favicon.svg`
- Fonts: `fonts/` + `css/fonts.css` (D-012). Never link a Google stylesheet from a page
- **The stylesheet: `css/site.css`** — this document in CSS, in section order. Built
  2026-08-25 from §3–§9 and **not** from `css/main.css`, which was the SPA's and is
  now deleted. Every hex literal in it sits inside a token declaration; there is no
  literal colour, font stack or radius anywhere else in the file or in any page
- The paper as structured data: `_data/paper.json` — read its `not_for_publication` note
  first; several fields are `WITHHELD` claims and exactly two of them render

**Mockups** (visual reference only — where they and this file disagree, this file wins):

- Brand direction: `https://claude.ai/code/artifact/d9f5bf84-1fd5-416e-ab9d-aa23f8d30fc9`
- Colour & motif: `https://claude.ai/code/artifact/8266b1aa-4bff-4b38-826b-3b0699485693`
- Homepage: `https://claude.ai/code/artifact/2bf3adec-378e-47cc-a269-2284123b1163`

**Phase 3.5 — the narrative pass** (2026-08-22). Read D-027 before these; they are the
working, and the entry is the answer.

- **Four narrative options**, with what each leaves out:
  `https://claude.ai/code/artifact/59d546c0-bcd8-4794-9076-233f25ef6352`
- **Two of them sketched beat by beat**:
  `https://claude.ai/code/artifact/c19dfa43-ad8c-4aa9-adeb-631aadddcc34`
- **The combined spine — settled as D-027**:
  `https://claude.ai/code/artifact/6c3aa80c-39ff-49cd-8d19-8607a0c28a52`

**Phase 3 deliverables** (2026-08-20, plus one from 2026-08-22):

- **The instrument material** — rendered in the design system, with the claim rows each
  section rests on. **Published 2026-08-22 as a page; it is not a page.** D-007 was reopened
  the same day and this artifact predates that, so read it as *content material shown in the
  system*, not as a settled surface: `https://claude.ai/code/artifact/ed32acb3-25f5-4596-a287-7dc9c7258149`
  *(Fonts embedded as data URIs from `fonts/` — D-012 holds; nothing loads from a Google
  origin. Generated by `scratchpad/gen.py`, which is not yet promoted to `scripts/`.)*

- **Copy deck** — the seven pages as of 2026-08-20, rendered in the design system.
  **Predates the Instrument page**, which D-024 added on 2026-08-21 and which no artifact
  yet renders:
  `https://claude.ai/code/artifact/573b66b3-33e9-4443-966d-0f48e239dace`
- **Coverage section** — the settled map, region strip and region totals:
  `https://claude.ai/code/artifact/ce3dbf66-d7e4-4616-82bf-31e3515ee5e8`
- **Coverage map, alternatives considered** — the record behind D-018:
  `https://claude.ai/code/artifact/b842265b-8a74-418e-b357-c5b74bfecb43`
- **Coverage, five earlier directions** — the record behind rejecting cartograms and
  ranked bars: `https://claude.ai/code/artifact/5d6c838e-cc7f-40c6-aeb4-09af81e0f3ff`

**Asset review** (2026-08-21) — *"Instrument Set"*, the built assets shown at size and in
all three theme states: the twelve icons, the mark, the favicons, the MAD figure, the type
kit, and the three coverage artefacts.

- `https://claude.ai/code/artifact/d55a5576-fb93-4eb4-8c10-fe0d03ed1392`

**Resolved 2026-08-21: the builder was promoted to `scripts/build-review.py`.** It reads
only committed files and writes one self-contained HTML, so it re-runs from a clean
checkout and the page can be regenerated whenever an asset changes — `build-coverage-map.py`
is the precedent. Its output path was repointed from the session scratchpad to `build/`.

**Republishing keeps the URL.** Publish the built file to the same artifact rather than
creating a second one; the link above is quoted in `AGENTS.md` and should not move.

**The page is a review aid, not a site page.** It uses the Google Fonts CDN because the
Artifact CSP permits no other font host, which §4 forbids for the site itself. Nothing in
`_site` should ever be built from it.

**Brand ancestry:** `../proposals/src/vlab_proposals/static/style.css` and
`static/fonts/`. The website inherits from the proposals, not the other way round.

---

*Phases 1–3 drafted, and Phase 3 reviewed — copy deck 2026-08-20, assets 2026-08-21.
Next: Nandan closing the Phase 3 gate in words, then Phase 4 build. D-014 is the only
decision blocking it.*
