WITH x AS (SELECT c.key AS camp, s.key AS strat, coalesce(s.value->>'date_start', e.period_start::date::string) AS d, max((s.value->>'spend')::float8) AS spend, max((s.value->>'impressions')::float8) AS imp FROM recruitment_data_events e, jsonb_each(e.data) AS c, jsonb_each(c.value) AS s WHERE jsonb_typeof(c.value)='object' AND jsonb_typeof(s.value)='object' AND s.value->>'spend' IS NOT NULL GROUP BY 1,2,3),
cs AS (SELECT c.key AS camp, min(e.study_id::string) AS sid FROM recruitment_data_events e, jsonb_each(e.data) AS c WHERE jsonb_typeof(c.value)='object' GROUP BY c.key HAVING count(DISTINCT e.study_id)=1),
sp AS (SELECT cs.sid, sum(x.spend) AS spend, sum(x.imp) AS imp, min(x.d) AS d0, max(x.d) AS d1, count(DISTINCT x.d) AS days FROM x JOIN cs ON cs.camp=x.camp GROUP BY 1),
fs AS (SELECT study_id, user_id, min(timestamp) AS ts FROM inference_data GROUP BY 1,2),
t0 AS (SELECT user_id, min(ts) AS t FROM fs GROUP BY 1),
firsts AS (SELECT f.user_id, f.study_id FROM fs f JOIN t0 ON t0.user_id=f.user_id AND f.ts=t0.t),
k AS (SELECT user_id, count(DISTINCT study_id) AS n FROM firsts GROUP BY 1),
per AS (SELECT f.study_id::string AS sid, count(*) AS all_first, count(*) FILTER (WHERE k.n=1) AS newresp FROM firsts f JOIN k ON k.user_id=f.user_id GROUP BY 1),
tot AS (SELECT study_id::string AS sid, count(*) AS allresp, min(ts)::date AS r0, max(ts)::date AS r1 FROM fs GROUP BY 1)
SELECT s.id, s.slug, tot.allresp, per.all_first, per.newresp, sp.spend, sp.imp, sp.d0, sp.d1, sp.days, tot.r0, tot.r1
FROM studies s LEFT JOIN tot ON tot.sid=s.id::string LEFT JOIN per ON per.sid=s.id::string LEFT JOIN sp ON sp.sid=s.id::string;
