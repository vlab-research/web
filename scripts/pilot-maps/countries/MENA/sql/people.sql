-- Unique people per country on the current platform. The embed studies share one survey pool, so a
-- person is assigned to a country by the City their ad carried (inference_data City, from ad metadata),
-- never by which study's inference table they sit in. Every study naming the country is included.
WITH c AS (SELECT * FROM (VALUES ('IQ','Baghdad'),('IQ','Basra'),('IQ','Mosul'),('EG','Cairo'),('EG','Giza'),('EG','Alexandria'),
  ('SA','Riyadh'),('SA','Jeddah'),('SA','Mecca'),('MA','Casablanca'),('MA','Fez'),('MA','Marrakech'),('JO','Amman'),('JO','Irbid'),('JO','Zarqa')) AS v(cc, city)),
u AS (SELECT i.user_id, i.value->>0 AS city, min(i.timestamp) t, array_agg(DISTINCT st.slug) sl FROM inference_data i JOIN studies st ON st.id=i.study_id
      WHERE i.variable='City' AND st.slug LIKE 'embed-%' GROUP BY 1,2)
SELECT c.cc, count(DISTINCT u.user_id) people, min(u.t)::date, max(u.t)::date,
  count(DISTINCT u.user_id) FILTER (WHERE u.t < '2025-12-01') pilot_era
FROM u JOIN c ON c.city=u.city GROUP BY 1 ORDER BY 1;
