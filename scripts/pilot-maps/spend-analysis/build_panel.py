"""Build the stratum x day panel: USD ad spend (Meta Insights) against NEW people who started.

Inputs (raw/, pulled read-only by pull.sh):
  spend_daily.tsv        max per study x campaign x ad set x day of spend / impressions / reach
  people_new_hourly.tsv  new people (first arrival anywhere) by tie-set of studies x UTC hour x
                         ad-metadata string -- counts only
  strata_md.tsv          every stratum id ever configured per study, with its metadata
  general_hist.tsv       ad account + country per study
  studies.tsv            slugs
Outputs:
  panel.csv            unit x day (unit = component of tied studies x stratum metadata signature)
  match_report.csv     per component: people, matched share, chosen timezone shift
  excluded_nonusd.csv  studies dropped on the CPM currency screen
"""
import csv, json
from collections import defaultdict
import numpy as np
import pandas as pd

csv.field_size_limit(10**9)
R = "raw/"
tsv = lambda p: list(csv.DictReader(open(R + p), delimiter="\t"))

slug = {r["id"]: r["slug"] for r in tsv("studies.tsv")}
acct, cc = {}, {}
for r in tsv("general_hist.tsv"):      # ordered by created: latest wins
    acct[r["study_id"]], cc[r["study_id"]] = r["acct"], r["cc"]

# ---------------- spend ----------------
sp = pd.DataFrame(tsv("spend_daily.tsv"))
for c in ["spend", "imp", "reach", "uclicks", "cpm", "nst"]:
    sp[c] = pd.to_numeric(sp[c].replace("NULL", np.nan), errors="coerce")
sp["slug"] = sp.study_id.map(slug)
n0 = sp.study_id.nunique()
sp = sp[sp.nst == 1]                                   # trap 2: campaigns shared across studies
sp = sp[~sp.slug.str.contains(r"^test$|fly_test|smoke|test-custom", regex=True, na=False)]  # trap 4
cpm_s = sp.groupby("study_id").apply(
    lambda g: 1000 * g.spend.sum() / g.imp.sum() if g.imp.sum() > 0 else g.cpm.median(),
    include_groups=False)
usd = set(cpm_s[(cpm_s > 0.05) & (cpm_s < 20)].index)  # trap 1: USD CPM ~0.2-3; naira 500+
nonusd = cpm_s[~cpm_s.index.isin(usd)]
sp = sp[sp.study_id.isin(usd)].copy()

# stratum metadata -> signature
md = defaultdict(dict)
for r in tsv("strata_md.tsv"):
    if r["md"] not in ("NULL", ""):
        d = json.loads(r["md"])
        md[r["study_id"]][r["sid"]] = frozenset((k.strip().lower(), str(v).strip().lower()) for k, v in d.items())
sp["sig"] = [md[s].get(t) for s, t in zip(sp.study_id, sp.strat)]
nosig = sp.sig.isna().groupby(sp.study_id).mean()
sp = sp[sp.sig.notna()]

# ---------------- people ----------------
pe = pd.DataFrame(tsv("people_new_hourly.tsv"))
pe["n"] = pe.n.astype(int)
pe["h"] = pd.to_datetime(pe.h)
pe["studies"] = pe.studies.str.split(",")

# components: studies joined by any tie set
parent = {}
def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
for ss in pe.studies:
    for s in ss[1:]:
        parent[find(s)] = find(ss[0])
comp = lambda s: find(s)
sp["comp"] = sp.study_id.map(comp)
pe["comp"] = pe.studies.map(lambda ss: comp(ss[0]))

def parse(s):
    out = {}
    if isinstance(s, str) and s not in ("NULL", ""):
        for kv in s.split("|"):
            k, _, v = kv.partition("=")
            out.setdefault(k.strip().lower(), set()).add(v.strip().lower())
    return out

sigs_by_study = sp.groupby("study_id").sig.agg(lambda x: set(x))
def match(studies, mdstr, cache={}):
    key = (tuple(studies), mdstr)
    if key in cache:
        return cache[key]
    u = parse(mdstr)
    cands = set()
    for s in studies:
        cands |= sigs_by_study.get(s, set())
    hits = [g for g in cands if all(k in u and v in u[k] for k, v in g)]
    if hits:                                   # most specific signature, if unique
        mx = max(len(g) for g in hits)
        hits = [g for g in hits if len(g) == mx]
    cache[key] = hits[0] if len(hits) == 1 else None
    return cache[key]

pe = pe[pe.comp.isin(set(sp.comp))].copy()
pe["sig"] = [match(ss, m) for ss, m in zip(pe.studies, pe.md)]

# ---------------- timezone shift per ad account ----------------
# Meta days are in the ad account's timezone; arrivals are UTC. For each account, choose the
# hour shift that maximises the correlation of day-on-day changes (log spend vs log starters)
# within units -- the variation the analysis itself uses.
sp["acct"] = sp.study_id.map(acct)
comp_acct = sp.groupby("comp").acct.agg(lambda x: x.mode().iloc[0])
spu = sp.groupby(["comp", "sig", "d"])[["spend", "imp", "reach", "uclicks"]].sum(min_count=1).reset_index()
spu["d"] = pd.to_datetime(spu.d)
pm = pe[pe.sig.notna()]

