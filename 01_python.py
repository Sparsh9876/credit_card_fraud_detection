#=====================================================================
# CREDIT CARD FRAUD DETECTION 
# PYTHON SCRIPT 
#=====================================================================
import os
import sys
import warnings

# Ignore warnings (only needs to be called once)
warnings.filterwarnings("ignore")

# Data manipulation libraries
import numpy as np
import pandas as pd

# Database libraries
import psycopg2
import sqlalchemy 
from sqlalchemy import create_engine, text

# Visualization libraries
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# Set matplotlib backend
matplotlib.use("Agg")

# Print verification statements
print("SQLAlchemy version:", sqlalchemy.__version__)
print("Psycopg2 driver is ready!")


#----------------PATHs-----------------

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, "..", "data",
                          "credit_card_fraud_detection_dataset.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
 
# ── Chart colours ─────────────────────────────────────────────────────────────
FRAUD_COLOR = "#E74C3C"      # red   → fraud
LEGIT_COLOR = "#27AE60"      # green → legitimate
BLUE_COLOR  = "#2980B9"
PURPLE_COLOR= "#8E44AD"
 
 
print("=" * 65)
print("  CREDIT CARD FRAUD DETECTION — DATA ANALYTICS PROJECT")
print("=" * 65)

print("\n  Connecting to PostgreSQL database …")
connection_string = (
    "postgresql+psycopg2://postgres:132570"
    "@localhost:5432/fraud_detection_db"
)

# Try to connect — if it fails, show a friendly error message
try:
    engine = create_engine(connection_string)
 
    with engine.connect() as conn:
        # Quick test — if this line works, you are connected
        test = conn.execute(text("SELECT 1"))
 
    print("  ✓  Connected to PostgreSQL successfully!")
    print(f"     Database : fraud_detection_db")
    print(f"     Host     : localhost:5432")
    print(f"     User     : postgres")
 
except Exception as e:
    # ── Common errors and how to fix them ────────────────────────────────────
    error_msg = str(e)
    print("\n  ✗  Connection FAILED. Read the fix below:\n")
 
    sys.exit(1)   # stop the script — no point continuing without a connection

# =============================================================================
#  LOADing DATA FROM POSTGRESQL INTO PYTHON
# =============================================================================
print(f"\n loading data from table 'transactions'...") 
with engine.connect() as conn:
    df = pd.read_sql(
        text(f"SELECT * FROM transactions"),
        conn
    )
 
print(f"  ✓  Data loaded successfully!")
print(f"     Rows    : {df.shape[0]:,}")
print(f"     Columns : {df.shape[1]}")
print(f"\n  Column names:")
for col in df.columns:
    print(f"     • {col}")
 
#====================================================
# DATA CLEANING
#==================================================== 
print(f"\n data cleaning ....")
print("-"* 40)

#------checking for null/missing values --------

print("\n  Null Value Check (0 = no problem):")
null_counts = df.isnull().sum()
for col, count in null_counts.items():
    status = "✓" if count == 0 else "  NEEDS FIXING"
    print(f"     {col:<30} : {count}  {status}")
 
total_nulls = null_counts.sum()
if total_nulls == 0:
    print("\n  ✓  No missing values found — data is clean!")
else:
    print(f"\n    Found {total_nulls} missing values — filling with defaults …")
    # Fill numeric nulls with median, text nulls with 'Unknown'
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col].fillna(df[col].median(), inplace=True)
        else:
            df[col].fillna('Unknown', inplace=True)
    print("  ✓  Missing values handled.")
 
 #---------------Check for duplicate rows -----------------------

print("\n  Duplicate Row Check:")
duplicates = df.duplicated().sum()
if duplicates == 0:
    print("  ✓  No duplicate rows found.")
else:
    df.drop_duplicates(inplace=True)
    print(f"  ✓  Removed {duplicates} duplicate rows.")
    print(f"     New shape: {df.shape[0]:,} rows")

#--------------Clean text columns---------------

print("\n  Cleaning text columns …")
text_columns = df.select_dtypes(include='object').columns
for col in text_columns:
    df[col] = df[col].str.strip()   # remove extra spaces

