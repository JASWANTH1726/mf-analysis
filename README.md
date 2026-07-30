# Mutual Fund Analysis — India

End-to-end data pipeline and analysis project covering 20 AMFI-registered mutual fund schemes across 10 fund houses. Built using Python, pandas, and live data from mfapi.in.

## What this project does

- Pulls live NAV data for 6 large-cap schemes directly from the MFAPI
- Loads and validates 10 structured datasets covering fund metadata, NAV history, portfolio holdings, SIP records, returns, AUM, expense ratios, fund managers, benchmarks, and risk metrics
- Validates AMFI scheme code coverage across datasets
- Lays the groundwork for returns analysis, risk profiling, and fund comparison

## Project structure

```
mf_analysis/
├── data/
│   ├── raw/              # source CSVs — generated + live fetched
│   └── processed/        # cleaned/transformed data (future)
├── notebooks/            # exploratory analysis
├── sql/                  # queries for structured analysis
├── dashboard/            # visualisation outputs
├── reports/              # final reports
├── data_ingestion.py     # loads all CSVs, explores fund_master, checks AMFI coverage
├── live_nav_fetch.py     # fetches live NAV from mfapi.in for 6 schemes
├── generate_datasets.py  # generates the 10 synthetic base datasets
└── requirements.txt
```

## Datasets

| File | Rows | Description |
|---|---|---|
| fund_master.csv | 20 | Scheme metadata — fund house, category, risk grade, benchmark |
| nav_history.csv | 10,000 | Daily NAV for 20 schemes from 2015–2024 |
| portfolio_holdings.csv | 200 | Top 10 stock holdings per scheme |
| sip_data.csv | 600 | Monthly SIP transactions Jan 2020–Dec 2024 |
| returns_data.csv | 20 | 1m/3m/6m/1y/3y/5y/inception returns |
| benchmark_data.csv | 500 | Nifty 50, Nifty 100, BSE 500, Nifty Midcap index values |
| aum_data.csv | 720 | Monthly AUM and folio count 2022–2024 |
| expense_ratio.csv | 20 | Direct vs regular plan TER |
| fund_manager.csv | 20 | Manager name, experience, qualification |
| risk_metrics.csv | 20 | Std dev, beta, Sharpe, alpha, R², Sortino |

Live NAV CSVs fetched from [mfapi.in](https://mfapi.in):
- HDFC Top 100 Direct (125497)
- SBI Bluechip (119551)
- ICICI Bluechip (120503)
- Nippon Large Cap (118632)
- Axis Bluechip (119092)
- Kotak Bluechip (120841)

## Setup

```bash
git clone https://github.com/JASWANTH1726/mf-analysis.git
cd mf-analysis
pip install -r requirements.txt
```

## Running

Generate the base datasets:
```bash
python generate_datasets.py
```

Load and explore all CSVs:
```bash
python data_ingestion.py
```

Fetch latest live NAV:
```bash
python live_nav_fetch.py
```

## Dependencies

```
pandas, numpy, matplotlib, seaborn, plotly, sqlalchemy, requests, scipy, jupyter
```

## Data notes

- All dates follow `DD-MM-YYYY` format (AMFI standard)
- NAV history uses a geometric random walk seeded at 10.0 — directionally realistic but synthetic
- Live NAV from mfapi.in may return scheme names that don't match the label in fund_master — AMFI codes map to specific scheme variants (direct/regular, growth/IDCW) so always verify the `scheme_name` field from the API response
- AMFI code coverage: 100% — all 20 master codes have corresponding NAV history

## Data sources

- Live NAV: [mfapi.in](https://mfapi.in) — free, no auth required
- AMFI scheme codes: [amfiindia.com](https://www.amfiindia.com)
