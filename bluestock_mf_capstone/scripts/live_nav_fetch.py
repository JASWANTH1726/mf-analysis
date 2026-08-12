"""Fetch latest NAVs for selected schemes from mfapi.in and save CSVs.
"""

import os
import requests
import pandas as pd

raw = os.path.join(os.path.dirname(__file__), "data", "raw")

schemes = {
    125497: "hdfc_top100",
    119551: "sbi_bluechip",
    120503: "icici_bluechip",
    118632: "nippon_largecap",
    119092: "axis_bluechip",
    120841: "kotak_bluechip",
}


def fetch(code):
    r = requests.get(f"https://api.mfapi.in/mf/{code}", timeout=30)
    r.raise_for_status()
    return r.json()


def save(code, label):
    data = fetch(code)
    meta = data["meta"]

    df = pd.DataFrame(data["data"])
    df["scheme_code"] = code
    df["scheme_name"] = meta.get("scheme_name", "")
    df["fund_house"] = meta.get("fund_house", "")
    df["scheme_type"] = meta.get("scheme_type", "")
    df["scheme_category"] = meta.get("scheme_category", "")

    out = os.path.join(raw, f"nav_{label}_{code}.csv")
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"{label}: {len(df)} rows, latest nav {df['nav'].iloc[0]} on {df['date'].iloc[0]}")


if __name__ == "__main__":
    os.makedirs(raw, exist_ok=True)
    for code, label in schemes.items():
        try:
            save(code, label)
        except Exception as e:
            print(f"{label} failed: {e}")
