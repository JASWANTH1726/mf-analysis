"""Load cleaned CSVs into a SQLite database and verify table row counts.

Creates dimension and fact tables used by the dashboard and analysis.
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text

proc = os.path.join(os.path.dirname(__file__), "data", "processed")
db   = os.path.join(os.path.dirname(__file__), "bluestock_mf.db")
sql  = os.path.join(os.path.dirname(__file__), "sql", "schema.sql")

engine = create_engine(f"sqlite:///{db}")


def init_schema():
    with open(sql) as f:
        schema = f.read()
    with engine.connect() as conn:
        for stmt in schema.split(";"):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()
    print("schema created")


def load_dim_fund():
    df = pd.read_csv(os.path.join(proc, "fund_master_clean.csv"))
    df.to_sql("dim_fund", engine, if_exists="replace", index=False)
    print(f"dim_fund: {len(df)} rows")


def load_dim_date():
    # build date dimension from nav date range
    nav = pd.read_csv(os.path.join(proc, "nav_history_clean.csv"), usecols=["date"])
    dates = pd.to_datetime(nav["date"]).drop_duplicates().sort_values()
    df = pd.DataFrame({
        "date_id":    dates.dt.strftime("%Y%m%d").astype(int),
        "date":       dates.dt.strftime("%Y-%m-%d"),
        "year":       dates.dt.year,
        "quarter":    dates.dt.quarter,
        "month":      dates.dt.month,
        "month_name": dates.dt.strftime("%b"),
        "week":       dates.dt.isocalendar().week.astype(int),
        "day_of_week":dates.dt.strftime("%A"),
        "is_weekend": dates.dt.dayofweek.isin([5, 6]).astype(int),
    })
    df.to_sql("dim_date", engine, if_exists="replace", index=False)
    print(f"dim_date: {len(df)} rows")


def load_fact_nav():
    df = pd.read_csv(os.path.join(proc, "nav_history_clean.csv"))
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = df[["scheme_code", "date", "nav"]]
    df.to_sql("fact_nav", engine, if_exists="replace", index=False)
    print(f"fact_nav: {len(df)} rows")


def load_fact_transactions():
    df = pd.read_csv(os.path.join(proc, "investor_transactions_clean.csv"))
    df["txn_date"] = pd.to_datetime(df["txn_date"]).dt.strftime("%Y-%m-%d")
    df.to_sql("fact_transactions", engine, if_exists="replace", index=False)
    print(f"fact_transactions: {len(df)} rows")


def load_fact_performance():
    df = pd.read_csv(os.path.join(proc, "scheme_performance_clean.csv"))
    df.to_sql("fact_performance", engine, if_exists="replace", index=False)
    print(f"fact_performance: {len(df)} rows")


def load_fact_aum():
    df = pd.read_csv(os.path.join(proc, "aum_data_clean.csv"))
    df["month"] = pd.to_datetime(df["month"]).dt.strftime("%Y-%m")
    df.to_sql("fact_aum", engine, if_exists="replace", index=False)
    print(f"fact_aum: {len(df)} rows")


def verify():
    tables = ["dim_fund", "dim_date", "fact_nav", "fact_transactions",
              "fact_performance", "fact_aum"]
    print("\nrow count verification:")
    with engine.connect() as conn:
        for t in tables:
            n = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            print(f"  {t}: {n}")


if __name__ == "__main__":
    init_schema()
    load_dim_fund()
    load_dim_date()
    load_fact_nav()
    load_fact_transactions()
    load_fact_performance()
    load_fact_aum()
    verify()
    print(f"\ndb saved: {db}")
