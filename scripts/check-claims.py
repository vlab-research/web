#!/usr/bin/env python3
"""Verify every number on a page traces to a VERIFIED row in CLAIMS.md, and carries
its source in the same visual unit.

Run before publishing any page that states a figure:

    python3 scripts/check-claims.py                 # every .html in the repo
    python3 scripts/check-claims.py _site/index.html

This is the check that enforces the brand. DESIGN.md §2 states the provenance rule —
a number rests on somebody else's document, and that citation appears in the same visual
unit — and CLAIMS.md states the factual one: no number reaches a page without a VERIFIED
row. Both were prose until this script existed.

**The provenance half does not apply to our own operating record** (2026-08-26). A line
reading "Virtual Lab production database" under a Virtual Lab figure cites nothing a
reader can check; it restates who is speaking, and printing it beside a real citation
devalues the real one. The split is read from the register, never from the markup —
a table whose fourth column is "Definition" says how we computed a number from our own
data, and one whose fourth column is "Source" says where somebody else published it.
Only the first is exempt, so the rule fails safe. See "THE CITATION RULE" below, and the
pair of fixtures that assert both halves: pass-own-record.html and fail-provenance.html. check-contrast.py exists because a colour bug shipped
once; this exists so a figure bug never does, because a plausible number with no source
discredits every number beside it.

Failure kinds, in order of severity:

  register    CLAIMS.md itself is malformed — an unrecognised status value. Fatal, and
              checked first: a typo in the status column must not silently widen what
              the site is allowed to say.
  banned      a value from a WITHHELD, PLACEHOLDER, or STALE row reached a page.
              Always fatal. There is no allowlist escape from this one.
  phrase      public copy names an internal platform, schema or migration, against
              CLAIMS.md "Publication rules for scale figures", rule 2. Not a numeric
              check, but it travels with the numbers it qualifies.
  provenance  an element carrying a THIRD-PARTY claim has no visible citation in its
              unit. First-party claims are exempt — see above.
  unsourced   a numeral in body text matches no VERIFIED value.

HOW A PAGE DECLARES ITS PROVENANCE
----------------------------------
The check is exact when the markup says what it is claiming, and heuristic when it does
not. Annotate the value-bearing element:

    <div class="cell" data-claim-unit>
      <div class="num" data-claim="C-003">6.1<span class="unit">p.p.</span></div>
      <div class="label">MEAN ABS. DEVIATION</div>
      <div class="src" data-claim-source>vs. GSS, CPS, Pew</div>
    </div>

    data-claim="C-003"        this element's numerals are the value of C-003. Space-
                              separate several ids. The value is checked against the
                              register, and a source line is required in the same unit.
    data-claim="none"         this numeral is deliberately not a claim (a list counter,
                              a street number, a count of things visible on the page).
    data-claim-source         this element is the visible source line.
    data-claim-unit           this element is the visual unit — the card or cell a
                              value and its source line must share, and the widest
                              element a value may draw a source line from. Without it
                              the unit is the nearest figure/li/td/section or
                              .cell/.card ancestor, and only that one counts.
    data-claim-scan="off"     stop scanning numerals inside this element. For legal
                              copy — the privacy policy states retention periods and
                              GDPR article numbers, which are not claims about our work.
                              Banned values are still checked inside it.
    data-claim-quote="C-055"  the words inside are somebody else's, reproduced verbatim
                              and attributed to that VERIFIED row. Their numerals are
                              that author's figures, not our claims. Requires a visible
                              attribution line; every withheld value it shields is
                              reported at warn level. See QUOTE_ATTR below for why the
                              shield is this narrow, and DESIGN.md §8.

A file with no data-claim attributes is scanned in heuristic mode instead: every numeral
in body text is matched against the register, with the allowlist below carrying the
ordinary non-claim numbers. Heuristic mode is deliberately noisier and deliberately
weaker (a bare "19" on a page matches C-011's 19 days by coincidence, and passes). It is
there so an un-annotated page still gets checked, not as the target state.
"""
import argparse
import os
import re
import sys
from html.parser import HTMLParser

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def short(path):
    full = os.path.abspath(path)
    return os.path.relpath(full, REPO) if full.startswith(REPO + os.sep) else path

# --- configuration -----------------------------------------------------------------
# Everything a reviewer might want to argue with lives here, not in the logic below.

# The status vocabulary. Anything else in the Status column is a register failure, not
# a publishable row — a typo must not silently widen what the site may say.
#   VERIFIED     traced to a named source, safe to publish
#   STALE        was verified, the source has moved, re-check before use
#   PLACEHOLDER  needed, not yet obtained
#   WITHHELD     traceable or not, a decision has been taken that it does not ship
STATUSES = {"VERIFIED", "STALE", "PLACEHOLDER", "WITHHELD"}
PUBLISHABLE_STATUS = {"VERIFIED"}

