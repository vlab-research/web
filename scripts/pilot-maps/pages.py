#!/usr/bin/env python3
"""Country pages and the cross-country "who" page, generated from the merged cell table.

    <venv>/bin/python pages.py          # after merge_cells.py; needs shapely + pyproj (geo venv)

Reads  scripts/data/{cells,recruitment-criteria,places,buckets}.json
       scripts/pilot-maps/private/*.map.json   (study slugs, for the For-review notes only)
Writes scripts/pilot-maps/out/review.html      the private review page (gitignored: it names studies)
       scripts/pilot-maps/out/maps/*.svg

Every figure on a page is computed here from the cells; nothing is typed. Edit this file, not the output.
"""
import collections, datetime, glob, json, math, os, re, statistics, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
OUT = os.path.join(HERE, "out")
os.makedirs(os.path.join(OUT, "maps"), exist_ok=True)

from shapely.geometry import shape, box, Point
from shapely.ops import unary_union
sys.path.insert(0, HERE)
import build_maps as B  # Frame, path, text, circle, STYLE, svg, esc

CELLS = json.load(open(os.path.join(DATA, "cells.json")))
CRIT = {r["rec"]: r for r in json.load(open(os.path.join(DATA, "recruitment-criteria.json")))}
PLACES = json.load(open(os.path.join(DATA, "places.json")))
BUCKETS = json.load(open(os.path.join(DATA, "buckets.json")))
PRIV = {}
RECID = re.compile(r"^[A-Z]{2}-\d{4}-\d{2}[a-z]?$")


def _walk(o):
    """Private maps differ in shape by group: collect any {rec id: {slugs|studies: [...]}} found at any depth."""
    if isinstance(o, dict):
        for k, v in o.items():
            if RECID.match(str(k)) and isinstance(v, dict):
                s = v.get("slugs") or v.get("studies") or v.get("study_slugs") or []
                PRIV.setdefault(k, {"slugs": [x if isinstance(x, str) else x.get("slug", "") for x in s]})
            else:
                _walk(v)
    elif isinstance(o, list):
        for v in o:
            _walk(v)


for f in glob.glob(os.path.join(HERE, "private", "*.map.json")):
    _walk(json.load(open(f)))

NAMES = dict(NG="Nigeria", GH="Ghana", KE="Kenya", BO="Bolivia", AR="Argentina", HN="Honduras", BD="Bangladesh",
             IN="India", PK="Pakistan", IQ="Iraq", EG="Egypt", MA="Morocco", JO="Jordan", SA="Saudi Arabia",
             AE="United Arab Emirates", US="United States", IE="Ireland", DE="Germany", ID="Indonesia",
             RS="Serbia", BG="Bulgaria", KG="Kyrgyzstan", TR="Türkiye")
THE = {"US", "AE"}  # "the United States"

MIN_SHOW, SOLID_STARTS, SOLID_SPEND = 50, 200, 100.0


# ------------------------------------------------------------------ helpers
def esc(s):
    return B.esc(str(s))


def money(x, whole=False):
    if x is None:
        return "—"
    if whole or x >= 1000:
        return f"${x:,.0f}"
    return f"${x:,.2f}"


def rng(a, b):
    return money(a) if round(a, 2) == round(b, 2) else f"{money(a)}–{money(b)}"


def month(d):
    return datetime.date.fromisoformat(d[:10]).strftime("%b %Y")


def span(a, b):
    a, b = month(a), month(b)
    return a if a == b else f"{a} – {b}"


def pct(x):
    return "—" if x is None else f"{100 * x:.0f}%"


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def pool(rows):
    sp = sum(x["spend_usd"] for x in rows)
    st = sum(x["started"] for x in rows)
    q = sum(x["qualified"] for x in rows)
    per = collections.defaultdict(lambda: [0.0, 0, 0])
    for x in rows:
        a = per[x["rec"]]
        a[0] += x["spend_usd"]; a[1] += x["started"]; a[2] += x["qualified"]
    good = {k: v for k, v in per.items() if v[1] >= MIN_SHOW and v[0] > 0}
    cps = [v[0] / v[1] for v in good.values()]
    return dict(spend=sp, started=st, qualified=q, cps=sp / st if st else None, cpq=sp / q if q else None,
                share=q / st if st else None, recs=len(per), per=per,
                cps_rng=(min(cps), max(cps)) if len(cps) > 1 else None,
                first=min(x["first"] for x in rows), last=max(x["last"] for x in rows))


def solid(p):
    return p["started"] >= SOLID_STARTS and p["spend"] >= SOLID_SPEND


def who_text(r):
    return r.get("who_qualified") or r.get("bucket_who") or "—"


