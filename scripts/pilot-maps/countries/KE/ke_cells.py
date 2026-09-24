"""Kenya's part of the KE-LAC cell table. Run countries/LAC/cells.py (or ./cells.py here).

The recruitments and their rules are the ones countries/KE/build.py settled (place pilot v6),
split to one cell per ad set as notes/cells-schema.md asks. Where people cannot be split by ad
set (their labels do not say which), the ad sets are pooled into one cell and flagged.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "LAC"))
import cells as E   # the group engine

RAW = os.path.join(HERE, "raw")
# Study ids, survey names, audience-group names and question refs live in the gitignored
# scripts/pilot-maps/private/KE-LAC.inputs.json: they can name a client or a topic.
CFG = E.inputs()["KE"]
STUDIES = {v[0]: k for k, v in CFG["studies"].items()}          # uuid -> neutral key
QREF = CFG["qual_refs"]
WINDOWS = {"KE-2024-09": ("2024-09-22", "2024-10-05"), "KE-2025-02": ("2025-02-04", "2025-02-25"),
           "KE-2025-05": ("2025-05-03", "2025-07-20"), "KE-2025-08": ("2025-08-10", "2025-08-20"),
           "KE-2025-12": ("2025-12-02", "2025-12-20"), "KE-2026-01": ("2026-01-13", "2026-02-01"),
           "KE-2026-05": ("2026-05-19", "2026-07-12"), "KE-2026-07": ("2026-07-15", "2026-09-30")}
LABELS = ["gender", "location", "geography", "demo_group"]


def fetch(salt):
    # 'gender' in the 2025 run is a self-reported answer code (1-4), kept because its quota rule uses it
    E.fetch(RAW, STUDIES, LABELS, ["English", "Kiswahili", "Swahili"], CFG["surveys"],
            [(r, QREF[r], *WINDOWS[r]) for r in WINDOWS], salt)


def priv(key):
    return dict(studies=CFG["studies"][key])


def sid(key):
    return CFG["studies"][key][0][:8]


# ----------------------------------------------------------------------------- places
def places(R):
    tv = R.latest(sid("tv_survey"), "strata")
    pins = next(s for s in tv if "urban" in s["id"])["facebook_targeting"]["geo_locations"]["custom_locations"]
    assert pins == R.latest(sid("tv_pilot"), "strata")[0]["facebook_targeting"]["geo_locations"]["custom_locations"]
    P, check = E.pin_set("KE", pins)
    shu = [s for s in R.latest(sid("groups"), "strata") if (s["facebook_targeting"].get("excluded_geo_locations") or {}).get("cities")]
    by_n = {len(s["facebook_targeting"]["excluded_geo_locations"]["cities"]): s for s in shu}

    def excl(n):
        out, chk = [], []
        for c in by_n[n]["facebook_targeting"]["excluded_geo_locations"]["cities"]:
            p = E.city_point("KE", c["name"])
            out.append([round(p["lat"], 5), round(p["lon"], 5), round(E.km(c), 2)])
            chk.append(dict(meta_city=c["name"], geonames=p["name"], feature=p["code"], pop=p["pop"]))
        return out, chk
    ex10, c10 = excl(10)
    exN, cN = excl(1)
    self = {}
    self["KE:country"] = dict(country="KE", type="country", label="Kenya, whole country")
    k10 = f"KE:country-minus:{len(ex10)}-cities-{E.radius_label(ex10)}"
    self[k10] = dict(country="KE", type="country_minus", label=f"Kenya except {len(ex10)} cities ({E.radius_label(ex10).replace('km', ' km')})",
                     pins_excluded=ex10)
    kN = f"KE:country-minus:{len(exN)}-city-{E.radius_label(exN)}"
    self[kN] = dict(country="KE", type="country_minus", label=f"Kenya except the capital ({E.radius_label(exN).replace('km', ' km')})",
                    pins_excluded=exN)
    kin = f"KE:radius:{len(P)}-towns-{E.radius_label(P)}"
    self[kin] = dict(country="KE", type="radius_set", label=f"Inside {len(P)} radius areas ({E.radius_label(P).replace('km', ' km').replace('-', '–')})",
                     pins=P)
    self[kin.replace(":radius:", ":outside:")] = dict(country="KE", type="radius_outside",
                                                     label=f"Kenya outside the {len(P)} radius areas", complement_of=kin)
    global PLACE
    PLACE = dict(country="KE:country", ten=k10, nbo=kN, inside=kin, outside=kin.replace(":radius:", ":outside:"))
    unnamed = [i for i, c in enumerate(check) if c is None]
    return self, {kin: dict(pins=len(P), named_within_5km=len(P) - len(unnamed), unnamed_pins=[P[i] for i in unnamed],
                            names=[c and c["name"] for c in check]),
                  k10: dict(excluded_cities=c10), kN: dict(excluded_cities=cN)}


PLACE = {}
SEEN = {"tv": set(), "ge": set()}   # people counted in an earlier sibling recruitment


# ----------------------------------------------------------------------------- recruitments
def recruitments(R):
    out = []
    # --- KE-2024-09 and KE-2025-02: one scoping survey, two ad runs, 81 radius areas vs the rest
    s1 = sid("tv_pilot")
    tv_side = lambda loc: ("inside", PLACE["inside"]) if loc == "urban" else ("outside", PLACE["outside"])
    cells = {}
    for g in ("men", "women"):
        for loc in ("urban", "rural"):
            st = R.stratum(s1, f"gender:{g},location:{loc}")
            side, pl = tv_side(loc)
            cells[f"gender:{g},location:{loc}"] = dict(place=pl, side=side, ads=E.ads_of(st), flags=["pin_checked"] + E.ad_flags(st))
    out.append(dict(
        id="KE-2024-09", country="KE", sids=[s1], labels=["gender", "location"], cells=cells,
        spend=lambda s, camp, strat, d: strat if strat in cells else None,
        person=lambda m, t0, u, s: f"gender:{m['gender']},location:{m['location']}" if {"gender", "location"} <= set(m) else None,
        qual=lambda v, k: QREF["KE-2024-09"] if QREF["KE-2024-09"] in v else None,
        register=lambda c: SEEN["tv"].update(c),
        private=priv("tv_pilot"),
        criteria=dict(rec="KE-2024-09", country="KE", round="pilot",
                      ads=dict(genders=["women", "men"], age_min=18, age_max=35, interests=False),
                      screen=["age:15-35", "consent"],
                      who_qualified="aged 15–35 (ads shown to 18–35); reached the end of the questions, about {m} minutes in",
                      qualify_rule="answered the last question before the contact and payment questions",
                      channel="messenger", languages=["en"], incentive=dict(amount=260, currency="KES", form="airtime"),
                      notes=("Pilot of the next recruitment's survey: gender x inside/outside 81 radius areas around towns. "
                             "The ad message offered 260 KES of airtime until 25 Sep 2024 and 130 KES after. "
                             "Insights recorded no impressions field for these runs; impressions are spend / CPM (CPM $1.9-2.5, a USD account). "
                             "Cost per person who started is very low ($0.04) and matches Meta's own count of conversations started "
                             "(see private map). qualify_point counts every prompt answered, including 'OK' taps."))))
    s2 = sid("tv_survey")
    cells2 = {}
    for per, lo_hi in (("pre", ("0000", "2025-02-09")), ("post", ("2025-02-10", "9999"))):
        for loc in ("urban", "rural"):
            side, pl = tv_side(loc)
            if per == "pre":
                st = R.stratum(s2, f"gender:women,location:{loc}")
                ads = dict(E.ads_of(st), genders="all")
                fl = ["pin_checked", "pooled_ad_sets"]
            else:
                st = R.stratum(s2, f"gender:1,location:{loc}")
                ads = E.ads_of(st)
                fl = ["pin_checked"]
            cells2[f"{per}:{loc}"] = dict(place=pl, side=side, ads=ads, flags=fl + E.ad_flags(st))

    def spend2(s, camp, strat, d):
        loc = strat.split("location:")[1]
        if strat.startswith(("gender:men", "gender:women")):
            return f"pre:{loc}"
        if strat.startswith("gender:1"):
            return f"post:{loc}"
        return None       # gender:2 (men) never spent after the rename
    out.append(dict(
        id="KE-2025-02", country="KE", sids=[s2], labels=["location"], cells=cells2, spend=spend2,
        person=lambda m, t0, u, s: (("pre" if t0[:10] <= "2025-02-09" else "post") + ":" + m["location"]) if "location" in m else None,
        # final rule: location label, self-reported gender answer 1 or 2 (each has a quota), and the last question answered
        qual=lambda v, k: QREF["KE-2025-02"] if QREF["KE-2025-02"] in v and v.get("gender", ("",))[0] in ("1", "2") else None,
        siblings=SEEN["tv"],
        private=dict(priv("tv_survey"),
                     note="strata renamed 10 Feb 2025 (gender:women/men -> gender:1/2); only gender:1 (Meta women) spent after"),
        criteria=dict(rec="KE-2025-02", country="KE", round="cross-section",
                      ads=dict(genders=["women", "men"], age_min=18, age_max=35, interests=False),
                      screen=["age:15-35", "consent"],
                      who_qualified="aged 15–35 (ads shown to 18–35), answered the gender question as a woman or a man; "
                                    "reached the end of the questions, about {m} minutes in",
                      qualify_rule="answered the last question before the contact and payment questions",
                      channel="messenger", languages=["en"], incentive=dict(amount=30, currency="KES", form="airtime"),
                      notes=("Same survey and radius areas as KE-2024-09. Ads ran 5-7 Feb 2025 to women and men, then from 11 Feb "
                             "to women only (renamed ad sets). People carry only the inside/outside label, so the 5-7 Feb cells pool "
                             "the men's and women's ad sets. People already counted in KE-2024-09 are not counted again. "
                             "Impressions are spend / CPM (no impressions field recorded)."))))
    # --- KE-2025-05: five audience groups chosen by age, gender and Meta interests
    s3 = sid("groups")
    SHU = dict(CFG["demo_groups"])      # final group name -> the short name its ad set had for one day
    cells3 = {}
    for long, short in SHU.items():
        for name in (long, short):
            st = R.stratum(s3, f"demo_group:{name}")
            nex = len((st["facebook_targeting"].get("excluded_geo_locations") or {}).get("cities") or [])
            pl = {0: PLACE["country"], 10: PLACE["ten"], 1: PLACE["nbo"]}[nex]
            fl = E.ad_flags(st) + ([] if name == long else ["renamed_ad_set_one_day", "not_in_final_quota"])
            cells3[name] = dict(place=pl, side=None, ads=E.ads_of(st), flags=fl)
    out.append(dict(
        id="KE-2025-05", country="KE", sids=[s3], labels=["demo_group"], cells=cells3,
        spend=lambda s, camp, strat, d: strat.split(":", 1)[1] if strat.split(":", 1)[1] in cells3 else None,
        person=lambda m, t0, u, s: m.get("demo_group") if m.get("demo_group") in cells3 else None,
        qual=lambda v, k: QREF["KE-2025-05"] if QREF["KE-2025-05"] in v and k in SHU else None,
        private=priv("groups"),
        criteria=dict(rec="KE-2025-05", country="KE", round="baseline",
                      ads=dict(genders=["women", "men"], age_min=18, age_max=24, interests=True),
                      screen=["consent", "gave_phone"],
                      who_qualified="aged 18–24 by the ads, mostly women, chosen by Meta interests; gave a phone number and "
                                    "reached the end of the questions, about {m} minutes in",
                      qualify_rule="answered the final phone-number question (the payment step)",
                      channel="messenger", languages=["sw", "en"], incentive=dict(amount=100, currency="KES", form="airtime"),
                      notes=("Five audience groups, each an ad set with its own ages (18, 18-21, 22-24), gender and Meta "
                             "interests/behaviours; followers of the sponsor's pages excluded. Two groups excluded cities: "
                             "10 cities at 16 km, and the capital at 24 km. The five short-named ad sets ran one day (5 May 2025) "
                             "after a rename and are outside the final quota groups, so their people never qualify. "
                             "No screening question beyond consent; a phone number is asked early and again at the end."))))
    # --- KE-2025-08: whole country, men and women, language choice
    s4 = sid("lang")
    cells4 = {}
    for g in ("men", "women"):
        st = R.stratum(s4, f"gender:{g},geography:country,language:Swahili")
        cells4[g] = dict(place=PLACE["country"], side=None, ads=E.ads_of(st), flags=["pooled_ad_sets", "quota_rule_quirk"] + E.ad_flags(st))
    out.append(dict(
        id="KE-2025-08", country="KE", sids=[s4], labels=["gender", "geography"], cells=cells4,
        spend=lambda s, camp, strat, d: strat.split(",")[0].split(":")[1],
        person=lambda m, t0, u, s: m.get("gender"),
        qual=lambda v, k: QREF["KE-2025-08"] if QREF["KE-2025-08"] in v and v.get("language", ("",))[0] in ("English", "Swahili") else None,
        private=dict(priv("lang"),
                     note="ad sets per gender x language (English ones spent $0.38); people carry only the gender label"),
        criteria=dict(rec="KE-2025-08", country="KE", round="pilot",
                      ads=dict(genders=["women", "men"], age_min=18, age_max=65, interests=False),
                      screen=["age:18-99", "consent", "education:max_secondary", "language:en"],
                      who_qualified="adults who had not completed a university degree and chose English; "
                                    "reached the end of the questions, about {m} minutes in",
                      qualify_rule="answered the mobile-operator question at the end, and chose English or Swahili "
                                   "(as the quota rule was written)",
                      channel="messenger", languages=["en", "sw"], incentive=dict(amount=35, currency="KES", form="airtime"),
                      notes=("The final quota rule asks for language = English or 'Swahili', but the answer was stored as "
                             "'Kiswahili', so only people who chose English qualify under the rule as written (kept as written; "
                             "hence the language:en tag). Each gender had two ad sets (by language) that people's labels do not "
                             "separate; pooled. Screen-outs: under 18, a university or higher degree, an age answer that contradicts "
                             "the age band."))))
    # --- two pilots and the two phases of the main run (one survey family, whole country, men and women)
    def ge(rid, key, labels, rnd, screen, langs, inc, notes, loc=None, siblings=None, register=None, age=(18, 30)):
        s = sid(key)
        qref = QREF[rid]
        cells = {}
        for g in ("men", "women"):
            skey = f"gender:{g},geography:country" if loc is None else f"gender:{g},location:{loc}"
            st = R.stratum(s, skey)
            cells[g] = dict(place=PLACE["country"], side=None, ads=E.ads_of(st), flags=E.ad_flags(st))
        def spend(s_, camp, strat, d):
            if loc is not None and f"location:{loc}" not in strat:
                return None
            return strat.split(",")[0].split(":")[1]
        def person(m, t0, u, s_):
            if loc is not None and m.get("location") != loc:
                return None
            return m.get("gender")
        return dict(id=rid, country="KE", sids=[s], labels=labels, cells=cells, spend=spend, person=person,
                    qual=lambda v, k: qref if qref in v else None, siblings=siblings or set(), register=register or (lambda c: None),
                    private=priv(key),
                    criteria=dict(rec=rid, country="KE", round=rnd,
                                  ads=dict(genders=["women", "men"], age_min=age[0], age_max=age[1], interests=False),
                                  screen=screen, who_qualified="aged 18–30; reached the end of the questions, about {m} minutes in",
                                  qualify_rule="answered the last question of the first questionnaire",
                                  channel="messenger", languages=langs, incentive=inc, notes=notes))
    out.append(ge("KE-2025-12", "p1", ["gender", "geography"], "pilot",
                  ["age:18-30", "consent", "attention_check"], ["en"],
                  dict(amount=225, currency="KES", form="airtime"),
                  "Whole country, men and women. The ad message said 'up to 225 KES' (to 150 on 12 Dec), across two "
                  "questionnaires; the consent text says 75 KES per questionnaire. Two attention checks screen out.",
                  register=lambda c: SEEN["ge"].update(c)))
    out.append(ge("KE-2026-01", "p2", ["gender", "geography"], "pilot",
                  ["age:18-30", "has_whatsapp", "consent", "attention_check"], ["en"],
                  dict(amount=150, currency="KES", form="airtime"),
                  "Second pilot, same survey family. 'Up to 150 KES' across questionnaires. People already counted in "
                  "KE-2025-12 (736 carried over) are not counted again.", siblings=SEEN["ge"]))
    out.append(ge("KE-2026-05", "main", ["gender", "location"], "baseline",
                  ["age:18-30", "has_whatsapp", "consent", "attention_check"], ["en", "sw"],
                  dict(amount=300, currency="KES", form="airtime"),
                  "First phase of the main run (ad sets labelled for this phase); earlier pilot respondents excluded by a "
                  "custom audience. 'Up to 300 KES' across questionnaires. 1,700+ people whose first record is the last "
                  "question with no ad labels are not attributable and not counted.", loc="geography"))
    out.append(ge("KE-2026-07", "main", ["gender", "location"], "baseline",
                  ["age:18-30", "has_whatsapp", "consent", "attention_check"], ["en", "sw"],
                  dict(amount=300, currency="KES", form="airtime"),
                  "Second phase of the main run, new ad sets, moved to another USD ad account on 8 Jul 2026; a custom "
                  "audience of earlier respondents excluded. Still fielding at pull time (config end 25 Sep 2026).",
                  loc="location"))
    out.append(dict(id="KE-2026-09", excluded=True,
                    private=dict(priv("never_ran"),
                                 reason="ad sets existed 1-14 Sep 2026 but Insights returned null for every ad set (no delivery); "
                                        "no FACEBOOK_ADOPT report; last survey response 5 Aug 2026 (tests)"),
                    criteria=dict(rec="KE-2026-09", country="KE", round="excluded",
                                  notes="Configured (6 ad sets over 263 radius areas of 5 km, 1-15 Sep 2026) but no ads were "
                                        "delivered: every ad set reports no spend and no survey responses arrived. Never ran.")))
    return out
