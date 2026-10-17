"""
scorer.py - scoring function for the privacy-preserving fraud pipeline.

Raw identifiers are tokenized (HMAC-SHA256) FIRST. Features and the model only ever
see tokens, never raw customer or account IDs.

Contract:
  input : {tx_id, customer_id, counterparty_id, amount, type, step}
  output: {tx_id, risk_score, top_reason}
"""
import hashlib
import hmac
import json
import math
import threading

import pandas as pd
import xgboost as xgb

FEATS = ["log_amount", "is_transfer", "hour", "recv_prev_count", "recv_prev_sum", "amt_vs_recv_avg"]

REASONS = {
    "log_amount": "Unusually large amount",
    "is_transfer": "Transaction type is TRANSFER",
    "hour": "Unusual time of day",
    "recv_prev_count": "Receiver account is new or rare",
    "recv_prev_sum": "Receiver inflow history",
    "amt_vs_recv_avg": "Amount unusual for this receiver",
}


class Scorer:
    def __init__(self, model_path, state_path, hmac_key_path):
        with open(hmac_key_path, "rb") as fh:
            self._key = fh.read()
        self.model = xgb.XGBClassifier()
        self.model.load_model(model_path)
        self.booster = self.model.get_booster()
        with open(state_path) as fh:
            self.state = json.load(fh)  # receiver token -> [prior count, prior amount sum]
        self._lock = threading.Lock()

    def tokenize(self, raw_id):
        digest = hmac.new(self._key, str(raw_id).encode(), hashlib.sha256).hexdigest()
        return "TK_" + digest[:16]

    def score(self, tx, update=True):
        # 1) tokenize before anything else touches the data
        token_receiver = self.tokenize(tx["counterparty_id"])

        amount = float(tx["amount"])
        with self._lock:
            count, total = self.state.get(token_receiver, [0, 0.0])
            if update:
                self.state[token_receiver] = [count + 1, total + amount]

        # 2) causal features: only transactions BEFORE this one are used
        avg_prev = max(total / max(count, 1), 1.0)
        row = {
            "log_amount": math.log1p(amount),
            "is_transfer": 1 if tx["type"] == "TRANSFER" else 0,
            "hour": int(tx["step"]) % 24,
            "recv_prev_count": count,
            "recv_prev_sum": total,
            "amt_vs_recv_avg": amount / avg_prev,
        }
        x = pd.DataFrame([row], columns=FEATS)

        # 3) score and explain
        risk = float(self.model.predict_proba(x)[0, 1])
        contrib = self.booster.predict(xgb.DMatrix(x), pred_contribs=True)[0][:-1]
        reason = REASONS[FEATS[int(contrib.argmax())]]
        return {"tx_id": tx["tx_id"], "risk_score": round(risk, 4), "top_reason": reason}
