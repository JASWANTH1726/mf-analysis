import os
import requests
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")

SCHEMES = {
    125497: "HDFC_Top100_Direct",
    119551: "SBI_Bluechip",
    120503: "ICICI_Bluechip",
    118632: "Nippon_LargeCap",
    119092: "Axis_Bluechip",
    120841: "Kotak_Bluechip",
}


def fetch_and_save(scheme_code, name):
    resp = requests.get(f"https://api.mfapi.in/mf/{scheme_code}", timeout=30)
    resp.raise_for_status()
    data = resp.json()

    meta = data.get("meta", {})
    df = pd.DataFrame(data.get("data", []))
    df["scheme_code"]     = scheme_code
    df["scheme_name"]     = meta.get("scheme_name", "")
    df["fund_house"]      = meta.get("fund_house", "")
    df["scheme_type"]     = meta.get("scheme_type", "")
    df["scheme_category"] = meta.get("scheme_category", "")

    out = os.path.join(RAW_DIR, f"nav_{name}_{scheme_code}.csv")
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"{name} ({scheme_code}): {len(df)} records | latest {df['date'].iloc[0]} -> {df['nav'].iloc[0]}")


if __name__ == "__main__":
    os.makedirs(RAW_DIR, exist_ok=True)
    for code, name in SCHEMES.items():
        try:
            fetch_and_save(code, name)
        except Exception as e:
            print(f"failed {name}: {e}")
