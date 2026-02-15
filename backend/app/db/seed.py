import argparse
import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Load


SEED_LOADS = [
    {
        "load_id": "HR-CHI-ATL-001",
        "origin": "Chicago, IL",
        "destination": "Atlanta, GA",
        "equipment_type": "Dry Van",
        "loadboard_rate": Decimal("2450.00"),
        "notes": "Drop and hook at shipper, FCFS receiver.",
        "weight": 40120,
        "commodity_type": "Retail Goods",
        "miles": 716,
        "dimensions": "53ft trailer",
        "num_of_pieces": 24,
    },
    {
        "load_id": "HR-DAL-PHX-002",
        "origin": "Dallas, TX",
        "destination": "Phoenix, AZ",
        "equipment_type": "Reefer",
        "loadboard_rate": Decimal("3125.00"),
        "notes": "Produce, temp set to 36F.",
        "weight": 38400,
        "commodity_type": "Fresh Produce",
        "miles": 1065,
        "dimensions": "53ft reefer",
        "num_of_pieces": 20,
    },
    {
        "load_id": "HR-LAX-SEA-003",
        "origin": "Los Angeles, CA",
        "destination": "Seattle, WA",
        "equipment_type": "Flatbed",
        "loadboard_rate": Decimal("3650.00"),
        "notes": "Tarp required. Appointment delivery.",
        "weight": 42000,
        "commodity_type": "Building Materials",
        "miles": 1135,
        "dimensions": "48ft flatbed",
        "num_of_pieces": 12,
    },
    {
        "load_id": "HR-KCM-MEM-004",
        "origin": "Kansas City, MO",
        "destination": "Memphis, TN",
        "equipment_type": "Dry Van",
        "loadboard_rate": Decimal("1820.00"),
        "notes": "Live load, same-day delivery window.",
        "weight": 29500,
        "commodity_type": "Packaged Foods",
        "miles": 486,
        "dimensions": "53ft trailer",
        "num_of_pieces": 16,
    },
    {
        "load_id": "HR-NWK-MIA-005",
        "origin": "Newark, NJ",
        "destination": "Miami, FL",
        "equipment_type": "Dry Van",
        "loadboard_rate": Decimal("4275.00"),
        "notes": "High value load, team service preferred.",
        "weight": 33700,
        "commodity_type": "Consumer Electronics",
        "miles": 1276,
        "dimensions": "53ft trailer",
        "num_of_pieces": 28,
    },
    {
        "load_id": "HR-DEN-SLC-006",
        "origin": "Denver, CO",
        "destination": "Salt Lake City, UT",
        "equipment_type": "Reefer",
        "loadboard_rate": Decimal("1540.00"),
        "notes": "Frozen freight, no mixed loads.",
        "weight": 36000,
        "commodity_type": "Frozen Foods",
        "miles": 520,
        "dimensions": "53ft reefer",
        "num_of_pieces": 18,
    },
    {
        "load_id": "HR-CLT-JAX-007",
        "origin": "Charlotte, NC",
        "destination": "Jacksonville, FL",
        "equipment_type": "Dry Van",
        "loadboard_rate": Decimal("1715.00"),
        "notes": "Auto-load at shipper. Strict delivery appointment.",
        "weight": 31000,
        "commodity_type": "Paper Products",
        "miles": 390,
        "dimensions": "53ft trailer",
        "num_of_pieces": 22,
    },
    {
        "load_id": "HR-CLE-DET-008",
        "origin": "Cleveland, OH",
        "destination": "Detroit, MI",
        "equipment_type": "Flatbed",
        "loadboard_rate": Decimal("980.00"),
        "notes": "Steel coils, securement inspection required.",
        "weight": 43200,
        "commodity_type": "Steel Coils",
        "miles": 170,
        "dimensions": "48ft flatbed",
        "num_of_pieces": 6,
    },
]


async def seed_loads_if_empty(session: AsyncSession) -> None:
    existing_count = (await session.execute(select(func.count(Load.id)))).scalar_one()
    if existing_count > 0:
        return

    now = datetime.now(timezone.utc)
    inserts: list[Load] = []
    for idx, row in enumerate(SEED_LOADS):
        pickup = now + timedelta(hours=8 + idx * 6)
        delivery = pickup + timedelta(hours=10 + idx * 2)
        inserts.append(Load(**row, pickup_datetime=pickup, delivery_datetime=delivery, is_active=True))

    session.add_all(inserts)
    await session.commit()


async def seed_loads_append_missing(session: AsyncSession) -> int:
    existing_ids = set((await session.execute(select(Load.load_id))).scalars().all())
    now = datetime.now(timezone.utc)
    inserts: list[Load] = []
    for idx, row in enumerate(SEED_LOADS):
        if row["load_id"] in existing_ids:
            continue
        pickup = now + timedelta(hours=8 + idx * 6)
        delivery = pickup + timedelta(hours=10 + idx * 2)
        inserts.append(Load(**row, pickup_datetime=pickup, delivery_datetime=delivery, is_active=True))

    if inserts:
        session.add_all(inserts)
        await session.commit()
    return len(inserts)


async def _run_seed_cli(mode: str) -> None:
    from app.db.session import SessionLocal

    async with SessionLocal() as session:
        if mode == "append":
            inserted = await seed_loads_append_missing(session)
            print(f"append mode complete: inserted={inserted}")
            return
        await seed_loads_if_empty(session)
        print("if-empty mode complete")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed loads data")
    parser.add_argument(
        "--mode",
        choices=["if-empty", "append"],
        default="if-empty",
        help="if-empty: only seed when table is empty; append: insert missing seed load_ids",
    )
    args = parser.parse_args()
    asyncio.run(_run_seed_cli(args.mode))


if __name__ == "__main__":
    main()
