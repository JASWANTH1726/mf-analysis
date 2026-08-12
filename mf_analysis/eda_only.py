"""Exploratory data analysis charts saved to `dashboard/eda/`.

This script generates a set of diagnostic charts used in the report and
presentation (boxplots, trends, volatility, transaction summaries, etc.).
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

BASE = os.path.dirname(__file__)
PROC = os.path.join(BASE, "data", "processed")
DASH = os.path.join(BASE, "dashboard", "eda")
os.makedirs(DASH, exist_ok=True)

# ── load data ─────────────────────────────────────────────────────────────────
nav = pd.read_csv(os.path.join(PROC, "nav_history_clean.csv"), parse_dates=["date"])
fm  = pd.read_csv(os.path.join(PROC, "fund_master_clean.csv"))
er  = pd.read_csv(os.path.join(PROC, "expense_ratio_clean.csv"))
aum = pd.read_csv(os.path.join(PROC, "aum_data_clean.csv"), parse_dates=["month"])
txn = pd.read_csv(os.path.join(PROC, "investor_transactions_clean.csv"))
sp  = pd.read_csv(os.path.join(PROC, "scheme_performance_clean.csv"))
bm  = pd.read_csv(os.path.join(PROC, "benchmark_data_clean.csv"), parse_dates=["date"])

nav = nav.sort_values(["scheme_code", "date"]).reset_index(drop=True)
scheme_names = fm.set_index("scheme_code")["scheme_name"].to_dict()
nav["name"] = nav["scheme_code"].map(scheme_names)

print(f"nav: {nav.shape}  |  funds: {nav['scheme_code'].nunique()}  |  date range: {nav['date'].min().date()} to {nav['date'].max().date()}")
print(f"transactions: {txn.shape}  |  aum: {aum.shape}  |  scheme_performance: {sp.shape}")

# ── 1. NAV distribution per fund ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 5))
sample_codes = nav["scheme_code"].unique()[:10]
data = [nav[nav["scheme_code"] == c]["nav"].values for c in sample_codes]
labels = [scheme_names.get(c, str(c)).replace(" Direct Growth", "").replace(" Mutual Fund", "")[:22] for c in sample_codes]
bp = ax.boxplot(data, labels=labels, patch_artist=True, notch=False)
colors = plt.cm.tab10(np.linspace(0, 1, 10))
for patch, color in zip(bp["boxes"], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax.set_title("NAV Distribution per Fund (10 funds)", fontsize=13)
ax.set_ylabel("NAV (Rs)")
ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(DASH, "01_nav_distribution.png"), dpi=150, bbox_inches="tight")
plt.close()
print("saved: 01_nav_distribution.png")

# ── 2. NAV trend — top 5 funds ────────────────────────────────────────────────
top5 = nav.groupby("scheme_code")["nav"].max().nlargest(5).index.tolist()
fig, ax = plt.subplots(figsize=(14, 5))
for code in top5:
    grp = nav[nav["scheme_code"] == code].set_index("date")["nav"]
    label = scheme_names.get(code, str(code)).replace(" Direct Growth", "")[:28]
    ax.plot(grp.index, grp.values, linewidth=1.5, label=label)
ax.set_title("NAV Trend — Top 5 Funds by Peak NAV", fontsize=13)
ax.set_ylabel("NAV (Rs)")
ax.legend(fontsize=8, loc="upper left")
plt.tight_layout()
plt.savefig(os.path.join(DASH, "02_nav_trend.png"), dpi=150, bbox_inches="tight")
plt.close()
print("saved: 02_nav_trend.png")

# ── 3. Daily returns distribution ────────────────────────────────────────────
nav["daily_ret"] = nav.groupby("scheme_code")["nav"].pct_change()
nav = nav.dropna(subset=["daily_ret"])

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
all_rets = nav["daily_ret"].values
axes[0].hist(all_rets, bins=100, color="steelblue", edgecolor="none", alpha=0.8)
axes[0].axvline(0, color="red", linestyle="--", linewidth=1)
axes[0].set_title("Daily Returns Distribution (all funds)", fontsize=12)
axes[0].set_xlabel("Daily Return")
axes[0].set_ylabel("Frequency")

# per-fund mean return bar
mean_rets = nav.groupby("scheme_code")["daily_ret"].mean().sort_values()
short_names = [scheme_names.get(c, str(c)).replace(" Direct Growth","").replace(" Mutual Fund","")[:20] for c in mean_rets.index]
colors_bar = ["#ef5350" if v < 0 else "#66bb6a" for v in mean_rets.values]
axes[1].barh(short_names, mean_rets.values * 100, color=colors_bar)
axes[1].axvline(0, color="white", linewidth=0.8)
axes[1].set_title("Mean Daily Return per Fund (%)", fontsize=12)
axes[1].set_xlabel("Mean Daily Return (%)")
axes[1].tick_params(axis="y", labelsize=7)
plt.tight_layout()
plt.savefig(os.path.join(DASH, "03_daily_returns.png"), dpi=150, bbox_inches="tight")
plt.close()
print("saved: 03_daily_returns.png")

# ── 4. Volatility (std of daily returns) ─────────────────────────────────────
vol = nav.groupby("scheme_code")["daily_ret"].std().sort_values(ascending=False)
short_names = [scheme_names.get(c, str(c)).replace(" Direct Growth","").replace(" Mutual Fund","")[:22] for c in vol.index]

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(short_names, vol.values * 100, color=plt.cm.RdYlGn_r(np.linspace(0.1, 0.9, len(vol))))
ax.set_title("Annualised Volatility per Fund (Daily Std x sqrt(252))", fontsize=12)
ax.set_ylabel("Volatility (%)")
ax.set_xticklabels(short_names, rotation=40, ha="right", fontsize=8)
for bar, val in zip(bars, vol.values * 100):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f"{val:.1f}%", ha="center", va="bottom", fontsize=7)
plt.tight_layout()
plt.savefig(os.path.join(DASH, "04_volatility.png"), dpi=150, bbox_inches="tight")
plt.close()
print("saved: 04_volatility.png")

# ── 5. AUM trend ──────────────────────────────────────────────────────────────
aum_total = aum.groupby("month")["aum_cr"].sum().reset_index()
top5_aum  = aum.groupby("scheme_code")["aum_cr"].mean().nlargest(5).index.tolist()

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].plot(aum_total["month"], aum_total["aum_cr"], color="steelblue", linewidth=2)
axes[0].fill_between(aum_total["month"], aum_total["aum_cr"], alpha=0.2, color="steelblue")
axes[0].set_title("Total AUM Trend (all funds)", fontsize=12)
axes[0].set_ylabel("AUM (Cr)")

for code in top5_aum:
    grp = aum[aum["scheme_code"] == code].set_index("month")["aum_cr"]
    label = scheme_names.get(code, str(code)).replace(" Direct Growth","")[:25]
    axes[1].plot(grp.index, grp.values, linewidth=1.5, label=label)
axes[1].set_title("AUM Trend — Top 5 Funds", fontsize=12)
axes[1].set_ylabel("AUM (Cr)")
axes[1].legend(fontsize=7)
plt.tight_layout()
plt.savefig(os.path.join(DASH, "05_aum_trend.png"), dpi=150, bbox_inches="tight")
plt.close()
print("saved: 05_aum_trend.png")

# ── 6. Expense ratio distribution ────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].hist(er["direct_ter"].dropna(), bins=20, color="#4fc3f7", edgecolor="white", alpha=0.8)
axes[0].set_title("Direct TER Distribution", fontsize=12)
axes[0].set_xlabel("TER (%)")
axes[0].set_ylabel("Count")

er_sorted = er.sort_values("direct_ter")
short = [scheme_names.get(c, str(c)).replace(" Direct Growth","").replace(" Mutual Fund","")[:20] for c in er_sorted["scheme_code"]]
axes[1].barh(short, er_sorted["direct_ter"], color="#ffa726")
axes[1].set_title("Direct TER per Fund", fontsize=12)
axes[1].set_xlabel("TER (%)")
axes[1].tick_params(axis="y", labelsize=7)
plt.tight_layout()
plt.savefig(os.path.join(DASH, "06_expense_ratio.png"), dpi=150, bbox_inches="tight")
plt.close()
print("saved: 06_expense_ratio.png")

# ── 7. Transaction analysis ───────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# txn type breakdown
txn_counts = txn["txn_type"].value_counts()
axes[0].pie(txn_counts.values, labels=txn_counts.index, autopct="%1.1f%%",
            colors=["#4fc3f7", "#66bb6a", "#ef5350"], startangle=90)
axes[0].set_title("Transaction Type Breakdown", fontsize=12)

# monthly transaction volume
txn["txn_date"] = pd.to_datetime(txn["txn_date"], errors="coerce")
txn["month"] = txn["txn_date"].dt.to_period("M")
monthly = txn.groupby("month")["amount"].sum().reset_index()
monthly["month_str"] = monthly["month"].astype(str)
axes[1].bar(monthly["month_str"], monthly["amount"] / 1e5, color="steelblue", alpha=0.8)
axes[1].set_title("Monthly Transaction Volume (Lakhs)", fontsize=12)
axes[1].set_xlabel("Month")
axes[1].set_ylabel("Amount (Lakhs)")
axes[1].set_xticklabels(monthly["month_str"], rotation=45, ha="right", fontsize=6)

# KYC status
kyc = txn["kyc_status"].value_counts()
colors_kyc = {"KYC_VERIFIED": "#66bb6a", "KYC_PENDING": "#ffa726", "KYC_REJECTED": "#ef5350"}
axes[2].bar(kyc.index, kyc.values, color=[colors_kyc.get(k, "grey") for k in kyc.index])
axes[2].set_title("KYC Status Breakdown", fontsize=12)
axes[2].set_ylabel("Count")
for i, (k, v) in enumerate(kyc.items()):
    axes[2].text(i, v + 5, str(v), ha="center", fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(DASH, "07_transactions.png"), dpi=150, bbox_inches="tight")
plt.close()
print("saved: 07_transactions.png")

# ── 8. Correlation heatmap (scheme performance metrics) ──────────────────────
num_cols = sp.select_dtypes(include=np.number).columns.tolist()
corr = sp[num_cols].corr()

fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
            center=0, ax=ax, linewidths=0.5, annot_kws={"size": 8})
ax.set_title("Correlation Heatmap — Scheme Performance Metrics", fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(DASH, "08_correlation_heatmap.png"), dpi=150, bbox_inches="tight")
plt.close()
print("saved: 08_correlation_heatmap.png")

# ── 9. Rolling 30-day volatility — top 3 funds ───────────────────────────────
top3 = nav.groupby("scheme_code")["daily_ret"].std().nlargest(3).index.tolist()
fig, ax = plt.subplots(figsize=(14, 5))
for code in top3:
    grp = nav[nav["scheme_code"] == code].set_index("date")["daily_ret"]
    roll_vol = grp.rolling(30).std() * np.sqrt(252) * 100
    label = scheme_names.get(code, str(code)).replace(" Direct Growth","")[:28]
    ax.plot(roll_vol.index, roll_vol.values, linewidth=1.5, label=label)
ax.set_title("Rolling 30-Day Volatility — Top 3 Most Volatile Funds", fontsize=12)
ax.set_ylabel("Annualised Volatility (%)")
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(DASH, "09_rolling_volatility.png"), dpi=150, bbox_inches="tight")
plt.close()
print("saved: 09_rolling_volatility.png")

# ── 10. Fund category breakdown ───────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

cat_counts = fm["category"].value_counts()
axes[0].pie(cat_counts.values, labels=cat_counts.index, autopct="%1.1f%%",
            startangle=90, colors=plt.cm.Set3(np.linspace(0, 1, len(cat_counts))))
axes[0].set_title("Fund Category Distribution", fontsize=12)

house_counts = fm["fund_house"].value_counts()
axes[1].barh(house_counts.index, house_counts.values, color=plt.cm.tab10(np.linspace(0, 1, len(house_counts))))
axes[1].set_title("Funds per Fund House", fontsize=12)
axes[1].set_xlabel("Number of Funds")
for i, v in enumerate(house_counts.values):
    axes[1].text(v + 0.05, i, str(v), va="center", fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(DASH, "10_fund_categories.png"), dpi=150, bbox_inches="tight")
plt.close()
print("saved: 10_fund_categories.png")

print("\nEDA complete. All 10 charts saved to dashboard/eda/")