# ------------------------------------------------------------------ maps
A1 = [f for f in json.load(open(os.path.join(HERE, "ne_10m_admin_1_states_provinces.geojson")))["features"]]
A0 = [f for f in json.load(open(os.path.join(HERE, "ne_10m_admin_0_countries.geojson")))["features"]]
DROP = r"\b(state|province|provincia|division|governorate|region|county|department|departamento|oblast|district|prefecture|muhafazat|wilayah|provinsi)\b"
ALIAS = {("NG", "abuja"): "federal capital territory", ("NG", "nasarawa"): "nassarawa",
         ("NG", "federal capital territory"): "federal capital territory"}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(DROP, " ", s)
    return re.sub(r"[^a-z ]+", " ", s).split() and " ".join(re.sub(r"[^a-z ]+", " ", s).split())


def a0(cc):
    for f in A0:
        p = f["properties"]
        if cc in (p.get("ISO_A2"), p.get("ISO_A2_EH"), p.get("WB_A2")):
            return shape(f["geometry"]).buffer(0)
    raise SystemExit(f"no admin-0 shape for {cc}")


def a1s(cc):
    out = {}
    for f in A1:
        p = f["properties"]
        if p.get("iso_a2") == cc:
            out[p["name"]] = (p, shape(f["geometry"]).buffer(0))
    return out


UNMATCHED = collections.defaultdict(set)


def match_region(cc, name, units):
    n = norm(name)
    n = ALIAS.get((cc, n), n)
    for k, (p, g) in units.items():
        names = [p.get(x) for x in ("name", "name_en", "gn_name", "gns_name", "woe_name", "name_local")]
        names += (p.get("name_alt") or "").split("|")
        if n in {norm(x) for x in names if x}:
            return k
    UNMATCHED[cc].add(name)
    return None


STEPS = [(0.25, ".3", "under $0.25"), (0.5, ".45", "$0.25–0.50"), (1.0, ".56", "$0.50–1"), (2.0, ".78", "$1–2"),
         (1e9, "1", "$2 or more")]


def step(c):
    return next(s for s in STEPS if c < s[0])


def fit_for(cc, land, targeted):
    if cc == "US":
        return land.intersection(box(-125, 24, -66.5, 49.5))
    minx, miny, maxx, maxy = land.bounds
    if maxx - minx > 30 and targeted is not None and not targeted.is_empty:
        return targeted.buffer(1.0)
    return land


def legend(body, x, y):
    body.append(B.text(x, y, "Advertising cost per start", "gm-eye"))
    for i, (_, op, lab) in enumerate(STEPS):
        xx = x + i * 118
        body.append(f'<rect x="{xx}" y="{y + 10}" width="16" height="12" style="fill:var(--data);fill-opacity:{op}"/>')
        body.append(B.text(xx + 22, y + 20, lab, "gm-tiny"))
    return y + 34


def rows_under(body, x, y, rows, width=760):
    """(label, sub, cost, starts, spend, solid) rows: the label on its own line, then the bar
    (length = cost per start) with its value, then when · starts · spend."""
    mc = max(r[2] for r in rows) or 1
    bw = width - 80
    for i, (lab, sub, c, n, sp, ok) in enumerate(rows):
        yy = y + i * 50
        body.append(B.text(x, yy + 11, lab if len(lab) <= 100 else lab[:98] + "…", "gm-lab"))
        L = max(2.0, bw * c / mc)
        body.append(f'<rect x="{x:.1f}" y="{yy + 17:.1f}" width="{L:.1f}" height="11" style="fill:var(--data);fill-opacity:{step(c)[1]}"/>')
        body.append(B.text(x + L + 6, yy + 27, money(c), "gm-val"))
        body.append(B.text(x, yy + 42, f"{sub} · {n:,} starts · {money(sp, True)} ads" + ("" if ok else " · thin"), "gm-tiny"))
    return y + len(rows) * 50