#-------------- Data types check ---------------------------

print("\n  Data Types:")
for col, dtype in df.dtypes.items():
    print(f"     {col:<30} : {dtype}")
     
# -------------Basic statistics ----------------------------------

print("\n  Basic Statistics (numeric columns):")
print(df[['age', 'transaction_amount', 'failed_attempts']].describe().round(2).to_string())
 
# --------------Outlier check on Transaction_Amount -----------------------

Q1  = df['transaction_amount'].quantile(0.25)
Q3  = df['transaction_amount'].quantile(0.75)
IQR = Q3 - Q1
lower_fence = Q1 - 1.5 * IQR
upper_fence = Q3 + 1.5 * IQR
outliers    = df[
    (df['transaction_amount'] < lower_fence) |
    (df['transaction_amount'] > upper_fence)
]
print(f"\n  Outlier Check on Transaction_Amount (IQR method):")
print(f"     Q1={Q1:.2f}  Q3={Q3:.2f}  IQR={IQR:.2f}")
print(f"     Lower fence : {lower_fence:.2f}")
print(f"     Upper fence : {upper_fence:.2f}")
print(f"     Outliers    : {len(outliers)} rows")
print(f"  → Keeping outliers (extreme amounts are real fraud signals)")


# =============================================================================
#   FEATURE ENGINEERING
#  (Creating new useful columns from existing ones)
# =============================================================================

print("\n Feature Engineering …")
print("-" * 40)
 
# Age Group  — group customers by age range
df['Age_Group'] = pd.cut(
    df['age'],
    bins=[17, 29, 39, 49, 59, 100],
    labels=['18-29', '30-39', '40-49', '50-59', '60+']
)
print("  ✓  Age_Group created (18-29 / 30-39 / 40-49 / 50-59 / 60+)")
 
# Amount Bucket — group transactions by value
df['Amount_Bucket'] = pd.cut(
    df['transaction_amount'],
    bins=[0, 499.99, 1999.99, 3499.99, float('inf')],
    labels=['Low (<500)', 'Medium (500-1999)', 'High (2000-3499)', 'Very High (3500+)']
)
print("  ✓  Amount_Bucket created (Low / Medium / High / Very High)")
 
# Hour — extract the hour from Transaction_Time  (format: DD-MM-YYYY HH:MM)
df['Hour'] = pd.to_datetime(
    df['transaction_time'], dayfirst=True
).dt.hour
print("  ✓  Hour extracted from Transaction_Time (0–23)")
 
# Time of Day — label the hour as a time period
def get_time_of_day(hour):
    if   0  <= hour <= 5:  return 'Late Night'
    elif 6  <= hour <= 11: return 'Morning'
    elif 12 <= hour <= 17: return 'Afternoon'
    else:                  return 'Evening'
 
df['Time_Of_Day'] = df['Hour'].apply(get_time_of_day)
print("  ✓  Time_Of_Day created (Late Night / Morning / Afternoon / Evening)")
 
# Readable labels — convert 0/1 to text
df['Fraud_Label']    = df['fraud'].map({1: 'Fraud', 0: 'Legitimate'})
df['Intl_Label']     = df['international_transaction'].map({1: 'International', 0: 'Domestic'})
df['Card_Type_Label']= df['card_present'].map({1: 'Card Present', 0: 'Card Not Present'})
print("  ✓  Fraud_Label / Intl_Label / Card_Type_Label created")
 
# High Risk Flag — 1 if customer had 3 or more failed attempts
df['High_Risk_Flag'] = (df['failed_attempts'] >= 3).astype(int)
print("  ✓  High_Risk_Flag created (1 = 3 or more failed attempts)")
 
print(f"\n  Final dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")

# =============================================================================
#  KEY PERFORMANCE INDICATORS (KPIs)
# =============================================================================
print("\n Calculating KPIs …")
print("-" * 40)
 
