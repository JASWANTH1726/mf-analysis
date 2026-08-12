"""Data cleaning utilities for the Bluestock MF analysis project.

This module reads CSVs in `data/raw`, performs parsing, validation,
and writes cleaned outputs to `data/processed`.
"""

import os
import pandas as pd
import numpy as np

raw  = os.path.join(os.path.dirname(__file__), "data", "raw")
proc = os.path.join(os.path.dirname(__file__), "data", "processed")
os.makedirs(proc, exist_ok=True)


def clean_nav_history():
    df = pd.read_csv(os.path.join(raw, "nav_history.csv"))

    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    df = df.drop_duplicates(subset=["scheme_code", "date"])
    df = df.sort_values(["scheme_code", "date"]).reset_index(drop=True)

    # forward-fill missing dates (holidays/weekends) per scheme
    full = []
    for code, grp in df.groupby("scheme_code"):
        idx = pd.date_range(grp["date"].min(), grp["date"].max(), freq="D")
        grp = grp.set_index("date").reindex(idx)
        grp["scheme_code"] = code
        grp["nav"] = grp["nav"].ffill()
        grp.index.name = "date"
        full.append(grp.reset_index())
    df = pd.concat(full, ignore_index=True)

    invalid = df[df["nav"] <= 0]
    if not invalid.empty:
        print(f"  nav_history: dropping {len(invalid)} rows with nav <= 0")
        df = df[df["nav"] > 0]

    df.to_csv(os.path.join(proc, "nav_history_clean.csv"), index=False)
    print(f"  nav_history: {len(df)} rows saved")
    return df


def clean_investor_transactions():
    df = pd.read_csv(os.path.join(raw, "investor_transactions.csv"))

    # standardise txn_type
    type_map = {
        "sip": "SIP", "SIP": "SIP",
        "lumpsum": "Lumpsum", "Lumpsum": "Lumpsum", "LUMP SUM": "Lumpsum",
        "redemption": "Redemption", "Redemption": "Redemption",
    }
    df["txn_type"] = df["txn_type"].map(type_map).fillna(df["txn_type"])

    # fix date formats
    df["txn_date"] = pd.to_datetime(df["txn_date"], dayfirst=True, errors="coerce")
    bad_dates = df["txn_date"].isna().sum()
    if bad_dates:
        print(f"  transactions: {bad_dates} unparseable dates dropped")
        df = df.dropna(subset=["txn_date"])

    # validate amount > 0
    neg = df[df["amount"] <= 0]
    if not neg.empty:
        print(f"  transactions: {len(neg)} rows with amount <= 0 dropped")
        df = df[df["amount"] > 0]

    # standardise kyc_status
    kyc_map = {
        "KYC_VERIFIED": "KYC_VERIFIED", "verified": "KYC_VERIFIED",
        "KYC_PENDING":  "KYC_PENDING",  "pending":  "KYC_PENDING",
        "KYC_REJECTED": "KYC_REJECTED", "rejected": "KYC_REJECTED",
    }
    df["kyc_status"] = df["kyc_status"].map(kyc_map).fillna("KYC_PENDING")

    df = df.drop_duplicates(subset=["txn_id"])
    df.to_csv(os.path.join(proc, "investor_transactions_clean.csv"), index=False)
    print(f"  transactions: {len(df)} rows saved")
    return df


def clean_scheme_performance():
    df = pd.read_csv(os.path.join(raw, "scheme_performance.csv"))

    ret_cols = ["ret_1m", "ret_3m", "ret_6m", "ret_1y", "benchmark_ret", "alpha"]
    for col in ret_cols:
        before = len(df)
        df[col] = pd.to_numeric(df[col], errors="coerce")
        coerced = before - df[col].notna().sum()
        if coerced:
            print(f"  performance: {coerced} non-numeric values in {col} set to NaN")

    # flag outliers in ret_1y (> 3 std devs)
    mean, std = df["ret_1y"].mean(), df["ret_1y"].std()
    outliers = df[df["ret_1y"].abs() > mean + 3 * std]
    if not outliers.empty:
        print(f"  performance: {len(outliers)} ret_1y outliers flagged -> capped")
        df.loc[df["ret_1y"] > mean + 3 * std, "ret_1y"] = mean + 3 * std
        df.loc[df["ret_1y"] < mean - 3 * std, "ret_1y"] = mean - 3 * std

    # validate expense_ratio range 0.1 – 2.5
    bad_er = df[(df["expense_ratio"] < 0.1) | (df["expense_ratio"] > 2.5)]
    if not bad_er.empty:
        print(f"  performance: {len(bad_er)} expense_ratio out of range [0.1, 2.5] -> clipped")
        df["expense_ratio"] = df["expense_ratio"].clip(0.1, 2.5)

    df = df.dropna(subset=ret_cols)
    df.to_csv(os.path.join(proc, "scheme_performance_clean.csv"), index=False)
    print(f"  performance: {len(df)} rows saved")
    return df


def clean_remaining():
    # fund_master
    df = pd.read_csv(os.path.join(raw, "fund_master.csv"))
    df["launch_date"] = pd.to_datetime(df["launch_date"], dayfirst=True)
    df.to_csv(os.path.join(proc, "fund_master_clean.csv"), index=False)
    print(f"  fund_master: {len(df)} rows")

    # aum_data
    df = pd.read_csv(os.path.join(raw, "aum_data.csv"))
    df["month"] = pd.to_datetime(df["month"], format="%b-%Y")
    df = df[df["aum_cr"] > 0]
    df.to_csv(os.path.join(proc, "aum_data_clean.csv"), index=False)
    print(f"  aum_data: {len(df)} rows")

    # returns_data
    df = pd.read_csv(os.path.join(raw, "returns_data.csv"))
    df["as_of"] = pd.to_datetime(df["as_of"], dayfirst=True)
    df.to_csv(os.path.join(proc, "returns_data_clean.csv"), index=False)
    print(f"  returns_data: {len(df)} rows")

    # risk_metrics
    df = pd.read_csv(os.path.join(raw, "risk_metrics.csv"))
    df["as_of"] = pd.to_datetime(df["as_of"], dayfirst=True)
    df.to_csv(os.path.join(proc, "risk_metrics_clean.csv"), index=False)
    print(f"  risk_metrics: {len(df)} rows")

    # expense_ratio
    df = pd.read_csv(os.path.join(raw, "expense_ratio.csv"))
    df["effective_date"] = pd.to_datetime(df["effective_date"], dayfirst=True)
    df.to_csv(os.path.join(proc, "expense_ratio_clean.csv"), index=False)
    print(f"  expense_ratio: {len(df)} rows")

    # portfolio_holdings
    df = pd.read_csv(os.path.join(raw, "portfolio_holdings.csv"))
    df["as_of"] = pd.to_datetime(df["as_of"], dayfirst=True)
    df = df[df["weight_pct"] > 0]
    df.to_csv(os.path.join(proc, "portfolio_holdings_clean.csv"), index=False)
    print(f"  portfolio_holdings: {len(df)} rows")

    # benchmark_data
    df = pd.read_csv(os.path.join(raw, "benchmark_data.csv"))
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    df.to_csv(os.path.join(proc, "benchmark_data_clean.csv"), index=False)
    print(f"  benchmark_data: {len(df)} rows")


if __name__ == "__main__":
    print("cleaning nav_history...")
    clean_nav_history()
    print("cleaning investor_transactions...")
    clean_investor_transactions()
    print("cleaning scheme_performance...")
    clean_scheme_performance()
    print("cleaning remaining datasets...")
    clean_remaining()
    print("\ndone — cleaned CSVs in data/processed/")
