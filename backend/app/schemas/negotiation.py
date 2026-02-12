from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_serializer


class EvaluateOfferRequest(BaseModel):
    load_id: str = Field(min_length=1, max_length=64)
    carrier_offer: Decimal = Field(gt=0)
    round_number: int = Field(ge=1, le=10)


class EvaluateOfferResponse(BaseModel):
    decision: Literal["accept", "counter", "reject", "needs_more_info"]
    counter_rate: Decimal | None = None
    reasoning: str | None = None

    @field_serializer("counter_rate")
    def serialize_counter_rate(self, value: Decimal | None) -> float | None:
        return float(value) if value is not None else None
