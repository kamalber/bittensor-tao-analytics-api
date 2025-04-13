from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

class TaoDividendResponse(BaseModel):
    netuid: int
    hotkey: str
    dividend: float
    cached: bool
    stake_tx_triggered: Optional[bool] = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SentimentAnalysisResult(BaseModel):
    score: float  # -100 to 100
    tweets_analyzed: int
    summary: str

class StakeActionRequest(BaseModel):
    netuid: Optional[int] = None
    hotkey: Optional[str] = None
    action_type: str  # stake or unstake
    amount: float
    sentiment_score: Optional[float] = None


