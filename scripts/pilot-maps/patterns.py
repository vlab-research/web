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
SMALL_RUN = 500.0                               # a recruitment under this much ad spend is a short test run

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


def concordance(comp, recs, keys):
    """Share of place pairs ranked the same way in every recruitment that has both (solid places only)."""
    agree = total = 0
    ks = sorted(keys)
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            signs = {comp[r][a][0] < comp[r][b][0] for r in recs
                     if a in comp[r] and b in comp[r] and P.solid(comp[r][a][1]) and P.solid(comp[r][b][1])}
            if signs:
                total += 1
                agree += len(signs) == 1
    return agree / total if total else None


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


def families(comp):
    """Recruitments that compared the same places, grouped: [(recs, places)] with 3+ shared places first."""
    fams = []
    for rec, ps in sorted(comp.items(), key=lambda kv: CRIT[kv[0]]["first"]):
        keys = set(ps)
        for f in fams:
            if len(keys & f[1]) >= 3:
                f[0].append(rec); f[1].update(keys)
                break
        else:
            fams.append(([rec], set(keys)))
    return sorted(fams, key=lambda f: (-len(f[0]), -sum(comp[r][k][1]["spend"] for r in f[0] for k in comp[r])))


def times(m):
    return "1×" if 0.95 <= m < 1.05 else f"{m:.1f}×" if m < 10 else f"{m:.0f}×"


def matrix_table(comp, recs, keys):
    """Places down, recruitments across, each cell the multiple of that recruitment's cheapest place."""
    geo = {}
    for k in keys:
        v = [math.log(comp[r][k][0]) for r in recs if k in comp[r] and P.solid(comp[r][k][1])]
        v = v or [math.log(comp[r][k][0]) for r in recs if k in comp[r]]
        geo[k] = math.exp(statistics.mean(v))
    order = sorted(keys, key=lambda k: geo[k])
    head = [("Where the ads ran", 0)] + [(span(CRIT[r]["first"], CRIT[r]["last"]), 1) for r in recs]
    rows = []
    for k in order:
        cells = [(esc(short(k)) + f'<span class="id">{esc(PLACES[k]["label"])}</span>', 0)]
        for r in recs:
            if k not in comp[r]:
                cells.append(("", 1))
            else:
                m, p = comp[r][k]
                cells.append((times(m) if P.solid(p) else f'<span style="color:var(--ink-3)">({times(m)})</span>', 1))
        rows.append(tr(cells))
    return table(head, rows), geo, order


def multiples_rows(ps):
    rows = []
    for k, (m, p) in sorted(ps.items(), key=lambda kv: kv[1][0]):
        rows.append(tr([(esc(short(k)) + f'<span class="id">{esc(PLACES[k]["label"])}</span>', 0), (f"{p['started']:,}", 1), (money(p["spend"], True), 1),
                        (money(p["cps"]), 1), (f"<b>{times(m)}</b>", 1)], thin=not P.solid(p)))
    return table([("Where the ads ran", 0), ("Started", 1), ("Ad spend", 1), ("Per start", 1),
                  ("Against the cheapest", 1)], rows)


# ------------------------------------------------------------------ maps shaded by multiple
MSTEPS = [(1.5, ".3", "cheapest (under 1.5×)"), (3, ".5", "1.5–3×"), (6, ".7", "3–6×"), (1e9, "1", "6× or more")]


def mstep(m):
    return next(s for s in MSTEPS if m < s[0])


def mlegend(body, y):
    body.append(B.text(0, y, "Cost per start, against the cheapest place", "gm-eye"))
    for i, (_, op, lab) in enumerate(MSTEPS):
        xx = i * 170
        body.append(f'<rect x="{xx}" y="{y + 10}" width="16" height="12" style="fill:var(--data);fill-opacity:{op}"/>')
        body.append(B.text(xx + 22, y + 20, lab, "gm-tiny"))
    return y + 34


