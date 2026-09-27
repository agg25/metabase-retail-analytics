"""Load data/*.csv into the Postgres 'retail' database.

Prereqs: `docker compose up -d` and `pip install -r requirements.txt`.

    python load_data.py
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

import psycopg

TABLES: dict[str, list[str]] = {
    "customers": ["customer_id", "signup_date", "signup_month", "region", "acquisition_channel"],
    "products": ["product_id", "category", "unit_price", "unit_cost"],
    "orders": ["order_id", "customer_id", "order_date", "order_month", "channel"],
    "order_items": ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount"],
    "returns": ["return_id", "order_item_id", "order_id", "product_id", "return_date", "reason", "refund_amount"],
    "marketing_spend": ["spend_id", "month", "channel", "spend"],
}

# Host port 5433 (not 5432) because a local PostgreSQL already uses 5432 on this machine.
CONN = os.getenv("DATABASE_URL", "postgresql://metabase:metabase@localhost:5433/retail")


def main() -> None:
    schema = Path("sql/schema_postgres.sql").read_text(encoding="utf-8")
    with psycopg.connect(CONN) as conn:
        for stmt in schema.split(";"):
            if stmt.strip():
                conn.execute(stmt.strip())
        conn.commit()
        for name, cols in TABLES.items():
            with (Path("data") / f"{name}.csv").open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            placeholders = ", ".join(["%s"] * len(cols))
            sql = f"INSERT INTO {name} ({', '.join(cols)}) VALUES ({placeholders})"
            cur = conn.cursor()
            cur.executemany(sql, [tuple(r[c] for c in cols) for r in rows])
            conn.commit()
            print(f"{name}: {len(rows)} rows")
    print("Loaded into Postgres 'retail' database.")


if __name__ == "__main__":
    main()
