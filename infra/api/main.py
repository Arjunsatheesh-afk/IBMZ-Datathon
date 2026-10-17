import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Locate the real scorer package
EXPORT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EXPORT_DIR))

from scorer import Scorer

app = FastAPI(
    title="STARK Paradox Scoring API",
    description="Real fraud scoring API for the IBM Z Datathon",
    version="1.0.0",
)

class ScoreRequest(BaseModel):
    tx_id: str
    customer_id: str
    counterparty_id: str
    amount: float = Field(ge=0)
    type: str
    step: int = Field(ge=0)

class ScoreResponse(BaseModel):
    tx_id: str
    risk_score: float
    top_reason: str

# The secret is mounted at runtime, never baked into the image.
scorer = Scorer(
    str(EXPORT_DIR / "model.json"),
    str(EXPORT_DIR / "state.json"),
    "/run/secrets/hmac.key",
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/score", response_model=ScoreResponse)
def score_transaction(request: ScoreRequest):
    try:
        result = scorer.score(request.model_dump())
        return ScoreResponse(
            tx_id=str(result["tx_id"]),
            risk_score=float(result["risk_score"]),
            top_reason=str(result["top_reason"]),
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Scoring failed")
