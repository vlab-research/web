// The coverage section's three artefacts, read from build/.
//
// DESIGN.md §8 "Coverage section": all three are always built together by
// scripts/build-coverage-map.py from scripts/data/coverage.json, and the output is
// never hand-edited. This file reads that output; it does not transform it beyond
// stripping the generator's "Required CSS" comment block, which is guidance for
// whoever writes the stylesheet and has no business in a served page. The two
// provenance comment lines are kept.
//
// build/ is generated and untracked, so `npm run build` regenerates it before
// Eleventy runs. A missing file is a hard error rather than a silent empty section:
// a coverage section that quietly renders nothing is worse than a failed build.

import fs from "node:fs";
import path from "node:path";

const BUILD = path.join(import.meta.dirname, "..", "build");

function fragment(name) {
  const file = path.join(BUILD, name);
  if (!fs.existsSync(file)) {
    throw new Error(
      `build/${name} is missing. Run: python3 scripts/build-coverage-map.py\n` +
        `(build/ is generated and untracked — see scripts/README.md.)`
    );
  }
  // Drop the multi-line "Required CSS (tokens from DESIGN.md §3): … -->" comment.
  return fs
    .readFileSync(file, "utf8")
    .replace(/<!--\s*Required CSS[\s\S]*?-->\s*/g, "")
    .trim();
}

export default {
  map: fragment("coverage-map.html"),
  strip: fragment("coverage-strip.html"),
  regions: fragment("coverage-regions.html"),
};
