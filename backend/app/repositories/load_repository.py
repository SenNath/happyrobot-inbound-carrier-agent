from datetime import datetime, timedelta, timezone

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Load


class LoadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search_loads(
        self,
        equipment_type: str,
        origin_location: str,
        availability_time: datetime,
        limit: int = 15,
    ) -> list[Load]:
        if availability_time.tzinfo is None:
            availability_time = availability_time.replace(tzinfo=timezone.utc)

        upper_bound = availability_time + timedelta(days=5)
        origin_token = origin_location.split(",")[0].strip().lower()

        query: Select[tuple[Load]] = (
            select(Load)
            .where(Load.is_active.is_(True))
            .where(func.lower(Load.equipment_type) == equipment_type.lower())
            .where(func.lower(Load.origin).contains(origin_token))
            .where(Load.pickup_datetime >= availability_time)
            .where(Load.pickup_datetime <= upper_bound)
            .order_by(Load.pickup_datetime.asc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_load_id(self, load_id: str) -> Load | None:
        result = await self.session.execute(select(Load).where(Load.load_id == load_id))
        return result.scalar_one_or_none()

    async def all_loads(self) -> list[Load]:
        result = await self.session.execute(select(Load).order_by(Load.pickup_datetime.asc()))
        return list(result.scalars().all())
