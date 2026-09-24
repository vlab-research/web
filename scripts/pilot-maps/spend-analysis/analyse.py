"""Does daily spend in a stratum raise the ad cost per person who started? Reads panel.csv.

Main estimator: Poisson pseudo-maximum-likelihood (PPML) of daily starters on log daily spend with
unit (stratum) fixed effects -- keeps zero-starter days and reads as an elasticity. If starters
scale as spend^b, cost per starter scales as spend^(1-b): doubling spend multiplies cost per
starter by 2^(1-b).
"""
import json, warnings
import numpy as np
import pandas as pd
import pyfixest as pf

warnings.filterwarnings("ignore")
rng = np.random.default_rng(7)

p = pd.read_csv("panel.csv", parse_dates=["d"])
p["comp"] = p.unit.str.split("|").str[0]

# ---------------- audience geometry per unit ----------------
geo = pd.read_csv("raw/strata_geo.tsv", sep="\t")
md = pd.read_csv("raw/strata_md.tsv", sep="\t")
def gclass(s):
    try:
        g = json.loads(s)
    except Exception:
        return "unknown"
    if g.get("custom_locations"):
        return "radius"
    if g.get("cities") or g.get("zips") or g.get("places"):
        return "city"
    if g.get("regions"):
        return "region"
    if g.get("countries"):
        return "country"
    return "unknown"
geo["gclass"] = geo.geo.map(gclass)
def sigstr(s):
    try:
        d = json.loads(s)
    except Exception:
        return None
    return ",".join(f"{k.strip().lower()}:{str(v).strip().lower()}" for k, v in sorted(
        ((k.strip().lower(), str(v).strip().lower()) for k, v in d.items())))
md["sig"] = md.md.map(sigstr)
gm = geo.merge(md[["study_id", "sid", "sig"]], on=["study_id", "sid"])
gm["comp8"] = None
# map study -> comp8 via panel: a unit's comp is the first 8 chars of the component root id;
# we instead match on signature within the studies listed for the unit
sig_class = gm.groupby("sig").gclass.agg(lambda x: x.mode().iloc[0])
p["sig"] = p.unit.str.split("|", n=1).str[1]
p["gclass"] = p.sig.map(sig_class).fillna("unknown")

# ---------------- analysis sample ----------------
p = p.sort_values(["unit", "d"])
p["cum_before"] = p.groupby("unit").spend.cumsum() - p.spend
first = p[p.spend > 0].groupby("unit").d.min()
p["day_in_field"] = (p.d - p.unit.map(first)).dt.days + 1
p["dow"] = p.d.dt.dayofweek
p["cdate"] = p.comp + "_" + p.d.dt.strftime("%Y%m%d")
p["spend_lag"] = p.groupby("unit").spend.shift(1)
p["spend_lead"] = p.groupby("unit").spend.shift(-1)
p["gap_lag"] = p.groupby("unit").d.diff().dt.days
comp_day = p.groupby(["comp", "d"]).spend.transform("sum")
p["loo_total"] = comp_day - p.spend                         # rest of the study that day

s = p[(p.spend >= 1)].copy()
ok = s.groupby("unit").agg(n=("d", "size"), st=("starters", "sum"))
keep = ok[(ok.n >= 5) & (ok.st >= 20)].index
s = s[s.unit.isin(keep)].copy()
s["ls"] = np.log(s.spend)
s["lt"] = np.log(s.day_in_field)
s["lc"] = np.log1p(s.cum_before)
s["lloo"] = np.log1p(s.loo_total)
s["cps"] = s.spend / s.starters.replace(0, np.nan)

N = dict(unit_days=len(s), units=s.unit.nunique(), study_groups=s.comp.nunique(),
         starters=int(s.starters.sum()), spend=round(s.spend.sum()), zero_days=float((s.starters == 0).mean()))
print("sample", N)

def est(fml, data, name, var="ls", vcov=None):
    m = pf.fepois(fml, data=data, vcov=vcov or {"CRV1": "comp"})
    b, se = m.coef()[var], m.se()[var]
    return dict(model=name, b=b, se=se, cps_elast=1 - b,
                double_pct=100 * (2 ** (1 - b) - 1),
                double_lo=100 * (2 ** (1 - (b + 1.96 * se)) - 1),
                double_hi=100 * (2 ** (1 - (b - 1.96 * se)) - 1), n=m._N), m

rows, models = [], {}
def add(fml, data, name, var="ls"):
    r, m = est(fml, data, name, var)
    rows.append(r); models[name] = m
    return m

