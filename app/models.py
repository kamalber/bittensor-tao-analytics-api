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
    netuid: int
    hotkey: str
    action_type: str  # stake or unstake
    amount: float
    sentiment_score: Optional[float] = None

class StakeActionResponse(BaseModel):
    success: bool
    transaction_hash: str
    amount: float
    netuid: int
    hotkey: str
    action: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    mock: Optional[bool] = False

class SubnetInfo(BaseModel):
    netuid: int
    name: Optional[str] = None
    total_stake: float
    validator_count: int
    miner_count: int
    emission_rate: Optional[float] = None
    difficulty: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SubnetListResponse(BaseModel):
    subnets: List[SubnetInfo]
    total: int
    page: int
    page_size: int

class ValidatorInfo(BaseModel):
    netuid: int
    hotkey: str
    stake: float
    trust: Optional[float] = None
    consensus: Optional[float] = None
    incentive: Optional[float] = None
    dividends: Optional[float] = None
    rank: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValidatorListResponse(BaseModel):
    validators: List[ValidatorInfo]
    total: int
    page: int
    page_size: int
    netuid: int

class MinerInfo(BaseModel):
    netuid: int
    hotkey: str
    uid: int
    stake: Optional[float] = None
    trust: Optional[float] = None
    consensus: Optional[float] = None
    incentive: Optional[float] = None
    dividends: Optional[float] = None
    emission: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MinerListResponse(BaseModel):
    miners: List[MinerInfo]
    total: int
    page: int
    page_size: int
    netuid: int

class WalletBalanceResponse(BaseModel):
    wallet_address: str
    balance: float
    staked_balance: float
    total_balance: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StakeHistoryItem(BaseModel):
    id: str
    action_type: str
    netuid: int
    hotkey: str
    amount: float
    sentiment_score: Optional[float] = None
    transaction_hash: Optional[str] = None
    status: str
    created_at: datetime

class StakeHistoryResponse(BaseModel):
    history: List[StakeHistoryItem]
    total: int
    page: int
    page_size: int

class NetworkStats(BaseModel):
    total_subnets: int
    total_stake: float
    total_validators: int
    total_miners: int
    avg_emission_rate: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DividendHistoryItem(BaseModel):
    id: str
    netuid: int
    hotkey: str
    dividend: float
    from_cache: bool
    created_at: datetime

class DividendHistoryResponse(BaseModel):
    history: List[DividendHistoryItem]
    total: int
    page: int
    page_size: int
    average_dividend: Optional[float] = None

class SentimentScoreResponse(BaseModel):
    topic: str
    score: float
    confidence: float
    tweets_analyzed: int
    summary: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


