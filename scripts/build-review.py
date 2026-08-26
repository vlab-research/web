#!/usr/bin/env python3
"""Assemble the self-contained asset-review page. Reads only; writes one HTML file."""
import base64, html, json, pathlib

REPO = pathlib.Path("/home/nandan/Documents/vlab-research/vlab.digital")
SCR  = REPO / "build"   # was a session temp dir; see scripts/README.md
OUT  = SCR / "review-assets.html"

read = lambda p: pathlib.Path(p).read_text(encoding="utf-8")

sprite   = read(REPO/"assets/icons/icons.svg")
mark     = read(REPO/"assets/mark.svg")
favicon  = read(REPO/"assets/favicon.svg")
mad      = read(REPO/"assets/figures/mad-comparison.svg")
cov_map  = read(REPO/"build/coverage-map.html")
cov_strip= read(REPO/"build/coverage-strip.html")
cov_reg  = read(REPO/"build/coverage-regions.html")
paper    = json.loads(read(REPO/"_data/paper.json"))

def dataurl(p):
    return "data:image/png;base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()

ICO16, ICO32, ICO48 = (dataurl(SCR/f"ico-{s}.png") for s in (16,32,48))

# --- strip the outer <svg> wrapper off mark/favicon so we can re-emit at any size ---
def inner(svg):
    return svg[svg.index(">", svg.index("<svg"))+1 : svg.rindex("</svg>")]

MARK_INNER = inner(mark)
FAV_INNER  = inner(favicon)

def mark_at(px, cls=""):
    return (f'<svg class="mk {cls}" width="{px}" height="{px}" viewBox="0 0 22 22" '
            f'aria-hidden="true">{MARK_INNER}</svg>')

def fav_at(px):
    return (f'<svg width="{px}" height="{px}" viewBox="0 0 32 32" role="img">'
            f'<title>Virtual Lab favicon at {px} pixels</title>{FAV_INNER}</svg>')

# ---------------------------------------------------------------- icon table
ICONS = [
 ("stratify","Stratify","Three bars, descending lengths.", None),
 ("optimize","Optimize","Three bars + a full-height target tick at right.",
  "Bar lengths are deliberately non-monotonic (17.5 / 11.5 / 14.5) so the icon cannot be "
  "read as Stratify's descending stack, and so the tick does work: two bars short of "
  "target, one at it."),
 ("recruit","Recruit","Three centred bars narrowing downward.",
  "Built as §7 specifies. Worth saying out loud: §6 bans “funnels narrowing to a coin.” "
  "The banned thing is the coin — the conversion metaphor — and three centred bars read as a "
  "population narrowing to a sample. The two lines of the spec sit close enough that someone "
  "should record which one governs."),
 ("survey","Survey","Two offset rounded bars (thread).",
  "Motif M5. The set's only round cap and join, and the only place radius exceeds 2px."),
 ("weight","Weight","A rule with three dots of differing radius.",
  "Shipped as a rule with three cells (3 / 5 / 7) seated on it, bottoms aligned, ascending. "
  "See the flag below: a dot is not one of the four primitives, and centring the cells on the "
  "rule read as a bolt rather than as mass on a beam."),
 ("waves","Waves","A baseline with three verticals of differing height.",
  "Shares a silhouette family with Weight. They are separated by fill — Waves is hairline "
  "strokes reaching high, Weight is solid cells in the lower band. Revisit if the two ever "
  "appear in the same row."),
 ("open-source","Open source","Two facing brackets <code>[ ]</code>.", None),
 ("precision","Precision","Two rules, a centre dot, two end ticks.",
  "Centre dot shipped as a 5×5 cell, same flag as Weight. Drawn as a short, centred span so it "
  "cannot be confused with Interval, which is the wide one."),
 ("coverage","Coverage","Six cells at two opacities.",
  "The two opacities are 1 and .4 — two steps of the coverage map's .26 / .40 / .56 / .76 / 1 "
  "ramp, rather than an invented value. The set's only filled icon: "
  "<code>fill=\"currentColor\"</code>, no stroke."),
 ("monitor","Monitor","An axis with a polyline.",
  "The polyline ends mid-height rather than high right, so it cannot read as the upward-right "
  "arrow §6 bans."),
 ("export","Export","A grid with one column rule emphasised.",
  "Stroke is fixed at 1.75 and there is one <code>currentColor</code>, so the rule cannot be "
  "emphasised by weight or by hue. It is emphasised by extension: it runs past the frame top "
  "and bottom while the other three stop at it."),
 ("interval","Interval","Two brackets with two crossbars.",
  "The two crossbars are of different width — a wide estimate and a tight one — which is M3's "
  "actual job."),
]

def icon_svg(slug, px, cls):
    return (f'<svg class="ic {cls}" width="{px}" height="{px}" viewBox="0 0 24 24" '
            f'aria-hidden="true"><use href="#icon-{slug}"/></svg>')

icon_cards = []
for slug, name, spec, note in ICONS:
    paper_row = "".join(icon_svg(slug, px, cls)
                        for cls in ("ic-brass","ic-ink") for px in (48,24))
    ink_row   = "".join(icon_svg(slug, px, cls)
                        for cls in ("ic-brass-inv","ic-on-inv") for px in (48,24))
    shipped = (f'<p class="shipped"><span class="tag">Shipped</span>{note}</p>' if note else "")
    icon_cards.append(f"""
  <figure class="icard">
    <figcaption class="ihead"><span class="iname">{name}</span><code class="islug">#icon-{slug}</code></figcaption>
    <div class="itiles">
      <div class="itile pap">{paper_row}</div>
      <div class="itile ink">{ink_row}</div>
    </div>
    <p class="ispec"><span class="tag">&sect;7</span>{spec}</p>
    {shipped}
  </figure>""")
ICON_CARDS = "\n".join(icon_cards)

# ink band strip: all twelve at 24 and 48
band_icons = "".join(
  f'<div class="bi"><div class="bi-row">{icon_svg(s,48,"ic-brass-inv")}'
  f'{icon_svg(s,24,"ic-brass-inv")}{icon_svg(s,48,"ic-on-inv")}{icon_svg(s,24,"ic-on-inv")}</div>'
  f'<span class="bi-n">{n}</span></div>' for s,n,_,_ in ICONS)

# ---------------------------------------------------------------- paper
# D-016, restored 2026-08-21: the Papers page is title, byline, the abstract quoted
# verbatim as attributed quotation, the citation, BibTeX and the link. Exactly two
# fields of _data/paper.json render, and both are read here: bibtex.entry and
# abstract.verbatim. The cost table, the comparator arms and every other field stay
# under not_for_publication and are NOT read.
title      = paper["title"]["value"]
authors    = paper["authors"]
byline     = " &middot; ".join(f'{html.escape(a["name"])}, {html.escape(a["affiliation"])}' for a in authors)
paper_url  = "https://ssrn.com/abstract=5495148"          # C-055, VERIFIED
bibtex     = html.escape(paper["_meta"]["bibtex"]["entry"])

# The abstract is COPIED FROM THE FIELD, never retyped. Nothing between the JSON and
# the page but html.escape(), so a page that disagrees with _data/paper.json is a bug
# in this line and nowhere else.
abstract   = html.escape(paper["abstract"]["verbatim"])
abs_edition = html.escape(paper["abstract"]["source_edition"])
_W = {1:"one",2:"two",3:"three",4:"four",5:"five",6:"six"}
abs_identical = _W.get(len(paper["abstract"]["identical_in"]),
                      str(len(paper["abstract"]["identical_in"])))

# The container as the Papers page builds it, shown as markup rather than described.
MARKUP = """<blockquote data-claim-quote="C-055">
  <p>This paper introduces and validates a new methodology …</p>
  <p class="src" data-claim-source>Abstract, quoted verbatim.
     Donati &amp; Rao, 2025. https://ssrn.com/abstract=5495148</p>
</blockquote>

<p class="reconcile">The abstract describes the thirty-three studies analysed
   in the paper. Our operating history is larger, and is reported on the
   Studies index.</p>"""
markup = html.escape(MARKUP)

# ---------------------------------------------------------------- the mad figure, twice
# The <style> block inside the SVG is document-scoped when inlined in HTML, so the
# second copy is emitted without it.
_s, _e = mad.index("<style>"), mad.index("</style>") + len("</style>")
mad_style, mad_nostyle = mad[_s:_e], mad[:_s] + mad[_e:]
mad_inv = mad_nostyle.replace('class="fig-mad"', 'class="fig-mad inv"', 1) \
                     .replace('id="madTitle"','id="madTitleInv"').replace('id="madDesc"','id="madDescInv"') \
                     .replace('aria-labelledby="madTitle madDesc"','aria-labelledby="madTitleInv madDescInv"')

TOKENS = """
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
  --brass-inv:#C9A250; /* brass ON an ink band - identical in BOTH themes */
  --data-inv:#4E9DB0;  /* data  ON an ink band - identical in BOTH themes */
  /* lattice ground opacity */
  --lat-op:.042;     --lat-op-inv:.065;
"""
DARK = """
    --paper:#13181C;   --surface:#1C2227;   --sunk:#262E34;   --invert:#0C1013;
    --ink:#E6EBEE;     --ink-2:#B2BEC6;     --ink-3:#808E97;
    --rule:#2A343B;    --rule-2:#414F58;
    --brass:#C9A250;   --brass-2:#DBB768;
    --data:#4E9DB0;    --data-2:#4A6871;
    --on-invert:#E6EBEE; --on-invert-2:#94A3AB; --rule-invert:#232C33;
    --brass-inv:#C9A250; --data-inv:#4E9DB0;
    --lat-op:.055;     --lat-op-inv:.065;
"""

def lattice(uid, inv=False):
    return (f'<svg class="lat{" inv" if inv else ""}" aria-hidden="true">'
            f'<defs><pattern id="{uid}" width="18" height="18" patternUnits="userSpaceOnUse">'
            f'<rect width="8" height="8" fill="currentColor"/></pattern></defs>'
            f'<rect width="100%" height="100%" fill="url(#{uid})"/></svg>')

