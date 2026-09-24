WITH x AS (SELECT e.study_id, c.key AS camp, s.key AS strat, coalesce(s.value->>'date_start', e.period_start::date::string) AS d,
  max((s.value->>'spend')::float8) AS spend, max((s.value->>'impressions')::float8) AS imp, max((s.value->>'reach')::float8) AS reach,
  max((s.value->>'unique_clicks')::float8) AS uclicks, max((s.value->>'cpm')::float8) AS cpm
  FROM recruitment_data_events e, jsonb_each(e.data) AS c, jsonb_each(c.value) AS s
  WHERE jsonb_typeof(c.value)='object' AND jsonb_typeof(s.value)='object' AND s.value->>'spend' IS NOT NULL GROUP BY 1,2,3,4),
cs AS (SELECT c.key AS camp, count(DISTINCT e.study_id) AS nst FROM recruitment_data_events e, jsonb_each(e.data) AS c WHERE jsonb_typeof(c.value)='object' GROUP BY 1)
SELECT x.*, cs.nst FROM x JOIN cs ON cs.camp=x.camp
