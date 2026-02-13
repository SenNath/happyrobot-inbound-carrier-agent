"""rebuild calls analytics schema

Revision ID: 20260213_0002
Revises: 20260212_0001
Create Date: 2026-02-13 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260213_0002"
down_revision: str | None = "20260212_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index(op.f("ix_calls_mc_number"), table_name="calls")
    op.drop_index(op.f("ix_calls_id"), table_name="calls")
    op.drop_index(op.f("ix_calls_call_sid"), table_name="calls")
    op.drop_table("calls")

    op.create_table(
        "calls",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("call_outcome", sa.String(length=64), nullable=False),
        sa.Column("sentiment", sa.String(length=32), nullable=True),
        sa.Column("mc_number", sa.String(length=32), nullable=True),
        sa.Column("carrier_verified", sa.Boolean(), nullable=True),
        sa.Column("verification_failure_reason", sa.String(length=128), nullable=True),
        sa.Column("loads_returned_count", sa.Integer(), nullable=True),
        sa.Column("loads_presented_count", sa.Integer(), nullable=True),
        sa.Column("carrier_interest_level", sa.String(length=32), nullable=True),
        sa.Column("load_id_discussed", sa.String(length=64), nullable=True),
        sa.Column("initial_rate", sa.Float(), nullable=True),
        sa.Column("carrier_counter_rate", sa.Float(), nullable=True),
        sa.Column("final_rate", sa.Float(), nullable=True),
        sa.Column("negotiation_rounds", sa.Integer(), nullable=True),
        sa.Column("deal_margin_pressure", sa.String(length=32), nullable=True),
        sa.Column("equipment_type", sa.String(length=50), nullable=True),
        sa.Column("origin_location", sa.String(length=255), nullable=True),
        sa.Column("availability_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("driver_contact_collected", sa.Boolean(), nullable=True),
        sa.Column("was_transferred", sa.Boolean(), nullable=True),
        sa.Column("transfer_reason", sa.String(length=128), nullable=True),
        sa.Column("analytics_payload", sa.JSON(), nullable=False),
        sa.Column("server_timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_calls_call_outcome"), "calls", ["call_outcome"], unique=False)
    op.create_index(op.f("ix_calls_carrier_verified"), "calls", ["carrier_verified"], unique=False)
    op.create_index(op.f("ix_calls_id"), "calls", ["id"], unique=False)
    op.create_index(op.f("ix_calls_load_id_discussed"), "calls", ["load_id_discussed"], unique=False)
    op.create_index(op.f("ix_calls_mc_number"), "calls", ["mc_number"], unique=False)
    op.create_index(op.f("ix_calls_sentiment"), "calls", ["sentiment"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_calls_sentiment"), table_name="calls")
    op.drop_index(op.f("ix_calls_mc_number"), table_name="calls")
    op.drop_index(op.f("ix_calls_load_id_discussed"), table_name="calls")
    op.drop_index(op.f("ix_calls_id"), table_name="calls")
    op.drop_index(op.f("ix_calls_carrier_verified"), table_name="calls")
    op.drop_index(op.f("ix_calls_call_outcome"), table_name="calls")
    op.drop_table("calls")

    op.create_table(
        "calls",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("call_sid", sa.String(length=128), nullable=False),
        sa.Column("mc_number", sa.String(length=32), nullable=True),
        sa.Column("load_id", sa.String(length=64), nullable=True),
        sa.Column("final_decision", sa.String(length=32), nullable=True),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("sentiment_score", sa.Float(), nullable=True),
        sa.Column("call_duration_seconds", sa.Integer(), nullable=True),
        sa.Column("analytics_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("call_sid"),
    )
    op.create_index(op.f("ix_calls_call_sid"), "calls", ["call_sid"], unique=False)
    op.create_index(op.f("ix_calls_id"), "calls", ["id"], unique=False)
    op.create_index(op.f("ix_calls_mc_number"), "calls", ["mc_number"], unique=False)
