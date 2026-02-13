from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Load


class LoadRepository:
    EQUIPMENT_ALIASES = {
        "dryvan": "dry van",
        "dry-van": "dry van",
        "reefer": "reefer",
        "flat bed": "flatbed",
        "flat-bed": "flatbed",
    }

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
        availability_time = self._normalize_datetime(availability_time)

        query_result = await self.session.execute(select(Load).where(Load.is_active.is_(True)))
        active_loads = list(query_result.scalars().all())
        if not active_loads:
            return []

        normalized_equipment = self._normalize_equipment(equipment_type)
        normalized_origin = self._normalize_text(origin_location)
        origin_tokens = [token for token in normalized_origin.split() if len(token) >= 2]

        scored: list[tuple[int, float, Load]] = []
        for load in active_loads:
            equipment_score = self._equipment_score(normalized_equipment, load.equipment_type)
            origin_score = self._origin_score(normalized_origin, origin_tokens, load.origin)
            if equipment_score == 0 and origin_score == 0:
                continue

            total_score = (equipment_score * 2) + (origin_score * 3)
            pickup_time = self._normalize_datetime(load.pickup_datetime)
            time_distance = abs((pickup_time - availability_time).total_seconds())
            scored.append((total_score, time_distance, load))

        scored.sort(key=lambda item: (-item[0], item[1], item[2].pickup_datetime))
        return [item[2] for item in scored[:limit]]

    async def get_by_load_id(self, load_id: str) -> Load | None:
        result = await self.session.execute(select(Load).where(Load.load_id == load_id))
        return result.scalar_one_or_none()

    async def all_loads(self) -> list[Load]:
        result = await self.session.execute(select(Load).order_by(Load.pickup_datetime.asc()))
        return list(result.scalars().all())

    def _normalize_text(self, value: str) -> str:
        normalized = value.strip().lower().replace(",", " ")
        return " ".join(normalized.split())

    def _normalize_equipment(self, equipment_type: str) -> str:
        normalized = self._normalize_text(equipment_type).replace(" ", "")
        alias = self.EQUIPMENT_ALIASES.get(normalized)
        if alias:
            return alias
        return self._normalize_text(equipment_type)

    def _equipment_score(self, requested_equipment: str, load_equipment: str) -> int:
        normalized_load_equipment = self._normalize_equipment(load_equipment)
        if requested_equipment == normalized_load_equipment:
            return 3
        if requested_equipment in normalized_load_equipment or normalized_load_equipment in requested_equipment:
            return 2
        return 0

    def _origin_score(self, normalized_origin: str, origin_tokens: list[str], load_origin: str) -> int:
        normalized_load_origin = self._normalize_text(load_origin)
        if normalized_origin and normalized_origin in normalized_load_origin:
            return 3
        token_matches = sum(1 for token in origin_tokens if token in normalized_load_origin)
        if token_matches >= 2:
            return 2
        if token_matches == 1:
            return 1
        return 0

    def _normalize_datetime(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value
        return value.astimezone(timezone.utc).replace(tzinfo=None)
