import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
APP_ID = os.getenv("META_APP_ID")
APP_SECRET = os.getenv("META_APP_SECRET")
APIFY_TOKEN = os.getenv("APIFY_TOKEN")

AD_LIBRARY_URL = "https://graph.facebook.com/v19.0/ads_archive"

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

AD_REACHED_COUNTRIES = ["ID"]
AD_TYPE = "ALL"
LIMIT_PER_REQUEST = 100

OUTPUT_FOLDER = "output"

REQUEST_DELAY = 1.5
MAX_RETRIES = 3