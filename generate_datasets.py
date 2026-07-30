import os
import numpy as np
import pandas as pd

RAW = os.path.join(os.path.dirname(__file__), "data", "raw")
os.makedirs(RAW, exist_ok=True)

rng = np.random.default_rng(42)

SCHEME_CODES = [125497, 119551, 120503, 118632, 119092, 120841,
                118989, 120594, 119775, 118825, 120465, 119386,
                118551, 120178, 119203, 118712, 120333, 119644,
                118890, 120712]

FUND_HOUSES = ["HDFC Mutual Fund", "SBI Mutual Fund", "ICICI Prudential",
               "Nippon India", "Axis Mutual Fund", "Kotak Mahindra",
               "Mirae Asset", "DSP Mutual Fund", "Franklin Templeton", "UTI Mutual Fund"]

CATEGORIES   = ["Equity", "Debt", "Hybrid", "Solution Oriented", "Other"]
SUB_CATS     = ["Large Cap", "Mid Cap", "Small Cap", "Flexi Cap",
                "ELSS", "Liquid", "Short Duration", "Balanced Advantage"]
RISK_GRADES  = ["Low", "Moderate", "Moderately High", "High", "Very High"]
SCHEME_TYPES = ["Open Ended", "Close Ended", "Interval"]

dates = pd.date_range("2015-01-01", "2024-12-31", freq="B")

# 1. fund_master
fund_master = pd.DataFrame({
    "scheme_code":    SCHEME_CODES,
    "scheme_name":    [f"{FUND_HOUSES[i % 10]} {SUB_CATS[i % 8]} Fund Direct Growth" for i in range(20)],
    "fund_house":     [FUND_HOUSES[i % 10] for i in range(20)],
    "category":       [CATEGORIES[i % 5] for i in range(20)],
    "sub_category":   [SUB_CATS[i % 8] for i in range(20)],
    "risk_grade":     [RISK_GRADES[i % 5] for i in range(20)],
    "scheme_type":    [SCHEME_TYPES[i % 3] for i in range(20)],
    "launch_date":    pd.date_range("2010-01-01", periods=20, freq="180D").strftime("%d-%m-%Y"),
    "benchmark":      ["Nifty 50", "Nifty 100", "BSE 500", "Nifty Midcap 150", "Nifty Smallcap 250"] * 4,
    "exit_load_pct":  rng.choice([0.0, 0.5, 1.0], size=20),
    "min_sip_amount": rng.choice([500, 1000, 5000], size=20),
})
fund_master.to_csv(os.path.join(RAW, "fund_master.csv"), index=False)
print(f"fund_master        : {fund_master.shape}")

# 2. nav_history (sampled — 20 schemes x 500 dates)
sample_dates = dates[::5][:500]
nav_rows = []
for code in SCHEME_CODES:
    nav = 10.0
    for d in sample_dates:
        nav *= (1 + rng.normal(0.0004, 0.008))
        nav_rows.append({"scheme_code": code, "date": d.strftime("%d-%m-%Y"),
                         "nav": round(nav, 4)})
nav_history = pd.DataFrame(nav_rows)
nav_history.to_csv(os.path.join(RAW, "nav_history.csv"), index=False)
print(f"nav_history        : {nav_history.shape}")

# 3. portfolio_holdings (top 10 stocks per scheme)
STOCKS = ["Reliance", "HDFC Bank", "Infosys", "TCS", "ICICI Bank",
          "Kotak Bank", "L&T", "Axis Bank", "HUL", "Bajaj Finance",
          "Wipro", "SBI", "Maruti", "Asian Paints", "Titan"]
holdings_rows = []
for code in SCHEME_CODES:
    stocks = rng.choice(STOCKS, size=10, replace=False)
    weights = rng.dirichlet(np.ones(10)) * 100
    for stock, w in zip(stocks, weights):
        holdings_rows.append({"scheme_code": code, "stock_name": stock,
                               "weight_pct": round(w, 2),
                               "sector": rng.choice(["Banking", "IT", "FMCG", "Auto", "Energy"]),
                               "as_of_date": "31-12-2024"})
portfolio_holdings = pd.DataFrame(holdings_rows)
portfolio_holdings.to_csv(os.path.join(RAW, "portfolio_holdings.csv"), index=False)
print(f"portfolio_holdings : {portfolio_holdings.shape}")

