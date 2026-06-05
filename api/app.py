from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).resolve().parents[1] / "artifacts" / "model.joblib"

app = FastAPI(title="ML Inference Service")

# -----------------------------
# API schema (Part 2 requirement)
# -----------------------------
class APIPayload(BaseModel):
    customer_id: str
    num_transactions: float
    total_debit: float
    total_credit: float
    avg_amount: float
    has_rent: int = 0
    has_salary: int = 0

# -----------------------------
# Load model
# -----------------------------
model = None

@app.on_event("startup")
def load_model():
    global model
    if not MODEL_PATH.exists():
        raise RuntimeError("Model file not found. Please place model.joblib in artifacts/")
    model = joblib.load(MODEL_PATH)

@app.get("/health")
def health():
    return {"status": "ok"}

# -----------------------------
# Prediction endpoint
# -----------------------------
@app.post("/predict")
def predict(payload: APIPayload):

    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    # -----------------------------------------
    # Transform API schema → model feature schema
    # -----------------------------------------
    X = [[
        payload.num_transactions,   # → txn_count
        payload.total_debit,
        payload.total_credit,
        payload.avg_amount,
        payload.has_rent,           # → kw_rent
        0,                          # kw_netflix (not provided)
        0,                          # kw_tesco (not provided)
        payload.has_salary,         # → kw_payroll
        0                           # kw_bonus (not provided)
    ]]

    # -----------------------------------------
    # Predict
    # -----------------------------------------
    proba = float(model.predict_proba(X)[0][1])
    pred = int(proba >= 0.5)

    return {
        "customer_id": payload.customer_id,
        "probability": proba,
        "prediction": pred
    }
