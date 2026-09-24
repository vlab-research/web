#!/usr/bin/env python3
"""Merge every country group's cells into one table, and derive the buckets.

    python3 merge_cells.py            # validate, merge, bucket; exits 1 on any contract breach

Reads  scripts/data/cells/<G>.{cells,criteria,places}.json   (notes/cells-schema.md)
       scripts/pilot-maps/private/*.map.json                  (slugs, gitignored: used only for the leak check)
Writes scripts/data/cells.json                 every cell, with its place slice and person buckets
       scripts/data/recruitment-criteria.json  every recruitment record (excluded ones included)
       scripts/data/places.json                every place's geometry
       scripts/data/buckets.json               the bucket definitions and the pooled figures per bucket

The bucket rules are here, in one place, so that a change to a rule is a change to this file.
They are proposals for review (notes/ws-bucketing.md step 2), not settled definitions.
"""
import glob, json, os, re, statistics, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
CELLS = os.path.join(DATA, "cells")
PRIV = os.path.join(HERE, "private")

ERR = []


def err(msg):
    ERR.append(msg)


# ------------------------------------------------------------------ load
cells, crit, places = [], [], {}
for f in sorted(glob.glob(os.path.join(CELLS, "*.cells.json"))):
    g = os.path.basename(f).split(".")[0]
    c = json.load(open(f))
    k = json.load(open(os.path.join(CELLS, g + ".criteria.json")))
    p = json.load(open(os.path.join(CELLS, g + ".places.json")))
    for x in c:
        x["group"] = g
    cells += c
    crit += k
    for key, v in p.items():
        if key in places and places[key] != v:
            err(f"place {key} defined differently by two groups")
        places[key] = v

REC = {}
for r in crit:
    if r["rec"] in REC:
        err(f"recruitment id {r['rec']} appears twice")
    REC[r["rec"]] = r

# ------------------------------------------------------------------ contract checks
REQ = ["rec", "cell", "country", "place", "ads", "first", "last", "spend_days", "spend_usd", "started", "qualified"]
seen = set()
for x in cells:
    for k in REQ:
        if k not in x:
            err(f"{x.get('cell')}: missing {k}")
    if x["cell"] in seen:
        err(f"duplicate cell {x['cell']}")
    seen.add(x["cell"])
    if x["place"] not in places:
        err(f"{x['cell']}: place {x['place']} not in places.json")
    if x["rec"] not in REC:
        err(f"{x['cell']}: recruitment {x['rec']} has no criteria record")
    elif REC[x["rec"]].get("round") == "excluded":
        err(f"{x['cell']}: recruitment {x['rec']} is marked excluded but has cells")
    if x["qualified"] > x["started"]:
        err(f"{x['cell']}: qualified {x['qualified']} > started {x['started']}")
    if x["spend_usd"] < 0 or x["started"] < 0:
        err(f"{x['cell']}: negative measure")

# no slug, UUID, or topic word in any tracked output
slugs = set()


def _slugs(o, under=False):
    """Every string held under a slug-like key in the private maps (their shapes differ by group)."""
    if isinstance(o, dict):
        for k, v in o.items():
            _slugs(v, under or k in ("slug", "slugs", "studies", "study_slugs", "study"))
    elif isinstance(o, list):
        for v in o:
            _slugs(v, under)
    elif under and isinstance(o, str) and not UUID.fullmatch(o):
        slugs.add(o)


UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
for f in glob.glob(os.path.join(PRIV, "*.json")):
    _slugs(json.load(open(f)))
slugs = {s for s in slugs if len(s) >= 4 and re.search(r"[a-z]", s)}
print(f"leak check: {len(slugs)} study names from the private maps")
# the denylist names clients and topics, so it lives in the gitignored private folder
_DENY = [w.strip() for w in open(os.path.join(PRIV, "denylist.txt")) if w.strip() and not w.startswith("#")]
TOPIC = re.compile(r"\b(" + "|".join(_DENY) + r")\b", re.I)
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
for f in glob.glob(os.path.join(CELLS, "*.json")):
    txt = open(f).read()
    for s in slugs:
        if f'"{s}"' in txt or f" {s} " in txt:
            err(f"{os.path.basename(f)}: study slug {s!r}")
    if UUID.search(txt):
        err(f"{os.path.basename(f)}: a UUID")
    for m in set(TOPIC.findall(txt)):
        if not m.lower().startswith("behaviour"):
            err(f"{os.path.basename(f)}: topic or programme word {m!r}")


