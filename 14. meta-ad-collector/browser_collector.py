from playwright.sync_api import sync_playwright
import time
import json
from datetime import datetime
from rich.console import Console
import config

console = Console()


class BrowserAdCollector:
    def __init__(self):
        self.base_url = "https://www.facebook.com/ads/library/"

    def collect_via_network_intercept(self, search_term, country="ID"):
        console.print(f"\n[yellow]Browser fallback: {search_term}[/yellow]")
        intercepted_data = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="en-US",
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
                                    self._extract_ads(parsed, intercepted_data)
                                except Exception:
                                    pass
                    except Exception:
                        pass

            page.on("response", handle_response)

            url = (
                f"https://www.facebook.com/ads/library/"
                f"?active_status=all&ad_type=all"
                f"&country={country}"
                f"&q={search_term}"
                f"&search_type=keyword_unordered"
                f"&media_type=all"
            )

            console.print(f"  Loading page...", end="")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                console.print("[green] OK[/green]")
            except Exception as e:
                console.print(f"[red] Error: {e}[/red]")
                browser.close()
                return []

            time.sleep(5)

            console.print("  Scrolling to load ads...")
            for i in range(8):
                try:
                    page.evaluate("window.scrollBy(0, 800)")
                    time.sleep(1.5)
                except Exception:
                    break

            time.sleep(3)
            browser.close()

        seen = set()
        unique = []
        for ad in intercepted_data:
            ad_id = str(ad.get("ad_archive_id") or ad.get("ad_id") or id(ad))
            if ad_id not in seen:
                seen.add(ad_id)
                unique.append(ad)

        normalized = [self._normalize(ad, search_term) for ad in unique]
        console.print(f"  [green]Intercepted {len(normalized)} ads[/green]")
        return normalized

    def _extract_ads(self, obj, result_list, depth=0):
        if depth > 8:
            return
        if isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict) and self._looks_like_ad(item):
                    result_list.append(item)
                else:
                    self._extract_ads(item, result_list, depth + 1)
        elif isinstance(obj, dict):
            for val in obj.values():
                self._extract_ads(val, result_list, depth + 1)

    def _looks_like_ad(self, obj):
        ad_keys = {"ad_archive_id", "page_name", "ad_delivery_start_time",
                   "snapshot", "spend", "impressions", "page_id", "start_date"}
        return bool(ad_keys.intersection(obj.keys()))

    def _normalize(self, ad, search_term):
        def safe_dict(val):
            return val if isinstance(val, dict) else {}

        def safe_list(val):
            return val if isinstance(val, list) else []

        def safe_str(val, default="N/A"):
            if val is None or val == "":
                return default
            return str(val)

        def ts_to_date(val):
            if not val:
                return "N/A"
            try:
                return datetime.fromtimestamp(int(val)).strftime("%Y-%m-%d")
            except Exception:
                return str(val)

        snapshot  = safe_dict(ad.get("snapshot"))
        platforms = safe_list(ad.get("publisher_platform"))

        raw_spend = ad.get("spend")
        spend = safe_dict(raw_spend)
        spend_lower = spend.get("lower_bound", "Not Disclosed" if raw_spend is None else "N/A")
        spend_upper = spend.get("upper_bound", "Not Disclosed" if raw_spend is None else "N/A")

        raw_imp = safe_dict(ad.get("impressions_with_index"))
        imp_text = raw_imp.get("impressions_text")
        imp_index = raw_imp.get("impressions_index", -1)
        if imp_text:
            imp_display = imp_text
        elif imp_index == -1:
            imp_display = "Not Disclosed"
        else:
            imp_display = str(imp_index)

        currency = safe_str(ad.get("currency"), "Not Disclosed")

        # Ad copy — coba semua sumber
        bodies = []
        for card in safe_list(snapshot.get("cards"))[:3]:
            if isinstance(card, dict):
                b = card.get("body", "") or card.get("title", "")
                if b:
                    bodies.append(str(b))
        if not bodies:
            raw_body = snapshot.get("body") or {}
            if isinstance(raw_body, dict):
                t = raw_body.get("text", "")
                if t:
                    bodies.append(t)
            elif isinstance(raw_body, str) and raw_body:
                bodies.append(raw_body)
        # Fallback ke title kalau body masih kosong
        if not any(b.strip() for b in bodies):
            t = snapshot.get("title", "")
            if t:
                bodies = [str(t)]

        ad_copy = " | ".join(filter(lambda x: x.strip(), bodies)) or "N/A"

        title       = safe_str(snapshot.get("title"))
        caption     = safe_str(snapshot.get("caption"))
        cta_text    = safe_str(snapshot.get("cta_text"))
        link_url    = safe_str(snapshot.get("link_url"))
        display_fmt = safe_str(snapshot.get("display_format"))
        page_likes  = snapshot.get("page_like_count", "N/A")

        return {
            "search_term":        search_term,
            "ad_id":              safe_str(ad.get("ad_archive_id") or ad.get("ad_id")),
            "page_name":          safe_str(ad.get("page_name")),
            "page_id":            safe_str(ad.get("page_id")),
            "status":             "ACTIVE" if ad.get("is_active") else "INACTIVE",
            "platforms":          ", ".join(platforms),
            "display_format":     display_fmt,
            "ad_title":           title,
            "ad_copy_preview":    ad_copy[:200],
            "caption":            caption,
            "cta_text":           cta_text,
            "link_url":           link_url,
            "start_date":         ts_to_date(ad.get("start_date")),
            "stop_date":          ts_to_date(ad.get("end_date")) if ad.get("end_date") else "Still Running",
            "total_active_days":  self._calc_days(ad.get("start_date"), ad.get("end_date")),
            "impressions":        imp_display,
            "spend_lower":        spend_lower,
            "spend_upper":        spend_upper,
            "currency":           currency,
            "page_likes":         page_likes,
            "collation_count":    ad.get("collation_count", 1),
            "categories":         ", ".join(safe_list(ad.get("categories"))),
            "targeted_countries": ", ".join(safe_list(ad.get("targeted_or_reached_countries"))),
            "page_profile_url":   safe_str(snapshot.get("page_profile_uri")),
            "collected_at":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _calc_days(self, start, end):
        try:
            s = datetime.fromtimestamp(int(start))
            e = datetime.fromtimestamp(int(end)) if end else datetime.now()
            return (e - s).days
        except Exception:
            return "N/A"