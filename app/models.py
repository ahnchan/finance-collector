from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, time


class TokenRequest(BaseModel):
    client_id: str
    client_secret: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TickerRequest(BaseModel):
    ticker: str
    date: Optional[date] = None
    country: Optional[str] = None


class HistoricalPrice(BaseModel):
    date: date
    time: time
    open: float
    high: float
    low: float
    close: float
    volume: int


class TickerResponse(BaseModel):
    ticker: str
    country: str
    prices: List[HistoricalPrice]
    metadata: Dict[str, Any] = Field(default_factory=dict)
