# Daily spend and cost per person (2026-09-24)

Nandan: *"as we spend more, cost per respondent goes up … see if there's something we can do
about that."* An agent analysed this read-only. The scripts and figures are in
`scripts/pilot-maps/spend-analysis/`. The panel (aggregate counts only, but holding study slugs)
stays in the session scratchpad.

**Finding.** Within the same stratum, starters grow at about spend^0.60, so **ad cost per person
who started grows at about spend^0.40**. Doubling a stratum's daily spend raises cost per
starter by **about 32% (95% CI 22–43%)**. The estimate rests on 306 strata in 38 recruitment
groups: 5,357 stratum-days, 154,255 starters and $224k of USD spend. The model is a Poisson with
stratum fixed effects and errors clustered by recruitment.

**Robustness.** Every check stays within +29% to +37%:
- controlling for time in field and weekday;
- recruitment × date effects;
- dropping each stratum's first and last days;
- keeping only days of $5 or more;
- dropping the two largest recruitments;
- leaving out each recruitment in turn.

An instrument for the optimiser's reallocation (the rest of the recruitment's spend that day)
gives the same +32%. Timezones were aligned per ad account. There is no penalty on days when
spend jumps, so this is not Meta's learning phase resetting.

**Mechanism.** CPM barely moves (elasticity 0.06), and reach rises almost in step (0.83). What
falls is the share of people reached who start. **It is audience depth, not auction price.**

**By audience size**, per doubling: radius areas +46% (36–58%), whole regions +32%, whole
country +24%.

**Time in field** is separate from spend: correlation 0.14 within a stratum. Holding spend
fixed, the first week is about 14% cheaper and weeks 2–6 are flat. "First people are cheap"
is real, but smaller than the spend effect.

**Trap.** Across strata in one recruitment, cost and daily spend correlate at about 1.1, nearly
three times the causal 0.4. The optimiser pushes harder on expensive strata to fill their
quotas. **Do not print daily spend beside a place's cost**, or readers will take the correlation
for the effect. Across recruitments, daily spend per stratum runs from $5.6 to $60 (p10 to
p90), worth about 2.6× in cost. So a pooled place figure partly reflects how hard its
recruitments pushed.

**Inferred, not shown:**
- that a recruitment *planned* at 10× the daily spend costs about 2.6× as much (the estimate
  comes from day-to-day variation);
- that the effect holds for qualified respondents (not modelled).

**Recommendation** (the agent's; not yet decided by Nandan):
- **(d)** A third "how it works" module on every country page: *spending faster in the same
  place costs more per person*, with the chart. It needs a `CLAIMS.md` Definition row, and it
  describes an average across our record, not a law.
- **(b-light)** Each place's typical daily spend per stratum goes in the data table and the
  CSV, not beside the headline.
- **Not (c):** no adjusting figures to a standard spend level. That would put modelled numbers
  on clean-data pages.
