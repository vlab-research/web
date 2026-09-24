#!/usr/bin/env python3
"""Country pages by pattern (v10): level from general data, differences as ratios within one recruitment.

    <geo venv>/bin/python patterns.py NG KE ID     # after merge_cells.py

The rule (Nandan, 2026-09-24): avoid data that is overly specific; lead with the general.
  * HOW MUCH comes only from recruitments whose audience tier is "general" (or, where a country has
    no general data, from one named "common" group, and the heading says which group).
  * WHERE comes from comparisons inside one recruitment, stated as multiples of the cheapest place.
    Those survive a narrow audience: both places were recruiting the same people on the same days.
  * "specialised" recruitments never set a figure on the page; they get one general sentence.

Patterns: "general" (a country with general-population data), "group" (only a common group),
"place" (a country whose story is where the ads ran). Chosen per country in PATTERN below.
Every number is computed from scripts/data/cells.json; nothing is typed.
"""
import collections, math, os, re, statistics, sys

import pages as P
from pages import B, esc, money, rng, span, pct, table, tr, pool, CELLS, CRIT, PLACES, NAMES, THE

PATTERN = {"KE": "general", "ID": "group", "NG": "place"}
MIN_PLACE_START, MIN_PLACE_SPEND = 50, 25.0     # a place enters a comparison

# ------------------------------------------------------------------ plain words for the specialised line
REASON_WORDS = [("interest", "audiences chosen by Meta interests"), ("behaviour:", "people who had done something specific"),
                ("occupation:", "one occupation"), ("citizen:", "citizens only"), ("child_task", "families where a child also took part"),
                ("communities", "particular communities"), ("works_or_studies_in", "people who work or study in one place"),
                ("follow_up", "people who came back for a later survey")]


def plain_reason(r):
    t = (r.get("tier_reason") or "").lower()
    return next((w for k, w in REASON_WORDS if k in t), "narrower groups")


def recs_of(cc, tier=None):
    rs = [r for r in CRIT.values() if r["country"] == cc and r.get("round") != "excluded"]
    return sorted([r for r in rs if tier is None or r.get("tier") == tier], key=lambda r: r["first"])


def cells_of(rec):
    return [x for x in CELLS if x["rec"] == rec]


def group_label(r):
    b = r.get("bucket_who") or ""
    return {"caregivers of girls: adolescents (9–17)": "parents and caregivers of adolescent girls",
            "caregivers of young children (under 6)": "parents and caregivers of young children"}.get(b, b)


# ------------------------------------------------------------------ comparisons inside one recruitment
NO_COMPARE = {"ad_arm_confounded_with_side"}   # a cell flag that makes a round's place differences uninterpretable


def comparisons(cc):
    """{rec: {place: (multiple of the cheapest solid place, pooled row)}} for recruitments with 2+ solid
    places (P.solid: 200+ starts and $100+ of ads). Thinner places ride along, greyed, never as the base."""
    out = {}
    for r in recs_of(cc):
        cs = cells_of(r["rec"])
        if any(NO_COMPARE & set(x.get("flags") or []) for x in cs):
            continue
        by = collections.defaultdict(list)
        for x in cs:
            by[x["place"]].append(x)
        ps = {k: pool(v) for k, v in by.items()}
        ps = {k: p for k, p in ps.items() if p["started"] >= MIN_PLACE_START and p["spend"] >= MIN_PLACE_SPEND}
        firm = [p for p in ps.values() if P.solid(p)]
        if len(firm) >= 2:
            lo = min(p["cps"] for p in firm)
            out[r["rec"]] = {k: (p["cps"] / lo, p) for k, p in ps.items()}
    return out


def short(k):
    """A heading-length name for a place; the full label stays in the table."""
    pl = PLACES[k]; lab = pl["label"]; t = pl["type"]
    if t == "region":
        return lab.replace(" (whole)", "").replace(" (whole territory)", "")
    if t == "radius_outside":
        return f"{pl['regions'][0]}, outside the radius areas" if pl.get("regions") else lab
    m = re.match(r"(?:Inside )?(\d+) radius areas? (?:of ([\d.]+) km|\(([\d.–-]+) km\)) in (?:the )?([A-Z][A-Za-z ]+?)(?: \(|,|$)", lab)
    if m:
        n, a, b, where = m.groups()
        return f"{where}, {n} radius area{'s' if n != '1' else ''} ({(a or b).replace('-', '–')} km)"
    return lab


