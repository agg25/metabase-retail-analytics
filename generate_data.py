"""Generate a synthetic e-commerce dataset that tells a business story.

Story: "Fix the profit leak."
Revenue grows year-over-year, but gross margin quietly shrinks because of three levers
the dashboard is designed to reveal:
  1. Over-discounting — discount rate rises over time, concentrated in the Social and
     Display acquisition channels.
  2. Rising returns — Apparel (size/fit) and Home Decor (damaged) drive return leakage.
  3. Misallocated ad spend — expensive channels acquire one-time buyers while cheap
     channels bring repeat buyers (a CAC vs LTV inversion).

Run:  python generate_data.py
Outputs: data/*.csv  (source of truth)  and  retail.db  (SQLite, for validation/preview)
"""

from __future__ import annotations

import csv
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

SEED = 42
OUT = Path("data")
START = date(2023, 1, 1)
END = date(2024, 12, 31)

CATEGORIES: dict[str, dict] = {
    #        cost ratio, price lo, price hi, base return rate, return reason
    "Apparel":     {"cost": 0.45, "lo": 30, "hi": 120, "ret": 0.20, "reason": "size_fit"},
    "Home Decor":  {"cost": 0.55, "lo": 40, "hi": 200, "ret": 0.12, "reason": "damaged"},
    "Kitchen":     {"cost": 0.50, "lo": 20, "hi": 150, "ret": 0.06, "reason": "changed_mind"},
    "Bed & Bath":  {"cost": 0.48, "lo": 25, "hi": 130, "ret": 0.05, "reason": "not_as_described"},
    "Accessories": {"cost": 0.40, "lo": 10, "hi": 60,  "ret": 0.04, "reason": "changed_mind"},
}

# channel -> (cac base, repeat probability, discount level)
CHANNELS: dict[str, tuple[int, float, str]] = {
    "Organic":  (15, 0.45, "low"),
    "Email":    (10, 0.45, "low"),
    "Referral": (20, 0.40, "low"),
    "Social":   (60, 0.15, "high"),
    "Display":  (80, 0.10, "high"),
}

REGIONS = ["North", "South", "East", "West", "Central"]

TABLES: dict[str, list[str]] = {
    "customers": ["customer_id", "signup_date", "signup_month", "region", "acquisition_channel"],
    "products": ["product_id", "category", "unit_price", "unit_cost"],
    "orders": ["order_id", "customer_id", "order_date", "order_month", "channel"],
    "order_items": ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount"],
    "returns": ["return_id", "order_item_id", "order_id", "product_id", "return_date", "reason", "refund_amount"],
    "marketing_spend": ["spend_id", "month", "channel", "spend"],
}


def _month(d: date) -> str:
    return d.strftime("%Y-%m")


def _rand_date(rng: random.Random, lo: date, hi: date) -> date:
    return lo + timedelta(days=rng.randint(0, max(0, (hi - lo).days)))


def _months_from_start(d: date) -> int:
    return (d.year - START.year) * 12 + (d.month - START.month)


def _discount(rng: random.Random, level: str, d: date) -> float:
    trend = 0.004 * _months_from_start(d)  # creeping over-discounting
    if level == "high":
        return round(min(0.45, rng.uniform(0.25, 0.35) + trend), 3)
    return round(min(0.20, rng.uniform(0.05, 0.12) + trend), 3)


def _return_rate(cat: str, d: date) -> float:
    return CATEGORIES[cat]["ret"] + 0.003 * _months_from_start(d)

def build(rng: random.Random) -> dict[str, list[dict]]:
    products: list[dict] = []
    for cat, meta in CATEGORIES.items():
        for _ in range(8):
            price = round(rng.uniform(meta["lo"], meta["hi"]), 2)
            products.append({
                "product_id": f"p{len(products) + 1:04d}",
                "category": cat,
                "unit_price": price,
                "unit_cost": round(price * meta["cost"], 2),
            })
    by_id = {p["product_id"]: p for p in products}

    channel_names = list(CHANNELS)
    weights = [0.30, 0.30, 0.15, 0.15, 0.10]
    customers: list[dict] = []
    for _ in range(1500):
        ch = rng.choices(channel_names, weights=weights)[0]
        signup = _rand_date(rng, START, date(2024, 11, 30))
        customers.append({
            "customer_id": f"c{len(customers) + 1:05d}",
            "signup_date": signup.isoformat(),
            "signup_month": _month(signup),
            "region": rng.choice(REGIONS),
            "acquisition_channel": ch,
        })

    orders: list[dict] = []
    items: list[dict] = []
    returns: list[dict] = []
    for cust in customers:
        ch = cust["acquisition_channel"]
        _, repeat_p, disc_level = CHANNELS[ch]
        n_orders = 1
        while n_orders < 8 and rng.random() < repeat_p:
            n_orders += 1
        signup = date.fromisoformat(cust["signup_date"])
        for _ in range(n_orders):
            od = _rand_date(rng, signup, END)
            oid = f"o{len(orders) + 1:06d}"
            orders.append({
                "order_id": oid,
                "customer_id": cust["customer_id"],
                "order_date": od.isoformat(),
                "order_month": _month(od),
                "channel": ch,
            })
            for _ in range(rng.randint(1, 4)):
                pid = rng.choice(list(by_id))
                p = by_id[pid]
                qty = rng.randint(1, 2)
                disc = _discount(rng, disc_level, od)
                iid = f"i{len(items) + 1:06d}"
                items.append({
                    "order_item_id": iid,
                    "order_id": oid,
                    "product_id": pid,
                    "quantity": qty,
                    "unit_price": p["unit_price"],
                    "discount": disc,
                })
                if rng.random() < _return_rate(p["category"], od):
                    returns.append({
                        "return_id": f"r{len(returns) + 1:06d}",
                        "order_item_id": iid,
                        "order_id": oid,
                        "product_id": pid,
                        "return_date": _rand_date(rng, od, min(od + timedelta(days=45), END)).isoformat(),
                        "reason": CATEGORIES[p["category"]]["reason"],
                        "refund_amount": round(p["unit_price"] * qty * (1 - disc), 2),
                    })

    spend: list[dict] = []
    month_starts = [date(2023, 1, 1) + timedelta(days=30 * i) for i in range(24)]
    for m in month_starts:
        mm = _month(m)
        for ch in channel_names:
            base = CHANNELS[ch][0]
            new_c = sum(1 for c in customers if c["signup_month"] == mm and c["acquisition_channel"] == ch)
            growth = 1.0 + 0.15 * (m.year - 2023)  # expensive channels scale up over time
            spend.append({
                "spend_id": f"s{len(spend) + 1:04d}",
                "month": mm,
                "channel": ch,
                "spend": round(base * max(new_c, 1) * growth * rng.uniform(0.9, 1.1), 2),
            })

    return {
        "products": products, "customers": customers, "orders": orders,
        "order_items": items, "returns": returns, "marketing_spend": spend,
    }

