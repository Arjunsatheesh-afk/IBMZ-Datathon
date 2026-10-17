"""Run from the folder that holds model.json, state.json and hmac.key:
   python test_scorer.py model.json state.json hmac.key
"""
import sys, time
from scorer import Scorer

model, state, key = sys.argv[1:4]
s = Scorer(model, state, key)

tx = {"tx_id": "TEST0001", "customer_id": "C000000001", "counterparty_id": "C000000002",
      "amount": 9500000.0, "type": "CASH_OUT", "step": 3}
out = s.score(tx, update=False)
print(out)
assert set(out) == {"tx_id", "risk_score", "top_reason"}
assert 0.0 <= out["risk_score"] <= 1.0
assert s.tokenize("C000000001") == s.tokenize("C000000001")      # deterministic
assert s.tokenize("C000000001") != s.tokenize("C000000002")      # distinct IDs differ

t0 = time.perf_counter()
for _ in range(200):
    s.score(tx, update=False)
print("mean latency per score: %.2f ms" % ((time.perf_counter() - t0) / 200 * 1000))
print("OK")
