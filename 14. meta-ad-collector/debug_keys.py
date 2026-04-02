from browser_collector import BrowserAdCollector
import json

c = BrowserAdCollector()

# Patch sementara untuk lihat raw data
from playwright.sync_api import sync_playwright
import time

intercepted_raw = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        locale="en-US"
    )
    page = context.new_page()

    def handle_response(response):
        url = response.url
        if any(x in url for x in ["ads/library/async", "graphql", "api/graphql"]):
            try:
                if response.status == 200:
                    body = response.text()
                    for line in body.splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            parsed = json.loads(line)
                            c._extract_ads(parsed, intercepted_raw)
                        except Exception:
                            pass
            except Exception:
                pass

    page.on("response", handle_response)
    page.goto(
        "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ID&q=Nike&search_type=keyword_unordered",
        wait_until="domcontentloaded", timeout=60000
    )
    time.sleep(5)
    for i in range(5):
        page.evaluate("window.scrollBy(0, 800)")
        time.sleep(1.5)
    browser.close()

if intercepted_raw:
    print("=== RAW KEYS dari ad pertama ===")
    first = intercepted_raw[0]
    print(json.dumps(list(first.keys()), indent=2))
    print("\n=== FULL DATA ad pertama ===")
    print(json.dumps(first, indent=2, default=str))
    print("\n=== SPEND RAW ===")
    print(json.dumps(intercepted_raw[0].get("spend"), indent=2, default=str))

    print("\n=== IMPRESSIONS RAW ===")  
    print(json.dumps(intercepted_raw[0].get("impressions_with_index"), indent=2, default=str))

    print("\n=== CURRENCY ===")
    print(intercepted_raw[0].get("currency"))

    print("\n=== SNAPSHOT keys ===")
    snap = intercepted_raw[0].get("snapshot", {})
    print(list(snap.keys()) if isinstance(snap, dict) else snap)
else:
    print("Tidak ada data ter-intercept")