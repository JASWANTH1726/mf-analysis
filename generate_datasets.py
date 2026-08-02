import os
import numpy as np
import pandas as pd

raw = os.path.join(os.path.dirname(__file__), "data", "raw")
os.makedirs(raw, exist_ok=True)

rng = np.random.default_rng(42)

codes = [125497, 119551, 120503, 118632, 119092, 120841,
         118989, 120594, 119775, 118825, 120465, 119386,
         118551, 120178, 119203, 118712, 120333, 119644,
         118890, 120712]

houses = ["HDFC Mutual Fund", "SBI Mutual Fund", "ICICI Prudential",
          "Nippon India", "Axis Mutual Fund", "Kotak Mahindra",
          "Mirae Asset", "DSP Mutual Fund", "Franklin Templeton", "UTI Mutual Fund"]

managers = [
    "Prashant Jain", "R. Srinivasan", "S. Naren", "Sailesh Raj Bhan",
    "Jinesh Gopani", "Harish Krishnan", "Neelesh Surana", "Apoorva Shah",
    "Anand Radhakrishnan", "Vetri Subramaniam", "Mahesh Patil", "Atul Penkar",
    "Sohini Andani", "Roshi Jain", "Shreyash Devalkar", "Taher Badshah",
    "Vinay Paharia", "Amit Ganatra", "Chirag Setalvad", "Lalit Kumar"
]

subcats = ["Large Cap", "Mid Cap", "Small Cap", "Flexi Cap",
           "ELSS", "Liquid", "Short Duration", "Balanced Advantage"]
risk    = ["Low", "Moderate", "Moderately High", "High", "Very High"]
types   = ["Open Ended", "Close Ended", "Interval"]

trading_days = pd.date_range("2015-01-01", "2024-12-31", freq="B")
sample       = trading_days[::5][:500]

# fund_master
fm = pd.DataFrame({
    "scheme_code":   codes,
    "scheme_name":   [f"{houses[i%10]} {subcats[i%8]} Fund Direct Growth" for i in range(20)],
    "fund_house":    [houses[i%10] for i in range(20)],
    "category":      ["Equity", "Debt", "Hybrid", "Solution Oriented", "Other"] * 4,
    "sub_category":  [subcats[i%8] for i in range(20)],
    "risk_grade":    [risk[i%5] for i in range(20)],
    "scheme_type":   [types[i%3] for i in range(20)],
    "launch_date":   pd.date_range("2010-01-01", periods=20, freq="180D").strftime("%d-%m-%Y"),
    "benchmark":     ["Nifty 50", "Nifty 100", "BSE 500", "Nifty Midcap 150", "Nifty Smallcap 250"] * 4,
    "exit_load_pct": rng.choice([0.0, 0.5, 1.0], size=20),
    "min_sip":       rng.choice([500, 1000, 5000], size=20),
})
fm.to_csv(os.path.join(raw, "fund_master.csv"), index=False)

# nav_history — random walk from NAV 10
rows = []
for code in codes:
    nav = 10.0
    for d in sample:
        nav *= 1 + rng.normal(0.0004, 0.008)
        rows.append({"scheme_code": code, "date": d.strftime("%d-%m-%Y"), "nav": round(nav, 4)})
pd.DataFrame(rows).to_csv(os.path.join(raw, "nav_history.csv"), index=False)

# portfolio_holdings
stocks = ["Reliance", "HDFC Bank", "Infosys", "TCS", "ICICI Bank", "Kotak Bank",
          "L&T", "Axis Bank", "HUL", "Bajaj Finance", "Wipro", "SBI",
          "Maruti", "Asian Paints", "Titan"]
rows = []
for code in codes:
    picks   = rng.choice(stocks, size=10, replace=False)
    weights = rng.dirichlet(np.ones(10)) * 100
    for s, w in zip(picks, weights):
        rows.append({
            "scheme_code": code, "stock": s, "weight_pct": round(w, 2),
            "sector": rng.choice(["Banking", "IT", "FMCG", "Auto", "Energy"]),
            "as_of": "31-12-2024"
        })
pd.DataFrame(rows).to_csv(os.path.join(raw, "portfolio_holdings.csv"), index=False)

# sip_data
rows = []
for code in codes[:10]:
    for d in pd.date_range("2020-01-01", "2024-12-31", freq="MS"):
        rows.append({
            "scheme_code": code,
            "date": d.strftime("%d-%m-%Y"),
            "amount": int(rng.choice([500, 1000, 2000, 5000])),
            "units": round(rng.uniform(5, 50), 4),
            "nav": round(rng.uniform(20, 300), 4),
        })
pd.DataFrame(rows).to_csv(os.path.join(raw, "sip_data.csv"), index=False)

# returns
pd.DataFrame({
    "scheme_code":      codes,
    "ret_1m":           rng.normal(1.2, 2.5, 20).round(2),
    "ret_3m":           rng.normal(3.5, 4.0, 20).round(2),
    "ret_6m":           rng.normal(7.0, 6.0, 20).round(2),
    "ret_1y":           rng.normal(14.0, 8.0, 20).round(2),
    "ret_3y":           rng.normal(12.0, 5.0, 20).round(2),
    "ret_5y":           rng.normal(13.5, 4.5, 20).round(2),
    "ret_inception":    rng.normal(15.0, 3.5, 20).round(2),
    "as_of":            "31-12-2024",
}).to_csv(os.path.join(raw, "returns_data.csv"), index=False)