def times(m):
    return "1×" if 0.95 <= m < 1.05 else f"{m:.1f}×" if m < 10 else f"{m:.0f}×"


MSTEPS = [(1.5, ".3", "cheapest (under 1.5×)"), (3, ".5", "1.5–3×"), (6, ".7", "3–6×"), (1e9, "1", "6× or more")]


def mstep(m):
    return next(s for s in MSTEPS if m < s[0])


QSTEPS = [(1.0, ".3", "under $1"), (3.0, ".5", "$1–3"), (10.0, ".7", "$3–10"), (1e9, "1", "$10 or more")]


def mlegend(body, y, steps=MSTEPS, title="Cost per start, against the cheapest place"):
    body.append(B.text(0, y, title, "gm-eye"))
    for i, (_, op, lab) in enumerate(steps):
        xx = i * 170
        body.append(f'<rect x="{xx}" y="{y + 10}" width="16" height="12" style="fill:var(--data);fill-opacity:{op}"/>')
        body.append(B.text(xx + 22, y + 20, lab, "gm-tiny"))
    return y + 34


def multiple_map(cc, mult, label, title, kind="mult"):
    """Regions or radius areas shaded by a value per place: kind "mult" (multiple of the cheapest place)
    or "money" (advertising cost per qualified respondent)."""
    steps = MSTEPS if kind == "mult" else QSTEPS
    fmt = times if kind == "mult" else money
    stepof = lambda v: next(x for x in steps if v < x[0])
    land = P.a0(cc)
    units = P.a1s(cc)
    geoms, pins = [], []
    regs = [r for k in mult for r in (PLACES[k].get("regions") or []) if PLACES[k]["type"] in ("region", "radius_outside")]
    if len(regs) != len(set(regs)):   # places overlap: shading would overwrite, so no map
        return None
    for k, m in mult.items():
        pl = PLACES[k]
        if pl["type"] in ("region", "radius_outside"):   # outside: the region is shaded, its radius areas drawn on top
            for rn in pl.get("regions", []):
                u = P.match_region(cc, rn, units)
                if u:
                    one = len(pl.get("regions", [])) == 1
                    geoms.append((units[u][1], m, (rn + (", outside" if pl["type"] == "radius_outside" else "")) if one else None))
        for la, lo, r in pl.get("pins", []) or []:
            pins.append((lo, la, r, m))
    if not geoms and not pins:
        return None
    from shapely.ops import unary_union
    from shapely.geometry import Point
    tgt = unary_union([g for g, _, _ in geoms] + [Point(lo, la).buffer(0.3) for lo, la, _, _ in pins])
    fit = P.fit_for(cc, land, tgt)
    if pins and not geoms:
        fit = tgt.buffer(0.6).intersection(land.buffer(0.2)) if tgt.area < land.area * 0.25 else land
    c = fit.centroid
    W, H = 760, 460
    F = B.Frame(c.x, c.y, fit, (0, 8, W, H - 16))
    body = [B.path(F.g(land), "gm-land")]
    for g, m, _ in geoms:
        body.append(B.path(F.g(g), "gm-circ", f' style="fill:var(--data);fill-opacity:{stepof(m)[1]}"'))
    for k, (p, g) in units.items():
        body.append(B.path(F.g(g), "gm-adm"))
    body.append(B.path(F.g(land), "gm-outline"))
    for lo, la, r, m in sorted(pins, key=lambda t: -(t[2] or 0)):
        op = stepof(m)[1]
        g = F.g(B.circle(lo, la, r or 16), clip=False, simplify=0.2)
        if math.sqrt(max(g.area, 0) / math.pi) < 2.2:
            x, y = F.xy(lo, la)
            body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" style="fill:var(--data);fill-opacity:{op}"/>')
        else:
            body.append(B.path(g, "gm-circ", f' style="fill:var(--data);fill-opacity:{op}"'))
    for g, m, rn in geoms:
        if rn is None:   # a group of regions: shaded, not labelled region by region (the table names them)
            continue
        pt = g.representative_point()
        x, y = F.xy(pt.x, pt.y)
        if 0 < x < W and 0 < y < H:
            body.append(B.text(x, y - 3, rn.replace(" State", ""), "gm-lab2 gm-halo", "middle"))
            body.append(B.text(x, y + 12, fmt(m), "gm-val gm-halo", "middle"))
    if not geoms:  # pins only: name the states or provinces they fall in, for orientation
        from shapely.geometry import Point as _Pt
        named = collections.Counter()
        for lo, la, _, _ in pins:
            for k, (p, g) in units.items():
                if g.contains(_Pt(lo, la)):
                    named[k] += 1
                    break
        for k in named:
            pt = units[k][1].representative_point()
            x, y = F.xy(pt.x, pt.y)
            if 0 < x < W and 0 < y < H:
                body.append(B.text(x, y, k, "gm-lab2 gm-halo", "middle"))
    y = mlegend(body, H + 6, steps, "Cost per start, against the cheapest place" if kind == "mult"
                else "Advertising cost per qualified respondent")
    desc = "; ".join(f"{PLACES[k]['label']}: {fmt(m)}" for k, m in sorted(mult.items(), key=lambda kv: kv[1]))
    return B.svg(W, y + 4, title, desc, body, label)


