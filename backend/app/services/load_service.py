from app.repositories.load_repository import LoadRepository
from app.schemas.load import LoadOut


class LoadService:
    def __init__(self, repo: LoadRepository) -> None:
        self.repo = repo

    async def search(self, equipment_type: str, origin_location: str, availability_time):
        rows = await self.repo.search_loads(equipment_type, origin_location, availability_time)
        return [
            LoadOut(
                load_id=row.load_id,
                origin=row.origin,
                destination=row.destination,
                pickup_datetime=row.pickup_datetime,
                delivery_datetime=row.delivery_datetime,
                equipment_type=row.equipment_type,
                loadboard_rate=row.loadboard_rate,
                notes=row.notes,
                weight=row.weight,
                commodity_type=row.commodity_type,
                miles=row.miles,
                dimensions=row.dimensions,
                num_of_pieces=row.num_of_pieces,
            )
            for row in rows
        ]