# Belt and braces on top of the status column. A row whose prose says it must not be
# published is held back even if its status says VERIFIED — the publication rules in
# CLAIMS.md are not all expressible as a status. C-015 ("NOT FOR PUBLICATION") is held
# back by these; C-042 ("current site copy, from the working paper") is not.
DO_NOT_PUBLISH = [
    r"not for publication",
    r"do not publish",
    r"must not be published",
    r"never publish",
    r"see the definition note",
]

# Attributed quotation. data-claim-quote="C-nnn" on a container says: the words inside
# are somebody else's, reproduced accurately, and the numerals in them are that author's
# figures rather than our claims. It exists for exactly one thing — the paper's abstract
# on the Papers page, which states $0.30 per question while C-004 withholds it.
#
# The distinction it encodes is real: C-004 governs what Virtual Lab asserts. Quoting a
# source correctly is the opposite of overclaiming, and a citation page that silently
# edited its own paper's abstract would be the worse failure. But a blanket exemption is
# how a rule stops being enforceable, so the shield is deliberately narrow:
#
#   * the container must name a VERIFIED CLAIMS.md row for the document being quoted,
#     so a quotation cannot be attributed to nothing;
#   * it must carry a visible attribution line, checked the same way a figure's source
#     line is checked;
#   * every withheld value it shields is REPORTED, every run, at warn level. The shield
#     stops a build failing; it never stops a human seeing.
#
# It does not travel. Paraphrase inside a quote block is not quotation, and this script
# cannot tell the difference — which is why the block must be small enough to read.
QUOTE_ATTR = "data-claim-quote"

# Not the same thing. These caveat the *scope* of a claim without forbidding it, and a
# row carrying one stays publishable. C-054 is the case that forced the distinction:
# "Do not generalise" means the IRB covers the validation study and not all work — but
# the register says in the same breath that the number is "declared in the paper and
# therefore safe to state". Treating that as a ban held the whole row back, which made
# the citation year 2025 a banned value site-wide, on a register that mandates
# "Donati & Rao, 2025" in every source line. A scope caveat is reported, never enforced;
# scope is a thing a human reads, not a thing this script can check.
SCOPE_CAVEATS = [
    r"do not generali[sz]e",
    r"applies to the validation study",
    r"do not attribute",
]

# CLAIMS.md, "Publication rules for scale figures", rule 2: never mention platforms,
# schemas or migrations in public copy. The split between the two databases is an
# implementation detail of ours, not a fact about the work — and 175 studies is exactly
# the kind of figure whose definition tempts an author into explaining the split. Public
# copy says respondents, responses, countries, studies, and nothing else.
#
# Deliberately narrow. "Kubernetes", "Helm", "open source" and "the platform is open
# source" are all sanctioned public copy (CONTENT.md, Platform page), so the denylist
# names internal identifiers and the split itself, never the word "platform" alone.
# "Migration" is only caught when qualified — a survey about migration is legitimate.
DENY_PHRASES = [
    ("internal db",     r"\bchatroach\b|\bcockroach(?:db)?\b|\bvprod\b|\bkubectl\b"),
    ("schema-qualified", r"\bvlab\.(?!digital\b)\w+"),
    ("internal table",  r"\b(?:study_confs|campaign_confs|adopt_reports|inference_data|"
                        r"study_id|userid|user_id|shortcodes?)\b"),
    ("the split",       r"\bboth (?:platforms|schemas)\b|\b(?:older|legacy|current)[- ]platform\b|"
                        r"\bold(?:er)? platform\b"),
    ("schema",          r"\bschemas?\b"),
    ("migration",       r"\b(?:data|platform|database|schema)\s+migrations?\b|"
                        r"\bmigrated\s+(?:from|to|off)\b"),
]

# Numerals inside a span matched by one of these are not claims and are not checked
# against the register. Matched against the rendered text; a numeral is allowed when it
# falls inside the span of one of these matches. Banned values ignore this list.
ALLOW = [
    ("year",        r"\b(?:19|20)\d{2}\b"),
    ("iso-date",    r"\b\d{4}-\d{2}-\d{2}\b"),
    ("legal-cite",  r"\bArticles?\s+\d+(?:\(\d+\))?(?:\([a-z]\))?"),
    ("list-number", r"(?m)^\s*\d+(?:\.\d+)*[.)]\s"),
    ("heading-num", r"(?m)^\s*\d+(?:\.\d+)+\s+\S"),
    ("street",      r"\b\d{2,6}\s+(?:N|S|E|W|NW|NE|SW|SE)\.?\s+\S.*?\b(?:Drive|Street|Avenue|Road|Lane|Boulevard|Way|Dr|St|Ave|Rd|Blvd)\b"),
    ("us-zip",      r"\b[A-Z]{2}\s+\d{5}(?:-\d{4})?\b"),
    ("phone",       r"\+?\d[\d\s().-]{7,}\d"),
]