def write_csv(name: str, rows: list[dict]) -> None:
    OUT.mkdir(exist_ok=True)
    with (OUT / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=TABLES[name])
        w.writeheader()
        w.writerows(rows)


def build_sqlite(data: dict[str, list[dict]]) -> None:
    db = Path("retail.db")
    if db.exists():
        db.unlink()
    conn = sqlite3.connect(db)
    for name, cols in TABLES.items():
        placeholders = ", ".join("?" for _ in cols)
        conn.execute(f"CREATE TABLE {name} ({', '.join(cols)})")
        conn.executemany(
            f"INSERT INTO {name} ({', '.join(cols)}) VALUES ({placeholders})",
            [tuple(r[c] for c in cols) for r in data[name]],
        )
    conn.commit()
    conn.close()
    print("Wrote retail.db")


def story_check() -> None:
    conn = sqlite3.connect("retail.db")

    print("\n== Story check: revenue grows while margin shrinks ==")
    for month, rev, margin in conn.execute("""
        SELECT order_month,
               ROUND(SUM(oi.quantity*oi.unit_price*(1-oi.discount)), 0),
               ROUND(100.0*SUM(oi.quantity*oi.unit_price*(1-oi.discount)-oi.quantity*p.unit_cost)
                     / SUM(oi.quantity*oi.unit_price*(1-oi.discount)), 1)
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE order_month IN ('2023-01','2023-07','2024-01','2024-07','2024-12')
        GROUP BY order_month ORDER BY order_month
    """).fetchall():
        print(f"  {month}: revenue=${rev:>8,.0f}  gross_margin={margin}%")

    print("\n== Discount rate by channel (over-discounting leak) ==")
    for ch, pct in conn.execute("""
        SELECT o.channel, ROUND(100.0*SUM(oi.quantity*oi.unit_price*oi.discount)
                                / SUM(oi.quantity*oi.unit_price), 1)
        FROM order_items oi JOIN orders o ON oi.order_id = o.order_id
        GROUP BY o.channel ORDER BY 2 DESC
    """).fetchall():
        print(f"  {ch:<10} {pct}%")

    print("\n== Return rate by category (return leak) ==")
    for cat, pct in conn.execute("""
        SELECT p.category, ROUND(100.0*COUNT(r.return_id)/COUNT(oi.order_item_id), 1)
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN returns r ON r.order_item_id = oi.order_item_id
        GROUP BY p.category ORDER BY 2 DESC
    """).fetchall():
        print(f"  {cat:<12} {pct}%")

    print("\n== LTV : CAC by acquisition channel (spend misallocation) ==")
    for ch, ltv, cac, ratio in conn.execute("""
        WITH spend AS (SELECT channel, SUM(spend) s FROM marketing_spend GROUP BY channel),
             cust  AS (SELECT acquisition_channel ch, COUNT(*) n FROM customers GROUP BY acquisition_channel),
             gp    AS (SELECT c.acquisition_channel ch,
                              SUM(oi.quantity*oi.unit_price*(1-oi.discount)-oi.quantity*p.unit_cost) g
                       FROM customers c
                       JOIN orders o ON o.customer_id = c.customer_id
                       JOIN order_items oi ON oi.order_id = o.order_id
                       JOIN products p ON oi.product_id = p.product_id
                       GROUP BY c.acquisition_channel)
        SELECT gp.ch, ROUND(gp.g/cust.n, 0), ROUND(spend.s/cust.n, 0),
               ROUND((gp.g/cust.n)/(spend.s/cust.n), 2)
        FROM gp JOIN cust ON gp.ch = cust.ch JOIN spend ON spend.channel = gp.ch
        ORDER BY 4 DESC
    """).fetchall():
        print(f"  {ch:<10} LTV=${ltv:>5}  CAC=${cac:>4}  LTV:CAC={ratio}")
    conn.close()


def main() -> None:
    rng = random.Random(SEED)
    data = build(rng)
    for name in TABLES:
        write_csv(name, data[name])
    for f in sorted(OUT.glob("*.csv")):
        n = sum(1 for _ in f.open(encoding="utf-8")) - 1
        print(f"{f.name}: {n} rows")
    build_sqlite(data)
    story_check()


if __name__ == "__main__":
    main()


