import sys
import csv
import hashlib
from datetime import datetime
from db_pg import init_db, upsert_listing

TEMPLATE_HEADERS = ["url","title","description","price","bedrooms","bathrooms","sqft","has_central_air","has_offstreet_prk","has_garage","has_dishwasher","pets_allowed","neighborhood","city","posted_at"]

def stable_id(url: str):
    key = f"manual|{url or ''}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

def run(path):
    init_db()
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = stable_id(row.get("url"))
            data = {
                "id": rid,
                "source": "manual",
                "source_id": None,
                "url": row.get("url"),
                "title": row.get("title"),
                "description": row.get("description"),
                "price": int(row["price"]) if row.get("price") else None,
                "bedrooms": float(row["bedrooms"]) if row.get("bedrooms") else None,
                "bathrooms": float(row["bathrooms"]) if row.get("bathrooms") else None,
                "sqft": int(row["sqft"]) if row.get("sqft") else None,
                "has_central_air": int(row["has_central_air"]) if row.get("has_central_air") else 0,
                "has_offstreet_prk": int(row["has_offstreet_prk"]) if row.get("has_offstreet_prk") else 0,
                "has_garage": int(row["has_garage"]) if row.get("has_garage") else 0,
                "has_dishwasher": int(row["has_dishwasher"]) if row.get("has_dishwasher") else 0,
                "pets_allowed": int(row["pets_allowed"]) if row.get("pets_allowed") else 0,
                "neighborhood": row.get("neighborhood"),
                "city": row.get("city"),
                "created_at": datetime.utcnow(),
                "posted_at": row.get("posted_at"),
            }
            upsert_listing(data)
    print("Manual import complete.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_manual_pg.py <csv_path>")
        sys.exit(1)
    run(sys.argv[1])