# Small bare integers from a banned row are not banned globally — "2 waves" from a
# PLACEHOLDER row would ban the digit 2 across the whole site. A banned value is
# enforced everywhere when it is distinctive: >= this magnitude, or written with a
# decimal or a thousands separator. Below it, the value is only enforced where an
# element declares that claim id explicitly.
BANNED_MIN_MAGNITUDE = 100

# The visual unit a value and its source line must share.
UNIT_TAGS = {"figure", "li", "td", "th", "blockquote", "section", "article", "aside", "dd"}
UNIT_CLASSES = {"cell", "stat", "stat-cell", "card", "study-card", "metric", "kpi", "tile", "readout"}

# What counts as a visible source line inside that unit.
SOURCE_TAGS = {"figcaption", "cite"}
SOURCE_CLASSES = {"src", "source", "cite", "prov", "provenance", "caption", "note"}

# In heuristic mode the provenance rule is only enforced where the markup looks like a
# figure — otherwise every numeral in a paragraph would demand a caption.
STAT_CLASSES = UNIT_CLASSES | {"num", "figure", "stat-row", "statrow"}
STAT_TAGS = {"figure"}

SKIP_TEXT = {"script", "style", "template", "svg"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
        "param", "source", "track", "wbr"}

NUMBER = re.compile(
    r"(?<![A-Za-z0-9.,])"
    r"(?<![A-Za-z]-)"          # Covid-19 and Twin-2K-500 are names, not figures
    r"(?P<cur>[$€£]?)"
    r"(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
    r"(?P<suf>\s?(?:%|p\.p\.|pp\b|k\b|K\b|thousand\b|million\b|m\b|billion\b|bn\b))?"
)
MULTIPLIER = {"k": 1e3, "K": 1e3, "thousand": 1e3, "m": 1e6, "million": 1e6,
              "bn": 1e9, "billion": 1e9}


# --- the register ------------------------------------------------------------------

class Claim:
    def __init__(self, cid, value_text, extra_text, status, caveat, checked, row_text,
                 first_party=False):
        self.cid = cid
        # True when the row came from a register table whose fourth column is
        # "Definition" rather than "Source" -- i.e. the claim is our own operating
        # record, computed from our own data, and there is no external document to
        # cite. Such a claim needs no visible source line. See CITATION_RULE below.
        self.first_party = first_party
        self.value_text = value_text
        self.status = status          # one of STATUSES, or the raw cell if unrecognised
        self.caveat = caveat          # prose after the status word, if any
        self.checked = checked
        self.row_text = row_text
        self.values = parse_values(value_text)
        # A withheld figure is often named in the reason it is withheld rather than in
        # the Value cell — C-004's Value reads "Not published" while the prose carries
        # the $0.30/$0.32 conflict. Banned rows therefore contribute every numeral in
        # the row; publishable rows contribute the Value cell only, so that a
        # definition's "n=137" never becomes a licence to print 137.
        #
        # Years are dropped from that harvest. A bare four-digit year in a row is a
        # citation, a benchmark wave or an approval date — never the figure the row is
        # about. Keeping them banned "2025" site-wide off the back of C-054's
        # "Donati & Rao (2025), title footnote", on a register that mandates
        # "Donati & Rao, 2025" in every source line. Excluding the whole Source column
        # instead would be the tidier rule and is wrong: C-004 names the $0.30/$0.32 it
        # withholds in exactly that cell, and dropping it disarmed the flagship ban.
        self.extra_values = {v: raw for v, raw in parse_values(extra_text).items()
                             if not is_year(v, raw)}
        self.blocked_by = next(
            (p for p in DO_NOT_PUBLISH if re.search(p, row_text, re.I)), None)
        self.scope_caveat = next(
            (p for p in SCOPE_CAVEATS if re.search(p, row_text, re.I)), None)

    @property
    def known(self):
        return self.status in STATUSES

    @property
    def publishable(self):
        return self.known and self.status in PUBLISHABLE_STATUS and not self.blocked_by

    @property
    def reason(self):
        if not self.known:
            return f"unrecognised status \"{self.status}\""
        if self.blocked_by:
            return f"{self.status}, held back by the register (\"{self.blocked_by}\")"
        return self.status


def strip_md(cell):
    cell = re.sub(r"`([^`]*)`", r"\1", cell)
    cell = re.sub(r"\*\*|\*|_", "", cell)
    return cell.strip()


def parse_values(text):
    """Every numeric token in a register cell. Ranges ($0.70–$20), multi-part values
    ("14 days planned · 19 days actual") and prose all reduce to the set of numbers the
    cell permits. Claim ids and dates are not values."""
    text = re.sub(r"\bC-\d+\b", "", text)
    skip = [(m.start(), m.end()) for m in re.finditer(r"\b\d{4}-\d{2}-\d{2}\b", text)]
    out = {}
    for m in NUMBER.finditer(text):
        if any(s <= m.start() < e for s, e in skip):
            continue
        v = normalize(m)
        if v is not None:
            out[v] = m.group(0).strip()
    return out