def daily_people(shift, comps):
    x = pm[pm.comp.isin(comps)]
    return (x.assign(d=(x.h + pd.Timedelta(hours=shift)).dt.floor("D"))
             .groupby(["comp", "sig", "d"]).n.sum().rename("starters").reset_index())

def fd_corr(j):
    j = j.sort_values(["comp", "sig", "d"]).copy()
    j = j[(j.spend > 0) & (j.starters > 0)]
    j["ls"], j["ln"] = np.log(j.spend), np.log(j.starters)
    g = j.groupby(["comp", "sig"])
    j["gap"] = g.d.diff().dt.days
    j["dls"], j["dln"] = g.ls.diff(), g.ln.diff()
    j = j[j.gap == 1]
    return (np.corrcoef(j.dls, j.dln)[0, 1], len(j)) if len(j) > 20 else (np.nan, len(j))

shift_of = {}
tzrows = []
for a, comps in comp_acct.groupby(comp_acct).groups.items():
    comps = set(comps)
    su = spu[spu.comp.isin(comps)]
    res = []
    for s in range(-12, 15):
        c, n = fd_corr(su.merge(daily_people(s, comps), on=["comp", "sig", "d"], how="left").fillna({"starters": 0}))
        res.append((s, c, n))
    best = max((r for r in res if not np.isnan(r[1])), key=lambda r: r[1], default=(0, np.nan, 0))
    shift_of[a] = best[0]
    tzrows.append(dict(acct=a, shift=best[0], fd_corr=best[1], n_pairs=best[2],
                       corr_at_0=[r[1] for r in res if r[0] == 0][0]))
tz = pd.DataFrame(tzrows)

# ---------------- assemble ----------------
parts = []
for a, comps in comp_acct.groupby(comp_acct).groups.items():
    comps = set(comps)
    j = spu[spu.comp.isin(comps)].merge(daily_people(shift_of[a], comps), on=["comp", "sig", "d"], how="outer")
    j["tz_shift"] = shift_of[a]
    j["acct"] = a
    parts.append(j)
panel = pd.concat(parts, ignore_index=True)
panel["spend"] = panel.spend.fillna(0)
panel["starters"] = panel.starters.fillna(0).astype(int)
panel["unit"] = panel.comp.str[:8] + "|" + panel.sig.map(lambda g: ",".join(f"{k}:{v}" for k, v in sorted(g)))
comp_slugs = sp.groupby("comp").slug.agg(lambda x: " + ".join(sorted(set(x))))
comp_cc = sp.groupby("comp").study_id.agg(lambda x: cc.get(x.iloc[0], ""))
panel["studies"] = panel.comp.map(comp_slugs)
panel["country"] = panel.comp.map(comp_cc)

# units: keep only those whose people were matched at all (otherwise it is a matching failure)
panel = panel[panel.groupby("unit").starters.transform("sum") > 0]
# restrict to the unit's spend window (first to last spend day); arrivals outside it are
# organic / late and are reported, not modelled
w = panel[panel.spend > 0].groupby("unit").d.agg(["min", "max"])
panel = panel.join(w, on="unit")
inwin = (panel.d >= panel["min"]) & (panel.d <= panel["max"])
outside = panel[~inwin].starters.sum()
panel = panel[inwin].drop(columns=["min", "max", "comp", "sig"]).sort_values(["unit", "d"])
panel["d"] = panel.d.dt.strftime("%Y-%m-%d")
panel.to_csv("panel.csv", index=False)

rep = pe.groupby("comp").apply(lambda g: pd.Series(dict(people=g.n.sum(), matched=g[g.sig.notna()].n.sum())),
                               include_groups=False)
rep["share"] = rep.matched / rep.people
rep["studies"] = rep.index.map(comp_slugs)
rep["acct_shift"] = rep.index.map(lambda c: shift_of.get(comp_acct.get(c)))
rep.sort_values("people", ascending=False).to_csv("match_report.csv")
tz.to_csv("tz_shift.csv", index=False)
nonusd.rename("cpm").to_frame().assign(slug=lambda x: x.index.map(slug)).to_csv("excluded_nonusd.csv")

print(tz.to_string())
print(rep.sort_values("people", ascending=False).head(40).to_string())
print(f"studies with spend rows {n0}; USD {len(usd)}; non-USD dropped {len(nonusd)}")
print(f"panel rows {len(panel)}  spend>0 {(panel.spend>0).sum()}  units {panel.unit.nunique()}  "
      f"components {panel.studies.nunique()}  starters {panel.starters.sum()}  spend ${panel.spend.sum():,.0f}  "
      f"starters outside spend window {outside}")
