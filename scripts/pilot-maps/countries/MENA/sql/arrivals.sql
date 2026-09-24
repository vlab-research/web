-- Daily first arrivals per country (by ad City metadata), to set against daily ad spend
WITH c AS (SELECT * FROM (VALUES ('IQ','Baghdad'),('IQ','Basra'),('IQ','Mosul'),('EG','Cairo'),('EG','Giza'),('EG','Alexandria'),
  ('SA','Riyadh'),('SA','Jeddah'),('SA','Mecca'),('MA','Casablanca'),('MA','Fez'),('MA','Marrakech'),('JO','Amman'),('JO','Irbid'),('JO','Zarqa')) AS v(cc, city)),
u AS (SELECT i.user_id, c.cc, min(i.timestamp) t FROM inference_data i JOIN studies st ON st.id=i.study_id JOIN c ON c.city=i.value->>0
      WHERE i.variable='City' AND st.slug='embed-uae' GROUP BY 1,2)
SELECT cc, t::date d, count(*) FROM u GROUP BY 1,2 ORDER BY 1,2;