def is_year(value, raw):
    """A bare four-digit 1900-2100 integer, written without separator or unit. Kept
    deliberately narrow: 2,400 (C-040) carries a comma and 2400 is out of range, so
    neither is mistaken for a year."""
    return (re.fullmatch(r"\d{4}", raw) is not None
            and float(value).is_integer() and 1900 <= value <= 2100)


def normalize(m):
    raw = m.group("num").replace(",", "")
    try:
        v = float(raw)
    except ValueError:
        return None
    suf = (m.group("suf") or "").strip()
    v *= MULTIPLIER.get(suf, 1.0)
    return round(v, 6)


def precision(m):
    """Tolerance implied by how the number is written: 841.7k is 841,700 give or take
    50, so it matches C-010's 841,660. 6.1 is 6.1 give or take .05."""
    raw = m.group("num").replace(",", "")
    decimals = len(raw.split(".")[1]) if "." in raw else 0
    mult = MULTIPLIER.get((m.group("suf") or "").strip(), 1.0)
    return 0.5 * (10 ** -decimals) * mult if mult > 1 or decimals else 0.5


# A rounded figure still matches the value it rounds, but only within this much of it.
# Without the cap, "1 million people" would match C-015's 1,097,153 at the tolerance
# implied by writing one significant figure, and every large round number on the site
# would collide with something in the register.
ROUNDING_TOLERANCE = 0.02


def matches(token_value, token_match, registered):
    tol = min(precision(token_match), abs(registered) * ROUNDING_TOLERANCE)
    return abs(token_value - registered) <= tol


def checked_rank(claim):
    m = re.search(r"\d{4}-\d{2}-\d{2}", claim.checked or "")
    return m.group(0) if m else ""


def read_register(path):
    """Parse CLAIMS.md's tables into a register. Tables differ in shape — Headline has
    Value/Source/Status/Checked, Production has Value/Definition/Status/Checked, Studies
    has 'Figures used in mockup' — so columns are found by name, not position."""
    claims, notes = {}, []
    header, cols = None, {}
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.lstrip().startswith("|"):
            header, cols = None, {}
            continue
        cells = [strip_md(c) for c in line.strip().strip("|").split("|")]
        if re.match(r"^[\s:|-]+$", line.replace("|", "-")) and header:
            continue
        if header is None:
            header = [c.lower() for c in cells]
            cols = {}
            for i, name in enumerate(header):
                if name == "id":
                    cols["id"] = i
                elif name in ("value", "figures used in mockup"):
                    cols["value"] = i
                elif name == "status":
                    cols["status"] = i
                elif name == "checked":
                    cols["checked"] = i
                elif name == "definition":
                    cols["definition"] = i
            if "id" not in cols or "status" not in cols:
                header, cols = None, {}
            continue
        if len(cells) <= max(cols.values()):
            continue
        cid = cells[cols["id"]]
        if not re.match(r"^C-\d+$", cid):
            continue
        status_cell = cells[cols["status"]]
        # The first word is the status; anything after it is caveat prose, which the
        # row still gets read for (DO_NOT_PUBLISH). An unrecognised first word is kept
        # verbatim so the register report can name it.
        word = re.match(r"\s*([A-Za-z_]+)", status_cell)
        token = word.group(1).upper() if word else status_cell
        status = token if token in STATUSES else (status_cell or "(empty)")
        caveat = status_cell[word.end():].strip(" ,—-") if word else ""
        skip_cols = {cols.get(k) for k in ("id", "value", "status", "checked")}
        claim = Claim(
            cid,
            cells[cols["value"]] if "value" in cols else "",
            " ".join(c for i, c in enumerate(cells) if i not in skip_cols),
            status,
            caveat,
            cells[cols["checked"]] if "checked" in cols else "",
            " | ".join(cells),
            first_party="definition" in cols,
        )
        prior = claims.get(cid)
        if prior:
            # C-010 and C-011 each appear twice: a PLACEHOLDER row in Headline figures
            # superseded by a VERIFIED row in Production figures. Latest Checked wins,
            # and an undated row loses to a dated one.
            keep, drop = ((claim, prior) if checked_rank(claim) >= checked_rank(prior)
                          else (prior, claim))
            notes.append(f"{cid}: {drop.status} row superseded by the {keep.status} row"
                         f" ({keep.checked or 'undated'})")
            claim = keep
        claims[cid] = claim
    return claims, notes


