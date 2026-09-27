-- ============================================================================
-- Retail analytics — Metabase dashboard cards (portable SQL)
-- Each block below is one Metabase "question" (native query). Copy the SQL
-- into a question, or use create_dashboard.py to push all of them via the API.
-- Works in Postgres (recommended), SQLite (validation), and Metabase's app DB.
-- ============================================================================

-- CARD: [number] PAGE 1 · THE PROBLEM · Total revenue
SELECT ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 0) AS total_revenue
FROM order_items oi;

-- CARD: [number] PAGE 1 · THE PROBLEM · Gross profit & margin
SELECT
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 0) AS revenue,
    ROUND(SUM(oi.quantity * p.unit_cost), 0) AS cogs,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount) - oi.quantity * p.unit_cost), 0) AS gross_profit,
    ROUND(100.0 * SUM(oi.quantity * oi.unit_price * (1 - oi.discount) - oi.quantity * p.unit_cost)
          / SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 1) AS gross_margin_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id;

-- CARD: [number] PAGE 1 · THE PROBLEM · Customers
SELECT COUNT(*) AS customers FROM customers;

-- CARD: [number] PAGE 1 · THE PROBLEM · Orders
SELECT COUNT(*) AS orders FROM orders;

-- CARD: [number] PAGE 1 · THE PROBLEM · Repeat rate
SELECT ROUND(100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS repeat_rate_pct
FROM (SELECT customer_id, COUNT(*) AS order_count FROM orders GROUP BY customer_id);

-- CARD: [line] PAGE 1 · THE PROBLEM · Revenue vs gross profit by month
SELECT o.order_month,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 0) AS revenue,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount) - oi.quantity * p.unit_cost), 0) AS gross_profit
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY o.order_month
ORDER BY o.order_month;

-- CARD: [line] PAGE 1 · THE PROBLEM · Discount rate by month
SELECT o.order_month,
       ROUND(100.0 * SUM(oi.quantity * oi.unit_price * oi.discount)
             / SUM(oi.quantity * oi.unit_price), 1) AS discount_pct
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
GROUP BY o.order_month
ORDER BY o.order_month;

-- CARD: [bar] PAGE 2 · DIAGNOSIS · Discount rate by channel
SELECT o.channel,
       ROUND(100.0 * SUM(oi.quantity * oi.unit_price * oi.discount)
             / SUM(oi.quantity * oi.unit_price), 1) AS discount_pct
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
GROUP BY o.channel
ORDER BY discount_pct DESC;

-- CARD: [bar] PAGE 2 · DIAGNOSIS · Discount rate by category
SELECT p.category,
       ROUND(100.0 * SUM(oi.quantity * oi.unit_price * oi.discount)
             / SUM(oi.quantity * oi.unit_price), 1) AS discount_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY discount_pct DESC;

-- CARD: [bar] PAGE 2 · DIAGNOSIS · Return rate by category
SELECT p.category,
       ROUND(100.0 * COUNT(r.return_id) / COUNT(oi.order_item_id), 1) AS return_rate_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN returns r ON r.order_item_id = oi.order_item_id
GROUP BY p.category
ORDER BY return_rate_pct DESC;

-- CARD: [table] PAGE 2 · DIAGNOSIS · Return reasons & refund $
SELECT reason, COUNT(*) AS returns, ROUND(SUM(refund_amount), 0) AS refunded
FROM returns
GROUP BY reason
ORDER BY returns DESC;

-- CARD: [line] PAGE 2 · DIAGNOSIS · Refund $ by month
SELECT substr(r.return_date, 1, 7) AS month, ROUND(SUM(r.refund_amount), 0) AS refunded
FROM returns r
GROUP BY substr(r.return_date, 1, 7)
ORDER BY month;

