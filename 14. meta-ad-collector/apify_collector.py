from apify_client import ApifyClient
from datetime import datetime
from rich.console import Console
import os
import time

console = Console()


class ApifyAdCollector:
    def __init__(self):
        self.token = os.getenv("APIFY_TOKEN")
        if not self.token:
            raise ValueError("APIFY_TOKEN tidak ada di .env")
        self.client = ApifyClient(self.token)

    def collect(self, search_terms, country="ID", limit=200):
        from urllib.parse import quote_plus
        all_ads = []

        for term in search_terms:
            console.print(f"\n[bold cyan]Apify collecting: {term}[/bold cyan]")

            # Encode term dengan benar
            encoded_term = quote_plus(term)

            search_url = (
                f"https://www.facebook.com/ads/library/"
                f"?active_status=all"
                f"&ad_type=all"
                f"&country={country}"
                f"&q={encoded_term}"
                f"&search_type=keyword_unordered"
                f"&media_type=all"
            )

            console.print(f"  URL: {search_url[:80]}...")

            try:
                run = self.client.actor("curious_coder/facebook-ads-library-scraper").call(
                    run_input={
                        "urls": [{"url": search_url}],
                        "limitPerSource": limit,
                        "scrapeAdDetails": True,
                        "scrapePageAds.activeStatus": "all",
                        "scrapePageAds.countryCode": country,
                        "scrapePageAds.sortBy": "impressions_desc",
                    },
                    timeout_secs=300,
                )

                count = 0
                dataset_id = run.get("defaultDatasetId")
                if not dataset_id:
                    console.print(f"  [red]No dataset returned[/red]")
                    continue

                for item in self.client.dataset(dataset_id).iterate_items():
                    normalized = self._normalize(item, term)
                    all_ads.append(normalized)
                    count += 1

                console.print(f"  [green]{count} ads collected[/green]")

            except Exception as e:
                console.print(f"  [red]Error: {e}[/red]")

            import time
            time.sleep(2)

        # Deduplicate
        seen = set()
        unique = []
        for ad in all_ads:
            aid = ad.get("ad_id", "")
            key = aid if aid and aid != "N/A" else str(ad.get("ad_copy_preview", ""))[:50]
            if key not in seen:
                seen.add(key)
                unique.append(ad)

        console.print(f"\n[bold green]Total unique ads dari Apify: {len(unique)}[/bold green]")
        return unique

    def _normalize(self, item, search_term):
        from datetime import datetime

        def safe(val, default="N/A"):
            if val is None or val == "" or val == []:
                return default
            return str(val)

        def safe_list(val):
            return val if isinstance(val, list) else []

        def safe_dict(val):
            return val if isinstance(val, dict) else {}

        def calc_days(start, end):
            try:
                s = datetime.fromisoformat(str(start))
                e = datetime.fromisoformat(str(end)) if end and end != "N/A" else datetime.now()
                return (e - s).days
            except Exception:
                return "N/A"

        # Core fields
        snapshot    = safe_dict(item.get("snapshot"))
        advertiser  = safe_dict(item.get("advertiser"))
        page_info   = safe_dict(safe_dict(advertiser.get("ad_library_page_info")).get("page_info"))
        aaa_info    = safe_dict(item.get("aaa_info"))
        platforms   = safe_list(item.get("publisher_platform"))

        # Dates — pakai formatted version yang sudah bersih
        start_date  = safe(item.get("start_date_formatted", item.get("start_date")))
        end_date    = item.get("end_date_formatted") or item.get("end_date")
        stop_date   = safe(end_date) if end_date else "Still Running"

        # Trim jam dari datetime string (2025-12-17 08:00:00 → 2025-12-17)
        if start_date != "N/A" and " " in start_date:
            start_date = start_date.split(" ")[0]
        if stop_date != "Still Running" and " " in stop_date:
            stop_date = stop_date.split(" ")[0]

        # Ad copy — coba body dulu, lalu cards
        bodies = []
        raw_body = snapshot.get("body") or {}
        if isinstance(raw_body, dict):
            t = raw_body.get("text", "")
            if t and t.strip():
                bodies.append(t.strip())
        elif isinstance(raw_body, str) and raw_body.strip():
            bodies.append(raw_body.strip())

        if not bodies:
            for card in safe_list(snapshot.get("cards"))[:2]:
                if isinstance(card, dict):
                    b = card.get("body", "").strip()
                    if b and b != " ":
                        bodies.append(b)

        if not bodies:
            t = snapshot.get("title", "")
            if t and t.strip():
                bodies.append(t.strip())

        ad_copy = " | ".join(filter(None, bodies)) or "N/A"

        # Spend
        raw_spend = item.get("spend")
        spend = safe_dict(raw_spend)
        spend_lower = spend.get("lower_bound", "Not Disclosed" if raw_spend is None else "N/A")
        spend_upper = spend.get("upper_bound", "Not Disclosed" if raw_spend is None else "N/A")

        # Impressions
        imp = safe_dict(item.get("impressions_with_index"))
        imp_text = imp.get("impressions_text")
        imp_index = imp.get("impressions_index", -1)
        impressions = imp_text if imp_text else ("Not Disclosed" if imp_index == -1 else str(imp_index))

        # EU reach dari aaa_info
        eu_reach = aaa_info.get("eu_total_reach", "N/A")
        gender_audience = safe(aaa_info.get("gender_audience"))
        age_audience = safe(aaa_info.get("age_audience"))

        # Page info dari advertiser
        ig_followers = safe(page_info.get("ig_followers"))
        ig_username  = safe(page_info.get("ig_username"))
        page_category = safe(page_info.get("page_category"))
        page_verified = safe(page_info.get("page_verification"))

        # Categories
        cats = safe_list(item.get("categories"))

        return {
            "search_term":      search_term,
            "ad_id":            "'" + safe(item.get("ad_archive_id") or item.get("ad_id")),
            "page_id":          "'" + safe(item.get("page_id")),
            "page_name":        safe(item.get("page_name")),
            "page_category":    page_category,
            "page_verified":    page_verified,
            "ig_username":      ig_username,
            "ig_followers":     ig_followers,
            "page_likes":       safe(snapshot.get("page_like_count")),
            "status":           "ACTIVE" if item.get("is_active") else "INACTIVE",
            "platforms":        ", ".join(platforms),
            "display_format":   safe(snapshot.get("display_format")),
            "ad_title":         safe(snapshot.get("title")),
            "ad_copy_preview":  ad_copy[:300],
            "cta_text":         safe(snapshot.get("cta_text")),
            "link_url":         safe(snapshot.get("link_url")),
            "start_date":       start_date,
            "stop_date":        stop_date,
            "total_active_days": calc_days(start_date, stop_date if stop_date != "Still Running" else None),
            "impressions":      impressions,
            "spend_lower":      spend_lower,
            "spend_upper":      spend_upper,
            "currency":         safe(item.get("currency"), "Not Disclosed"),
            "eu_reach":         eu_reach,
            "gender_audience":  gender_audience,
            "age_audience":     age_audience,
            "categories":       ", ".join(cats),
            "targeted_countries": ", ".join(safe_list(item.get("targeted_or_reached_countries"))),
            "total_ads_found":  safe(item.get("total")),
            "ad_library_url":   safe(item.get("ad_library_url")),
            "page_profile_url": safe(snapshot.get("page_profile_uri")),
            "collected_at":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }