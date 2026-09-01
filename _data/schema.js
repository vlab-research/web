// JSON-LD, emitted once in the <head> by _includes/base.html.
//
// WHY THIS FILE EXISTS AT ALL, AND THE RULE IT IS BUILT UNDER
//
// `check-claims.py` skips <script>: SKIP_TEXT = {"script", "style", "template",
// "svg"}. So a number inside a JSON-LD block is never scanned, never needs a
// `data-claim`, and would sail straight past the one mechanism this repo built to
// stop invented figures. Structured data is a page the crawler reads, and it has no
// checker.
//
// The response is not "be careful with the numbers". It is:
//
//   ** NO FIGURE APPEARS IN STRUCTURED DATA. **
//
// Not the respondent total, not the study count, not the country count, not a
// per-country count. There is no schema.org field that needs one, so carrying one
// would be decoration with the provenance rule switched off. If a future change
// wants a figure in here, that is the moment to make `check-claims.py` read
// ld+json — not the moment to type a number.
//
// What IS generated: the country NAMES in `areaServed`, from
// build/coverage-countries.json, which scripts/build-coverage-map.py writes in the
// same run that draws the map. Names are identifiers, not claims, and generating
// them means the structured data and the map cannot disagree about where we work.
//
// WHAT THIS IS FOR. vlab.digital is a small domain and cannot out-page anyone; the
// realistic lever is telling Google what KIND of thing it is. Two nodes do that: an
// Organization that knows about survey methodology and operates in 41 countries, and
// the paper it published. `notes/ws-seo.md` §4 is the reasoning.

import fs from "node:fs";
import path from "node:path";

import site from "./site.js";

const BUILD = path.join(import.meta.dirname, "..", "build");

// Read rather than `import ... with { type: "json" }`. The import-attributes syntax
// needs Node >= 20.10 and still warns as experimental on the 20.x line that
// netlify.toml pins; fs is what _data/coverage.js already does, and it cannot break
// on a runtime bump.
const paper = JSON.parse(
  fs.readFileSync(path.join(import.meta.dirname, "paper.json"), "utf8")
);

// Same contract as _data/coverage.js: build/ is generated and untracked, and a
// missing file is a hard error rather than a silently thinner page.
function countries() {
  const file = path.join(BUILD, "coverage-countries.json");
  if (!fs.existsSync(file)) {
    throw new Error(
      `build/coverage-countries.json is missing. Run: python3 scripts/build-coverage-map.py\n` +
        `(build/ is generated and untracked — see scripts/README.md.)`
    );
  }
  return JSON.parse(fs.readFileSync(file, "utf8")).countries;
}

// Ours, not the paper's — and the difference is the point. `paper.abstract.keywords`
// reads: Ad Platforms · APIs · **Consumer Insights** · Online Sampling · Survey
// Research. Those are the authors' keywords for a journal, and they are not wrong
// there. But "Consumer Insights" is the exact audience the site is trying not to
// attract (ws-seo.md §5), and emitting it here would be us telling Google we are
// relevant to it. Structured data is our own voice, not a quotation, so the paper's
// keyword line is not reproduced anywhere below.
const KNOWS_ABOUT = [
  "Survey methodology",
  "Survey sampling",
  "Stratified sampling",
  "Population-representative sampling",
  "Survey research",
  "Respondent recruitment",
  "Online data collection",
  "Impact evaluation",
  "Public health research",
];

const ORG = `${site.url}/#organization`;
const ARTICLE = `${site.url}/#paper`;

const organization = {
  "@type": "Organization",
  // Organization, deliberately — not ProfessionalService, not LocalBusiness, not
  // any of the marketing-adjacent types. The type vocabulary is itself a signal
  // about which cluster this domain belongs to, and it is one of the few negative
  // targeting levers that actually exists (ws-seo.md §5).
  "@id": ORG,
  name: site.name,
  legalName: site.legal,
  url: site.url,
  email: site.email,
  description: site.description,
  logo: `${site.url}/assets/mark.svg`,
  sameAs: [site.github],
  address: {
    "@type": "PostalAddress",
    addressLocality: "Corvallis",
    addressRegion: "Oregon",
    addressCountry: "US",
  },
  knowsAbout: KNOWS_ABOUT,
  // All 41: the 37 with a count and the 4 with verified coverage and no computed
  // count. `areaServed` is a statement about where we operate, not about respondent
  // counts, so the pending four belong here exactly as much as the rest — and no
  // count is carried either way, so the "never render as zero" rule has nothing to
  // trip over.
  areaServed: countries().map((c) => ({
    "@type": "Country",
    name: c.name,
    identifier: c.code,
  })),
  subjectOf: { "@id": ARTICLE },
};

const article = {
  "@type": "ScholarlyArticle",
  "@id": ARTICLE,
  name: paper.title.value,
  author: paper.authors.map((a) => ({
    "@type": "Person",
    name: a.name,
    affiliation: { "@type": "Organization", name: a.affiliation },
  })),
  // 2025, the year the document prints on its own title page in every edition —
  // ws-paper.md, "Citation year". The filename of one edition says 2026; citing that
  // would cite a year the paper does not carry.
  datePublished: "2025",
  url: site.paper.url,
  identifier: site.paper.url,
  mainEntityOfPage: `${site.url}/`,
  publisher: { "@id": ORG },

  // NO `abstract`, and this is a decision rather than an omission. D-016 permits the
  // abstract on the page only as a verbatim quotation inside data-claim-quote="C-055"
  // with its visible attribution — that block is the whole of the permission. It also
  // names Prolific and digital twins, and D-023 is explicit that the quotation is
  // admitted only in its block: "never pulled out of the block, never restated in a
  // heading, never summarised beneath it." Lifting it into a JSON-LD field is pulling
  // it out of the block. A reader who wants the abstract has it at SSRN.
  //
  // The block itself came off the page 2026-08-31, held "for now" (D-016), which makes
  // this field the only place an abstract could reappear by accident. It must not.
  //
  // NO `keywords`, for the reason recorded at KNOWS_ABOUT above.
};

export default {
  "@context": "https://schema.org",
  "@graph": [organization, article],
};
