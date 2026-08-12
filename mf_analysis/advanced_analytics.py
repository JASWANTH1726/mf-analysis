"""Advanced analytics: VaR/CVaR, HHI concentration, recommender, and reports.

Writes `var_cvar_report.csv`, `hhi_concentration.csv`, and other analytic outputs.
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

warnings.filterwarnings("ignore")

BASE = os.path.dirname(__file__)
PROC = os.path.join(BASE, "data", "processed")
DASH = os.path.join(BASE, "dashboard")
os.makedirs(DASH, exist_ok=True)

# ── palette ───────────────────────────────────────────────────────────────────
BG    = "#0d1117"; PANEL = "#161b22"; BORDER = "#30363d"
BLUE  = "#4fc3f7"; GREEN = "#56d364"; AMBER  = "#e3b341"
RED   = "#f85149"; PURPLE= "#bc8cff"; WHITE  = "#e6edf3"; GRAY = "#8b949e"
ACCENT = [BLUE, GREEN, AMBER, RED, PURPLE, "#ff7b72", "#79c0ff", "#ffa657"]

def style_ax(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=GRAY, labelsize=8)
    ax.xaxis.label.set_color(GRAY); ax.yaxis.label.set_color(GRAY)
    ax.title.set_color(BLUE)
    for sp in ax.spines.values(): sp.set_edgecolor(BORDER)

# ── load ──────────────────────────────────────────────────────────────────────
nav = pd.read_csv(os.path.join(PROC, "nav_history_clean.csv"), parse_dates=["date"])
fm  = pd.read_csv(os.path.join(PROC, "fund_master_clean.csv"))
txn = pd.read_csv(os.path.join(PROC, "investor_transactions_clean.csv"), parse_dates=["txn_date"])
ph  = pd.read_csv(os.path.join(PROC, "portfolio_holdings_clean.csv"))

nav = nav.sort_values(["scheme_code","date"]).reset_index(drop=True)
names = fm.set_index("scheme_code")["scheme_name"].to_dict()
risk_map = fm.set_index("scheme_code")["risk_grade"].to_dict()
nav["daily_ret"] = nav.groupby("scheme_code")["nav"].pct_change()
nav = nav.dropna(subset=["daily_ret"])

RF = 0.065 / 252

print("=" * 60)

# ─────────────────────────────────────────────────────────────────────────────
# TASK 1 — Historical VaR (95%) & CVaR for all 40 schemes
# ─────────────────────────────────────────────────────────────────────────────
print("\n[1] Computing VaR & CVaR for all 40 schemes...")

rows = []
for code, grp in nav.groupby("scheme_code"):
    rets = grp["daily_ret"].dropna()
    var95  = np.percentile(rets, 5)
    cvar95 = rets[rets <= var95].mean()
    ann_ret = rets.mean() * 252 * 100
    ann_vol = rets.std() * np.sqrt(252) * 100
    rows.append({
        "scheme_code": code,
        "scheme_name": names.get(code, "")[:40],
        "risk_grade":  risk_map.get(code, ""),
        "var_95_daily_pct":  round(var95 * 100, 4),
        "cvar_95_daily_pct": round(cvar95 * 100, 4),
        "ann_return_pct":    round(ann_ret, 2),
        "ann_vol_pct":       round(ann_vol, 2),
    })

var_df = pd.DataFrame(rows).sort_values("var_95_daily_pct")
var_df.to_csv(os.path.join(BASE, "var_cvar_report.csv"), index=False)
print(f"  Saved: var_cvar_report.csv  ({len(var_df)} funds)")
print(f"  Highest VaR: {var_df.iloc[0]['scheme_name']} ({var_df.iloc[0]['var_95_daily_pct']}%)")
print(f"  Lowest  VaR: {var_df.iloc[-1]['scheme_name']} ({var_df.iloc[-1]['var_95_daily_pct']}%)")

# ─────────────────────────────────────────────────────────────────────────────
# TASK 2 — Rolling 90-day Sharpe for 5 key funds
# ─────────────────────────────────────────────────────────────────────────────
print("\n[2] Rolling 90-day Sharpe chart...")

sc = pd.read_csv(os.path.join(BASE, "fund_scorecard.csv"), index_col=0)
top5 = sc.head(5)["scheme_code"].tolist()

fig, ax = plt.subplots(figsize=(14, 6), facecolor=BG)
style_ax(ax)

for i, code in enumerate(top5):
    grp = nav[nav["scheme_code"] == code].set_index("date")["daily_ret"]
    roll_sharpe = (
        (grp.rolling(90).mean() - RF) / grp.rolling(90).std()
    ) * np.sqrt(252)
    label = names.get(code, "").replace(" Direct Growth", "").replace(" Mutual Fund", "")[:28]
    ax.plot(roll_sharpe.index, roll_sharpe.values, color=ACCENT[i],
            linewidth=1.5, label=label, alpha=0.9)

ax.axhline(0, color=GRAY, linewidth=0.8, linestyle="--")
ax.set_title("Rolling 90-Day Sharpe Ratio — Top 5 Funds", fontsize=13)
ax.set_ylabel("Sharpe Ratio (annualised)")
ax.set_xlabel("Date")
ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE, framealpha=0.8)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
fig.patch.set_facecolor(BG)
plt.tight_layout()
out = os.path.join(DASH, "rolling_sharpe_chart.png")
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"  Saved: {out}")

# ─────────────────────────────────────────────────────────────────────────────
# TASK 3 — Investor cohort analysis
# ─────────────────────────────────────────────────────────────────────────────
print("\n[3] Investor cohort analysis...")

sip = txn[txn["txn_type"] == "SIP"].copy()
first_yr = sip.groupby("investor_id")["txn_date"].min().dt.year.rename("cohort_year")
sip = sip.join(first_yr, on="investor_id")

cohort = sip.groupby("cohort_year").agg(
    investors   = ("investor_id", "nunique"),
    avg_sip_amt = ("amount", "mean"),
    total_invested = ("amount", "sum"),
).round(2)

# top fund per cohort
top_fund = (
    sip.groupby(["cohort_year", "scheme_code"])["amount"]
    .sum().reset_index()
    .sort_values("amount", ascending=False)
    .groupby("cohort_year").first()["scheme_code"]
    .map(lambda c: names.get(c, "")[:30])
    .rename("top_fund")
)
cohort = cohort.join(top_fund)
cohort.to_csv(os.path.join(BASE, "cohort_analysis.csv"))
print(cohort.to_string())

# ─────────────────────────────────────────────────────────────────────────────
# TASK 4 — SIP continuity analysis
# ─────────────────────────────────────────────────────────────────────────────
print("\n[4] SIP continuity analysis...")

sip_sorted = sip.sort_values(["folio_no", "txn_date"])
sip_sorted["prev_date"] = sip_sorted.groupby("folio_no")["txn_date"].shift(1)
sip_sorted["gap_days"]  = (sip_sorted["txn_date"] - sip_sorted["prev_date"]).dt.days

# folios with 3+ SIP transactions
freq = sip_sorted.groupby("folio_no")["txn_date"].count()
active = freq[freq >= 3].index
sip_active = sip_sorted[sip_sorted["folio_no"].isin(active)]

continuity = sip_active.groupby("folio_no")["gap_days"].mean().reset_index()
continuity.columns = ["folio_no", "avg_gap_days"]
continuity["at_risk"] = continuity["avg_gap_days"] > 35

at_risk_count = continuity["at_risk"].sum()
total_active  = len(continuity)
continuity_rate = round((1 - at_risk_count / total_active) * 100, 1)

continuity.to_csv(os.path.join(BASE, "sip_continuity.csv"), index=False)
print(f"  Active investors (6+ SIPs): {total_active}")
print(f"  At-risk (gap > 35 days):    {at_risk_count}")
print(f"  SIP continuity rate:        {continuity_rate}%")

# ─────────────────────────────────────────────────────────────────────────────
# TASK 5 — Fund Recommender
# ─────────────────────────────────────────────────────────────────────────────
print("\n[5] Fund recommender built -> recommender.py")

recommender_code = '''import pandas as pd, os

BASE = os.path.dirname(__file__)

def recommend(risk_appetite: str):
    """
    risk_appetite: "Low" | "Moderate" | "High"
    Returns top 3 funds by Sharpe within matching risk_grade.
    """
    risk_map = {
        "Low":      ["Low"],
        "Moderate": ["Moderate", "Moderately High"],
        "High":     ["High", "Very High", "Moderately High"],
    }
    sc  = pd.read_csv(os.path.join(BASE, "fund_scorecard.csv"), index_col=0)
    fm  = pd.read_csv(os.path.join(BASE, "data", "processed", "fund_master_clean.csv"))
    rg  = fm.set_index("scheme_code")["risk_grade"].to_dict()
    sc["risk_grade"] = sc["scheme_code"].map(rg)

    grades  = risk_map.get(risk_appetite, ["Moderate"])
    filtered = sc[sc["risk_grade"].isin(grades)].nlargest(3, "sharpe")

    cols = ["scheme_name", "risk_grade", "sharpe", "cagr_3y", "alpha_annual", "score"]
    result = filtered[cols].copy()
    result.columns = ["Fund", "Risk Grade", "Sharpe", "CAGR 3Y", "Alpha %", "Score"]
    result["Fund"] = result["Fund"].str.replace(" Direct Growth", "").str.replace(" Mutual Fund", "")
    result = result.reset_index(drop=True)
    result.index += 1

    print(f"\\n  Top 3 Funds for {risk_appetite} risk appetite:")
    print(result.to_string())
    return result

if __name__ == "__main__":
    for r in ["Low", "Moderate", "High"]:
        recommend(r)
        print()
'''

with open(os.path.join(BASE, "recommender.py"), "w") as f:
    f.write(recommender_code)

# run it inline too
risk_map_grades = {
    "Low":      ["Low"],
    "Moderate": ["Moderate", "Moderately High"],
    "High":     ["High", "Very High", "Moderately High"],
}
rg_map = fm.set_index("scheme_code")["risk_grade"].to_dict()
sc["risk_grade"] = sc["scheme_code"].map(rg_map)

for appetite in ["Low", "Moderate", "High"]:
    grades   = risk_map_grades[appetite]
    filtered = sc[sc["risk_grade"].isin(grades)].nlargest(3, "sharpe")
    print(f"\n  [{appetite}] Top 3 by Sharpe:")
    for _, row in filtered.iterrows():
        name = names.get(row["scheme_code"], "")[:35]
        print(f"    {name:35s}  Sharpe={row['sharpe']:.3f}  Score={row['score']:.1f}")

# ─────────────────────────────────────────────────────────────────────────────
# TASK 6 — Sector HHI Concentration
# ─────────────────────────────────────────────────────────────────────────────
print("\n[6] Sector HHI concentration...")

equity_codes = fm[fm["category"] == "Equity"]["scheme_code"].tolist()
ph_eq = ph[ph["scheme_code"].isin(equity_codes)].copy()

hhi_rows = []
for code, grp in ph_eq.groupby("scheme_code"):
    weights = grp["weight_pct"] / 100
    hhi = (weights ** 2).sum()
    sector_top = grp.groupby("sector")["weight_pct"].sum().idxmax()
    hhi_rows.append({
        "scheme_code":  code,
        "scheme_name":  names.get(code, "")[:35],
        "hhi":          round(hhi, 4),
        "concentration": "High" if hhi > 0.15 else "Moderate" if hhi > 0.08 else "Low",
        "top_sector":   sector_top,
    })

hhi_df = pd.DataFrame(hhi_rows).sort_values("hhi", ascending=False)
hhi_df.to_csv(os.path.join(BASE, "hhi_concentration.csv"), index=False)
print(hhi_df[["scheme_name","hhi","concentration","top_sector"]].to_string(index=False))

# ─────────────────────────────────────────────────────────────────────────────
# Summary print
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("Deliverables:")
print("  var_cvar_report.csv")
print("  cohort_analysis.csv")
print("  sip_continuity.csv")
print("  hhi_concentration.csv")
print("  recommender.py")
print("  dashboard/rolling_sharpe_chart.png")
print("=" * 60)