def region_map(cc, pooled):
    """Whole-region places: every region it covers, shaded by the place's cost per start."""
    units = a1s(cc)
    land = a0(cc)
    shade, labels, targeted = {}, [], []
    pooled = [(k, p) for k, p in pooled if len(PLACES[k].get("regions", [])) == 1]
    if len(pooled) < 2:
        return None
    for key, p in pooled:
        pl = PLACES[key]
        ks = [match_region(cc, r, units) for r in pl.get("regions", [])]
        ks = [k for k in ks if k]
        for k in ks:
            shade[k] = p["cps"]
            targeted.append(units[k][1])
        if ks:
            labels.append((pl["label"], ks, p))
    if not shade:
        return None
    T = unary_union(targeted)
    fit = fit_for(cc, land, T)
    c = fit.centroid
    W, H = 760, 470
    F = B.Frame(c.x, c.y, fit, (0, 8, W, H - 16))
    body = [B.path(F.g(land.buffer(0.3).intersection(fit.buffer(3)) if cc == "US" else land), "gm-land")]
    for k, (p, g) in units.items():
        if k in shade:
            body.append(B.path(F.g(g), "gm-circ", f' style="fill:var(--data);fill-opacity:{step(shade[k])[1]}"'))
    for k, (p, g) in units.items():
        body.append(B.path(F.g(g), "gm-adm"))
    body.append(B.path(F.g(land), "gm-outline"))
    for lab, ks, p in labels:
        if len(ks) == 1:
            pt = units[ks[0]][1].representative_point()
            x, y = F.xy(pt.x, pt.y)
            if 0 < x < W and 0 < y < H:
                body.append(B.text(x, y, lab.split(" (")[0].replace(" State", "")[:22], "gm-lab2 gm-halo", "middle"))
    y = legend(body, 0, H + 6)
    rows = [(PLACES[k]["label"], span(p["first"], p["last"]), p["cps"], p["started"], p["spend"], solid(p))
            for k, p in sorted(pooled, key=lambda kp: kp[1]["cps"])]
    y = rows_under(body, 0, y + 8, rows)
    title = f"{NAMES[cc]}: advertising cost per start in each whole region the ads targeted"
    desc = "; ".join(f"{r[0]} {money(r[2])} per start ({r[3]:,} starts)" for r in rows)
    return B.svg(W, y + 6, title, desc, body, f"map-{cc.lower()}-regions")


def radius_map(cc, pooled):
    """Radius-area places: every pin at true radius (a minimum dot where too small to see)."""
    land = a0(cc)
    pins = []
    for key, p in pooled:
        for lat, lon, r in PLACES[key].get("pins", []):
            pins.append((lon, lat, r, p["cps"]))
    if not pins:
        return None
    pts = unary_union([Point(lo, la) for lo, la, _, _ in pins])
    fit = fit_for(cc, land, pts.buffer(1.5))
    c = fit.centroid
    W, H = 760, 470
    F = B.Frame(c.x, c.y, fit, (0, 8, W, H - 16))
    body = [B.path(F.g(land), "gm-land")]
    units = a1s(cc)
    for k, (p, g) in units.items():
        body.append(B.path(F.g(g), "gm-adm"))
    body.append(B.path(F.g(land), "gm-outline"))
    for lon, lat, r, cps in sorted(pins, key=lambda t: -(t[2] or 0)):
        op = step(cps)[1]
        if r is None:  # a Meta city with no radius: Meta's own city area, drawn as a marker
            x, y = F.xy(lon, lat)
            body.append(f'<rect x="{x - 4:.1f}" y="{y - 4:.1f}" width="8" height="8" style="fill:var(--data);fill-opacity:{op};stroke:var(--ink);stroke-width:.8"/>')
            continue
        g = F.g(B.circle(lon, lat, r), clip=False, simplify=0.2)
        if math.sqrt(g.area / math.pi) < 1.8:
            x, y = F.xy(lon, lat)
            body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.8" style="fill:var(--data);fill-opacity:{op}"/>')
        else:
            body.append(B.path(g, "gm-circ", f' style="fill:var(--data);fill-opacity:{op}"'))
    y = legend(body, 0, H + 6)
    allp = [(k, p) for k, p in POOLED[cc] if PLACES[k]["type"] in ("radius_set", "city_radius", "radius_outside")]
    rows = [(PLACES[k]["label"], span(p["first"], p["last"]), p["cps"], p["started"], p["spend"], solid(p))
            for k, p in sorted(allp, key=lambda kp: kp[1]["cps"])]
    y = rows_under(body, 0, y + 8, rows)
    title = f"{NAMES[cc]}: radius areas the ads targeted, shaded by advertising cost per start"
    desc = f"{len(pins)} radius areas. " + "; ".join(f"{r[0]} {money(r[2])} per start" for r in rows)
    return B.svg(W, y + 6, title, desc, body, f"map-{cc.lower()}-radius")


# ------------------------------------------------------------------ shared modules
TPL = open(os.path.join(HERE, "review-page.tpl.html")).read()
HEAD = TPL[:TPL.index('<div class="wrap">')]
MOD_GEO = TPL[TPL.index('    <div class="how">\n      <div class="k">How it works · location targeting on Meta'):]
MOD_GEO = MOD_GEO[:MOD_GEO.index("    </div>\n") + 11]
MOD_NUM = TPL[TPL.index('    <div class="how">\n      <div class="k">How it works · what the numbers count'):]
MOD_NUM = MOD_NUM[:MOD_NUM.index("    </div>\n") + 11]
EXTRA_CSS = """<style>
tr.sub th{font:600 13px/1.3 var(--ui);letter-spacing:0;text-transform:none;color:var(--ink);padding-top:18px}
td.thin{color:var(--ink-3);font-style:italic}
.tags{font:400 12px/1.4 var(--mono);color:var(--ink-2)}
</style>
"""

