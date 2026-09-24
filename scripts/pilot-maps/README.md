# Pilot targeting maps (D-032, 2026-09-24)

Maps of exactly where each pilot study's ads were targeted: circles at their true radius, whole
regions, and exclusions, with advertising cost per qualified respondent per group. They are
review material for the country-page pilot, **not wired into the site**, and not yet
registered in `CLAIMS.md`.

- `targeting.json`: the latest strata config (Meta `geo_locations` and
  `excluded_geo_locations`) and per-stratum report for each pilot study, pulled read-only
  from production on 2026-09-23. The Bolivia report in this file is stale. The figures on the
  maps come from `../data/country-*.json`.
- `fetch_ne.py`: downloads Natural Earth 10m admin-1 and populated places, and the GeoNames
  dumps for NG, BO and ID, into this folder. They are large and gitignored; run it first.
- `build_maps.py`: writes `out/*.svg` and `out/summary.json`. The summary holds every number
  drawn, plus circle counts, radii and area shares. Needs shapely: `pip install shapely pyproj`.

What the maps found is in `notes/ws-inbound.md` §7. It is worth knowing before anyone writes
"by state": the 2024 Nigeria "state" strata are 2–4 km circles around towns, and each Bauchi
"LGA" stratum is a radius around a single point.
