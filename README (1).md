# 🛡️ TrustShield AI
### Real-Time Fraud Detection & Credit Risk Scoring API

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0+-FF6600?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

A production-grade REST API for real-time fraud detection and credit risk scoring. Built independently from scratch — no prior fintech ML experience before this project.

---

## Architecture

```
Transaction JSON  ──►  Feature Engine (34 features)
                              │
                              ▼
                     XGBoost Classifier
                     F1: 0.56 │ AUC: 0.91
                              │
                        fraud_score ∈ [0,1]
                              │
                              ▼
                      Decision Engine
                   block / manual_review / approve
                              │
                   ┌──────────┴──────────┐
                   ▼                     ▼
            SHAP Explainer         SQLite Audit Log
         (top 5 risk factors)   (every decision logged)
                   │
                   ▼
            JSON Response
            (< 150ms latency)
```

---

## Features

- **Real-time inference** — sub-150ms end-to-end latency per transaction
- **34 domain-engineered features** — velocity, location deviation, device fingerprint, card metadata, time patterns
- **XGBoost classifier** — trained on the Kaggle Credit Card Fraud dataset with class imbalance handling
- **SHAP explainability** — top 5 contributing risk factors returned per decision
- **Configurable decision engine** — approve / manual_review / block with dynamic thresholds by score and transaction amount
- **SQLite audit log** — every prediction stored with full decision trail
- **Live operations dashboard** — real-time stats, decision breakdown, risk gauge
- **Stream simulator** — fires 100 transactions to stress-test the API

---

## Quickstart

### 1. Clone and install
```bash
git clone https://github.com/vivek7488/trustshield-ai
cd trustshield-ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Download dataset
Download `creditcard.csv` from [Kaggle — Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) and place it in `data/`.

### 3. Train the model
```bash
python notebooks/train_model.py
```

### 4. Start the API
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Open the dashboard
```
http://127.0.0.1:8000/
```

### 6. Run the stream simulator
```bash
python simulate_stream.py
```

---

## API Reference

### `POST /predict`

**Request:**
```json
{
  "TransactionAmt": 250.00,
  "card6": "credit",
  "P_emaildomain": "gmail.com",
  "addr1": "315",
  "addr2": "315",
  "DeviceType": "desktop",
  "card_age": 24,
  "TransactionDT": 86400
}
```

**Response:**
```json
{
  "decision": "approve",
  "fraud_score": 0.0312,
  "triggered_rule": "fraud_score 0.031 below all thresholds",
  "top_risk_factors": [
    { "feature": "card_age",    "shap_value": -1.91, "direction": "decreases_risk" },
    { "feature": "C1",          "shap_value":  1.48, "direction": "increases_risk" },
    { "feature": "hour_of_day", "shap_value": -0.84, "direction": "decreases_risk" }
  ],
  "latency_ms": 134.2
}
```

### `GET /dashboard`
Live operational stats — total transactions, fraud rate, avg latency, decision breakdown.

### `GET /health`
API health check and model load status.

### `GET /metrics`
Model performance metrics and active thresholds.

---

## Decision Engine

| Fraud Score | Transaction Amount | Decision |
|---|---|---|
| >= 0.70 | any | BLOCK |
| 0.30 - 0.69 | any | MANUAL REVIEW |
| < 0.30 | >= $10,000 | MANUAL REVIEW (escalated) |
| < 0.30 | < $10,000 | APPROVE |

All thresholds configurable in `config.py`.

---

## Feature Engineering (34 features)

| Category | Features |
|---|---|
| Transaction | Amount, log-amount, round-dollar flag, fractional cents |
| Location | Address mismatch, billing-to-shipping distance (dist1, dist2) |
| Device | Device type known flag |
| Identity | Email domain risk score, encoded email domain |
| Card | Card type encoded, card age |
| Time | Hour of day |
| C-features | C1-C10 (transaction count aggregates) |
| V-features | V1-V10 (Vesta-engineered features) |

---

## Project Structure

```
trustshield-ai/
├── app/
│   ├── main.py           # FastAPI app, routes, CORS, dashboard serving
│   ├── model.py          # Model loading, inference, SHAP explanation
│   ├── features.py       # 34-feature engineering pipeline
│   ├── decision.py       # Decision engine with configurable thresholds
│   ├── logger.py         # SQLite audit log
│   └── schemas.py        # Pydantic request/response models
├── notebooks/
│   └── train_model.py    # Full training pipeline
├── dashboard.html        # Live operations dashboard
├── simulate_stream.py    # Dataflow-style stream simulator
├── config.py             # Thresholds and settings
└── requirements.txt
```

---

## Performance

| Metric | Value |
|---|---|
| F1 Score | 0.56 |
| AUC-ROC | 0.91 |
| Avg Inference Latency | ~130ms |
| Dataset | Kaggle Credit Card Fraud (284k transactions) |

---

## Built By

**Vivek Kumar** — CS Dual Degree (B.Tech + M.Tech), VIT Bhopal
Built independently with no prior fintech ML experience.

[LinkedIn](https://linkedin.com/in/vi-vek-ku-mar) · [GitHub](https://github.com/vivek7488)
