# app/logger.py — SQLite Transaction Audit Log
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "data/trustshield.db"


def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp      TEXT,
            amount         REAL,
            decision       TEXT,
            fraud_score    REAL,
            triggered_rule TEXT,
            top_factors    TEXT,
            latency_ms     REAL
        )
    """)
    conn.commit()
    conn.close()


def log_transaction(amount, decision, fraud_score, triggered_rule, top_factors, latency_ms):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO transactions
            (timestamp, amount, decision, fraud_score, triggered_rule, top_factors, latency_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        amount,
        decision,
        fraud_score,
        triggered_rule,
        json.dumps([f.model_dump() for f in top_factors]),
        latency_ms,
    ))
    conn.commit()
    conn.close()


def get_dashboard_stats():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM transactions")
    total = cur.fetchone()[0]

    if total == 0:
        conn.close()
        return {
            "total_transactions": 0,
            "fraud_rate_pct": 0.0,
            "avg_latency_ms": 0.0,
            "decisions": {"approve": 0, "manual_review": 0, "block": 0},
            "avg_fraud_score": 0.0,
            "last_10_transactions": [],
        }

    cur.execute("SELECT COUNT(*) FROM transactions WHERE decision='block'")
    blocked = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM transactions WHERE decision='manual_review'")
    manual = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM transactions WHERE decision='approve'")
    approved = cur.fetchone()[0]

    cur.execute("SELECT AVG(latency_ms) FROM transactions")
    avg_latency = round(cur.fetchone()[0] or 0, 2)

    cur.execute("SELECT AVG(fraud_score) FROM transactions")
    avg_score = round(cur.fetchone()[0] or 0, 4)

    cur.execute("""
        SELECT timestamp, amount, decision, fraud_score, latency_ms
        FROM transactions ORDER BY id DESC LIMIT 10
    """)
    last_10 = [
        {"timestamp": r[0], "amount": r[1], "decision": r[2],
         "fraud_score": r[3], "latency_ms": r[4]}
        for r in cur.fetchall()
    ]

    conn.close()
    return {
        "total_transactions":   total,
        "fraud_rate_pct":       round((blocked / total) * 100, 2),
        "avg_latency_ms":       avg_latency,
        "decisions":            {"approve": approved, "manual_review": manual, "block": blocked},
        "avg_fraud_score":      avg_score,
        "last_10_transactions": last_10,
    }