"""Data ingestion helpers: load CSVs and perform basic exploration.

Used to inspect raw/processed datasets and verify AMFI coverage.
"""

import os
import glob
import pandas as pd

raw = os.path.join(os.path.dirname(__file__), "data", "raw")


def load_csvs(path=raw):
    datasets = {}
    for f in sorted(glob.glob(os.path.join(path, "*.csv"))):
        name = os.path.splitext(os.path.basename(f))[0]
        df = pd.read_csv(f)
        datasets[name] = df

        print(f"\n{name}")
        print(df.shape)
        print(df.dtypes)
        print(df.head())

        bad = df.isnull().sum()
        bad = bad[bad > 0]
        if not bad.empty:
            print("nulls:", bad.to_dict())
        if df.duplicated().sum():
            print("dupes:", df.duplicated().sum())

    return datasets


def explore_fund_master(df):
    for col in ["fund_house", "category", "sub_category", "risk_grade"]:
        print(f"\n{col}: {df[col].nunique()} unique")
        print(df[col].value_counts())

    # scheme_code is a 6-digit AMFI-assigned ID, unique per scheme variant
    # direct growth, regular growth, IDCW etc all get separate codes
    print("\ncode range:", df["scheme_code"].min(), "to", df["scheme_code"].max())


def check_amfi_coverage(master, nav):
    m = set(master["scheme_code"].astype(str))
    n = set(nav["scheme_code"].astype(str))

    missing = m - n
    print(f"\nmaster: {len(m)} codes, nav_history: {len(n)} codes")
    print(f"missing from nav: {len(missing)}")
    if missing:
        print("sample:", list(missing)[:5])
    print(f"coverage: {round(len(m - missing) / len(m) * 100, 1)}%")


if __name__ == "__main__":
    data = load_csvs()

    if "fund_master" in data:
        explore_fund_master(data["fund_master"])

    if "fund_master" in data and "nav_history" in data:
        check_amfi_coverage(data["fund_master"], data["nav_history"])
    else:
        print("fund_master or nav_history not found, skipping coverage check")
