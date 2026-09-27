"""Create every dashboard card in Metabase via its REST API (free edition).

Prereqs (see README):
  1. Metabase running, admin account created, and the Postgres 'retail' DB connected.
  2. `pip install -r requirements.txt`

Usage:
  python create_dashboard.py --url http://localhost:3000 \
      --email you@example.com --password YOUR_PASSWORD --database 2

The --database value is the internal id of the connected database
(Admin -> Databases -> the id in the URL, e.g. /admin/databases/2).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import requests

DISPLAY = {
    "number": "scalar",
    "line": "line",
    "bar": "bar",
    "table": "table",
    "pivot": "table",
}


def parse_cards() -> list[tuple[str, str]]:
    text = Path("sql/cards.sql").read_text(encoding="utf-8")
    parts = re.split(r"(?m)^-- CARD:", text)
    cards: list[tuple[str, str]] = []
    for part in parts[1:]:
        lines = part.splitlines()
        title = lines[0].strip()
        query = "\n".join(l for l in lines[1:] if l.strip() and not l.strip().startswith("--"))
        cards.append((title, query))
    return cards


def viz_for(title: str) -> str:
    m = re.match(r"\[(\w+)\]", title)
    return DISPLAY.get(m.group(1) if m else "", "table")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:3000")
    ap.add_argument("--email", default="admin@metabase.local")
    ap.add_argument("--password", default="")
    ap.add_argument("--database", type=int, required=True)
    ap.add_argument("--dashboard", default="Retail: Fix the Profit Leak")
    args = ap.parse_args()

    s = requests.Session()
    r = s.post(f"{args.url}/api/session", json={"username": args.email, "password": args.password})
    r.raise_for_status()
    s.headers["X-Metabase-Session"] = r.json()["id"]

    card_ids: list[int] = []
    for title, query in parse_cards():
        payload = {
            "name": title,
            "display": viz_for(title),
            "dataset_query": {
                "database": args.database,
                "type": "native",
                "native": {"query": query, "template_tags": {}},
            },
            "visualization_settings": {},
        }
        card = s.post(f"{args.url}/api/card", json=payload).json()
        card_ids.append(card["id"])
        print(f"card {card['id']}: {title}")

    dash = s.post(f"{args.url}/api/dashboard", json={"name": args.dashboard}).json()
    for i, card_id in enumerate(card_ids):
        s.post(f"{args.url}/api/dashboard/{dash['id']}/cards", json={
            "cardId": card_id,
            "row": (i // 2) * 4,
            "col": (i % 2) * 12,
            "sizeX": 12,
            "sizeY": 4,
        })
    print(f"\nDashboard: {args.url}/dashboard/{dash['id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
