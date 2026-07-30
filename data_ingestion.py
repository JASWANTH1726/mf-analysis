import os
import glob
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")


def load_all_csvs(directory=RAW_DIR):
    files = sorted(glob.glob(os.path.join(directory, "*.csv")))
    if not files:
        print(f"no CSVs found in {directory}")
        return {}

    datasets = {}
    for path in files:
        name = os.path.splitext(os.path.basename(path))[0]
        df = pd.read_csv(path)
        datasets[name] = df

        print(f"\n{'='*55}")
        print(f"  {name}")
        print(f"  shape : {df.shape}")
        print(f"  dtypes:\n{df.dtypes.to_string()}")
        print(f"  head  :\n{df.head().to_string()}")

        nulls = df.isnull().sum()
        nulls = nulls[nulls > 0]
        if not nulls.empty:
            print(f"  [!] nulls:\n{nulls.to_string()}")

        dups = df.duplicated().sum()
        if dups:
            print(f"  [!] {dups} duplicate rows")

    print(f"\nloaded {len(datasets)} datasets")
    return datasets


def explore_fund_master(datasets):
    fm = datasets.get("fund_master")
    if fm is None:
        print("fund_master not found")
        return

    print("\n--- fund_master exploration ---")
    for col in ["fund_house", "category", "sub_category", "risk_grade"]:
        if col in fm.columns:
            vals = fm[col].unique()
            print(f"\n{col} ({len(vals)} unique): {vals}")

    # AMFI scheme codes are 6-digit numeric IDs — each scheme variant
    # (direct/regular, growth/dividend) gets its own unique code
    if "scheme_code" in fm.columns:
        print(f"\nscheme_code range: {fm['scheme_code'].min()} - {fm['scheme_code'].max()}")
        print(f"sample codes: {fm['scheme_code'].head(5).tolist()}")


def validate_amfi_codes(datasets):
    fm  = datasets.get("fund_master")
    nav = datasets.get("nav_history")

    if fm is None or nav is None:
        print("need fund_master + nav_history for validation")
        return

    master_codes = set(fm["scheme_code"].dropna().astype(str))
    nav_codes    = set(nav["scheme_code"].dropna().astype(str))

    missing  = master_codes - nav_codes
    extra    = nav_codes - master_codes
    coverage = round((len(master_codes) - len(missing)) / len(master_codes) * 100, 1)

    print("\n--- data quality summary ---")
    print(f"fund_master codes          : {len(master_codes)}")
    print(f"nav_history unique codes   : {len(nav_codes)}")
    print(f"missing from nav_history   : {len(missing)}")
    if missing:
        print(f"  e.g. {sorted(missing)[:5]}")
    print(f"extra in nav, not in master: {len(extra)}")
    print(f"amfi code coverage         : {coverage}%")

    if coverage == 100.0:
        print("all master codes have NAV history — data looks clean")
    else:
        print(f"[!] {len(missing)} codes lack NAV history — investigate before analysis")


if __name__ == "__main__":
    datasets = load_all_csvs()
    explore_fund_master(datasets)
    validate_amfi_codes(datasets)
