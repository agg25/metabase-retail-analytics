# The Business Story: "Fix the Profit Leak"

This dashboard is built around **one question and a decision**, not a pile of charts.

## The problem
Revenue is growing, but gross margin is quietly shrinking:

- Revenue grows from **$307/month** (Jan 2023) to **$77,096/month** (Dec 2024).
- Gross margin falls from **41.6%** (Jul 2023) to **38.7%** (Dec 2024).
- Full period: **$528,385** revenue → **$210,715** gross profit → **39.9%** margin, drifting down.

So the headline is: *"We're selling more and keeping less."* The dashboard's job is to
find the leak and put a dollar number on the fix.

## Diagnosis — three leaks
1. **Over-discounting (channel-driven)** — discount rate by channel:
   - Social **37.3%**, Display **36.7%** vs Organic **15.4%**, Email **15.5%**, Referral **15.3%**.
2. **Rising returns (category-driven)** — return rate by category:
   - Apparel **25.3%** (size/fit), Home Decor **17.0%** (damaged) vs ~9% elsewhere.
3. **Misallocated acquisition spend** — LTV:CAC ratio:
   - Email **16.0×**, Organic **10.4×**, Referral **6.8×** — but Social **0.6×**, Display **0.5×**
     (losing money on every customer acquired there).

The **margin bridge** quantifies it: **$124,016** given away in discounts and **$79,617**
lost to refunds — together ~38% of gross profit.

## Insight → recommendation → value
| Finding | Recommendation | Expected impact |
|---|---|---|
| Social & Display are discounted 2.4× more | Cap discounts on those channels | margin up ~2–3 pts |
| Apparel returns 25.3% (size/fit) | Fix sizing charts + fit guide | returns down |
| Social & Display LTV:CAC < 1 | Shift budget to Email / Organic / Referral | payback ↓, profit ↑ |
| Repeat rate 34% (Organic 44% vs Display 14%) | Retention program for the good cohorts | LTV ↑ |

## The business model (from the dashboard)
The dashboard computes the unit economics directly — LTV, CAC, LTV:CAC, gross margin,
repeat rate per channel. **That is the business model**, and it shows the *target* model
once the recommendations are applied:

- **Today:** blended margin 39.9%, and Social/Display LTV:CAC < 1 (value-destroying).
- **Target:** cut Social/Display discount + shift spend → margin back to ~44%+,
  LTV:CAC ≥ 3 on every channel.

## Page map (how the story flows)
1. **Page 1 — The Problem:** revenue up, margin down (KPIs + trends).
2. **Page 2 — Diagnosis:** the three leaks (discount, returns, spend).
3. **Page 3 — Customer economics:** who is actually valuable (CAC, LTV, cohorts).
4. **Page 4 — Business model & recommendations:** the numbers that justify the decision.
