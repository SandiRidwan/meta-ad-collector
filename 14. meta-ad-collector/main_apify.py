import sys
from rich.console import Console
from apify_collector import ApifyAdCollector
from browser_collector import BrowserAdCollector
from exporter import DataExporter
import config

console = Console()


def run_collection(export_csv=True, export_sheets=True):
    ads_data = []
    all_terms = config.TARGET_BRANDS + config.SEARCH_KEYWORDS

    # Primary: Apify
    console.print("[bold]Step 1: Trying Apify...[/bold]")
    try:
        apify = ApifyAdCollector()
        ads_data = apify.collect(all_terms, country="ID", limit=200)
    except Exception as e:
        console.print(f"[yellow]Apify failed ({e}), switching to browser fallback...[/yellow]")
        ads_data = []

    # Fallback: Browser
    if not ads_data:
        console.print("[bold yellow]Using Browser Fallback...[/bold yellow]")
        browser = BrowserAdCollector()
        for term in all_terms:
            try:
                ads = browser.collect_via_network_intercept(term)
                ads_data.extend(ads)
            except Exception as e:
                console.print(f"[red]Error on '{term}': {e}[/red]")

    if not ads_data:
        console.print("[red]No data collected.[/red]")
        return

    # Deduplicate
    seen = set()
    unique = []
    for ad in ads_data:
        aid = ad.get("ad_id", "")
        if aid and aid not in seen:
            seen.add(aid)
            unique.append(ad)
        elif not aid:
            unique.append(ad)

    exporter = DataExporter()
    exporter.export_summary(unique)

    if export_csv:
        exporter.to_csv(unique)

    if export_sheets:
        exporter.to_google_sheets(unique)

    return unique


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "once"

    if mode == "schedule":
        import schedule
        import time

        def job():
            run_collection()

        schedule.every().day.at("08:00").do(job)
        console.print("[bold green]Scheduler aktif. Ctrl+C untuk stop.[/bold green]")
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        run_collection()