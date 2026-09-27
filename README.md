# Metabase Retail Analytics — "Fix the Profit Leak"

A complete Metabase dashboard project: synthetic e-commerce data → **Postgres** →
**Metabase**, built around a business story with recommendations (not just charts).

## What's here
| File | Purpose |
|---|---|
| `data/*.csv` | 6 clean tables (customers, products, orders, order_items, returns, marketing_spend) |
| `sql/cards.sql` | 18 dashboard questions (native SQL), each labeled with page + viz |
| `sql/schema_postgres.sql` | the data model (DDL) |
| `generate_data.py` | regenerate the data + a story sanity check |
| `validate_sql.py` | run every card against SQLite (no Metabase needed) |
| `load_data.py` | load the CSVs into Postgres |
| `create_dashboard.py` | create all cards + the dashboard via the Metabase API |
| `docker-compose.yml` | Metabase + Postgres |
| `STORY.md` | the narrative, insights, and recommendations |

## The story (one line)
Revenue is up, margin is down — the dashboard finds **three leaks** (over-discounting,
returns, misallocated ad spend) and quantifies the fix. Full narrative: `STORY.md`.

## Setup (~10 minutes)
1. **Generate data** (or use the committed CSVs):
   ```powershell
   python generate_data.py
   ```
2. **Start Metabase + Postgres:**
   ```powershell
   docker compose up -d
   ```
3. **Load data into Postgres:**
   ```powershell
   pip install -r requirements.txt
   python load_data.py
   ```
4. **Connect Metabase** — open http://localhost:3000, create your admin account, then
   *Admin → Databases → Add database* → PostgreSQL:
   - Host `postgres` (or `localhost`), Port `5432`, DB `retail`, user `metabase`, password `metabase`.
5. **Build the dashboard** — either:
   - **Auto** (creates cards + dashboard via the API):
     ```powershell
     python create_dashboard.py --email you@example.com --password YOUR_PASSWORD --database 2
     ```
   - **Manual:** for each block in `sql/cards.sql` → *New → SQL question* → paste → save,
     then add them to a dashboard (see the `[viz]` tag in each header for the chart type).

## Preview without Metabase
```powershell
python validate_sql.py   # prints every card's result from retail.db (SQLite)
```

## Data model (star schema)
- **Dimensions:** `customers`, `products`
- **Facts:** `orders`, `order_items`, `returns`, `marketing_spend`
- Pre-computed `*_month` columns keep the dashboard SQL simple and portable across
  Postgres / SQLite / Metabase.

## Key findings (from the validated data)
- Margin fell **41.6% → 38.7%** while revenue grew 250× over the period.
- **Discount leak:** Social/Display ~37% vs ~15% elsewhere.
- **Return leak:** Apparel 25.3% (size/fit), Home Decor 17% (damaged).
- **Spend leak:** LTV:CAC = Email 16×, Organic 10× … but Social 0.6× and Display 0.5×.
