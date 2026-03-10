# app/schemas.py — Request & Response Models
from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict


class TransactionRequest(BaseModel):
    """Incoming transaction payload."""
    TransactionAmt:    float           = Field(...,  gt=0,    description="Transaction amount in USD")
    TransactionDT:     Optional[float] = Field(None,          description="Transaction datetime offset (seconds)")
    card6:             Optional[str]   = Field(None,          description="Card type: credit / debit / charge card")
    card_age:          Optional[float] = Field(None,  ge=0,   description="Card age in months")
    P_emaildomain:     Optional[str]   = Field(None,          description="Purchaser email domain")
    addr1:             Optional[str]   = Field(None,          description="Billing address code")
    addr2:             Optional[str]   = Field(None,          description="Shipping address code")
    dist1:             Optional[float] = Field(None,          description="Distance between billing and shipping")
    DeviceType:        Optional[str]   = Field(None,          description="Device type (mobile / desktop)")
    # Velocity fields (pre-computed by caller or defaulted)
    card_txn_count:    Optional[float] = Field(None,  ge=0,   description="Number of recent txns on this card")
    card_amt_sum:      Optional[float] = Field(None,  ge=0,   description="Sum of recent txn amounts on this card")
    card_amt_mean:     Optional[float] = Field(None,  ge=0,   description="Mean of recent txn amounts on this card")

    model_config = {"json_schema_extra": {"example": {
        "TransactionAmt": 250.00,
        "TransactionDT":  86400,
        "card6":          "credit",
        "card_age":       24,
        "P_emaildomain":  "gmail.com",
        "addr1":          "315",
        "addr2":          "315",
        "dist1":          0,
        "DeviceType":     "desktop",
        "card_txn_count": 3,
        "card_amt_sum":   430.0,
        "card_amt_mean":  143.3,
    }}}


class SHAPFeature(BaseModel):
    feature:    str
    shap_value: float
    direction:  Literal["increases_risk", "decreases_risk"]


class PredictResponse(BaseModel):
    decision:         Literal["approve", "manual_review", "block"]
    fraud_score:      float = Field(..., description="Probability of fraud [0–1]")
    triggered_rule:   str
    top_risk_factors: List[SHAPFeature]
    latency_ms:       float


class HealthResponse(BaseModel):
    status:        str
    model_loaded:  bool
    version:       str


class MetricsResponse(BaseModel):
    model_type:    str
    f1_score:      float
    auc_roc:       float
    features_used: int
    threshold_block:         float
    threshold_manual_review: float
