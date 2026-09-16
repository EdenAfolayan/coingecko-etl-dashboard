-- =========================================
-- COINS: reference/dimension table
-- One row per coin, ever seen in top 100
-- Grows over time, rarely updated otherwise
-- =========================================
CREATE TABLE coins (
    coin_id     VARCHAR(100)  PRIMARY KEY,   -- CoinGecko's id, e.g. 'bitcoin'
    symbol      VARCHAR(20)  NOT NULL,
    name        VARCHAR(100) NOT NULL,
    image_url   TEXT,
    first_seen  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    last_seen   TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- =========================================
-- COIN_MARKET_DATA: fact table
-- One row per coin per timestamp
-- Fed by BOTH live pulls and backfill
-- =========================================
CREATE TABLE coin_market_data (
    id                     BIGSERIAL PRIMARY KEY,
    coin_id                VARCHAR(100) NOT NULL REFERENCES coins(coin_id),
    price_usd              NUMERIC(24,8),
    market_cap_usd         NUMERIC(28,2),
    volume_24h_usd         NUMERIC(28,2),
    price_change_24h_pct   NUMERIC(10,4),      -- NULL for backfilled rows
    market_cap_rank        INT,                 -- NULL for backfilled rows
    pulled_at              TIMESTAMPTZ NOT NULL,
    source                 VARCHAR(10) NOT NULL DEFAULT 'live'
                               CHECK (source IN ('live', 'backfill')),

    -- prevents the exact same coin+timestamp+source combo twice
    -- (protects you if a script accidentally runs twice, or backfill re-runs)
    UNIQUE (coin_id, pulled_at, source)
);

-- =========================================
-- INDEXES
-- Your line-chart query filters by coin_id
-- and sorts/ranges by pulled_at — this is
-- exactly what this composite index speeds up
-- =========================================
CREATE INDEX idx_market_data_coin_time
    ON coin_market_data (coin_id, pulled_at);