def multiple_map(cc, mult, label, title):
    """Regions or radius areas shaded by their multiple of the cheapest place."""
    land = P.a0(cc)
    units = P.a1s(cc)
    geoms, pins = [], []
    for k, m in mult.items():
        pl = PLACES[k]
        if pl["type"] in ("region", "radius_outside"):   # outside: the region is shaded, its radius areas drawn on top
            for rn in pl.get("regions", []):
                u = P.match_region(cc, rn, units)
                if u:
                    geoms.append((units[u][1], m, rn + (", outside" if pl["type"] == "radius_outside" else "")))
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
        body.append(B.path(F.g(g), "gm-circ", f' style="fill:var(--data);fill-opacity:{mstep(m)[1]}"'))
    for k, (p, g) in units.items():
        body.append(B.path(F.g(g), "gm-adm"))
    body.append(B.path(F.g(land), "gm-outline"))
    for lo, la, r, m in sorted(pins, key=lambda t: -(t[2] or 0)):
        op = mstep(m)[1]
        g = F.g(B.circle(lo, la, r or 16), clip=False, simplify=0.2)
        if math.sqrt(max(g.area, 0) / math.pi) < 2.2:
            x, y = F.xy(lo, la)
            body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" style="fill:var(--data);fill-opacity:{op}"/>')
        else:
            body.append(B.path(g, "gm-circ", f' style="fill:var(--data);fill-opacity:{op}"'))
    for g, m, rn in geoms:
        pt = g.representative_point()
        x, y = F.xy(pt.x, pt.y)
        if 0 < x < W and 0 < y < H:
            body.append(B.text(x, y - 3, rn.replace(" State", ""), "gm-lab2 gm-halo", "middle"))
            body.append(B.text(x, y + 12, times(m), "gm-val gm-halo", "middle"))
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
    y = mlegend(body, H + 6)
    desc = "; ".join(f"{PLACES[k]['label']}: {times(m)}" for k, m in sorted(mult.items(), key=lambda kv: kv[1]))
    return B.svg(W, y + 4, title, desc, body, label)


# ------------------------------------------------------------------ blocks
def level_table(recs):
    rows = []
    for r in recs:
        p = pool(cells_of(r["rec"]))
        if p["started"] < MIN_PLACE_START:
            continue
        rows.append(tr([(span(r["first"], r["last"]), 0), (esc(r.get("who_qualified") or ""), 0),
                        (money(p["spend"], True), 1), (f"{p['started']:,}", 1), (money(p["cps"]), 1),
                        (pct(p["share"]) if r.get("who_comparable", True) else "—", 1),
                        (money(p["cpq"]) if r.get("who_comparable", True) else "—", 1)], thin=p["spend"] < SMALL_RUN))
    return table([("When", 0), ("Who qualified", 0), ("Ad spend", 1), ("Started", 1), ("Per start", 1),
                  ("Qualified", 1), ("Per qualified", 1)], rows)


def scale_split(recs):
    """Short test runs against full runs: medians of per-recruitment cost per start and per qualified."""
    small, full = [], []
    for r in recs:
        p = pool(cells_of(r["rec"]))
        if p["started"] < MIN_PLACE_START:
            continue
        (small if p["spend"] < SMALL_RUN else full).append((r, p))
    return small, full


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
    cmp_ = f", against {rng(*ref)} in the general recruitments above" if ref else ""
    n = len(sp)
    return (f"<p>{n} recruitment{'s' if n > 1 else ''} here looked for narrower groups ({esc(what)}). "
            f"{'They' if n > 1 else 'It'} cost {rng(min(q), max(q))} per qualified respondent{cmp_}. "
            f"Figures for narrow groups say more about the group than about {'the country' if cc not in THE else 'the country'}, "
            f"so they are not broken down here.</p>")