CSS = """
:root{%(TOKENS)s}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){%(DARK)s}
}
:root[data-theme="dark"]{%(DARK)s}

*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%%}
body{margin:0;background:var(--paper);color:var(--ink);
  font:400 16.5px/1.6 "Source Sans 3","Helvetica Neue",Arial,sans-serif;
  font-variant-numeric:tabular-nums;-webkit-font-smoothing:antialiased}
a{color:var(--brass)}
code{font:400 .92em "IBM Plex Mono",ui-monospace,monospace}
:focus-visible{outline:2px solid var(--brass);outline-offset:3px}

.wrap{max-width:1180px;margin:0 auto;padding:0 32px}
main section{border-top:1px solid var(--rule);padding:84px 0}
main section:first-child{border-top:0;padding-top:56px}

h1{font:300 clamp(42px,6vw,70px)/1.02 "Zilla Slab",Georgia,serif;letter-spacing:-.018em;
   margin:0;text-wrap:balance}
h2{font:300 clamp(28px,3.6vw,42px)/1.10 "Zilla Slab",Georgia,serif;letter-spacing:-.012em;
   margin:0;text-wrap:balance}
h3{font:400 20px/1.30 "Zilla Slab",Georgia,serif;margin:0;text-wrap:balance}
p{margin:0;max-width:65ch}
.sub{font-size:18px;line-height:1.55;max-width:50ch;color:var(--ink-2)}
.eyebrow{font:500 11px "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.15em;
  text-transform:uppercase;color:var(--ink-3);margin:0}
.caption,small{font-size:13px}
.stack{display:flex;flex-direction:column;gap:16px}
.stack.tight{gap:9px}
.stack.loose{gap:28px}
.hd{display:flex;flex-direction:column;gap:12px;margin-bottom:34px}
.srcline{font:italic 400 13px/1.5 "Source Serif 4",Georgia,serif;color:var(--ink-3);
  max-width:66ch;margin:0}
.tag{font:500 9.5px "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.13em;
  text-transform:uppercase;color:var(--brass);margin-right:9px;white-space:nowrap}
.scroll{overflow-x:auto}

/* ---- top bar: DESIGN.md sect.8 Nav ---- */
.topbar{position:sticky;top:0;z-index:20;height:66px;
  background:color-mix(in srgb,var(--paper) 86%%,transparent);
  -webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);
  border-bottom:1px solid var(--rule)}
.topbar .wrap{height:66px;display:flex;align-items:center;gap:16px}
.brand{display:flex;align-items:center;gap:11px;color:var(--ink)}
.brand .nm{font:300 21px/1 "Zilla Slab",Georgia,serif;letter-spacing:-.01em}
.brand .sep{color:var(--rule-2)}
.brand .pg{font:500 11px "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.15em;
  text-transform:uppercase;color:var(--ink-3)}
.themer{margin-left:auto;display:flex;align-items:center;gap:10px}
.themer .lb{font:500 9.5px "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.13em;
  text-transform:uppercase;color:var(--ink-3)}
.seg{display:flex;gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:2px}
.seg button{appearance:none;border:0;border-radius:0;background:var(--paper);color:var(--ink-2);
  font:600 11.5px "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.09em;
  text-transform:uppercase;padding:12px 13px;min-height:44px;cursor:pointer;
  transition:color 150ms,background-color 150ms}
.seg button:first-child{border-radius:2px 0 0 2px}
.seg button:last-child{border-radius:0 2px 2px 0}
.seg button[aria-pressed="true"]{background:var(--ink);color:var(--paper)}

/* ---- contents ---- */
.toc{display:grid;grid-template-columns:repeat(auto-fit,minmax(268px,1fr));
  border-top:1px solid var(--rule);border-left:1px solid var(--rule)}
.toc a{background:var(--paper);padding:16px 18px;
  border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);text-decoration:none;color:var(--ink);
  display:flex;flex-direction:column;gap:5px;transition:background-color 150ms}
.toc a:hover{background:var(--sunk)}
.toc .n{font:500 10px "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.15em;color:var(--brass)}
.toc .t{font:400 17px/1.25 "Zilla Slab",Georgia,serif}
.toc .d{font-size:13px;color:var(--ink-2)}

/* ---- the ask + flag blocks ---- */
.ask,.flag{border-left:2px solid var(--brass);padding:4px 0 4px 18px;
  display:flex;flex-direction:column;gap:9px;max-width:70ch}
.ask .hh,.flag .hh{font:500 10.5px "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.14em;
  text-transform:uppercase;color:var(--brass);margin:0}
.ask p,.flag p{font-size:15px;color:var(--ink-2);margin:0;max-width:70ch}
.flag{border-left-color:var(--rule-2)}
.flag .hh{color:var(--ink-2)}
.band .ask,.band .flag{border-left-color:var(--brass-inv)}
.band .ask .hh,.band .flag .hh{color:var(--brass-inv)}
.band .ask p,.band .flag p{color:var(--on-invert-2)}

/* ---- ink band, DESIGN.md sect.8 ---- */
.band{position:relative;overflow:hidden;background:var(--invert);color:var(--on-invert)}
.band .wrap{position:relative;padding-top:56px;padding-bottom:56px}
.band h2,.band h3{color:var(--on-invert)}
.band p{color:var(--on-invert-2)}
.band .eyebrow{color:var(--on-invert-2)}
.band .srcline{color:var(--on-invert-2)}
.lat{position:absolute;inset:0;width:100%%;height:100%%;color:var(--ink);
  opacity:var(--lat-op);pointer-events:none}
.lat.inv{color:var(--on-invert);opacity:var(--lat-op-inv)}

/* ---- icons ---- */
.icons{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(320px,100%%),1fr));
  border-top:1px solid var(--rule);border-left:1px solid var(--rule)}
.icard{background:var(--surface);margin:0;padding:20px 20px 18px;
  border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);
  display:flex;flex-direction:column;gap:12px}
.ihead{display:flex;align-items:baseline;justify-content:space-between;gap:12px}
.iname{font:400 20px/1.2 "Zilla Slab",Georgia,serif}
.islug{font:400 11px "IBM Plex Mono",ui-monospace,monospace;color:var(--ink-3)}
.itiles{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--rule);
  border:1px solid var(--rule);border-radius:2px}
.itile{display:flex;align-items:center;gap:14px;padding:16px 18px;flex-wrap:wrap}
.itile.pap{background:var(--paper)}
.itile.ink{background:var(--invert)}
.ic{display:block;flex:none}
.ic-brass{color:var(--brass)}
.ic-ink{color:var(--ink)}
.ic-brass-inv{color:var(--brass-inv)}
.ic-on-inv{color:var(--on-invert)}
.ispec,.shipped{font-size:14px;line-height:1.55;color:var(--ink-2);margin:0;max-width:none}
.shipped{color:var(--ink-2)}
.shipped .tag{color:var(--ink-3)}
.ikey{display:flex;flex-wrap:wrap;gap:20px;align-items:center}
.ikey span{font:400 11.5px "IBM Plex Mono",ui-monospace,monospace;color:var(--ink-3);
  display:flex;align-items:center;gap:8px}
.ikey i{width:12px;height:12px;display:block;border-radius:2px}

/* icon ink band strip */
.bstrip{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
  border-top:1px solid var(--rule-invert);border-left:1px solid var(--rule-invert)}
.bi{background:var(--invert);padding:16px 16px 12px;
  border-right:1px solid var(--rule-invert);border-bottom:1px solid var(--rule-invert);display:flex;flex-direction:column;gap:10px}
.bi-row{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.bi-n{font:500 9.5px "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.13em;
  text-transform:uppercase;color:var(--on-invert-2)}

/* ---- mark + favicon ---- */
.specrow{display:flex;flex-wrap:wrap;gap:1px;background:var(--rule);
  border:1px solid var(--rule);border-radius:2px}
.specrow .cellp,.specrow .celli{padding:22px 26px;display:flex;flex-direction:column;
  align-items:flex-start;gap:14px;min-width:150px;flex:1}
.specrow .cellp{background:var(--paper)}
.specrow .celli{background:var(--invert)}
.specrow .celli .px{color:var(--on-invert-2)}
.px{font:500 9.5px "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.13em;
  text-transform:uppercase;color:var(--ink-3);max-width:none}
.mk{display:block;color:var(--ink)}
.mk.brass{color:var(--brass)}
.celli .mk{color:var(--on-invert)}
.celli .mk.brass{color:var(--brass-inv)}
.navsim{display:flex;align-items:center;gap:11px;height:66px;padding:0 18px;
  background:var(--paper);border:1px solid var(--rule);border-radius:2px}
.navsim .nm{font:300 21px/1 "Zilla Slab",Georgia,serif;letter-spacing:-.01em}
.navsim .lk{font:400 14.5px "Source Sans 3","Helvetica Neue",Arial,sans-serif;color:var(--ink-2)}
.navsim .lk.on{color:var(--ink);position:relative}
.navsim .lk.on::after{content:"";position:absolute;left:0;right:0;bottom:-23px;height:2px;
  background:var(--brass)}
.raster{display:flex;flex-wrap:wrap;gap:26px;align-items:flex-end;overflow-x:auto}
.raster figure{margin:0;display:flex;flex-direction:column;gap:10px}
.raster img{image-rendering:pixelated;display:block;border:1px solid var(--rule);border-radius:0}

/* ---- coverage (CSS emitted by scripts/build-coverage-map.py) ---- */
.cov{margin:0}
.coverage{display:block;width:100%%;height:auto}
.cv-ghost{fill:none;stroke:var(--rule);stroke-width:.7}
.cv-on{fill:var(--data);stroke:var(--paper);stroke-width:.6}
.cv-pending{fill:none;stroke:var(--data);stroke-width:1.2;stroke-dasharray:3 2}
.mlegend{display:flex;flex-wrap:wrap;gap:18px;margin-top:18px;align-items:center}
.ml{display:flex;align-items:center;gap:8px;color:var(--ink-3);
  font:400 11.5px "IBM Plex Mono",ui-monospace,monospace;font-variant-numeric:tabular-nums}
.ml i{width:20px;height:10px;background:var(--data);display:block;border-radius:2px}
.ml i.p{background:none;border:1.1px dashed var(--data)}
.src{font:400 13px/1.5 "Source Serif 4",Georgia,serif;font-style:italic;
  color:var(--ink-3);margin-top:16px;max-width:66ch}
.cs-bar{display:block;width:100%%;height:30px}
.cs-ground{fill:var(--rule)}
.cs-seg{fill:var(--data)}
.cs-cells{display:grid;grid-template-columns:repeat(6,1fr);gap:1px;background:var(--rule);
  border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);margin-top:1px}
.cs-cell{background:var(--paper);padding:18px 16px 16px;display:flex;flex-direction:column;gap:0}
.cs-n{font:400 clamp(22px,2.2vw,28px)/1 "IBM Plex Mono",ui-monospace,monospace;
  letter-spacing:-.025em;color:var(--ink);font-variant-numeric:tabular-nums}
.cs-r{margin-top:11px;font:500 10px "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.13em;
  text-transform:uppercase;color:var(--ink-2);line-height:1.5}
.cs-m{margin-top:7px;font:400 12.5px "Source Serif 4",Georgia,serif;font-style:italic;color:var(--ink-3)}
.cs-p{margin-top:5px;font:400 11px "IBM Plex Mono",ui-monospace,monospace;color:var(--brass);
  font-variant-numeric:tabular-nums}
.note{border-left:2px solid var(--brass);padding:4px 0 4px 18px;margin-top:34px;
  display:flex;flex-direction:column;gap:9px;max-width:66ch}
.note .hd{font:500 10.5px "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.14em;
  text-transform:uppercase;color:var(--brass);margin:0}
.note p{font:400 15px/1.6 "Source Sans 3","Helvetica Neue",Arial,sans-serif;color:var(--ink-2);margin:0}
@media (max-width:1000px){.cs-cells{grid-template-columns:repeat(3,1fr)}}
@media (max-width:640px){.cs-cells{grid-template-columns:repeat(2,1fr)}}

/* ---- figures on cards ---- */
.figcard{background:var(--surface);border:1px solid var(--rule);border-radius:2px;
  padding:22px 22px 18px;margin:0;display:flex;flex-direction:column;gap:14px}
.band .figcard{background:transparent;border-color:var(--rule-invert)}
.cap{font:500 9.5px "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.11em;
  text-transform:uppercase;color:var(--ink-3);margin:0;max-width:none}
.band .cap{color:var(--on-invert-2)}
.figcard svg{max-width:100%%}

/* ---- type specimen ---- */
.tspec{display:flex;flex-direction:column;gap:10px;padding:24px 0;
  border-top:1px solid var(--rule)}
.spec{font:400 11px "IBM Plex Mono",ui-monospace,monospace;color:var(--ink-3);
  letter-spacing:.04em;margin:0;max-width:none}
.serifprose{font:400 16.5px/1.6 "Source Serif 4",Georgia,serif;max-width:62ch;color:var(--ink)}
.sans600{font:600 16.5px/1.6 "Source Sans 3","Helvetica Neue",Arial,sans-serif}
.mono400{font:400 15px/1.6 "IBM Plex Mono",ui-monospace,monospace}
.mono500{font:500 15px/1.6 "IBM Plex Mono",ui-monospace,monospace}
.big{font-size:34px;line-height:1.25;margin:0}
.statrow{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--rule);
  border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}
.statcell{background:var(--paper);padding:20px 18px 18px;display:flex;flex-direction:column}
.statcell .n{font:400 clamp(32px,3.6vw,42px)/1 "IBM Plex Mono",ui-monospace,monospace;
  letter-spacing:-.025em;font-variant-numeric:tabular-nums;color:var(--ink)}
.statcell .l{margin-top:12px;font:500 10px "IBM Plex Mono",ui-monospace,monospace;
  letter-spacing:.15em;text-transform:uppercase;color:var(--ink-2)}
.statcell .s{margin-top:7px;font:italic 400 12.5px "Source Serif 4",Georgia,serif;color:var(--ink-3)}
/* the size step D-020 asks for on the ten-character cell; never a second rounding */
.statcell.wide .n{font-size:clamp(18px,2.6vw,34px)}
table{border-collapse:collapse;width:100%%;min-width:560px;
  font:400 14px/1.5 "IBM Plex Mono",ui-monospace,monospace}
.tab{font-variant-numeric:tabular-nums}
.prop{font-variant-numeric:proportional-nums}
th,td{text-align:right;padding:7px 12px;border-bottom:1px solid var(--rule)}
th:first-child,td:first-child{text-align:left}
th{font-weight:500;font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:var(--ink-2)}

/* ---- paper ---- */
.papercard{background:var(--surface);border:1px solid var(--rule);border-radius:2px;padding:26px 24px 22px;
  display:flex;flex-direction:column;gap:14px}
.paper-title{font:300 clamp(28px,4.4vw,40px)/1.04 "Zilla Slab",Georgia,serif;
  letter-spacing:-.018em;margin:0;text-wrap:balance;color:var(--ink)}
.byline{font:400 14px/1.5 "Source Sans 3","Helvetica Neue",Arial,sans-serif;color:var(--ink-2);
  max-width:62ch;margin:0}
.cite{font:400 16px/1.62 "Source Serif 4",Georgia,serif;color:var(--ink);max-width:62ch;margin:0}
.cite a{word-break:break-word}
.bib,.code{margin:0;overflow-x:auto;background:var(--sunk);border:1px solid var(--rule);border-radius:2px;
  padding:15px 17px;white-space:pre;color:var(--ink);
  font:400 13px/1.6 "IBM Plex Mono",ui-monospace,monospace}

/* ---- attributed quotation, DESIGN.md sect.8 ---- */
.abstract{margin:0;border-left:2px solid var(--rule-2);padding:3px 0 3px 20px;
  display:flex;flex-direction:column;gap:14px}
.abstract .q{font:400 16.5px/1.62 "Source Serif 4",Georgia,serif;color:var(--ink);
  max-width:62ch;margin:0}
.qsrc{font:italic 400 13px/1.5 "Source Serif 4",Georgia,serif;color:var(--ink-3);
  max-width:62ch;margin:0}
.qsrc a{word-break:break-word}
.reconcile{font:400 15px/1.6 "Source Sans 3","Helvetica Neue",Arial,sans-serif;
  color:var(--ink-2);max-width:62ch;margin:0}
.rules{margin:0;padding-left:22px;display:flex;flex-direction:column;gap:10px;
  max-width:70ch}
.rules li{font-size:15px;line-height:1.55;color:var(--ink-2)}
.rules li strong{color:var(--ink);font-weight:600}
.rules li code{color:var(--ink)}

/* ---- what is still open ---- */
.openlist{display:grid;grid-template-columns:minmax(112px,170px) 1fr;
  border-top:1px solid var(--rule);margin:0;max-width:none}
.openlist dt{font:500 10.5px "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.13em;
  text-transform:uppercase;color:var(--brass);padding:16px 20px 16px 0;
  border-bottom:1px solid var(--rule)}
.openlist dd{margin:0;padding:16px 0;border-bottom:1px solid var(--rule);
  font-size:15px;line-height:1.55;color:var(--ink-2)}
.openlist dd strong{color:var(--ink);font-weight:600}
@media (max-width:640px){
  .openlist{grid-template-columns:1fr}
  .openlist dt{border-bottom:0;padding:16px 0 3px}
  .openlist dd{padding-top:0}
}
.hr{height:1px;background:var(--rule);border:0;margin:0}

@media (max-width:900px){ .itiles{grid-template-columns:1fr} }
@media (max-width:760px){ .statrow{grid-template-columns:repeat(2,1fr)} }
@media (max-width:560px){ .statrow{grid-template-columns:1fr} }
@media (max-width:860px){ main section{padding:56px 0} .wrap{padding:0 22px}
  .themer .lb{display:none} }
@media (max-width:560px){ .brand .sep,.brand .pg{display:none} }
@media (max-width:420px){ .topbar .wrap{padding:0 14px;gap:10px} .brand{gap:8px}
  .brand .nm{font-size:17px}
  .seg button{padding:12px 7px;font-size:10px;letter-spacing:.04em} }
@media (prefers-reduced-motion: reduce){
  *,*::before,*::after{animation-duration:.001ms !important;animation-iteration-count:1 !important;
    transition-duration:.001ms !important;scroll-behavior:auto !important}
}
""" % {"TOKENS": TOKENS, "DARK": DARK}

