"""Dashboard builder: compose KPI pages and charts used in the dashboard folder.

Generates PNGs and a Dashboard PDF combining visual summaries.
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker
import seaborn as sns
from matplotlib.patches import FancyBboxPatch
from scipy import stats

warnings.filterwarnings("ignore")

BASE  = os.path.dirname(__file__)
PROC  = os.path.join(BASE, "data", "processed")
DASH  = os.path.join(BASE, "dashboard")
os.makedirs(DASH, exist_ok=True)

# ── palette ───────────────────────────────────────────────────────────────────
BG      = "#0d1117"
PANEL   = "#161b22"
BORDER  = "#30363d"
BLUE    = "#4fc3f7"
GREEN   = "#56d364"
AMBER   = "#e3b341"
RED     = "#f85149"
PURPLE  = "#bc8cff"
WHITE   = "#e6edf3"
GRAY    = "#8b949e"
ACCENT  = [BLUE, GREEN, AMBER, RED, PURPLE, "#ff7b72", "#79c0ff", "#ffa657"]

def style_ax(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=GRAY, labelsize=8)
    ax.xaxis.label.set_color(GRAY)
    ax.yaxis.label.set_color(GRAY)
    ax.title.set_color(BLUE)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)

def kpi_box(fig, x, y, w, h, label, value, color=BLUE):
    ax = fig.add_axes([x, y, w, h])
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(color)
        spine.set_linewidth(1.5)
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(0.5, 0.62, value, ha="center", va="center", fontsize=16,
            fontweight="bold", color=color, transform=ax.transAxes)
    ax.text(0.5, 0.22, label, ha="center", va="center", fontsize=8,
            color=GRAY, transform=ax.transAxes)
    return ax

# ── load data ─────────────────────────────────────────────────────────────────
nav  = pd.read_csv(os.path.join(PROC, "nav_history_clean.csv"), parse_dates=["date"])
fm   = pd.read_csv(os.path.join(PROC, "fund_master_clean.csv"))
er   = pd.read_csv(os.path.join(PROC, "expense_ratio_clean.csv"))
aum  = pd.read_csv(os.path.join(PROC, "aum_data_clean.csv"), parse_dates=["month"])
txn  = pd.read_csv(os.path.join(PROC, "investor_transactions_clean.csv"), parse_dates=["txn_date"])
bm   = pd.read_csv(os.path.join(PROC, "benchmark_data_clean.csv"), parse_dates=["date"])
sc   = pd.read_csv(os.path.join(BASE, "fund_scorecard.csv"), index_col=0)
ab   = pd.read_csv(os.path.join(BASE, "alpha_beta.csv"))

nav  = nav.sort_values(["scheme_code","date"]).reset_index(drop=True)
names = fm.set_index("scheme_code")["scheme_name"].to_dict()
nav["name"] = nav["scheme_code"].map(names)
nav["daily_ret"] = nav.groupby("scheme_code")["nav"].pct_change()
nav = nav.dropna(subset=["daily_ret"])

RF = 0.065 / 252

def sharpe(rets):
    excess = rets - RF
    return (excess.mean() / rets.std()) * np.sqrt(252) if rets.std() > 0 else np.nan

# ── PAGE 1: Industry Overview ─────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 11.25), facecolor=BG)
fig.text(0.5, 0.96, "Mutual Fund Industry Overview", ha="center", fontsize=20,
         fontweight="bold", color=WHITE)
fig.text(0.5, 0.935, "Bluestock Fintech  |  40 Schemes  |  2015–2024", ha="center",
         fontsize=11, color=GRAY)

# KPI cards
total_aum   = aum["aum_cr"].sum()
total_folios = aum["folios"].sum()
sip_amt     = txn[txn["txn_type"]=="SIP"]["amount"].sum()
schemes     = fm["scheme_code"].nunique()

kpi_box(fig, 0.04, 0.80, 0.20, 0.10, "Total AUM (Cr)", f"₹{total_aum/1e5:.1f}L Cr", BLUE)
kpi_box(fig, 0.27, 0.80, 0.20, 0.10, "SIP Inflows (Cr)", f"₹{sip_amt/1e7:.1f}K Cr", GREEN)
kpi_box(fig, 0.50, 0.80, 0.20, 0.10, "Total Folios", f"{total_folios/1e7:.2f} Cr", AMBER)
kpi_box(fig, 0.73, 0.80, 0.20, 0.10, "Schemes", str(schemes), PURPLE)

# AUM trend
ax1 = fig.add_axes([0.04, 0.44, 0.54, 0.30])
style_ax(ax1)
aum_trend = aum.groupby("month")["aum_cr"].sum().reset_index()
ax1.fill_between(aum_trend["month"], aum_trend["aum_cr"]/1e5, alpha=0.25, color=BLUE)
ax1.plot(aum_trend["month"], aum_trend["aum_cr"]/1e5, color=BLUE, linewidth=2)
ax1.set_title("Industry AUM Trend 2022–2024 (Lakh Cr)", fontsize=11)
ax1.set_ylabel("AUM (Lakh Cr)", color=GRAY)
ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))

# AUM by fund house
ax2 = fig.add_axes([0.62, 0.44, 0.35, 0.30])
style_ax(ax2)
aum_fm = aum.merge(fm[["scheme_code","fund_house"]], on="scheme_code")
aum_by_house = aum_fm.groupby("fund_house")["aum_cr"].sum().nlargest(10).sort_values()
bars = ax2.barh(aum_by_house.index, aum_by_house.values/1e5, color=ACCENT[:len(aum_by_house)])
ax2.set_title("AUM by Fund House (Top 10, Lakh Cr)", fontsize=11)
ax2.set_xlabel("AUM (Lakh Cr)", color=GRAY)
ax2.tick_params(axis="y", labelsize=7)
for bar, val in zip(bars, aum_by_house.values/1e5):
    ax2.text(val+0.01, bar.get_y()+bar.get_height()/2, f"{val:.1f}", va="center", color=WHITE, fontsize=7)

# Category pie
ax3 = fig.add_axes([0.04, 0.06, 0.28, 0.32])
style_ax(ax3)
cat = fm["category"].value_counts()
wedges, texts, autotexts = ax3.pie(cat.values, labels=cat.index, autopct="%1.0f%%",
    colors=ACCENT[:len(cat)], startangle=90, textprops={"color": WHITE, "fontsize": 8})
for at in autotexts:
    at.set_color(BG)
    at.set_fontsize(7)
ax3.set_title("Fund Category Mix", fontsize=11)

# Sub-category bar
ax4 = fig.add_axes([0.36, 0.06, 0.28, 0.32])
style_ax(ax4)
subcat = fm["sub_category"].value_counts().sort_values()
ax4.barh(subcat.index, subcat.values, color=BLUE, alpha=0.8)
ax4.set_title("Schemes by Sub-Category", fontsize=11)
ax4.set_xlabel("Count", color=GRAY)
ax4.tick_params(axis="y", labelsize=7)

# Risk grade donut
ax5 = fig.add_axes([0.68, 0.06, 0.28, 0.32])
style_ax(ax5)
risk = fm["risk_grade"].value_counts()
risk_colors = [GREEN, BLUE, AMBER, RED, PURPLE]
wedges2, _, at2 = ax5.pie(risk.values, labels=risk.index, autopct="%1.0f%%",
    colors=risk_colors[:len(risk)], startangle=90,
    wedgeprops={"width": 0.6}, textprops={"color": WHITE, "fontsize": 8})
for a in at2:
    a.set_color(BG); a.set_fontsize(7)
ax5.set_title("Risk Grade Distribution", fontsize=11)

plt.savefig(os.path.join(DASH, "page1_industry_overview.png"), dpi=150,
            bbox_inches="tight", facecolor=BG)
plt.close()
print("saved: page1_industry_overview.png")

# ── PAGE 2: Fund Performance ──────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 11.25), facecolor=BG)
fig.text(0.5, 0.96, "Fund Performance Analytics", ha="center", fontsize=20,
         fontweight="bold", color=WHITE)
fig.text(0.5, 0.935, "CAGR  |  Sharpe  |  Alpha  |  Scorecard  |  Benchmark", ha="center",
         fontsize=11, color=GRAY)

# Scatter: return vs risk
ax1 = fig.add_axes([0.04, 0.54, 0.42, 0.36])
style_ax(ax1)
vol_s  = nav.groupby("scheme_code")["daily_ret"].std() * np.sqrt(252) * 100
ret_s  = nav.groupby("scheme_code")["daily_ret"].mean() * 252 * 100
aum_s  = aum.groupby("scheme_code")["aum_cr"].mean()
merged = pd.DataFrame({"vol": vol_s, "ret": ret_s, "aum": aum_s}).dropna()
sc_map = sc.set_index("scheme_code")["score"]
merged["score"] = merged.index.map(sc_map)
sizes  = (merged["aum"] / merged["aum"].max() * 400 + 50).values
colors_sc = [GREEN if s >= 60 else AMBER if s >= 45 else RED for s in merged["score"].fillna(50)]
ax1.scatter(merged["vol"], merged["ret"], s=sizes, c=colors_sc, alpha=0.75, edgecolors=BORDER, linewidth=0.5)
ax1.axhline(0, color=GRAY, linewidth=0.8, linestyle="--")
ax1.set_title("Return vs Risk (bubble = AUM, colour = score)", fontsize=10)
ax1.set_xlabel("Annualised Volatility (%)")
ax1.set_ylabel("Annualised Return (%)")
for code, row in merged.iterrows():
    short = names.get(code,"").split(" Fund")[0][:12]
    ax1.annotate(short, (row["vol"], row["ret"]), fontsize=5, color=GRAY,
                 xytext=(3,3), textcoords="offset points")

# Scorecard table (top 10)
ax2 = fig.add_axes([0.50, 0.54, 0.47, 0.36])
style_ax(ax2)
ax2.axis("off")
top10 = sc.head(10)[["scheme_name","score","cagr_3y","sharpe","alpha_annual","max_dd"]].copy()
top10["scheme_name"] = top10["scheme_name"].str.replace(" Direct Growth","").str.replace(" Mutual Fund","").str[:28]
top10.columns = ["Fund","Score","CAGR 3Y","Sharpe","Alpha","Max DD"]
tbl = ax2.table(cellText=top10.values, colLabels=top10.columns,
                cellLoc="center", loc="center", bbox=[0,0,1,1])
tbl.auto_set_font_size(False)
tbl.set_fontsize(8)
for (r,c), cell in tbl.get_celld().items():
    cell.set_facecolor(PANEL if r % 2 == 0 else "#1c2128")
    cell.set_edgecolor(BORDER)
    cell.set_text_props(color=BLUE if r==0 else WHITE)
ax2.set_title("Fund Scorecard — Top 10", fontsize=11, color=BLUE, pad=10)

# NAV trend top 5
ax3 = fig.add_axes([0.04, 0.08, 0.42, 0.38])
style_ax(ax3)
top5 = sc.head(5)["scheme_code"].tolist()
cutoff = nav["date"].max() - pd.DateOffset(years=3)
for i, code in enumerate(top5):
    grp = nav[(nav["scheme_code"]==code) & (nav["date"]>=cutoff)].set_index("date")["nav"]
    grp = grp / grp.iloc[0] * 100
    label = names.get(code,"").split(" Fund")[0][:22]
    ax3.plot(grp.index, grp.values, color=ACCENT[i], linewidth=1.5, label=label)
for col, lbl, ls in [("nifty50","Nifty 50","--"),("nifty100","Nifty 100",":")]:
    b = bm[bm["date"]>=cutoff].set_index("date")[col].dropna()
    ax3.plot(b.index, b/b.iloc[0]*100, color=GRAY, linewidth=1.2, linestyle=ls, label=lbl)
ax3.set_title("Top 5 Funds vs Benchmark (3yr, rebased 100)", fontsize=10)
ax3.set_ylabel("Indexed NAV")
ax3.legend(fontsize=6, facecolor=PANEL, labelcolor=WHITE, framealpha=0.8)
ax3.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f"))

# Alpha bar
ax4 = fig.add_axes([0.50, 0.08, 0.47, 0.38])
style_ax(ax4)
ab_top = ab.nlargest(15, "alpha_annual")
short  = [names.get(c,"").replace(" Direct Growth","").replace(" Mutual Fund","")[:22] for c in ab_top["scheme_code"]]
colors_ab = [GREEN if v > 0 else RED for v in ab_top["alpha_annual"]]
bars = ax4.barh(short, ab_top["alpha_annual"], color=colors_ab, alpha=0.85)
ax4.axvline(0, color=GRAY, linewidth=0.8)
ax4.set_title("Alpha (Annualised %) — Top 15 Funds", fontsize=10)
ax4.set_xlabel("Alpha (%)")
ax4.tick_params(axis="y", labelsize=7)
for bar, val in zip(bars, ab_top["alpha_annual"]):
    ax4.text(val + 0.3, bar.get_y()+bar.get_height()/2, f"{val:.1f}%", va="center", color=WHITE, fontsize=7)

plt.savefig(os.path.join(DASH, "page2_fund_performance.png"), dpi=150,
            bbox_inches="tight", facecolor=BG)
plt.close()
print("saved: page2_fund_performance.png")

# ── PAGE 3: Investor Analytics ────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 11.25), facecolor=BG)
fig.text(0.5, 0.96, "Investor Analytics", ha="center", fontsize=20,
         fontweight="bold", color=WHITE)
fig.text(0.5, 0.935, "Transactions  |  KYC  |  State  |  Monthly Volume", ha="center",
         fontsize=11, color=GRAY)

# Txn type donut
ax1 = fig.add_axes([0.04, 0.54, 0.22, 0.36])
style_ax(ax1)
txn_type = txn["txn_type"].value_counts()
wedges, _, at = ax1.pie(txn_type.values, labels=txn_type.index, autopct="%1.1f%%",
    colors=[BLUE, GREEN, RED], startangle=90,
    wedgeprops={"width": 0.6}, textprops={"color": WHITE, "fontsize": 9})
for a in at:
    a.set_color(BG); a.set_fontsize(8)
ax1.set_title("SIP / Lumpsum / Redemption Split", fontsize=10)

# KYC bar
ax2 = fig.add_axes([0.30, 0.54, 0.22, 0.36])
style_ax(ax2)
kyc = txn["kyc_status"].value_counts()
kyc_colors = {"KYC_VERIFIED": GREEN, "KYC_PENDING": AMBER, "KYC_REJECTED": RED}
bars = ax2.bar(kyc.index, kyc.values, color=[kyc_colors.get(k, GRAY) for k in kyc.index])
ax2.set_title("KYC Status Breakdown", fontsize=10)
ax2.set_ylabel("Count")
ax2.tick_params(axis="x", labelsize=8)
for bar, val in zip(bars, kyc.values):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+5, str(val),
             ha="center", color=WHITE, fontsize=9)

# State bar
ax3 = fig.add_axes([0.56, 0.54, 0.40, 0.36])
style_ax(ax3)
state_amt = txn.groupby("state")["amount"].sum().nlargest(10).sort_values()
bars = ax3.barh(state_amt.index, state_amt.values/1e5, color=BLUE, alpha=0.8)
ax3.set_title("Transaction Amount by State — Top 10 (Lakhs)", fontsize=10)
ax3.set_xlabel("Amount (Lakhs)")
ax3.tick_params(axis="y", labelsize=8)
for bar, val in zip(bars, state_amt.values/1e5):
    ax3.text(val+0.5, bar.get_y()+bar.get_height()/2, f"₹{val:.0f}L", va="center", color=WHITE, fontsize=7)

# Monthly volume
ax4 = fig.add_axes([0.04, 0.08, 0.54, 0.38])
style_ax(ax4)
txn["month"] = txn["txn_date"].dt.to_period("M")
monthly = txn.groupby(["month","txn_type"])["amount"].sum().unstack(fill_value=0)
months_str = [str(m) for m in monthly.index]
x = np.arange(len(months_str))
w = 0.28
for i, (col, color) in enumerate(zip(monthly.columns, [BLUE, GREEN, RED])):
    ax4.bar(x + i*w, monthly[col].values/1e5, w, label=col, color=color, alpha=0.8)
ax4.set_title("Monthly Transaction Volume by Type (Lakhs)", fontsize=10)
ax4.set_ylabel("Amount (Lakhs)")
ax4.set_xticks(x[::6] + w)
ax4.set_xticklabels(months_str[::6], rotation=45, ha="right", fontsize=7)
ax4.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)

# Avg amount by fund house
ax5 = fig.add_axes([0.62, 0.08, 0.35, 0.38])
style_ax(ax5)
txn_fm = txn.merge(fm[["scheme_code","fund_house"]], on="scheme_code", how="left")
avg_amt = txn_fm.groupby("fund_house")["amount"].mean().nlargest(10).sort_values()
bars = ax5.barh(avg_amt.index, avg_amt.values/1000, color=AMBER, alpha=0.8)
ax5.set_title("Avg Transaction Amount by Fund House (K)", fontsize=10)
ax5.set_xlabel("Avg Amount (₹K)")
ax5.tick_params(axis="y", labelsize=7)
for bar, val in zip(bars, avg_amt.values/1000):
    ax5.text(val+0.1, bar.get_y()+bar.get_height()/2, f"₹{val:.1f}K", va="center", color=WHITE, fontsize=7)

plt.savefig(os.path.join(DASH, "page3_investor_analytics.png"), dpi=150,
            bbox_inches="tight", facecolor=BG)
plt.close()
print("saved: page3_investor_analytics.png")

# ── PAGE 4: SIP & Market Trends ───────────────────────────────────────────────
fig = plt.figure(figsize=(20, 11.25), facecolor=BG)
fig.text(0.5, 0.96, "SIP & Market Trends", ha="center", fontsize=20,
         fontweight="bold", color=WHITE)
fig.text(0.5, 0.935, "SIP Inflows  |  Nifty 50  |  Category Heatmap  |  Net Inflows", ha="center",
         fontsize=11, color=GRAY)

# Dual axis: SIP bar + Nifty 50 line
ax1 = fig.add_axes([0.04, 0.54, 0.54, 0.36])
style_ax(ax1)
sip_monthly = txn[txn["txn_type"]=="SIP"].groupby("month")["amount"].sum().reset_index()
sip_monthly["month_dt"] = sip_monthly["month"].dt.to_timestamp()
bm_monthly  = bm.set_index("date")["nifty50"].resample("MS").last().reset_index()
bm_monthly.columns = ["date","nifty50"]

ax1b = ax1.twinx()
ax1b.set_facecolor(PANEL)
ax1b.tick_params(colors=GRAY, labelsize=8)
ax1b.yaxis.label.set_color(GRAY)
ax1b.spines["right"].set_edgecolor(BORDER)

ax1.bar(sip_monthly["month_dt"], sip_monthly["amount"]/1e5, width=20,
        color=BLUE, alpha=0.7, label="SIP Inflow")
ax1b.plot(bm_monthly["date"], bm_monthly["nifty50"], color=AMBER, linewidth=2, label="Nifty 50")
ax1.set_title("SIP Inflows (Lakhs) vs Nifty 50 — 2020–2024", fontsize=10)
ax1.set_ylabel("SIP Amount (Lakhs)", color=BLUE)
ax1b.set_ylabel("Nifty 50", color=AMBER)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1b.get_legend_handles_labels()
ax1.legend(lines1+lines2, labels1+labels2, fontsize=8, facecolor=PANEL, labelcolor=WHITE)

# Category inflow heatmap
ax2 = fig.add_axes([0.62, 0.54, 0.35, 0.36])
style_ax(ax2)
txn_cat = txn.merge(fm[["scheme_code","sub_category"]], on="scheme_code", how="left")
txn_cat["year"] = txn_cat["txn_date"].dt.year
heat = txn_cat.groupby(["sub_category","year"])["amount"].sum().unstack(fill_value=0) / 1e5
sns.heatmap(heat, ax=ax2, cmap="YlOrRd", annot=True, fmt=".0f",
            linewidths=0.5, linecolor=BORDER, annot_kws={"size": 7},
            cbar_kws={"shrink": 0.8})
ax2.set_title("Category Inflow Heatmap (Lakhs)", fontsize=10)
ax2.tick_params(axis="x", labelsize=7, rotation=45)
ax2.tick_params(axis="y", labelsize=7)

# Top 5 categories net inflow
ax3 = fig.add_axes([0.04, 0.08, 0.42, 0.38])
style_ax(ax3)
txn_cat["net"] = txn_cat.apply(lambda r: r["amount"] if r["txn_type"]!="Redemption" else -r["amount"], axis=1)
net_cat = txn_cat.groupby("sub_category")["net"].sum().nlargest(8).sort_values()
colors_net = [GREEN if v > 0 else RED for v in net_cat.values]
bars = ax3.barh(net_cat.index, net_cat.values/1e5, color=colors_net, alpha=0.85)
ax3.axvline(0, color=GRAY, linewidth=0.8)
ax3.set_title("Net Inflow by Category (Lakhs)", fontsize=10)
ax3.set_xlabel("Net Amount (Lakhs)")
ax3.tick_params(axis="y", labelsize=8)
for bar, val in zip(bars, net_cat.values/1e5):
    ax3.text(val + (1 if val >= 0 else -1), bar.get_y()+bar.get_height()/2,
             f"₹{val:.0f}L", va="center", color=WHITE, fontsize=7)

# SIP YoY trend
ax4 = fig.add_axes([0.50, 0.08, 0.47, 0.38])
style_ax(ax4)
sip_yr = txn[txn["txn_type"]=="SIP"].copy()
sip_yr["year"] = sip_yr["txn_date"].dt.year
sip_yoy = sip_yr.groupby("year").agg(count=("amount","count"), total=("amount","sum")).reset_index()
ax4b = ax4.twinx()
ax4b.set_facecolor(PANEL)
ax4b.tick_params(colors=GRAY, labelsize=8)
ax4b.spines["right"].set_edgecolor(BORDER)
ax4.bar(sip_yoy["year"], sip_yoy["total"]/1e5, color=BLUE, alpha=0.7, label="SIP Amount (L)")
ax4b.plot(sip_yoy["year"], sip_yoy["count"], color=GREEN, linewidth=2, marker="o", label="SIP Count")
ax4.set_title("SIP Year-over-Year — Amount vs Count", fontsize=10)
ax4.set_ylabel("Amount (Lakhs)", color=BLUE)
ax4b.set_ylabel("Count", color=GREEN)
ax4.set_xticks(sip_yoy["year"])
lines1, labels1 = ax4.get_legend_handles_labels()
lines2, labels2 = ax4b.get_legend_handles_labels()
ax4.legend(lines1+lines2, labels1+labels2, fontsize=8, facecolor=PANEL, labelcolor=WHITE)

plt.savefig(os.path.join(DASH, "page4_sip_market_trends.png"), dpi=150,
            bbox_inches="tight", facecolor=BG)
plt.close()
print("saved: page4_sip_market_trends.png")

# ── combine into PDF ──────────────────────────────────────────────────────────
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

pages = [
    "page1_industry_overview.png",
    "page2_fund_performance.png",
    "page3_investor_analytics.png",
    "page4_sip_market_trends.png",
]

pdf_path = os.path.join(DASH, "Dashboard.pdf")
with PdfPages(pdf_path) as pdf:
    for p in pages:
        img = Image.open(os.path.join(DASH, p))
        fig, ax = plt.subplots(figsize=(20, 11.25))
        ax.imshow(img)
        ax.axis("off")
        fig.patch.set_facecolor(BG)
        pdf.savefig(fig, bbox_inches="tight", facecolor=BG)
        plt.close()

print(f"saved: {pdf_path}")
print("\nDone. Deliverables:")
print("  dashboard/page1_industry_overview.png")
print("  dashboard/page2_fund_performance.png")
print("  dashboard/page3_investor_analytics.png")
print("  dashboard/page4_sip_market_trends.png")
print("  dashboard/Dashboard.pdf")