POOLED = {}


def table(head, rows, cls=None):
    h = "".join(f"<th{' class=n' if n else ''}>{esc(t)}</th>" for t, n in head)
    body = "\n".join(rows)
    return f'<div class="tbl"><table><thead><tr>{h}</tr></thead><tbody>\n{body}\n</tbody></table></div>'


def tr(cells, thin=False):
    out = []
    for v, n in cells:
        c = []
        if n:
            c.append("n")
        if thin:
            c.append("thin")
        out.append(f"<td{' class=\"' + ' '.join(c) + '\"' if c else ''}>{v}</td>")
    return "<tr>" + "".join(out) + "</tr>"


# ------------------------------------------------------------------ one country
def country(cc):
    C = [x for x in CELLS if x["country"] == cc]
    recs = sorted({x["rec"] for x in C}, key=lambda r: CRIT[r]["first"])
    excl = [r for r in CRIT.values() if r["country"] == cc and r.get("round") == "excluded"]
    byplace = collections.defaultdict(list)
    for x in C:
        byplace[x["place"]].append(x)
    pooled = [(k, pool(v)) for k, v in byplace.items()]
    POOLED[cc] = pooled
    shown = [(k, p) for k, p in pooled if p["started"] >= MIN_SHOW and p["spend"] > 0]
    firm = [(k, p) for k, p in shown if solid(p)]
    tot = pool(C)
    name = NAMES.get(cc, cc)
    the = "the " if cc in THE else ""
    sid = slug(name)

    has_radius = any(PLACES[k]["type"] in ("radius_set", "city_radius", "radius_outside", "country_minus") for k, _ in shown)
    per_rec = [(r, pool([x for x in C if x["rec"] == r])) for r in recs]
    per_rec_ok = [(r, p) for r, p in per_rec if p["started"] >= MIN_SHOW and p["qualified"] > 0]

    # lede
    L = firm or shown
    lo = min(L, key=lambda kp: kp[1]["cps"]) if L else None
    hi = max(L, key=lambda kp: kp[1]["cps"]) if L else None
    nrec = len(recs)
    s = []
    if lo and hi and lo[0] != hi[0]:
        s.append(f"From {month(tot['first'])} to {month(tot['last'])}, advertising cost <b>{money(lo[1]['cps'])} to "
                 f"{money(hi[1]['cps'])} per person who started a survey</b> in {the}{name}, depending on where the ads ran: "
                 f"from {esc(PLACES[lo[0]]['label'])} to {esc(PLACES[hi[0]]['label'])}.")
    elif lo:
        s.append(f"From {month(tot['first'])} to {month(tot['last'])}, advertising cost <b>{money(lo[1]['cps'])} per "
                 f"person who started a survey</b> in {the}{name} ({esc(PLACES[lo[0]]['label'])}).")
    if per_rec_ok:
        q = [p["cpq"] for _, p in per_rec_ok]
        if len(q) > 1:
            s.append(f"Per qualified respondent it cost <b>{rng(min(q), max(q))}</b> across {len(per_rec_ok)} recruitments, "
                     f"depending on who qualified.")
        else:
            r0 = CRIT[per_rec_ok[0][0]]
            s.append(f"Per qualified respondent ({esc(who_text(r0))}) it cost <b>{money(q[0])}</b>.")
    lede = " ".join(s)

    facts = [(f"{tot['started']:,}", f"starts from our ads, {span(tot['first'], tot['last'])}"),
             (f"{tot['qualified']:,}", "qualified respondents: in a quota group and past the screening questions"),
             (money(tot["spend"], True), "advertising spend behind every figure on this page"),
             (f"{len(shown)}", f"places, from {nrec} recruitment{'s' if nrec != 1 else ''}")]

    H = [f'  <section id="{sid}" role="tabpanel" aria-labelledby="t-{sid}" hidden>',
         f'    <div class="eyebrow">{esc(name)} · Recruitment cost</div>',
         f'    <h1>What does it cost to recruit survey respondents in {the}{esc(name)}?</h1>',
         f'    <p class="lede">{lede}</p>',
         '    <div class="facts">' + "".join(f"<div><b>{a}</b><span>{esc(b)}</span></div>" for a, b in facts) + "</div>",
         MOD_GEO if has_radius else "", MOD_NUM]

    # ---- place slice
    if shown:
        H.append(f"    <h2>Where the ads ran</h2>")
        H.append("    <p>Each place is one way the ads were aimed, pooled over every recruitment that aimed them that way: "
                 "spend added up, people added up. A person counts toward a place if they came in through an ad aimed there, "
                 "whatever they later answered. Where a place pools several recruitments, the range shows how far its cost "
                 "moved between them.</p>")
        maps = []
        regs = [(k, p) for k, p in shown if PLACES[k]["type"] == "region"]
        rads = [(k, p) for k, p in shown if PLACES[k]["type"] in ("radius_set", "city_radius")]
        for fn, sel, tag in ((region_map, regs, "regions"), (radius_map, rads, "radius")):
            if sel:
                m = fn(cc, sel)
                if m:
                    open(os.path.join(OUT, "maps", f"{cc.lower()}-{tag}.svg"), "w").write(m)
                    maps.append(m)
        for m in maps:
            H.append(f"    <figure>{m}</figure>")
        rows = []
        order = ["whole country", "whole regions", "smaller areas", "radius areas", "outside radius areas"]
        for sl in order:
            sel = [(k, p) for k, p in shown if CELLS_SLICE[k] == sl]
            if not sel:
                continue
            rows.append(f'<tr class="sub"><th colspan="7">{esc(sl.capitalize())}</th></tr>')
            for k, p in sorted(sel, key=lambda kp: kp[1]["cps"]):
                r = p["cps_rng"]
                rows.append(tr([(esc(PLACES[k]["label"]), 0), (span(p["first"], p["last"]), 0), (p["recs"], 1),
                                (f"{p['started']:,}", 1), (money(p["spend"], True), 1), (money(p["cps"]), 1),
                                (rng(*r) if r else "", 1)], thin=not solid(p)))
        H.append(table([("Where the ads ran", 0), ("When", 0), ("Recruitments", 1), ("Started", 1), ("Ad spend", 1),
                        ("Per start", 1), ("Range", 1)], rows))
        H.append(f'    <p class="cap">Started: people who sent a first message through an ad aimed at that place. Range: '
                 f'cost per start in each recruitment with at least {MIN_SHOW} starts there. In grey italics: under '
                 f'{SOLID_STARTS} starts or under ${SOLID_SPEND:.0f} of ads, so read as thin. Places with fewer than '
                 f'{MIN_SHOW} starts are left out.</p>')

    # ---- same-recruitment comparisons
    same = []
    for r in recs:
        sel = collections.defaultdict(list)
        for x in C:
            if x["rec"] == r:
                sel[x["place"]].append(x)
        ps = [(k, pool(v)) for k, v in sel.items()]
        ps = [(k, p) for k, p in ps if p["started"] >= MIN_SHOW and p["spend"] > 0]
        if len(ps) >= 2:
            same.append((r, ps))
    if same:
        same.sort(key=lambda rp: -sum(p["spend"] for _, p in rp[1]))
        H.append("    <h2>The fair comparison: places within one recruitment</h2>")
        H.append("    <p>Pooled figures mix recruitments that ran at different times and pushed at different speeds, and "
                 "spending faster in the same place costs more per person. Within one recruitment the survey, the dates "
                 "and the budget rules are the same, so the difference between places is the place.</p>")
        for r, ps in same[:3]:
            cr = CRIT[r]
            lo_, hi_ = min(p["cps"] for _, p in ps), max(p["cps"] for _, p in ps)
            rows = [tr([(esc(PLACES[k]["label"]), 0), (f"{p['started']:,}", 1), (money(p["spend"], True), 1),
                        (money(p["cps"]), 1), (pct(p["share"]), 1), (money(p["cpq"]), 1)], thin=not solid(p))
                    for k, p in sorted(ps, key=lambda kp: kp[1]["cps"])]
            H.append(f"    <h3 style=\"font:600 16px/1.3 var(--ui);margin:28px 0 4px\">{span(cr['first'], cr['last'])}: "
                     f"{len(ps)} places, {money(lo_)} to {money(hi_)} per start</h3>")
            H.append(f'    <p class="cap" style="margin-top:0">Qualified: {esc(who_text(cr))}.</p>')
            H.append(table([("Where the ads ran", 0), ("Started", 1), ("Ad spend", 1), ("Per start", 1),
                            ("Qualified", 1), ("Per qualified", 1)], rows))

    # ---- person slice
    if per_rec_ok:
        H.append("    <h2>Who qualified, and what that did to the cost</h2>")
        H.append("    <p>Cost per start measures the place. Cost per qualified respondent also depends on who a recruitment "
                 "was looking for and how long its screening took, because the ads also reach people who don't qualify. "
                 "As a rule of thumb, cost per qualified is roughly cost per start divided by the share of starters who "
                 "qualify.</p>")
        rows = []
        for r, p in per_rec_ok:
            cr = CRIT[r]
            m = cr.get("median_minutes_to_qualify")
            rows.append(tr([(span(cr["first"], cr["last"]), 0),
                            (esc(who_text(cr)) + f'<span class="id">{esc(cr.get("bucket_who", ""))}</span>', 0),
                            (f"{m:.0f}" if m and m <= 120 else "—", 1), (f"{p['started']:,}", 1), (pct(p["share"]), 1),
                            (money(p["cps"]), 1), (money(p["cpq"]), 1)], thin=not solid(p)))
        H.append(table([("When", 0), ("Who qualified", 0), ("Minutes", 1), ("Started", 1), ("Qualified", 1),
                        ("Per start", 1), ("Per qualified", 1)], rows))
        H.append('    <p class="cap">Minutes: the median time from a person\'s first message to the question that '
                 'qualified them. Qualified: the share of people who started who qualified.</p>')

    # ---- gender of the ads, within recruitments that split by it
    pairs = []
    for r in recs:
        g = collections.defaultdict(list)
        for x in C:
            if x["rec"] == r:
                g[x["ads"].get("genders") or "all"].append(x)
        if g.get("women") and g.get("men"):
            w, m_ = pool(g["women"]), pool(g["men"])
            if w["started"] >= MIN_SHOW and m_["started"] >= MIN_SHOW:
                pairs.append((r, w, m_))
    if pairs:
        W_ = pool([x for r, *_ in pairs for x in C if x["rec"] == r and x["ads"].get("genders") == "women"])
        M_ = pool([x for r, *_ in pairs for x in C if x["rec"] == r and x["ads"].get("genders") == "men"])
        cheaper = sum(1 for _, w, m_ in pairs if w["cps"] < m_["cps"])
        H.append(f"    <h2>{'Women' if W_['cps'] < M_['cps'] else 'Men'} cost less to reach"
                 f"{'' if cheaper in (0, len(pairs)) else ', but not in every recruitment'}</h2>")
        rows = [tr([("Ads shown to women", 0), (f"{W_['started']:,}", 1), (money(W_["spend"], True), 1), (money(W_["cps"]), 1)]),
                tr([("Ads shown to men", 0), (f"{M_['started']:,}", 1), (money(M_["spend"], True), 1), (money(M_["cps"]), 1)])]
        H.append(table([(f"{len(pairs)} recruitment{'s' if len(pairs) > 1 else ''} with separate ads by gender", 0),
                        ("Started", 1), ("Ad spend", 1), ("Per start", 1)], rows))
        H.append(f'    <p class="cap">Women were cheaper to reach in {cheaper} of {len(pairs)}. Only recruitments that ran '
                 f'separate ads to women and to men, each with at least {MIN_SHOW} starts, are counted.</p>')

    # ---- set-up
    chans = sorted({CRIT[r].get("channel") for r in recs if CRIT[r].get("channel")})
    CH = dict(messenger="Messenger", whatsapp="WhatsApp", instagram="Instagram", web="a web survey")
    H.append("    <h2>How the recruitments were set up</h2><dl>")
    H.append(f"<dt>Channel</dt><dd>Facebook and Instagram ads leading to a survey in "
             f"{' or '.join(CH.get(c, c) for c in chans) or '—'}.</dd>")
    inc = [CRIT[r].get("incentive") for r in recs]
    H.append("<dt>Incentive</dt><dd>" + ("Paid to respondents in some recruitments; never included in the advertising cost."
                                          if any(inc) else "None recorded.") + "</dd>")
    H.append("<dt>Qualified</dt><dd>In a quota group, and past the recruitment's screening questions, as listed by "
             "recruitment above.</dd></dl>")
    H.append(f'    <p class="cta">Planning a study in {the}{esc(name)}? Write to <b>info@vlab.digital</b>.</p>')

    # ---- for review
    N = ['    <div class="note"><h3>For review</h3><ul>']
    for r in recs:
        cr = CRIT[r]
        pv = PRIV.get(r, {})
        studies = ", ".join(f"<code>{esc(s)}</code>" for s in (pv.get("studies") or pv.get("slugs") or []))
        p = dict(per_rec)[r]
        N.append(f"<li><b>{esc(r)}</b> ({cr.get('round', '')}) {studies}: {money(p['spend'], True)}, "
                 f"{p['started']:,} started, {p['qualified']:,} qualified. {esc(cr.get('notes') or '')}</li>")
    for cr in excl:
        pv = PRIV.get(cr["rec"], {})
        studies = ", ".join(f"<code>{esc(s)}</code>" for s in (pv.get("studies") or pv.get("slugs") or []))
        N.append(f"<li><b>Excluded {esc(cr['rec'])}</b> {studies}: {esc(cr.get('notes') or '')}</li>")
    if UNMATCHED.get(cc):
        N.append(f"<li><b>Map:</b> regions not matched to a boundary: {esc(', '.join(sorted(UNMATCHED[cc])))}.</li>")
    N.append("</ul></div>")
    H += N
    H.append("  </section>")
    return sid, name, "\n".join(x for x in H if x)