# 0. naive between-unit (no FE): what a pooled comparison across recruitments sees
agg = s.groupby("unit").agg(spend=("spend", "sum"), st=("starters", "sum"), days=("d", "size"), comp=("comp", "first"))
agg["ls"] = np.log(agg.spend / agg.days)
r0, m0 = est("st ~ ls + np.log(days)", agg.reset_index(), "between units (no FE): avg daily spend")
rows.append(r0)
add("starters ~ ls | unit", s, "within stratum")
add("starters ~ ls + lt | unit + dow", s, "within + log day-in-field + weekday")
add("starters ~ ls + lc | unit + dow", s, "within + log cumulative spend + weekday")
add("starters ~ ls + lt + lc | unit + dow", s, "within + both time controls + weekday")
add("starters ~ ls | unit + cdate", s, "within + study-group x date FE")

# lags / timezone robustness: spend yesterday and tomorrow
sl = s[(s.gap_lag == 1) & s.spend_lag.notna() & s.spend_lead.notna() & (s.spend_lag > 0) & (s.spend_lead > 0)].copy()
sl["ls_lag"], sl["ls_lead"] = np.log(sl.spend_lag), np.log(sl.spend_lead)
m = pf.fepois("starters ~ ls + ls_lag + ls_lead + lt | unit + dow", data=sl, vcov={"CRV1": "comp"})
lagtab = pd.DataFrame(dict(b=m.coef(), se=m.se()))
btot = m.coef()[["ls", "ls_lag", "ls_lead"]].sum()
print("lags\n", lagtab, "\n sum of spend coefs", btot)

# 3-day blocks (absorb timezone / next-day arrivals)
s["blk"] = (s.d - s.unit.map(first)).dt.days // 3
b3 = s.groupby(["unit", "blk"]).agg(spend=("spend", "sum"), starters=("starters", "sum"), days=("d", "size"),
                                     comp=("comp", "first"), lt=("lt", "mean")).reset_index()
b3 = b3[b3.days == 3]
b3["ls"] = np.log(b3.spend)
add("starters ~ ls + lt | unit", b3, "3-day blocks, within + day-in-field")

# study-group level: total daily spend is set by budget / days left (human-set), not by the
# optimiser's between-strata allocation
cd = s.groupby(["comp", "d"]).agg(spend=("spend", "sum"), starters=("starters", "sum"), cum=("cum_before", "sum"),
                                   dif=("day_in_field", "max")).reset_index()
cd = cd[cd.groupby("comp").d.transform("size") >= 5]
cd["ls"], cd["lt"], cd["dow"] = np.log(cd.spend), np.log(cd.dif), cd.d.dt.dayofweek
add("starters ~ ls + lt | comp + dow", cd, "study-group total per day, within + day-in-field")

# control function IV: stratum spend instrumented by the rest of the study's spend that day
iv = s[s.loo_total > 0].copy()
def cf_fit(d):
    fs = pf.feols("ls ~ lloo + lt | unit + dow", data=d)
    d = d.assign(v=fs.resid())
    m = pf.fepois("starters ~ ls + lt + v | unit + dow", data=d)
    return m.coef()["ls"], fs
bcf, fs = cf_fit(iv)
fs_t = fs.coef()["lloo"] / fs.se()["lloo"]
comps = iv.comp.unique()
boots = []
for i in range(200):
    pick = rng.choice(comps, len(comps), replace=True)
    d = pd.concat([iv[iv.comp == c].assign(unit=lambda x, i=j: x.unit + f"#{i}") for j, c in enumerate(pick)])
    try:
        boots.append(cf_fit(d)[0])
    except Exception:
        pass
se_cf = float(np.std(boots))
rows.append(dict(model="control-function IV: rest-of-study spend", b=bcf, se=se_cf, cps_elast=1 - bcf,
                 double_pct=100 * (2 ** (1 - bcf) - 1), double_lo=100 * (2 ** (1 - (bcf + 1.96 * se_cf)) - 1),
                 double_hi=100 * (2 ** (1 - (bcf - 1.96 * se_cf)) - 1), n=len(iv)))
print("first stage t", fs_t, "boot reps", len(boots))

# heterogeneity by geometry
het = []
for g, d in s.groupby("gclass"):
    if d.unit.nunique() < 5 or d.comp.nunique() < 3:
        continue
    r, _ = est("starters ~ ls + lt | unit + dow", d, f"geometry = {g}")
    r.update(units=d.unit.nunique(), groups=d.comp.nunique()); het.append(r)
# heterogeneity by typical daily spend level of the unit (is the curve steeper at high spend?)
s["unit_med"] = s.groupby("unit").spend.transform("median")
s["lvl"] = pd.qcut(s.unit_med, 3, labels=["low", "mid", "high"])
for g, d in s.groupby("lvl", observed=True):
    r, _ = est("starters ~ ls + lt | unit + dow", d, f"unit median daily spend tercile = {g} "
               f"(${d.unit_med.min():.0f}-{d.unit_med.max():.0f})")
    r.update(units=d.unit.nunique(), groups=d.comp.nunique()); het.append(r)

