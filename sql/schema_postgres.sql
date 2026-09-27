-- Postgres schema for the retail dataset. Executed by load_data.py.
DROP TABLE IF EXISTS returns CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS marketing_spend CASCADE;

CREATE TABLE customers (
    customer_id         TEXT PRIMARY KEY,
    signup_date         DATE,
    signup_month        TEXT,
    region              TEXT,
    acquisition_channel TEXT
);

CREATE TABLE products (
    product_id TEXT PRIMARY KEY,
    category   TEXT,
    unit_price NUMERIC,
    unit_cost  NUMERIC
);

CREATE TABLE orders (
    order_id    TEXT PRIMARY KEY,
    customer_id TEXT,
    order_date  DATE,
    order_month TEXT,
    channel     TEXT
);

CREATE TABLE order_items (
    order_item_id TEXT PRIMARY KEY,
    order_id      TEXT,
    product_id    TEXT,
    quantity      INT,
    unit_price    NUMERIC,
    discount      NUMERIC
);

CREATE TABLE returns (
    return_id     TEXT PRIMARY KEY,
    order_item_id TEXT,
    order_id      TEXT,
    product_id    TEXT,
    return_date   DATE,
    reason        TEXT,
    refund_amount NUMERIC
);

CREATE TABLE marketing_spend (
    spend_id TEXT PRIMARY KEY,
    month    TEXT,
    channel  TEXT,
    spend    NUMERIC
);
