-- Where people stopped: the furthest baseline question each person answered, by country (read-only)
WITH c AS (SELECT * FROM (VALUES ('IQ','Baghdad'),('IQ','Basra'),('IQ','Mosul'),('EG','Cairo'),('EG','Giza'),('EG','Alexandria'),
  ('SA','Riyadh'),('SA','Jeddah'),('SA','Mecca'),('MA','Casablanca'),('MA','Fez'),('MA','Marrakech'),('JO','Amman'),('JO','Irbid'),('JO','Zarqa')) AS v(cc, city)),
u AS (SELECT DISTINCT i.user_id, c.cc FROM vlab.inference_data i JOIN vlab.studies st ON st.id=i.study_id JOIN c ON c.city=i.value->>0
      WHERE i.variable='City' AND st.slug IN ('embed-iraq','embed-egypt','embed-ksa','embed-morocco','embed-jordan') AND i.timestamp >= '2025-12-01'),
b AS (SELECT userid, max(question_idx) mx, bool_or(question_ref LIKE 'intro_consent%') consent, count(*) n,
        max(shortcode) sc, bool_or(question_ref IN ('no_consent','below_30','city_other','nationality_no')) exited FROM chatroach.responses WHERE shortcode IN ('baselinear','baselineeng','baselinefr','baselinefrenglish','baselineeng1') AND timestamp > '2025-12-01' AND timestamp < '2026-03-01' GROUP BY 1)
SELECT u.cc, count(*) people,
  count(*) FILTER (WHERE b.userid IS NULL) no_baseline_answer,
  count(*) FILTER (WHERE b.mx <= 6 AND NOT b.exited) stopped_at_consent,
  count(*) FILTER (WHERE b.mx BETWEEN 7 AND 16 AND NOT b.exited) stopped_in_screening,
  count(*) FILTER (WHERE b.mx BETWEEN 17 AND 74 AND NOT b.exited) stopped_mid_survey,
  count(*) FILTER (WHERE b.mx BETWEEN 75 AND 84 AND NOT b.exited) reached_height,
  count(*) FILTER (WHERE b.exited) screened_or_declined
FROM u LEFT JOIN b ON b.userid=u.user_id GROUP BY 1 ORDER BY 1;
