from pydantic import BaseModel, Field


class VerifyCarrierRequest(BaseModel):
    mc_number: str = Field(min_length=1, max_length=32)


class VerifyCarrierResponse(BaseModel):
    eligible: bool
    verification_status: str | None = None
