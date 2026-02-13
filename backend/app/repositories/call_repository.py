from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Call


class CallRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_call(self, payload: dict) -> Call:
        payload_copy = dict(payload)
        analytics_payload = payload_copy.pop("analytics_payload", None)
        call = Call(**payload_copy, analytics_payload=analytics_payload or payload_copy)
        self.session.add(call)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(call)
        return call

    async def overview_stats(self) -> dict:
        metrics_query = select(
            func.count(Call.id).label("total_calls"),
            func.sum(case((Call.carrier_verified.is_(True), 1), else_=0)).label("verified"),
            func.sum(case((Call.carrier_verified.is_(False), 1), else_=0)).label("unverified"),
            func.sum(case((func.lower(Call.call_outcome) == "booked", 1), else_=0)).label("booked"),
            func.coalesce(func.avg(Call.negotiation_rounds), 0.0).label("avg_negotiation_rounds"),
            func.coalesce(
                func.avg(
                    case(
                        (func.lower(Call.deal_margin_pressure) == "high", 3.0),
                        (func.lower(Call.deal_margin_pressure) == "medium", 2.0),
                        (func.lower(Call.deal_margin_pressure) == "low", 1.0),
                        else_=None,
                    )
                ),
                0.0,
            ).label("avg_margin_pressure"),
        )
        metrics = (await self.session.execute(metrics_query)).one()
        total_calls = int(metrics.total_calls or 0)
        verified = int(metrics.verified or 0)
        unverified = int(metrics.unverified or 0)
        booked = int(metrics.booked or 0)
        booking_rate = round((booked / total_calls) * 100.0, 2) if total_calls else 0.0
        verified_ratio = round((verified / unverified), 2) if unverified else float(verified)

        sentiment_score_q = select(
            func.coalesce(
                func.avg(
                    case(
                        (func.lower(Call.sentiment) == "positive", 1.0),
                        (func.lower(Call.sentiment) == "neutral", 0.0),
                        (func.lower(Call.sentiment) == "negative", -1.0),
                        else_=None,
                    )
                ),
                0.0,
            )
        )
        avg_sentiment = float((await self.session.execute(sentiment_score_q)).scalar_one())

        return {
            "total_calls": total_calls,
            "verified_carriers": verified,
            "booked_loads": booked,
            "avg_sentiment": round(avg_sentiment, 2),
            "booking_rate": booking_rate,
            "avg_negotiation_rounds": round(float(metrics.avg_negotiation_rounds or 0.0), 2),
            "avg_margin_pressure": round(float(metrics.avg_margin_pressure or 0.0), 2),
            "verified_vs_unverified_ratio": verified_ratio,
            "verified_count": verified,
            "unverified_count": unverified,
        }

    async def funnel_breakdown(self) -> list[dict]:
        stage_query = select(
            func.sum(case((Call.carrier_verified.is_(True), 1), else_=0)).label("verified"),
            func.sum(case((Call.loads_presented_count.is_not(None), 1), else_=0)).label("presented"),
            func.sum(case((func.lower(Call.call_outcome) == "booked", 1), else_=0)).label("booked"),
        )
        result = (await self.session.execute(stage_query)).one()
        return [
            {"stage": "Verified", "value": int(result.verified or 0)},
            {"stage": "Load Presented", "value": int(result.presented or 0)},
            {"stage": "Booked", "value": int(result.booked or 0)},
        ]

    async def sentiment_timeseries(self) -> list[dict]:
        date_bucket = func.date(Call.created_at)
        query = (
            select(
                date_bucket.label("date"),
                func.round(
                    func.coalesce(
                        func.avg(
                            case(
                                (func.lower(Call.sentiment) == "positive", 1.0),
                                (func.lower(Call.sentiment) == "neutral", 0.0),
                                (func.lower(Call.sentiment) == "negative", -1.0),
                                else_=None,
                            )
                        ),
                        0.0,
                    ),
                    2,
                ).label("avg_sentiment"),
            )
            .group_by(date_bucket)
            .order_by(date_bucket)
        )
        rows = (await self.session.execute(query)).all()
        return [{"date": str(row.date), "avg_sentiment": float(row.avg_sentiment)} for row in rows]

    async def sentiment_distribution(self) -> list[dict]:
        query = (
            select(
                func.coalesce(func.lower(Call.sentiment), "unknown").label("sentiment"),
                func.count(Call.id).label("count"),
            )
            .group_by(func.coalesce(func.lower(Call.sentiment), "unknown"))
            .order_by(func.count(Call.id).desc())
        )
        rows = (await self.session.execute(query)).all()
        return [{"sentiment": row.sentiment, "count": int(row.count)} for row in rows]