def gender_block(recs):
    pairs = []
    for r in recs:
        g = collections.defaultdict(list)
        for x in cells_of(r["rec"]):
            g[x["ads"].get("genders") or "all"].append(x)
        if g.get("women") and g.get("men"):
            w, m = pool(g["women"]), pool(g["men"])
            if P.solid(w) and P.solid(m):
                pairs.append((r, w, m))
    if not pairs:
        return ""
    rows = [tr([(span(r["first"], r["last"]), 0), (money(w["cps"]), 1), (money(m["cps"]), 1), (f"{w['cps'] / m['cps']:.2f}", 1)])
            for r, w, m in pairs]
    cheaper = sum(1 for _, w, m in pairs if w["cps"] < m["cps"])
    head = ("Ads to women cost less per start" if cheaper == len(pairs) else
            "Ads to men cost less per start" if cheaper == 0 else "Neither gender was reliably cheaper to reach")
    return (f"    <h2>{head}</h2>\n" + table([("Recruitment", 0), ("Women, per start", 1), ("Men, per start", 1),
                                               ("Ratio", 1)], rows) +
            f'\n    <p class="cap">Recruitments that ran separate ads to women and to men, each side with at least '
            f'{P.SOLID_STARTS} starts and ${P.SOLID_SPEND:.0f} of ads.</p>')


