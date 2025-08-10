import hashlib
import feedparser
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from db_pg import init_db, upsert_listing
from parse_utils import parse_price, parse_bedrooms, parse_bathrooms, parse_sqft, parse_flags, parse_when
from datetime import datetime

RSS_URL = "https://grandrapids.craigslist.org/search/apa?format=rss"

def clean_html(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(" ", strip=True)

def stable_id(source: str, source_id: str, url: str) -> str:
    key = f"{source}|{source_id or ''}|{url or ''}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

def extract_source_id(entry_link: str):
    try:
        path = urlparse(entry_link).path
        digits = "".join(ch for ch in path if ch.isdigit())
        return digits or None
    except Exception:
        return None

def fetch():
    return feedparser.parse(RSS_URL)

def run():
    init_db()
    feed = fetch()
    count = 0
    for e in feed.entries:
        title = e.get("title", "") or ""
        summary = e.get("summary", "") or ""
        link = e.get("link", "") or ""
        published = e.get("published", "") or ""

        desc = clean_html(summary)
        text_all = f"{title}\n{desc}"
        price = parse_price(text_all)
        beds = parse_bedrooms(text_all)
        baths = parse_bathrooms(text_all)
        sqft = parse_sqft(text_all)
        flags = parse_flags(text_all)
        posted_dt = parse_when(published)

        sid = extract_source_id(link)
        rid = stable_id("craigslist", sid, link)

        row = {
            "id": rid,
            "source": "craigslist",
            "source_id": sid,
            "url": link,
            "title": title,
            "description": desc,
            "price": price,
            "bedrooms": beds,
            "bathrooms": baths,
            "sqft": sqft,
            "has_central_air": flags.get("has_central_air", 0),
            "has_offstreet_prk": flags.get("has_offstreet_prk", 0),
            "has_garage": flags.get("has_garage", 0),
            "has_dishwasher": flags.get("has_dishwasher", 0),
            "pets_allowed": flags.get("pets_allowed", 0),
            "neighborhood": None,
            "city": None,
            "created_at": datetime.utcnow(),
            "posted_at": posted_dt,
        }
        upsert_listing(row)
        count += 1
    print(f"Upserted {count} listings from Craigslist RSS.")

if __name__ == "__main__":
    run()