# ------------------------------------------------------------------ one index per place (no dates, no per-recruitment columns)
def place_index(cc):
    """Fit log(cost per start) = recruitment level + place effect, weighted by starts, over every usable
    place in every recruitment that ran 2+ places (confounded rounds excluded). The recruitment level
    absorbs who was sought, when and how hard; the place effect is learned only from differences
    inside recruitments, yet pools all of them. Returns components of places that are connected
    through shared recruitments: [{place: dict(mult, recs, starts, spend, cps)}], cheapest = 1."""
    import numpy as np
    rows = []   # (rec, place, log cps, weight, pooled)
    for r in recs_of(cc):
        if r.get("tier") == "specialised":   # narrow audiences stay off the page, comparisons included
            continue
        cs = cells_of(r["rec"])
        if any(NO_COMPARE & set(x.get("flags") or []) for x in cs):
            continue
        by = collections.defaultdict(list)
        for x in cs:
            by[x["place"]].append(x)
        ps = {k: pool(v) for k, v in by.items()}
        ps = {k: p for k, p in ps.items() if p["started"] >= MIN_PLACE_START and p["spend"] >= MIN_PLACE_SPEND}
        if len(ps) >= 2 and sum(P.solid(p) for p in ps.values()) >= 2:
            for k, p in ps.items():
                rows.append((r["rec"], k, math.log(p["cps"]), p["started"], p))
    # recruitments join one comparison only when they share two or more places: a chain through a single
    # place would carry that place's own swings (Lagos was cheapest in one recruitment, dear in another)
    rp = collections.defaultdict(set)
    for rec, k, *_ in rows:
        rp[rec].add(k)
    parent = {}

    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    recs_ = sorted(rp)
    for i, a in enumerate(recs_):
        find(a)
        for b in recs_[i + 1:]:
            if len(rp[a] & rp[b]) >= 2:
                parent[find(a)] = find(b)
    comps = collections.defaultdict(list)
    for row in rows:
        comps[find(row[0])].append(row)
    out = []
    for rs in comps.values():
        recs = sorted({x[0] for x in rs}); places = sorted({x[1] for x in rs})
        if len(places) < 2:
            continue
        X = np.zeros((len(rs), len(recs) + len(places) - 1)); y = np.zeros(len(rs)); w = np.zeros(len(rs))
        for i, (rec, k, ly, wt, _) in enumerate(rs):
            X[i, recs.index(rec)] = 1
            j = places.index(k)
            if j:
                X[i, len(recs) + j - 1] = 1
            y[i] = ly; w[i] = math.sqrt(wt)
        beta = np.linalg.lstsq(X * w[:, None], y * w, rcond=None)[0]
        eff = {places[0]: 0.0, **{places[j]: beta[len(recs) + j - 1] for j in range(1, len(places))}}
        lo = min(eff.values())
        comp = {}
        for k in places:
            prs = [x for x in rs if x[1] == k]
            # dollars from the same recruitments as the comparison, so the two columns cannot disagree
            same = [x for x in CELLS if x["place"] == k and x["rec"] in recs]
            pp = pool(same) if same else None
            comp[k] = dict(mult=math.exp(eff[k] - lo), recs=len(prs), starts=sum(x[4]["started"] for x in prs),
                           solid=any(P.solid(x[4]) for x in prs), pooled=pp)
        # dollars are comparable across places only if every place ran in every recruitment behind them
        balanced = all(comp[k]["recs"] == len(recs) for k in places)
        for k in places:
            if not balanced:
                comp[k]["pooled"] = None
        out.append(comp)
    return sorted(out, key=lambda c: (-len(c), -sum(v["starts"] for v in c.values())))


