WITH pool AS (
  SELECT i.user_id, max(CASE WHEN variable='City' THEN value->>0 END) city, max(CASE WHEN variable='Gender' THEN value->>0 END) g, max(CASE WHEN variable='Age' THEN value->>0 END) a, min(i.timestamp) t
  FROM vlab.inference_data i WHERE i.study_id='ad2af262-02c5-4ec7-bb5a-5364a715c575' GROUP BY 1),
r AS (SELECT userid, question_ref, min(timestamp) ts FROM chatroach.responses WHERE timestamp > '2025-12-01' AND timestamp < '2026-03-01' AND question_ref IN ('height','phone_number','pre_pay_info','recruit_learn','nationality_ksa','nationality_uae','nationality_no','city_other','below_30','intro_consent_eg') AND (shortcode LIKE 'baseline%' OR shortcode LIKE 'embedpamenadiagpay%') GROUP BY 1,2)
SELECT p.city, count(*) pool,
 count(*) FILTER (WHERE EXISTS (SELECT 1 FROM r WHERE r.userid=p.user_id AND r.question_ref='height')) height,
 count(*) FILTER (WHERE EXISTS (SELECT 1 FROM r WHERE r.userid=p.user_id AND r.question_ref IN ('phone_number','pre_pay_info'))) paystep,
 count(*) FILTER (WHERE EXISTS (SELECT 1 FROM r WHERE r.userid=p.user_id AND r.question_ref='recruit_learn')) rlearn,
 count(*) FILTER (WHERE EXISTS (SELECT 1 FROM r WHERE r.userid=p.user_id AND r.question_ref='city_other')) city_other,
 count(*) FILTER (WHERE EXISTS (SELECT 1 FROM r WHERE r.userid=p.user_id AND r.question_ref='below_30')) below30,
 count(*) FILTER (WHERE EXISTS (SELECT 1 FROM r WHERE r.userid=p.user_id AND r.question_ref='nationality_no')) nat_no,
 min(p.t)::date, max(p.t)::date
FROM pool p GROUP BY 1 ORDER BY 1;