# 4. sip_data
sip_dates = pd.date_range("2020-01-01", "2024-12-31", freq="MS")
sip_rows = []
for code in SCHEME_CODES[:10]:
    for d in sip_dates:
        sip_rows.append({"scheme_code": code, "sip_date": d.strftime("%d-%m-%Y"),
                         "sip_amount": rng.choice([500, 1000, 2000, 5000]),
                         "units_allotted": round(rng.uniform(5, 50), 4),
                         "nav_on_date": round(rng.uniform(20, 300), 4)})
sip_data = pd.DataFrame(sip_rows)
sip_data.to_csv(os.path.join(RAW, "sip_data.csv"), index=False)
print(f"sip_data           : {sip_data.shape}")

# 5. returns_data
returns_data = pd.DataFrame({
    "scheme_code":   SCHEME_CODES,
    "return_1m":     rng.normal(1.2, 2.5, 20).round(2),
    "return_3m":     rng.normal(3.5, 4.0, 20).round(2),
    "return_6m":     rng.normal(7.0, 6.0, 20).round(2),
    "return_1y":     rng.normal(14.0, 8.0, 20).round(2),
    "return_3y":     rng.normal(12.0, 5.0, 20).round(2),
    "return_5y":     rng.normal(13.5, 4.5, 20).round(2),
    "return_since_inception": rng.normal(15.0, 3.5, 20).round(2),
    "as_of_date":    "31-12-2024",
})
returns_data.to_csv(os.path.join(RAW, "returns_data.csv"), index=False)
print(f"returns_data       : {returns_data.shape}")

# 6. benchmark_data
bench_rows = []
for d in sample_dates:
    bench_rows.append({"date": d.strftime("%d-%m-%Y"),
                       "nifty50":      round(rng.uniform(8000, 24000), 2),
                       "nifty100":     round(rng.uniform(8500, 25000), 2),
                       "bse500":       round(rng.uniform(7000, 22000), 2),
                       "nifty_midcap": round(rng.uniform(5000, 18000), 2)})
benchmark_data = pd.DataFrame(bench_rows)
benchmark_data.to_csv(os.path.join(RAW, "benchmark_data.csv"), index=False)
print(f"benchmark_data     : {benchmark_data.shape}")

# 7. aum_data
aum_rows = []
for code in SCHEME_CODES:
    for month in pd.date_range("2022-01-01", "2024-12-31", freq="MS"):
        aum_rows.append({"scheme_code": code,
                         "month":       month.strftime("%b-%Y"),
                         "aum_cr":      round(rng.uniform(100, 50000), 2),
                         "no_of_folios": int(rng.integers(1000, 500000))})
aum_data = pd.DataFrame(aum_rows)
aum_data.to_csv(os.path.join(RAW, "aum_data.csv"), index=False)
print(f"aum_data           : {aum_data.shape}")

# 8. expense_ratio
expense_ratio = pd.DataFrame({
    "scheme_code":       SCHEME_CODES,
    "direct_expense_pct": rng.uniform(0.1, 1.0, 20).round(3),
    "regular_expense_pct": rng.uniform(0.8, 2.5, 20).round(3),
    "effective_date":    "01-01-2024",
})
expense_ratio.to_csv(os.path.join(RAW, "expense_ratio.csv"), index=False)
print(f"expense_ratio      : {expense_ratio.shape}")

# 9. fund_manager
fund_manager = pd.DataFrame({
    "scheme_code":    SCHEME_CODES,
    "manager_name":   [f"Manager_{chr(65+i)}" for i in range(20)],
    "experience_yrs": rng.integers(5, 25, 20),
    "managing_since": pd.date_range("2015-01-01", periods=20, freq="90D").strftime("%d-%m-%Y"),
    "qualification":  rng.choice(["MBA", "CFA", "CA", "MBA+CFA"], size=20),
})
fund_manager.to_csv(os.path.join(RAW, "fund_manager.csv"), index=False)
print(f"fund_manager       : {fund_manager.shape}")

# 10. risk_metrics
risk_metrics = pd.DataFrame({
    "scheme_code":   SCHEME_CODES,
    "std_dev":       rng.uniform(5, 25, 20).round(3),
    "beta":          rng.uniform(0.6, 1.4, 20).round(3),
    "sharpe_ratio":  rng.uniform(0.3, 2.5, 20).round(3),
    "alpha":         rng.uniform(-2, 5, 20).round(3),
    "r_squared":     rng.uniform(0.7, 0.99, 20).round(3),
    "sortino_ratio": rng.uniform(0.4, 3.0, 20).round(3),
    "as_of_date":    "31-12-2024",
})
risk_metrics.to_csv(os.path.join(RAW, "risk_metrics.csv"), index=False)
print(f"risk_metrics       : {risk_metrics.shape}")

print("\nAll 10 datasets generated in data/raw/")
