// The client wall. COPY.md §1.5, DESIGN.md §8 "Client wall".
//
// Two separate things are needed before a mark renders, and conflating them is the
// mistake this file exists to prevent:
//
//   1. `logo`    — the vector file, from the institution's own brand portal.
//   2. `cleared` — D-014, written permission from its owner. A VERIFIED CLAIMS.md
//                  row licenses the *relationship*; it never licenses the *logo*.
//
// A mark renders only when BOTH are true. Anything else renders as the institution's
// name in type in the same cell. That is the shipping mechanism, not a fallback
// (COPY.md §1.5) — the page ships with any mix, and marks drop in as they clear.
//
// Every file in assets/logos/ was downloaded, not cleared. D-014 quotes what each
// source actually says; the World Bank, Harvard and WashU explicitly bar implying
// affiliation, which is what a wall on a commercial site does. So `cleared` is false
// on all six, and flipping one to true without D-014 closing is the failure mode.
//
// Heading is "Used by researchers from" — one frame for all six, including the
// commissioned work. It is the weaker claim and it is true of every row.

export default [
  { name: "The World Bank",                     claim: "C-020", logo: "/assets/logos/world-bank-group-official.svg", cleared: false },
  { name: "Columbia University",                claim: "C-024", logo: "/assets/logos/columbia.svg",                  cleared: false },
  { name: "George Washington University",       claim: "C-025", logo: "/assets/logos/gwu.svg",                       cleared: false },
  { name: "Harvard University",                 claim: "C-094", logo: "/assets/logos/harvard-stacked-official.svg",  cleared: false },
  { name: "University of Washington",           claim: "C-095", logo: "/assets/logos/uw.svg",                        cleared: false },
  { name: "Washington University in St. Louis", claim: "C-096", logo: "/assets/logos/washu.svg",                     cleared: false },
];
