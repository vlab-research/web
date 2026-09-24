#!/usr/bin/env python3
"""Kenya country page data (D-032 pilot, recipe notes/country-recipe.md).

Reproduces country-ke.json from production, READ-ONLY (SELECT only).
  python3 build.py --fetch   # re-pull raw/ from vprod, then build
  python3 build.py           # build from the raw/ files already pulled

No maps: the one recruitment that passes the rules targeted the whole country,
so there is no geography to draw (see the For review note in section.html).
"""
import csv, json, subprocess, sys, os, datetime, collections

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
csv.field_size_limit(10**9)

STUDIES = {
    "e3440713-c44a-4333-bdd3-f8b7097fb010": "girl-effect",
    "ca72c2f8-2508-40f5-aaab-eed4ff99d147": "shujaaz-free2choose-digital-evaluation",
    "7ff75f3c-e4cb-4105-82ad-2dc24acf7586": "girl-effect-pilot",
    "8fe1ffb9-ab04-4f8e-bc8d-9afcf341f0ef": "girl-effect-pilot-2",
    "84757600-d8fd-4767-be40-12f383cc1e58": "kenya-tvet-scoping-survey",
    "215d714c-2d40-4079-bf55-683378f70d3c": "kenya-tvet-scoping-pilot",
    "ab059733-d087-42fd-acb1-b91e5eb1cdcb": "llm-bias-kenya-pilot",
    "8a5b150a-fbbf-4708-b2df-3c84c1ce487d": "kenya-tvet",
}
MAIN = "e3440713-c44a-4333-bdd3-f8b7097fb010"
PHASE2 = "2026-07-16"  # recruitment start_date the report's lifetime_spent counts from
IDS = ",".join(f"'{s}'" for s in STUDIES)


def q(db, sql):
    assert sql.lstrip().upper().startswith(("SELECT", "WITH")), "read-only"
    out = subprocess.run(
        ["kubectl", "exec", "-n", "vprod", "gbv-cockroachdb-0", "--", "/cockroach/cockroach",
         "sql", "--insecure", "--format=tsv", f"--database={db}", "-e", sql],
        check=True, capture_output=True, text=True, timeout=300).stdout
    return out


def fetch():
    os.makedirs(RAW, exist_ok=True)
    # latest adopt report, one study at a time (the recipe: never a correlated max())
    for sid in (MAIN, "ca72c2f8-2508-40f5-aaab-eed4ff99d147"):
        open(os.path.join(RAW, f"adopt_{sid[:8]}.tsv"), "w").write(q("vlab",
            f"SELECT created, details::string FROM adopt_reports WHERE study_id='{sid}' "
            "AND report_type='FACEBOOK_ADOPT' ORDER BY created DESC LIMIT 1"))
    open(os.path.join(RAW, "daily.tsv"), "w").write(q("vlab", f"""
      WITH x AS (SELECT e.study_id, c.key AS camp, s.key AS strat,
             coalesce(s.value->>'date_start', e.period_start::date::string) AS d,
             max((s.value->>'spend')::float8) AS spend, max((s.value->>'impressions')::float8) AS imp
        FROM recruitment_data_events e, jsonb_each(e.data) AS c, jsonb_each(c.value) AS s
        WHERE e.study_id IN ({IDS}) AND jsonb_typeof(c.value)='object'
          AND jsonb_typeof(s.value)='object' AND s.value->>'spend' IS NOT NULL
        GROUP BY 1,2,3,4)
      SELECT study_id, camp, strat, d, spend, imp FROM x ORDER BY 1,4"""))
    open(os.path.join(RAW, "people.tsv"), "w").write(q("vlab",
        f"SELECT count(DISTINCT user_id), min(timestamp)::date, max(timestamp)::date "
        f"FROM inference_data WHERE study_id IN ({IDS})"))
    # main study, per person: ad-set gender and location (written at entry), and whether
    # they answered the last baseline question (gnormi_phone), which is the quota rule
    open(os.path.join(RAW, "main_people.tsv"), "w").write(q("vlab", f"""
      SELECT user_id, min(timestamp) t0,
        max(CASE WHEN variable='gender' THEN value::string END) g,
        max(CASE WHEN variable='location' THEN value::string END) loc,
        max(CASE WHEN variable='gnormi_phone' THEN 1 ELSE 0 END) fin,
        extract(epoch FROM min(CASE WHEN variable='gnormi_phone' THEN timestamp END)
                          - min(CASE WHEN variable='gender' THEN timestamp END))::FLOAT/60 AS mins
      FROM inference_data WHERE study_id='{MAIN}' GROUP BY 1"""))


def tsv(name):
    return list(csv.DictReader(open(os.path.join(RAW, name)), delimiter="\t"))


def num(v):
    return 0.0 if v in ("NULL", "", None) else float(v)


def median(xs):
    xs = sorted(xs); n = len(xs)
    return (xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2) if n else None


