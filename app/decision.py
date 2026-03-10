# app/decision.py — Decision Engine
from typing import Literal
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

DecisionType = Literal["approve", "manual_review", "block"]

DECISION_PRIORITY = ["approve", "manual_review", "block"]


def _escalate(d1: DecisionType, d2: DecisionType) -> DecisionType:
    """Return the higher-severity decision of the two."""
    return d1 if DECISION_PRIORITY.index(d1) >= DECISION_PRIORITY.index(d2) else d2


def make_decision(fraud_score: float, transaction_amt: float) -> dict:
    """
    Apply configurable thresholds to produce a final decision.

    Rules (applied in order, most restrictive wins):
      1. fraud_score >= BLOCK threshold          → block
      2. fraud_score >= MANUAL_REVIEW threshold  → manual_review
      3. transaction_amt >= HIGH_VALUE_AMOUNT    → escalate to HIGH_VALUE_FLOOR minimum
      4. else                                    → approve

    Returns a dict with decision, fraud_score, and the triggered rule.
    """
    thresholds = config.FRAUD_SCORE_THRESHOLDS

    # Base decision from score
    if fraud_score >= thresholds["block"]:
        base_decision: DecisionType = "block"
        triggered_rule = f"fraud_score {fraud_score:.3f} >= block threshold {thresholds['block']}"
    elif fraud_score >= thresholds["manual_review"]:
        base_decision = "manual_review"
        triggered_rule = f"fraud_score {fraud_score:.3f} >= manual_review threshold {thresholds['manual_review']}"
    else:
        base_decision = "approve"
        triggered_rule = f"fraud_score {fraud_score:.3f} below all thresholds"

    # High-value override
    final_decision = base_decision
    if transaction_amt >= config.HIGH_VALUE_AMOUNT_USD:
        floor: DecisionType = config.HIGH_VALUE_FLOOR  # type: ignore
        final_decision = _escalate(base_decision, floor)
        if final_decision != base_decision:
            triggered_rule += f" | escalated: transaction ${transaction_amt:,.0f} >= high-value threshold ${config.HIGH_VALUE_AMOUNT_USD:,}"

    return {
        "decision":     final_decision,
        "fraud_score":  round(fraud_score, 4),
        "triggered_rule": triggered_rule,
    }