# ------------------------------------------------------------------ the "who" page
def who_page():
    kept = [r for r in CRIT.values() if r.get("round") != "excluded"]
    H = ['  <section id="who" role="tabpanel" aria-labelledby="t-who" hidden>',
         '    <div class="eyebrow">Across countries · Who qualified</div>',
         '    <h1>What share of the people our ads reach qualify?</h1>']
    b = collections.defaultdict(list)
    for x in CELLS:
        b[x["slice_who"]].append(x)
    nc = b.pop("not comparable", [])
    P = {k: pool(v) for k, v in b.items()}
    order = sorted(P, key=lambda k: -P[k]["share"])
    H.append('    <p class="lede">Where the ads ran sets the cost of reaching a person. Who a recruitment is looking for '
             'sets how many of the people reached count. Across '
             f'{len(kept)} recruitments in {len({x["country"] for x in CELLS})} countries, the share of people who '
             f'started a survey and qualified ranged from <b>{pct(min(p["share"] for p in P.values()))}</b> to '
             f'<b>{pct(max(p["share"] for p in P.values()))}</b> by type of person.</p>')
    H.append(MOD_NUM)
    H.append("    <h2>Share who qualify, by who a recruitment was looking for</h2>")
    rows = []
    for k in order:
        p = P[k]
        shares = [v[2] / v[1] for v in p["per"].values() if v[1] >= MIN_SHOW]
        cpq = [v[0] / v[2] for v in p["per"].values() if v[1] >= MIN_SHOW and v[2]]
        rows.append(tr([(esc(k[0].upper() + k[1:]), 0), (p["recs"], 1),
                        (len({x["country"] for x in b[k]}), 1), (f"{p['started']:,}", 1), (pct(p["share"]), 1),
                        (f"{pct(min(shares))}–{pct(max(shares))}" if len(shares) > 1 else "", 1),
                        (rng(min(cpq), max(cpq)) if cpq else "—", 1)]))
    H.append(table([("Who qualified", 0), ("Recruitments", 1), ("Countries", 1), ("Started", 1), ("Qualified", 1),
                    ("Range", 1), ("Per qualified", 1)], rows))
    H.append(f'    <p class="cap">Qualified: people who qualified ÷ people who started, pooled. Range: the same share in '
             f'each recruitment with at least {MIN_SHOW} starts. Per qualified: the range of advertising cost per '
             f'qualified respondent across those recruitments, which also carries the place. '
             f'{len({x["rec"] for x in nc})} recruitments are left out of this table because their "qualified" '
             f'means something else (a later wave, or a screen outside the survey).</p>')

    lb = collections.defaultdict(list)
    for x in CELLS:
        lb[x["slice_length"]].append(x)
    H.append("    <h2>Share who qualify, by how long the screening took</h2>")
    rows = [tr([(esc(k), 0), (pool(v)["recs"], 1), (f"{pool(v)['started']:,}", 1), (pct(pool(v)["share"]), 1)])
            for k, v in sorted(lb.items(), key=lambda kv: ["under 10 minutes", "10–20 minutes", "over 20 minutes", "unknown"].index(kv[0]))]
    H.append(table([("Median time to the qualifying question", 0), ("Recruitments", 1), ("Started", 1), ("Qualified", 1)], rows))

    # gender of the ads, within recruitment
    ratios = []
    for r in {x["rec"] for x in CELLS}:
        g = collections.defaultdict(list)
        for x in CELLS:
            if x["rec"] == r:
                g[x["ads"].get("genders") or "all"].append(x)
        if g.get("women") and g.get("men"):
            w, m_ = pool(g["women"]), pool(g["men"])
            if w["started"] >= SOLID_STARTS and m_["started"] >= SOLID_STARTS and m_["cps"]:
                ratios.append((r, w["cps"] / m_["cps"]))
    if ratios:
        med = statistics.median(v for _, v in ratios)
        H.append("    <h2>Ads to women against ads to men</h2>")
        H.append(f"    <p>In {len(ratios)} recruitments that ran separate ads to women and to men, each with at least {SOLID_STARTS} starts, a start from an ad "
                 f"shown to women cost a median <b>{med:.2f} times</b> one from an ad shown to men; women were cheaper in "
                 f"{sum(1 for _, v in ratios if v < 1)} of them. The ratio ranged from {min(v for _, v in ratios):.2f} "
                 f"to {max(v for _, v in ratios):.2f}.</p>")
    H.append("  </section>")
    return "\n".join(H)


