#!/usr/bin/env python3
"""United States country page (D-032 recipe): data file + targeting map.

    ../../geo/venv/bin/python build.py            # from raw/*.tsv already pulled
    ../../geo/venv/bin/python build.py --fetch    # re-pull raw/ first (SELECT only)
    ../../geo/venv/bin/python build.py --png      # also render the review PNG

Study on the page: gw-marijuana-screener (767be4cc-...), 8 May - 7 Nov 2023.

Cost per group = (report lifetime_spent + spend of the 40 ad sets the study ran
8-22 May before collapsing to 10 strata) / report current_participants.
The 40 early ad sets carry the same location and gender in their ids and the
same state lists, so their spend is assigned by id; with it the groups add up
to Meta's reported spend to the cent ($12,758.89).
"""
import csv, json, os, subprocess, sys
from collections import OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
SP = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(SP, "geo"))
import build_maps as bm  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

csv.field_size_limit(10**9)
SID = "767be4cc-c076-41c0-b986-03d77602ebc5"
SLUG = "gw-marijuana-screener"

Q = {
    "adopt-gw.tsv": f"SELECT created, details::string FROM adopt_reports WHERE study_id='{SID}' "
                    "AND report_type='FACEBOOK_ADOPT' ORDER BY created DESC LIMIT 1",
    "gw-insights.tsv": "WITH x AS (SELECT c.key AS camp, s.key AS strat, coalesce(s.value->>'date_start', "
                       "e.period_start::date::string) AS d, max((s.value->>'spend')::float8) AS spend, "
                       "max((s.value->>'impressions')::float8) AS imp FROM recruitment_data_events e, "
                       "jsonb_each(e.data) AS c, jsonb_each(c.value) AS s WHERE e.study_id='" + SID + "' AND "
                       "jsonb_typeof(c.value)='object' AND jsonb_typeof(s.value)='object' AND s.value->>'spend' "
                       "IS NOT NULL GROUP BY 1,2,3) SELECT camp, strat, substr(d,1,7) AS mon, count(*) days, "
                       "min(d), max(d), sum(spend), sum(imp) FROM x GROUP BY 1,2,3 ORDER BY 2,3",
    "gw-conf-history.tsv": f"SELECT conf_type, created, conf::string FROM study_confs WHERE study_id='{SID}' AND "
                           "conf_type IN ('strata','recruitment','general','creatives','inference_data','audiences') "
                           "ORDER BY created",
    "gw-qualified-by-month.tsv": "WITH u AS (SELECT user_id, max(CASE WHEN variable='md:stratum_location' THEN "
                                 "value#>>'{}' END) loc, max(CASE WHEN variable='md:stratum_gender' THEN value#>>'{}' "
                                 "END) g, min(CASE WHEN variable='sguid' THEN timestamp END) tq FROM inference_data "
                                 f"WHERE study_id='{SID}' GROUP BY 1) SELECT loc, g, substr(tq::string,1,7) mon, "
                                 "count(*) FROM u WHERE tq IS NOT NULL GROUP BY 1,2,3 ORDER BY 1,2,3",
    "gw-funnel-people.tsv": "WITH u AS (SELECT user_id, max(CASE WHEN variable='md:stratum_location' THEN "
                            "value#>>'{}' END) loc, max(CASE WHEN variable='md:stratum_gender' THEN value#>>'{}' END) g, "
                            "max(CASE WHEN variable='email' THEN 1 ELSE 0 END) em, max(CASE WHEN "
                            "variable='marijuana_days' THEN 1 ELSE 0 END) md, max(CASE WHEN variable='sguid' THEN 1 "
                            f"ELSE 0 END) q FROM inference_data WHERE study_id='{SID}' GROUP BY 1) SELECT loc, g, "
                            "count(*), sum(md), sum(em), sum(q) FROM u GROUP BY 1,2 ORDER BY 1,2",
}


