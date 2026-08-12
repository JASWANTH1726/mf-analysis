CREATE TABLE IF NOT EXISTS dim_fund (
    scheme_code INTEGER PRIMARY KEY,
    scheme_name TEXT,
    fund_house TEXT,
    category TEXT,
    sub_category TEXT,
    risk_grade TEXT,
    scheme_type TEXT,
    launch_date TEXT,
    benchmark TEXT,
    exit_load_pct REAL,
    min_sip REAL
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id INTEGER PRIMARY KEY,
    date TEXT,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name TEXT,
    week INTEGER,
    day_of_week TEXT,
    is_weekend INTEGER
);

CREATE TABLE IF NOT EXISTS fact_nav (
    scheme_code INTEGER,
    date TEXT,
    nav REAL,
    FOREIGN KEY(scheme_code) REFERENCES dim_fund(scheme_code)
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    txn_id TEXT PRIMARY KEY,
    scheme_code INTEGER,
    txn_date TEXT,
    txn_type TEXT,
    amount REAL,
    units REAL,
    nav REAL,
    investor_id TEXT,
    state TEXT,
    kyc_status TEXT,
    folio_no TEXT,
    FOREIGN KEY(scheme_code) REFERENCES dim_fund(scheme_code)
);

CREATE TABLE IF NOT EXISTS fact_performance (
    scheme_code INTEGER,
    period TEXT,
    ret_1m REAL,
    ret_3m REAL,
    ret_6m REAL,
    ret_1y REAL,
    expense_ratio REAL,
    benchmark_ret REAL,
    alpha REAL,
    FOREIGN KEY(scheme_code) REFERENCES dim_fund(scheme_code)
);

CREATE TABLE IF NOT EXISTS fact_aum (
    scheme_code INTEGER,
    month TEXT,
    aum_cr REAL,
    folios INTEGER,
    FOREIGN KEY(scheme_code) REFERENCES dim_fund(scheme_code)
);
