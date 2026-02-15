from decimal import Decimal

from sqlalchemy import Numeric, case, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Negotiation


class NegotiationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_entry(
        self,
        call_sid: str | None,
        load_id: str,
        carrier_offer: Decimal,
        round_number: int,
        decision: str,
        counter_rate: Decimal | None,
        reasoning: str,
    ) -> Negotiation:
        entry = Negotiation(
            call_sid=call_sid,
            load_id=load_id,
            carrier_offer=carrier_offer,
            round_number=round_number,
            decision=decision,
            counter_rate=counter_rate,
            reasoning=reasoning,
        )
        self.session.add(entry)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def latest_counter_before_round(self, load_id: str, round_number: int) -> Decimal | None:
        query = (
            select(Negotiation.counter_rate)
            .where(
                Negotiation.load_id == load_id,
                Negotiation.round_number < round_number,
                Negotiation.counter_rate.is_not(None),
            )
            .order_by(Negotiation.round_number.desc(), Negotiation.created_at.desc(), Negotiation.id.desc())
            .limit(1)
        )
        return (await self.session.execute(query)).scalar_one_or_none()

    async def decision_breakdown(self) -> list[dict]:
        query = (
            select(
                Negotiation.decision,
                func.count(Negotiation.id).label("count"),
                func.round(func.avg(Negotiation.round_number), 2).label("avg_round"),
            )
            .group_by(Negotiation.decision)
            .order_by(func.count(Negotiation.id).desc())
        )
        rows = (await self.session.execute(query)).all()
        return [
            {
                "decision": row.decision,
                "count": int(row.count),
                "avg_round": float(row.avg_round or 0),
            }
            for row in rows
        ]

    async def revenue_accepted(self) -> float:
        query = select(func.coalesce(func.sum(Negotiation.carrier_offer), 0)).where(Negotiation.decision == "accept")
        value = (await self.session.execute(query)).scalar_one()
        return float(value)

    async def load_performance(self) -> list[dict]:
        attempts = func.count(Negotiation.id)
        accepted = func.sum(case((Negotiation.decision == "accept", 1), else_=0))
        acceptance_rate_expr = cast((accepted * 100.0) / func.nullif(attempts, 0), Numeric(8, 2))

        query = (
            select(
                Negotiation.load_id,
                func.round(acceptance_rate_expr, 2).label("acceptance_rate"),
                func.round(func.avg(Negotiation.carrier_offer), 2).label("avg_offer"),
            )
            .group_by(Negotiation.load_id)
            .order_by(func.count(Negotiation.id).desc())
            .limit(15)
        )
        rows = (await self.session.execute(query)).all()
        return [
            {
                "load_id": row.load_id,
                "acceptance_rate": float(row.acceptance_rate or 0),
                "avg_offer": float(row.avg_offer or 0),
            }
            for row in rows
        ]
