# Power BI Dashboard Setup Guide
## Vendor Performance & Procurement Cost Analysis

---

## Step 1 — Load the data

1. Open Power BI Desktop (free download: powerbi.microsoft.com)
2. Click **Get Data → Text/CSV**
3. Load these 3 files from the `data/` folder:
   - `vendor_summary.csv`
   - `purchase_orders.csv`
   - `monthly_trends.csv`
4. Click **Load** for each

---

## Step 2 — Create relationships

Go to **Model view** (left sidebar icon):

| From table          | Column      | To table     | Column    |
|---------------------|-------------|--------------|-----------|
| purchase_orders     | vendor_id   | vendor_info  | vendor_id |
| monthly_trends      | vendor_name | vendor_info  | vendor_name |

---

## Step 3 — Create these DAX measures

In the **Data view**, click **New Measure** and add each:

```dax
Total Spend INR = SUM(purchase_orders[order_value_inr])

Avg Fill Rate % = AVERAGE(purchase_orders[fill_rate_pct])

Avg Lead Variance = AVERAGE(purchase_orders[lead_variance_days])

Total Emergency Cost INR = SUM(purchase_orders[emergency_purchase_inr])

On Time % =
DIVIDE(
    COUNTROWS(FILTER(purchase_orders, purchase_orders[on_time] = 1)),
    COUNTROWS(purchase_orders),
    0
) * 100

Weighted Score =
CALCULATE(AVERAGE(vendor_summary[weighted_score]))
```

---

## Step 4 — Build these 5 visuals

### Visual 1 — KPI Cards (top row)
- **Card** visual × 4
  - Total Spend INR → format as ₹ currency
  - Total Emergency Cost INR → format as ₹
  - Avg Fill Rate %
  - On Time %

### Visual 2 — Vendor Scorecard Bar Chart
- Visual: **Horizontal Bar Chart**
- Y-axis: `vendor_name` (from vendor_summary)
- X-axis: `weighted_score`
- Color: conditional formatting by score (green = high, red = low)
- Title: "Overall Vendor Performance Score"

### Visual 3 — Lead Time Variance by Vendor
- Visual: **Clustered Bar Chart**
- X-axis: `vendor_name`
- Y-axis: `avg_lead_variance_days`
- Add constant line at 0 (Reference line)
- Title: "Average Days Late vs 5-Day SLA Commitment"

### Visual 4 — Emergency Cost by Vendor
- Visual: **Bar Chart**
- X-axis: `vendor_name`
- Y-axis: `emergency_cost_inr`
- Color: Red gradient
- Data label: ₹ format
- Title: "Annual Emergency Procurement Cost (₹)"

### Visual 5 — Monthly Lead Trend (Line Chart)
- Visual: **Line Chart**
- X-axis: `month` (from monthly_trends)
- Y-axis: `avg_lead_variance`
- Legend: `vendor_name`
- Title: "Monthly Lead Time Variance Trend — All Vendors"

---

## Step 5 — Add slicers (filters)

Add **Slicer** visuals for:
- `vendor_name` (dropdown)
- `category` (list: Cotton, Synthetic, Silk, Mixed)
- `month` (slider: 1–12)

---

## Step 6 — Format the dashboard

- Background: White (#FFFFFF)
- Title text colour: Navy (#1F3864)
- Accent bars: Blue (#2E6DA4), Red (#C0392B) for warnings
- Currency format: ₹ #,##0 for all INR values
- Page title: "Vendor Performance Dashboard · KS Textile Shop · Tamil Nadu"

---

## Step 7 — Export

- **Save as**: `vendor_dashboard.pbix`
- **Export to PDF**: File → Export → PDF
- Take a screenshot of the final dashboard for your GitHub README

---

## Notes for recruiters

All data in this project is based on real supply chain coordination patterns
from 2+ years managing 5+ suppliers at KS Textile Shop, Tamil Nadu, India.
Figures are illustrative but modelled on actual Indian textile retail procurement
cycles. Currency is INR throughout.
