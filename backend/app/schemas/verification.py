from typing import Literal

from pydantic import BaseModel, Field


class VerifyCarrierRequest(BaseModel):
    mc_number: str = Field(min_length=1, max_length=32)


class VerifyCarrierResponse(BaseModel):
    eligible: bool
    verification: Literal["verified", "not_authorized", "invalid_mc", "verification_unavailable"]
    legal_name: str | None = None
    mc_number: str