# benchmark
rows = []
for d in sample:
    rows.append({
        "date":         d.strftime("%d-%m-%Y"),
        "nifty50":      round(rng.uniform(8000, 24000), 2),
        "nifty100":     round(rng.uniform(8500, 25000), 2),
        "bse500":       round(rng.uniform(7000, 22000), 2),
        "nifty_midcap": round(rng.uniform(5000, 18000), 2),
    })
pd.DataFrame(rows).to_csv(os.path.join(raw, "benchmark_data.csv"), index=False)

# aum
rows = []
for code in codes:
    for m in pd.date_range("2022-01-01", "2024-12-31", freq="MS"):
        rows.append({
            "scheme_code": code,
            "month":       m.strftime("%b-%Y"),
            "aum_cr":      round(rng.uniform(100, 50000), 2),
            "folios":      int(rng.integers(1000, 500000)),
        })
pd.DataFrame(rows).to_csv(os.path.join(raw, "aum_data.csv"), index=False)

# expense ratio
pd.DataFrame({
    "scheme_code":   codes,
    "direct_ter":    rng.uniform(0.1, 1.0, 20).round(3),
    "regular_ter":   rng.uniform(0.8, 2.5, 20).round(3),
    "effective_date": "01-01-2024",
}).to_csv(os.path.join(raw, "expense_ratio.csv"), index=False)

# fund managers
pd.DataFrame({
    "scheme_code":    codes,
    "manager":        managers,
    "exp_years":      rng.integers(5, 25, 20),
    "managing_since": pd.date_range("2015-01-01", periods=20, freq="90D").strftime("%d-%m-%Y"),
    "qualification":  rng.choice(["MBA", "CFA", "CA", "MBA+CFA"], size=20),
}).to_csv(os.path.join(raw, "fund_manager.csv"), index=False)

# risk metrics
pd.DataFrame({
    "scheme_code":  codes,
    "std_dev":      rng.uniform(5, 25, 20).round(3),
    "beta":         rng.uniform(0.6, 1.4, 20).round(3),
    "sharpe":       rng.uniform(0.3, 2.5, 20).round(3),
    "alpha":        rng.uniform(-2, 5, 20).round(3),
    "r_squared":    rng.uniform(0.7, 0.99, 20).round(3),
    "sortino":      rng.uniform(0.4, 3.0, 20).round(3),
    "as_of":        "31-12-2024",
}).to_csv(os.path.join(raw, "risk_metrics.csv"), index=False)

# investor_transactions
states = ["Maharashtra", "Karnataka", "Tamil Nadu", "Delhi", "Gujarat",
          "West Bengal", "Rajasthan", "Telangana", "Uttar Pradesh", "Kerala"]
tx_types = ["SIP", "Lumpsum", "Redemption", "SIP", "Lumpsum"]  # weighted toward SIP
kyc = ["KYC_VERIFIED", "KYC_PENDING", "KYC_REJECTED"]
rows = []
for i in range(2000):
    code = rng.choice(codes)
    rows.append({
        "txn_id":       f"TXN{100000+i}",
        "scheme_code":  code,
        "txn_date":     pd.Timestamp(rng.choice(pd.date_range("2020-01-01", "2024-12-31", freq="B").values)).strftime("%d-%m-%Y"),
        "txn_type":     rng.choice(tx_types),
        "amount":       round(float(rng.choice([500, 1000, 2000, 5000, 10000, 25000, 50000])), 2),
        "units":        round(rng.uniform(1, 200), 4),
        "nav":          round(rng.uniform(10, 500), 4),
        "investor_id":  f"INV{rng.integers(1000, 9999)}",
        "state":        rng.choice(states),
        "kyc_status":   rng.choice(kyc, p=[0.85, 0.12, 0.03]),
        "folio_no":     f"FOLIO{rng.integers(100000, 999999)}",
    })
# inject some dirty data for cleaning exercise
rows[5]["txn_type"]  = "sip"          # lowercase
rows[10]["txn_type"] = "LUMP SUM"     # wrong format
rows[15]["amount"]   = -500           # negative amount
rows[20]["txn_date"] = "2024/06/15"   # wrong date format
rows[25]["kyc_status"] = "verified"   # non-standard
pd.DataFrame(rows).to_csv(os.path.join(raw, "investor_transactions.csv"), index=False)

# scheme_performance
perf_rows = []
for code in codes:
    for qtr in pd.date_range("2020-01-01", "2024-12-31", freq="QS"):
        perf_rows.append({
            "scheme_code":   code,
            "period":        qtr.strftime("%b-%Y"),
            "ret_1m":        round(rng.normal(1.2, 3.0), 2),
            "ret_3m":        round(rng.normal(3.5, 5.0), 2),
            "ret_6m":        round(rng.normal(7.0, 7.0), 2),
            "ret_1y":        round(rng.normal(14.0, 9.0), 2),
            "expense_ratio": round(rng.uniform(0.1, 2.5), 3),
            "benchmark_ret": round(rng.normal(12.0, 6.0), 2),
            "alpha":         round(rng.normal(1.5, 2.5), 3),
        })
# inject anomalies
perf_rows[3]["ret_1y"]        = 999.0   # outlier
perf_rows[7]["expense_ratio"] = 5.5     # out of range
perf_rows[12]["ret_3m"]       = "N/A"   # non-numeric
pd.DataFrame(perf_rows).to_csv(os.path.join(raw, "scheme_performance.csv"), index=False)

print("done")
