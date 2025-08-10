import os
import psycopg2
from contextlib import contextmanager
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

SCHEMA = """
CREATE TABLE IF NOT EXISTS listings (
    id TEXT PRIMARY KEY,
    source TEXT,
    source_id TEXT,
    url TEXT,
    title TEXT,
    description TEXT,
    price INTEGER,
    bedrooms REAL,
    bathrooms REAL,
    sqft INTEGER,
    has_central_air INTEGER,
    has_offstreet_prk INTEGER,
    has_garage INTEGER,
    has_dishwasher INTEGER,
    pets_allowed INTEGER,
    neighborhood TEXT,
    city TEXT,
    created_at TIMESTAMP,
    posted_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_listings_source ON listings(source);
CREATE INDEX IF NOT EXISTS idx_listings_price ON listings(price);
CREATE INDEX IF NOT EXISTS idx_listings_bedrooms ON listings(bedrooms);
"""

@contextmanager
def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL env var is not set")
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA)

def upsert_listing(row: dict):
    keys = sorted(row.keys())
    cols = ",".join(keys)
    placeholders = ",".join([f"%({k})s" for k in keys])
    updates = ",".join([f"{k}=EXCLUDED.{k}" for k in keys if k != "id"])
    sql = f"INSERT INTO listings ({cols}) VALUES ({placeholders}) ON CONFLICT (id) DO UPDATE SET {updates}"
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, row)

def now_iso():
    return datetime.utcnow().isoformat()
