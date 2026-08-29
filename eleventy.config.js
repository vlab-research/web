// Eleventy configuration. DECISIONS.md D-006: HTML-first, layouts and _data and
// nothing beyond them. No component framework, no asset pipeline, no client-side
// router, and Eleventy ships none of its own JavaScript to the browser.
//
// Input is the repository root, so `_includes/base.html` and `_data/` sit where
// D-006 says they sit. Eleventy honours .gitignore, which already excludes
// node_modules/, _site/, media/ and build/; .eleventyignore adds the documentation
// set and the fixture pages that are built to fail.

import markdownIt from "markdown-it";
import markdownItAnchor from "markdown-it-anchor";
import markdownItContainer from "markdown-it-container";
import syntaxHighlight from "@11ty/eleventy-plugin-syntaxhighlight";

// The docs live in docs/ as Markdown and render through _includes/docs.html.
// D-008. Everything below that is docs-specific is grouped under the DOCS
// headings, so the marketing site's configuration stays readable on its own.

// Section order in the sidebar is `weight` ascending, then title. A page with no
// weight sorts as 0, which is Hugo's rule and the one 40 of the 47 pages were
// written against.
const byWeight = (a, b) => {
  const wa = a.data.weight ?? 0, wb = b.data.weight ?? 0;
  if (wa !== wb) return wa - wb;
  return (a.data.title || "").localeCompare(b.data.title || "");
};