def index_table(comp):
    order = ["country", "country_minus", "region", "subregion_set", "region_minus", "radius_set", "city_radius", "radius_outside"]
    rows = []
    for k, v in sorted(comp.items(), key=lambda kv: kv[1]["mult"]):
        pp = v["pooled"]
        rows.append(tr([(esc(short(k)) + f'<span class="id">{esc(PLACES[k]["label"])}</span>', 0),
                        (f"{pp['qualified']:,}" if pp else "—", 1),
                        (money(pp["cpq"]) if pp and pp["qualified"] else "—", 1),
                        (money(pp["cps"]) if pp and pp["started"] else "—", 1),
                        (f"<b>{times(v['mult'])}</b>", 1)], thin=not v["solid"]))
    return table([("Where the ads ran", 0), ("Qualified", 1), ("Per qualified", 1), ("Per start", 1),
                  ("Against the cheapest", 1)], rows)


INDEX_CAP = ("Per qualified and per start: advertising spend ÷ qualified respondents, and ÷ people who started, "
             "pooled over the recruitments behind the comparison, and shown only where every place ran in every one of them. Against the cheapest: how much more "
             "a start cost here than in the cheapest place, estimated only from recruitments that ran several of "
             "these places at once, so it does not depend on who a recruitment was looking for. In grey italics: "
             "never reached "
             f"{P.SOLID_STARTS} starts and ${P.SOLID_SPEND:.0f} of ads in one recruitment.")


# ------------------------------------------------------------------ blocks
def level_table(recs):
    """One row per recruitment, no dates, sorted by cost per start."""
    rows = []
    for r in recs:
        p = pool(cells_of(r["rec"]))
        if p["started"] < MIN_PLACE_START:
            continue
        rows.append((p["cps"], tr([(esc(r.get("who_qualified") or ""), 0), (f"{p['started']:,}", 1), (money(p["cps"]), 1),
                                   (pct(p["share"]) if r.get("who_comparable", True) else "—", 1),
                                   (money(p["cpq"]) if r.get("who_comparable", True) else "—", 1)])))
    return table([("Who qualified", 0), ("Started", 1), ("Per start", 1), ("Qualified", 1), ("Per qualified", 1)],
                 [x for _, x in sorted(rows, key=lambda t: t[0])])


def level_stats(recs):
    ps = [(r, pool(cells_of(r["rec"]))) for r in recs]
    ps = [(r, p) for r, p in ps if p["started"] >= MIN_PLACE_START]
    s = [p["cps"] for _, p in ps]
    q = [p["cpq"] for r, p in ps if r.get("who_comparable", True) and p["qualified"]]
    return ps, s, q


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def specialised_line(cc, ref):
    """ref: (low, high) cost per qualified in the page's headline recruitments, or None."""
    sp = [(r, pool(cells_of(r["rec"]))) for r in recs_of(cc, "specialised")]
    sp = [(r, p) for r, p in sp if p["started"] >= MIN_PLACE_START and p["qualified"]]
    if not sp:
        return ""
    words = sorted({plain_reason(r) for r, _ in sp})
    q = [p["cpq"] for _, p in sp]
    what = " and ".join([", ".join(words[:-1]), words[-1]] if len(words) > 1 else words)
    cmp_ = f", against {rng(*ref)} for the general recruitments above" if ref else ""
    n = len(sp)
    return (f"<p>{n} recruitment{'s' if n > 1 else ''} here looked for narrower groups ({esc(what)}). "
            f"{'They' if n > 1 else 'It'} cost {rng(min(q), max(q))} per qualified respondent{cmp_}. "
            f"A figure for a narrow group says more about the group than about the country, so they are not "
            f"broken down here.</p>")


