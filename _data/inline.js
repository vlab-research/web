// Files that must be inlined into the document rather than linked.
//
// sprite — DESIGN.md §7: `<use href="external.svg#id">` does not resolve
//   cross-document in Chrome or Safari, so assets/icons/icons.svg is dropped
//   straight after <body>. It is written to be inlined as-is (width=0, height=0,
//   display:none, aria-hidden) and carries no <title>; decorative use carries
//   aria-hidden="true" at the call site.
//
// mark — the nav mark, inlined so it takes currentColor and holds in all three
//   theme states. A linked <img> would not.
//
// figures — assets/figures/*.svg are complete figures: they carry their own
//   <title>/<desc>, their own scoped <style> resolved from §3 tokens, their own
//   data-claim-unit and their own mandatory source lines. Inline them whole; do not
//   unpick them, and never restate a value they already state.

import fs from "node:fs";
import path from "node:path";

const ROOT = path.join(import.meta.dirname, "..");
const read = (p) => fs.readFileSync(path.join(ROOT, p), "utf8").trim();

export default {
  sprite: read("assets/icons/icons.svg"),
  mark: read("assets/mark.svg"),
  figures: {
    throughput: read("assets/figures/throughput-box.svg"),
    adcost: read("assets/figures/ad-cost.svg"),
    // M5, the thread. Hand-authored rather than generated: it draws no data, so there
    // is nothing for a generator to read. Its numerals are list indices and carry
    // data-claim="none".
    reallocations: read("assets/figures/reallocations-box.svg"),
    thread: read("assets/figures/thread.svg"),
  },
};
