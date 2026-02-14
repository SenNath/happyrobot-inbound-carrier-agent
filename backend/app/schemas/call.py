from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _normalize_optional_string(value):
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "" or stripped.lower() in {"null", "none", "n/a"}:
            return None
        return stripped
    return value


def _coerce_optional_bool(value):
    value = _normalize_optional_string(value)
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    lowered = str(value).strip().lower()
    if lowered in {"true", "1", "yes", "y"}:
        return True
    if lowered in {"false", "0", "no", "n"}:
        return False
    raise ValueError("Invalid boolean value")


def _coerce_optional_int(value):
    value = _normalize_optional_string(value)
    if value is None:
        return None
    return int(float(value))


def _coerce_optional_float(value):
    value = _normalize_optional_string(value)
    if value is None:
        return None
    return float(value)


class LogCallRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    call_outcome: str = Field(min_length=1, max_length=64)
    sentiment: str | None = None
    mc_number: str | None = None
    carrier_verified: bool | None = None
    verification_failure_reason: str | None = None
    loads_returned_count: int | None = None
    loads_presented_count: int | None = None
    carrier_interest_level: str | None = None
    load_id_discussed: str | None = None
    initial_rate: float | None = None
    carrier_counter_rate: float | None = None
    final_rate: float | None = None
    negotiation_rounds: int | None = None
    deal_margin_pressure: str | None = None
    equipment_type: str | None = None
    origin_location: str | None = None
    availability_time: datetime | None = None
    driver_contact_collected: bool | None = None
    was_transferred: bool | None = None
    transfer_reason: str | None = None

    @field_validator(
        "sentiment",
        "mc_number",
        "verification_failure_reason",
        "carrier_interest_level",
        "load_id_discussed",
        "deal_margin_pressure",
        "equipment_type",
        "origin_location",
        "transfer_reason",
        mode="before",
    )
    @classmethod
    def normalize_optional_strings(cls, value):
        return _normalize_optional_string(value)

    @field_validator("carrier_verified", "driver_contact_collected", "was_transferred", mode="before")
    @classmethod
    def normalize_optional_booleans(cls, value):
        return _coerce_optional_bool(value)

    @field_validator("loads_returned_count", "loads_presented_count", "negotiation_rounds", mode="before")
    @classmethod
    def normalize_optional_integers(cls, value):
        return _coerce_optional_int(value)

    @field_validator("initial_rate", "carrier_counter_rate", "final_rate", mode="before")
    @classmethod
    def normalize_optional_floats(cls, value):
        return _coerce_optional_float(value)

    @field_validator("availability_time", mode="before")
    @classmethod
    def normalize_optional_datetime(cls, value):
        return _normalize_optional_string(value)


class LogCallResponse(BaseModel):
    status: str
    call_id: int