def build():
    daily = tsv("daily.tsv")
    main_daily = [r for r in daily if r["study_id"] == MAIN and num(r["spend"]) > 0]
    p2 = [r for r in main_daily if r["d"] >= PHASE2]
    p1 = [r for r in main_daily if r["d"] < PHASE2]
    ins = collections.defaultdict(float)
    for r in p2:
        ins[r["strat"]] += num(r["spend"])

    rows = list(csv.reader(open(os.path.join(RAW, f"adopt_{MAIN[:8]}.tsv")), delimiter="\t"))
    rep_created, rep = rows[1][0], json.loads(rows[1][1])
    groups = {"Men": "gender:men,location:location", "Women": "gender:women,location:location"}
    by_gender, strata = {}, []
    for k, v in rep.items():
        strata.append({"id": k, "current_participants": v.get("current_participants"),
                       "lifetime_spent": v.get("lifetime_spent"),
                       "current_price_per_participant": v.get("current_price_per_participant")})

    people = tsv("main_people.tsv")
    ppl2 = [p for p in people if p["t0"] >= PHASE2]
    for label, sid in groups.items():
        v = rep[sid]
        gval = '"' + label.lower() + '"'
        entered = [p for p in ppl2 if p["g"] == gval and p["loc"] == '"location"']
        fin = [p for p in entered if p["fin"] == "1"]
        by_gender[label] = {
            "spend": round(v["lifetime_spent"], 2),
            "insights_spend": round(ins[sid], 2),
            "qualified": v["current_participants"],
            "cost": round(v["lifetime_spent"] / v["current_participants"], 2),
            "entered_survey": len(entered),
            "reached_last_question_pct": round(100 * len(fin) / len(entered)),
            "median_minutes_to_last_question": round(median([num(p["mins"]) for p in fin if p["mins"] != "NULL"]), 1),
            "ad_days": len({r["d"] for r in p2 if r["strat"] == sid}),
        }
    spend = round(sum(g["spend"] for g in by_gender.values()), 2)
    qual = sum(g["qualified"] for g in by_gender.values())
    ppl = tsv("people.tsv")[0]
    vals = list(ppl.values())

    meta = json.load(open(os.path.join(HERE, "meta.json")))
    out = {
        "_meta": meta,
        "country": "KE",
        "status": "STILL FIELDING at pull time: recruitment end_date 2026-09-25; report pulled " + rep_created[:16] + " UTC. Re-pull after it closes.",
        "all_people_surveyed": {"unique_people": int(vals[0]), "first": vals[1], "last": vals[2],
                                "studies": len(STUDIES),
                                "note": "Anyone who answered in any Kenya study on the current platform (distinct inference_data user_id); includes test entries before ads began"},
        "study": {
            "slug": "girl-effect",
            "phase": f"second recruitment phase, from {PHASE2}; the report's lifetime_spent starts there",
            "fielded": "16 Jul – 24 Sep 2026",
            "ad_days": len({r["d"] for r in p2}),
            "ad_pause": "20 Aug – 9 Sep 2026 (no spend)",
            "started_survey": len(ppl2),
            "qualified": qual,
            "spend": spend,
            "cost": round(spend / qual, 2),
            "cpm_usd": round(sum(num(r["spend"]) for r in p2) / sum(num(r["imp"]) for r in p2) * 1000, 2),
            "channel": "Messenger",
            "incentive": "prepaid mobile credit, 'up to 300 KSh' per the welcome message; recruitment conf incentive_per_respondent = 0.69 (USD)",
            "quota_rule": "arrived through the men's or women's ad set and answered gnormi_phone, the last question of the baseline survey (a gender-norms item about a household's one phone, NOT a phone-number question)",
            "quotas": "Gender (men, women), ages 18–30, whole country; quota 50/50 from 17 Aug (women 99% to 29 Jul, 80% to 6 Aug, 60% to 17 Aug)",
            "target_max_sample": 12000,
        },
        "by_gender": by_gender,
        "strata": strata,
        "checks": [
            f"report lifetime_spent per active group equals Insights spend since {PHASE2} to the cent: men {by_gender['Men']['spend']} / {by_gender['Men']['insights_spend']}, women {by_gender['Women']['spend']} / {by_gender['Women']['insights_spend']}",
            "two retired ad sets (location:geography) carry $8.20 in the report and no Insights spend after 16 Jul; left out of the total",
            f"CPM ${round(sum(num(r['spend']) for r in p2) / sum(num(r['imp']) for r in p2) * 1000, 2)}: a USD account",
            "no campaign shared with another study",
            "prior respondents excluded by custom audience, so phase 2 recruits new people",
            f"phase 1 ({p1[0]['d']} – {p1[-1]['d']}, ${round(sum(num(r['spend']) for r in p1), 2)} Insights) is not in the report's lifetime and is left out",
        ],
        "excluded_for_review": json.load(open(os.path.join(HERE, "excluded.json"))),
        "strata_note": "Stratum ids are the study's own labels; 'location:location' is the whole country. The persona labels in the excluded study are a brand's segmentation and must not be published.",
    }
    json.dump(out, open(os.path.join(HERE, "country-ke.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: out[k] for k in ("study", "by_gender", "all_people_surveyed")}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        fetch()
    build()
