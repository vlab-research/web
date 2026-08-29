// Directory data for docs/. Applies to every page under it (D-008).
//
// This is .js and not .json because two of the values below have to be COMPUTED,
// and a computed value written as a JSON string template is escaped by Nunjucks on
// the way out and escaped AGAIN by base.html on the way in — an apostrophe reaches
// the page as `&amp;#39;`. A real function returns a real string exactly once.
//
// (Unrelated to the `_data/*.js must export a function` note in AGENTS.md: that is
// about GLOBAL data files. A directory data file exports the object itself.)

// A page's own description, taken from its opening prose — better than one shared
// string across 47 pages. Read from the Markdown as written rather than from the
// rendered output, which would be circular: the description is needed in <head>,
// and <head> renders before the body it would have to read.
function firstProse(raw) {
  const body = String(raw || "").replace(/^---[\s\S]*?\n---\n/, "");
  for (const block of body.split(/\n\s*\n/)) {
    const t = block.trim();
    // The first PARAGRAPH, not the first line: skip headings, lists, tables, code
    // fences and callout fences.
    if (!t || /^(#|[-*+>|]|\d+\.|:::|```)/.test(t)) continue;
    const flat = t
      .replace(/!?\[([^\]]*)\]\([^)]*\)/g, "$1")   // links and images to their text
      .replace(/[*_`]/g, "")
      .replace(/\s+/g, " ")
      .trim();
    if (flat.length < 40) continue;
    return flat.length > 155
      ? flat.slice(0, 152).replace(/\s+\S*$/, "") + "…"
      : flat;
  }
  return "";
}

export default {
  layout: "docs.html",
  docsSection: true,

  // Docs Markdown is rendered as Markdown and NOTHING else. The repo default is
  // markdownTemplateEngine: "njk", and pointing Nunjucks at this content breaks the
  // build outright: Fly's message interpolation is written {{hidden:name}}, and
  // documenting that syntax is a large part of what these pages are FOR. Nunjucks
  // reads it as a variable and fails to parse.
  //
  // Turning it off is the right answer rather than a workaround. Docs are prose;
  // nothing in them should be computed, and a page that documents a templating
  // syntax must be able to print that syntax literally. Anything dynamic belongs in
  // the layout, which is still Nunjucks.
  templateEngineOverride: "md",

  eleventyComputed: {
    // `title` is left ALONE — it is the short name, and the <h1>, the sidebar and
    // the breadcrumbs all want it. The SEO form is a separate key that only <head>
    // reads.
    //
    // Computing `title` FROM `title` is what the first attempt did, and it does not
    // work: eleventyComputed resolves in dependency order, so the <h1> read the
    // value the computation had already replaced and rendered
    // "Bails — Virtual Lab Documentation" as the page heading.
    headTitle: (data) =>
      data.page.url === "/docs/"
        ? "Virtual Lab Documentation"
        : data.title + " — Virtual Lab Documentation",

    // A page may override by setting `description:` in its own front matter.
    description: (data) => data.description || firstProse(data.page.rawInput),
  },
};