def gender_block(recs):
    pairs = []
    for r in recs:
        g = collections.defaultdict(list)
        for x in cells_of(r["rec"]):
            g[x["ads"].get("genders") or "all"].append(x)
        if g.get("women") and g.get("men"):
            w, m = pool(g["women"]), pool(g["men"])
            if P.solid(w) and P.solid(m):
                pairs.append((w, m))
    if not pairs:
        return ""
    ratios = [w["cps"] / m["cps"] for w, m in pairs]
    cheaper = sum(1 for x in ratios if x < 1)
    n = len(pairs)
    if n == 1:
        txt = (f"Where the ads were split by gender, a start from an ad shown to women cost "
               f"{money(pairs[0][0]['cps'])} and one shown to men {money(pairs[0][1]['cps'])}.")
        headline = "Ads to women cost less per start" if cheaper else "Ads to men cost less per start"
    else:
        txt = (f"In {n} recruitments that ran separate ads to women and to men, a start from an ad shown to women cost "
               f"{min(ratios):.2f} to {max(ratios):.2f} times one from an ad shown to men (median {med(ratios):.2f}); "
               f"women were cheaper in {cheaper} of the {n}.")
        headline = ("Ads to women cost less per start" if cheaper == n else "Ads to men cost less per start" if cheaper == 0
                    else "Neither gender was reliably cheaper to reach")
    return (f"    <h2>{headline}</h2><p>{txt}</p>\n    <p class=\"cap\">Counted only where each side had at least "
            f"{P.SOLID_STARTS} starts and ${P.SOLID_SPEND:.0f} of ads.</p>")


MOD_SPEED = """    <div class="how">
      <div class="k">How it works · speed</div>
      <h2>Spending faster in the same place costs more per person</h2>
      <p>Meta shows an ad first to the people most likely to respond to it. The faster a recruitment needs people, the further it has to reach past them, and each extra person costs more. Across our recruitments, doubling an ad set's daily spend in the same place raised its cost per start by about a third.</p>
    </div>
"""


def head(cc, lede, facts, radius):
    name = NAMES[cc]
    the = "the " if cc in THE else ""
    sid = P.slug(name)
    return sid, [f'  <section id="{sid}" role="tabpanel" aria-labelledby="t-{sid}" hidden>',
                 f'    <div class="eyebrow">{esc(name)} · Recruitment cost</div>',
                 f'    <h1>What does it cost to recruit survey respondents in {the}{esc(name)}?</h1>',
                 f'    <p class="lede">{lede}</p>',
                 '    <div class="facts">' + "".join(f"<div><b>{a}</b><span>{esc(b)}</span></div>" for a, b in facts) + "</div>",
                 P.MOD_NUM, MOD_SPEED, P.MOD_GEO if radius else ""]


def review_note(cc, extra):
    N = ['    <div class="note"><h3>For review</h3><ul>']
    N += [f"<li>{x}</li>" for x in extra]
    for r in recs_of(cc):
        pv = P.PRIV.get(r["rec"], {})
        slugs = ", ".join(f"<code>{esc(s)}</code>" for s in pv.get("slugs", []))
        p = pool(cells_of(r["rec"]))
        N.append(f"<li><b>{esc(r['rec'])}</b> · {esc(r.get('tier'))}"
                 f"{' (' + esc(r['tier_reason']) + ')' if r.get('tier_reason') else ''} · {slugs} · "
                 f"{money(p['spend'], True)}, {p['started']:,} started, {p['qualified']:,} qualified</li>")
    N.append("</ul></div>")
    return N


def close(cc, H):
    the = "the " if cc in THE else ""
    H.append(f'    <p class="cta">Planning a study in {the}{esc(NAMES[cc])}? Write to <b>info@vlab.digital</b>.</p>')


