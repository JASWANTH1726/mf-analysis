import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore")

BASE   = os.path.dirname(__file__)
PROC   = os.path.join(BASE, "data", "processed")
RAW    = os.path.join(BASE, "data", "raw")
DASH   = os.path.join(BASE, "dashboard")
os.makedirs(DASH, exist_ok=True)

RF = 0.065 / 252   # daily risk-free rate (RBI repo 6.5%)

# ── load data ────────────────────────────────────────────────────────────────
nav = pd.read_csv(os.path.join(PROC, "nav_history_clean.csv"), parse_dates=["date"])
fm  = pd.read_csv(os.path.join(PROC, "fund_master_clean.csv"))
er  = pd.read_csv(os.path.join(PROC, "expense_ratio_clean.csv"))
bm  = pd.read_csv(os.path.join(PROC, "benchmark_data_clean.csv"), parse_dates=["date"])

nav = nav.sort_values(["scheme_code", "date"]).reset_index(drop=True)

scheme_names = fm.set_index("scheme_code")["scheme_name"].to_dict()
nav["name"]  = nav["scheme_code"].map(scheme_names)

# ── 1. daily returns ─────────────────────────────────────────────────────────
nav["daily_ret"] = nav.groupby("scheme_code")["nav"].pct_change()
nav = nav.dropna(subset=["daily_ret"])

# sanity check — returns should be roughly normal, mostly within ±5%
ret_stats = nav.groupby("scheme_code")["daily_ret"].agg(["mean", "std", "skew"])
print("daily return stats (sample):")
print(ret_stats.head(5).round(6))
extreme = nav[nav["daily_ret"].abs() > 0.05]
print(f"returns > ±5%: {len(extreme)} rows ({len(extreme)/len(nav)*100:.2f}%)")

# ── 2. CAGR ──────────────────────────────────────────────────────────────────
def cagr(series, years):
    if len(series) < 2:
        return np.nan
    end   = series.iloc[-1]
    start = series.iloc[max(0, len(series) - int(years * 252))]
    if start <= 0:
        return np.nan
    return (end / start) ** (1 / years) - 1

cagr_rows = []
for code, grp in nav.groupby("scheme_code"):
    grp = grp.sort_values("date")
    cagr_rows.append({
        "scheme_code": code,
        "scheme_name": scheme_names.get(code, str(code)),
        "cagr_1y":  round(cagr(grp["nav"], 1)  * 100, 2),
        "cagr_3y":  round(cagr(grp["nav"], 3)  * 100, 2),
        "cagr_5y":  round(cagr(grp["nav"], 5)  * 100, 2),
    })
cagr_df = pd.DataFrame(cagr_rows).sort_values("cagr_3y", ascending=False)
print("\nCAGR comparison (top 5 by 3yr):")
print(cagr_df[["scheme_name", "cagr_1y", "cagr_3y", "cagr_5y"]].head(5).to_string(index=False))

# ── 3. Sharpe ratio ──────────────────────────────────────────────────────────
def sharpe(rets):
    excess = rets - RF
    return (excess.mean() / rets.std()) * np.sqrt(252) if rets.std() > 0 else np.nan

sharpe_s = nav.groupby("scheme_code")["daily_ret"].apply(sharpe).rename("sharpe")
sharpe_df = sharpe_s.reset_index()
sharpe_df["scheme_name"] = sharpe_df["scheme_code"].map(scheme_names)
sharpe_df = sharpe_df.sort_values("sharpe", ascending=False).reset_index(drop=True)
sharpe_df["sharpe_rank"] = sharpe_df.index + 1
print("\nSharpe ratio ranking (top 5):")
print(sharpe_df[["scheme_name", "sharpe", "sharpe_rank"]].head(5).to_string(index=False))

# ── 4. Sortino ratio ─────────────────────────────────────────────────────────
def sortino(rets):
    excess   = rets - RF
    downside = rets[rets < 0].std()
    return (excess.mean() / downside) * np.sqrt(252) if downside > 0 else np.nan