total_txns      = len(df)
total_amount    = df['transaction_amount'].sum()
fraud_cases     = df['fraud'].sum()
legit_cases     = total_txns - fraud_cases
fraud_rate      = fraud_cases / total_txns * 100
fraud_amount    = df[df['fraud']==1]['transaction_amount'].sum()
avg_fraud_amt   = df[df['fraud']==1]['transaction_amount'].mean()
avg_legit_amt   = df[df['fraud']==0]['transaction_amount'].mean()
intl_fraud_rate = df[df['international_transaction']==1]['fraud'].mean() * 100
cnp_fraud_rate  = df[df['card_present']==0]['fraud'].mean() * 100
high_risk_rate  = df[df['High_Risk_Flag']==1]['fraud'].mean() * 100

print(f"""
  ╔═════════════════════════════════════════════════════════╗
  ║           FRAUD ANALYTICS — KPI DASHBOARD               ║
  ╠═════════════════════════════════════════════════════════╣
  ║  Total Transactions         : {total_txns:>8,}          
  ║  Total Amount               : ${total_amount:>12,.2f}   
  ║  Fraud Cases                : {fraud_cases:>8,}         
  ║  Legitimate Cases           : {legit_cases:>8,}         
  ║  Fraud Rate                 : {fraud_rate:>8.2f}%       
  ║  Total Fraud Amount         : ${fraud_amount:>12,.2f}   
  ║  Avg Fraud Transaction      : ${avg_fraud_amt:>12,.2f}  
  ║  Avg Legitimate Transaction : ${avg_legit_amt:>12,.2f}  
  ║  International Fraud Rate   : {intl_fraud_rate:>8.2f}%  
  ║  Card-Not-Present Fraud Rate: {cnp_fraud_rate:>8.2f}%   
  ║  High-Risk (≥3 fails) Rate  : {high_risk_rate:>8.2f}%   
  ╚═════════════════════════════════════════════════════════╝
""")

# =============================================================================
# EXPLORATORY DATA ANALYSIS (EDA)
# =============================================================================

# STEP 6 — EDA Calculations

cat_analysis = (
    df.groupby('merchant_category')['fraud']
    .agg(['sum', 'count'])
    .rename(columns={'sum': 'Fraud_Count', 'count': 'Total'})
    .assign(Fraud_Rate_Pct=lambda x: (x['Fraud_Count'] / x['Total'] * 100).round(2))
    .sort_values('Fraud_Rate_Pct', ascending=False)
)

city_analysis = (
    df.groupby('city')['fraud']
    .agg(['sum', 'count'])
    .rename(columns={'sum': 'Fraud_Count', 'count': 'Total'})
    .assign(Fraud_Rate_Pct=lambda x: (x['Fraud_Count'] / x['Total'] * 100).round(2))
    .sort_values('Fraud_Rate_Pct', ascending=False)
)

fa_analysis = (
    df.groupby('failed_attempts')['fraud']
    .agg(['sum', 'count'])
    .rename(columns={'sum': 'Fraud_Count', 'count': 'Total'})
    .assign(Fraud_Rate_Pct=lambda x: (x['Fraud_Count'] / x['Total'] * 100).round(2))
)

print("  Fraud Rate by Merchant Category:")
print(cat_analysis.to_string())

print("\n  Fraud Rate by City:")
print(city_analysis.to_string())

print("\n  Fraud Rate by Failed Attempts:")
print(fa_analysis.to_string())

# =============================================================================
#  DATA VISUALISATION  (charts)
# =============================================================================

print("\nCreating Charts …")
print("-" * 40)

# =============================================================================
#  STEP 7 — DATA VISUALISATION (9 Charts)
# =============================================================================

# Global chart style
plt.rcParams.update({
    "figure.dpi"       : 150,
    "axes.spines.top"  : False,
    "axes.spines.right": False,
    "axes.titlesize"   : 13,
    "axes.titleweight" : "bold",
    "axes.labelsize"   : 11,
})

def save_chart(filename):
    plt.savefig(os.path.join(OUTPUT_DIR, filename), bbox_inches='tight')
    plt.close()
    print(f"  ✓ saved {filename}")


