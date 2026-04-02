# debug_apify.py
from apify_client import ApifyClient
from dotenv import load_dotenv
import os, json
from urllib.parse import quote_plus

load_dotenv()
client = ApifyClient(os.getenv("APIFY_TOKEN"))

term = "Nike Indonesia"
encoded = quote_plus(term)
url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ID&q={encoded}&search_type=keyword_unordered&media_type=all"

run = client.actor("curious_coder/facebook-ads-library-scraper").call(
    run_input={
        "urls": [{"url": url}],
        "limitPerSource": 3,
        "scrapeAdDetails": True,
        "scrapePageAds.activeStatus": "all",
        "scrapePageAds.countryCode": "ID",
    },
    timeout_secs=120,
)

items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
print(f"Total items: {len(items)}")
if items:
    print("\n=== KEYS ===")
    print(json.dumps(list(items[0].keys()), indent=2))
    print("\n=== FULL ITEM 1 ===")
    print(json.dumps(items[0], indent=2, default=str))