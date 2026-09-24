"""Per-country figures for the embed programme (Iraq, Egypt, Saudi Arabia, Morocco, Jordan).
Reads raw/*.tsv pulled read-only from production (queries in sql/). Writes nothing by itself;
country_data() is imported by build.py, which writes the JSON files and maps."""
import csv, json, os
from collections import defaultdict, OrderedDict
csv.field_size_limit(10**9)
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

STUDIES = OrderedDict([
    ("IQ", dict(slug="embed-iraq", rule="phone_number", cities=["Baghdad", "Mosul", "Basra"])),
    ("EG", dict(slug="embed-egypt", rule="phone_number", cities=["Cairo", "Giza", "Alexandria"])),
    ("SA", dict(slug="embed-ksa", rule="pre_pay_info", cities=["Riyadh", "Jeddah", "Mecca"])),
    ("MA", dict(slug="embed-morocco", rule="phone_number", cities=["Casablanca", "Fez", "Marrakech"])),
    ("JO", dict(slug="embed-jordan", rule="phone_number", cities=["Amman", "Irbid", "Zarqa"])),
])


def part(sid, key):
    return dict(p.split(":", 1) for p in sid.split(","))[key]


def adopt(slug):
    r = next(csv.DictReader(open(os.path.join(RAW, f"adopt-{slug}.tsv")), delimiter="\t"))
    return r["created"], json.loads(r["details"])


def qualified(slug):
    out = {}
    for r in csv.DictReader(open(os.path.join(RAW, "qualified.tsv")), delimiter="\t"):
        if r["slug"] == slug:
            out[f"Gender:{r['g']},Age:{r['a']},City:{r['city']}"] = dict(
                started=int(r["started"]), started_in_window=int(r["started_in_window"]),
                qualified=int(r["qualified"]), qualified_any_time=int(r["qualified_any_time"]))
    return out


def insights(slug):
    tot = defaultdict(lambda: [0.0, 0.0, 0.0, set()])
    for r in csv.DictReader(open(os.path.join(RAW, "daily.tsv")), delimiter="\t"):
        if r["slug"] != slug:
            continue
        f = lambda x: float(x) if x not in ("NULL", "") else 0.0
        t = tot[part(r["strat"], "City")]
        t[0] += f(r["spend"]); t[1] += f(r["imp"]); t[2] += f(r["clicks"])
        if f(r["spend"]) > 0:
            t[3].add(r["d"])
    days = set().union(*[v[3] for v in tot.values()])
    return {k: dict(spend=round(v[0], 2), impressions=int(v[1]), unique_clicks=int(v[2])) for k, v in tot.items()}, sorted(days)


def people():
    return {r["cc"]: dict(unique_people=int(r["people"]), first=r["min"], last=r["max"])
            for r in csv.DictReader(open(os.path.join(RAW, "people.tsv")), delimiter="\t")}


def country_data(cc):
    s = STUDIES[cc]
    created, rep = adopt(s["slug"])
    q = qualified(s["slug"])
    ins, days = insights(s["slug"])
    strata = []
    for sid, v in rep.items():
        strata.append(OrderedDict(id=sid, lifetime_spent=round(v["lifetime_spent"], 2),
                                  report_current_participants=v["current_participants"],
                                  qualified=q[sid]["qualified"], started=q[sid]["started"],
                                  current_price_per_participant=v["current_price_per_participant"]))

    def pooled(key):
        acc = OrderedDict()
        for x in strata:
            k = part(x["id"], key)
            a = acc.setdefault(k, dict(spend=0.0, qualified=0, started=0, report_qualified=0))
            a["spend"] += x["lifetime_spent"]; a["qualified"] += x["qualified"]; a["started"] += x["started"]
            a["report_qualified"] += x["report_current_participants"]
        for a in acc.values():
            a["spend"] = round(a["spend"], 2)
            a["cost"] = round(a["spend"] / a["qualified"], 2)
            a["cost_per_started"] = round(a["spend"] / a["started"], 2)
            a["completion_pct"] = round(100 * a["qualified"] / a["started"], 1)
        return acc
    spend = round(sum(x["lifetime_spent"] for x in strata), 2)
    n = sum(x["qualified"] for x in strata)
    return dict(cc=cc, slug=s["slug"], rule=s["rule"], report_created=created, strata=strata,
                by_city=pooled("City"), by_gender=pooled("Gender"), by_age=pooled("Age"),
                spend=spend, qualified=n, cost=round(spend / n, 2),
                started=sum(x["started"] for x in strata),
                report_qualified=sum(x["report_current_participants"] for x in strata),
                insights_by_city=ins, ad_days=len(days), first_ad_day=days[0], last_ad_day=days[-1],
                insights_spend=round(sum(v["spend"] for v in ins.values()), 2),
                people=people()[cc])


if __name__ == "__main__":
    for cc in STUDIES:
        d = country_data(cc)
        print(f"\n== {cc} {d['slug']} spend {d['spend']} (insights {d['insights_spend']}) qualified {d['qualified']} "
              f"(report {d['report_qualified']}) cost {d['cost']} started {d['started']} days {d['ad_days']} "
              f"{d['first_ad_day']}..{d['last_ad_day']} people {d['people']}")
        for k in ("by_city", "by_gender", "by_age"):
            for g, a in d[k].items():
                print(f"   {k:9} {g:11} spend {a['spend']:9.2f} qual {a['qualified']:5} started {a['started']:5} "
                      f"cost {a['cost']:6.2f} /start {a['cost_per_started']:5.2f} compl {a['completion_pct']:5}%  report_q {a['report_qualified']}")
        for c, v in d["insights_by_city"].items():
            print("   insights", c, v)
