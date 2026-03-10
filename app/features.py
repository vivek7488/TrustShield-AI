# app/features.py — Feature Engineering (matches training features exactly)
import pandas as pd
import numpy as np
from typing import Dict, Any

# Must match TRAIN_FEATURES from train_model.py exactly
FEATURE_COLUMNS = [
    "TransactionAmt", "amt_log", "amt_rounded", "amt_cents",
    "addr_mismatch", "dist1_filled", "device_known",
    "email_domain_risk", "p_emaildomain_encoded",
    "card_type_encoded", "card_age", "hour_of_day",
    "C1","C2","C3","C4","C5","C6","C7","C8","C9","C10",
    "V1","V2","V3","V4","V5","V6","V7","V8","V9","V10",
    "dist2",
]

HIGH_RISK_EMAIL_DOMAINS = {
    "gmail.com": 0.3,
    "yahoo.com": 0.4,
    "hotmail.com": 0.4,
    "outlook.com": 0.3,
    "anonymous.com": 0.9,
    "protonmail.com": 0.6,
    "": 0.8,
}

CARD_TYPE_MAP = {"credit": 0, "debit": 1, "debit or credit": 2, "charge card": 3}


def engineer_features(raw: Dict[str, Any]) -> pd.DataFrame:
    amt = float(raw.get("TransactionAmt") or 0)

    # Transaction features
    amt_log      = np.log1p(amt)
    amt_rounded  = 1 if (amt % 1 == 0) else 0
    amt_cents    = amt - int(amt)

    # Location deviation
    addr1 = str(raw.get("addr1") or -1)
    addr2 = str(raw.get("addr2") or -1)
    addr_mismatch = 0 if addr1 == addr2 else 1
    dist1_filled  = float(raw.get("dist1") or 0)
    dist2         = float(raw.get("dist2") or 0)

    # Device / identity
    device_known = 1 if raw.get("DeviceType") else 0
    email_domain = str(raw.get("P_emaildomain") or "").lower().strip()
    email_domain_risk = HIGH_RISK_EMAIL_DOMAINS.get(email_domain, 0.2)
    domain_list = list(HIGH_RISK_EMAIL_DOMAINS.keys())
    p_emaildomain_encoded = domain_list.index(email_domain) if email_domain in domain_list else len(domain_list)

    # Card features
    card_type = str(raw.get("card6") or "debit").lower()
    card_type_encoded = CARD_TYPE_MAP.get(card_type, 1)
    card_age  = float(raw.get("card_age") or 12)

    # Time
    transaction_dt = float(raw.get("TransactionDT") or 0)
    hour_of_day    = int((transaction_dt / 3600) % 24)

    # C-features (default 0 if not provided)
    c_features = {f"C{i}": float(raw.get(f"C{i}") or 0) for i in range(1, 11)}

    # V-features (default 0 if not provided)
    v_features = {f"V{i}": float(raw.get(f"V{i}") or 0) for i in range(1, 11)}

    row = {
        "TransactionAmt":        amt,
        "amt_log":               amt_log,
        "amt_rounded":           amt_rounded,
        "amt_cents":             amt_cents,
        "addr_mismatch":         addr_mismatch,
        "dist1_filled":          dist1_filled,
        "device_known":          device_known,
        "email_domain_risk":     email_domain_risk,
        "p_emaildomain_encoded": p_emaildomain_encoded,
        "card_type_encoded":     card_type_encoded,
        "card_age":              card_age,
        "hour_of_day":           hour_of_day,
        "dist2":                 dist2,
        **c_features,
        **v_features,
    }

    return pd.DataFrame([row], columns=FEATURE_COLUMNS)