# app/main.py — TrustShield AI FastAPI Application
import time
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import config
from app.schemas import TransactionRequest, PredictResponse, HealthResponse, MetricsResponse
from app.features import engineer_features
from app.model import load_model, predict, is_loaded, get_metrics
from app.decision import make_decision
from app.logger import init_db, log_transaction, get_dashboard_stats


# ── Lifespan: load model + init DB once at startup ───────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    load_model()
    yield


app = FastAPI(
    title       = config.API_TITLE,
    description = config.API_DESCRIPTION,
    version     = config.API_VERSION,
    lifespan    = lifespan,
)

# ── CORS: allow dashboard.html to call the API ───────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],
    allow_methods  = ["*"],
    allow_headers  = ["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
def serve_dashboard():
    """Serve the visual dashboard."""
    dashboard_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "dashboard.html"
    )
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"message": "Dashboard not found. Place dashboard.html in the project root."}


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health():
    """Health check — confirms the API is live and model is loaded."""
    return HealthResponse(
        status       = "ok",
        model_loaded = is_loaded(),
        version      = config.API_VERSION,
    )


@app.get("/metrics", response_model=MetricsResponse, tags=["System"])
def metrics():
    """Model performance metrics."""
    m = get_metrics()
    return MetricsResponse(
        model_type              = "XGBoostClassifier",
        f1_score                = m.get("f1",  0.0),
        auc_roc                 = m.get("auc", 0.0),
        features_used           = 34,
        threshold_block         = config.FRAUD_SCORE_THRESHOLDS["block"],
        threshold_manual_review = config.FRAUD_SCORE_THRESHOLDS["manual_review"],
    )


@app.get("/dashboard", tags=["System"])
def dashboard():
    """Live operational stats — total transactions, fraud rate, avg latency, decision breakdown."""
    return get_dashboard_stats()


@app.post("/predict", response_model=PredictResponse, tags=["Fraud Detection"])
def predict_fraud(transaction: TransactionRequest):
    """
    Score a transaction for fraud risk.

    Returns a decision (approve / manual_review / block), fraud probability,
    the rule that triggered the decision, and the top SHAP risk factors.
    """
    if not is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded yet. Try again in a moment.")

    t0 = time.perf_counter()

    # 1. Feature engineering
    features_df = engineer_features(transaction.model_dump())

    # 2. Inference + SHAP
    fraud_score, shap_features = predict(features_df)

    # 3. Decision engine
    decision_result = make_decision(fraud_score, transaction.TransactionAmt)

    latency_ms = (time.perf_counter() - t0) * 1000

    # 4. Audit log — every decision saved to SQLite
    log_transaction(
        amount         = transaction.TransactionAmt,
        decision       = decision_result["decision"],
        fraud_score    = decision_result["fraud_score"],
        triggered_rule = decision_result["triggered_rule"],
        top_factors    = shap_features,
        latency_ms     = round(latency_ms, 2),
    )

    return PredictResponse(
        decision         = decision_result["decision"],
        fraud_score      = decision_result["fraud_score"],
        triggered_rule   = decision_result["triggered_rule"],
        top_risk_factors = shap_features,
        latency_ms       = round(latency_ms, 2),
    )