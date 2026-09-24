"""Three review figures from analyse.py / robustness.py outputs. Not for publication as-is."""
import numpy as np, pandas as pd, json, matplotlib, matplotlib.ticker
matplotlib.use("Agg"); import matplotlib.pyplot as plt
BLUE, INK, INK2, GRID, SURF, ORANGE = "#2a78d6", "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb", "#eb6834"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF})
est = pd.read_csv("estimates.csv"); het = pd.read_csv("heterogeneity.csv"); bs = pd.read_csv("binscatter.csv")
S = json.load(open("summary.json"))["sample"]
b = est.loc[est.model == "within + log day-in-field + weekday", "b"].item()

# 1. binned scatter
fig, ax = plt.subplots(figsize=(7, 4.6))
ax.set_xscale("log"); ax.set_yscale("log")
x = np.geomspace(bs.rel_sp.min() * .8, bs.rel_sp.max() * 1.2, 50)
ax.plot(x, x ** (1 - b) / np.exp(np.average(np.log(bs.rel_sp.values ** (1 - b)), weights=bs.st)) * np.exp(np.average(np.log(bs.rel_cps), weights=bs.st)),
        color=INK2, lw=1, ls="--", zorder=1)
ax.vlines(bs.rel_sp, bs.lo, bs.hi, color=BLUE, lw=2, alpha=.45, zorder=2)
ax.scatter(bs.rel_sp, bs.rel_cps, s=40, color=BLUE, edgecolor=SURF, linewidth=2, zorder=3)
for v in [.25, .5, 1, 2, 4]:
    ax.axvline(v, color=GRID, lw=.6, zorder=0)
for v in [.5, 1, 1.5]:
    ax.axhline(v, color=GRID, lw=.6, zorder=0)
ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); ax.set_xticks([.25, .5, 1, 2, 4]); ax.set_xticklabels(["¼×", "½×", "1×", "2×", "4×"])
ax.set_yticks([.4, .5, .7, 1, 1.5]); ax.set_yticklabels(["0.4×", "0.5×", "0.7×", "1×", "1.5×"])
ax.set_xlabel("Daily spend, relative to that audience's typical day")
ax.set_ylabel("Ad cost per person who started,\nrelative to that audience's average")
ax.text(1.6, .45, f"slope ≈ {1-b:.2f}\ndoubling spend ≈ +{100*(2**(1-b)-1):.0f}% per person", color=INK2, fontsize=9)
ax.set_title("Same audience, bigger day: each person costs more", loc="left", color=INK, fontsize=12)
fig.text(.01, .01, f"{S['units']} audiences (strata) · {S['study_groups']} recruitments · {S['unit_days']:,} audience-days · "
         "\ndeciles of within-audience daily spend; bars = 95% bootstrap over recruitments", color=INK2, fontsize=7.5)
fig.tight_layout(rect=(0, .06, 1, 1)); fig.savefig("fig1_binscatter.svg"); fig.savefig("fig1_binscatter.png", dpi=150)

# 2. estimate across specifications + by geometry
rows = pd.concat([est.assign(grp="spec"), het.assign(grp="het")])
lab = {"between units (no FE): avg daily spend": "Across audiences, no controls (confounded)",
       "within stratum": "Within audience",
       "within + log day-in-field + weekday": "  + time in field, weekday  (headline)",
       "within + log cumulative spend + weekday": "  + cumulative spend instead",
       "within + both time controls + weekday": "  + both time controls",
       "within + study-group x date FE": "  + recruitment × date effects",
       "3-day blocks, within + day-in-field": "  3-day blocks (timezone-proof)",
       "study-group total per day, within + day-in-field": "Whole recruitment's daily total",
       "control-function IV: rest-of-study spend": "IV: rest of recruitment's spend that day"}
rows["label"] = rows.model.map(lambda m: lab.get(m, m.replace("geometry = ", "Geometry: ").replace("unit median daily spend tercile = ", "Typical spend: ")))
rows = rows.iloc[::-1].reset_index(drop=True)
fig, ax = plt.subplots(figsize=(7.2, 5.6))
for i, r in rows.iterrows():
    c = ORANGE if r.model.startswith("between") else BLUE
    ax.hlines(i, r.double_lo, r.double_hi, color=c, lw=2, alpha=.5)
    ax.scatter(r.double_pct, i, s=36, color=c, edgecolor=SURF, linewidth=2, zorder=3)
    ax.text(r.double_hi + 2, i, f"+{r.double_pct:.0f}%", va="center", fontsize=8, color=INK2)
ax.set_yticks(range(len(rows))); ax.set_yticklabels(rows.label, fontsize=8.5)
ax.axvline(0, color=INK2, lw=.8)
ax.set_xlabel("Change in ad cost per starter when daily spend doubles (95% CI)")
ax.grid(axis="x", color=GRID, lw=.6); ax.set_axisbelow(True)
nh = (rows.grp == "het").sum()
ax.axhline(nh - .5, color=GRID, lw=1)
ax.set_title("The estimate barely moves across specifications", loc="left", color=INK, fontsize=12)
fig.tight_layout(); fig.savefig("fig2_estimates.svg"); fig.savefig("fig2_estimates.png", dpi=150)

# 3. time in field
tp = pd.read_csv("time_profile.csv")
fig, ax = plt.subplots(figsize=(6.4, 3.4))
lbl = ["wk 1", "wk 2", "wk 3", "wk 4", "wk 5", "wk 6", "wk 7+"]
ax.bar(range(len(tp)), tp.rel_cps, color=BLUE, width=.6)
for i, r in tp.iterrows():
    ax.text(i, r.rel_cps + .02, f"{r.rel_cps:.2f}×", ha="center", fontsize=8, color=INK2)
ax.set_xticks(range(len(tp))); ax.set_xticklabels(lbl)
ax.axhline(1, color=INK2, lw=.8, ls="--")
ax.set_ylabel("Cost per starter vs\nexpected at audience average", fontsize=9)
ax.set_title("Time in field: first week cheaper, then roughly flat", loc="left", color=INK, fontsize=12)
fig.tight_layout(); fig.savefig("fig3_time_in_field.svg"); fig.savefig("fig3_time_in_field.png", dpi=150)
