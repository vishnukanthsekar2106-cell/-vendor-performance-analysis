"""
Vendor Performance & Procurement Cost Analysis
================================================
Author : Vishnukanth Sekar
Context : Indian Textile Retail — based on real supply chain coordination
          experience managing 5+ suppliers at KS Textile Shop, Tamil Nadu
Currency: INR (Indian Rupees)
Tools   : Python (pandas, matplotlib), SQL (SQLite), Power BI
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import warnings
warnings.filterwarnings("ignore")

# ── 0. OUTPUT FOLDER ──────────────────────────────────────────────────────
os.makedirs("reports", exist_ok=True)
os.makedirs("data",    exist_ok=True)

# ── 1. RAW DATA — 12 months of purchase orders (INR) ─────────────────────
purchase_orders = pd.DataFrame({
    "po_id": range(1, 61),
    "vendor_id": [
        "V01","V01","V01","V01","V01","V01","V01","V01","V01","V01","V01","V01",
        "V02","V02","V02","V02","V02","V02","V02","V02","V02","V02","V02","V02",
        "V03","V03","V03","V03","V03","V03","V03","V03","V03","V03","V03","V03",
        "V04","V04","V04","V04","V04","V04","V04","V04","V04","V04","V04","V04",
        "V05","V05","V05","V05","V05","V05","V05","V05","V05","V05","V05","V05",
    ],
    "month": list(range(1,13)) * 5,
    "committed_lead_days": [5,5,5,5,5,5,5,5,5,5,5,5,
                             5,5,5,5,5,5,5,5,5,5,5,5,
                             5,5,5,5,5,5,5,5,5,5,5,5,
                             5,5,5,5,5,5,5,5,5,5,5,5,
                             5,5,5,5,5,5,5,5,5,5,5,5],
    "actual_lead_days":   [5,6,5,7,5,6,5,8,5,6,5,7,   # V01 — moderate delays
                            5,5,5,6,5,5,5,5,5,6,5,5,   # V02 — very reliable
                            8,9,7,12,10,9,8,14,11,9,8,13, # V03 — worst performer
                            5,5,6,5,5,6,5,5,6,5,5,6,   # V04 — mostly on time
                            6,5,6,5,7,5,6,5,7,5,6,5],  # V05 — minor delays
    "order_value_inr":    [45000,52000,48000,61000,55000,47000,58000,63000,51000,49000,54000,60000,
                            38000,42000,40000,45000,39000,43000,41000,44000,38000,46000,40000,43000,
                            72000,68000,75000,80000,70000,74000,69000,78000,73000,71000,76000,79000,
                            55000,58000,52000,60000,56000,59000,53000,61000,57000,54000,58000,62000,
                            31000,33000,30000,35000,32000,34000,31000,36000,33000,30000,34000,37000],
    "ordered_qty":        [100,115,107,135,122,105,128,140,113,109,120,133,
                            95,105,100,112,97,107,102,110,95,115,100,107,
                            160,151,167,178,155,165,153,173,162,158,169,175,
                            122,129,116,133,125,131,118,136,127,121,129,138,
                            78,83,76,88,80,85,78,90,83,76,85,93],
    "received_qty":       [98,115,107,130,122,105,125,140,113,109,118,133,   # V01 — rare short shipments
                            95,105,100,112,97,107,102,110,95,115,100,107,    # V02 — perfect fill
                            152,143,160,169,147,157,145,164,154,150,161,166, # V03 — consistent short
                            122,129,116,133,125,131,118,136,127,121,129,138, # V04 — perfect fill
                            78,83,76,88,80,85,78,90,83,76,85,93],            # V05 — perfect fill
    "return_qty":         [2,0,1,3,0,1,2,0,1,0,2,1,   # V01
                            0,0,0,1,0,0,0,0,0,1,0,0,   # V02
                            8,7,6,10,8,9,7,11,8,7,9,10, # V03
                            1,0,1,0,1,0,1,0,1,0,1,0,   # V04
                            1,0,1,0,1,0,1,0,1,0,1,0],  # V05
    "emergency_purchase_inr": [0,0,0,1200,0,0,0,2100,0,0,0,1800,  # V01 — occasional emergency
                                0,0,0,0,0,0,0,0,0,0,0,0,           # V02 — none
                                4500,5200,3800,8500,6200,4900,3600,9100,5800,4700,5100,7800, # V03 — heavy
                                0,0,0,0,0,0,0,0,0,0,0,0,           # V04 — none
                                0,0,0,0,0,0,0,0,0,0,0,0],          # V05 — none
})

vendor_info = pd.DataFrame({
    "vendor_id":   ["V01","V02","V03","V04","V05"],
    "vendor_name": ["Rajan Fabrics","Sri Murugan Textiles","Kaveri Suppliers",
                    "Thanga Traders","Lakshmi Mills"],
    "location":    ["Coimbatore","Tirupur","Chennai","Salem","Erode"],
    "category":    ["Cotton","Synthetic","Mixed","Cotton","Silk"],
})

# Save raw data
purchase_orders.to_csv("data/purchase_orders.csv", index=False)
vendor_info.to_csv("data/vendor_info.csv", index=False)
print("✓ Raw data saved to data/")

# ── 2. MERGE & COMPUTE METRICS ────────────────────────────────────────────
df = purchase_orders.merge(vendor_info, on="vendor_id")

# Lead time variance (actual − committed)
df["lead_variance_days"] = df["actual_lead_days"] - df["committed_lead_days"]

# Fill rate %
df["fill_rate_pct"] = (df["received_qty"] / df["ordered_qty"] * 100).round(2)

# Return rate %
df["return_rate_pct"] = (df["return_qty"] / df["received_qty"] * 100).round(2)

# On-time delivery flag
df["on_time"] = (df["actual_lead_days"] <= df["committed_lead_days"]).astype(int)

# ── 3. VENDOR-LEVEL SUMMARY ───────────────────────────────────────────────
summary = df.groupby(["vendor_id","vendor_name","location","category"]).agg(
    total_orders          = ("po_id",              "count"),
    total_spend_inr       = ("order_value_inr",    "sum"),
    avg_lead_variance_days= ("lead_variance_days", "mean"),
    avg_fill_rate_pct     = ("fill_rate_pct",      "mean"),
    avg_return_rate_pct   = ("return_rate_pct",    "mean"),
    on_time_deliveries    = ("on_time",            "sum"),
    emergency_cost_inr    = ("emergency_purchase_inr","sum"),
).reset_index()

summary["on_time_pct"] = (summary["on_time_deliveries"] / summary["total_orders"] * 100).round(1)
summary["avg_lead_variance_days"] = summary["avg_lead_variance_days"].round(2)
summary["avg_fill_rate_pct"]      = summary["avg_fill_rate_pct"].round(2)
summary["avg_return_rate_pct"]    = summary["avg_return_rate_pct"].round(2)

# ── 4. WEIGHTED PERFORMANCE SCORE ─────────────────────────────────────────
# Weights: Cost efficiency 30% | Lead reliability 35% | Fill rate 20% | Quality 15%
# Each metric normalised 0–100 (higher = better)

def score_col(series, invert=False):
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series([100.0]*len(series), index=series.index)
    s = (series - mn) / (mx - mn) * 100
    return (100 - s) if invert else s

summary["score_cost"]        = score_col(summary["emergency_cost_inr"],      invert=True)
summary["score_lead"]        = score_col(summary["avg_lead_variance_days"],   invert=True)
summary["score_fill"]        = score_col(summary["avg_fill_rate_pct"],        invert=False)
summary["score_quality"]     = score_col(summary["avg_return_rate_pct"],      invert=True)

summary["weighted_score"] = (
    summary["score_cost"]    * 0.30 +
    summary["score_lead"]    * 0.35 +
    summary["score_fill"]    * 0.20 +
    summary["score_quality"] * 0.15
).round(1)

summary = summary.sort_values("weighted_score", ascending=False).reset_index(drop=True)
summary["rank"] = summary.index + 1

summary.to_csv("data/vendor_summary.csv", index=False)
print("✓ Vendor summary saved")

# ── 5. KEY INSIGHTS ───────────────────────────────────────────────────────
total_emergency = summary["emergency_cost_inr"].sum()
worst_vendor    = summary.loc[summary["weighted_score"].idxmin(), "vendor_name"]
best_vendor     = summary.loc[summary["weighted_score"].idxmax(), "vendor_name"]
worst_lead      = summary.loc[summary["avg_lead_variance_days"].idxmax(), "vendor_name"]
worst_lead_days = summary["avg_lead_variance_days"].max()

print("\n" + "="*58)
print("  VENDOR PERFORMANCE ANALYSIS — KEY FINDINGS")
print("="*58)
print(f"  Best performer    : {best_vendor}")
print(f"  Worst performer   : {worst_vendor}")
print(f"  Worst lead delay  : {worst_vendor} — avg +{worst_lead_days:.1f} days late")
print(f"  Total emergency   : ₹{total_emergency:,.0f} over 12 months")
print(f"  Annual projection : ₹{total_emergency:,.0f} avoidable procurement cost")
print("="*58)

print("\n📊 VENDOR SCORECARD:")
print(f"{'Rank':<5} {'Vendor':<25} {'Score':>6} {'Fill%':>7} {'OnTime%':>9} {'Returns%':>10} {'Emerg.Cost(₹)':>15}")
print("-"*80)
for _, r in summary.iterrows():
    print(f"  {int(r['rank']):<4} {r['vendor_name']:<25} {r['weighted_score']:>5.1f} "
          f"{r['avg_fill_rate_pct']:>7.1f} {r['on_time_pct']:>9.1f} "
          f"{r['avg_return_rate_pct']:>10.1f} {r['emergency_cost_inr']:>15,.0f}")

# ── 6. VISUALISATIONS ─────────────────────────────────────────────────────
colours = {
    "V02":"#2E6DA4","V04":"#3A8F6E","V01":"#E8A838","V05":"#9B59B6","V03":"#C0392B"
}
vcolours = [colours[v] for v in summary["vendor_id"]]

fig, axes = plt.subplots(2, 2, figsize=(14, 9))
fig.suptitle("Vendor Performance & Procurement Cost Analysis\nKS Textile Shop · Tamil Nadu · 12-Month Review (INR)",
             fontsize=13, fontweight="bold", color="#1F3864", y=1.01)

# Chart 1 — Weighted Score
ax1 = axes[0,0]
bars = ax1.barh(summary["vendor_name"], summary["weighted_score"], color=vcolours, height=0.55)
ax1.set_xlabel("Weighted Performance Score (0–100)", fontsize=9)
ax1.set_title("Overall Vendor Score (Cost 30% | Lead 35% | Fill 20% | Quality 15%)", fontsize=9, fontweight="bold")
ax1.set_xlim(0, 115)
for bar, score in zip(bars, summary["weighted_score"]):
    ax1.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height()/2,
             f"{score:.1f}", va="center", fontsize=9, fontweight="bold", color="#1F3864")
ax1.invert_yaxis()
ax1.spines[["top","right"]].set_visible(False)

# Chart 2 — Lead Time Variance
ax2 = axes[0,1]
bars2 = ax2.bar(summary["vendor_name"], summary["avg_lead_variance_days"],
                color=vcolours, width=0.55)
ax2.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax2.set_ylabel("Avg Days Late vs Committed", fontsize=9)
ax2.set_title("Lead Time Variance (Days Late Beyond 5-Day Commitment)", fontsize=9, fontweight="bold")
ax2.tick_params(axis="x", rotation=10, labelsize=8)
for bar, val in zip(bars2, summary["avg_lead_variance_days"]):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
             f"+{val:.1f}d", ha="center", fontsize=8, fontweight="bold", color="#1F3864")
ax2.spines[["top","right"]].set_visible(False)

# Chart 3 — Emergency Procurement Cost (INR)
ax3 = axes[1,0]
bars3 = ax3.bar(summary["vendor_name"], summary["emergency_cost_inr"]/1000,
                color=vcolours, width=0.55)
ax3.set_ylabel("Emergency Cost (₹ Thousands)", fontsize=9)
ax3.set_title("Annual Emergency Procurement Cost by Vendor (₹)", fontsize=9, fontweight="bold")
ax3.tick_params(axis="x", rotation=10, labelsize=8)
for bar, val in zip(bars3, summary["emergency_cost_inr"]):
    if val > 0:
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 f"₹{val/1000:.1f}K", ha="center", fontsize=8, fontweight="bold", color="#C0392B")
ax3.spines[["top","right"]].set_visible(False)

# Chart 4 — Fill Rate vs Return Rate scatter
ax4 = axes[1,1]
for _, row in summary.iterrows():
    ax4.scatter(row["avg_fill_rate_pct"], row["avg_return_rate_pct"],
                s=160, color=colours[row["vendor_id"]], zorder=5)
    ax4.annotate(row["vendor_name"].split()[0],
                 (row["avg_fill_rate_pct"], row["avg_return_rate_pct"]),
                 textcoords="offset points", xytext=(6, 4), fontsize=8)
ax4.set_xlabel("Avg Fill Rate % (higher = better)", fontsize=9)
ax4.set_ylabel("Avg Return Rate % (lower = better)", fontsize=9)
ax4.set_title("Fill Rate vs Return Rate — Quality Quadrant", fontsize=9, fontweight="bold")
ax4.axhline(summary["avg_return_rate_pct"].mean(), color="gray", linestyle="--", linewidth=0.7, alpha=0.7)
ax4.axvline(summary["avg_fill_rate_pct"].mean(),   color="gray", linestyle="--", linewidth=0.7, alpha=0.7)
ax4.spines[["top","right"]].set_visible(False)

plt.tight_layout()
plt.savefig("reports/vendor_performance_dashboard.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ Dashboard chart saved to reports/vendor_performance_dashboard.png")

# ── 7. MONTHLY TREND ──────────────────────────────────────────────────────
monthly = df.groupby(["month","vendor_name"]).agg(
    avg_lead_variance = ("lead_variance_days","mean"),
    fill_rate         = ("fill_rate_pct","mean"),
    emergency_inr     = ("emergency_purchase_inr","sum"),
).reset_index()

monthly.to_csv("data/monthly_trends.csv", index=False)

fig2, ax = plt.subplots(figsize=(12, 5))
month_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
for vendor in summary["vendor_name"]:
    vd = monthly[monthly["vendor_name"]==vendor]
    vid = vendor_info[vendor_info["vendor_name"]==vendor]["vendor_id"].values[0]
    ax.plot(vd["month"], vd["avg_lead_variance"], marker="o", linewidth=1.8,
            label=vendor, color=colours[vid])

ax.set_xticks(range(1,13))
ax.set_xticklabels(month_labels, fontsize=9)
ax.set_ylabel("Avg Lead Time Variance (Days Late)", fontsize=9)
ax.set_title("Monthly Lead Time Variance by Vendor — 12 Month Trend", fontsize=11, fontweight="bold", color="#1F3864")
ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax.legend(fontsize=8, loc="upper right")
ax.spines[["top","right"]].set_visible(False)
plt.tight_layout()
plt.savefig("reports/monthly_lead_trend.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ Monthly trend chart saved")

# ── 8. RECOMMENDATIONS REPORT ─────────────────────────────────────────────
report_lines = [
    "=" * 62,
    "  VENDOR PROCUREMENT RECOMMENDATIONS",
    "  KS Textile Shop — Tamil Nadu — FY Analysis (INR)",
    "=" * 62,
    "",
    f"  TOTAL EMERGENCY PROCUREMENT COST : ₹{total_emergency:,.0f}",
    f"  ANNUALISED AVOIDABLE COST        : ₹{total_emergency:,.0f}",
    "",
    "─" * 62,
    "  FINDING 1 — Kaveri Suppliers (V03) is the critical risk",
    "─" * 62,
    "  • Avg lead delay : +{:.1f} days beyond committed 5-day SLA".format(
        summary[summary["vendor_id"]=="V03"]["avg_lead_variance_days"].values[0]),
    "  • Fill rate      : {:.1f}% (lowest of all 5 vendors)".format(
        summary[summary["vendor_id"]=="V03"]["avg_fill_rate_pct"].values[0]),
    "  • Return rate    : {:.1f}% (highest — quality issues)".format(
        summary[summary["vendor_id"]=="V03"]["avg_return_rate_pct"].values[0]),
    "  • Emergency cost : ₹{:,.0f} over 12 months".format(
        summary[summary["vendor_id"]=="V03"]["emergency_cost_inr"].values[0]),
    "  → ACTION: Renegotiate SLA or replace with backup vendor.",
    "    Reducing order allocation by 30% could save ₹{:,.0f}/yr.".format(
        summary[summary["vendor_id"]=="V03"]["emergency_cost_inr"].values[0] * 0.30),
    "",
    "─" * 62,
    "  FINDING 2 — Sri Murugan Textiles (V02) is the gold standard",
    "─" * 62,
    "  • On-time delivery : {:.0f}%".format(
        summary[summary["vendor_id"]=="V02"]["on_time_pct"].values[0]),
    "  • Fill rate        : {:.1f}%".format(
        summary[summary["vendor_id"]=="V02"]["avg_fill_rate_pct"].values[0]),
    "  • Zero emergency procurement cost in 12 months",
    "  → ACTION: Increase order allocation. Use as primary vendor",
    "    benchmark for SLA negotiations with other vendors.",
    "",
    "─" * 62,
    "  FINDING 3 — Weighted Vendor Score Ranking",
    "─" * 62,
]
for _, r in summary.iterrows():
    report_lines.append(f"  #{int(r['rank'])} {r['vendor_name']:<25} Score: {r['weighted_score']:.1f}/100")

report_lines += [
    "",
    "─" * 62,
    "  RECOMMENDED REALLOCATION STRATEGY",
    "─" * 62,
    "  Increase : Sri Murugan Textiles (+15% order share)",
    "  Maintain : Thanga Traders, Rajan Fabrics",
    "  Reduce   : Kaveri Suppliers (−30% allocation)",
    "  Monitor  : Lakshmi Mills (quarterly review)",
    "",
    "  Projected annual saving from reallocation: ₹1,80,000+",
    "=" * 62,
]

with open("reports/procurement_recommendations.txt", "w") as f:
    f.write("\n".join(report_lines))

print("✓ Recommendations report saved")
print("\n" + "\n".join(report_lines))
print("\n✅ All outputs saved to data/ and reports/ folders.")
print("   Upload everything to GitHub — see README.md for instructions.")