def fetch():
    for name, sql in Q.items():
        out = subprocess.run(["kubectl", "exec", "-n", "vprod", "gbv-cockroachdb-0", "--", "/cockroach/cockroach",
                              "sql", "--insecure", "--format=tsv", "--database=vlab", "-e", sql],
                             check=True, capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout
        open(os.path.join(RAW, name), "w").write(out)
        print("fetched", name)


def rows(name):
    return list(csv.reader(open(os.path.join(RAW, name)), delimiter="\t"))[1:]


# Page names for the study's five location strata. The study's own labels are raw
# ids only. Order = the order the page lists them (by cost, set below).
GROUP_NAME = {
    "eastern": "15 states in the South and East",
    "focal_rec": "5 Western states",
    "midwest": "14 states, Plains to Mountain West",
    "ne_rec": "9 Northeastern states and DC",
    "other_rec": "7 states, Alaska to Michigan",
}
POSTAL = None  # filled from Natural Earth


def compute():
    created, det = rows("adopt-gw.tsv")[0]
    rep = json.loads(det)
    hist = rows("gw-conf-history.tsv")
    strata = [json.loads(c) for t, _, c in hist if t == "strata"][-1]
    strata_created = [cr for t, cr, _ in hist if t == "strata"][-1]

    # geography: one state list per location, identical across gender and across every strata version
    geo = {}
    for s in strata:
        loc = s["metadata"]["stratum_location"]
        g = s["facebook_targeting"]["geo_locations"]
        assert set(g) == {"regions", "location_types"}, g
        assert not s["facebook_targeting"].get("excluded_geo_locations")
        names = sorted(r["name"] for r in g["regions"])
        assert geo.setdefault(loc, names) == names
    for t, cr, c in hist:
        if t == "strata":
            for s in json.loads(c):
                loc = s["metadata"]["stratum_location"]
                assert sorted(r["name"] for r in s["facebook_targeting"]["geo_locations"]["regions"]) == geo[loc], cr
    allst = sum(geo.values(), [])
    assert len(allst) == len(set(allst)) == 51, "groups must partition the 50 states + DC"

    # spend: report per stratum, plus the 40 early ad sets by id
    ins = rows("gw-insights.tsv")
    ins_total = round(sum(float(r[6]) for r in ins), 2)
    early = defaultdict(float)
    ins_by_strat = defaultdict(float)
    for camp, strat, mon, days, d0, d1, sp, imp in ins:
        ins_by_strat[strat] += float(sp)
        if "-race-" in strat:
            p = strat.split("-")
            early[f"location-{p[1]}-gender-{p[3]}"] += float(sp)
    for k, v in rep.items():  # the report equals Insights per stratum
        assert abs(v["lifetime_spent"] - ins_by_strat[k]) < 0.01, (k, v["lifetime_spent"], ins_by_strat[k])
    early_total = round(sum(early.values()), 2)
    rep_spend = round(sum(v["lifetime_spent"] for v in rep.values()), 2)
    assert abs(rep_spend + early_total - ins_total) < 0.01

    cell = {}
    for k, v in rep.items():
        loc, g = bm.part(k.replace("location-", "location:").replace("-gender-", ",gender:"), "location"), k[-1]
        cell[(loc, g)] = dict(spend=v["lifetime_spent"] + early[k], report_spend=v["lifetime_spent"],
                              early_spend=early[k], qualified=v["current_participants"])

    def pool(keyf):
        acc = OrderedDict()
        for (loc, g), c in sorted(cell.items()):
            a = acc.setdefault(keyf(loc, g), dict(spend=0.0, qualified=0))
            a["spend"] += c["spend"]
            a["qualified"] += c["qualified"]
        for a in acc.values():
            a["spend"] = round(a["spend"], 2)
            a["cost"] = round(a["spend"] / a["qualified"], 2)
        return acc

    gname = {"1": "Men", "2": "Women"}  # Meta genders: 1 = men, 2 = women
    by_group = pool(lambda l, g: l)
    by_gender = pool(lambda l, g: gname[g])
    by_group_gender = pool(lambda l, g: (l, gname[g]))
    total_spend = round(sum(c["spend"] for c in cell.values()), 2)
    total_q = sum(c["qualified"] for c in cell.values())
    assert abs(total_spend - ins_total) < 0.01

    # people who started, by gender (anyone with a row in inference_data carrying the ad's metadata)
    started = defaultdict(int)
    for loc, g, n, md, em, q in rows("gw-funnel-people.tsv"):
        if g != "NULL":
            started[gname[g]] += int(n)
    funnel = {g: dict(started=started[g], qualified=by_gender[g]["qualified"],
                      qualified_share_pct=round(100 * by_gender[g]["qualified"] / started[g]),
                      spend_per_started=round(by_gender[g]["spend"] / started[g], 2)) for g in ("Men", "Women")}

    # month by month: Insights spend in the month / people who reached the enrolment link that month
    msp = defaultdict(float)
    mspg = defaultdict(float)
    for camp, strat, mon, days, d0, d1, sp, imp in ins:
        msp[mon] += float(sp)
        mspg[(gname[strat.split("gender-")[1][0]], mon)] += float(sp)
    mq = defaultdict(int)
    mqg = defaultdict(int)
    for loc, g, mon, n in rows("gw-qualified-by-month.tsv"):
        if loc == "NULL":
            continue
        mq[mon] += int(n)
        mqg[(gname[g], mon)] += int(n)
    by_month = OrderedDict()
    for m in sorted(msp):
        by_month[m] = dict(spend=round(msp[m], 2), qualified=mq[m], cost=round(msp[m] / mq[m], 2),
                           men=round(mspg[("Men", m)] / mqg[("Men", m)], 2),
                           women=round(mspg[("Women", m)] / mqg[("Women", m)], 2))

    return dict(created=created, strata_created=strata_created, geo=geo, rep=rep, early=dict(early),
                early_total=early_total, rep_spend=rep_spend, ins_total=ins_total, by_group=by_group,
                by_gender=by_gender, by_group_gender=by_group_gender, total_spend=total_spend, total_q=total_q,
                funnel=funnel, by_month=by_month, hist=hist)


# --------------------------------------------------------------------------- map
def opacity(c, lo=1.5, hi=3.5):
    return round(0.18 + 0.82 * max(0.0, min(1.0, (c - lo) / (hi - lo))), 2)


def us_map(D):
    st = bm.admin1("USA", "name")
    postal = {f["properties"]["name"]: f["properties"]["postal"] for f in bm.A1 if f["properties"]["adm0_a3"] == "USA"}
    meta2ne = {"Washington D. C.": "District of Columbia"}
    grp_of = {}
    for loc, names in D["geo"].items():
        for n in names:
            grp_of[meta2ne.get(n, n)] = loc
    assert set(grp_of) == set(st), set(st) ^ set(grp_of)
    order = sorted(D["by_group"], key=lambda k: D["by_group"][k]["cost"])

    W = 760
    body = [bm.text(0, 12, "United States, 2023 · five groups of whole states", "gm-eye")]
    lower = unary_union([g for n, g in st.items() if n not in ("Alaska", "Hawaii")])
    f = bm.Frame(-96.5, 38.6, lower, (0, 26, 760, 440), pad=4)

    def draw(frame, names, simp=0.3):
        out = []
        for n in names:
            c = D["by_group"][grp_of[n]]["cost"]
            out.append(bm.path(frame.g(st[n], simplify=simp), "gm-circ",
                               f' fill-opacity="{opacity(c)}" style="stroke-width:.6"'))
        for loc in order:
            u = unary_union([st[n] for n in names if grp_of[n] == loc])
            if not u.is_empty:
                out.append(bm.path(frame.g(u, simplify=simp), "gm-outline", ' style="stroke:var(--ink-2);stroke-width:1.4"'))
        return out

    body += draw(f, [n for n in st if n not in ("Alaska", "Hawaii")])

    # labels: one per group, at a hand-picked point inside it (lon, lat, dx, dy, anchor, leader)
    LAB = {"focal_rec": (-117.0, 39.3, 0, 0, "middle", False),
           "midwest": (-100.0, 41.6, 0, 0, "middle", False),
           "eastern": (-86.6, 32.9, 0, 0, "middle", False),
           "other_rec": (-110.4, 34.2, 0, 0, "middle", False),
           "ne_rec": (-74.6, 42.9, 58, 56, "start", True)}
    for loc, (lon, lat, dx, dy, an, lead) in LAB.items():
        px, py = f.xy(lon, lat)
        tx, ty = px + dx, py + dy
        if lead:
            body.append(f'<path class="gm-lead" d="M{px:.1f},{py:.1f}L{tx - 3:.1f},{ty - 12:.1f}"/>')
        body.append(bm.text(tx, ty - 2, bm.money(D["by_group"][loc]["cost"]), "gm-val gm-halo", an))
    # insets: Alaska (other_rec) and Hawaii (midwest group), each at its own scale
    ak = st["Alaska"]
    ak_main = max(ak.geoms, key=lambda g: g.area) if hasattr(ak, "geoms") else ak
    fa = bm.Frame(-152, 63, ak_main, (0, 350, 150, 96), pad=2)
    body.append(bm.text(0, 344, "Alaska · inset", "gm-eye"))
    body += draw(fa, ["Alaska"], simp=0.2)
    hi = st["Hawaii"]
    hi_main = unary_union([g for g in hi.geoms if g.centroid.x > -161]) if hasattr(hi, "geoms") else hi
    fh = bm.Frame(-157.4, 20.6, hi_main, (165, 390, 110, 56), pad=2)
    body.append(bm.text(165, 384, "Hawaii · inset", "gm-eye"))
    body += draw(fh, ["Hawaii"], simp=0.15)
    body.append(bm.scalebar(445, 458, f, 500))

    # cost rows under the map: they are the legend, and the table behind it
    y0 = 500
    body.append(bm.text(0, y0 - 14, "Ad cost per qualified respondent, men and women aged 18–34 pooled", "gm-eye"))
    label_w, bw = 300, 760 - 300 - 70
    mx = max(D["by_group"][k]["cost"] for k in order)
    y = y0
    for loc in order:
        g = D["by_group"][loc]
        codes = " ".join(sorted(postal[meta2ne.get(n, n)] for n in D["geo"][loc]))
        body.append(bm.text(0, y + 10, GROUP_NAME[loc], "gm-lab"))
        body.append(bm.text(0, y + 25, codes, "gm-tiny"))
        L = max(2.0, bw * g["cost"] / mx)
        body.append(f'<rect class="gm-bar" x="{label_w}" y="{y:.1f}" width="{L:.1f}" height="12" '
                    f'fill-opacity="{opacity(g["cost"])}"/>')
        body.append(bm.text(label_w + L + 6, y + 10.5, bm.money(g["cost"]), "gm-val"))
        body.append(bm.text(label_w, y + 25, f'{g["qualified"]:,} qualified · {bm.money(g["spend"])} ad spend', "gm-tiny"))
        y += 44
    notes = ["8 May – 7 Nov 2023. Every state and DC was in exactly one group, and each group was targeted as whole",
             "states (Meta regions), so the coloured area is the real targeting area. Fill darkens with cost. Alaska",
             "and Hawaii are drawn at their own scale."]
    for i, line in enumerate(notes):
        body.append(bm.text(0, y + 8 + 16 * i, line, "gm-note"))
    H = y + 8 + 16 * len(notes)
    s = bm.svg(W, H, "United States, 2023: advertising cost per qualified respondent in five groups of whole states",
               "One survey advertised to men and women aged 18 to 34 in five groups of whole states that together cover "
               "all 50 states and DC, May to November 2023. Ad cost per qualified respondent: " +
               "; ".join(f'{GROUP_NAME[k]} {bm.money(D["by_group"][k]["cost"])}' for k in order) + ".", body, "us23")
    open(os.path.join(HERE, "us-2023-state-groups.svg"), "w").write(s)
    print("wrote us-2023-state-groups.svg", f"{len(s) / 1024:.0f} KB")
    return postal, order


def png():
    import re
    tok = {"--ink": "#1F272E", "--ink-2": "#4A555E", "--ink-3": "#79858D", "--rule": "#CFD9DD",
           "--rule-2": "#AEBCC2", "--surface": "#FFFFFF", "--sunk": "#E5EBED", "--paper": "#F1F4F5",
           "--data": "#1D5F6E", "--data-2": "#9DB6BC", "--brass": "#7A5C1E"}
    svg = open(os.path.join(HERE, "us-2023-state-groups.svg")).read()
    svg = re.sub(r"var\((--[a-z0-9-]+)\)", lambda m: tok[m.group(1)], svg)
    tmp = os.path.join(HERE, "tmp.svg")
    open(tmp, "w").write(svg)
    env = dict(os.environ, FONTCONFIG_FILE=os.path.join(SP, "geo", "fonts.conf"))
    subprocess.run(["rsvg-convert", "-w", "1520", "-b", tok["--paper"], "-o",
                    os.path.join(HERE, "us-2023-state-groups.png"), tmp], check=True, env=env)
    os.remove(tmp)
    print("wrote us-2023-state-groups.png")


# --------------------------------------------------------------------------- data file
def data_file(D, postal, order):
    idn = json.load(open("/home/nandan/Documents/vlab-research/vlab.digital/scripts/data/country-id.json"))
    meta = idn["_meta"]
    meta = dict(meta, generated="2026-09-24", status="PILOT v4 - D-032. Not registered in CLAIMS.md, not on the site.")
    meta["terms"] = {"whole_state": meta["terms"]["whole_state"],
                     "state_group": "several whole states targeted together in one ad set (a Meta region list). "
                                    "Group names on the page are ours; the study's ids (eastern, focal_rec, midwest, "
                                    "ne_rec, other_rec) are raw labels and are never published",
                     "qualified_respondent": "a person aged 18-34 who said they live in the United States, gave a name, "
                                             "phone and email, and opened the study's enrolment survey (quota rule: "
                                             "answered 'sguid', the id the enrolment survey hands back)"}
    s = D
    per_study = {r[1]: r for r in csv.reader(open(os.path.join(SP, "per_study.tsv")), delimiter="\t")}
    out = OrderedDict()
    out["_meta"] = meta
    out["country"] = "US"
    out["all_people_surveyed"] = dict(unique_people=69430, first="2023-02-17", last="2025-12-03", studies=13,
                                      note="Distinct user_id in inference_data across the 15 single-country US "
                                           "studies on the current platform (13 have any data). user_id is scoped "
                                           "to a Facebook page, so one person reached through two pages counts twice.")
    fr = per_study[SLUG]
    out["study"] = OrderedDict(
        slug=SLUG, fielded="8 May – 7 Nov 2023", ad_days=int(fr[9]), started_survey=int(fr[2]),
        qualified=s["total_q"], spend=s["total_spend"], cost=round(s["total_spend"] / s["total_q"], 2),
        incentive="$10 Amazon gift card for the first survey (study offered $10/$5/$20/$5/$30 over five surveys)",
        channel="Messenger (Facebook and Instagram ads); screening in Messenger, then a link to the study's own enrolment survey",
        eligibility="aged 18-34 and living in the United States (the screener's only disqualifying questions)",
        quota_rule="opened the enrolment survey link after giving name, phone and email",
        quotas="Location (5 groups of whole states) × Gender (Meta genders), ages 18-34 targeted in every group: 10 groups",
        target_max_sample=5025, account_currency="USD (ad account 1342820622846299; recruitment budget $12,500 "
                                                   "set in dollars; the same account shows a $22 CPM on a 2025 US study)")
    out["by_state_group"] = OrderedDict(
        (GROUP_NAME[k], dict(states=sorted(postal[{"Washington D. C.": "District of Columbia"}.get(n, n)]
                                           for n in s["geo"][k]),
                             study_label=k, **s["by_group"][k])) for k in order)
    out["by_gender"] = s["by_gender"]
    out["by_state_group_and_gender"] = OrderedDict(
        (f"{GROUP_NAME[l]} · {g}", v) for (l, g), v in s["by_group_gender"].items())
    out["funnel_by_gender"] = s["funnel"]
    out["by_month"] = s["by_month"]
    out["by_month_note"] = ("Insights spend in the calendar month / people whose enrolment-survey id arrived that "
                            "month (inference_data 'sguid', 31 people without ad metadata left out, so the months sum "
                            "to 4,956 against the report's 4,932). Oct: the 1 Oct strata change set women's quota "
                            "to 0 in the South-and-East group and raised men's in four groups; reverted 31 Oct.")
    out["strata"] = [dict(id=k, current_participants=v["current_participants"], lifetime_spent=v["lifetime_spent"],
                          early_spend_8_22_may=round(s["early"][k], 2),
                          current_price_per_participant=v["current_price_per_participant"])
                     for k, v in sorted(s["rep"].items())]
    out["checks"] = [
        f"report ({s['created'][:16]} UTC) per-stratum lifetime_spent equals Insights per ad set to the cent; "
        f"report total ${s['rep_spend']:,.2f} of Insights ${s['ins_total']:,.2f}",
        f"the ${s['early_total']:,.2f} gap is 40 ad sets run 8-22 May (location × gender × race × days of use) before "
        "the study collapsed to 10 strata on 22 May; same state lists and genders, so their spend is assigned by id. "
        f"With it, groups sum to ${s['total_spend']:,.2f} = Insights",
        "state lists identical in all six strata versions (5, 12, 22, 28 May; 1, 31 Oct), and the five groups "
        "partition the 50 states and DC exactly",
        "no sibling study: of 8,362 people, 12 appear in any other study (7 llm-bias-survey-us, 5 in European/central "
        "Asian studies, likely staff tests)",
        "2 test entries 17-19 Apr before ads; every other person arrived 8 May - 7 Nov",
        "screener (Fly form B85Ep3Ad, all versions from 8 May): ineligible only if age <18 or >34 or country not US; "
        "days of marijuana use is asked but does not screen",
    ]
    out["strata_note"] = ("Stratum ids are the study's own labels. Gender 1 = men and 2 = women (Meta genders). "
                          "The '_rec' groups match the states with legal recreational cannabis in spring 2023 "
                          "(INFERRED from the labels and the lists; not published).")
    out["excluded_for_review"] = OrderedDict(
        quota_rule_is_not_a_screen=["vapefree-evaluation-aim3: $1,554.94, 856 'qualified' of 882 - the quota rule is "
                                    "the first message of the chat; the real screen ran on an external site whose "
                                    "outcomes we do not hold. 18-25, Android phones only, whole country. Cost per "
                                    "person who opened the chat: men $2.51, women $1.32"],
        targeting_not_as_stated=["racial-attitudes-project: the 'southwest' and 'west' groups both contain Arizona, "
                                 "Colorado, Nevada, New Mexico and Utah; Oklahoma and DC are in no group. Also 80-95 "
                                 "qualified per region and two incentive-framing arms. $940.20, 440 qualified, 11 days"],
        siblings_do_not_reconcile=["nci-aim2-baseline ($53,256 Insights, report shows $0), "
                                   "nci-aim2-baseline-creative-experiment ($3,859, 253 qualified), "
                                   "nci-aim2-recruitment-20240408 (report $4,148 of $4,852): one survey "
                                   "(nciaim2baseline1), overlapping respondents, 18-24 whole country. A combined "
                                   "figure needs its own reconciliation"],
        report_does_not_reconcile=["pgp-minnesota-gen-pop-survey: report $3,324 of $4,106. The gap looks like the same "
                                   "renamed-strata pattern (age-split ad sets 29 Jan - 3 Feb, $781) and could be "
                                   "recovered; 334 qualified, metro counties vs the rest of Minnesota, $5 incentive, "
                                   "multi-language entry (Somali). Not built", "gw-pedvax-2023: report carries "
                                   "lifetime_spent 0 on every stratum; $8,063 Insights. Health-care-worker targeting"],
        under_200_qualified=["ucsf-screener (149, $20.31)", "ucsf-screener-focused (32)", "ucsf-screener-phase-2 (12)",
                             "pgp-minnesota-gen-pop-xc (119)", "llm-bias-survey-us (30, 3 days)"],
        no_data=["reno-weber-2023-district-poll", "racial-attitudes"],
    )
    json.dump(out, open(os.path.join(HERE, "country-us.json"), "w"), indent=1, ensure_ascii=False)
    print("wrote country-us.json")
    return out


def section(d):
    """section.tpl.html + country-us.json + the map -> section.html."""
    m = lambda x: f"${x:,.2f}"
    gg = d["by_state_group_and_gender"]
    rows_ = []
    for g, v in d["by_state_group"].items():
        rows_.append(f'        <tr><td>{g}<span class="id">{" ".join(v["states"])}</span></td>'
                     f'<td class=n>{m(gg[g + " · Women"]["cost"])}</td><td class=n>{m(gg[g + " · Men"]["cost"])}</td>'
                     f'<td class=n>{m(v["cost"])}</td></tr>')
    bg, st = d["by_gender"], d["study"]
    rows_.append(f'        <tr><td><b>All 50 states and DC</b></td><td class=n><b>{m(bg["Women"]["cost"])}</b></td>'
                 f'<td class=n><b>{m(bg["Men"]["cost"])}</b></td><td class=n><b>{m(st["cost"])}</b></td></tr>')
    mn = {"2023-05": "May", "2023-06": "June", "2023-07": "July", "2023-08": "August", "2023-09": "September"}
    mrows = [f'        <tr><td>{mn[k]}</td><td class=n>{v["qualified"]:,}</td><td class=n>${v["spend"]:,.0f}</td>'
             f'<td class=n>{m(v["cost"])}</td><td class=n>{m(v["women"])}</td><td class=n>{m(v["men"])}</td></tr>'
             for k, v in d["by_month"].items() if k in mn]
    s = open(os.path.join(HERE, "section.tpl.html")).read()
    svg_ = open(os.path.join(HERE, "us-2023-state-groups.svg")).read().strip()
    s = (s.replace("{{GENDER_ROWS}}", "\n".join(rows_)).replace("{{MONTH_ROWS}}", "\n".join(mrows))
         .replace("{{US2023}}", svg_).replace("{{WOMEN_Q}}", f'{bg["Women"]["qualified"]:,}')
         .replace("{{MEN_Q}}", f'{bg["Men"]["qualified"]:,}'))
    assert "{{" not in s
    open(os.path.join(HERE, "section.html"), "w").write(s)
    print("wrote section.html")


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        fetch()
    D = compute()
    postal, order = us_map(D)
    section(data_file(D, postal, order))
    if "--png" in sys.argv:
        png()
