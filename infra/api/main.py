
from fastapi import FastAPI
from pydantic import BaseModel, Field
import random

app = FastAPI(
    title="STARK Paradox Scoring API",
    description="Dummy fraud scoring API for the IBM Z Datathon",
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


def score(request: ScoreRequest) -> ScoreResponse:
    """Temporary dummy scorer; replace with the real scorer later."""
    return ScoreResponse(
        tx_id=request.tx_id,
        risk_score=round(random.random(), 4),
        top_reason="Dummy score: real model integration pending",
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/score", response_model=ScoreResponse)
def score_transaction(request: ScoreRequest):
    return score(request)

