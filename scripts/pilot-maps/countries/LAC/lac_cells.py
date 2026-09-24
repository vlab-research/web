"""Bolivia, Argentina and Honduras: the LAC part of the KE-LAC cell table. Run ./cells.py.

One design in three countries, September 2026: gender x (inside a set of radius areas around
cities and towns / the rest of the country), one survey per country. Each country had two ad
runs into that survey:
  a  5-9 Sep: link-click ads to a page offering Messenger or WhatsApp (4 ad sets). Pilot.
  b  from 9 Sep: conversation ads opening Messenger (4 ad sets, one campaign)
  c  from 9 Sep: conversation ads opening WhatsApp (4 ad sets, one campaign)
b and c ran as separate arms with their own budget and sample cap, so each is a recruitment
with one channel. People are assigned to b or c by the platform they wrote from. Each person is
counted once across a, b and c.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cells as E

RAW = os.path.join(HERE, "raw")
# Study ids, survey names, form codes and the qualifying question ref live in the gitignored
# scripts/pilot-maps/private/KE-LAC.inputs.json: they can name a client or a topic.
CFG = E.inputs()["LAC"]
STUDIES = {v[0]: k for k, v in CFG["studies"].items()}          # uuid -> neutral key
C = {  # country: (incentive promised in the ad message, noun for the radius areas, name)
    "BO": (dict(amount=11, currency="BOB", form="airtime"), "cities", "Bolivia"),
    "AR": (dict(amount=3000, currency="ARS", form="airtime"), "towns", "Argentina"),
    "HN": (dict(amount=90, currency="HNL", form="airtime"), "towns", "Honduras"),
}
QREF = CFG["qual_ref"]
QUAL_PATHS = [(f"{cc}-2026-09{x}", QREF, "2026-09-04", "2026-10-15") for cc in C for x in "abc"]
# Bolivia's two 'Urban' ad sets targeted the country MINUS the 13 radius areas from 5 Sep 18:07 UTC to
# 7 Sep 15:56 UTC (strata config history); their spend tracks the 'Rural' ad sets day for day until 7 Sep
# and drops on 8 Sep. So their 5-7 Sep spend and people belong to the outside place.
BO_URBAN_WRONG_UNTIL = "2026-09-07"


def fetch(salt):
    E.fetch(RAW, STUDIES, ["Gender", "Location"], [], CFG["surveys"], QUAL_PATHS, salt, platforms=CFG["platform_forms"])


def sid(key):
    return CFG["studies"][key][0][:8]


PLACE = {}


def places(R):
    out, checks = {}, {}
    for cc, (_inc, noun, name) in C.items():
        pilot, ch = f"{cc}_a", f"{cc}_bc"
        st = R.latest(sid(ch), "strata")
        urban = next(s for s in st if s["id"].endswith("Urban"))["facebook_targeting"]["geo_locations"]["custom_locations"]
        rural = next(s for s in st if s["id"].endswith("Rural"))["facebook_targeting"]
        assert rural["excluded_geo_locations"]["custom_locations"] == urban and rural["geo_locations"]["countries"] == [cc]
        # the pilot's final strata use the same pins
        pst = R.latest(sid(pilot), "strata")
        assert next(s for s in pst if s["id"].endswith("Urban"))["facebook_targeting"]["geo_locations"]["custom_locations"] == urban
        P, chk = E.pin_set(cc, urban)
        kin = f"{cc}:radius:{len(P)}-{noun}-{E.radius_label(P)}"
        kout = kin.replace(":radius:", ":outside:")
        out[kin] = dict(country=cc, type="radius_set",
                        label=f"Inside {len(P)} radius areas ({E.radius_label(P).replace('km', ' km').replace('-', '–')})", pins=P)
        out[kout] = dict(country=cc, type="radius_outside", label=f"{name} outside the {len(P)} radius areas", complement_of=kin)
        PLACE[cc] = dict(inside=kin, outside=kout)
        unnamed = [i for i, c in enumerate(chk) if c is None]
        checks[kin] = dict(pins=len(P), named_within_5km=len(P) - len(unnamed), unnamed_pins=[P[i] for i in unnamed],
                           names=[c and c["name"] for c in chk])
    return out, checks


def recruitments(R):
    out = []
    for cc, (inc, noun, name) in C.items():
        pilot, ch = f"{cc}_a", f"{cc}_bc"
        seen = set()
        sp, sc = sid(pilot), sid(ch)
        npins = len(R.latest(sc, "strata")[1]["facebook_targeting"]["geo_locations"]["custom_locations"])
        base_screen = ["age:18-99", "consent"]
        who = "adults (18+ by birth year); reached the end of the questions, about {m} minutes in"
        rule = "answered the last question of the survey, before the payment form"

        def cellset(s, early_split=False):
            cells = {}
            for g in ("Women", "Men"):
                for loc in ("Urban", "Rural"):
                    st = R.stratum(s, f"Gender:{g},Location:{loc}")
                    side = "inside" if loc == "Urban" else "outside"
                    cells[f"{g}:{loc}"] = dict(place=PLACE[cc][side], side=side, ads=E.ads_of(st),
                                              flags=["pin_checked"] + E.ad_flags(st))
                    if early_split and loc == "Urban":
                        cells[f"{g}:Urban:early"] = dict(place=PLACE[cc]["outside"], side="outside", ads=E.ads_of(st),
                                                         flags=["pin_checked", "label_differs_from_geometry"] + E.ad_flags(st))
            return cells

        def key(strat, d, split):
            g, loc = strat.split(",")[0].split(":")[1], strat.split(",")[1].split(":")[1]
            k = f"{g}:{loc}"
            if split and loc == "Urban" and d <= BO_URBAN_WRONG_UNTIL:
                k += ":early"
            return k

        split = cc == "BO"
        ca = cellset(sp, split)
        out.append(dict(
            id=f"{cc}-2026-09a", country=cc, sids=[sp], labels=["Gender", "Location"], cells=ca,
            spend=lambda s, camp, strat, d, split=split: key(strat, d, split),
            person=lambda m, t0, u, s, split=split: key(f"Gender:{m['Gender']},Location:{m['Location']}", t0[:10], split)
            if {"Gender", "Location"} <= set(m) else None,
            qual=lambda v, k: QREF if QREF in v else None, register=seen.update,
            private=dict(studies=CFG["studies"][pilot]),
            criteria=dict(rec=f"{cc}-2026-09a", country=cc, round="pilot",
                          ads=dict(genders=["women", "men"], age_min=18, age_max=65, interests=False),
                          screen=base_screen, who_qualified=who, qualify_rule=rule,
                          channel="messenger", languages=["es"], incentive=inc,
                          notes=(f"Link-click ads to a page offering Messenger or WhatsApp; most people who started wrote on "
                                 f"Messenger. Gender x inside/outside {npins} radius areas around {noun}. Ages by Meta default "
                                 f"(18-65+). Few people reached the survey from these ads; a short first run."
                                 + (" The two 'inside' ad sets were configured with the outside geometry on 5-7 Sep; those days' "
                                    "spend and people are placed outside (flag label_differs_from_geometry)." if split else "")
                                 + " qualify_point counts every prompt answered, including 'OK' taps."))))
        for x, plat, camp_suffix in (("b", "messenger", "-Messenger"), ("c", "whatsapp", "-WhatsApp")):
            cx = cellset(sc)
            rid = f"{cc}-2026-09{x}"
            out.append(dict(
                id=rid, country=cc, sids=[sc], labels=["Gender", "Location"], cells=cx,
                spend=lambda s, camp, strat, d, suf=camp_suffix: key(strat, d, False) if camp.endswith(suf) else None,
                person=lambda m, t0, u, s, plat=plat: key(f"Gender:{m['Gender']},Location:{m['Location']}", t0[:10], False)
                if {"Gender", "Location"} <= set(m) and R.platform.get(u) == plat else None,
                qual=lambda v, k: QREF if QREF in v else None, siblings=seen, register=seen.update,
                private=dict(studies=CFG["studies"][ch], campaign_suffix=camp_suffix,
                             note="report lifetime_spent covers only the campaign current at report time"),
                criteria=dict(rec=rid, country=cc, round="cross-section",
                              ads=dict(genders=["women", "men"], age_min=18, age_max=65, interests=False),
                              screen=base_screen,
                              who_qualified=who, qualify_rule=rule, channel=plat, languages=["es"], incentive=inc,
                              notes=(f"Conversation ads opening {plat.capitalize()}, one arm of a two-channel run into the same survey "
                                     f"as {cc}-2026-09a (same {npins} radius areas and gender split). The arms ran on different days "
                                     f"(both 9-12 Sep; then one at a time). Still fielding at pull time (config end 10 Oct 2026). "
                                     f"People assigned by the platform they wrote from; each person counted once across a, b, c."
                                     + (" On WhatsApp, anyone arriving without an ad referral is asked to come back through an ad."
                                        if plat == "whatsapp" else "")
                                     + " qualify_point counts every prompt answered, including 'OK' taps."))))
    return out