sortino_s  = nav.groupby("scheme_code")["daily_ret"].apply(sortino).rename("sortino")
sortino_df = sortino_s.reset_index()
sortino_df["scheme_name"] = sortino_df["scheme_code"].map(scheme_names)
sortino_df = sortino_df.sort_values("sortino", ascending=False).reset_index(drop=True)
sortino_df["sortino_rank"] = sortino_df.index + 1

# ── 5. Alpha & Beta (OLS vs Nifty 100) ───────────────────────────────────────
bm_daily = bm.set_index("date")["nifty100"].pct_change().dropna().rename("bm_ret")

ab_rows = []
for code, grp in nav.groupby("scheme_code"):
    grp = grp.set_index("date")["daily_ret"].dropna()
    merged = pd.concat([grp, bm_daily], axis=1).dropna()
    if len(merged) < 30:
        continue
    slope, intercept, r, p, se = stats.linregress(merged["bm_ret"], merged["daily_ret"])
    ab_rows.append({
        "scheme_code": code,
        "scheme_name": scheme_names.get(code, str(code)),
        "beta":        round(slope, 4),
        "alpha_annual":round(intercept * 252 * 100, 4),   # annualised %
        "r_squared":   round(r**2, 4),
    })
alpha_beta = pd.DataFrame(ab_rows).sort_values("alpha_annual", ascending=False)
print("\nAlpha & Beta (top 5 by alpha):")
print(alpha_beta[["scheme_name", "alpha_annual", "beta", "r_squared"]].head(5).to_string(index=False))
alpha_beta.to_csv(os.path.join(BASE, "alpha_beta.csv"), index=False)
print("saved: alpha_beta.csv")

# ── 6. Maximum drawdown ───────────────────────────────────────────────────────
def max_drawdown(grp):
    grp = grp.sort_values("date")
    roll_max = grp["nav"].cummax()
    dd       = grp["nav"] / roll_max - 1
    min_idx  = dd.idxmin()
    peak_idx = grp.loc[:min_idx, "nav"].idxmax()
    return {
        "max_dd":      round(dd.min() * 100, 2),
        "trough_date": grp.loc[min_idx, "date"].date(),
        "peak_date":   grp.loc[peak_idx, "date"].date(),
    }

dd_rows = []
for code, grp in nav.groupby("scheme_code"):
    r = max_drawdown(grp)
    r["scheme_code"] = code
    r["scheme_name"] = scheme_names.get(code, str(code))
    dd_rows.append(r)
dd_df = pd.DataFrame(dd_rows).sort_values("max_dd")
print("\nWorst drawdowns (top 5):")
print(dd_df[["scheme_name", "max_dd", "peak_date", "trough_date"]].head(5).to_string(index=False))

# ── 7. Fund scorecard ─────────────────────────────────────────────────────────
sc = cagr_df[["scheme_code", "cagr_3y"]].copy()
sc = sc.merge(sharpe_df[["scheme_code", "sharpe", "sharpe_rank"]], on="scheme_code")
sc = sc.merge(sortino_df[["scheme_code", "sortino_rank"]], on="scheme_code")
sc = sc.merge(alpha_beta[["scheme_code", "alpha_annual"]], on="scheme_code")
sc = sc.merge(dd_df[["scheme_code", "max_dd"]], on="scheme_code")
sc = sc.merge(er[["scheme_code", "direct_ter"]], on="scheme_code", how="left")

n = len(sc)
sc["ret_rank"]   = sc["cagr_3y"].rank(ascending=True)
sc["alpha_rank"] = sc["alpha_annual"].rank(ascending=True)
sc["er_rank"]    = sc["direct_ter"].rank(ascending=False)   # lower TER = better
sc["dd_rank"]    = sc["max_dd"].rank(ascending=False)       # less negative = better

