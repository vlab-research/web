// Eleventy configuration. DECISIONS.md D-006: HTML-first, layouts and _data and
// nothing beyond them. No component framework, no asset pipeline, no client-side
// router, and Eleventy ships none of its own JavaScript to the browser.
//
// Input is the repository root, so `_includes/base.html` and `_data/` sit where
// D-006 says they sit. Eleventy honours .gitignore, which already excludes
// node_modules/, _site/, media/ and build/; .eleventyignore adds the documentation
// set and the fixture pages that are built to fail.

export default function (eleventyConfig) {
  // Static. Everything here is committed and served as-is.
  //   fonts/ + css/fonts.css are the self-hosted kit (D-012) — nothing may load
  //   from a Google origin at runtime.
  eleventyConfig.addPassthroughCopy("css");
  eleventyConfig.addPassthroughCopy("fonts");
  eleventyConfig.addPassthroughCopy("assets");
  eleventyConfig.addPassthroughCopy("robots.txt");
  eleventyConfig.addPassthroughCopy("_redirects");

  // Rebuild when a generator's data or output changes, so `--serve` picks up a
  // re-run of build-coverage-map.py without a restart.
  eleventyConfig.addWatchTarget("./build/");
  eleventyConfig.addWatchTarget("./scripts/data/");

  return {
    dir: {
      input: ".",
      output: "_site",
      includes: "_includes",
      data: "_data",
    },
    // Pages are .html with front matter and a layout: line (D-006). Nunjucks is
    // the engine for both the page body and the layout chain.
    //
    // "njk" is here for exactly one file — sitemap.njk, which emits /sitemap.xml.
    // It is not a page and carries no layout, so giving it a .html extension would
    // be worse: it would read as a page to everyone who opened the directory.
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
    templateFormats: ["html", "njk"],
  };
}