# ── Chart 1 : Fraud vs Legitimate ────────────────────────────────────────────
counts = df['Fraud_Label'].value_counts()
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Fraud vs Legitimate Transactions", fontsize=14, fontweight='bold')

axes[0].pie(counts, labels=counts.index, colors=[LEGIT_COLOR, FRAUD_COLOR],
            autopct='%1.1f%%', startangle=90,
            wedgeprops=dict(edgecolor='white', linewidth=2))
axes[0].set_title("Share")

bars = axes[1].bar(counts.index, counts.values,
                   color=[LEGIT_COLOR, FRAUD_COLOR], edgecolor='white', width=0.5)
axes[1].bar_label(bars, fmt='%d', padding=3, fontweight='bold')
axes[1].set_title("Count")
axes[1].set_ylabel("Count")

plt.tight_layout()
save_chart("01_fraud_vs_legitimate.png")


# ── Chart 2 : Fraud Rate by Merchant Category ─────────────────────────────────
cat_plot = cat_analysis.reset_index().sort_values('Fraud_Rate_Pct')

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(cat_plot['merchant_category'], cat_plot['Fraud_Rate_Pct'],
               color=FRAUD_COLOR, edgecolor='white', height=0.6)
ax.bar_label(bars, fmt='%.1f%%', padding=4, fontsize=9)
ax.set_xlabel("Fraud Rate (%)")
ax.set_title("Fraud Rate by Merchant Category")
ax.xaxis.set_major_formatter(mticker.PercentFormatter())

plt.tight_layout()
save_chart("02_fraud_by_category.png")


# ── Chart 3 : Transaction Amount Distribution ─────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(df[df['Fraud_Label']=='Legitimate']['transaction_amount'],
        bins=30, alpha=0.6, color=LEGIT_COLOR, label='Legitimate', edgecolor='white')
ax.hist(df[df['Fraud_Label']=='Fraud']['transaction_amount'],
        bins=30, alpha=0.6, color=FRAUD_COLOR, label='Fraud', edgecolor='white')
ax.set_xlabel("Transaction Amount ($)")
ax.set_ylabel("Number of Transactions")
ax.set_title("Transaction Amount Distribution — Fraud vs Legitimate")
ax.legend()

plt.tight_layout()
save_chart("03_amount_distribution.png")


# ── Chart 4 : Fraud by Age Group (Dual Axis) ──────────────────────────────────
age_data = (
    df.groupby('Age_Group', observed=True)['fraud']
    .agg(['sum', 'count'])
    .rename(columns={'sum': 'Fraud_Count', 'count': 'Total'})
    .assign(Fraud_Rate=lambda x: x['Fraud_Count'] / x['Total'] * 100)
    .reset_index()
)

fig, ax1 = plt.subplots(figsize=(9, 5))
ax2 = ax1.twinx()

ax1.bar(age_data['Age_Group'].astype(str), age_data['Fraud_Count'],
        color=BLUE_COLOR, alpha=0.7, label='Fraud Count')
ax2.plot(age_data['Age_Group'].astype(str), age_data['Fraud_Rate'],
         'o-', color=FRAUD_COLOR, linewidth=2, markersize=8, label='Fraud Rate %')

ax1.set_xlabel("Age Group")
ax1.set_ylabel("Fraud Count", color=BLUE_COLOR)
ax2.set_ylabel("Fraud Rate (%)", color=FRAUD_COLOR)
ax1.set_title("Fraud Count and Rate by Age Group")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.tight_layout()
save_chart("04_fraud_by_age_group.png")


# ── Chart 5 : Failed Attempts vs Fraud Rate ───────────────────────────────────
fa_plot = fa_analysis.reset_index()
bar_colors = ['#27AE60', '#F39C12', '#E67E22', '#E74C3C', '#C0392B', '#8E44AD']

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(fa_plot['failed_attempts'], fa_plot['Fraud_Rate_Pct'],
              color=bar_colors[:len(fa_plot)], edgecolor='white', width=0.6)
