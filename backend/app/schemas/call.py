from pydantic import BaseModel, Field


class LogCallRequest(BaseModel):
    call_sid: str = Field(min_length=1, max_length=128)
    mc_number: str | None = None
    load_id: str | None = None
    final_decision: str | None = None
    transcript: str | None = None
    sentiment_score: float | None = None
    call_duration_seconds: int | None = None
    analytics_payload: dict = Field(default_factory=dict)


class LogCallResponse(BaseModel):
    status: str
    call_id: int