# ------------------------------------------------------------------ buckets
def place_slice(p):
    t = places[p]["type"]
    return {"country": "whole country", "country_minus": "whole country", "region": "whole regions",
            "radius_set": "radius areas", "city_radius": "radius areas",
            "radius_outside": "outside radius areas",
            # counties, a state minus counties, postcode sets: smaller than a region, not a radius
            "subregion_set": "smaller areas", "region_minus": "smaller areas", "zip_set": "smaller areas",
            "location_cluster": "smaller areas"}.get(t, t)


def ads_age(a):
    lo, hi = a.get("age_min") or 18, a.get("age_max") or 65
    if hi <= 35:
        return "ads to under-36s"
    if lo >= 25:
        return "ads to 25 and over"
    return "ads to all adult ages"


CHILD_BANDS = [(0, 6, "young children (under 6)"), (6, 12, "children aged 6–11"), (9, 18, "adolescents (9–17)")]


def child_band(tag):
    a, b = (int(v) for v in tag.split(":")[-1].split("-"))
    for lo, hi, lab in CHILD_BANDS:
        if a >= lo and b <= hi:
            return lab
    return f"children aged {a}–{b}"


def who_bucket(r, override=None):
    """The qualifying slice: who a recruitment counted as qualified, from its screening tags.
    First match wins, most specific first."""
    tags = list(r.get("screen") or [])
    for o in override or []:  # a cell's tag replaces the recruitment's tag of the same kind, and adds otherwise
        kind = o.split(":")[0]
        tags = [t for t in tags if t.split(":")[0] != kind] + [o]
    ads = r.get("ads") or {}
    if any(t.startswith("behaviour:") for t in tags):
        return "people with a specific behaviour"
    if any(t.startswith("occupation:") for t in tags):
        return "people in a specific occupation"
    if "pregnant_or_recent_birth" in tags:
        return "pregnant or recently gave birth"
    cg = [t for t in tags if t.startswith("caregiver:child_age:")]
    if cg:
        girls = "caregiver:child_gender:girl" in tags
        return "caregivers of " + ("girls: " if girls else "") + child_band(cg[0])
    if "parent_any" in tags:
        return "parents and caregivers"
    ages = [t for t in tags if t.startswith("age:")]
    hi = int(ages[0].split("-")[-1]) if ages else (ads.get("age_max") or 65)
    women = "gender:women" in tags or ads.get("genders") in (["women"], "women")
    if women:
        return "young women (up to 35)" if hi <= 35 else "women"
    if hi <= 35:
        return "young adults (up to 35)"
    return "any adult"


def length_band(m):
    if m is None or m > 120:  # over two hours is an external survey's sync time, not a survey length
        return "unknown"
    return "under 10 minutes" if m < 10 else "10–20 minutes" if m <= 20 else "over 20 minutes"


def who_comparable(r):
    """Can this recruitment's share-who-qualify be compared with others'? Not when "qualified" means
    coming back for a later wave, when almost nobody could reach the qualifying question (a routing
    quirk), or when nearly everyone qualified because the screen happened before the first message
    or outside our survey. Such recruitments still count for place (cost per start)."""
    st, q = r.get("started") or 0, r.get("qualified") or 0
    if "completed_follow_up" in (r.get("screen") or []):
        return False, "qualified means returning for a later wave"
    if st >= 50 and q / st < 0.03:
        return False, "under 3% qualified: the qualifying question was not on everyone's path"
    if st >= 50 and q / st > 0.97:
        return False, "over 97% qualified: screened before the first message or outside the survey"
    return True, None


# ------------------------------------------------------------------ audience tier
# general: broad ads, any adult or an age band or one gender, screened only on who-you-are basics.
# common: a population researchers often seek and we have recruited repeatedly (parents by child's age).
# specialised: anything narrower; it never sets a headline and is described in one general sentence.
BASIC = ("age:", "lives_in:", "consent", "language:", "gave_phone", "has_phone", "has_whatsapp",
         "attention_check", "gender:", "education:", "quota_group:education")
OVERRIDES = {k: v for k, v in json.load(open(os.path.join(DATA, "tier-overrides.json"))).items() if not k.startswith("_")}
REC_CELLS = collections.defaultdict(list)
for x in cells:
    REC_CELLS[x["rec"]].append(x)


def audience_tier(r):
    if r["rec"] in OVERRIDES:
        return OVERRIDES[r["rec"]]["tier"], OVERRIDES[r["rec"]]["reason"]
    cs = REC_CELLS.get(r["rec"], [])
    sp = sum(x["spend_usd"] for x in cs) or 1
    if sum(x["spend_usd"] for x in cs if x["ads"].get("interests")) / sp > 0.25:
        return "specialised", "Meta interest or behaviour targeting chose who saw the ads"
    tags = r.get("screen") or []
    narrow = [t for t in tags if not t.startswith(BASIC) and not t.startswith(("caregiver:", "parent_any"))]
    if narrow:
        return "specialised", "screened on " + ", ".join(narrow)
    if any(t.startswith(("caregiver:", "parent_any")) for t in tags):
        return "common", "parents or caregivers, by the child's age"
    return "general", None