# ------------------------------------------------------------------ the buckets tab (review)
def buckets_page():
    H = ['  <section id="buckets" role="tabpanel" aria-labelledby="t-buckets" hidden>',
         '    <div class="eyebrow">For review · Not a page</div>',
         '    <h1>Every recruitment, and the bucket it falls in</h1>',
         '    <p class="lede">The buckets are proposals, derived by rule from each recruitment\'s screening tags '
         '(<code>merge_cells.py</code>, <code>who_bucket</code>). Change a rule there, not a row here.</p>',
         '    <h2>The rules, first match wins</h2><ol style="font:400 15px/1.5 var(--ui)">',
         '<li>Any <code>behaviour:</code> tag → people with a specific behaviour</li>',
         '<li>Any <code>occupation:</code> tag → people in a specific occupation</li>',
         '<li><code>pregnant_or_recent_birth</code> → pregnant or recently gave birth</li>',
         '<li><code>caregiver:child_age:a-b</code> → caregivers of young children (under 6) / children aged 6–11 / adolescents (9–17)</li>',
         '<li><code>parent_any</code> → parents and caregivers</li>',
         '<li>Women only (screened, or every ad to women) → women, or young women if the age cap is 35 or under</li>',
         '<li>Age cap of 35 or under → young adults</li><li>Otherwise → any adult</li></ol>',
         '    <p>Place slice: whole country (including country minus some cities), whole regions, radius areas, outside '
         'radius areas. Survey length: under 10, 10–20, over 20 minutes to the qualifying question. Daily spend is '
         'recorded per cell and shown nowhere.</p>']
    rows = []
    for r in sorted(CRIT.values(), key=lambda r: (r["country"], r.get("first") or "")):
        a = r.get("ads") or {}
        pv = PRIV.get(r["rec"], {})
        studies = " ".join(pv.get("studies") or pv.get("slugs") or [])
        g = a.get("genders")
        g = "/".join(g) if isinstance(g, list) else (g or "")
        ex = r.get("round") == "excluded"
        rows.append(tr([(f"{esc(r['rec'])}<span class=\"id\">{esc(studies)}</span>", 0), (esc(r.get("round", "")), 0),
                        (f"{esc(g)} {a.get('age_min', '')}–{a.get('age_max', '')}{' · interests' if a.get('interests') else ''}", 0),
                        (f'<span class="tags">{esc(" ".join(r.get("screen") or []))}</span>', 0),
                        (esc(r.get("notes") or "") if ex else esc(who_text(r)), 0),
                        ("—" if ex else esc(r.get("bucket_who", "")), 0),
                        ("" if ex or not r.get("started") else pct(r["qualified"] / r["started"]), 1)], thin=ex))
    H.append(table([("Recruitment", 0), ("Round", 0), ("Ads", 0), ("Screen", 0), ("Who qualified", 0), ("Bucket", 0),
                    ("Qualified", 1)], rows))
    H.append("  </section>")
    return "\n".join(H)


