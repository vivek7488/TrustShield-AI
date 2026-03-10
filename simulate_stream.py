# simulate_stream.py — Dataflow-style Transaction Stream Simulator
# Fires 100 transactions at the API and prints a summary report
# Usage: python simulate_stream.py

import urllib.request
import urllib.error
import json
import random
import time
from datetime import datetime

API_URL = "http://127.0.0.1:8000/predict"

# Transaction templates
LEGIT_TEMPLATES = [
    {"TransactionAmt": 25.99,  "card6": "debit",  "P_emaildomain": "gmail.com",   "DeviceType": "desktop"},
    {"TransactionAmt": 149.00, "card6": "credit", "P_emaildomain": "yahoo.com",   "DeviceType": "mobile"},
    {"TransactionAmt": 59.99,  "card6": "debit",  "P_emaildomain": "outlook.com", "DeviceType": "desktop"},
    {"TransactionAmt": 320.00, "card6": "credit", "P_emaildomain": "gmail.com",   "DeviceType": "desktop"},
    {"TransactionAmt": 12.50,  "card6": "debit",  "P_emaildomain": "gmail.com",   "DeviceType": "mobile"},
]

FRAUD_TEMPLATES = [
    {"TransactionAmt": 9999.99,  "card6": "credit", "P_emaildomain": "anonymous.com", "addr1": "100", "addr2": "999"},
    {"TransactionAmt": 15000.00, "card6": "credit", "P_emaildomain": "anonymous.com", "addr1": "200", "addr2": "888"},
    {"TransactionAmt": 4999.00,  "card6": "credit", "P_emaildomain": "protonmail.com","addr1": "300", "addr2": "777"},
    {"TransactionAmt": 7500.00,  "card6": "debit",  "P_emaildomain": "",              "addr1": "400", "addr2": "666"},
]


def send_transaction(payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(
        API_URL,
        data    = data,
        headers = {"Content-Type": "application/json"},
        method  = "POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    print("=" * 55)
    print("  TrustShield AI — Stream Simulator")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    results   = {"approve": 0, "manual_review": 0, "block": 0}
    latencies = []
    errors    = 0
    total     = 100

    for i in range(1, total + 1):
        # 80% legit, 20% fraud
        if random.random() < 0.8:
            payload = random.choice(LEGIT_TEMPLATES).copy()
        else:
            payload = random.choice(FRAUD_TEMPLATES).copy()

        # Add some random noise
        payload["TransactionAmt"] = round(payload["TransactionAmt"] * random.uniform(0.8, 1.2), 2)
        payload["card_age"]       = random.randint(1, 60)
        payload["TransactionDT"]  = random.randint(0, 86400)

        try:
            response = send_transaction(payload)
            decision = response["decision"]
            results[decision] += 1
            latencies.append(response["latency_ms"])

            status = {"approve": "✅", "manual_review": "⚠️ ", "block": "🚫"}[decision]
            print(f"  [{i:03d}] {status} {decision:<14} score={response['fraud_score']:.3f}  "
                  f"amt=${payload['TransactionAmt']:<8.2f} {response['latency_ms']:.1f}ms")

        except Exception as e:
            errors += 1
            print(f"  [{i:03d}] ❌ ERROR: {e}")

        time.sleep(0.05)  # 50ms between requests

    # Summary
    print("\n" + "=" * 55)
    print("  SIMULATION COMPLETE")
    print("=" * 55)
    print(f"  Total transactions : {total}")
    print(f"  Approved           : {results['approve']}")
    print(f"  Manual Review      : {results['manual_review']}")
    print(f"  Blocked            : {results['block']}")
    print(f"  Errors             : {errors}")
    if latencies:
        print(f"  Avg latency        : {sum(latencies)/len(latencies):.1f}ms")
        print(f"  Max latency        : {max(latencies):.1f}ms")
        print(f"  Min latency        : {min(latencies):.1f}ms")
    print("=" * 55)
    print("\nCheck live stats: http://127.0.0.1:8000/dashboard")


if __name__ == "__main__":
    main()
