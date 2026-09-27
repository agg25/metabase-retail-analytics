"""Preview every dashboard card against retail.db (SQLite) without Metabase.

Run after `python generate_data.py`:

    python validate_sql.py
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path


def main() -> None:
    text = Path("sql/cards.sql").read_text(encoding="utf-8")
    parts = re.split(r"(?m)^-- CARD:", text)
    conn = sqlite3.connect("retail.db")
    for part in parts[1:]:
        lines = part.splitlines()
        title = lines[0].strip()
        query = "\n".join(ln for ln in lines[1:] if ln.strip() and not ln.strip().startswith("--"))
        print(f"\n### {title}")
        try:
            cur = conn.execute(query)
            cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
            print("  " + " | ".join(cols))
            for row in rows[:6]:
                print("  " + " | ".join(str(v) for v in row))
            if len(rows) > 6:
                print(f"  ... ({len(rows)} rows total)")
        except Exception as exc:  # keep going if one card fails
            print(f"  ERROR: {exc}")
    conn.close()


if __name__ == "__main__":
    main()
