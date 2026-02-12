from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_serializer


class SearchLoadsRequest(BaseModel):
    equipment_type: str = Field(min_length=1, max_length=50)
    origin_location: str = Field(min_length=1, max_length=255)
    availability_time: datetime


class LoadOut(BaseModel):
    load_id: str
    origin: str
    destination: str
    pickup_datetime: datetime
    delivery_datetime: datetime
    equipment_type: str
    loadboard_rate: Decimal
    notes: str
    weight: int
    commodity_type: str
    miles: int
    dimensions: str
    num_of_pieces: int

    @field_serializer("loadboard_rate")
    def serialize_loadboard_rate(self, value: Decimal) -> float:
        return float(value)


class SearchLoadsResponse(BaseModel):
    loads: list[LoadOut]
