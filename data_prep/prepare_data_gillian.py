# data_prep/prepare_data.py  (original file, now extended)
from pathlib import Path
import pandas as pd
import re

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)

def clean_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

if __name__ == "__main__":
    tx = pd.read_csv(DATA_DIR / "transactions.csv", parse_dates=["txn_timestamp"])
    labels = pd.read_csv(DATA_DIR / "labels.csv")

    tx["clean_desc"] = tx["description"].fillna("").apply(clean_text)

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

    # super simple text feature: indicator words
    keywords = ["rent", "netflix", "tesco", "payroll", "bonus"]
    for kw in keywords:
        agg[f"kw_{kw}"] = agg["all_desc"].str.contains(rf"\b{kw}\b").astype(int)

    # ------------------------------------------------------------
    # ⭐ NEW FEATURE 1: Average Transaction Value
    # This is different from avg_amount because avg_amount includes
    # both positive and negative values. Here we compute the mean
    # absolute transaction size to capture spending behaviour.
    # ------------------------------------------------------------
    tx["abs_amount"] = tx["amount"].abs()
    avg_tx_value = tx.groupby("customer_id")["abs_amount"].mean().reset_index()
    avg_tx_value.rename(columns={"abs_amount": "avg_transaction_value"}, inplace=True)
    agg = agg.merge(avg_tx_value, on="customer_id", how="left")

    # ------------------------------------------------------------
    # ⭐ NEW FEATURE 2: Salary Stability Indicator
    # 1 if the customer received payroll at least once, else 0.
    # This uses the existing keyword detection for "payroll".
    # ------------------------------------------------------------
    agg["salary_stability"] = (agg["kw_payroll"] > 0).astype(int)

    # ------------------------------------------------------------
    # ⭐ NEW FEATURE 3: Net Cashflow
    # total_credit - total_debit
    # A simple but powerful indicator of financial health.
    # ------------------------------------------------------------
    agg["net_cashflow"] = agg["total_credit"] - agg["total_debit"]

    # Merge labels and save
    df = agg.merge(labels, on="customer_id", how="left")
    df.to_csv(ARTIFACTS_DIR / "training_set.csv", index=False)
    print("wrote artifacts/training_set.csv")
