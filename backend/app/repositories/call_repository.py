from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Call


class CallRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_call(self, payload: dict) -> Call:
        call = Call(**payload)
        self.session.add(call)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(call)
        return call

    async def overview_stats(self) -> dict:
        total_calls_q = select(func.count(Call.id))
        verified_q = select(func.count(Call.id)).where(Call.mc_number.is_not(None))
        booked_q = select(func.count(Call.id)).where(Call.final_decision == "accept")
        avg_sentiment_q = select(func.coalesce(func.avg(Call.sentiment_score), 0.0))

        total_calls = int((await self.session.execute(total_calls_q)).scalar_one())
        verified = int((await self.session.execute(verified_q)).scalar_one())
        booked = int((await self.session.execute(booked_q)).scalar_one())
        avg_sentiment = float((await self.session.execute(avg_sentiment_q)).scalar_one())

        return {
            "total_calls": total_calls,
            "verified_carriers": verified,
            "booked_loads": booked,
            "avg_sentiment": round(avg_sentiment, 2),
        }

    async def funnel_breakdown(self) -> list[dict]:
        stage_query = select(
            func.sum(case((Call.mc_number.is_not(None), 1), else_=0)).label("verified"),
            func.sum(case((Call.load_id.is_not(None), 1), else_=0)).label("matched"),
            func.sum(case((Call.final_decision == "accept", 1), else_=0)).label("booked"),
        )
        result = (await self.session.execute(stage_query)).one()
        return [
            {"stage": "Verified", "value": int(result.verified or 0)},
            {"stage": "Load Matched", "value": int(result.matched or 0)},
            {"stage": "Booked", "value": int(result.booked or 0)},
        ]

    async def sentiment_timeseries(self) -> list[dict]:
        date_bucket = func.date(Call.created_at)
        query = (
            select(
                date_bucket.label("date"),
                func.round(func.coalesce(func.avg(Call.sentiment_score), 0.0), 2).label("avg_sentiment"),
            )
            .group_by(date_bucket)
            .order_by(date_bucket)
        )
        rows = (await self.session.execute(query)).all()
        return [{"date": str(row.date), "avg_sentiment": float(row.avg_sentiment)} for row in rows]