def build_sets(claims):
    """publishable: value -> the ids that permit it. banned: value -> the ids that
    forbid it. Every non-VERIFIED row contributes to banned, including rows whose status
    the parser did not recognise — an unreadable status is treated as unpublishable.

    A value that lands in both sets stays banned. C-004's $0.32 is WITHHELD because the
    paper contradicts itself, even though C-012 quotes the same figure in a VERIFIED
    row; CLAIMS.md says render an em dash until it is called. That overlap is the
    loophole this rule closes, and the contested values are printed so it is visible."""
    publishable, banned, weak = {}, {}, {}
    for c in claims.values():
        if c.publishable:
            for v in c.values:
                publishable.setdefault(v, []).append(c.cid)
            continue
        for v, raw in list(c.values.items()) + list(c.extra_values.items()):
            target = banned if (abs(v) >= BANNED_MIN_MAGNITUDE or
                                "." in raw or "," in raw) else weak
            target.setdefault(v, []).append(c.cid)
    contested = sorted(set(publishable) & set(banned))
    for v in contested:
        publishable.pop(v)
    return publishable, banned, weak, contested


# --- the page ----------------------------------------------------------------------

class Node:
    def __init__(self, tag, attrs, parent, line):
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.children = []
        self.line = line

    def classes(self):
        return set((self.attrs.get("class") or "").split())

    def ancestors(self):
        n = self
        while n:
            yield n
            n = n.parent


class Run:
    def __init__(self, text, node, line):
        self.text, self.node, self.line = text, node, line


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", {}, None, 0)
        self.stack = [self.root]
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        node = Node(tag, {k: (v or "") for k, v in attrs}, self.stack[-1],
                    self.getpos()[0])
        self.stack[-1].children.append(node)
        if tag in SKIP_TEXT:
            self.skip += 1
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        node = Node(tag, {k: (v or "") for k, v in attrs}, self.stack[-1],
                    self.getpos()[0])
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag):
        if tag in SKIP_TEXT and self.skip:
            self.skip -= 1
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if self.skip or not data.strip():
            return
        self.stack[-1].children.append(Run(data, self.stack[-1], self.getpos()[0]))


def flatten(node):
    """Rendered text, with an index from character offset back to the element that
    produced it. Element boundaries become newlines so that adjacent cells in a stat
    row do not read as one number."""
    parts, runs, pos = [], [], 0

    def walk(n):
        nonlocal pos
        for child in n.children:
            if isinstance(child, Run):
                text = child.text
                parts.append(text)
                runs.append((pos, pos + len(text), child))
                pos += len(text)
            else:
                parts.append("\n")
                pos += 1
                walk(child)
                parts.append("\n")
                pos += 1
    walk(node)
    return "".join(parts), runs


def owner(runs, offset):
    for start, end, run in runs:
        if start <= offset < end:
            return run
    return None


def attr_ancestor(node, name):
    for n in node.ancestors():
        if name in n.attrs:
            return n
    return None


def units_of(node):
    """The visual units a value may draw its source line from, nearest first.

    The nearest card or cell is the default, and it is tight on purpose. An explicit
    data-claim-unit ancestor widens it to that element and stops there: an author who
    marks a <figure> as the unit is saying that its <figcaption> serves every value
    inside it, which is what DESIGN.md means by "the same visual unit". Without that
    marker the search does not widen, so a source line elsewhere on the page never
    counts as provenance for a figure.
    """
    units = []
    for n in node.ancestors():
        explicit = "data-claim-unit" in n.attrs
        if explicit or n.tag in UNIT_TAGS or (n.classes() & UNIT_CLASSES):
            units.append(n)
            if explicit:
                return units
    return units[:1]


def has_source(units):
    if isinstance(units, list):
        return any(has_source(u) for u in units)
    unit = units
    if unit is None:
        return False

    def walk(n):
        for child in n.children:
            if isinstance(child, Run):
                continue
            if "data-claim-source" in child.attrs or child.tag in SOURCE_TAGS \
                    or (child.classes() & SOURCE_CLASSES):
                text, _ = flatten(child)
                if text.strip():
                    return True
            if walk(child):
                return True
        return False
    return walk(unit)


def in_source_line(node):
    for n in node.ancestors():
        if "data-claim-source" in n.attrs or n.tag in SOURCE_TAGS \
                or (n.classes() & SOURCE_CLASSES):
            return True
    return False


def is_stat(node):
    for n in node.ancestors():
        if n.tag in STAT_TAGS or (n.classes() & STAT_CLASSES):
            return True
    return False


def allowed_spans(text):
    spans = []
    for name, pattern in ALLOW:
        for m in re.finditer(pattern, text):
            spans.append((m.start(), m.end(), name))
    return spans


# --- the check ---------------------------------------------------------------------