export default function (eleventyConfig) {
  // Static. Everything here is committed and served as-is.
  //   fonts/ + css/fonts.css are the self-hosted kit (D-012) — nothing may load
  //   from a Google origin at runtime.
  eleventyConfig.addPassthroughCopy("css");
  eleventyConfig.addPassthroughCopy("fonts");
  // assets/ is copied SUBDIRECTORY BY SUBDIRECTORY, deliberately, so that
  // assets/logos/ is NOT published. Not one of those eight institutional marks is
  // cleared (D-014): every institution requires permission for third-party use, and
  // the World Bank, Harvard and WashU explicitly bar use that implies affiliation.
  // Copying assets/ wholesale would host eight third-party trademarks on our own
  // domain, publicly fetchable, with no permission for any of them — and nothing on
  // the site references them, because the client wall renders as type until a mark
  // is both supplied AND cleared.
  //
  // When a mark clears, add its file here as well as flipping `cleared` in
  // _data/clients.js. Two separate things, exactly as that file says.
  eleventyConfig.addPassthroughCopy("assets/figures");
  eleventyConfig.addPassthroughCopy("assets/icons");
  eleventyConfig.addPassthroughCopy("assets/favicon.svg");
  eleventyConfig.addPassthroughCopy("assets/favicon.ico");
  eleventyConfig.addPassthroughCopy("assets/apple-touch-icon.png");
  eleventyConfig.addPassthroughCopy("assets/mark.svg");
  // The share card. og.png only — assets/og.svg is the generated source and nothing
  // fetches it, so it stays unpublished on the same principle as the rest of this list.
  eleventyConfig.addPassthroughCopy("assets/og.png");
  // DOCS · the screenshots. DESIGN.md hard rule 8 bans raster illustration on the
  // marketing site; docs are carved out of it (D-029) because a capture of the Fly
  // UI *is* the documentation. The ban still holds everywhere else.
  eleventyConfig.addPassthroughCopy("docs/images");
  eleventyConfig.addPassthroughCopy("docs/docs.js");

  eleventyConfig.addPassthroughCopy("robots.txt");
  eleventyConfig.addPassthroughCopy("_redirects");

  // Rebuild when a generator's data or output changes, so `--serve` picks up a
  // re-run of build-coverage-map.py without a restart.
  eleventyConfig.addWatchTarget("./build/");
  eleventyConfig.addWatchTarget("./scripts/data/");

  // ==========================================================================
  // DOCS · Markdown
  // ==========================================================================
  //
  // Eleventy's default markdown-it instance is replaced so that headings get ids
  // (the on-page contents rail and every #anchor in the migrated content need
  // them) and so `::: note` / `::: warning` render as callouts.
  //
  // `html: true` is required: the migrated content carries none today, but Hugo
  // had `unsafe = true` set and turning it off silently swallows any HTML a future
  // page adds rather than failing.
  const md = markdownIt({ html: true, linkify: false, typographer: false })
    .use(markdownItAnchor, {
      permalink: markdownItAnchor.permalink.headerLink({ safariReaderFix: true }),
      slugify: (s) =>
        encodeURIComponent(
          String(s).trim().toLowerCase()
            .replace(/[^\w\s-]/g, "").replace(/\s+/g, "-")
        ),
      level: [2, 3, 4],
    });

  // The two callout types the Hugo docs used, and only those two. A third would
  // need a DESIGN.md entry first, not a line here — see D-029 on why neither of
  // these introduces a colour.
  for (const type of ["note", "warning"]) {
    md.use(markdownItContainer, type, {
      render: (tokens, idx) =>
        tokens[idx].nesting === 1
          ? `<div class="callout ${type}" role="note">` +
            `<p class="callout-label">${type === "note" ? "Note" : "Warning"}</p>\n`
          : "</div>\n",
    });
  }
  // DESIGN.md §5: wide content scrolls inside its own container, and the body
  // never scrolls sideways. Markdown emits a bare <table>, so the container has
  // to be added here — 18 of the 47 pages have one, several of them wide.
  md.renderer.rules.table_open = () => '<div class="table-wrap">\n<table>\n';
  md.renderer.rules.table_close = () => "</table>\n</div>\n";

  eleventyConfig.setLibrary("md", md);

  // Prism, at build time. It ships no JavaScript to the browser; the theme is
  // ours, in css/docs.css, built from the DESIGN.md tokens.
  eleventyConfig.addPlugin(syntaxHighlight);

  // ==========================================================================
  // DOCS · Collections
  // ==========================================================================
  eleventyConfig.addCollection("docs", (c) =>
    c.getFilteredByGlob("docs/**/*.md").sort(byWeight)
  );

  // The sidebar tree. Built from URLs rather than from file paths so that a page
  // and its section index are the same node: /docs/fly/ is fly/index.md, and
  // /docs/fly/reference/ is its child.
  eleventyConfig.addCollection("docsTree", (c) => {
    const pages = c.getFilteredByGlob("docs/**/*.md").sort(byWeight);
    const nodes = new Map();
    for (const p of pages) {
      nodes.set(p.url, {
        url: p.url,
        title: p.data.title,
        weight: p.data.weight ?? 0,
        children: [],
      });
    }
    // /docs/ is the root NODE, not a sidebar entry: the landing page is reached by
    // the brand mark, and listing it as a peer of Fly and Virtual Lab would put the
    // page you are already on inside its own navigation.
    const orphans = [];
    for (const [url, node] of nodes) {
      if (url === "/docs/") continue;
      // Parent of /docs/fly/reference/bails/ is /docs/fly/reference/.
      const parent = url.replace(/[^/]+\/$/, "");
      const p = nodes.get(parent);
      (p ? p.children : orphans).push(node);
    }
    // A page whose parent section has no index.md would vanish from the sidebar
    // entirely. Every section has one today; if one is ever added without, this
    // fails the build rather than silently hiding the page.
    if (orphans.length) {
      throw new Error(
        "docsTree: no parent section for " +
          orphans.map((o) => o.url).join(", ") +
          " — add an index.md to the section directory"
      );
    }
    const sort = (list) => {
      list.sort((a, b) => a.weight - b.weight || a.title.localeCompare(b.title));
      list.forEach((n) => sort(n.children));
    };
    const roots = nodes.get("/docs/").children;
    sort(roots);
    return roots;
  });

  // ==========================================================================
  // DOCS · Filters
  // ==========================================================================
  //
  // The "On this page" rail, read back out of the rendered HTML. Deriving it from
  // the output rather than from the Markdown means it can never disagree with the
  // ids markdown-it-anchor actually emitted, which is the bug every hand-rolled
  // table of contents eventually has.
  eleventyConfig.addFilter("headings", (html) => {
    const out = [];
    const re = /<h([23])[^>]*\sid="([^"]+)"[^>]*>(.*?)<\/h\1>/gis;
    const s = String(html || "");
    let m;
    while ((m = re.exec(s))) {
      out.push({
        level: Number(m[1]),
        id: m[2],
        text: m[3].replace(/<[^>]+>/g, "").trim(),
      });
    }
    return out;
  });

  // Plain text of a rendered page, for the search index. Code blocks are kept —
  // half of what anyone searches this site for is a field name that only ever
  // appears inside one — but the anchor links markdown-it-anchor injects into
  // every heading are dropped, or every heading would be indexed twice.
  eleventyConfig.addFilter("searchText", (html) =>
    String(html || "")
      .replace(/<a class="header-anchor"[^>]*>|<\/a>/g, " ")
      .replace(/<[^>]+>/g, " ")
      .replace(/&(?:amp|lt|gt|quot|#39|nbsp);/g, " ")
      .replace(/\s+/g, " ")
      .trim()
  );

  // Breadcrumbs, from the URL and the docs collection's titles.
  eleventyConfig.addFilter("crumbs", (url, docs) => {
    const parts = String(url).split("/").filter(Boolean); // ["docs","fly","reference"]
    const out = [];
    let acc = "";
    for (const part of parts) {
      acc += "/" + part;
      const page = docs.find((p) => p.url === acc + "/");
      if (page) out.push({ url: acc + "/", title: page.data.title });
    }
    return out;
  });

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
    // "md" is here for docs/ only. Every other Markdown file in the repo is the
    // documentation set, not a page, and .eleventyignore keeps it that way.
    templateFormats: ["html", "njk", "md"],
  };
}