def where_section(cc, H, comps, heading=True, mult_map=False):
    """The place index, one table (and map) per connected set of places."""
    small = [c for c in comps[1:] if len(c) < 4]
    comps = [comps[0]] + [c for c in comps[1:] if len(c) >= 4] if comps else []
    for n, comp in enumerate(comps):
        if heading:
            lo = min(comp, key=lambda k: comp[k]["mult"]); hi = max(comp, key=lambda k: comp[k]["mult"])
            H.append(f"    <h2>{esc(short(hi))} cost {times(comp[hi]['mult'])} as much per start as {esc(short(lo))}</h2>"
                     if n == 0 else f"    <h2>{esc(short(hi))} cost {times(comp[hi]['mult'])} as much per start as "
                     f"{esc(short(lo))}</h2><p>These places were not recruited alongside the ones above, so they are "
                     f"compared only with each other.</p>")
        dollars = {k: v["pooled"]["cpq"] for k, v in comp.items() if v["pooled"] and v["pooled"]["qualified"]}
        m = None if len(comp) < 4 or not dollars else multiple_map(cc, dollars, f"map-{cc.lower()}-usd{n}",
                         f"{NAMES[cc]}: advertising cost per qualified respondent in each place", kind="money")
        if m:
            H.append(f"    <figure>{m}</figure>")
        if (mult_map or not dollars) and len(comp) >= 4:
            m = multiple_map(cc, {k: v["mult"] for k, v in comp.items()}, f"map-{cc.lower()}-idx{n}",
                             f"{NAMES[cc]}: cost per start in each place, against the cheapest")
            if m:
                H.append(f"    <figure>{m}</figure>")
        H.append(index_table(comp))
    if comps:
        H.append(f'    <p class="cap">{INDEX_CAP}</p>')
    if small:
        lines = []
        for c in small:
            lo = min(c, key=lambda k: c[k]["mult"]); hi = max(c, key=lambda k: c[k]["mult"])
            both = c[lo]["pooled"] and c[hi]["pooled"] and c[lo]["pooled"]["qualified"] and c[hi]["pooled"]["qualified"]
            lines.append(f"<li>{esc(short(hi))} cost {times(c[hi]['mult'])} as much per start as {esc(short(lo))}"
                         + (f" ({money(c[hi]['pooled']['cpq'])} against {money(c[lo]['pooled']['cpq'])} per qualified "
                            f"respondent)" if both else "") + ".</li>")
        H.append("    <h3 style=\"font:600 16px/1.3 var(--ui);margin:28px 0 4px\">Smaller comparisons</h3>"
                 "<ul style=\"font:400 15.5px/1.55 var(--ui)\">" + "".join(lines) + "</ul>")


# ------------------------------------------------------------------ pattern: general
def page_general(cc):
    G = recs_of(cc, "general")
    ps, s, q = level_stats(G)
    allp = pool([x for r in G for x in cells_of(r["rec"])])
    lede = (f"Recruiting adults in {NAMES[cc]} through Facebook and Instagram ads cost <b>{rng(min(s), max(s))} per "
            f"person who started a survey</b> and <b>{rng(min(q), max(q))} per qualified respondent</b>, across "
            f"{len(ps)} recruitments of the general population. The price varied a lot between recruitments, which "
            f"differed in survey, quotas and size.")
    facts = [(f"{allp['started']:,}", "people who started a survey, general recruitments"),
             (f"{allp['qualified']:,}", "qualified respondents"),
             (money(med(s)), "median cost per start across recruitments"),
             (money(med(q)), "median cost per qualified respondent")]
    comps = place_index(cc)
    sid, H = head(cc, lede, facts, radius=any(PLACES[k]["type"] != "country" for c in comps for k in c))
    H.append("    <h2>What each general recruitment cost</h2>")
    H.append("    <p>Each row is one recruitment: ads shown to adults across the country, screened only on basics such "
             "as age. The rows are sorted by cost per start.</p>")
    H.append(level_table(G))
    H.append('    <p class="cap">Qualified: the share of people who started who met the recruitment\'s quotas and '
             'finished its screening.</p>')
    H.append("    <h2>Where the ads ran</h2>")
    if comps:
        where_section(cc, H, comps, heading=False)
    else:
        H.append("<p>Our recruitments here ran mostly to the whole country, and the few that split the ads between places "
                 "did so on budgets too small to compare, so this page has no comparison between places.</p>")
    H.append(gender_block(G))
    sl = specialised_line(cc, (min(q), max(q)) if q else None)
    if sl:
        H.append("    <h2>Narrower groups</h2>" + sl)
    close(cc, H)
    H += review_note(cc, ["<b>Pattern: general.</b> No dates on the page. The speed module's one-third figure is the "
                          "within-ad-set elasticity in <code>ws-spend-intensity.md</code> and needs a CLAIMS Definition row."])
    H.append("  </section>")
    return sid, NAMES[cc], "\n".join(x for x in H if x)