def check_file(path, claims, publishable, banned, weak, exempt_ids, only_failures):
    source = open(path, encoding="utf-8").read()
    tree = Tree()
    tree.feed(source)
    annotated = "data-claim" in source
    text, runs = flatten(tree.root)
    spans = allowed_spans(text)
    lines, failures = [], []

    def record(mark, kind, detail, line):
        lines.append((mark, kind, detail, line))
        if mark == "FAIL":
            failures.append((path, kind, detail, line))

    seen_claim_nodes = set()
    quote_verdicts = {}
    quoted_warnings = 0

    def quote_verdict(qnode):
        """Is this a well-formed quotation container? Cached: the answer is a property
        of the container, not of each numeral inside it."""
        key = id(qnode)
        if key in quote_verdicts:
            return quote_verdicts[key]
        cite = (qnode.attrs.get(QUOTE_ATTR) or "").strip()
        problems = []
        if not cite:
            problems.append("names no source")
        elif not re.match(r"^C-\d+$", cite):
            problems.append(f'names "{cite}", which is not a CLAIMS.md id')
        elif cite not in claims:
            problems.append(f"names unknown {cite}")
        elif not claims[cite].publishable:
            problems.append(f"names {cite}, which is {claims[cite].reason}")
        if not has_source(qnode):
            problems.append("carries no visible attribution line")
        verdict = (cite, not problems, "; ".join(problems))
        quote_verdicts[key] = verdict
        return verdict

    # Rule 2 of CLAIMS.md's publication rules is a text check, not a numeric one, and
    # runs over the whole rendered page. No exemption: a schema name in public copy is
    # wrong on a legal page too.
    for label, pattern in DENY_PHRASES:
        for m in re.finditer(pattern, text, re.I):
            run = owner(runs, m.start())
            phrase = re.sub(r"\s+", " ", m.group(0)).strip()
            record("FAIL", "phrase",
                   f'"{phrase}" — {label}; CLAIMS.md publication rule 2 '
                   f'(no platforms, schemas or migrations in public copy)',
                   run.line if run else 0)

    for m in NUMBER.finditer(text):
        value = normalize(m)
        if value is None:
            continue
        run = owner(runs, m.start())
        if run is None:
            continue
        node, line = run.node, run.line
        shown = re.sub(r"\s+", " ", m.group(0)).strip()

        declared_node = attr_ancestor(node, "data-claim")
        declared = (declared_node.attrs["data-claim"].split()
                    if declared_node else [])
        ids = [i for i in declared if i != "none"]

        # 0. Attributed quotation. Someone else's words, someone else's figures.
        quote_node = attr_ancestor(node, QUOTE_ATTR)
        if quote_node is not None:
            cite, ok, why = quote_verdict(quote_node)
            if not ok:
                record("FAIL", "quote",
                       f'"{shown}" — quotation block {why}', line)
                continue
            withheld = next((who for v, who in banned.items() if matches(value, m, v)),
                            None)
            if withheld:
                held = "; ".join(f"{c} ({claims[c].reason})" for c in withheld)
                record("warn", "quote",
                       f'"{shown}" — quoted from {cite}, and {held}. '
                       f'Permitted as attributed speech; never repeat it in our own copy',
                       line)
                quoted_warnings += 1
            elif not only_failures:
                record("skip", "quote", f'"{shown}" — quoted from {cite}', line)
            continue

        # 1. Banned values. No allowlist, no exemption, no mode. Hard stop.
        banned_ids = next((who for v, who in banned.items() if matches(value, m, v)),
                          None)
        if banned_ids is None and ids:
            # Below BANNED_MIN_MAGNITUDE a banned value is only enforced where the
            # element declares that claim itself.
            banned_ids = next((who for v, who in weak.items()
                               if matches(value, m, v) and set(who) & set(ids)), None)
        if banned_ids:
            why = "; ".join(f"{c} ({claims[c].reason})" for c in banned_ids)
            record("FAIL", "banned", f'"{shown}" — {why}', line)
            continue

        exempt = attr_ancestor(node, "data-claim-scan")
        if exempt is not None and exempt.attrs.get("data-claim-scan") == "off":
            if not only_failures:
                record("skip", "exempt", f'"{shown}" — inside data-claim-scan="off"', line)
            continue
        if any(node_id in exempt_ids for node_id in
               (n.attrs.get("id", "") for n in node.ancestors())):
            if not only_failures:
                record("skip", "exempt", f'"{shown}" — inside an --exempt-id container', line)
            continue

        # 2. Declared claims: value must belong to the claim, and the unit must carry
        #    a visible source line. This is the provenance rule, mechanised.
        if declared_node is not None:
            if "none" in declared:
                if not only_failures:
                    record("skip", "declared-none", f'"{shown}" — declared not a claim', line)
                continue
            unknown = [i for i in ids if i not in claims]
            if unknown:
                record("FAIL", "claim-id",
                       f'"{shown}" — data-claim references unknown {", ".join(unknown)}', line)
                continue
            blocked = [i for i in ids if not claims[i].publishable]
            if blocked:
                why = "; ".join(f"{i} ({claims[i].reason})" for i in blocked)
                record("FAIL", "banned", f'"{shown}" — declares {why}', line)
                continue
            ok_value = any(matches(value, m, v) for i in ids for v in claims[i].values)
            if not ok_value:
                permitted = ", ".join(sorted(
                    {r for i in ids for r in claims[i].values.values()}))
                record("FAIL", "claim-value",
                       f'"{shown}" — declares {", ".join(ids)}, which permits {permitted}', line)
                continue
            key = id(declared_node)
            # THE CITATION RULE. A source line is required where the claim rests on
            # somebody else's document, and not where it is our own operating record.
            #
            # Nandan, 2026-08-26: "We are the ones claiming the data. Nobody cares
            # where it comes from. They're assuming we have access to our own data."
            # He is right, and the rule is better for it: "Virtual Lab production
            # database" under a Virtual Lab figure is not a citation, it is a
            # restatement of who is speaking. It cites nothing a reader could check,
            # and printing it beside a real citation devalues the real one.
            #
            # The split is a fact about the claim, so it lives in the register, not in
            # the markup -- a page must not be able to talk its way out of a citation.
            # A register table whose fourth column is "Definition" says how WE computed
            # a number from OUR data; a table whose fourth column is "Source" says
            # where somebody else published it. Only the first is exempt.
            #
            # It fails safe: exemption requires a Definition column, so anything
            # unmarked, mis-parsed, or newly added to a Source table still demands a
            # citation. A source line is never FORBIDDEN here -- the box plots keep
            # theirs, because those state what an "active day" is and what the box
            # spans, which is a definition a reader needs and not an attribution.
            if all(claims[i].first_party for i in ids):
                seen_claim_nodes.add(key)
                if not only_failures:
                    record("ok", ", ".join(ids), f'"{shown}" — our own record', line)
                continue
            units = units_of(declared_node)
            if not has_source(units):
                if key not in seen_claim_nodes:
                    where = (f"<{units[0].tag}> has no source line" if units
                             else "it sits in no enclosing unit")
                    record("FAIL", "provenance",
                           f'{", ".join(ids)} "{shown}" — {where}', line)
                seen_claim_nodes.add(key)
                continue
            seen_claim_nodes.add(key)
            if not only_failures:
                record("ok", ", ".join(ids), f'"{shown}"', line)
            continue

        # 3. Un-annotated numerals.
        if in_source_line(node):
            if not only_failures:
                record("skip", "source-line", f'"{shown}" — inside a source line', line)
            continue
        allow = next((n for s, e, n in spans if s <= m.start() and m.end() <= e), None)
        if allow:
            if not only_failures:
                record("skip", allow, f'"{shown}"', line)
            continue
        if annotated:
            record("FAIL", "unannotated",
                   f'"{shown}" — no data-claim, and this page uses annotation', line)
            continue
        cids = next((publishable[v] for v in publishable if matches(value, m, v)), None)
        if not cids:
            record("FAIL", "unsourced", f'"{shown}" — no VERIFIED value in CLAIMS.md', line)
            continue
        if is_stat(node) and not has_source(units_of(node)):
            record("FAIL", "provenance",
                   f'{", ".join(cids)} "{shown}" — figure has no source line', line)
            continue
        if not only_failures:
            record("ok", ", ".join(cids), f'"{shown}" (heuristic)', line)

    return annotated, lines, failures