for x in cells:
    r = REC.get(x["rec"], {})
    x["slice_place"] = place_slice(x["place"])
    x["tier"] = audience_tier(r)[0] if r else None
    x["slice_ads_gender"] = (x["ads"].get("genders") or "all")
    x["slice_ads_age"] = ads_age(x["ads"])
    x["slice_who"] = who_bucket(r, x.get("person_override")) if who_comparable(r)[0] else "not comparable"
    x["slice_length"] = length_band(r.get("median_minutes_to_qualify"))  # the recruitment's survey, not the cell's

for r in crit:
    if r.get("round") != "excluded":
        r["who_comparable"], r["who_not_comparable_because"] = who_comparable(r)
        r["bucket_who"] = who_bucket(r)
        r["tier"], r["tier_reason"] = audience_tier(r)
        r["bucket_length"] = length_band(r.get("median_minutes_to_qualify"))


def pool(rows):
    sp = sum(x["spend_usd"] for x in rows)
    st = sum(x["started"] for x in rows)
    q = sum(x["qualified"] for x in rows)
    per_rec = collections.defaultdict(lambda: [0.0, 0, 0])
    for x in rows:
        a = per_rec[x["rec"]]
        a[0] += x["spend_usd"]; a[1] += x["started"]; a[2] += x["qualified"]
    recs = {k: v for k, v in per_rec.items() if v[1] >= 50}
    share = [v[2] / v[1] for v in recs.values() if v[1]]
    cps = [v[0] / v[1] for v in recs.values() if v[1]]
    cpq = [v[0] / v[2] for v in recs.values() if v[2]]
    rng = lambda xs: [round(min(xs), 2), round(max(xs), 2)] if xs else None
    return dict(spend=round(sp, 2), started=st, qualified=q,
                cost_per_start=round(sp / st, 2) if st else None,
                cost_per_qualified=round(sp / q, 2) if q else None,
                share_qualified=round(q / st, 3) if st else None,
                recruitments=len(per_rec), countries=sorted({x["country"] for x in rows}),
                range_cost_per_start=rng(cps), range_cost_per_qualified=rng(cpq),
                range_share_qualified=[round(min(share), 3), round(max(share), 3)] if share else None,
                median_share_qualified=round(statistics.median(share), 3) if share else None)


buckets = {}
for dim in ("slice_place", "slice_ads_gender", "slice_ads_age", "slice_who", "slice_length"):
    groups = collections.defaultdict(list)
    for x in cells:
        groups[x[dim]].append(x)
    buckets[dim] = {k: pool(v) for k, v in sorted(groups.items())}

# ------------------------------------------------------------------ write
if ERR:
    print(f"{len(ERR)} contract problem(s):")
    for e in ERR:
        print("  -", e)
    sys.exit(1)

cells.sort(key=lambda x: (x["country"], x["rec"], x["cell"]))
json.dump(cells, open(os.path.join(DATA, "cells.json"), "w"), indent=1, ensure_ascii=False)
json.dump(sorted(crit, key=lambda r: (r["country"], r["rec"])), open(os.path.join(DATA, "recruitment-criteria.json"), "w"),
          indent=1, ensure_ascii=False)
json.dump(dict(sorted(places.items())), open(os.path.join(DATA, "places.json"), "w"), indent=1, ensure_ascii=False)
json.dump(dict(_meta=dict(status="PROPOSED buckets for review; not on the site",
                          rules="scripts/pilot-maps/merge_cells.py: place_slice, ads_age, who_bucket, length_band",
                          pooling="spend and people summed; ranges are across recruitments with at least 50 starts in the bucket"),
               **buckets), open(os.path.join(DATA, "buckets.json"), "w"), indent=1, ensure_ascii=False)
kept = [r for r in crit if r.get("round") != "excluded"]
print(f"{len(cells)} cells · {len(kept)} recruitments kept, {len(crit) - len(kept)} excluded · "
      f"{len(places)} places · {len({x['country'] for x in cells})} countries · "
      f"${sum(x['spend_usd'] for x in cells):,.0f} · {sum(x['started'] for x in cells):,} starts")
for k, v in buckets["slice_who"].items():
    print(f"  {k:40s} recs {v['recruitments']:3d}  starts {v['started']:7,}  share {v['share_qualified']}  "
          f"$/start {v['cost_per_start']}  $/qual {v['cost_per_qualified']}")
