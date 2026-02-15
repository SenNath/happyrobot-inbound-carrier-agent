import re

from sqlalchemy import Numeric, case, cast, func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Call, Load


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
            func.count(Call.id).label("total_calls"),
            func.sum(case((Call.carrier_verified.is_(True), 1), else_=0)).label("verified"),
            func.sum(func.coalesce(Call.loads_presented_count, 0)).label("loads_pitched"),
            func.sum(case((func.lower(Call.call_outcome) == "booked", 1), else_=0)).label("booked"),
        )
        result = (await self.session.execute(stage_query)).one()
        return [
            {"stage": "Calls Received", "value": int(result.total_calls or 0)},
            {"stage": "Verified", "value": int(result.verified or 0)},
            {"stage": "Loads Pitched", "value": int(result.loads_pitched or 0)},
            {"stage": "Booked", "value": int(result.booked or 0)},
        ]

    async def sentiment_timeseries(self) -> list[dict]:
        date_bucket = func.date(Call.created_at)
        sentiment_avg_raw = func.coalesce(
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
        query = (
            select(
                date_bucket.label("date"),
                func.round(cast(sentiment_avg_raw, Numeric(6, 2)), 2).label("avg_sentiment"),
            )
            .group_by(date_bucket)
            .order_by(date_bucket)
        )
        rows = (await self.session.execute(query)).all()
        return [{"date": str(row.date), "avg_sentiment": float(row.avg_sentiment)} for row in rows]

    async def sentiment_distribution(self) -> list[dict]:
        sentiment_expr = func.coalesce(func.lower(Call.sentiment), literal_column("'unknown'"))
        query = (
            select(
                sentiment_expr.label("sentiment"),
                func.count(Call.id).label("count"),
            )
            .group_by(sentiment_expr)
            .order_by(func.count(Call.id).desc())
        )
        rows = (await self.session.execute(query)).all()
        return [{"sentiment": row.sentiment, "count": int(row.count)} for row in rows]

    async def load_performance_insights(self) -> list[dict]:
        equipment_expr = func.lower(Call.equipment_type)
        query = (
            select(
                equipment_expr.label("equipment_type_raw"),
                Load.origin.label("origin"),
                Load.destination.label("destination"),
                func.count(Call.id).label("total_calls"),
                func.sum(case((func.lower(Call.call_outcome) == "booked", 1), else_=0)).label("booked_calls"),
                func.round(cast(func.coalesce(func.avg(Call.final_rate), 0.0), Numeric(10, 2)), 2).label("avg_final_rate"),
                func.round(
                    cast(func.coalesce(func.avg(cast(Load.loadboard_rate, Numeric(10, 2))), 0.0), Numeric(10, 2)),
                    2,
                ).label("avg_loadboard_rate"),
                func.round(cast(func.coalesce(func.avg(Load.miles), 0.0), Numeric(10, 2)), 2).label("avg_miles"),
            )
            .select_from(Call)
            .join(Load, Load.load_id == Call.load_id_discussed, isouter=True)
            .where(Call.load_id_discussed.is_not(None), Call.equipment_type.is_not(None))
            .group_by(equipment_expr, Load.origin, Load.destination)
            .order_by(func.count(Call.id).desc())
            .limit(40)
        )
        rows = (await self.session.execute(query)).all()

        def normalize_equipment(raw: str | None) -> str | None:
            if raw is None:
                return None
            value = raw.strip().lower()
            if not value:
                return None
            tokens = [token.strip() for token in re.split(r"[,/&;|]+", value) if token.strip()]
            recognized: list[str] = []
            for token in tokens:
                if "dry" in token and "van" in token:
                    recognized.append("Dry Van")
                elif "reefer" in token:
                    recognized.append("Reefer")
                elif "flatbed" in token:
                    recognized.append("Flatbed")
            # Ignore mixed/ambiguous values (e.g. "reefer, dry van").
            if len(set(recognized)) != 1:
                return None
            return recognized[0]

        insights: list[dict] = []
        for row in rows:
            equipment_type = normalize_equipment(row.equipment_type_raw)
            if equipment_type is None:
                continue
            total_calls = int(row.total_calls or 0)
            booked_calls = int(row.booked_calls or 0)
            booking_rate = round((booked_calls / total_calls) * 100.0, 2) if total_calls else 0.0
            avg_final_rate = float(row.avg_final_rate or 0.0)
            avg_loadboard_rate = float(row.avg_loadboard_rate or 0.0)
            market_gap_pct = (
                round(((avg_final_rate - avg_loadboard_rate) / avg_loadboard_rate) * 100.0, 2) if avg_loadboard_rate else 0.0
            )
            insights.append(
                {
                    "equipment_type": equipment_type,
                    "origin": row.origin or "Unknown",
                    "destination": row.destination or "Unknown",
                    "total_calls": total_calls,
                    "booked_calls": booked_calls,
                    "booking_rate": booking_rate,
                    "avg_final_rate": avg_final_rate,
                    "avg_loadboard_rate": avg_loadboard_rate,
                    "avg_miles": float(row.avg_miles or 0.0),
                    "market_gap_pct": market_gap_pct,
                }
            )
        return insights
