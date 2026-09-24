#!/usr/bin/env python3
"""Nigeria place page: stratum-level evidence from every cleaned recruitment.

Inputs (read-only pulls, this directory):
  fam.json            recruitment families (sibling studies that fed one survey / one round of ads)
  all_confs.tsv       study_confs history (strata, creatives, recruitment, general, inference_data)
  spend_daily.tsv     Insights spend > 0 per study x campaign x stratum x day
  shared_camps.tsv    campaigns seen under more than one study
  inf.tsv             inference_data rows for every family study
  user_creatives.tsv  Fly responses: creative name per user with first timestamp (metadata written at message time)
  rep/*.tsv           latest FACEBOOK_ADOPT report per study (for validation only)
Writes strata_evidence.json: one row per family x stratum with geometry, spend, starters, qualified.
"""
import csv, json, os, re, collections, datetime as dt


def jl(s):
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return json.loads(re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', s))


csv.field_size_limit(10 ** 9)
HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda f: os.path.join(HERE, f)
FAM = json.load(open(P("fam.json")))
SID2SLUG = {sid: slug for fam in FAM.values() for slug, sid in fam.items()}
SID2FAM = {sid: f for f, fam in FAM.items() for sid in fam.values()}

# ---------------------------------------------------------------- configs
H = collections.defaultdict(list)
for r in csv.DictReader(open(P("all_confs.tsv")), delimiter="\t"):
    H[(r["study_id"], r["conf_type"])].append((r["created"], jl(r["conf"])))


def latest(sid, t):
    v = H.get((sid, t))
    return v[-1][1] if v else None


def rule_vars(q):
    out = []

    def walk(x):
        if not x:
            return
        if x.get("op") in ("and", "or"):
            for v in x["vars"]:
                walk(v)
        elif x.get("op") == "answered":
            out.append(x["vars"][0]["value"].strip('"'))
    walk(q)
    return out


def geo_sig(ft):
    def one(g):
        if not g:
            return None
        d = {}
        for k in ("countries", "regions", "cities", "custom_locations", "places"):
            if g.get(k):
                if k == "countries":
                    d[k] = sorted(g[k])
                elif k == "regions":
                    d[k] = sorted(x["name"] for x in g[k])
                elif k == "cities":
                    d[k] = sorted((x.get("name"), x.get("key"), x.get("radius"), x.get("distance_unit")) for x in g[k])
                elif k == "custom_locations":
                    d[k] = sorted((round(x["latitude"], 4), round(x["longitude"], 4), x.get("radius"), x.get("distance_unit")) for x in g[k])
                else:
                    d[k] = sorted((x.get("name"), x.get("key"), round(float(x.get("latitude", 0)), 4), round(float(x.get("longitude", 0)), 4), x.get("radius"), x.get("distance_unit")) for x in g[k])
        return d or None
    return json.dumps([one(ft.get("geo_locations")), one(ft.get("excluded_geo_locations"))], sort_keys=True)


STUDY = {}
for sid, slug in SID2SLUG.items():
    strata = latest(sid, "strata") or []
    cr_names = set()  # filled after spend windows are known (versions in force while ads ran)
    camps = {(latest(sid, "recruitment") or {}).get("ad_campaign_name")}
    inf = latest(sid, "inference_data") or {}
    md_vars = []
    for src in (inf.get("data_sources") or {}).values():
        for e in src.get("extraction_confs", []):
            if e["location"] == "metadata" and e["name"] not in md_vars:
                md_vars.append(e["name"])
    st = {}
    for s in strata:
        ft = s.get("facebook_targeting") or {}
        st[s["id"]] = dict(meta=s.get("metadata") or {}, geo=geo_sig(ft), ft=ft,
                           rule=rule_vars(s.get("question_targeting")),
                           genders=ft.get("genders"), age=(ft.get("age_min"), ft.get("age_max")),
                           creatives=s.get("creatives") or [])
    rec = latest(sid, "recruitment") or {}
    STUDY[sid] = dict(slug=slug, strata=st, creatives=cr_names, camps=camps, md_vars=md_vars, rec=rec,
                      strata_created=(H.get((sid, "strata")) or [[None]])[-1][0])

# ---------------------------------------------------------------- spend (deduped within family)
spend = {}  # (fam, camp, strat, d) -> (spend, sid)
CONV = {}
for r in csv.DictReader(open(P("insights_daily.tsv")), delimiter="\t"):
    f = SID2FAM[r["sid"]]
    k = (f, r["camp"], r["strat"], r["d"])
    c = float(r["conv"]) if r["conv"] not in ("", "NULL") else None
    if c is not None and (k not in CONV or c > CONV[k]):
        CONV[k] = c
for r in csv.DictReader(open(P("spend_daily.tsv")), delimiter="\t"):
    f = SID2FAM[r["sid"]]
    k = (f, r["camp"], r["strat"], r["d"])
    v = float(r["spend"])
    if k not in spend or v > spend[k][0]:
        spend[k] = (v, r["sid"])
shared = {}
for r in list(csv.reader(open(P("shared_camps.tsv")), delimiter="\t"))[1:]:
    shared[r[0]] = r[1].strip("{}").split(",")
cross_family_shared = {c: s for c, s in shared.items() if len({SID2FAM.get(x) for x in s}) > 1 and any(x in SID2FAM for x in s)}

camp_studies = collections.defaultdict(set)
win = collections.defaultdict(lambda: [None, None])  # sid -> [first, last] spend day
for (f, camp, strat, d), (v, sid) in spend.items():
    camp_studies[(f, camp)].add(sid)
    w = win[sid]
    w[0] = d if w[0] is None or d < w[0] else w[0]
    w[1] = d if w[1] is None or d > w[1] else w[1]
for (f, camp), sids in camp_studies.items():
    for sid in shared.get(camp, []):
        if sid in SID2FAM and SID2FAM[sid] == f:
            sids.add(sid)
            # a study that shares a campaign inherits its window
    if len(sids) > 1:
        lo = min(win[s][0] for s in sids if win[s][0]); hi = max(win[s][1] for s in sids if win[s][1])
        for s in sids:
            win[s] = [min(filter(None, [win[s][0], lo])), max(filter(None, [win[s][1], hi]))]

def creatives_in_force(sid):
    hist = H.get((sid, "strata"), [])
    lo, hi = win[sid]
    if not hist or lo is None:
        return set()
    out = set()
    for i, (t, c) in enumerate(hist):
        nxt = hist[i + 1][0] if i + 1 < len(hist) else "9999"
        if nxt[:10] >= lo and t[:10] <= hi:   # this version was live for some part of the ad window
            for x in c:
                out.update(x.get("creatives") or [])
    return out


for sid in STUDY:
    STUDY[sid]["creatives"] = creatives_in_force(sid)

sp_day = collections.defaultdict(float)
for (f_, camp, strat, d), (v, sid) in spend.items():
    for s_ in camp_studies[(f_, camp)]:
        if camp in STUDY[s_]["camps"]:
            sp_day[(s_, strat, d)] += v

# ---------------------------------------------------------------- people
inf = collections.defaultdict(lambda: collections.defaultdict(dict))  # fam -> user -> {var: (value, ts, sid)}
for r in csv.DictReader(open(P("inf.tsv")), delimiter="\t"):
    f = SID2FAM[r["study_id"]]
    val = json.loads(r["value"]) if r["value"] not in ("", "NULL") else None
    ts = r["timestamp"][:19]
    cur = inf[f][r["user_id"]].get(r["variable"])
    if cur is None or ts < cur[1]:
        inf[f][r["user_id"]][r["variable"]] = (val, ts, r["study_id"])
ucr = collections.defaultdict(dict)
for r in csv.DictReader(open(P("user_creatives.tsv")), delimiter="\t"):
    if r["cr"] not in ("", "NULL"):
        ucr[r["userid"]][r["cr"]] = r["t0"][:19]


def day(ts):
    return ts[:10]


def within(sid, ts, before=1, after=3):
    lo, hi = win[sid]
    if lo is None:
        return False
    d = dt.date.fromisoformat(day(ts))
    return dt.date.fromisoformat(lo) - dt.timedelta(days=before) <= d <= dt.date.fromisoformat(hi) + dt.timedelta(days=after)


rows = collections.defaultdict(lambda: dict(spend=0.0, starters=0, qualified=0, days=set(), people_days=[]))
assign_log = collections.Counter()
unassigned = collections.defaultdict(collections.Counter)
people = []
for f, fam in FAM.items():
    sids = list(fam.values())
    for u, vars_ in inf[f].items():
        # metadata-derived stratum labels, earliest record
        md = {}
        t0 = None
        for sid in sids:
            for v in STUDY[sid]["md_vars"]:
                if v in vars_ and v not in md:
                    md[v] = vars_[v][0]
                    t0 = vars_[v][1] if t0 is None or vars_[v][1] < t0 else t0
        if not md or t0 is None:
            unassigned[f]["no ad metadata"] += 1
            continue
        cands = []
        for sid in sids:
            for stid, s in STUDY[sid]["strata"].items():
                keys = [k for k in s["meta"] if k in STUDY[sid]["md_vars"]]
                if keys and all(str(md.get(k)) == str(s["meta"][k]) for k in keys):
                    if within(sid, t0):
                        cands.append((sid, stid))
        if len(cands) > 1 and len({c[0] for c in cands}) > 1:
            crs = ucr.get(u, {})
            mine = sorted((t, cr) for cr, t in crs.items() if any(cr in STUDY[c[0]]["creatives"] for c in cands))
            if mine:
                first = mine[0][1]
                cands = [c for c in cands if first in STUDY[c[0]]["creatives"]]
                assign_log[(f, "by-creative")] += 1
        if len(cands) > 1 and len({c[0] for c in cands}) > 1:
            # prefer the ad set that was spending on the person's first day (or the day before)
            d0 = dt.date.fromisoformat(day(t0))
            ok = {(d0 - dt.timedelta(days=k)).isoformat() for k in (0, 1)}
            live = [c for c in cands if any(sp_day.get((c[0], c[1], x)) for x in ok)]
            if live and len(live) < len(cands):
                cands = live
                assign_log[(f, "by-live-ad-set")] += 1
        if len(cands) > 1:
            geos = {STUDY[s]["strata"][st]["geo"] for s, st in cands}
            if len(geos) == 1:
                assign_log[(f, "ambiguous-same-geometry")] += 1
                cands = [sorted(cands)[0]]
            else:
                unassigned[f]["ambiguous geometry"] += 1
                continue
        if not cands:
            unassigned[f]["outside spend window or no matching stratum"] += 1
            continue
        sid, stid = cands[0]
        rule = STUDY[sid]["strata"][stid]["rule"]
        q = bool(rule) and all(rv in vars_ for rv in rule)
        key = (f, sid, stid)
        rows[key]["starters"] += 1
        rows[key]["qualified"] += int(q)
        people.append((f, sid, stid, u, t0, q))

# spend onto (family, study, stratum). A campaign shared inside a family is attributed to the
# study whose strata contain the stratum id; if both do, to the first (geometry is then checked equal).
spend_unmatched = collections.Counter()
for (f, camp, strat, d), (v, sid) in spend.items():
    owners = [s for s in sorted(camp_studies[(f, camp)]) if strat in STUDY[s]["strata"]]
    named = [s for s in owners if camp in STUDY[s]["camps"]]
    if named:
        owners = named
    if not owners:
        spend_unmatched[(f, camp, strat)] += v
        continue
    geos = {STUDY[s]["strata"][strat]["geo"] for s in owners}
    if len(geos) > 1:
        spend_unmatched[(f, camp, strat, "geometry differs across owners")] += v
        continue
    key = (f, owners[0], strat)
    rows[key]["spend"] += v
    if (f, camp, strat, d) in CONV:
        rows[key]["conv"] = rows[key].get("conv", 0.0) + CONV[(f, camp, strat, d)]
        rows[key]["conv_days"] = rows[key].get("conv_days", 0) + 1
    rows[key]["days"].add(d)

# merge rows whose stratum lives in several studies of one family with the same geometry
out = []
for (f, sid, stid), r in rows.items():
    s = STUDY[sid]["strata"].get(stid)
    out.append(dict(family=f, study=STUDY[sid]["slug"], sid=sid, stratum=stid, meta=s["meta"] if s else None,
                    geo=s["geo"] if s else None, rule=s["rule"] if s else None, genders=s["genders"] if s else None,
                    age=s["age"] if s else None, spend=round(r["spend"], 2), starters=r["starters"],
                    qualified=r["qualified"], days=sorted(r["days"]),
                    meta_conversations=r.get("conv"), conv_days=r.get("conv_days", 0),
                    ))
json.dump(dict(rows=out, unassigned={f: dict(c) for f, c in unassigned.items()},
               assign_log={f"{a}|{b}": n for (a, b), n in assign_log.items()},
               spend_unmatched={"|".join(map(str, k)): round(v, 2) for k, v in spend_unmatched.items()},
               windows={STUDY[s]["slug"]: w for s, w in win.items()},
               cross_family_shared=cross_family_shared),
          open(P("strata_evidence.json"), "w"), indent=1)
with open(P("people.tsv"), "w") as fh:
    for p in people:
        fh.write("\t".join(map(str, p)) + "\n")

# ---------------------------------------------------------------- validation vs reports
print("family / study                              spend   starters  qual  | report spend  report qual")
agg = collections.defaultdict(lambda: [0.0, 0, 0])
for o in out:
    a = agg[(o["family"], o["study"])]
    a[0] += o["spend"]; a[1] += o["starters"]; a[2] += o["qualified"]
for (f, st), (sp, n, q) in sorted(agg.items()):
    rp = os.path.join(HERE, "rep", st + ".tsv")
    rs = rq = ""
    if os.path.exists(rp):
        rr = list(csv.DictReader(open(rp), delimiter="\t"))
        if rr:
            d = json.loads(rr[0]["details"])
            rs = round(sum(v.get("lifetime_spent", v.get("total_spent", 0)) for v in d.values()), 2)
            rq = sum(v["current_participants"] for v in d.values())
    print(f"{f[:22]:22} {st[:22]:22} {sp:9.2f} {n:7d} {q:6d}  | {rs!s:>10} {rq!s:>6}")
print("unassigned", json.dumps({f: dict(c) for f, c in unassigned.items()}, indent=0))
print("spend unmatched", {k: round(v, 2) for k, v in spend_unmatched.items()})
print("cross-family shared campaigns", cross_family_shared)

if os.environ.get("DEBUG"):
    import itertools
    fams = os.environ["DEBUG"].split(",")
    for f in fams:
        sids = list(FAM[f].values())
        c = collections.Counter(); ex = []
        for u, vars_ in inf[f].items():
            if any(p[3] == u for p in people[:0]):
                pass
        assigned = {p[3] for p in people if p[0] == f}
        for u in inf[f]:
            if u in assigned:
                continue
            crs = tuple(sorted(ucr.get(u, {}).items(), key=lambda x: x[1])[:3])
            c[tuple(x[0] for x in crs)] += 1
        print(f, "unassigned creatives (top)", c.most_common(12))
        print({STUDY[s]["slug"]: sorted(STUDY[s]["creatives"]) for s in sids})
        print({STUDY[s]["slug"]: win[s] for s in sids})
