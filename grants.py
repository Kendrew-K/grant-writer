"""Find music and orchestra grants and track every application in one CSV.

Usage:
  python grants.py scrape                 # pull open arts/music grants from grants.gov
  python grants.py add --funder F --title T --url U [--deadline MM/DD/YYYY]
                       [--amount N] [--eligibility TEXT] [--notes TEXT]
  python grants.py top [-n 10]            # open grants worth working, best first
  python grants.py status                 # every tracked grant grouped by status
  python grants.py mark <id> <status> [--note TEXT]

grants.gov is the only source with a free, keyless API. Private foundations,
regional and state arts agencies have none, so the agent sweeps the funders in
sources.md by hand and records each open call with `add`.
"""
import argparse
import csv
import datetime
import html
import json
import os
import pathlib
import re
import sys
import urllib.request

TRACKER_PATH = os.environ.get("GRANTS_TRACKER", "grants.csv")
FIELDS = ["id", "funder", "title", "url", "deadline", "amount", "eligibility",
          "relevance", "status", "note", "updated"]

# new: found, not started. drafting: answers being written.
# needs-info: blocked on a question only the user can answer.
# ready-for-review: portal filled, waiting for the user's explicit "submit".
# submitted / skipped: final.
STATUSES = ["new", "drafting", "needs-info", "ready-for-review", "submitted", "skipped"]
OPEN_STATUSES = ("new", "drafting", "needs-info")

# A grant counts as music-relevant when its text names at least one of these.
# Each is matched as a whole word, so "band" does not hit "broadband". Generic
# words like "concert", "commission", "recording" or "instrument" are left out
# on purpose: on 2026-09-25 they pulled in a tuna research program and an NIH
# trial, because federal notices use them in non-musical senses.
MUSIC_TERMS = [
    "music", "musical", "musician", "musicians", "orchestra", "orchestras",
    "orchestral", "symphony", "symphonic", "philharmonic", "chamber music",
    "composer", "composers", "conductor", "opera", "choir", "choral", "chorus",
    "jazz", "music education", "youth orchestra",
]

# U.S. embassy programs (agency codes like DOS-EGY, DOS-TUN) fund applicants in
# that country, so a U.S. orchestra or musician cannot use them. DOS-ECA is the
# State Department's cultural exchange bureau and does fund U.S. applicants.
def is_embassy_program(agency_code: str) -> bool:
    return agency_code.startswith("DOS-") and agency_code != "DOS-ECA"


def deadline_of(hit: dict, detail: dict) -> str:
    """Posted grants carry closeDate. Forecasts only carry an estimated due date,
    which is what exposes a years-old forecast nobody ever posted."""
    if hit.get("closeDate"):
        return hit["closeDate"]
    est = (detail.get("forecast") or {}).get("estApplicationResponseDateStr", "")
    return f"{est[5:7]}/{est[8:10]}/{est[:4]}" if len(est) >= 10 else ""

# A single mention is noise in federal notices: NASA's MUREP program is
# abbreviated "MUSIC", and NIH trials list music among many interventions.
# Two distinct terms is where real music grants start (checked 2026-09-25).
MIN_RELEVANCE = 2

API = "https://api.grants.gov/v1/api/"
# "AR" is grants.gov's Arts funding category. The keyword searches catch music
# grants filed under Education or Humanities instead.
SEARCHES = [{"fundingCategories": "AR"}] + [
    {"keyword": k} for k in ("music", "orchestra", "symphony", "musician",
                             "performing arts", "composer", "choral")
]


def post(endpoint: str, payload: dict) -> dict:
    req = urllib.request.Request(
        API + endpoint, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]


def relevance(text: str) -> int:
    """How many distinct music terms the text names. 0 means not a music grant."""
    lowered = text.lower()
    return sum(1 for t in MUSIC_TERMS if re.search(r"\b" + re.escape(t) + r"\b", lowered))


def parse_deadline(value: str) -> datetime.date | None:
    """grants.gov writes MM/DD/YYYY. Blank means rolling or not yet announced."""
    try:
        return datetime.datetime.strptime(value.strip(), "%m/%d/%Y").date()
    except ValueError:
        return None


def is_open(row: dict, today: datetime.date | None = None) -> bool:
    due = parse_deadline(row["deadline"])
    return due is None or due >= (today or datetime.date.today())


def strip_html(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text or ""))).strip()


def read_tracker(path=TRACKER_PATH) -> dict[str, dict]:
    path = pathlib.Path(path)
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def write_tracker(rows: dict[str, dict], path=TRACKER_PATH) -> None:
    with pathlib.Path(path).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows.values())


def merge(rows: dict[str, dict], found: dict) -> None:
    """Insert a new grant, or refresh the facts of a known one.

    Status and note are the user's work, so a rescrape never overwrites them.
    """
    if found["id"] in rows:
        for k in ("funder", "title", "url", "deadline", "amount", "eligibility", "relevance"):
            rows[found["id"]][k] = found[k]
    else:
        rows[found["id"]] = {**found, "status": "new", "note": "",
                             "updated": datetime.date.today().isoformat()}


