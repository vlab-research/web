"""Robustness for the headline within-stratum model. Reads analysis_sample.csv (from analyse.py)."""
import numpy as np, pandas as pd, pyfixest as pf, warnings
warnings.filterwarnings("ignore")
s = pd.read_csv("analysis_sample.csv", parse_dates=["d"])
F = "starters ~ ls + lt | unit + dow"
def b(d, f=F):
    m = pf.fepois(f, data=d, vcov={"CRV1": "comp"}); return m.coef()["ls"], m.se()["ls"]
out = []
base = b(s); out.append(("headline", *base, len(s)))
# leave one study group out
jk = []
for c in s.comp.unique():
    d = s[s.comp != c]; jk.append((c, s[s.comp == c].studies.iloc[0][:60], b(d)[0]))
jk = pd.DataFrame(jk, columns=["comp", "studies", "b"]).sort_values("b")
print("leave-one-group-out range of b:", jk.b.min().round(3), jk.b.max().round(3)); print(jk.head(3).to_string()); print(jk.tail(3).to_string())
out.append(("drop first 2 and last day of each unit", *b(s[(s.day_in_field > 2) & (s.d < s.groupby('unit').d.transform('max'))]), 0))
out.append(("spend >= $5 days only", *b(s[s.spend >= 5]), 0))
out.append(("units with >= 14 days", *b(s[s.groupby('unit').d.transform('size') >= 14]), 0))
big = s.groupby("comp").unit.transform("nunique") >= 100
out.append(("drop the two 100+-stratum groups (embed MENA, UNICEF Turkey)", *b(s[~big]), 0))
# asymmetry: day-on-day increases vs decreases (learning-phase resets on budget changes)
s = s.sort_values(["unit", "d"])
s["dls"] = s.groupby("unit").ls.diff()
s["up"] = np.where(s.dls > 0.2, 1, 0)
m = pf.fepois("starters ~ ls + up + lt | unit + dow", data=s.dropna(subset=["dls"]), vcov={"CRV1": "comp"})
print("jump-up day indicator (spend up >22% vs yesterday):", m.coef()["up"].round(3), "se", m.se()["up"].round(3), "b", m.coef()["ls"].round(3))
# weight each study group equally (PPML weights by volume): unit-level OLS on log cps, positive days
q = s[s.starters > 0].copy(); q["lcps"] = np.log(q.spend / q.starters)
w = 1 / q.groupby("comp").d.transform("size")
m = pf.feols("lcps ~ ls + lt | unit + dow", data=q, weights=None, vcov={"CRV1": "comp"})
m2 = pf.feols("lcps ~ ls + lt | unit + dow", data=q.assign(w=w), weights="w", vcov={"CRV1": "comp"})
print("log-log OLS (positive days) CPS elasticity:", m.coef()["ls"].round(3), m.se()["ls"].round(3),
      "| each study group weighted equally:", m2.coef()["ls"].round(3), m2.se()["ls"].round(3))
r = pd.DataFrame(out, columns=["check", "b", "se", "n"]); r["double_pct"] = 100 * (2 ** (1 - r.b) - 1)
print(r.round(3).to_string()); r.to_csv("robustness.csv", index=False); jk.to_csv("jackknife.csv", index=False)