-- CARD: [bar] PAGE 3 · CUSTOMER ECONOMICS · CAC by channel
WITH spend AS (SELECT channel, SUM(spend) AS total_spend FROM marketing_spend GROUP BY channel),
     cust  AS (SELECT acquisition_channel AS channel, COUNT(*) AS n FROM customers GROUP BY acquisition_channel)
SELECT cust.channel,
       ROUND(spend.total_spend, 0) AS total_spend,
       cust.n AS new_customers,
       ROUND(spend.total_spend / cust.n, 0) AS cac
FROM cust
JOIN spend ON spend.channel = cust.channel
ORDER BY cac DESC;

-- CARD: [bar] PAGE 3 · CUSTOMER ECONOMICS · LTV by channel
SELECT c.acquisition_channel AS channel,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount) - oi.quantity * p.unit_cost)
             / COUNT(DISTINCT c.customer_id), 0) AS ltv
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY c.acquisition_channel
ORDER BY ltv DESC;

-- CARD: [table] PAGE 3 · CUSTOMER ECONOMICS · LTV : CAC ratio by channel
WITH spend AS (SELECT channel, SUM(spend) s FROM marketing_spend GROUP BY channel),
     cust  AS (SELECT acquisition_channel ch, COUNT(*) n FROM customers GROUP BY acquisition_channel),
     gp    AS (SELECT c.acquisition_channel ch,
                      SUM(oi.quantity * oi.unit_price * (1 - oi.discount) - oi.quantity * p.unit_cost) g
               FROM customers c
               JOIN orders o ON o.customer_id = c.customer_id
               JOIN order_items oi ON oi.order_id = o.order_id
               JOIN products p ON oi.product_id = p.product_id
               GROUP BY c.acquisition_channel)
SELECT gp.ch AS channel,
       ROUND(gp.g / cust.n, 0) AS ltv,
       ROUND(spend.s / cust.n, 0) AS cac,
       ROUND((gp.g / cust.n) / (spend.s / cust.n), 2) AS ltv_cac_ratio
FROM gp
JOIN cust ON gp.ch = cust.ch
JOIN spend ON spend.channel = gp.ch
ORDER BY ltv_cac_ratio DESC;

-- CARD: [bar] PAGE 3 · CUSTOMER ECONOMICS · Repeat rate by channel
SELECT c.acquisition_channel AS channel,
       ROUND(100.0 * SUM(CASE WHEN o.order_count > 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS repeat_rate_pct
FROM customers c
JOIN (SELECT customer_id, COUNT(*) AS order_count FROM orders GROUP BY customer_id) o
  ON o.customer_id = c.customer_id
GROUP BY c.acquisition_channel
ORDER BY repeat_rate_pct DESC;

-- CARD: [pivot] PAGE 3 · CUSTOMER ECONOMICS · Cohort retention (rows=cohort, cols=active month)
SELECT c.signup_month AS cohort,
       o.order_month AS active_month,
       COUNT(DISTINCT o.customer_id) AS active_customers
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.signup_month, o.order_month
ORDER BY cohort, active_month;

-- CARD: [number] PAGE 4 · BUSINESS MODEL · Margin bridge — where profit leaks
SELECT
    ROUND(SUM(oi.quantity * oi.unit_price * oi.discount), 0) AS discount_given,
    ROUND(SUM(r.refund_amount), 0) AS refund_given
FROM order_items oi
LEFT JOIN returns r ON r.order_item_id = oi.order_item_id;

-- CARD: [number] PAGE 4 · BUSINESS MODEL · Revenue concentration (top 20% of customers)
WITH rev AS (
    SELECT o.customer_id, SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY o.customer_id
),
ranked AS (
    SELECT revenue, ROW_NUMBER() OVER (ORDER BY revenue DESC) AS rn, COUNT(*) OVER () AS total
    FROM rev
)
SELECT ROUND(100.0 * SUM(CASE WHEN rn <= total * 0.2 THEN revenue ELSE 0 END) / SUM(revenue), 1)
       AS top_20_pct_share
FROM ranked;

