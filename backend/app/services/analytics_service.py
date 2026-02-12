from app.repositories.call_repository import CallRepository
from app.repositories.load_repository import LoadRepository
from app.repositories.negotiation_repository import NegotiationRepository


class AnalyticsService:
    def __init__(
        self,
        call_repo: CallRepository,
        negotiation_repo: NegotiationRepository,
        load_repo: LoadRepository,
    ) -> None:
        self.call_repo = call_repo
        self.negotiation_repo = negotiation_repo
        self.load_repo = load_repo

    async def overview(self) -> dict:
        base = await self.call_repo.overview_stats()
        revenue = await self.negotiation_repo.revenue_accepted()
        base["revenue_accepted"] = round(revenue, 2)
        return base

    async def funnel(self) -> list[dict]:
        return await self.call_repo.funnel_breakdown()

    async def negotiation_insights(self) -> list[dict]:
        return await self.negotiation_repo.decision_breakdown()

    async def sentiment(self) -> list[dict]:
        return await self.call_repo.sentiment_timeseries()

    async def load_performance(self) -> list[dict]:
        base = await self.negotiation_repo.load_performance()
        loads = {load.load_id: load for load in await self.load_repo.all_loads()}

        enriched = []
        for item in base:
            load = loads.get(item["load_id"])
            enriched.append(
                {
                    **item,
                    "loadboard_rate": float(load.loadboard_rate) if load else 0.0,
                }
            )
        return enriched
