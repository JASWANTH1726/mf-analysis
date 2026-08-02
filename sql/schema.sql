-- bluestock_mf.db — star schema
-- Day 2: SQLite database design

PRAGMA foreign_keys = ON;

-- ── dimension tables ──────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS dim_fund (
    scheme_code     INTEGER PRIMARY KEY,
    scheme_name     TEXT    NOT NULL,
    fund_house      TEXT    NOT NULL,
    category        TEXT,
    sub_category    TEXT,
    risk_grade      TEXT,
    scheme_type     TEXT,
    launch_date     TEXT,
    benchmark       TEXT,
    exit_load_pct   REAL    DEFAULT 0.0,
    min_sip         INTEGER DEFAULT 500
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id         INTEGER PRIMARY KEY,   -- YYYYMMDD
    date            TEXT    NOT NULL UNIQUE,
    year            INTEGER,
    quarter         INTEGER,
    month           INTEGER,
    month_name      TEXT,
    week            INTEGER,
    day_of_week     TEXT,
    is_weekend      INTEGER DEFAULT 0
);

-- ── fact tables ───────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS fact_nav (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code     INTEGER NOT NULL REFERENCES dim_fund(scheme_code),
    date            TEXT    NOT NULL,
    nav             REAL    NOT NULL CHECK (nav > 0),
    UNIQUE (scheme_code, date)
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    txn_id          TEXT    PRIMARY KEY,
    scheme_code     INTEGER NOT NULL REFERENCES dim_fund(scheme_code),
    txn_date        TEXT    NOT NULL,
    txn_type        TEXT    NOT NULL CHECK (txn_type IN ('SIP', 'Lumpsum', 'Redemption')),
    amount          REAL    NOT NULL CHECK (amount > 0),
    units           REAL,
    nav             REAL,
    investor_id     TEXT,
    state           TEXT,
    kyc_status      TEXT    CHECK (kyc_status IN ('KYC_VERIFIED', 'KYC_PENDING', 'KYC_REJECTED')),
    folio_no        TEXT
);

CREATE TABLE IF NOT EXISTS fact_performance (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code     INTEGER NOT NULL REFERENCES dim_fund(scheme_code),
    period          TEXT    NOT NULL,
    ret_1m          REAL,
    ret_3m          REAL,
    ret_6m          REAL,
    ret_1y          REAL,
    expense_ratio   REAL    CHECK (expense_ratio BETWEEN 0.1 AND 2.5),
    benchmark_ret   REAL,
    alpha           REAL,
    UNIQUE (scheme_code, period)
);

CREATE TABLE IF NOT EXISTS fact_aum (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code     INTEGER NOT NULL REFERENCES dim_fund(scheme_code),
    month           TEXT    NOT NULL,
    aum_cr          REAL    CHECK (aum_cr > 0),
    folios          INTEGER,
    UNIQUE (scheme_code, month)
);

-- indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_nav_code_date   ON fact_nav(scheme_code, date);
CREATE INDEX IF NOT EXISTS idx_txn_date        ON fact_transactions(txn_date);
CREATE INDEX IF NOT EXISTS idx_txn_type        ON fact_transactions(txn_type);
CREATE INDEX IF NOT EXISTS idx_perf_code       ON fact_performance(scheme_code);
CREATE INDEX IF NOT EXISTS idx_aum_month       ON fact_aum(month);
