"""SQLite-toegang voor de Kassa POC.

Bedragen zijn overal integers in centen. Prijzen zijn inclusief btw.
"""
import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "kassa.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS stores (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    kvk TEXT,
    btw_nummer TEXT
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id INTEGER REFERENCES categories(id),
    icon TEXT,
    color TEXT,
    sort INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    ean TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category_id INTEGER REFERENCES categories(id),   -- NULL = niet zichtbaar in de kassa
    price_cents INTEGER NOT NULL,
    btw_pct INTEGER NOT NULL DEFAULT 9,
    statiegeld_cents INTEGER NOT NULL DEFAULT 0,
    age_restricted INTEGER NOT NULL DEFAULT 0,
    unit TEXT DEFAULT 'stuk',
    image_url TEXT,
    stock INTEGER NOT NULL DEFAULT 0,
    min_stock INTEGER NOT NULL DEFAULT 5
);

CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL REFERENCES stores(id),
    ts TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    total_cents INTEGER NOT NULL,
    statiegeld_cents INTEGER NOT NULL DEFAULT 0,
    payment_method TEXT NOT NULL,
    payment_ref TEXT,
    status TEXT NOT NULL DEFAULT 'completed'
);

CREATE TABLE IF NOT EXISTS sale_lines (
    id INTEGER PRIMARY KEY,
    sale_id INTEGER NOT NULL REFERENCES sales(id),
    product_id INTEGER REFERENCES products(id),
    name TEXT NOT NULL,
    qty INTEGER NOT NULL,
    unit_price_cents INTEGER NOT NULL,
    btw_pct INTEGER NOT NULL,
    statiegeld_cents INTEGER NOT NULL DEFAULT 0
);
"""


def connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db():
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_schema():
    with get_db() as conn:
        conn.executescript(SCHEMA)


def is_seeded():
    with get_db() as conn:
        return conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] > 0
