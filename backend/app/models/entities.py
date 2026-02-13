from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Load(Base):
    __tablename__ = "loads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    load_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    origin: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    destination: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    pickup_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    delivery_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    equipment_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    loadboard_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    weight: Mapped[int] = mapped_column(Integer, nullable=False)
    commodity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    miles: Mapped[int] = mapped_column(Integer, nullable=False)
    dimensions: Mapped[str] = mapped_column(String(120), nullable=False)
    num_of_pieces: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    negotiations: Mapped[list["Negotiation"]] = relationship(back_populates="load")


class Call(Base):
    __tablename__ = "calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    call_outcome: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    sentiment: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    mc_number: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    carrier_verified: Mapped[bool | None] = mapped_column(Boolean, nullable=True, index=True)
    verification_failure_reason: Mapped[str | None] = mapped_column(String(128), nullable=True)
    loads_returned_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    loads_presented_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    carrier_interest_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    load_id_discussed: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    initial_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    carrier_counter_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    negotiation_rounds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deal_margin_pressure: Mapped[str | None] = mapped_column(String(32), nullable=True)
    equipment_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    origin_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    availability_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    driver_contact_collected: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    was_transferred: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    transfer_reason: Mapped[str | None] = mapped_column(String(128), nullable=True)
    analytics_payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    server_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Negotiation(Base):
    __tablename__ = "negotiations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    call_sid: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    load_id: Mapped[str] = mapped_column(String(64), ForeignKey("loads.load_id"), nullable=False, index=True)
    carrier_offer: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    decision: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    counter_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    load: Mapped[Load] = relationship(back_populates="negotiations")