# ------------------------------------------------------------------ pattern: one common group
def page_group(cc):
    C = recs_of(cc, "common")
    grp = group_label(C[0]) if C else "one group"
    allp = pool([x for r in C for x in cells_of(r["rec"])])
    comps = place_index(cc)
    lede = (f"Recruiting {esc(grp)} in {NAMES[cc]} cost <b>{money(allp['cps'])} per person who started a survey</b> "
            f"and <b>{money(allp['cpq'])} per qualified respondent</b>. It is the only group we have recruited here, "
            f"so this page is about that group, not the general population.")
    facts = [(f"{allp['started']:,}", "people who started a survey"), (f"{allp['qualified']:,}", "qualified respondents"),
             (pct(allp["share"]), "of those who started qualified"),
             (times(max(v["mult"] for c in comps for v in c.values())) if comps else "—", "the widest gap between places")]
    sid, H = head(cc, lede, facts, radius=any(PLACES[k]["type"] != "region" for c in comps for k in c))
    if len(C) == 1:
        H.append(f"    <p><b>Who qualified:</b> {esc(C[0].get('who_qualified', ''))}.</p>")
    where_section(cc, H, comps)
    H.append(gender_block(C))
    close(cc, H)
    H += review_note(cc, ["<b>Pattern: one common group.</b> No dates on the page."])
    H.append("  </section>")
    return sid, NAMES[cc], "\n".join(x for x in H if x)


# ------------------------------------------------------------------ pattern: place story
def page_place(cc):
    comps = place_index(cc)
    G = recs_of(cc, "general")
    Cm = recs_of(cc, "common")
    ps, s, q = level_stats(G)
    big = comps[0] if comps else {}
    lo = min(big, key=lambda k: big[k]["mult"]); hi = max(big, key=lambda k: big[k]["mult"])
    firm = {k: v for k, v in big.items() if v["solid"]}
    fhi = max(firm, key=lambda k: firm[k]["mult"])
    lede = (f"In {NAMES[cc]}, where the ads run matters more than anything else about the cost. A start in "
            f"{esc(short(fhi))} cost <b>{times(firm[fhi]['mult'])}</b> as much as one in {esc(short(lo))}, whoever "
            f"the recruitment was looking for."
            + (f" General recruitments of adults cost <b>{rng(min(s), max(s))}</b> per person who started." if s else ""))
    facts = [(f"{sum(len(c) for c in comps)}", "places compared"),
             (times(firm[fhi]["mult"]), f"{short(fhi)} against {short(lo)}"),
             (rng(min(s), max(s)) if s else "—", f"per start, {len(ps)} general recruitments"),
             (f"{sum(pool(cells_of(r['rec']))['started'] for r in recs_of(cc)):,}", "people who started a survey")]
    radius = any(PLACES[k]["type"] in ("radius_set", "radius_outside", "city_radius") for c in comps for k in c)
    sid, H = head(cc, lede, facts, radius)
    H.append("    <h2>How the places are compared</h2><p>Many of our recruitments here ran the same survey in several "
             "places at once. Within one recruitment, the people sought, the survey and the days are the same, so the "
             "difference between places is the place. We combine every such comparison into one figure per place: "
             "how much a start cost there against the cheapest place. It holds whichever group a recruitment was "
             "looking for, which is why it is a multiple and not a dollar amount.</p>")
    where_section(cc, H, comps, mult_map=True)
    # the spread of the multiple for well-used places: rankings are not fixed
    if G:
        H.append("    <h2>What general recruitment cost</h2>")
        H.append(level_table(G))
        H.append('    <p class="cap">General recruitments: ads to adults, screened only on basics such as age.</p>')
    if Cm:
        cp = [(r, pool(cells_of(r["rec"]))) for r in Cm]
        cp = [(r, p) for r, p in cp if p["started"] >= MIN_PLACE_START and r.get("who_comparable", True)]
        byg = collections.defaultdict(list)
        for r, p in cp:
            byg[group_label(r)].append(p)
        main = [(g, ps_) for g, ps_ in byg.items() if len(ps_) >= 2]
        if main:
            H.append("    <h2>Parents and caregivers</h2><p>" + " ".join(
                f"{len(ps_)} recruitments looked for {esc(g)}. A median {pct(med([p['share'] for p in ps_]))} of the "
                f"people who started qualified, and a qualified respondent cost "
                f"{rng(min(p['cpq'] for p in ps_), max(p['cpq'] for p in ps_))}, mostly depending on where the ads ran."
                for g, ps_ in sorted(main, key=lambda kv: -len(kv[1]))) + "</p>")
    sl = specialised_line(cc, None)
    if sl:
        H.append("    <h2>Narrower groups</h2>" + sl)
    close(cc, H)
    H += review_note(cc, ["<b>Pattern: place story.</b> No dates. Place figures come from a fixed-effects fit "
                          "(log cost per start = recruitment + place, weighted by starts) over every recruitment "
                          "that ran two or more places; rounds flagged <code>ad_arm_confounded_with_side</code> are out."])
    H.append("  </section>")
    return sid, NAMES[cc], "\n".join(x for x in H if x)