def scrape_grants_gov(fetch=post, today: datetime.date | None = None) -> list[dict]:
    hits = {}
    for search in SEARCHES:
        data = fetch("search2", {**search, "oppStatuses": "forecasted|posted", "rows": 100})
        for h in data.get("oppHits", []):
            hits[h["id"]] = h
    found = []
    for opp_id, h in hits.items():
        # Both checks run before fetchOpportunity to save one request per dead grant.
        if is_embassy_program(h.get("agencyCode", "")) or not is_open({"deadline": h.get("closeDate", "")}, today):
            continue
        detail = fetch("fetchOpportunity", {"opportunityId": int(opp_id)})
        deadline = deadline_of(h, detail)
        if not is_open({"deadline": deadline}, today):
            continue
        # Posted opportunities carry "synopsis", forecasted ones "forecast".
        s = detail.get("synopsis") or detail.get("forecast") or {}
        text = " ".join([h["title"], strip_html(s.get("synopsisDesc", "")),
                         strip_html(s.get("forecastDesc", ""))])
        score = relevance(text)
        if score < MIN_RELEVANCE:
            continue
        elig = "; ".join(t.get("description", "") for t in s.get("applicantTypes", []) or [])
        found.append({
            "id": f"gg-{opp_id}", "funder": h.get("agency", ""), "title": h["title"],
            "url": f"https://www.grants.gov/search-results-detail/{opp_id}",
            "deadline": deadline,
            "amount": s.get("awardCeiling", "") or "",
            "eligibility": (elig + " " + strip_html(s.get("applicantEligibilityDesc", ""))).strip()[:300],
            "relevance": str(score),
        })
    return found


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def top(rows: dict[str, dict], n: int, today: datetime.date | None = None) -> list[dict]:
    """Open, unfinished grants: most music-relevant first, then soonest deadline."""
    live = [r for r in rows.values() if r["status"] in OPEN_STATUSES and is_open(r, today)]
    far = datetime.date.max
    live.sort(key=lambda r: (-int(r["relevance"] or 0), parse_deadline(r["deadline"]) or far))
    return live[:n]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scrape")
    a = sub.add_parser("add")
    for name in ("funder", "title", "url"):
        a.add_argument("--" + name, required=True)
    for name in ("deadline", "amount", "eligibility", "notes"):
        a.add_argument("--" + name, default="")
    t = sub.add_parser("top")
    t.add_argument("-n", type=int, default=10)
    sub.add_parser("status")
    m = sub.add_parser("mark")
    m.add_argument("id")
    m.add_argument("status", choices=STATUSES)
    m.add_argument("--note", default=None)
    args = p.parse_args(argv)

    rows = read_tracker()
    if args.cmd == "scrape":
        found = scrape_grants_gov()
        for g in found:
            merge(rows, g)
        write_tracker(rows)
        print(f"{len(found)} open music-relevant grants from grants.gov; {len(rows)} tracked in {TRACKER_PATH}")
    elif args.cmd == "add":
        if args.deadline and not parse_deadline(args.deadline):
            sys.exit("--deadline must be MM/DD/YYYY (leave it out for rolling deadlines)")
        # Added grants come from the curated music funders in sources.md, so
        # they count as relevant even when the title names no music term.
        text = f"{args.funder} {args.title} {args.notes}"
        merge(rows, {"id": "m-" + slug(f"{args.funder} {args.title}"), "funder": args.funder,
                     "title": args.title, "url": args.url, "deadline": args.deadline,
                     "amount": args.amount, "eligibility": args.eligibility,
                     "relevance": str(max(relevance(text), 1))})
        write_tracker(rows)
        print("Tracked m-" + slug(f"{args.funder} {args.title}"))
    elif args.cmd == "top":
        for r in top(rows, args.n):
            print(f"{r['id']:<28} due {r['deadline'] or 'rolling':<10} rel {r['relevance']:<2} "
                  f"${r['amount'] or '?':<9} {r['funder'][:28]} | {r['title'][:70]}")
    elif args.cmd == "status":
        for s in STATUSES:
            group = [r for r in rows.values() if r["status"] == s]
            if group:
                print(f"\n{s} ({len(group)})")
                for r in group:
                    print(f"  {r['id']:<28} {r['deadline'] or 'rolling':<10} {r['title'][:60]}"
                          + (f"  [{r['note']}]" if r["note"] else ""))
    elif args.cmd == "mark":
        if args.id not in rows:
            sys.exit(f"No grant with id {args.id}. Run `python grants.py status` to list ids.")
        rows[args.id]["status"] = args.status
        if args.note is not None:
            rows[args.id]["note"] = args.note
        rows[args.id]["updated"] = datetime.date.today().isoformat()
        write_tracker(rows)
        print(f"{args.id} -> {args.status}")


if __name__ == "__main__":
    main()