# mechanism: does reach keep up with spend? (saturation shows as reach elasticity < 1, CPM rising)
rr = s[(s.reach > 0) & s.imp.notna() & (s.imp > 0)].copy()
rr["lr"], rr["lcpm"] = np.log(rr.reach), np.log(1000 * rr.spend / rr.imp)
mr = pf.feols("lr ~ ls + lt | unit + dow", data=rr, vcov={"CRV1": "comp"})
mc = pf.feols("lcpm ~ ls + lt | unit + dow", data=rr, vcov={"CRV1": "comp"})
mech = dict(reach_elast=mr.coef()["ls"], reach_se=mr.se()["ls"], cpm_elast=mc.coef()["ls"], cpm_se=mc.se()["ls"],
            n=len(rr))
# starters per person reached
rr2 = rr.copy()
mconv = pf.fepois("starters ~ ls + lt + lr | unit + dow", data=rr2, vcov={"CRV1": "comp"})
mech.update(starters_on_reach=mconv.coef()["lr"])
print("mechanism", mech)

# collinearity of spend and time in field
cor = s.assign(ls_w=s.ls - s.groupby("unit").ls.transform("mean"),
               lt_w=s["lt"] - s.groupby("unit")["lt"].transform("mean"),
               lc_w=s.lc - s.groupby("unit").lc.transform("mean"))[["ls_w", "lt_w", "lc_w"]].corr()
print("within-unit correlations\n", cor)
tcoef = models["within + log day-in-field + weekday"].coef()["lt"]

# ---------------- practical scale: how different are recruitments' spend levels? ----------------
ua = s.groupby("unit").agg(spend=("spend", "sum"), st=("starters", "sum"), days=("d", "size"))
ua["daily"] = ua.spend / ua.days
spread = ua.daily.describe(percentiles=[.1, .25, .5, .75, .9])

res = pd.DataFrame(rows)
hetd = pd.DataFrame(het)
res.to_csv("estimates.csv", index=False)
hetd.to_csv("heterogeneity.csv", index=False)
lagtab.to_csv("lags.csv")
json.dump(dict(sample=N, mechanism=mech, first_stage_t=fs_t, boot_reps=len(boots),
               corr_within=cor.round(3).to_dict(), time_coef_log_day=tcoef,
               lag_sum=btot, unit_daily_spend=spread.round(2).to_dict()),
          open("summary.json", "w"), indent=1, default=float)
pd.set_option("display.width", 250)
print(res.round(3).to_string())
print(hetd.round(3).to_string())
print(spread)

# ---------------- binned scatter data (figure) ----------------
# relative cost per starter by within-unit spend decile: sum(spend)/sum(expected at unit's own average)
s["rel_sp"] = s.spend / s.groupby("unit").spend.transform(lambda x: np.exp(np.log(x).mean()))
s["exp_st"] = s.spend * s.groupby("unit").starters.transform("sum") / s.groupby("unit").spend.transform("sum")
s["bin"] = pd.qcut(np.log(s.rel_sp), 10, labels=False)
bs = s.groupby("bin").agg(rel_sp=("rel_sp", "median"), st=("starters", "sum"), ex=("exp_st", "sum"), n=("d", "size"))
bs["rel_cps"] = bs.ex / bs.st
# same after removing time-in-field: residualise with the time coefficient from the within model
b_lt = tcoef
s["exp_t"] = s.exp_st * np.exp(b_lt * (s["lt"] - s.groupby("unit")["lt"].transform("mean")))
s["exp_t"] *= s.groupby("unit").starters.transform("sum") / s.groupby("unit").exp_t.transform("sum")
bs["rel_cps_t"] = s.groupby("bin").exp_t.sum() / bs.st
# boot CI per bin by resampling study groups
bb = []
for i in range(200):
    pick = rng.choice(s.comp.unique(), s.comp.nunique(), replace=True)
    d = pd.concat([s[s.comp == c] for c in pick])
    g = d.groupby("bin").agg(st=("starters", "sum"), ex=("exp_st", "sum"))
    bb.append(g.ex / g.st)
bb = pd.concat(bb, axis=1)
bs["lo"], bs["hi"] = bb.quantile(.025, axis=1), bb.quantile(.975, axis=1)
bs.to_csv("binscatter.csv")
# time in field profile
s["wk"] = np.minimum((s.day_in_field - 1) // 7, 6)
tp = s.groupby("wk").agg(st=("starters", "sum"), ex=("exp_st", "sum"), n=("d", "size"),
                         rel_sp=("rel_sp", "median"))
tp["rel_cps"] = tp.ex / tp.st
tp.to_csv("time_profile.csv")
print(bs.round(3)); print(tp.round(3))
s.drop(columns=["cdate"]).to_csv("analysis_sample.csv", index=False)