MOD_SPEED = """    <div class="how">
      <div class="k">How it works · speed</div>
      <h2>Spending faster in the same place costs more per person</h2>
      <p>Meta shows an ad first to the people most likely to respond to it. A short run with a small budget reaches only those people, and they are cheap. A run that needs thousands of respondents in a few weeks has to keep reaching further, to people less likely to respond, and each one costs more. Across our recruitments, doubling an ad set's daily spend in the same place raised its cost per start by about a third.</p>
      <p>So the cost of a short test run is a floor, not a forecast. Plan a full study on the figures from full runs.</p>
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


# ------------------------------------------------------------------ pattern: general
def page_general(cc):
    G = recs_of(cc, "general")
    small, full = scale_split(G)
    allp = pool([x for r in G for x in cells_of(r["rec"])])
    fs = [p["cps"] for _, p in full]
    ss = [p["cps"] for _, p in small]
    fq = [p["cpq"] for r, p in full if r.get("who_comparable", True)]
    lede = (f"Recruiting adults in {NAMES[cc]} through Facebook and Instagram ads cost "
            + (f"<b>{rng(min(fs), max(fs))} per person who started a survey</b> in the {len(full)} full-scale "
               f"recruitment{'s' if len(full) > 1 else ''} we ran for the general population"
               + (f", and <b>{rng(min(fq), max(fq))} per qualified respondent</b>" if fq else "") if full else "")
            + (f". Short test runs of under ${SMALL_RUN:.0f} found people for {rng(min(ss), max(ss))} each" if ss else "")
            + f", between {P.month(allp['first'])} and {P.month(allp['last'])}.")
    facts = [(f"{allp['started']:,}", "starts from general recruitments"),
             (f"{allp['qualified']:,}", "qualified respondents"),
             (money(allp["spend"], True), "advertising spend, general recruitments"),
             (f"{len(G)}", f"general recruitments, {len(full)} full-scale")]
    comp = {k: v for k, v in comparisons(cc).items() if CRIT[k].get("tier") == "general"}
    sid, H = head(cc, lede, facts, radius=bool(comp))
    H.append(f"    <h2>{'Full runs cost ' + rng(min(fs), max(fs)) + ' per start; test runs cost cents' if full and ss else 'What each recruitment cost'}</h2>")
    H.append("    <p>Each row is one general recruitment: ads shown to adults across the country, screened only on basics "
             "such as age. Short runs with small budgets (in grey) reach only the most responsive people, so they are "
             "cheaper than a full study will be.</p>")
    H.append(level_table(G))
    H.append(f'    <p class="cap">Qualified: the share of people who started who met the recruitment\'s quotas and '
             f'finished its screening. Grey rows: recruitments with under ${SMALL_RUN:.0f} of ads in total.</p>')
    if comp:
        H.append("    <h2>Where the ads ran</h2>")
        for rec, ps in comp.items():
            H.append(f'    <p class="cap">{span(CRIT[rec]["first"], CRIT[rec]["last"])}</p>' + multiples_rows(ps))
    else:
        tiny = [r for r in G if len({x["place"] for x in cells_of(r["rec"])}) > 1]
        H.append("    <h2>Where the ads ran</h2><p>The full-scale recruitments here ran to the whole country"
                 + (f"; {len(tiny)} test run{'s' if len(tiny) > 1 else ''} split the ads between places, but on "
                    f"budgets too small to compare" if tiny else "") + ", so this page has no comparison between places.</p>")
    H.append(gender_block(G))
    sl = specialised_line(cc, (min(fq), max(fq)) if fq else None)
    if sl:
        H.append("    <h2>Narrower groups</h2>" + sl)
    close(cc, H)
    H += review_note(cc, ["<b>Pattern: general.</b> Only general recruitments set figures. The speed module is new: "
                          "its one-third figure is the within-ad-set elasticity in <code>ws-spend-intensity.md</code> "
                          "and needs a CLAIMS Definition row."])
    H.append("  </section>")
    return sid, NAMES[cc], "\n".join(x for x in H if x)


# ------------------------------------------------------------------ pattern: one common group
def page_group(cc):
    C = recs_of(cc, "common")
    grp = group_label(C[0]) if C else "one group"
    allp = pool([x for r in C for x in cells_of(r["rec"])])
    comp = comparisons(cc)
    one = len(C) == 1
    lede = (f"Recruiting {esc(grp)} in {NAMES[cc]} cost <b>{money(allp['cps'])} per person who started a survey</b> "
            f"and <b>{money(allp['cpq'])} per qualified respondent</b>"
            + (f", in one recruitment in {span(C[0]['first'], C[0]['last'])}" if one else
               f", across {len(C)} recruitments between {P.month(allp['first'])} and {P.month(allp['last'])}")
            + ". It is the only group we have recruited here, so this page is about that group, not the general population.")
    facts = [(f"{allp['started']:,}", "people who started a survey"),
             (f"{allp['qualified']:,}", "qualified respondents"),
             (money(allp["spend"], True), "advertising spend"), (pct(allp["share"]), "of those who started qualified")]
    radius = any(PLACES[k]["type"] in ("radius_set", "radius_outside", "city_radius") for v in comp.values() for k in v)
    sid, H = head(cc, lede, facts, radius)
    H.append(f"    <p><b>Who qualified:</b> {esc(C[0].get('who_qualified', ''))}.</p>" if one else "")
    for rec, ps in comp.items():
        firm = {k: v for k, v in ps.items() if P.solid(v[1])}
        lo = min(firm, key=lambda k: firm[k][0]); hi = max(firm, key=lambda k: firm[k][0])
        H.append(f"    <h2>{esc(short(hi))} cost {times(firm[hi][0])} as much per start as {esc(short(lo))}</h2>")
        H.append("    <p>All of these places were recruiting the same people, with the same survey, on the same days, "
                 "so the differences are the places. Each is shown against the cheapest.</p>")
        m = multiple_map(cc, {k: v[0] for k, v in ps.items()}, f"map-{cc.lower()}-mult",
                         f"{NAMES[cc]}: cost per start in each place, against the cheapest, in one recruitment")
        if m:
            H.append(f"    <figure>{m}</figure>")
        H.append(multiples_rows(ps))
    H.append(gender_block(C))
    close(cc, H)
    H += review_note(cc, ["<b>Pattern: one common group.</b> The group is in the lede; nothing here is offered as a "
                          "general-population figure."])
    H.append("  </section>")
    return sid, NAMES[cc], "\n".join(x for x in H if x)


def widest(comp):
    best = (1.0, None, None, None)
    for rec, ps in comp.items():
        firm = {k: v for k, v in ps.items() if P.solid(v[1])}
        lo = min(firm, key=lambda k: firm[k][0]); hi = max(firm, key=lambda k: firm[k][0])
        if firm[hi][0] > best[0]:
            best = (firm[hi][0], rec, lo, hi)
    return best


def page_place(cc):
    comp = comparisons(cc)
    fams = families(comp)
    G = recs_of(cc, "general")
    Cm = recs_of(cc, "common")
    small, full = scale_split(G)
    gs = [p["cps"] for _, p in small + full]
    top = widest(comp)
    allp = pool([x for r in G for x in cells_of(r["rec"])])
    lede = (f"In {NAMES[cc]}, where the ads run matters more than anything else about the cost. Within a single "
            f"recruitment, one place cost <b>{'more than 100 times' if top[0] > 100 else times(top[0])} as much per "
            f"person who started</b> as another. "
            + (f"General recruitments of adults, all of them short runs, found people for <b>{rng(min(gs), max(gs))}</b> "
               f"per start." if gs else ""))
    facts = [(f"{len(comp)}", "recruitments that ran the same survey in several places at once"),
             (times(top[0]), f"the widest gap: {short(top[3])} against {short(top[2])}"),
             (rng(min(gs), max(gs)) if gs else "—", f"per start in {len(G)} short general recruitments"),
             (f"{sum(pool(cells_of(r['rec']))['started'] for r in recs_of(cc)):,}", "people who started a survey")]
    radius = any(PLACES[k]["type"] in ("radius_set", "radius_outside", "city_radius") for v in comp.values() for k in v)
    sid, H = head(cc, lede, facts, radius)
    H.append("    <h2>How to read the comparisons</h2><p>Each comparison below comes from one recruitment: the same "
             "survey, looking for the same people, on the same days, in several places at once. So the difference "
             "between places is the place, even when the recruitment was looking for a particular group. We show each "
             "place as a multiple of the cheapest place in that recruitment, not in dollars, because the dollar level "
             "depends on who was being recruited.</p>")
    # repeated comparisons first, then the single recruitments with the most solid, whole-region places
    multi = [f for f in fams if len(f[0]) >= 2]
    single = sorted([f for f in fams if len(f[0]) == 1],
                    key=lambda f: (-sum(P.solid(v[1]) for v in comp[f[0][0]].values()),
                                   -all(PLACES[k]["type"] in ("region", "country") for k in comp[f[0][0]])))
    for n, (recs, keys) in enumerate(multi[:1] + single[:2]):
        if len(recs) >= 2:
            t, geo, order = matrix_table(comp, recs, keys)
            c = concordance(comp, recs, keys)
            steady = c is not None and c >= 0.8
            H.append(f"    <h2>The same places, {len(recs)} times: "
                     f"{'the order held' if steady else 'the order moved'}</h2>")
            H.append(f"<p>The same {len(keys)} places were recruited side by side {len(recs)} times between "
                     f"{P.month(CRIT[recs[0]]['first'])} and {P.month(CRIT[recs[-1]]['last'])}. "
                     + (f"{esc(short(order[0]))} was the cheapest and {esc(short(order[-1]))} the dearest; "
                        f"{c:.0%} of pairs of places kept the same order every time. " if steady else
                        f"Only {c:.0%} of pairs of places kept the same order every time, so read any one "
                        f"recruitment's ranking with care. ")
                     + "</p>")
            m = multiple_map(cc, geo, f"map-{cc.lower()}-fam{n}",
                             f"{NAMES[cc]}: cost per start against the cheapest place, averaged over {len(recs)} recruitments")
            if m:
                H.append(f"    <figure>{m}</figure>")
            H.append(t)
            H.append('    <p class="cap">Each column is one recruitment; each figure is that place\'s cost per start '
                     'divided by the cheapest solid place\'s in the same recruitment. In brackets: under '
                     f'{P.SOLID_STARTS} starts or ${P.SOLID_SPEND:.0f} of ads. The map shows the geometric mean '
                     'across recruitments.</p>')
        else:
            rec = recs[0]; ps = comp[rec]
            firm = {k: v for k, v in ps.items() if P.solid(v[1])}
            lo = min(firm, key=lambda k: firm[k][0]); hi = max(firm, key=lambda k: firm[k][0])
            H.append(f"    <h2>{span(CRIT[rec]['first'], CRIT[rec]['last'])}: {esc(short(hi))} cost "
                     f"{times(firm[hi][0])} as much as {esc(short(lo))}</h2>")
            m = multiple_map(cc, {k: v[0] for k, v in ps.items()}, f"map-{cc.lower()}-fam{n}",
                             f"{NAMES[cc]}: cost per start against the cheapest place, {span(CRIT[rec]['first'], CRIT[rec]['last'])}")
            if m:
                H.append(f"    <figure>{m}</figure>")
            H.append(multiples_rows(ps))
    # a solid place that was cheapest in one recruitment and dear in another
    seen = collections.defaultdict(list)
    for rec, ps in comp.items():
        firm = {k: v for k, v in ps.items() if P.solid(v[1])}
        cheapest = min(firm, key=lambda k: firm[k][0])
        for k, (m, p) in firm.items():
            seen[k].append((rec, k == cheapest, m))
    flips = [(k, v) for k, v in seen.items() if any(c for _, c, _ in v) and any(m >= 2 for _, _, m in v)]
    if flips:
        k, v = max(flips, key=lambda kv: max(m for _, _, m in kv[1]))
        dear = max(v, key=lambda t: t[2]); cheap = next(t for t in v if t[1])
        H.append(f"    <h2>A cheap place is not cheap for good</h2><p>{esc(short(k))} was the cheapest place in "
                 f"{span(CRIT[cheap[0]]['first'], CRIT[cheap[0]]['last'])}, and cost {times(dear[2])} the cheapest "
                 f"place in {span(CRIT[dear[0]]['first'], CRIT[dear[0]]['last'])}. Rankings move with the season, "
                 f"the competition for ad space and how hard a recruitment pushes, so plan with a margin.</p>")
    if G:
        H.append("    <h2>What general recruitment cost</h2>")
        H.append(level_table(G))
        H.append(f'    <p class="cap">General recruitments: ads to adults, screened only on basics such as age. '
                 f'Grey rows: under ${SMALL_RUN:.0f} of ads. None of these was a full-scale run, so read them as a floor.</p>')
    if Cm:
        cp = [(r, pool(cells_of(r["rec"]))) for r in Cm]
        cp = [(r, p) for r, p in cp if p["started"] >= MIN_PLACE_START and r.get("who_comparable", True)]
        byg = collections.defaultdict(list)
        for r, p in cp:
            byg[group_label(r)].append(p)
        main = [(g, ps) for g, ps in byg.items() if len(ps) >= 2]
        if main:
            H.append("    <h2>Parents and caregivers</h2><p>" + " ".join(
                f"{len(ps)} recruitments looked for {esc(g)}. A median {pct(med([p['share'] for p in ps]))} of the "
                f"people who started qualified, and a qualified respondent cost {rng(min(p['cpq'] for p in ps), max(p['cpq'] for p in ps))} "
                f"depending on where and when." for g, ps in sorted(main, key=lambda kv: -len(kv[1]))) + "</p>")
    sl = specialised_line(cc, None)
    if sl:
        H.append("    <h2>Narrower groups</h2>" + sl)
    close(cc, H)
    H += review_note(cc, ["<b>Pattern: place story.</b> Dollar figures come only from general recruitments; every "
                          "place figure is a multiple inside one recruitment, so it holds whichever group was sought.",
                          "Left out of the comparisons: rounds whose ad arm was confounded with the side of a radius "
                          "line (flag <code>ad_arm_confounded_with_side</code>), and any recruitment with fewer than "
                          f"two places of {P.SOLID_STARTS}+ starts and ${P.SOLID_SPEND:.0f}+ of ads."])
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
    P.assemble(secs, tabs, "Pilot v10 · three patterns")
