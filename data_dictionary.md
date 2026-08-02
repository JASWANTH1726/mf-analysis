# Data Dictionary — bluestock_mf.db

Last updated: Day 2 | Source: AMFI / mfapi.in / synthetic

---

## dim_fund

Master dimension for all mutual fund schemes.

| Column | Type | Description | Example |
|---|---|---|---|
| scheme_code | INTEGER (PK) | Unique 6-digit AMFI-assigned scheme identifier | 125497 |
| scheme_name | TEXT | Full scheme name as registered with AMFI | HDFC Top 100 Fund Direct Growth |
| fund_house | TEXT | Asset Management Company name | HDFC Mutual Fund |
| category | TEXT | SEBI category — Equity / Debt / Hybrid / Solution Oriented / Other | Equity |
| sub_category | TEXT | SEBI sub-category within the category | Large Cap |
| risk_grade | TEXT | Risk level — Low / Moderate / Moderately High / High / Very High | Moderately High |
| scheme_type | TEXT | Open Ended / Close Ended / Interval | Open Ended |
| launch_date | TEXT | Date scheme was launched (DD-MM-YYYY) | 01-01-2013 |
| benchmark | TEXT | Index used as performance benchmark | Nifty 100 |
| exit_load_pct | REAL | Exit load percentage charged on redemption | 1.0 |
| min_sip | INTEGER | Minimum SIP amount in INR | 500 |

---

## dim_date

Date dimension for time-based analysis.

| Column | Type | Description | Example |
|---|---|---|---|
| date_id | INTEGER (PK) | Date in YYYYMMDD integer format | 20240115 |
| date | TEXT (UNIQUE) | ISO date string YYYY-MM-DD | 2024-01-15 |
| year | INTEGER | Calendar year | 2024 |
| quarter | INTEGER | Quarter of year (1–4) | 1 |
| month | INTEGER | Month number (1–12) | 1 |
| month_name | TEXT | Abbreviated month name | Jan |
| week | INTEGER | ISO week number | 3 |
| day_of_week | TEXT | Full day name | Monday |
| is_weekend | INTEGER | 1 if Saturday or Sunday, else 0 | 0 |

---

## fact_nav

Daily NAV (Net Asset Value) for each scheme. Forward-filled for holidays and weekends.

| Column | Type | Description | Example |
|---|---|---|---|
| id | INTEGER (PK) | Auto-increment surrogate key | 1 |
| scheme_code | INTEGER (FK) | References dim_fund.scheme_code | 125497 |
| date | TEXT | NAV date in YYYY-MM-DD format | 2024-07-24 |
| nav | REAL | Net Asset Value in INR, must be > 0 | 204.8535 |

Notes:
- Unique constraint on (scheme_code, date)
- Missing dates (holidays, weekends) are forward-filled from last known NAV
- Source: mfapi.in for live schemes, synthetic random walk for others

---

## fact_transactions

Investor-level buy/sell/SIP transactions.

| Column | Type | Description | Example |
|---|---|---|---|
| txn_id | TEXT (PK) | Unique transaction identifier | TXN100042 |
| scheme_code | INTEGER (FK) | References dim_fund.scheme_code | 119551 |
| txn_date | TEXT | Transaction date YYYY-MM-DD | 2023-03-15 |
| txn_type | TEXT | SIP / Lumpsum / Redemption | SIP |
| amount | REAL | Transaction amount in INR, must be > 0 | 5000.00 |
| units | REAL | Units allotted or redeemed | 24.3812 |
| nav | REAL | NAV at time of transaction | 205.07 |
| investor_id | TEXT | Anonymised investor identifier | INV4821 |
| state | TEXT | Investor's state of residence | Maharashtra |
| kyc_status | TEXT | KYC_VERIFIED / KYC_PENDING / KYC_REJECTED | KYC_VERIFIED |
| folio_no | TEXT | Unique folio number for the investor-scheme pair | FOLIO482910 |

Notes:
- txn_type standardised from raw variants (sip → SIP, LUMP SUM → Lumpsum)
- Rows with amount <= 0 removed during cleaning
- kyc_status non-standard values mapped to KYC_PENDING

---

## fact_performance

Quarterly scheme performance metrics.

| Column | Type | Description | Example |
|---|---|---|---|
| id | INTEGER (PK) | Auto-increment surrogate key | 1 |
| scheme_code | INTEGER (FK) | References dim_fund.scheme_code | 120503 |
| period | TEXT | Quarter start month in Mon-YYYY format | Jan-2024 |
| ret_1m | REAL | 1-month trailing return (%) | 2.34 |
| ret_3m | REAL | 3-month trailing return (%) | 7.12 |
| ret_6m | REAL | 6-month trailing return (%) | 11.45 |
| ret_1y | REAL | 1-year trailing return (%) | 18.92 |
| expense_ratio | REAL | Total Expense Ratio (%), range 0.1–2.5 | 0.85 |
| benchmark_ret | REAL | Benchmark index return for same period (%) | 15.30 |
| alpha | REAL | Excess return over benchmark (%) | 3.62 |

Notes:
- Non-numeric return values coerced to NaN and dropped
- ret_1y outliers (> 3 std devs) capped at mean ± 3σ
- expense_ratio clipped to [0.1, 2.5] per SEBI regulations

---

## fact_aum

Monthly Assets Under Management per scheme.

| Column | Type | Description | Example |
|---|---|---|---|
| id | INTEGER (PK) | Auto-increment surrogate key | 1 |
| scheme_code | INTEGER (FK) | References dim_fund.scheme_code | 118632 |
| month | TEXT | Month in YYYY-MM format | 2024-03 |
| aum_cr | REAL | AUM in Indian Crores (₹), must be > 0 | 12450.75 |
| folios | INTEGER | Number of active investor folios | 284921 |

Notes:
- Unique constraint on (scheme_code, month)
- 1 Crore = 10 million INR

---

## Cleaned CSV files (data/processed/)

| File | Source | Rows | Key changes |
|---|---|---|---|
| nav_history_clean.csv | nav_history.csv | 69,880 | Dates parsed, forward-filled, sorted |
| investor_transactions_clean.csv | investor_transactions.csv | 1,998 | txn_type standardised, bad dates/amounts removed |
| scheme_performance_clean.csv | scheme_performance.csv | 399 | Non-numeric coerced, outliers capped, TER clipped |
| fund_master_clean.csv | fund_master.csv | 20 | launch_date parsed to datetime |
| aum_data_clean.csv | aum_data.csv | 720 | month parsed to datetime |
| returns_data_clean.csv | returns_data.csv | 20 | as_of parsed to datetime |
| risk_metrics_clean.csv | risk_metrics.csv | 20 | as_of parsed to datetime |
| expense_ratio_clean.csv | expense_ratio.csv | 20 | effective_date parsed to datetime |
| portfolio_holdings_clean.csv | portfolio_holdings.csv | 200 | as_of parsed, zero-weight rows removed |
| benchmark_data_clean.csv | benchmark_data.csv | 500 | date parsed to datetime |

---

## Data sources

| Source | URL | Auth |
|---|---|---|
| mfapi.in | https://api.mfapi.in/mf/{scheme_code} | None |
| AMFI India | https://www.amfiindia.com | None |
| Synthetic data | generate_datasets.py | N/A |
