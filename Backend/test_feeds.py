"""
Quick smoke-test: iterate over every feed URL in the new Indian source dicts
and print whether it returns ≥1 entry or is failing.
No DB writes, no model loads.

Usage:
    cd backend
    source venv/bin/activate
    python test_feeds.py
"""
import feedparser
import sys

# Import the feed dicts from scraper without loading the full app
sys.path.insert(0, ".")
from scraper import NATIONAL_EXTRA_FEEDS, INDIAN_STATE_FEEDS, INDIAN_CITY_FEEDS

PASS = "\033[32m✓\033[0m"
FAIL = "\033[31m✗\033[0m"

results = {"ok": 0, "fail": 0}

def check(label: str, url: str):
    try:
        feed = feedparser.parse(url)
        n = len(feed.entries)
        if n > 0:
            print(f"  {PASS} {label:40s}  ({n} entries)  {url[:60]}")
            results["ok"] += 1
        else:
            print(f"  {FAIL} {label:40s}  (0 entries – bozo={feed.bozo})  {url[:60]}")
            results["fail"] += 1
    except Exception as e:
        print(f"  {FAIL} {label:40s}  ERROR: {e}")
        results["fail"] += 1

print("\n=== Tier 4: National Extra Feeds ===")
for url in NATIONAL_EXTRA_FEEDS:
    check("National", url)

print("\n=== Tier 3: State Feeds ===")
for state, urls in INDIAN_STATE_FEEDS.items():
    for url in urls:
        check(state, url)

print("\n=== Tier 1+2: City Feeds ===")
for city, urls in INDIAN_CITY_FEEDS.items():
    for url in urls:
        check(city, url)

total = results["ok"] + results["fail"]
print(f"\n{'─'*60}")
print(f"Results: {results['ok']}/{total} feeds OK, {results['fail']} failing\n")
