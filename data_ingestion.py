import os
import glob
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")


def load_all_csvs(directory=RAW_DIR):
    files = glob.glob(os.path.join(directory, "*.csv"))
    if not files:
        print(f"No CSVs found in {directory}")
        return {}

    datasets = {}
    for path in files:
        name = os.path.splitext(os.path.basename(path))[0]
        df = pd.read_csv(path)
        datasets[name] = df

        print(f"\n{'='*55}\n{name}")
        print(f"shape : {df.shape}")
        print(f"dtypes:\n{df.dtypes}")
        print(f"head  :\n{df.head()}")

        nulls = df.isnull().sum()
        nulls = nulls[nulls > 0]
        if not nulls.empty:
            print(f"[!] nulls found:\n{nulls}")

        dups = df.duplicated().sum()
        if dups:
            print(f"[!] {dups} duplicate rows")

    return datasets


def explore_fund_master(datasets):
    fm = datasets.get("fund_master")
    if fm is None:
        print("fund_master not loaded, skipping.")
        return

    for col in ["fund_house", "category", "sub_category", "risk_grade"]:
        if col in fm.columns:
            print(f"\n{col} ({fm[col].nunique()} unique):\n{fm[col].unique()}")

    # AMFI scheme codes are 6-digit numeric IDs assigned by AMFI per scheme variant
    if "scheme_code" in fm.columns:
        print(f"\nscheme_code samples: {fm['scheme_code'].head(5).tolist()}")


def validate_amfi_codes(datasets):
    fm = datasets.get("fund_master")
    nav = datasets.get("nav_history")

    if fm is None or nav is None:
        print("Need both fund_master and nav_history for validation.")
        return

    master_codes = set(fm["scheme_code"].dropna().astype(str))
    nav_codes    = set(nav["scheme_code"].dropna().astype(str))

    missing = master_codes - nav_codes
    extra   = nav_codes - master_codes
    coverage = round((len(master_codes) - len(missing)) / len(master_codes) * 100, 1)

    print("\n--- data quality summary ---")
    print(f"master codes : {len(master_codes)}")
    print(f"nav codes    : {len(nav_codes)}")
    print(f"in master, missing from nav : {len(missing)}")
    if missing:
        print(f"  e.g. {list(missing)[:5]}")
    print(f"in nav, not in master       : {len(extra)}")
    print(f"coverage: {coverage}%")


if __name__ == "__main__":
    datasets = load_all_csvs()
    explore_fund_master(datasets)
    validate_amfi_codes(datasets)
