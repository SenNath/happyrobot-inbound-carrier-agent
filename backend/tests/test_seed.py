from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select

from app.db.seed import SEED_LOADS, seed_loads_append_missing
from app.models import Load


@pytest.mark.asyncio
async def test_seed_loads_append_missing_is_idempotent(db_session):
    row = SEED_LOADS[0]
    existing = Load(
        **row,
        pickup_datetime=datetime.now(timezone.utc) + timedelta(hours=1),
        delivery_datetime=datetime.now(timezone.utc) + timedelta(hours=10),
        is_active=True,
    )
    db_session.add(existing)
    await db_session.commit()

    inserted_first = await seed_loads_append_missing(db_session)
    total_after_first = (await db_session.execute(select(func.count(Load.id)))).scalar_one()

    inserted_second = await seed_loads_append_missing(db_session)
    total_after_second = (await db_session.execute(select(func.count(Load.id)))).scalar_one()

    assert inserted_first == len(SEED_LOADS) - 1
    assert int(total_after_first) == len(SEED_LOADS)
    assert inserted_second == 0
    assert int(total_after_second) == len(SEED_LOADS)
