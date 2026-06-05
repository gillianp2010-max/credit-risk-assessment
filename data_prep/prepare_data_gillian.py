# data_prep/prepare_data.py  (original file, now extended)
from pathlib import Path
import pandas as pd
import re
import matplotlib
matplotlib.use("Agg")   # [REQ 5.0 – validated] Use non-GUI backend for saving plots
import matplotlib.pyplot as plt   # [REQ 5.0 – validated] Simple EDA visualisations

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)

# [REQ 3.1 – validated] Clean the text: lowercase, remove punctuation/numbers
def clean_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

if __name__ == "__main__":

    # ------------------------------------------------------------
    # [REQ 1.1 – validated] Load and explore the data
    # ------------------------------------------------------------
    tx = pd.read_csv(DATA_DIR / "transactions.csv", parse_dates=["txn_timestamp"])
    labels = pd.read_csv(DATA_DIR / "labels.csv")

    # ------------------------------------------------------------
    # [REQ 3.1 – validated] Clean text column
    # ------------------------------------------------------------
    tx["clean_desc"] = tx["description"].fillna("").apply(clean_text)

    # ------------------------------------------------------------
    # [REQ 5.1 – validated] SIMPLE EXPLORATORY DATA ANALYSIS (Optional)
    # NOTE:
    # I do not work in financial services, so these are intentionally
    # simple, generic visualisations to demonstrate exploratory thinking.
    # All plots are saved to artifacts/ instead of displayed.
    # ------------------------------------------------------------

    # [REQ 5.1a – validated] Plot 1 — Distribution of transaction amounts
    plt.hist(tx["amount"], bins=20, edgecolor="black")
    plt.title("Distribution of Transaction Amounts")
    plt.xlabel("Amount")
    plt.ylabel("Frequency")
    plt.savefig(ARTIFACTS_DIR / "eda_amount_distribution.png")
    plt.close()
    print("Saved plot: eda_amount_distribution.png")

    # [REQ 5.1b – validated] Plot 2 — Number of transactions per customer
    tx.groupby("customer_id")["transaction_id"].count().plot(kind="bar")
    plt.title("Transactions per Customer")
    plt.xlabel("Customer ID")
    plt.ylabel("Count")
    plt.savefig(ARTIFACTS_DIR / "eda_transactions_per_customer.png")
    plt.close()
    print("Saved plot: eda_transactions_per_customer.png")

    # [REQ 5.1c – validated] Plot 3 — Most common words in cleaned descriptions
    from collections import Counter
    words = " ".join(tx["clean_desc"]).split()
    common = Counter(words).most_common(10)

    plt.bar([w for w, _ in common], [c for _, c in common])
    plt.title("Most Common Words in Descriptions")
    plt.xticks(rotation=45)
    plt.ylabel("Frequency")
    plt.savefig(ARTIFACTS_DIR / "eda_common_words.png")
    plt.close()
    print("Saved plot: eda_common_words.png")

    # ------------------------------------------------------------
    # [REQ 1.2 – validated] Data quality checks (nulls, duplicates, outliers)
    # ------------------------------------------------------------

    print("Null counts:")
    print(tx.isnull().sum())

    dup_tx = tx["transaction_id"].duplicated().sum()
    print(f"Duplicate transaction_id rows: {dup_tx}")

    q1 = tx["amount"].quantile(0.25)
    q3 = tx["amount"].quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = tx[(tx["amount"] < lower_bound) | (tx["amount"] > upper_bound)]
    print("Potential outliers in 'amount':")
    print(outliers)

    # ------------------------------------------------------------
    # [REQ 1.2 – validated] Additional Data Quality Check (Assumption)
    # Duplicate transactions close in time may indicate system error
    # ------------------------------------------------------------
    tx_sorted = tx.sort_values(["customer_id", "txn_timestamp"])
    tx_sorted["time_diff"] = (
        tx_sorted.groupby("customer_id")["txn_timestamp"]
        .diff()
        .dt.total_seconds()
    )

    potential_dupes = tx_sorted[
        (tx_sorted["amount"].eq(tx_sorted["amount"].shift())) &
        (tx_sorted["clean_desc"].eq(tx_sorted["clean_desc"].shift())) &
        (tx_sorted["time_diff"] <= 30)
    ]

    print("Potential duplicate transactions (same amount + description within 30 seconds):")
    print(potential_dupes)

    # ------------------------------------------------------------
    # [REQ 2.1 – validated] Aggregate transactions → one row per customer
    # [REQ 2.2 – validated] Required features
    # ------------------------------------------------------------
    agg = (
        tx.groupby("customer_id")
        .agg(
            txn_count=("transaction_id", "count"),
            total_debit=("amount", lambda x: x[x < 0].sum()),
            total_credit=("amount", lambda x: x[x > 0].sum()),
            avg_amount=("amount", "mean"),
            all_desc=("clean_desc", lambda x: " ".join(x)),
        )
        .reset_index()
    )

    # ------------------------------------------------------------
    # [REQ 3.2 – validated] Keyword flags (merchant category signals)
    # ------------------------------------------------------------
    keywords = ["rent", "netflix", "tesco", "payroll", "bonus"]
    for kw in keywords:
        agg[f"kw_{kw}"] = agg["all_desc"].str.contains(rf"\b{kw}\b").astype(int)

    # ------------------------------------------------------------
    # [REQ 2.3 – validated] NEW FEATURE 1: Average Transaction Value
    # ------------------------------------------------------------
    tx["abs_amount"] = tx["amount"].abs()
    avg_tx_value = tx.groupby("customer_id")["abs_amount"].mean().reset_index()
    avg_tx_value.rename(columns={"abs_amount": "avg_transaction_value"}, inplace=True)
    agg = agg.merge(avg_tx_value, on="customer_id", how="left")

    # ------------------------------------------------------------
    # [REQ 2.3 – validated] NEW FEATURE 2: Salary Stability Indicator
    # ------------------------------------------------------------
    agg["salary_stability"] = (agg["kw_payroll"] > 0).astype(int)

    # ------------------------------------------------------------
    # [REQ 2.3 – validated] NEW FEATURE 3: Net Cashflow
    # ------------------------------------------------------------
    agg["net_cashflow"] = agg["total_credit"] - agg["total_debit"]

    # ------------------------------------------------------------
    # [REQ 4.1 – validated] Merge with labels → training-ready dataset
    # [REQ 4.2 – validated] Save as artifacts/training_set.csv
    # ------------------------------------------------------------
    df = agg.merge(labels, on="customer_id", how="left")
    df.to_csv(ARTIFACTS_DIR / "training_set.csv", index=False)
    print("wrote artifacts/training_set.csv")
