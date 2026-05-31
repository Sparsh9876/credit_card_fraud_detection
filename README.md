# 💳 Credit Card Fraud Detection — End-to-End Data Analytics Project

![Status](https://img.shields.io/badge/Status-Completed-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![PowerBI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

> An industry-level end-to-end data analytics project detecting fraudulent credit card transactions using **PostgreSQL**, **Python**, and **Power BI** — built to mirror real workflows used at companies like American Express, Deutsche Bank, Deloitte, and Accenture.

---

## 📸 Dashboard Preview

<table>
<tr>
<th>Page 1 — Fraud Overview</th>
<th>Page 2 — Pattern Analysis</th>
<th>Page 3 — Transaction Details</th>
</tr>
<tr>
<td><img src="https://github.com/user-attachments/assets/58e5826f-f1e7-40de-8e21-97e0b050eb4e" width="300"></td>
<td><img src="https://github.com/user-attachments/assets/631d2f20-26db-422a-826c-52cf24356506" width="300"></td>
<td><img src="https://github.com/user-attachments/assets/30a64e87-cf93-4aa1-837a-d871eea08093" width="300"></td>
</tr>
</table>

---

## 📌 Project Overview

This project analyses **1,000 real credit card transactions** to identify fraud patterns, build KPIs, and deliver actionable business recommendations. The workflow mirrors exactly how data analysts work at financial institutions — raw data enters a database, Python handles the analysis, and Power BI delivers the story to business stakeholders.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **PostgreSQL 15 + pgAdmin 4** | Database storage, table design, SQL analysis |
| **Python 3.10+** | Data pipeline, cleaning, EDA, visualisation |
| **pandas** | Data manipulation and aggregation |
| **numpy** | Numerical operations and outlier detection |
| **matplotlib + seaborn** | 9 publication-quality charts |
| **SQLAlchemy + psycopg2** | Python ↔ PostgreSQL connection |
| **Power BI Desktop** | 3-page interactive dashboard with slicers |

---

## 🔄 Project Workflow

```
Raw CSV (1,000 rows)
    ↓
PostgreSQL Database
(pgAdmin 4 — table creation, import, SQL queries)
    ↓
Python Analysis
(data cleaning → feature engineering → EDA → 9 charts)
    ↓
Power BI Dashboard
(3 pages → KPIs → slicers → business insights)
    ↓
Business Recommendations
```

---

## 📁 Project Structure

```
credit-card-fraud-detection/
│
├── README.md
├── requirements.txt
│
├── data/
│   └── credit_card_fraud_detection_dataset.csv
│
├── sql/
│   └── 01_setup_database.sql
│
├── python/
│   └── fraud_analysis_postgresql.py
│
├── outputs/
│   ├── 01_fraud_vs_legitimate.png
│   ├── 02_fraud_by_category.png
│   ├── 03_amount_distribution.png
│   ├── 04_fraud_by_age_group.png
│   ├── 05_failed_attempts_vs_fraud.png
│   ├── 06_heatmap_category_time.png
│   ├── 07_treemap.png
│   ├── 08_scatter_plot.png
│   ├── 09_hourly_trend.png
│   └── fraud_clean_for_powerbi.csv
│
└── dashboard/
    ├── #page1- Overview.png
    ├── #page2- analysis.png
    └── #page3- transaction details.png
```

---

## 📊 Dataset

| Property | Value |
|---|---|
| Total Rows | 1,000 transactions |
| Total Columns | 13 features |
| Target Variable | `Fraud` (1 = Fraud, 0 = Legitimate) |
| Key Features | Transaction Amount, Merchant Category, City, Failed Attempts, Card Present, International Transaction |

---

## 📈 Key Results & Findings

| # | Finding | Value |
|---|---|---|
| 1 | Overall Fraud Rate | **49.1%** |
| 2 | Total Fraud Amount | **$1,473,833** |
| 3 | Highest Fraud Category | **Online Shopping (62.3%)** |
| 4 | Strongest Fraud Predictor | **≥3 Failed Attempts (75.6%)** |
| 5 | International Fraud Rate | **61.6%** |
| 6 | Highest Risk City | **Chennai (54.6%)** |
| 7 | Peak Fraud Hour | **7 PM (Evening)** |
| 8 | Card-Not-Present Fraud Rate | **57.8%** |

---

## 🧹 Data Cleaning Steps

| Step | Check | Result |
|---|---|---|
| 1 | Null values | 0 nulls found |
| 2 | Duplicate rows | 0 duplicates found |
| 3 | Text standardisation | Stripped spaces, fixed capitalisation |
| 4 | Data type check | Fixed Transaction_Time string → datetime |
| 5 | Outlier detection (IQR) | Kept outliers — extreme amounts are real fraud signals |

---

## ⚙️ Feature Engineering

8 new columns created from existing data:

| New Column | Created From | Purpose |
|---|---|---|
| `Age_Group` | Age | Segment customers by lifecycle |
| `Amount_Bucket` | Transaction_Amount | Low / Medium / High / Very High |
| `Hour` | Transaction_Time | Extract hour for trend analysis |
| `Time_Of_Day` | Hour | Morning / Afternoon / Evening / Late Night |
| `Fraud_Label` | Fraud (0/1) | Human-readable Fraud / Legitimate |
| `Intl_Label` | International_Transaction | International / Domestic |
| `Card_Type_Label` | Card_Present | Card Present / Card Not Present |
| `High_Risk_Flag` | Failed_Attempts | 1 if ≥3 failed attempts |

---

## 📉 Visualisations Generated

| Chart | Title | Key Insight |
|---|---|---|
| 01 | Fraud vs Legitimate — Pie & Bar | 49.1% fraud rate overall |
| 02 | Fraud Rate by Merchant Category | Online Shopping highest at 62.3% |
| 03 | Transaction Amount Distribution | Fraud skews toward higher amounts |
| 04 | Fraud by Age Group (Dual Axis) | 50-59 age group most affected |
| 05 | Fraud Rate by Failed Attempts | 3+ attempts → 75.6% fraud |
| 06 | Heatmap: Category × Time of Day | Evening + Online Shopping = peak risk |
| 07 | Treemap — Fraud by Merchant | Visual breakdown of fraud concentration |
| 08 | Scatter Plot — Amount vs Attempts | Clear fraud cluster in top-right |
| 09 | Hourly Fraud Trend (Area Line) | Fraud peaks sharply at 7 PM |

---

## 📋 Power BI Dashboard

3-page interactive dashboard with 6 cross-page slicers:

**Page 1 — Fraud Overview**
- 5 KPI cards (Total Transactions, Fraud Cases, Fraud Rate, Fraud Amount, Legitimate Cases)
- Donut chart — Fraud vs Legitimate share
- Bar chart — Fraud rate by merchant category
- City-wise fraud rate visual

**Page 2 — Fraud Pattern Analysis**
- Fraud by time of day (area chart)
- International vs Domestic fraud (donut + KPI cards)
- City-wise fraud rate (clustered bar)
- Stacked bar — Fraud vs Legitimate by category

**Page 3 — Transaction Details**
- Drillable transaction table with red/green conditional formatting
- Treemap — Fraud cases by merchant category
- Scatter plot — Transaction amount vs failed attempts

**Slicers (synced across all pages):**
City · Merchant Category · Fraud Status · Age Group · Amount Bucket · Gender

---

## 💡 Business Recommendations

| # | Insight | Recommendation |
|---|---|---|
| 1 | Online Shopping: 62.3% fraud | Enforce OTP / 3D Secure for all online transactions |
| 2 | ≥3 Failed Attempts: 75.6% fraud | Auto-lock card after 3 failed attempts |
| 3 | International: 61.6% fraud | Push notification approval for every international transaction |
| 4 | Chennai: 54.6% fraud | Deploy geo-velocity alerts |
| 5 | Peak at 7 PM | Schedule extra analyst staffing 6 PM – 10 PM |
| 6 | Very High amounts: 66.4% fraud | Secondary verification above $3,500 |
| 7 | Card-Not-Present: 57.8% fraud | Mandatory CVV + 3DS for all online transactions |
| 8 | High fraud rate overall | Implement real-time ML fraud scoring |

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/Sparsh9876/credit-card-fraud-detection.git
cd credit-card-fraud-detection
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up PostgreSQL
```
1. Open pgAdmin 4
2. Run: 01_sql_analysis.sql
3. Import the CSV from data/ folder
```

### 4. Update your credentials in the Python file
```python
# Open 01_python.py
# Update line 56:
DB_PASSWORD = "YourPassword"
```

### 5. Run the analysis
```bash
python 01_python.py
```

### 6. Open Power BI
```
Load: outputs/fraud_clean_for_powerbi.csv
```

---

## 📦 Requirements

```
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
```

---

## 🎯 Target Roles

This project demonstrates skills for:

- **Data Analyst**
- **Business Intelligence Analyst**
- **Fraud Analytics Analyst**
- **Risk Analytics Analyst**

At companies like:
**American Express · Deutsche Bank · Google · Deloitte · Accenture · HDFC Bank · Razorpay · Paytm**

---

## 🙋 About Me

- 🎓 MCA Student — Amity University
- 💼 Aspiring Data Analyst/ Data Scientist
- 🛠 Skills: Python · SQL · Power BI · pandas · Data Visualisation
- 🔗 LinkedIn: www.linkedin.com/in/sparshbhatnagar
- 📧 Email: sparsh.bhatnagar13@gmail.com

---

## ⭐ If you found this project useful

Give it a star ⭐ on GitHub — it helps others find the project!

---

*Built with ❤️ as part of my Data Analytics learning journey*