def is_template(path):
    """An Eleventy source template, not a page. D-006: pages are .html with front
    matter and a layout: line, and Eleventy renders them into _site/. A template's
    own text is not what ships — its {# #} comments carry section numbers, motif ids
    and claim ids that are stripped at build time, and scanning them reports drift
    that does not exist on any page. The built output is scanned instead.

    Detected by the front-matter fence on the first line, which is what makes the
    file a template in the first place. A plain .html file with no front matter is
    still walked, so this narrows nothing that was previously covered."""
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.readline().rstrip("\n\r") == "---"
    except OSError:
        return False


def html_files(paths, include_vendor):
    """Default walk: everything that ships, and nothing that is built to fail.

    _site/ is walked when it exists — it is the built site, and it is what a visitor
    receives. The source templates that produced it are skipped (see is_template).
    Before a first build there is no _site/, so the root .html files are walked as
    they always were and the gate still means something on a clean checkout.

    Always skipped: scripts/fixtures/, nine pages whose entire job is to fail — a
    gate that can never pass is a gate nobody runs.

    Also always skipped: docs/ and its build output in _site/docs/. D-029.
    The provenance rule governs CLAIMS — a figure offered as evidence for what
    Virtual Lab can do. Reference documentation is not making claims: its numerals
    are JSON payloads, timeout values, HTTP codes, field weights and API examples,
    and there is nothing for a reader to check because nothing is being asserted.
    Pointing this checker at 47 such pages produces hundreds of findings, and a gate
    that reports hundreds of non-problems is the same dead gate scripts/fixtures/
    already taught us not to build.

    THE RULE ITSELF IS NOT NARROWED. If a docs page ever states an outcome figure —
    a response rate, a cost, a sample achieved — it is a claim wherever it is
    printed, and it goes in CLAIMS.md and gets scanned by naming the file
    explicitly, which the `paths` argument above has always allowed."""
    if paths:
        return paths
    site = os.path.join(REPO, "_site")
    built = os.path.isdir(site)
    found, skipped = [], []
    for root, dirs, files in os.walk(REPO):
        if not include_vendor:
            # _includes/ holds layouts and partials. A layout is not a page — it is
            # half of one, and it reaches a visitor only through the built output that
            # is already being scanned. Its comments carry the same section numbers a
            # template's do.
            drop = {".git", "node_modules", "media", "fixtures", "_includes", "docs"}
            if not built:
                drop.add("_site")
            dirs[:] = [d for d in dirs if d not in drop]
        for f in sorted(files):
            if not f.endswith(".html"):
                continue
            full = os.path.join(root, f)
            if built and is_template(full):
                skipped.append(full)
                continue
            found.append(full)
    for t in sorted(skipped):
        print(f"  note  {short(t)} is an Eleventy template; its built output in "
              f"_site/ is scanned instead")
    return sorted(found)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="*", help="HTML files (default: every .html in the repo)")
    ap.add_argument("--claims", default=os.path.join(REPO, "CLAIMS.md"))
    ap.add_argument("--exempt-id", action="append", default=[], metavar="ID",
                    help="skip numerals inside this element id (repeatable)")
    ap.add_argument("--include-vendor", action="store_true",
                    help="also walk node_modules, and source templates")
    ap.add_argument("--only-failures", action="store_true", help="print failures only")
    ap.add_argument("--register", action="store_true",
                    help="print the parsed register and exit")
    args = ap.parse_args()

    claims, notes = read_register(args.claims)
    publishable, banned, weak, contested = build_sets(claims)

    print(f"REGISTER  {short(args.claims)}")
    print(f"  {len(claims)} claims · "
          f"{sum(1 for c in claims.values() if c.publishable)} publishable · "
          f"{len(publishable)} publishable values · {len(banned)} banned values")
    for note in notes:
        print(f"  note  {note}")

    for c in sorted(claims.values(), key=lambda c: c.cid):
        if c.scope_caveat and c.publishable:
            print(f"  scope {c.cid} is publishable but scoped — \"{c.caveat[:72]}\"."
                  f" Not enforceable here; a human checks the wording around it.")

    register_failures = []
    for c in sorted(claims.values(), key=lambda c: c.cid):
        if not c.known:
            detail = (f'{c.cid} status reads "{c.status}", which is not one of '
                      f'{"/".join(sorted(STATUSES))}')
            print(f"  FAIL  {detail}")
            register_failures.append((args.claims, "register", detail, 0))
        elif c.blocked_by and c.values:
            print(f"  held  {c.cid} {c.status} — {c.value_text[:60]}"
                  + (f" ({c.caveat[:60]})" if c.caveat else ""))
    for v in contested:
        pub = ", ".join(sorted({c.cid for c in claims.values()
                                if c.publishable and v in c.values}))
        print(f"  contested  {v:g} appears in a banned row and in {pub} — banned wins")

    if args.register:
        for c in sorted(claims.values(), key=lambda c: c.cid):
            vals = ", ".join(sorted(c.values.values())) or "—"
            print(f"  {c.cid}  {c.status:<11} {'pub ' if c.publishable else 'HELD'}  {vals}")
        return 1 if register_failures else 0

    all_failures = list(register_failures)
    for path in html_files(args.files, args.include_vendor):
        annotated, lines, failures = check_file(
            path, claims, publishable, banned, weak,
            set(args.exempt_id), args.only_failures)
        mode = "annotated" if annotated else "heuristic — no data-claim on this page"
        print(f"\n{short(path)}  [{mode}]")
        if not lines:
            print("  clean" if args.only_failures else "  no numerals in body text")
        for mark, kind, detail, line in lines:
            print(f"  {mark:<4} {kind:<14} {detail}  (line {line})")
        all_failures.extend(failures)

    print()
    if all_failures:
        by_kind = {}
        for path, kind, detail, line in all_failures:
            by_kind.setdefault(kind, []).append((path, detail, line))
        print(f"{len(all_failures)} failure(s):")
        for kind in sorted(by_kind):
            print(f"  {kind} ({len(by_kind[kind])})")
            for path, detail, line in by_kind[kind]:
                print(f"    {short(path)}:{line}  {detail}")
        print("\nEvery number needs a VERIFIED row in CLAIMS.md. A claim resting on\n"
              "somebody else's document also needs its citation in the same visual\n"
              "unit; a claim from our own record does not. If a value is missing,\n"
              "render — and add a PLACEHOLDER row.")
        return 1
    print("Every number traces to a VERIFIED row, and every third-party claim is cited.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