SECTIONS = [
 ("icons","01","The twelve icons","24×24 grid, one sprite, on paper and on an ink band"),
 ("mark","02","The lattice mark","22px nav size, plus 44 and 16"),
 ("favicon","03","The favicon","16 / 32 / 64, and the true 16px raster"),
 ("coverage","04","The coverage section","Map, region strip, region totals — all three generated"),
 ("mad","05","The deviation figure","One bar on the 0–12 p.p. ruler, on paper and on ink"),
 ("type","06","The type specimen","Four faces at the §4 scale, and the totals band"),
 ("paper","07","The Papers page","The abstract quoted verbatim, the citation, BibTeX and the link"),
 ("open","08","What is still open","Four items; one of them blocks Phase 4"),
]
toc = "".join(
  f'<a href="#{i}"><span class="n">{n}</span><span class="t">{t}</span><span class="d">{d}</span></a>'
  for i,n,t,d in SECTIONS)

HTML = f"""<title>Instrument Set</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&amp;family=Source+Sans+3:wght@400;600&amp;family=Source+Serif+4:ital,wght@0,400;1,400&amp;family=Zilla+Slab:wght@300;400&amp;display=swap">
<style>{CSS}</style>

{sprite}

<header class="topbar">
  <div class="wrap">
    <span class="brand">{mark_at(22)}<span class="nm">Virtual Lab</span>
      <span class="sep">/</span><span class="pg">Asset review</span></span>
    <div class="themer">
      <span class="lb">Theme</span>
      <div class="seg" role="group" aria-label="Theme">
        <button type="button" data-set="light" aria-pressed="false">Light</button>
        <button type="button" data-set="dark" aria-pressed="false">Dark</button>
        <button type="button" data-set="system" aria-pressed="true">System</button>
      </div>
    </div>
  </div>
</header>

<main>

<section id="top">
  <div class="wrap stack loose">
    <div class="stack tight">
      <p class="eyebrow">Phase 3 &middot; 2026-08-21 &middot; review gate</p>
      <h1>The first assets, built against the design system</h1>
      <p class="sub">Six workstreams produced these. Nothing here is on the site yet.
        Approve or flag each group before the Phase 4 build starts.</p>
    </div>
    <div class="stack">
      <p>Every graphic below is inline SVG built from the four primitives &mdash; bar, tick,
        cell, bracket &mdash; and takes its colour from <code>DESIGN.md</code> &sect;3 tokens
        only, so all three theme states resolve from one drawing. Use the theme control in
        the bar above to check light, dark and unstamped (system) without changing your OS
        setting.</p>
      <p>Every figure carries its source line, as the provenance rule requires. Where a
        workstream could not follow the spec literally, the reason sits beside the thing
        rather than in a footnote, marked <span class="tag" style="margin:0">Flag</span>.
        Four of those are substantive and each is called out in its own section.</p>
      <p class="srcline">Fonts on this page load from the Google CDN, because the Artifact
        content-security policy permits no other font host. That is a constraint of this
        preview only: the site self-hosts all seven face+weight combinations from
        <code>fonts/</code> via <code>css/fonts.css</code> (D-012, <code>DESIGN.md</code> &sect;4).</p>
    </div>
    <div class="toc">{toc}</div>
  </div>
</section>

<section id="icons">
  <div class="wrap stack loose">
    <div class="hd">
      <p class="eyebrow">01 &middot; assets/icons/</p>
      <h2>The twelve icons</h2>
      <p>24&times;24 grid, 1.75px stroke, square caps, <code>stroke="currentColor"</code>.
        Every coordinate is a multiple of 0.5 and all content sits in an 18&times;18 optical
        box, so the outermost rendered pixel is 2.125 and nothing touches the viewBox edge.
        Two icons are exceptions and both are deliberate: Coverage is the cells icon and is
        filled, not stroked; Survey is the thread and carries the set's only round caps.</p>
    </div>

    <div class="ikey">
      <span>Each tile: 48px then 24px</span>
      <span><i style="background:var(--brass)"></i>--brass</span>
      <span><i style="background:var(--ink)"></i>--ink</span>
    </div>

    <div class="icons">{ICON_CARDS}</div>

    <p class="srcline"><code>assets/icons/*.svg</code> and the
      <code>&lt;symbol&gt;</code> sprite <code>assets/icons/icons.svg</code>, generated
      together by <code>scratchpad/build-icons.py</code>. Constructions quoted from
      <code>DESIGN.md</code> &sect;7. This page inlines the sprite and draws every icon
      above with <code>&lt;use href="#icon-&hellip;"&gt;</code> &mdash; cross-document
      <code>&lt;use&gt;</code> does not work in Chrome or Safari.</p>

    <div class="flag">
      <p class="hh">Flag &middot; a dot is not one of the four primitives</p>
      <p>&sect;7 specifies <strong>Weight</strong> as &ldquo;a rule with three <em>dots</em> of
        differing radius&rdquo; and <strong>Precision</strong> as &ldquo;two rules, <em>a centre
        dot</em>, two end ticks.&rdquo; A circle is not one of the four primitives, and
        <code>AGENTS.md</code> rule 8 is absolute about that. Drawn as circles, three stroked
        rings on a rule read as chain links at 24px. Both shipped with <strong>square
        cells</strong> instead &mdash; a primitive, and the same form the lattice is made of.</p>
      <p>Weight also could not keep the cells centred on the rule: eight variants were
        rendered at 24 and 56px and every centred one read as a bolt or a dart. The cells are
        seated on the rule, bottoms aligned.</p>
      <p>The proposed &sect;7 edits are in <code>scratchpad/ws-icons.md</code> and have not been
        written into <code>DESIGN.md</code>. The same note proposes that motif M3, written
        <code>&#9500;&mdash;&mdash;&#9679;&mdash;&mdash;&#9508;</code>, becomes
        <code>&#9500;&mdash;&mdash;&#9632;&mdash;&mdash;&#9508;</code> so the icon and the
        motif do not drift.</p>
    </div>

    <div class="ask">
      <p class="hh">What is being asked</p>
      <p>Approve the twelve as drawn, or flag individual icons. Two decisions need your
        answer either way: whether the &ldquo;dot&rdquo;&nbsp;&rarr;&nbsp;cell substitution is
        written into &sect;7, and whether M3's dot becomes a cell with it.</p>
    </div>
  </div>
</section>

<section class="band" style="border-top:0;padding:0">
  {lattice("latIcons", inv=True)}
  <div class="wrap stack loose">
    <div class="stack tight">
      <p class="eyebrow">01b &middot; the same twelve, on an ink band</p>
      <h3>Icons on an ink band</h3>
      <p style="max-width:70ch">An ink band is dark in <em>both</em> themes, so brass here is
        always <code>--brass-inv</code> <code>#C9A250</code> and never <code>--brass</code>:
        <code>--brass</code> on an ink band measures 2.43:1 in light mode and looks correct in
        dark. Navigation ink becomes <code>--on-invert</code>. Each tile: 48px then 24px in
        <code>--brass-inv</code>, then 48px then 24px in <code>--on-invert</code>.</p>
    </div>
    <div class="bstrip">{band_icons}</div>
    <p class="srcline">The same sprite, recoloured by <code>currentColor</code> only.
      Contrast pairs enforced by <code>scripts/check-contrast.py</code>
      (<code>DESIGN.md</code> &sect;3).</p>
  </div>
</section>

<section id="mark">
  <div class="wrap stack loose">
    <div class="hd">
      <p class="eyebrow">02 &middot; assets/mark.svg</p>
      <h2>The lattice mark</h2>
      <p>Nine cells, five at target, as &sect;8 specifies for the nav. Row&nbsp;0 filled,
        filled, ghost; row&nbsp;1 filled, ghost, filled; row&nbsp;2 ghost, filled, ghost.
        Every row and every column carries at least one filled cell and none is complete, so
        it reads as a design mid-field rather than as ornament, and it has no rotational
        symmetry. The four unfilled cells are drawn at <code>fill-opacity .28</code>.</p>
    </div>

    <div class="specrow">
      <div class="cellp"><span class="px">22px &middot; nav</span>{mark_at(22)}</div>
      <div class="cellp"><span class="px">44px</span>{mark_at(44)}</div>
      <div class="cellp"><span class="px">16px</span>{mark_at(16)}</div>
      <div class="cellp"><span class="px">22px &middot; --brass</span>{mark_at(22,"brass")}</div>
      <div class="celli"><span class="px">22px &middot; on ink</span>{mark_at(22)}</div>
      <div class="celli"><span class="px">16px &middot; --brass-inv</span>{mark_at(16,"brass")}</div>
    </div>

    <div class="stack tight">
      <p class="px">In context &mdash; nav at 66px, &sect;8</p>
      <div class="scroll">
        <div class="navsim">
          {mark_at(22)}<span class="nm">Virtual Lab</span>
          <span class="lk on" style="margin-left:26px">Method</span>
          <span class="lk">Studies</span><span class="lk">Paper</span><span class="lk">About</span>
        </div>
      </div>
    </div>

    <p class="srcline"><code>assets/mark.svg</code>, generated by
      <code>scratchpad/build-icons.py</code>. Motif M1, per <code>DESIGN.md</code> &sect;6 and
      the Nav component in &sect;8.</p>

    <div class="flag">
      <p class="hh">Flag &middot; the mark cannot use the M1 4:9 lattice ratio</p>
      <p>&sect;6 fixes the lattice at cell 8 / pitch 18 and says &ldquo;do not alter the
        ratio&rdquo;; &sect;6 lists the mark among M1's uses; &sect;8 sets the mark at 22px with
        nine cells. The three are not jointly satisfiable at a legible size. Nine cells at 4:9
        in a 22px box gives cell&nbsp;4, pitch&nbsp;9 &mdash; which lands on 22 exactly, and is
        almost certainly why 22px was chosen &mdash; but renders as a scatter of 4px dots lost
        in whitespace, and disappears at 16px.</p>
      <p>Shipped at <strong>cell 6, pitch 8</strong> (3:4), which also lands exactly on 22 and
        holds down to 12px. The proposed distinction: 4:9 is a <em>tiling</em> ratio governing
        the lattice as a background field, where the cells must disappear at a glance; the mark
        is nine discrete cells that must survive at 16px. This is question 2 of the open
        decision D-021, and it now has a rendering behind it. Five variants at 16 / 22 / 44px
        are in <code>scratchpad/mark-variants.html</code>.</p>
    </div>

    <div class="ask">
      <p class="hh">What is being asked</p>
      <p>Approve cell 6 / pitch 8 for the mark, or send it back to 4:9 and accept the 16px
        loss. Approving also settles D-021 question 2.</p>
    </div>
  </div>
</section>

<section id="favicon">
  <div class="wrap stack loose">
    <div class="hd">
      <p class="eyebrow">03 &middot; assets/favicon.svg</p>
      <h2>The favicon</h2>
      <p>Motif M2 &mdash; bar and target tick &mdash; on an ink tile with the 2px radius. The
        top bar reaches the tick and is <code>--data-inv</code>; the bottom bar stops short and
        is <code>--brass-inv</code>. This is the one asset in the set that contains literal
        hex values, and every one of them is a token whose value is identical in both themes
        (<code>--invert</code>, <code>--on-invert</code>, <code>--data-inv</code>,
        <code>--brass-inv</code>). A favicon has no theme context to inherit, so no media
        query is wanted.</p>
    </div>

    <div class="specrow">
      <div class="cellp"><span class="px">64px</span>{fav_at(64)}</div>
      <div class="cellp"><span class="px">32px</span>{fav_at(32)}</div>
      <div class="cellp"><span class="px">16px &middot; tab size</span>{fav_at(16)}</div>
      <div class="celli"><span class="px">on ink, 32px</span>{fav_at(32)}</div>
    </div>

    <div class="stack tight">
      <p class="px">The true rasters, shown at 9&times; nearest-neighbour</p>
      <div class="raster">
        <figure><img src="{ICO16}" width="144" height="144" alt="The 16-pixel favicon raster, magnified nine times"><figcaption class="px">16px</figcaption></figure>
        <figure><img src="{ICO32}" width="288" height="288" alt="The 32-pixel favicon raster, magnified nine times"><figcaption class="px">32px</figcaption></figure>
        <figure><img src="{ICO48}" width="432" height="432" alt="The 48-pixel favicon raster, magnified nine times"><figcaption class="px">48px</figcaption></figure>
      </div>
    </div>

    <p class="srcline"><code>assets/favicon.svg</code>, rasterised with
      <code>rsvg-convert</code> and packed into <code>assets/favicon.ico</code> at 16 / 32 / 48;
      <code>assets/apple-touch-icon.png</code> is the same drawing at 180px, square and opaque,
      because iOS applies its own mask. These three magnified images are the only raster
      content on this page.</p>

    <div class="flag">
      <p class="hh">Flag &middot; M2's hatch does not exist at favicon size</p>
      <p>&sect;6 M2 requires under-target to be hatched brass <em>and</em> brass-hued, so state
        survives greyscale and colour-blind reading. At 16px a 3px-period 135&deg; hatch is
        sub-pixel: it renders as flat brass at best and as mud at worst. The favicon keeps the
        redundancy through a different second channel &mdash; the under-target bar is brass
        <em>and</em> stops visibly short of the tick, while the on-target bar reaches it.
        Length is the encoding M2 is actually about. Checked by rasterising to true 16px and
        inspecting at 9&times;, which is the row above.</p>
      <p>Proposed &sect;6 M2 edit: &ldquo;Below ~24px the hatch is dropped; state is carried by
        hue and by the bar's length against the tick.&rdquo;</p>
    </div>

    <div class="ask">
      <p class="hh">What is being asked</p>
      <p>Approve the favicon and the hatch exception, or flag it. If you approve, &sect;6 M2
        needs the sentence above.</p>
    </div>
  </div>
</section>

<section id="coverage">
  <div class="wrap stack loose">
    <div class="hd">
      <p class="eyebrow">04 &middot; build/, from scripts/build-coverage-map.py</p>
      <h2>The coverage section</h2>
      <p>Three artefacts, built together in one run from
        <code>scripts/data/coverage.json</code>: the cropped choropleth, the region strip and
        the region totals. Every colour is a <code>var(--&hellip;)</code> &mdash; there is no
        literal hex anywhere in the emitted markup &mdash; so all three inherit this page's
        theme. No number changed in the rebuild; what changed is that the numbers are now
        computed rather than typed.</p>
    </div>

    <div class="stack tight">
      <p class="px">1 &middot; Map &mdash; cropped choropleth, six-state legend (D-018)</p>
      <div class="scroll">{cov_map}</div>
    </div>

    <div class="stack tight">
      <p class="px">2 &middot; Region strip &mdash; M2 without a target tick</p>
      <div class="scroll">{cov_strip}</div>
    </div>

    <div class="stack tight">
      <p class="px">3 &middot; Region totals &mdash; the stat row at region scale</p>
      <div class="scroll">{cov_reg}</div>
    </div>

    <div class="flag">
      <p class="hh">Flag &middot; the legend labels in the published record were wrong</p>
      <p>The record read <code>under 1,000 &middot; 1,000+ &middot; 10,000+ &middot; 50,000+
        &middot; 100,000+</code>. The code that fills the map has always been
        <code>int(log10(v))</code> clamped to 1&ndash;5, so the true steps are
        <code>under 100 &middot; 100+ &middot; 1,000+ &middot; 10,000+ &middot; 100,000+</code>
        &mdash; wrong by an order of magnitude. Under the old labels Germany (23) and Ireland
        (206) sat in one bucket labelled &ldquo;under 1,000&rdquo; at two different opacities,
        and every country from 1,000 to 9,999 &mdash; twenty of the forty-one, the largest
        bucket &mdash; was labelled &ldquo;10,000+&rdquo;. The labels are now generated from the
        same function that picks the opacity, so they cannot drift again. This is the one place
        where the rebuild does not match the record, because the record was wrong.</p>
      <p>A second correction: the strip's old source line put the 103,052 unattributed
        respondents next to the four countries covered but not counted, which invited the
        reading that Palestine, Moldova, North Macedonia and Kosovo account for 103,052 people.
        Each gap is now named separately, and each of the three source lines states its own
        denominator.</p>
    </div>

    <div class="flag">
      <p class="hh">Placement &middot; settled in D-019, and it decides the ground</p>
      <p>The section lives on <strong>Home, on paper ground</strong>, and the Studies index
        carries no map. It is never an ink band, because <strong>Home is already at the
        two-band limit</strong> &sect;8 sets &mdash; the validation section and the footer &mdash;
        and they sit at positions 4 and 9 with four sections between them, so the
        &ldquo;never adjacent&rdquo; rule holds. That is why all three artefacts above are
        drawn on paper here and have no <code>.inv</code> variant in this set. The band and
        the map must not restate each other either: the totals band answers <em>how much</em>,
        the map answers <em>where</em>, so the coverage lede drops the country count, the start
        date and the field window the band has already stated.</p>
    </div>

    <div class="ask">
      <p class="hh">What is being asked</p>
      <p>Approve all three as the coverage section, or flag. Two open items sit underneath and
        neither blocks the build: D-022, whether the strip should draw the 103,052
        unattributed respondents as a ghost segment rather than naming them only in the source
        line &mdash; the workstream recommends leaving it as built &mdash; and whether the six
        regional totals get a register row at all. Both are in the list at the end.</p>
    </div>
  </div>
</section>

<section id="mad">
  <div class="wrap stack loose">
    <div class="hd">
      <p class="eyebrow">05 &middot; assets/figures/mad-comparison.svg</p>
      <h2>The deviation figure</h2>
      <p>One bar on a 0&ndash;12&nbsp;p.p. ruler: our own mean absolute deviation from
        gold-standard benchmarks, in <code>--data</code>, with an M4 tick rule carrying the
        graduations and <strong>zero labelled as the benchmark</strong>. The figure resolves
        its own colours from tokens through local custom properties, and the
        <code>.inv</code> class swaps every one of them for its ink-band counterpart, so one
        drawing serves both grounds. Re-inlined from disk for this page &mdash; the file is
        the one <code>CONTENT.md</code> Home &sect;4 specifies.</p>
    </div>

    <figure class="figcard">
      <p class="cap">On paper &mdash; --data, --ink-2, --rule</p>
      {mad}
    </figure>

    <p class="srcline"><code>assets/figures/mad-comparison.svg</code>. The value is C-003 in
      <code>CLAIMS.md</code>, <code>VERIFIED</code>: 6.1&nbsp;p.p., post-stratification
      weighted, against GSS 2024, CPS 2024 and Pew 2023, from Donati &amp; Rao, 2025. The
      1,500-person sample in the figure's own source line is C-005, also
      <code>VERIFIED</code>. The figure carries its source line inside the drawing, as the
      provenance rule requires. Four GSS items are drawn from the 2022 wave, where the 2024
      wave did not field them; <code>CONTENT.md</code> Home &sect;4 is now the only place
      that footnote can live, in prose beneath the figure.</p>

    <div class="flag">
      <p class="hh">Note &middot; redrawn 2026-08-20, and the ruler deliberately did not move</p>
      <p>Under D-023 the site makes no comparative claim against another recruitment source,
        so this figure carries <strong>C-003 alone</strong> &mdash; what we deviate from
        benchmarks we did not choose after the fact. <strong>The scale is unchanged:</strong>
        still 0&ndash;12&nbsp;p.p. at 32px per point, so the axis was not retuned around a
        single value, and the drawing records that in a comment. Zero is labelled
        <code>0 &mdash; BENCHMARK</code>, which is what lets one bar be read at all: the
        reader sees the size of the deviation rather than being told it is small.</p>
    </div>

    <div class="flag">
      <p class="hh">Note &middot; this figure is deliberately not motif M3</p>
      <p>Every edition of the manuscript was searched for standard errors, confidence
        intervals, error bars, bootstraps and p-values on any MAD: zero hits. &sect;6 M3 says
        the interval &ldquo;appears only where a real interval exists. Decorative use would be
        a lie,&rdquo; so M3 is prohibited here. No tick sits inside the bar either &mdash;
        M2's tick means <em>target</em>, and a deviation has no target, so borrowing that form
        would repeat the same lie in a different vocabulary. A real scale with a real ruler is
        what is left, and it is all the figure claims. <code>CONTENT.md</code> Home &sect;4
        now says the same; the correction this workstream asked for has landed.</p>
    </div>
  </div>
</section>

<section class="band" style="border-top:0;padding:0">
  {lattice("latMad", inv=True)}
  <div class="wrap stack loose">
    <div class="stack tight">
      <p class="eyebrow">05b &middot; the same figure, on an ink band</p>
      <h3>The deviation figure, ink-band variant</h3>
      <p style="max-width:70ch">Adding <code>.inv</code> swaps <code>--data</code> for
        <code>--data-inv</code>, <code>--ink-3</code> for <code>--on-invert-2</code>, and
        <code>--rule</code> for <code>--rule-invert</code>. Both substitutions are contrast
        fixes, not taste: <code>--data</code> on a light-mode ink band measures 2.10:1, worse
        than the brass failure, and an <code>--ink-3</code> source line there measures 4.00:1.
        This is the ground the figure actually ships on &mdash; Home &sect;4 is one of Home's
        two ink bands.</p>
    </div>
    <figure class="figcard">
      <p class="cap">On an ink band &mdash; --data-inv, --on-invert-2, --rule-invert</p>
      {mad_inv}
    </figure>
    <div class="ask">
      <p class="hh">What is being asked</p>
      <p>Approve the figure on both grounds, or flag. Confirm you are content that it ships
        without intervals, and that a single bar with the benchmark at zero is enough to
        carry the validation section.</p>
    </div>
  </div>
</section>

<section id="type">
  <div class="wrap stack loose">
    <div class="hd">
      <p class="eyebrow">06 &middot; fonts/ + css/fonts.css</p>
      <h2>The type specimen</h2>
      <p>Four faces, each with one job, at the &sect;4 scale. Zilla Slab 300 for display,
        Source Sans 3 for interface and body, Source Serif 4 for abstracts and long-form
        method prose, IBM Plex Mono for every numeral, eyebrow and label. The kit is twelve
        woff2 files, latin and latin-ext, 264.6&nbsp;kB in total, of which 127.4&nbsp;kB is the
        latin half that a normal English page actually fetches.</p>
    </div>

    <div class="tspec">
      <p class="spec">Zilla Slab 300 &middot; h1 &middot; clamp(42px, 6vw, 70px)/1.02 &middot; ls &minus;.018em</p>
      <p style="font:300 clamp(42px,6vw,70px)/1.02 'Zilla Slab',Georgia,serif;letter-spacing:-.018em;text-wrap:balance;max-width:none">Fieldwork at the edge of the sample frame</p>
    </div>
    <div class="tspec">
      <p class="spec">Zilla Slab 300 &middot; h2 &middot; clamp(28px, 3.6vw, 42px)/1.10 &middot; ls &minus;.012em</p>
      <p style="font:300 clamp(28px,3.6vw,42px)/1.10 'Zilla Slab',Georgia,serif;letter-spacing:-.012em;text-wrap:balance;max-width:none">Who did we actually reach, and how do we know</p>
    </div>
    <div class="tspec">
      <p class="spec">Zilla Slab 400 &middot; h3 &middot; 20px/1.30 &middot; latin-ext below</p>
      <p style="font:400 20px/1.30 'Zilla Slab',Georgia,serif;max-width:none">Recruitment, weighting, and the cost of a completed interview</p>
      <p style="font:400 20px/1.30 'Zilla Slab',Georgia,serif;color:var(--ink-2);max-width:none">&#272;&#7863;ng Th&#7883; Ng&#7885;c &mdash; K&auml;rnten, &#321;&oacute;d&#378;, &#478; &#417; &#560; &#7835;</p>
    </div>
    <div class="tspec">
      <p class="spec">Source Sans 3 400 &middot; body &middot; 16.5px/1.6 &middot; measure capped at 65ch</p>
      <p>A survey is only as good as the account it can give of itself. The instrument records
        who was invited, who arrived, who finished, and what each of those cost &mdash; and the
        record travels with the estimate rather than sitting in an appendix nobody opens. Where
        a figure cannot be traced, the field is left empty on purpose.</p>
      <p style="color:var(--ink-2);font-size:14px">latin-ext &middot; Krak&oacute;w, &Aring;ngstr&ouml;m, Ca&ntilde;&oacute;n, &#486;&#491;&#273;, &#514;&#519;&#523;, &#7838;, &#8378; &#8380; &#8358; &#8353;</p>
    </div>
    <div class="tspec">
      <p class="spec">Source Sans 3 600 &middot; buttons, emphasis</p>
      <p class="sans600">Read the method note &middot; See where we have fielded &middot; Talk to us</p>
    </div>
    <div class="tspec">
      <p class="spec">Source Serif 4 400 &middot; abstracts and long-form method prose &middot; measure capped at 62ch</p>
      <p class="serifprose">We describe a recruitment procedure that draws respondents through
        advertising inventory, and we measure how far the resulting sample sits from
        gold-standard benchmarks it was not fitted to. The target distribution is declared
        before fielding, budget is reallocated between strata while recruitment runs, and every
        deviation that remains is reported rather than absorbed into a weight.</p>
      <p class="spec">Specimen prose, written for glyph fitting. It is not site copy and makes no claim.</p>
    </div>
    <div class="tspec">
      <p class="spec">IBM Plex Mono 400 &middot; table cells, code &middot; and 500 &middot; eyebrows, labels</p>
      <p class="mono400">country_code &middot; field_window_days &middot; completes &middot; cost_per_complete</p>
      <p class="mono500">RESPONDENTS &middot; SURVEY RESPONSES &middot; COUNTRIES &middot; STUDIES FIELDED</p>
    </div>

    <div class="stack tight">
      <p class="px">Tabular numerals in the totals band &mdash; the four D-020 cells, each with its source</p>
      <div class="statrow">
        <div class="statcell"><span class="n">841,660</span><span class="l">Respondents</span>
          <span class="s">Virtual Lab production data, August 2026 &middot; C-010</span></div>
        <div class="statcell wide"><span class="n">17,979,910</span><span class="l">Survey responses</span>
          <span class="s">Virtual Lab production data, August 2026 &middot; C-016</span></div>
        <div class="statcell"><span class="n">41</span><span class="l">Countries</span>
          <span class="s">Virtual Lab production data, August 2026 &middot; C-017, a floor</span></div>
        <div class="statcell"><span class="n">175</span><span class="l">Studies fielded</span>
          <span class="s">Virtual Lab production data, August 2026 &middot; C-019</span></div>
      </div>
      <p class="spec">Plex Mono 400 at clamp(32px, 3.6vw, 42px), tabular, four cells with 1px
        gaps over <code>--rule</code>, each carrying a mandatory Source Serif italic source
        line (&sect;8). The figures are C-010, C-016, C-017 and C-019, all
        <code>VERIFIED</code>. The country count is a floor: the extraction takes the first
        match per row and undercounts multi-country studies. Three rules bind this row &mdash;
        &ldquo;respondents&rdquo; and never &ldquo;people reached&rdquo;; the source is the
        production database and its date and never Donati &amp; Rao, which sources validation
        and nothing else; and 175 is never explained.</p>
      <p class="spec"><strong>17,979,910 takes a size step of its own, not a rounding.</strong>
        Ten characters at 42px will not fit the cell, and &ldquo;18M&rdquo; would be a second
        rounding of one figure &mdash; the exact number is the argument. That one cell runs at
        clamp(18px, 2.6vw, 34px); the other three keep the &sect;8 size.</p>
      <p class="spec"><strong>The median field window is not a cell.</strong> C-011 is
        <code>VERIFIED</code> at nineteen days actual against fourteen planned, and D-020 gave
        the fourth cell to the study count, so it sits in the prose beside the band with the
        start date (C-018): <em>Operating since February 2020. Half of our studies field in
        under three weeks &mdash; the median window from first to last recruitment report is
        nineteen days. Virtual Lab production data, August 2026. Field window n=116.</em></p>
    </div>

    <div class="stack tight">
      <p class="px">Why &sect;4 requires tabular numerals on every numeral</p>
      <div class="scroll">
        <table>
          <tr><th>row</th><th>tabular</th><th>tabular</th><th class="prop">proportional</th></tr>
          <tr><td>a</td><td class="tab">1,111,111</td><td class="tab">10.00</td><td class="prop">1,111,111</td></tr>
          <tr><td>b</td><td class="tab">4,206,913</td><td class="tab">&minus;0.45</td><td class="prop">4,206,913</td></tr>
          <tr><td>c</td><td class="tab">88,240,516</td><td class="tab">9.87</td><td class="prop">88,240,516</td></tr>
          <tr><td>d</td><td class="tab">&mdash;</td><td class="tab">&mdash;</td><td class="prop">&mdash;</td></tr>
        </table>
      </div>
      <p class="spec">The right-hand column is the same digits without
        <code>tabular-nums</code>; the decimals drift. <strong>These digits are glyph-fitting
        specimens, not figures.</strong> They carry no source and must never be copied to a
        page; they are also chosen so that none of them collides with a value the register
        withholds. Row d shows the <code>&mdash;</code> that stands in for a value we do not have.</p>
    </div>

    <div class="stack tight">
      <p class="px">The kit, one line each</p>
      <p class="big" style="font-family:'Zilla Slab',Georgia,serif;font-weight:300">Zilla Slab 300 &mdash; Handgloves 0123456789</p>
      <p class="big" style="font-family:'Zilla Slab',Georgia,serif;font-weight:400">Zilla Slab 400 &mdash; Handgloves 0123456789</p>
      <p class="big" style="font-family:'Source Sans 3','Helvetica Neue',Arial,sans-serif;font-weight:400">Source Sans 3 400 &mdash; Handgloves 0123456789</p>
      <p class="big" style="font-family:'Source Sans 3','Helvetica Neue',Arial,sans-serif;font-weight:600">Source Sans 3 600 &mdash; Handgloves 0123456789</p>
      <p class="big" style="font-family:'Source Serif 4',Georgia,serif;font-weight:400">Source Serif 4 400 &mdash; Handgloves 0123456789</p>
      <p class="big" style="font-family:'IBM Plex Mono',ui-monospace,monospace;font-weight:400">IBM Plex Mono 400 &mdash; Handgloves 0123456789</p>
      <p class="big" style="font-family:'IBM Plex Mono',ui-monospace,monospace;font-weight:500">IBM Plex Mono 500 &mdash; Handgloves 0123456789</p>
    </div>

    <p class="srcline"><code>fonts/</code> and <code>css/fonts.css</code>, per D-012 and
      <code>DESIGN.md</code> &sect;4. Source Sans 3 is published by Google only as a variable
      font: one file per subset carries both 400 and 600, which is also the smaller option. If
      600 renders identically to 400 above, the variation axis is not being applied.</p>

    <div class="flag">
      <p class="hh">Note &middot; this preview is the documented exception, not the spec</p>
      <p>&sect;4 says never to link a <code>fonts.googleapis.com</code> stylesheet from a page,
        because a German court held in January 2022 that embedding Google Fonts transmits
        visitor IP addresses to a US server without consent. We sell to EU institutions and our
        own privacy policy states EU hosting. The Artifact CSP permits no other font host, so
        this preview uses the CDN and the site does not. One open point in &sect;4 is unrelated
        to hosting: Georgia now backs both Zilla Slab and Source Serif 4, so a page that loses
        both webfonts loses the display/prose contrast between them.</p>
    </div>

    <div class="ask">
      <p class="hh">What is being asked</p>
      <p>Approve the four faces and seven weights as the shipped kit, or flag. Nothing here
        adds a face or a weight to &sect;4.</p>
    </div>
  </div>
</section>

<section id="paper">
  <div class="wrap stack loose">
    <div class="hd">
      <p class="eyebrow">07 &middot; the Papers page</p>
      <h2>The abstract, quoted</h2>
      <p><strong>D-016 was reversed on 2026-08-21 and the abstract is back.</strong> The page
        is title &middot; authors and affiliations &middot; <strong>the abstract reproduced
        verbatim as attributed quotation</strong> &middot; the citation &middot; BibTeX
        &middot; a link to what a reader can open. No cost table, no figures. The card below
        is the whole page. Everything after it is about one attribute, because Papers is the
        only page on the site that will ever carry it.</p>
      <p>The reasoning is a distinction, not an exception. <strong>A quotation is attributed
        speech, not a claim.</strong> <code>CLAIMS.md</code> governs what Virtual Lab
        asserts; reproducing what the paper says, accurately, is the opposite of
        overclaiming &mdash; and a citation page that silently edited its own paper's
        abstract would be the worse failure by some distance. Nothing is laundered by this:
        every withheld figure stays withheld in every sentence the site writes in its own
        voice, which is every sentence on the site except one quoted paragraph.</p>
    </div>

    <div class="papercard">
      <p class="eyebrow">Paper</p>
      <h3 class="paper-title">{html.escape(title)}</h3>
      <p class="byline">{byline}</p>
      <hr class="hr">
      <p class="px">Abstract, reproduced verbatim</p>
      <blockquote class="abstract" data-claim-quote="C-055">
        <p class="q">{abstract}</p>
        <p class="qsrc" data-claim-source>Abstract, quoted verbatim. Donati &amp; Rao, 2025.
          <a href="{paper_url}">{paper_url}</a></p>
      </blockquote>
      <p class="reconcile">The abstract describes the thirty-three studies analysed in the
        paper. Our operating history is larger, and is reported on the Studies index.</p>
      <hr class="hr">
      <p class="px">Cite as</p>
      <p class="cite">Donati, D. and Rao, N. (2025). <em>{html.escape(title)}.</em>
        Working paper. <a href="{paper_url}">{paper_url}</a></p>
      <hr class="hr">
      <p class="px">BibTeX</p>
      <pre class="bib">{bibtex}</pre>
      <hr class="hr">
      <p class="px">Read it</p>
      <p class="cite"><a href="{paper_url}">{paper_url}</a> &mdash; SSRN</p>
      <p class="spec">Zilla Slab 300 for the title, Source Sans 3 for the byline, Source
        Serif 4 at ~62ch for the abstract and the citation, Plex Mono 400 for the BibTeX
        block, which scrolls in its own container.</p>
    </div>

    <p class="srcline">Title and byline read from <code>_data/paper.json</code>. The abstract
      is <strong>copied programmatically from <code>abstract.verbatim</code></strong> in that
      same file &mdash; the field the paper workstream mined from the manuscript &mdash; with
      nothing between the JSON and the page but HTML escaping, so this page cannot drift from
      the record and no hand ever retypes it. It is read from the <code>{abs_edition}</code>
      edition and is identical in all {abs_identical} editions the file records it in. Two
      things in it are deliberately not corrected: the grammatical error in the source, the
      phrase &ldquo;a mean absolute deviations&rdquo;, recorded under
      <code>abstract.verbatim_warnings</code>; and the figure flagged below. Fixing either
      would be a paraphrase in the one place a paraphrase is invisible.</p>

    <div class="stack">
      <p class="px">The markup is the mechanism</p>
      <p>Papers is the only place on the site that will carry
        <code>data-claim-quote</code>, so this is where a reader learns what it does. The
        container above is built exactly like this, and the clause after it is deliberately
        outside the container:</p>
      <pre class="code">{markup}</pre>
      <p><code>python3 scripts/check-claims.py</code> enforces three constraints on that
        container, and enforces them rather than describing them:</p>
      <ol class="rules">
        <li><strong>It must name a <code>VERIFIED</code> <code>CLAIMS.md</code> row for the
          document being quoted.</strong> Here that is C-055, the paper's public URL. Not
          nothing, not a free-text string like <code>"the paper"</code>, not a withheld row
          &mdash; a quotation is attributed to something or it is not a quotation.</li>
        <li><strong>It must carry a visible attribution line</strong>, checked exactly as a
          figure's source line is: same visual unit, same rule. That is the italic line
          beneath the paragraph in the card above.</li>
        <li><strong>Every withheld value it shields is reported at <code>warn</code> level on
          every run</strong>, naming the value and the row that withholds it. <strong>The
          shield stops a build failing; it never stops a human seeing.</strong></li>
      </ol>
      <p>The exemption belongs to the <em>container</em>, which is why paraphrase inside one
        is not quotation and the checker cannot tell the difference &mdash; anything written
        inside inherits a shield it did not earn. Quote, or write outside the block; there is
        no third option, and the block stays small enough that a human can read the whole of
        it. <strong>Expect this attribute exactly once on the whole site. A second use is a
        signal to stop and ask, not a pattern to copy</strong> &mdash; a second page wanting
        to quote a source is a content decision before it is a markup decision, because the
        interesting question is never whether the markup validates.</p>
      <p class="srcline">Worked pair in <code>scripts/fixtures/</code>:
        <code>quote-abstract.html</code> is this block, expected to exit 0 with one warn, and
        <code>fail-quote-unattributed.html</code> is the same attribute used as a loophole in
        three shapes, expected to exit 1. Both run under <code>python3
        scripts/test-check-claims.py</code>, which passes all nine cases today.</p>
      <p class="srcline"><strong>Run against the card above, the checker behaves exactly as
        described.</strong> It skips the shielded numerals as quoted from C-055, reports the
        withheld cost figure at <code>warn</code> naming C-004 as the row that withholds it,
        and accepts the attribution line. <strong>It also surfaces one thing this card still
        gets wrong, and it is not the quotation:</strong> the BibTeX block carries no
        <code>data-claim</code> and no source line in its own unit, so it fails as an
        unannotated numeral. That is pre-existing and needs an annotation decision before
        Papers ships. <code>data-claim="C-055"</code> is <em>not</em> the answer &mdash; the
        entry carries the citation year as well as the URL id, and the checker correctly
        refuses a row whose permitted value is only the id.</p>
    </div>

    <div class="stack">
      <p class="px">One clause, outside the quotation</p>
      <p>The abstract counts the studies analysed in the paper. The Studies index counts our
        operating history, which is larger &mdash; C-019 and C-017, both
        <code>VERIFIED</code>. Both are true, of different populations, and a reader who
        meets the smaller pair first must not be left to reconcile them. One clause does it,
        in our own voice, immediately beneath the block. It is set in Source Sans against the
        abstract's Source Serif, so the change of voice is visible before it is read.</p>
      <p><strong>The placement is the whole point.</strong> Editing the abstract to fix a
        problem of ours is exactly what verbatim forbids, and a clause of ours inside the
        block would inherit a shield it did not earn. <strong>The count is spelled in
        words</strong> &mdash; a bare numeral outside the block would be read as our figure,
        and it is the paper's.</p>
    </div>

    <div class="flag">
      <p class="hh">Flag &middot; the quotation states a figure C-004 withholds</p>
      <p>The abstract states a cost per question per respondent. <strong>C-004 is
        <code>WITHHELD</code></strong>: the source contradicts itself &mdash; the abstract and
        the paper's own cost table compute different values &mdash; and the resolution was to
        publish neither <em>in our own voice</em>. So it appears on this page once, as the
        authors' sentence inside their abstract, and nowhere else. <strong>It looks like a
        violation until you know the mechanism</strong>, which is why it is flagged here
        rather than left in a document nobody opens. The figure is not printed anywhere
        outside the block on this page, including in this paragraph.</p>
      <p>What it does not license: <strong>the cost table stays off, permanently.</strong>
        Every row of it is denominated per question &mdash; ours, GSS traditional, GSS
        Follow-on, Prolific &mdash; so reproducing it publishes the withheld figure four times
        over, in a component whose entire job is to display values. That is not quotation;
        that is publishing the figure with the paper cited as an excuse. The abstract states
        it once, in a sentence about deployability, inside an argument its authors are making.
        The test, if the distinction ever blurs: <em>would a reader take this as the paper's
        sentence, or as our number?</em> The cost conversation lives on Method, in
        per-participant units (C-014).</p>
    </div>

    <div class="flag">
      <p class="hh">Flag &middot; the quotation compares, and D-023 says the site does not</p>
      <p>The abstract names Prolific and LLM-based digital twins and reports the method
        improving &ldquo;on both&rdquo;. That is C-006 and C-007, <code>WITHHELD</code> under
        D-023 &mdash; <strong>the site makes no comparative claim against another recruitment
        source.</strong> Shown that sentence on 2026-08-21 and asked directly, Nandan chose to
        keep the quotation whole: <em>&ldquo;keep it &mdash; quotation is quotation.&rdquo;</em>
        D-023 now carries an <strong>in our own voice</strong> qualifier recording it. That is
        a correction to the decision's premise, not a softening of it &mdash; D-023 was
        settled on the understanding that no comparison would appear anywhere on the site,
        and that stopped being true the moment the abstract came back. A settled decision
        resting on a false premise is how it gets reopened by whoever spots the contradiction
        before they find the paragraph.</p>
      <p>The boundary is hard: <strong>quoted only.</strong> Never pulled out of the block,
        never restated in a heading, never summarised beneath it, never repeated in our own
        copy, never used to justify a comparative claim elsewhere. If any of that starts
        happening, the abstract is being mined for claims rather than reproduced, and the
        answer is to reopen D-016, not to trim the quotation. This flag names the sentence
        rather than restating it, on that same rule.</p>
      <p>Worth recording, because it is the opposite of self-serving: the comparison the
        abstract carries is the manuscript's, and the authors' own later analysis walks it
        back &mdash; which is the reason D-023 exists at all. We are not endorsing it; we are
        quoting a document a reader can open for themselves, which is the point of a citation
        page.</p>
    </div>

    <div class="flag">
      <p class="hh">Flag &middot; what this page must not say, and one question it cannot answer</p>
      <p><strong>No posted date, no revision date, no page count, no SSRN version number, no
        DOI.</strong> None of them has been seen from here, and writing one down would be
        inventing a figure &mdash; the exact failure the register exists to prevent. The URL
        is C-055, <code>VERIFIED</code> on the author's word: Nandan Rao supplied it as a
        co-author, and <strong>nobody here has read the SSRN landing page</strong> &mdash;
        SSRN sits behind Cloudflare and returns 403 to any non-browser client. If the link
        ever 404s, the fix is to ask the author, not to search for a replacement id.</p>
      <p>The BibTeX entry is <strong>constructed, not found</strong>: no entry for this paper
        exists in either <code>.bib</code> tree in the paper repository. It is
        <code>@misc</code> with <code>howpublished = {{Working paper}}</code> because the
        manuscript is JMR-25-0847, under a major revision, so no journal, volume, number or
        page range may be named.</p>
      <p><strong>Which edition is actually on SSRN?</strong> The only compiled PDF in the
        paper repository is the JMR submission, which is <em>blinded and carries no
        byline</em>. If that is what was uploaded, a reader clicking through from this page
        gets an author-less document directly beneath the byline printed above it.
        <code>SSRN_09152025.tex</code> is the bylined edition and is what should be there.
        Ten seconds for you, unanswerable from here. And the <code>Jul2026</code> working
        manuscript may not be published at all &mdash; it is a live revision responding to
        reviewers, and it is the edition this abstract was read from.</p>
    </div>

    <div class="ask">
      <p class="hh">What is being asked</p>
      <p>Approve the page as it stands above &mdash; the quotation whole, the clause outside
        it, the citation, the BibTeX and the link &mdash; or flag. The question D-016 was
        reopened on is answered by the restoration itself: with the abstract back, Papers is
        no longer five lines, and it has left the list in section 08. Folding it into Method
        is still yours to want; nothing waits on it. The live question here is the SSRN
        edition, flagged above.</p>
    </div>
  </div>
</section>

<section id="open">
  <div class="wrap stack loose">
    <div class="hd">
      <p class="eyebrow">08 &middot; DECISIONS.md, open</p>
      <h2>What is still open</h2>
      <p>Everything below is yours and nobody else's. Only the first one blocks the Phase 4
        build; the rest can be answered while it runs, and each has a recorded fallback.</p>
    </div>

    <dl class="openlist">
      <dt>D-014</dt>
      <dd><strong>Which client marks are cleared for logo use.</strong> The only thing
        blocking Phase 4. World Bank, UNICEF, Gavi and EFSA typically need written
        permission; Columbia, GWU, Truth Initiative and Shujaaz are lower risk but
        unconfirmed. The wall is built to degrade &mdash; cleared marks render as logos,
        uncleared ones stay as type in the same grid.</dd>

      <dt>D-021</dt>
      <dd><strong>Two motif rules the coverage and icon work exposed.</strong> Does M2
        require a real target, scoped to figures rather than icons? And does the M1 lattice
        ratio hold at every scale &mdash; the mark ships at cell&nbsp;6 / pitch&nbsp;8, which
        &sect;6 does not sanction. Section 02 has the rendering.</dd>

      <dt>D-022</dt>
      <dd><strong>Whether the region strip draws the unattributed respondents as a ghost
        segment.</strong> 103,052 of 841,660 belong to studies whose strata carry no country
        tag; today the strip spans the 738,608 that are attributable and names the gap in its
        source line. <em>C-010 and the per-country table in <code>CLAIMS.md</code>, both
        <code>VERIFIED</code>; Virtual Lab production data, August 2026.</em> The workstream
        recommends leaving it as built.</dd>

      <dt>Region buckets</dt>
      <dd><strong>Whether the six regional totals get a <code>CLAIMS.md</code> row.</strong>
        They are sums of the verified per-country table, but the <em>bucketing</em> is an
        editorial choice in <code>coverage.json</code>, not a database fact &mdash; the MENA
        bucket includes Israel, and that grouping reads as a statement. Not a Phase 4 blocker:
        the fallback is that the section ships with the map, the strip and country figures,
        and drops the regional layer.</dd>

    </dl>

    <p class="srcline"><strong>D-016 has left this list.</strong> It was here as
      &ldquo;does Papers still earn a page?&rdquo;, a question premised on a page of five
      lines; the abstract's restoration on 2026-08-21 removed the premise, and
      <code>DECISIONS.md</code> now records D-016 as settled rather than open. Folding Papers
      into Method is still yours to want, and nothing waits on it. Everything above is
      sourced from <code>DECISIONS.md</code> (Open) and the two items <code>CLAIMS.md</code>
      and <code>AGENTS.md</code> record as awaiting you. D-008, D-009, D-010, D-015 and D-017
      are also open but touch nothing in this set. One more thing is waiting on you and is
      not a decision: which edition of the paper is on SSRN &mdash; section 07.</p>
  </div>
</section>

<section class="compressed">
  <div class="wrap stack">
    <p class="eyebrow">Checked before this page was handed over</p>
    <p><strong>Regenerated 2026-08-21 against the settled record.</strong> Section 07 is
      rebuilt: <strong>D-016 was reversed on 2026-08-21</strong> and the Papers page carries
      the paper's abstract again, reproduced verbatim inside
      <code>data-claim-quote="C-055"</code> with its visible attribution line, the reconciling
      clause outside the block, and the two things that look like violations flagged in
      context. The abstract is copied from <code>_data/paper.json</code>
      <code>abstract.verbatim</code> by this page's build script and is never retyped.
      <strong>D-023</strong> stands with the qualifier it gained the same day &mdash; no
      comparison with another recruitment source <em>in our own voice</em> &mdash; so the
      figure in section 05 is still one bar on the same ruler and no comparator value appears
      in any sentence of ours. <strong>D-019</strong> &mdash; the coverage section is on Home,
      on paper, because Home is at its two-band limit. <strong>D-020</strong> &mdash; the stat
      row in section 06 is the four-cell totals band. Source lines carry the citation year,
      2025, everywhere the paper is cited.</p>
    <p>Every number on this page traces to a <code>VERIFIED</code> row in
      <code>CLAIMS.md</code> or to <code>scripts/data/coverage.json</code>, and carries its
      source beside it. The one exception is labelled: the numerals in the tabular/proportional
      table are glyph-fitting specimens and say so. <code>python3 scripts/check-contrast.py</code>
      passes on all 22 pairs. Nothing <code>WITHHELD</code> appears anywhere on this page
      <strong>except inside the quoted abstract in section 07</strong>, which is the one
      container permitted to hold it: the cost-per-question figure and the comparative
      sentence ship there as the authors' words, attributed and warned, and neither is lifted
      out of the block, restated or summarised in any sentence of ours. <code>python3
      scripts/build-coverage-map.py</code> was re-run for this build and the outputs above are
      its current ones &mdash; it ran clean:
      41 countries drawn, 4 of them pending, 6 regions, 738,608 of 841,660 respondents
      attributed. All colour comes from &sect;3 tokens, in all three theme states; the body sets
      an explicit <code>background: var(--paper)</code>; wide content scrolls in its own
      container; decorative SVG is <code>aria-hidden</code> and meaningful SVG carries
      <code>role="img"</code> with a <code>&lt;title&gt;</code>; and nothing on this page moves.</p>
    <p class="srcline">No repository document was edited to produce this page, and no proposed
      &sect;6, &sect;7 or D-021 edit quoted above has been written into
      <code>DESIGN.md</code> or <code>DECISIONS.md</code>. They are in
      <code>scratchpad/ws-icons.md</code> and <code>scratchpad/ws-coverage.md</code>, awaiting
      this review.</p>
  </div>
</section>

</main>

<script>
(function(){{
  var root = document.documentElement;
  var btns = document.querySelectorAll('.seg button');
  function apply(v){{
    if(v === 'system'){{ root.removeAttribute('data-theme'); }}
    else {{ root.setAttribute('data-theme', v); }}
    btns.forEach(function(b){{ b.setAttribute('aria-pressed', String(b.dataset.set === v)); }});
  }}
  btns.forEach(function(b){{ b.addEventListener('click', function(){{ apply(b.dataset.set); }}); }});
}})();
</script>
"""

OUT.write_text(HTML, encoding="utf-8")
print("wrote", OUT, OUT.stat().st_size, "bytes")
