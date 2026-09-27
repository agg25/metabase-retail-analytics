# Findings, Problems, Recommendations & Future Growth

> Dashboard: **"Fix the Profit Leak"** — a Metabase dashboard over synthetic retail
> e-commerce data. Every number below comes from the validated SQL in `sql/cards.sql`.

---

## 1. Executive summary

Revenue grew strongly over the period, but **gross margin quietly shrank**. The dashboard
traces the gap to **three leaks** — over-discounting, rising returns, and misallocated
acquisition spend — and quantifies the fix. In short: *the business is selling more and
keeping less, and two acquisition channels are actively destroying value.*

---

## 2. Findings

| Metric | Value |
|---|---|
| Total revenue | **$528,385** |
| COGS | $317,670 |
| Gross profit | **$210,715** |
| Gross margin | **39.9%** (falling) |
| Customers | 1,500 |
| Orders | 2,387 |
| Repeat rate | 34.3% |

**Revenue vs. margin trend:** revenue rose from **$307/month** (Jan 2023) to **$77,096/month**
(Dec 2024), while gross margin fell from **41.6%** (Jul 2023) to **38.7%** (Dec 2024).

### Finding A — Over-discounting is channel-driven
Discount rate by acquisition channel:

| Channel | Discount rate |
|---|---|
| Social | **37.3%** |
| Display | **36.7%** |
| Email | 15.5% |
| Organic | 15.4% |
| Referral | 15.3% |

Social and Display are discounted **~2.4× more** than every other channel.

### Finding B — Returns are category-driven
Return rate by category:

| Category | Return rate |
|---|---|
| Apparel | **25.3%** (size/fit) |
| Home Decor | **17.0%** (damaged) |
| Kitchen | 11.9% |
| Bed & Bath | 9.9% |
| Accessories | 8.6% |

### Finding C — Acquisition spend is misallocated (LTV : CAC)
| Channel | LTV | CAC | LTV:CAC |
|---|---|---|---|
| Email | $172 | $11 | **16.0** |
| Organic | $178 | $17 | **10.4** |
| Referral | $153 | $23 | **6.8** |
| Social | $41 | $66 | **0.6** |
| Display | $45 | $95 | **0.5** |

Social and Display cost **more to acquire than the customer is worth** (LTV:CAC < 1),
while Email, Organic and Referral are highly profitable.

### Finding D — The margin bridge
| Leak | Amount |
|---|---|
| Discounts given away | **$124,016** |
| Refunds | **$79,617** |
| **Total leaked** | **~$204k ≈ 38% of gross profit** |

### Finding E — Customer concentration
The **top 20% of customers drive 47.6% of revenue** — a concentration risk worth managing.

---

## 3. Problems identified

1. **Discount leakage** — Social/Display promotions are eroding margin without a
   compensating increase in customer quality.
2. **Return leakage** — Apparel (fit) and Home Decor (damage) have return rates far above
   the portfolio average, generating refunds and operational cost.
3. **Negative unit economics** — Social and Display customers are unprofitable on a
   unit basis (LTV:CAC 0.5–0.6); every dollar spent there destroys ~$0.40–0.50 of value.
4. **Weak repeat behavior in paid channels** — repeat rate is 43.7% (Organic) vs 13.5%
   (Display), so the expensive channels acquire one-and-done buyers.
5. **Concentration risk** — nearly half of revenue sits with the top fifth of customers.

---

## 4. Recommendations

1. **Cap discounting on Social/Display** (37% → ~15%) — the single highest-leverage margin
   fix, with minimal expected revenue loss given the weak LTV of those customers.
2. **Fix Apparel fit and Home Decor packaging** — the two return drivers; a fit guide and
   better packaging directly cut the $79k refund leak.
3. **Reallocate acquisition budget** toward Email / Organic / Referral (LTV:CAC 6.8–16×)
   and away from Display/Social, or renegotiate those channels' unit costs.
4. **Launch a retention program** for the high-value cohort (top 20% of customers) to lift
   the 34% repeat rate and reduce concentration risk.
5. **Introduce a margin guardrail** — an alert when blended discount rate or return rate
   passes a threshold, so the leak is caught in weeks, not quarters.

**Target model:** blended margin back above **~44%**, and **LTV:CAC ≥ 3** on every channel.

---

## 5. Future growth ideas

**Analytics maturity**
- **Forecasting** — time-series models (Prophet/ARIMA) to project revenue & margin under
  different discount/return scenarios.
- **ML risk & value models** — churn prediction, LTV prediction, and an anomaly detector
  flagging abnormal discount/return patterns automatically.
- **Drill-down depth** — SKU-level and (for multi-store) location-level analysis.

**Data & automation**
- **Real-time ingestion** — stream orders/returns into the warehouse (e.g. CDC, Kafka)
  so the dashboard is always live, not batch-refreshed.
- **Alerting** — threshold-based alerts (Slack/email) for margin, return rate, and
  LTV:CAC breaches.
- **More sources** — inventory/supplier cost, web analytics, and support tickets to
  enrich the story (e.g. link complaints to return reasons).

**Product & reach**
- **Recreate in Power BI** (same star schema, DAX measures) to cover the most
  in-demand BI tool.
- **Build the wider portfolio** — HR attrition, finance P&L vs budget, logistics/delivery,
  and marketing-funnel dashboards, each with its own data source + ingestion pattern.
