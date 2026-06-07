from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).resolve().parents[1] / "artifacts" / "model.joblib"

print("[DEBUG] MODEL_PATH:", MODEL_PATH)

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
    print("[DEBUG] Startup event triggered — loading model...")
    global model
    if not MODEL_PATH.exists():
        print("[DEBUG] Model file missing at:", MODEL_PATH)
        raise RuntimeError("Model file not found. Please place model.joblib in artifacts/")
    model = joblib.load(MODEL_PATH)
    print("[DEBUG] Model loaded successfully.")

@app.get("/health")
def health():
    print("[DEBUG] /health endpoint called")
    return {"status": "ok"}

# -----------------------------
# Prediction endpoint
# -----------------------------
@app.post("/predict")
def predict(payload: APIPayload):

    print("[DEBUG] /predict endpoint called")
    print("[DEBUG] Incoming payload:", payload.dict())

    if model is None:
        print("[DEBUG] ERROR: Model is not loaded")
        raise HTTPException(status_code=500, detail="Model not loaded")

    # -----------------------------------------
    # Transform API schema → model feature schema
    # -----------------------------------------
    print("[DEBUG] Transforming payload into model feature vector...")
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

    print("[DEBUG] Feature vector:", X)

    # -----------------------------------------
    # Predict
    # -----------------------------------------
    print("[DEBUG] Running model.predict_proba...")
    proba = float(model.predict_proba(X)[0][1])
    pred = int(proba >= 0.5)

    print("[DEBUG] Prediction probability:", proba)
    print("[DEBUG] Prediction label:", pred)

    return {
        "customer_id": payload.customer_id,
        "probability": proba,
        "prediction": pred
    }
