"""Google Trends data in Python: interest over time, interest by region, and daily trending searches.

Gets the data through the Apify Actor data_xplorer/google-trends-fast-scraper, so there is no
Google rate limit (HTTP 429) to handle on your side and no unofficial library to keep patched.

Examples:
    python trends.py interest chatgpt "climate change" --geo US --timeframe "today 3-m"
    python trends.py interest bitcoin --geo FR --regions
    python trends.py trending --country US --hours 24 --watch "bitcoin,taylor swift"
"""
import argparse
import csv
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from apify_client import ApifyClient

ACTOR = "data_xplorer/google-trends-fast-scraper"
TIMEFRAMES = ["now 1-h", "now 4-h", "now 1-d", "now 7-d", "today 1-m", "today 3-m", "today 12-m", "today 5-y"]


def run_actor(run_input):
    client = ApifyClient(os.environ["APIFY_TOKEN"])
    run = client.actor(ACTOR).call(run_input=run_input)
    return list(client.dataset(run["defaultDatasetId"]).iterate_items())


def write_csv(path, header, rows):
    with Path(path).open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"{len(rows)} rows written to {path}")


def notify(text):
    """Telegram message if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID are set, console otherwise."""
    token, chat = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        print(text)
        return
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                  json={"chat_id": chat, "text": text}, timeout=30)


def interest(args):
    """Interest over time (0-100) for each keyword, plus interest by region with --regions."""
    timeline, regions = [], []
    for keyword in args.keywords:
        items = run_actor({
            "mode": "keyword",
            "keyword": keyword,
            "predefinedTimeframe": args.timeframe,
            "geo": args.geo,
            "fetchRegionalData": args.regions,
        })
        if not items:
            print(f"{keyword}: no data")
            continue
        item = items[0]
        if item.get("error"):
            # e.g. not enough Google searches for this keyword, period and country
            print(f"{keyword}: {item['error']}")
            continue
        series = item["timeline_data"].get(keyword, {})
        for day, value in series.items():
            timeline.append([day, keyword, value])
        for region in item.get("region_data") or []:
            regions.append([keyword, region["rank"], region["region"], region["value"]])
        if series:
            peak_day, peak = max(series.items(), key=lambda kv: kv[1])
            last_day, last = list(series.items())[-1]
            print(f"{keyword}: peak {peak} on {peak_day}, latest {last} on {last_day} "
                  f"({item['data_granularity']} data)")

    write_csv(args.out, ["date", "keyword", "value"], timeline)
    if args.regions:
        write_csv("interest_by_region.csv", ["keyword", "rank", "region", "value"], regions)


def trending(args):
    """Today's trending searches for a country. Alerts on new terms and on watched words."""
    items = run_actor({
        "mode": "trending",
        "trendingSearchesCountry": args.country,
        "trendingSearchesTimeframe": str(args.hours),
        "trendingSearchesMaxItems": args.max,
    })
    searches = items[0]["trending_searches"] if items else []
    history = Path(args.out)
    seen = set()
    if history.exists():
        with history.open() as fh:
            seen = {row["term"] for row in csv.DictReader(fh) if row["country"] == args.country}

    watch = [w.strip().lower() for w in args.watch.split(",") if w.strip()]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    new_file = not history.exists()
    with history.open("a", newline="") as fh:
        writer = csv.writer(fh)
        if new_file:
            writer.writerow(["checkedAt", "country", "rank", "term", "volume", "related"])
        for s in searches:
            related = s.get("related_terms") or []
            writer.writerow([now, args.country, s["rank"], s["term"], s.get("trend_volume", ""), "; ".join(related[:5])])
            print(f"{s['rank']:>3}. {s['term']} ({s.get('trend_volume', '?')})")

            text = " ".join([s["term"], *related]).lower()
            hits = [w for w in watch if re.search(rf"\b{re.escape(w)}\b", text)]
            if hits:
                notify(f"Google Trends {args.country}: '{s['term']}' is trending ({s.get('trend_volume', '?')}), "
                       f"matches {', '.join(hits)}")
            elif args.alert_new and seen and s["term"] not in seen:
                notify(f"New on Google Trends {args.country}: '{s['term']}' ({s.get('trend_volume', '?')})")


def main():
    parser = argparse.ArgumentParser(description="Google Trends data in Python, via Apify.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("interest", help="interest over time for one or more keywords")
    p.add_argument("keywords", nargs="+")
    p.add_argument("--geo", default="", help="country code (US, FR...), empty for worldwide")
    p.add_argument("--timeframe", default="today 12-m", choices=TIMEFRAMES)
    p.add_argument("--regions", action="store_true", help="also save interest by region")
    p.add_argument("--out", default="interest_over_time.csv")
    p.set_defaults(func=interest)

    p = sub.add_parser("trending", help="today's trending searches for a country")
    p.add_argument("--country", default="US")
    p.add_argument("--hours", type=int, default=24, choices=[4, 24, 48, 168])
    p.add_argument("--max", type=int, default=25, help="number of trending searches to keep")
    p.add_argument("--watch", default="", help="comma-separated words to get an alert for")
    p.add_argument("--alert-new", action="store_true", help="alert on every term not seen in earlier runs")
    p.add_argument("--out", default="trending_history.csv")
    p.set_defaults(func=trending)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
