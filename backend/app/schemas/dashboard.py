from pydantic import BaseModel


class OverviewStats(BaseModel):
    total_calls: int
    verified_carriers: int
    booked_loads: int
    avg_sentiment: float
    revenue_accepted: float
    booking_rate: float
    avg_negotiation_rounds: float
    avg_margin_pressure: float
    verified_vs_unverified_ratio: float
    verified_count: int
    unverified_count: int


class FunnelStage(BaseModel):
    stage: str
    value: int


class NegotiationInsight(BaseModel):
    decision: str
    count: int
    avg_round: float


class SentimentPoint(BaseModel):
    date: str
    avg_sentiment: float


class SentimentDistributionPoint(BaseModel):
    sentiment: str
    count: int


class LoadPerformancePoint(BaseModel):
    equipment_type: str
    origin: str
    destination: str
    total_calls: int
    booked_calls: int
    booking_rate: float
    avg_final_rate: float
    avg_loadboard_rate: float
    avg_miles: float
    market_gap_pct: float