sc["score"] = (
    0.30 * sc["ret_rank"]   / n * 100 +
    0.25 * sc["sharpe_rank"]/ n * 100 +
    0.20 * sc["alpha_rank"] / n * 100 +
    0.15 * sc["er_rank"]    / n * 100 +
    0.10 * sc["dd_rank"]    / n * 100
)
sc["score"] = sc["score"].round(2)
sc["scheme_name"] = sc["scheme_code"].map(scheme_names)
scorecard = sc[["scheme_code", "scheme_name", "score", "cagr_3y", "sharpe",
                "alpha_annual", "direct_ter", "max_dd"]].sort_values("score", ascending=False)
scorecard = scorecard.reset_index(drop=True)
scorecard.index += 1
print("\nFund scorecard (top 10):")
print(scorecard.head(10).to_string())
scorecard.to_csv(os.path.join(BASE, "fund_scorecard.csv"))
print("saved: fund_scorecard.csv")

# ── 8. Benchmark comparison chart ────────────────────────────────────────────
top5_codes = scorecard.head(5)["scheme_code"].tolist()
cutoff     = nav["date"].max() - pd.DateOffset(years=3)

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.patch.set_facecolor("#0f1117")
for ax in axes:
    ax.set_facecolor("#12151f")
    ax.tick_params(colors="#90a4ae")
    ax.xaxis.label.set_color("#90a4ae")
    ax.yaxis.label.set_color("#90a4ae")
    ax.title.set_color("#4fc3f7")
    for spine in ax.spines.values():
        spine.set_edgecolor("#2a3550")

colors = ["#4fc3f7", "#66bb6a", "#ffa726", "#ef5350", "#ce93d8"]

# left: normalised NAV (rebased to 100)
ax = axes[0]
for i, code in enumerate(top5_codes):
    grp = nav[(nav["scheme_code"] == code) & (nav["date"] >= cutoff)].copy()
    grp = grp.set_index("date")["nav"]
    grp = grp / grp.iloc[0] * 100
    label = scheme_names.get(code, str(code)).split(" Fund")[0][:25]
    ax.plot(grp.index, grp.values, color=colors[i], linewidth=1.5, label=label)

# overlay Nifty 50 and Nifty 100
for col, lbl, ls in [("nifty50", "Nifty 50", "--"), ("nifty100", "Nifty 100", ":")]:
    bm_sub = bm[bm["date"] >= cutoff].set_index("date")[col].dropna()
    bm_sub = bm_sub / bm_sub.iloc[0] * 100
    ax.plot(bm_sub.index, bm_sub.values, color="#78909c", linewidth=1.2,
            linestyle=ls, label=lbl)

ax.set_title("Top 5 Funds vs Benchmark (3yr, rebased 100)")
ax.set_ylabel("Indexed NAV")
ax.legend(fontsize=7, facecolor="#1a1f35", labelcolor="white", framealpha=0.8)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f"))

# right: tracking error bar chart
ax2 = axes[1]
te_vals, te_labels = [], []
for code in top5_codes:
    grp = nav[(nav["scheme_code"] == code) & (nav["date"] >= cutoff)].copy()
    grp = grp.set_index("date")["daily_ret"]
    bm_sub = bm[bm["date"] >= cutoff].set_index("date")["nifty100"].pct_change().dropna()
    merged = pd.concat([grp, bm_sub.rename("bm")], axis=1).dropna()
    te = (merged["daily_ret"] - merged["bm"]).std() * np.sqrt(252) * 100
    te_vals.append(round(te, 2))
    te_labels.append(scheme_names.get(code, str(code)).split(" Fund")[0][:20])

bars = ax2.barh(te_labels, te_vals, color=colors[:len(te_vals)])
ax2.set_title("Tracking Error vs Nifty 100 (annualised %)")
ax2.set_xlabel("Tracking Error (%)")
for bar, val in zip(bars, te_vals):
    ax2.text(val + 0.1, bar.get_y() + bar.get_height()/2,
             f"{val:.1f}%", va="center", color="white", fontsize=9)

plt.tight_layout(pad=2)
chart_path = os.path.join(DASH, "benchmark_comparison.png")
plt.savefig(chart_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"saved: {chart_path}")

print("\nDay 3 EDA complete.")
print("Deliverables: alpha_beta.csv, fund_scorecard.csv, dashboard/benchmark_comparison.png")
