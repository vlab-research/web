-- Qualified respondents per stratum under each study's LATEST question_targeting rule
-- (phone_number for EG/IQ/MA/JO, pre_pay_info for SA): metadata Gender x Age x City from the
-- study's own inference pool, arrival (first inference timestamp) inside the study's ad window,
-- and an answer to the rule question at any time. Read-only.
WITH s AS (SELECT * FROM (VALUES
  ('embed-iraq','phone_number','2025-12-26','2026-02-13', ARRAY['Baghdad','Basra','Mosul']),
  ('embed-egypt','phone_number','2025-12-11','2026-01-15', ARRAY['Cairo','Giza','Alexandria']),
  ('embed-ksa','pre_pay_info','2025-12-05','2026-01-15', ARRAY['Riyadh','Jeddah','Mecca']),
  ('embed-morocco','phone_number','2025-12-11','2026-01-12', ARRAY['Casablanca','Fez','Marrakech']),
  ('embed-jordan','phone_number','2025-12-11','2026-01-08', ARRAY['Amman','Irbid','Zarqa'])) AS v(slug, rule, d0, d1, cities)),
pool AS (
  SELECT s.slug, s.rule, s.d0, s.d1, i.user_id,
    max(CASE WHEN variable='City' THEN value->>0 END) city, max(CASE WHEN variable='Gender' THEN value->>0 END) g,
    max(CASE WHEN variable='Age' THEN value->>0 END) a, min(i.timestamp) t
  FROM vlab.inference_data i JOIN vlab.studies st ON st.id=i.study_id JOIN s ON s.slug=st.slug
  GROUP BY 1,2,3,4,5),
r AS (SELECT DISTINCT userid, question_ref FROM chatroach.responses WHERE timestamp > '2025-12-01' AND timestamp < '2026-03-01'
      AND question_ref IN ('phone_number','pre_pay_info') AND shortcode LIKE 'embedpamenadiagpay%')
SELECT p.slug, p.city, p.g, p.a,
  count(*) AS started,
  count(*) FILTER (WHERE p.t::date BETWEEN p.d0::date AND p.d1::date) AS started_in_window,
  count(*) FILTER (WHERE r.userid IS NOT NULL) AS qualified_any_time,
  count(*) FILTER (WHERE r.userid IS NOT NULL AND p.t::date BETWEEN p.d0::date AND p.d1::date) AS qualified,
  min(p.t)::date, max(p.t)::date
FROM pool p JOIN s ON s.slug=p.slug AND p.city = ANY(s.cities) LEFT JOIN r ON r.userid=p.user_id AND r.question_ref=p.rule
GROUP BY 1,2,3,4 ORDER BY 1,2,3,4;