CELLS_SLICE = {x["place"]: x["slice_place"] for x in CELLS}


# ------------------------------------------------------------------ assemble
def assemble(secs, tabs, label):
    stamp = datetime.date.today().strftime("%-d %b %Y")
    page = (HEAD.replace("<title>Country Pages Pilot</title>", "<title>Recruitment Cost Pages</title>") + EXTRA_CSS +
            f'<div class="wrap">\n  <div class="bar">\n    <span>{label} · not on the site · '
            f'data as of {stamp}</span>\n    <div class="tabs" role="tablist">' +
            "".join(f'\n      <button role="tab" id="t-{i}" aria-controls="{i}">{esc(n)}</button>' for i, n in tabs) +
            "\n    </div>\n  </div>\n" + "\n".join(secs) + "\n</div>\n" + TPL[TPL.index("<script>"):])
    dup = [i for i in set(re.findall(r' id="([^"]+)"', page)) if page.count(f' id="{i}"') > 1]
    open(os.path.join(OUT, "review.html"), "w").write(page)
    print(f"wrote out/review.html: {len(tabs)} tabs, {len(page) / 1024:.0f} KB, duplicate ids: {dup or 'none'}")
    for cc, names in UNMATCHED.items():
        print(f"  unmatched regions {cc}: {sorted(names)}")


if __name__ == "__main__":
    countries = sorted({x["country"] for x in CELLS},
                       key=lambda c: -sum(x["spend_usd"] for x in CELLS if x["country"] == c))
    secs, tabs = [], []
    for cc in countries:
        sid, name, html = country(cc)
        secs.append(html)
        tabs.append((sid, name))
    secs.append(who_page()); tabs.append(("who", "Who qualified"))
    secs.append(buckets_page()); tabs.append(("buckets", "Buckets"))
    assemble(secs, tabs, "Pilot v9 · generated from the cell table")
