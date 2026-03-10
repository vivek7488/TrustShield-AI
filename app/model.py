# app/model.py — Model Loading, Inference & SHAP
import joblib
import shap
import numpy as np
import pandas as pd
from typing import List, Dict
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config
from app.schemas import SHAPFeature

# ── Singleton state (loaded once at startup) ──────────────────────────────────
_model      = None
_explainer  = None
_metrics    = {}


def load_model():
    """Load model and SHAP explainer once at startup."""
    global _model, _explainer, _metrics

    model_path = config.MODEL_PATH
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model not found at '{model_path}'. "
            "Run notebooks/train_model.ipynb first to train and save the model."
        )

    bundle     = joblib.load(model_path)
    _model     = bundle["model"]
    _metrics   = bundle.get("metrics", {})

    # TreeExplainer is fastest for XGBoost — O(1) per prediction
    _explainer = shap.TreeExplainer(_model)
    print(f"[TrustShield] Model loaded | F1={_metrics.get('f1'):.3f} | AUC={_metrics.get('auc'):.3f}")


def is_loaded() -> bool:
    return _model is not None


def get_metrics() -> dict:
    return _metrics


def predict(features_df: pd.DataFrame):
    """
    Run inference + SHAP explanation on a single-row features DataFrame.
    Returns (fraud_probability, top_shap_features).
    """
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")

    # ── Inference ─────────────────────────────────────────────────────────────
    fraud_prob = float(_model.predict_proba(features_df)[0][1])

    # ── SHAP explanation ──────────────────────────────────────────────────────
    shap_values = _explainer.shap_values(features_df)

    # shap_values shape: (1, n_features) — take first (and only) row
    if isinstance(shap_values, list):
        # Binary classification returns list of [neg_class, pos_class]
        sv = shap_values[1][0]
    else:
        sv = shap_values[0]

    feature_names = features_df.columns.tolist()

    # Sort by absolute SHAP value, take top N
    top_idx = np.argsort(np.abs(sv))[::-1][: config.SHAP_TOP_N_FEATURES]
    top_features: List[SHAPFeature] = []
    for i in top_idx:
        top_features.append(SHAPFeature(
            feature    = feature_names[i],
            shap_value = round(float(sv[i]), 4),
            direction  = "increases_risk" if sv[i] > 0 else "decreases_risk",
        ))

    return fraud_prob, top_features
