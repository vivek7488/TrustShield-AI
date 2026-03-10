# config.py — TrustShield AI Configuration

# ── Decision Engine Thresholds ──────────────────────────────────────────────
FRAUD_SCORE_THRESHOLDS = {
    "block":         0.70,   # score >= 0.70  → block
    "manual_review": 0.30,   # score >= 0.30  → manual_review
    # else                   → approve
}

# High-value transactions get escalated regardless of score
HIGH_VALUE_AMOUNT_USD   = 10_000
HIGH_VALUE_FLOOR        = "manual_review"   # minimum decision for high-value txns

# ── Model ────────────────────────────────────────────────────────────────────
MODEL_PATH = "models/trustshield.pkl"

# ── SHAP ─────────────────────────────────────────────────────────────────────
SHAP_TOP_N_FEATURES = 5     # number of top contributing features returned per decision

# ── API ──────────────────────────────────────────────────────────────────────
API_TITLE       = "TrustShield AI"
API_DESCRIPTION = "Real-time fraud detection and credit risk scoring API"
API_VERSION     = "1.0.0"