ax.bar_label(bars, fmt='%.1f%%', padding=3, fontsize=9, fontweight='bold')
ax.set_xlabel("Number of Failed Login Attempts")
ax.set_ylabel("Fraud Rate (%)")
ax.set_title("Fraud Rate by Failed Attempts")
ax.yaxis.set_major_formatter(mticker.PercentFormatter())

plt.tight_layout()
save_chart("05_failed_attempts_vs_fraud.png")


# ── Chart 6 : Heatmap — Category × Time of Day ───────────────────────────────
pivot = (df[df['fraud'] == 1]
         .groupby(['merchant_category', 'Time_Of_Day'])
         .size()
         .unstack(fill_value=0))

time_order = [t for t in ['Late Night', 'Morning', 'Afternoon', 'Evening']
              if t in pivot.columns]
pivot = pivot[time_order]

fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(pivot, annot=True, fmt='d', cmap='Reds',
            linewidths=0.5, linecolor='white', ax=ax)
ax.set_title("Fraud Heatmap: Merchant Category × Time of Day")
ax.set_xlabel("Time of Day")
ax.set_ylabel("Merchant Category")

plt.tight_layout()
save_chart("06_heatmap_category_time.png")


# ── Chart 7 : International vs Domestic & Card Present ───────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Fraud Rate: International vs Domestic  |  Card Present vs Not Present",
             fontsize=12, fontweight='bold')

for ax, col, label in [(axes[0], 'Intl_Label', 'Transaction Type'),
                       (axes[1], 'Card_Type_Label', 'Card Presence')]:
    grp = (df.groupby(col)['fraud']
             .agg(['sum', 'count'])
             .assign(Rate=lambda x: x['sum'] / x['count'] * 100)
             .reset_index())
    bars = ax.bar(grp[col], grp['Rate'],
                  color=[LEGIT_COLOR, FRAUD_COLOR][:len(grp)],
                  edgecolor='white', width=0.5)
    ax.bar_label(bars, fmt='%.1f%%', padding=3, fontweight='bold')
    ax.set_ylabel("Fraud Rate (%)")
    ax.set_xlabel(label)
    ax.set_ylim(0, grp['Rate'].max() * 1.3)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())

plt.tight_layout()
save_chart("07_international_and_card_type.png")


# ── Chart 8 : Fraud Rate by City ──────────────────────────────────────────────
city_plot = city_analysis.reset_index().sort_values('Fraud_Rate_Pct', ascending=False)

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(city_plot['city'], city_plot['Fraud_Rate_Pct'],
              color=PURPLE_COLOR, edgecolor='white', width=0.6)
ax.bar_label(bars, fmt='%.1f%%', padding=3, fontsize=9, fontweight='bold')
ax.set_xlabel("City")
ax.set_ylabel("Fraud Rate (%)")
ax.set_title("Fraud Rate by City")
ax.yaxis.set_major_formatter(mticker.PercentFormatter())

plt.tight_layout()
save_chart("08_fraud_by_city.png")


# ── Chart 9 : Correlation Heatmap ────────────────────────────────────────────
numeric_cols = ['age', 'transaction_amount', 'international_transaction',
                'card_present', 'failed_attempts', 'fraud']
corr_matrix  = df[numeric_cols].corr()
mask         = np.triu(np.ones_like(corr_matrix, dtype=bool))

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f',
            cmap='coolwarm', center=0, linewidths=0.5,
            linecolor='white', vmin=-1, vmax=1, ax=ax)
ax.set_title("Correlation Matrix — How Each Column Relates to Fraud")

plt.tight_layout()
save_chart("09_correlation_heatmap.png")

print(f"\n  ✓  All 9 charts saved to: {OUTPUT_DIR}")

# =============================================================================
#  EXPORT CLEAN DATA FOR POWER BI
# =============================================================================
print(" Exporting clean data for Power BI …")

export_path = os.path.join(OUTPUT_DIR, "fraud_clean_for_powerbi.csv")
df.to_csv(export_path, index=False)
print("Clean data exported for Power BI!")

print("\n" + "=" * 60)
print("  PROJECT COMPLETE!")
print(f"  All charts and clean CSV saved to:")
print(f"  {OUTPUT_DIR}")
print("=" * 60)