# ------------------------------------------------------------------ tiers tab (review)
def tiers_page():
    H = ['  <section id="tiers" role="tabpanel" aria-labelledby="t-tiers" hidden>',
         '    <div class="eyebrow">For review · Not a page</div>',
         '    <h1>Which recruitments count as general</h1>',
         '    <p class="lede">Every recruitment gets one tier, by rule (<code>merge_cells.py</code>, '
         '<code>audience_tier</code>), overridable by hand in <code>scripts/data/tier-overrides.json</code>.</p>',
         '    <dl><dt>General</dt><dd>Broad ads (no Meta interest targeting on more than a quarter of the spend), screened '
         'only on basics: age, gender, residence, language, consent, a phone number, an attention check, education.</dd>'
         '<dt>Common</dt><dd>Parents and caregivers, by the child\'s age (and the child\'s gender where screened). '
         'Sets a figure only on a page whose heading names the group.</dd>'
         '<dt>Specialised</dt><dd>Anything narrower. Never sets a figure; one general sentence per country.</dd></dl>']
    rows = []
    for r in sorted(CRIT.values(), key=lambda r: (r["country"], r.get("first") or "")):
        if r.get("round") == "excluded":
            continue
        p = pool(cells_of(r["rec"]))
        pv = P.PRIV.get(r["rec"], {})
        rows.append(tr([(f"{esc(r['rec'])}<span class=\"id\">{esc(' '.join(pv.get('slugs', [])))}</span>", 0),
                        (f"<b>{esc(r.get('tier'))}</b>", 0), (esc(r.get("tier_reason") or ""), 0),
                        (esc(r.get("who_qualified") or ""), 0), (money(p["spend"], True), 1),
                        (money(p["cps"]) if p["started"] else "—", 1)]))
    H.append(table([("Recruitment", 0), ("Tier", 0), ("Why", 0), ("Who qualified", 0), ("Ad spend", 1), ("Per start", 1)], rows))
    H.append("  </section>")
    return "\n".join(H)


if __name__ == "__main__":
    ccs = sys.argv[1:] or list(PATTERN)
    fn = {"general": page_general, "group": page_group, "place": page_place}
    secs, tabs = [], []
    for cc in ccs:
        sid, name, html = fn[PATTERN[cc]](cc)
        secs.append(html); tabs.append((sid, name))
    secs.append(tiers_page()); tabs.append(("tiers", "Tiers"))
    P.assemble(secs, tabs, "Pilot v11 · three patterns, no dates")
