# 🎯 Meta Ad Library Collector

<div align="center">

```
███╗   ███╗███████╗████████╗ █████╗      █████╗ ██████╗ ███████╗
████╗ ████║██╔════╝╚══██╔══╝██╔══██╗    ██╔══██╗██╔══██╗██╔════╝
██╔████╔██║█████╗     ██║   ███████║    ███████║██║  ██║███████╗
██║╚██╔╝██║██╔══╝     ██║   ██╔══██║    ██╔══██║██║  ██║╚════██║
██║ ╚═╝ ██║███████╗   ██║   ██║  ██║    ██║  ██║██████╔╝███████║
╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝    ╚═╝  ╚═╝╚═════╝ ╚══════╝
```

**Automated competitive intelligence tool for Meta Ad Library**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Automation-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev)
[![Apify](https://img.shields.io/badge/Apify-Scraper-FF9900?style=for-the-badge&logo=apify&logoColor=white)](https://apify.com)
[![Google Sheets](https://img.shields.io/badge/Google_Sheets-Export-34A853?style=for-the-badge&logo=google-sheets&logoColor=white)](https://sheets.google.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

*Collect · Analyze · Export — Publicly available ad data, ethically.*

</div>

---

## ✨ What It Does

This tool automatically collects **publicly available** ad data from the [Meta Ad Library](https://www.facebook.com/ads/library/) — the same data anyone can browse manually, but automated, structured, and delivered straight to your CSV or Google Sheets.

```
🔍 Search by brand name or keyword
        ↓
📦 Collect ad details (status, platforms, copy, dates, spend ranges)
        ↓
🧹 Deduplicate & clean data automatically
        ↓
📊 Export to CSV + Google Sheets
        ↓
⏰ Schedule for daily/weekly automated runs
```

---

## 🚀 Features

| Feature | Description |
|---|---|
| 🔄 **Hybrid Collection** | Apify scraper (primary) + Playwright browser fallback |
| 🎯 **Multi-brand Search** | Search multiple brands & keywords in one run |
| 📅 **Date Parsing** | Auto-converts timestamps to human-readable dates |
| 🔢 **Deduplication** | Global dedup across all search terms |
| 📊 **Google Sheets Sync** | Auto-upload with formatted headers |
| ⏰ **Scheduler** | Run on-demand or on a daily cron schedule |
| 🛡️ **Rate Limit Handling** | Auto-retry with backoff on 429 errors |
| 🌍 **Multi-country** | Filter by any country code (ID, US, GB, etc.) |

---

## 📋 Data Collected

For each ad, the tool captures:

```
✅ Ad ID & Page Name          ✅ Active / Inactive Status
✅ Start & Stop Dates         ✅ Total Days Running
✅ Publisher Platforms        ✅ Display Format (Image/Video/Carousel)
✅ Ad Copy Preview            ✅ CTA Text & Link URL
✅ Spend Range (if disclosed) ✅ Impressions (if disclosed)
✅ Currency                   ✅ EU Reach Data
✅ Gender & Age Audience      ✅ Instagram Followers
✅ Page Category              ✅ Ad Library URL
```

> **Note:** Spend and impressions data are only visible when advertisers opt into transparency disclosure. This is a Meta platform policy, not a tool limitation.

---

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- [Apify account](https://apify.com) (free tier available — $5 credit/month)
- Google Cloud account (for Sheets export — optional)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/meta-ad-collector.git
cd meta-ad-collector

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright browsers
playwright install chromium

# 4. Configure environment
cp .env.example .env
# Edit .env with your tokens (see Configuration section)
```

---

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
# Apify (Primary scraper)
APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxxxx

# Meta Graph API (Optional — requires Ad Library API approval)
META_ACCESS_TOKEN=your_long_lived_token_here
META_APP_ID=your_app_id_here
META_APP_SECRET=your_app_secret_here

# Google Sheets (Optional)
GOOGLE_SHEETS_ID=your_google_sheet_id_here
GOOGLE_CREDS_FILE=google_creds.json
```

Edit `config.py` to set your target brands and keywords:

```python
TARGET_BRANDS = [
    "Nike Indonesia",
    "Adidas Indonesia",
    "Puma",
    "Uniqlo Indonesia",
    "Zara",
    "H&M Indonesia",
]

SEARCH_KEYWORDS = [
    "flash sale",
    "diskon",
]

AD_REACHED_COUNTRIES = ["ID"]  # ID = Indonesia
```

---

## 🎮 Usage

### Run Once (On-Demand)
```bash
python main.py
```

### Run on Schedule (Daily at 8 AM)
```bash
python main.py schedule
```

### Output
```
output/
└── meta_ads_20260403_201156.csv   ← timestamped CSV
```
Google Sheets link will be printed in the terminal after each run.

---

## 🏗️ Project Structure

```
meta-ad-collector/
│
├── main.py                 ← Entry point — orchestrates everything
├── config.py               ← Brands, keywords, settings
├── apify_collector.py      ← Primary: Apify-based scraper
├── browser_collector.py    ← Fallback: Playwright browser automation
├── exporter.py             ← CSV + Google Sheets export
├── scheduler.py            ← Cron-style scheduler
│
├── .env                    ← API keys (never commit this!)
├── .env.example            ← Template for .env
├── google_creds.json       ← Google service account (never commit!)
├── requirements.txt        ← Python dependencies
│
└── output/                 ← All exported CSV files
    └── meta_ads_TIMESTAMP.csv
```

---

## 🔧 How It Works

### Hybrid Architecture

```
                    ┌─────────────────┐
                    │    main.py      │
                    └────────┬────────┘
                             │
              ┌──────────────▼──────────────┐
              │      Apify Scraper          │  ← Primary
              │  (curious_coder actor)      │
              └──────────────┬──────────────┘
                             │ fails?
              ┌──────────────▼──────────────┐
              │   Playwright Browser        │  ← Fallback
              │   (network intercept)       │
              └──────────────┬──────────────┘
                             │
              ┌──────────────▼──────────────┐
              │      DataExporter           │
              │   CSV  +  Google Sheets     │
              └─────────────────────────────┘
```

### Data Collection Strategy

1. **Apify (Primary)** — Uses `curious_coder/facebook-ads-library-scraper` actor. Reliable, structured, includes extra fields like EU reach and audience demographics.

2. **Playwright Fallback** — Headless Chromium browser with network response interception. Intercepts Meta's internal GraphQL API calls directly from the browser session.

3. **Meta Graph API (Optional)** — Requires Ad Library API approval from Meta. Provides the most structured data including spend/impressions when advertisers disclose.

---

## 📦 Dependencies

```
requests          — HTTP client for Meta API
pandas            — Data manipulation & CSV export
gspread           — Google Sheets API client
google-auth       — Google authentication
playwright        — Browser automation
apify-client      — Apify platform client
python-dotenv     — Environment variable management
schedule          — Job scheduling
rich              — Beautiful terminal output
```

---

## 🔑 Getting API Keys

### Apify Token
1. Sign up at [apify.com](https://apify.com)
2. Go to **Settings → Integrations**
3. Copy your **Personal API Token**

### Google Sheets (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → Enable **Google Sheets API** + **Google Drive API**
3. Create a **Service Account** → Download JSON key → rename to `google_creds.json`
4. Share your Google Sheet with the service account email

### Meta Ad Library API (Optional — Requires Approval)
1. Visit [facebook.com/ads/library/api](https://www.facebook.com/ads/library/api)
2. Complete identity verification
3. Wait for Meta approval (1-3 business days)
4. Generate token via [Graph API Explorer](https://developers.facebook.com/tools/explorer/)

---

## 📊 Sample Output

| search_term | page_name | status | start_date | stop_date | platforms | ad_copy_preview |
|---|---|---|---|---|---|---|
| Nike Indonesia | Nike ID | ACTIVE | 2026-01-15 | Still Running | FACEBOOK, INSTAGRAM | Just Do It — New collection now available |
| Adidas Indonesia | Adidas ID | INACTIVE | 2025-12-01 | 2026-01-31 | INSTAGRAM | Impossible is Nothing |
| flash sale | Tokopedia | ACTIVE | 2026-03-28 | 2026-04-07 | FACEBOOK, INSTAGRAM, MESSENGER | 🔥 Flash Sale 99% OFF hari ini! |

---

## ⚠️ Important Notes

- **This tool only collects publicly available data** — the same data visible to anyone at [facebook.com/ads/library](https://www.facebook.com/ads/library)
- **No authentication bypass** — all collection is done through approved public interfaces
- **Spend & impressions** may show "Not Disclosed" — this is Meta's platform policy for advertisers who don't opt into transparency disclosure
- **Rate limiting** is built-in — the tool automatically handles Meta's rate limits with configurable delays

---

## 🗺️ Roadmap

- [ ] Slack/email notifications after each scheduled run
- [ ] Delta mode — only collect new ads since last run
- [ ] Ad creative image downloading
- [ ] Dashboard UI with charts
- [ ] Multi-country parallel collection

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with Python 🐍 · Powered by Apify 🕷️ · Data from Meta Ad Library 📚**

*For competitive intelligence. For research. For transparency.*

</div>
