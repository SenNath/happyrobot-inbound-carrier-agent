"""init schema

Revision ID: 20260212_0001
Revises: 
Create Date: 2026-02-12 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260212_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "loads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("load_id", sa.String(length=64), nullable=False),
        sa.Column("origin", sa.String(length=255), nullable=False),
        sa.Column("destination", sa.String(length=255), nullable=False),
        sa.Column("pickup_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("delivery_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("equipment_type", sa.String(length=50), nullable=False),
        sa.Column("loadboard_rate", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("weight", sa.Integer(), nullable=False),
        sa.Column("commodity_type", sa.String(length=100), nullable=False),
        sa.Column("miles", sa.Integer(), nullable=False),
        sa.Column("dimensions", sa.String(length=120), nullable=False),
        sa.Column("num_of_pieces", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("load_id"),
    )
    op.create_index(op.f("ix_loads_equipment_type"), "loads", ["equipment_type"], unique=False)
    op.create_index(op.f("ix_loads_id"), "loads", ["id"], unique=False)
    op.create_index(op.f("ix_loads_is_active"), "loads", ["is_active"], unique=False)
    op.create_index(op.f("ix_loads_load_id"), "loads", ["load_id"], unique=False)
    op.create_index(op.f("ix_loads_origin"), "loads", ["origin"], unique=False)
    op.create_index(op.f("ix_loads_pickup_datetime"), "loads", ["pickup_datetime"], unique=False)

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

    op.create_table(
        "negotiations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("call_sid", sa.String(length=128), nullable=True),
        sa.Column("load_id", sa.String(length=64), nullable=False),
        sa.Column("carrier_offer", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("decision", sa.String(length=32), nullable=False),
        sa.Column("counter_rate", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["load_id"], ["loads.load_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_negotiations_call_sid"), "negotiations", ["call_sid"], unique=False)
    op.create_index(op.f("ix_negotiations_decision"), "negotiations", ["decision"], unique=False)
    op.create_index(op.f("ix_negotiations_id"), "negotiations", ["id"], unique=False)
    op.create_index(op.f("ix_negotiations_load_id"), "negotiations", ["load_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_negotiations_load_id"), table_name="negotiations")
    op.drop_index(op.f("ix_negotiations_id"), table_name="negotiations")
    op.drop_index(op.f("ix_negotiations_decision"), table_name="negotiations")
    op.drop_index(op.f("ix_negotiations_call_sid"), table_name="negotiations")
    op.drop_table("negotiations")

    op.drop_index(op.f("ix_calls_mc_number"), table_name="calls")
    op.drop_index(op.f("ix_calls_id"), table_name="calls")
    op.drop_index(op.f("ix_calls_call_sid"), table_name="calls")
    op.drop_table("calls")

    op.drop_index(op.f("ix_loads_pickup_datetime"), table_name="loads")
    op.drop_index(op.f("ix_loads_origin"), table_name="loads")
    op.drop_index(op.f("ix_loads_load_id"), table_name="loads")
    op.drop_index(op.f("ix_loads_is_active"), table_name="loads")
    op.drop_index(op.f("ix_loads_id"), table_name="loads")
    op.drop_index(op.f("ix_loads_equipment_type"), table_name="loads")
    op.drop_table("loads")
