#!/bin/sh
# Re-pull every input from production CockroachDB. READ-ONLY: SELECT statements only.
# Then: .venv/bin/python build_panel.py && .venv/bin/python analyse.py && .venv/bin/python robustness.py && .venv/bin/python figures.py
set -e
cd "$(dirname "$0")"; mkdir -p raw
q() { timeout 300 kubectl exec -n vprod gbv-cockroachdb-0 -- /cockroach/cockroach sql --insecure --format=tsv --database=vlab -e "$1"; }
q "SELECT id, slug FROM studies" > raw/studies.tsv
q "SELECT study_id, created, conf->>'ad_account' acct, conf->>'country_code' cc FROM study_confs WHERE conf_type='general' ORDER BY 1,2" > raw/general_hist.tsv
q "SELECT DISTINCT c.study_id, s->>'id' AS sid, s->'metadata' AS md FROM study_confs c, jsonb_array_elements(c.conf) AS s WHERE c.conf_type='strata' AND jsonb_typeof(c.conf)='array'" > raw/strata_md.tsv
q "SELECT DISTINCT ON (c.study_id, s->>'id') c.study_id, s->>'id' AS sid, s->'facebook_targeting'->'geo_locations' AS geo, s->'facebook_targeting'->'age_min' amin, s->'facebook_targeting'->'age_max' amax, s->'facebook_targeting'->'genders' g FROM study_confs c, jsonb_array_elements(c.conf) AS s WHERE c.conf_type='strata' AND jsonb_typeof(c.conf)='array' ORDER BY c.study_id, s->>'id', c.created DESC" > raw/strata_geo.tsv
q "$(cat spend.sql)" > raw/spend_daily.tsv
# people.sql has the metadata-variable list (every key in any stratum metadata, bare and md:-prefixed) baked in
q "$(cat people.sql)" > raw/people_new_hourly.tsv
