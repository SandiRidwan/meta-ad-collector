import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
from rich.console import Console
import config

console = Console()


class DataExporter:
    def __init__(self):
        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

    def to_csv(self, ads_data, filename=None):
        if not ads_data:
            console.print("[red]No data to export![/red]")
            return

        os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{config.OUTPUT_FOLDER}/meta_ads_{timestamp}.csv"

        df = pd.DataFrame(ads_data)

        # Paksa kolom ID tetap string — cegah Excel convert ke scientific notation
        for col in ["ad_id", "page_id"]:
            if col in df.columns:
                df[col] = df[col].astype(str)

        # Sort
        if "page_name" in df.columns and "start_date" in df.columns:
            df = df.sort_values(["page_name", "start_date"], ascending=[True, False])

        df.to_csv(filename, index=False, encoding="utf-8-sig")
        console.print(f"\n[bold green]CSV saved: {filename}[/bold green]")
        console.print(f"   Total rows: {len(df)}")
        console.print(f"   Columns: {len(df.columns)}")
        return filename

    def to_google_sheets(self, ads_data, sheet_name="Meta Ads Data"):
        if not ads_data:
            console.print("[red]No data to export![/red]")
            return

        creds_file = os.getenv("GOOGLE_CREDS_FILE", "google_creds.json")
        sheet_id   = os.getenv("GOOGLE_SHEETS_ID")

        if not os.path.exists(creds_file):
            console.print("[yellow]google_creds.json tidak ditemukan, skip Google Sheets[/yellow]")
            return
        if not sheet_id:
            console.print("[yellow]GOOGLE_SHEETS_ID kosong di .env, skip Google Sheets[/yellow]")
            return

        try:
            creds = Credentials.from_service_account_file(creds_file, scopes=self.scopes)
            gc = gspread.authorize(creds)
            spreadsheet = gc.open_by_key(sheet_id)

            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                worksheet.clear()
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=sheet_name, rows=len(ads_data) + 100, cols=30
                )

            df = pd.DataFrame(ads_data)
            for col in ["ad_id", "page_id"]:
                if col in df.columns:
                    df[col] = df[col].astype(str)

            rows = [list(df.columns)] + df.fillna("").values.tolist()
            worksheet.update(rows, value_input_option="USER_ENTERED")
            worksheet.format("1:1", {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.2, "green": 0.4, "blue": 0.8}
            })

            sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
            console.print(f"\n[bold green]Google Sheets updated: {sheet_url}[/bold green]")
            return sheet_url

        except Exception as e:
            console.print(f"[red]Google Sheets error: {e}[/red]")

    def export_summary(self, ads_data):
        df = pd.DataFrame(ads_data)
        console.print("\n[bold cyan]══════════════ DATA SUMMARY ══════════════[/bold cyan]")
        console.print(f"  Total Ads      : {len(df)}")
        if "status" in df.columns:
            console.print(f"  Active Ads     : {len(df[df['status'] == 'ACTIVE'])}")
            console.print(f"  Inactive Ads   : {len(df[df['status'] == 'INACTIVE'])}")
        if "page_name" in df.columns:
            console.print(f"  Unique Brands  : {df['page_name'].nunique()}")
        if "search_term" in df.columns:
            console.print(f"  Search Terms   : {df['search_term'].nunique()}")
        console.print("[bold cyan]══════════════════════════════════════════[/bold cyan]")