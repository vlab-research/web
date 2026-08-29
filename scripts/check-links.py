#!/usr/bin/env python3
"""Every internal link, image and anchor in the built site resolves.

    python3 scripts/check-links.py

This exists because of what the docs migration gave up. Under Hugo, internal links
were written `{{< ref "fly/reference/bails.md" >}}` and the build FAILED if the
target did not exist. Folding the docs into Eleventy (D-008) resolved all 116 of
those to plain URLs once, which is the right end state -- the content no longer
carries a templating idiom, and it renders as Markdown anywhere -- but it hands
back the guarantee. A moved page would now break its inbound links silently.

So the guarantee moves here, and it covers more than `ref` ever did:

  * internal hrefs resolve to a page the build actually wrote
  * <img src> resolves to a file the build actually copied
  * a #fragment resolves to an id ON THE PAGE IT POINTS AT, which `ref` could not
    check at all -- it validated the path and took the anchor on trust

That third check is not hypothetical. The docs carry cross-page anchors like
`.../hidden/#interpolation-transforms`, and heading ids are generated from heading
TEXT: rewording a heading silently breaks every link into it.

Known finding on the first run: nine images referenced by the Hugo docs were never
committed -- six `bails-*` captures (BAILS_DOC_SCREENSHOTS.md in the old repo is
the capture plan for them) and three `fly-monitor-*`. They were broken on the live
docs site too. They are reported, not excused.

Exit 1 on any finding. External links are NOT fetched: a checker that makes network
calls is a checker that fails for reasons that have nothing to do with this repo.
"""
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urldefrag

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(REPO, "_site")


class Page(HTMLParser):
    """Collects link targets and the ids a page offers."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []   # (kind, value)
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        # <a name> is still an anchor target in every browser.
        if tag == "a" and a.get("name"):
            self.ids.add(a["name"])
        if tag == "a" and a.get("href"):
            self.links.append(("href", a["href"]))
        elif tag == "img" and a.get("src"):
            self.links.append(("src", a["src"]))


def load():
    pages = {}
    for root, _, files in os.walk(SITE):
        for f in files:
            if not f.endswith(".html"):
                continue
            full = os.path.join(root, f)
            p = Page()
            with open(full, encoding="utf-8") as fh:
                p.feed(fh.read())
            # _site/docs/fly/index.html -> /docs/fly/
            rel = os.path.relpath(full, SITE).replace(os.sep, "/")
            url = "/" + rel[: -len("index.html")] if rel.endswith("index.html") else "/" + rel
            pages[url] = p
    return pages


def main():
    if not os.path.isdir(SITE):
        print("_site/ does not exist -- run the build first", file=sys.stderr)
        return 2

    pages = load()
    findings = []

    for url, page in sorted(pages.items()):
        for kind, raw in page.links:
            # Anything with a scheme, or a protocol-relative URL, is somebody
            # else's to keep working.
            if re.match(r"^(?:[a-z][a-z0-9+.-]*:|//)", raw, re.I):
                continue
            target, frag = urldefrag(raw)
            target, frag = unquote(target), unquote(frag)

            if target in ("", "."):
                # A bare #fragment: same page.
                dest_url, dest = url, page
            else:
                if not target.startswith("/"):
                    base = url if url.endswith("/") else url.rsplit("/", 1)[0] + "/"
                    target = os.path.normpath(base + target)
                    if raw.endswith("/") and not target.endswith("/"):
                        target += "/"
                dest_url = target

                if dest_url in pages:
                    dest = pages[dest_url]
                else:
                    # Not a page. It may still be a copied file -- an image, the
                    # search index, a stylesheet.
                    on_disk = os.path.join(SITE, dest_url.lstrip("/").replace("/", os.sep))
                    if os.path.isfile(on_disk):
                        continue
                    findings.append((url, kind, raw, "no such page or file"))
                    continue

            if frag and frag not in dest.ids:
                findings.append((url, kind, raw, f"no id \"{frag}\" on {dest_url}"))

    if findings:
        for src, kind, raw, why in findings:
            print(f"  fail  {src}\n          {kind}={raw!r}  -- {why}")
        print(f"\n{len(findings)} broken reference(s) across {len(pages)} pages.")
        return 1

    print(f"All internal links, images and anchors resolve. ({len(pages)} pages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
