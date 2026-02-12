from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories import CallRepository, LoadRepository, NegotiationRepository
from app.schemas.call import LogCallRequest, LogCallResponse
from app.schemas.dashboard import FunnelStage, LoadPerformancePoint, NegotiationInsight, OverviewStats, SentimentPoint
from app.schemas.load import SearchLoadsRequest, SearchLoadsResponse
from app.schemas.negotiation import EvaluateOfferRequest, EvaluateOfferResponse
from app.schemas.verification import VerifyCarrierRequest, VerifyCarrierResponse
from app.services import AnalyticsService, CarrierService, LoadService, NegotiationService
from app.services.fmcsa_client import FMCSAClient, FMCSAServiceError
from app.core.config import get_settings

router = APIRouter()


@router.get("/health")
async def healthcheck() -> dict:
    return {"status": "ok"}


@router.post("/verify-carrier", response_model=VerifyCarrierResponse)
async def verify_carrier(
    request: VerifyCarrierRequest,
) -> VerifyCarrierResponse:
    settings = get_settings()
    carrier_service = CarrierService(FMCSAClient(api_key=settings.fmcsa_api_key))

    try:
        result = await carrier_service.verify(request.mc_number)
        return VerifyCarrierResponse(eligible=result.eligible, verification_status=result.verification_status)
    except FMCSAServiceError:
        return VerifyCarrierResponse(eligible=False, verification_status="verification_unavailable")


@router.post("/search-loads", response_model=SearchLoadsResponse)
async def search_loads(
    request: SearchLoadsRequest,
    session: AsyncSession = Depends(get_db_session),
) -> SearchLoadsResponse:
    service = LoadService(LoadRepository(session))
    loads = await service.search(
        equipment_type=request.equipment_type,
        origin_location=request.origin_location,
        availability_time=request.availability_time,
    )
    return SearchLoadsResponse(loads=loads)


@router.post("/evaluate-offer", response_model=EvaluateOfferResponse)
async def evaluate_offer(
    request: EvaluateOfferRequest,
    session: AsyncSession = Depends(get_db_session),
) -> EvaluateOfferResponse:
    load_repo = LoadRepository(session)
    negotiation_repo = NegotiationRepository(session)

    load = await load_repo.get_by_load_id(request.load_id)
    decision, counter_rate, reasoning = NegotiationService().evaluate_offer(
        load=load,
        carrier_offer=request.carrier_offer,
        round_number=request.round_number,
    )

    if load is not None:
        await negotiation_repo.create_entry(
            call_sid=None,
            load_id=request.load_id,
            carrier_offer=request.carrier_offer,
            round_number=request.round_number,
            decision=decision,
            counter_rate=counter_rate,
            reasoning=reasoning,
        )

    return EvaluateOfferResponse(decision=decision, counter_rate=counter_rate, reasoning=reasoning)


@router.post("/log-call", response_model=LogCallResponse)
async def log_call(
    request: LogCallRequest,
    session: AsyncSession = Depends(get_db_session),
) -> LogCallResponse:
    repo = CallRepository(session)
    record = await repo.create_call(request.model_dump())
    return LogCallResponse(status="logged", call_id=record.id)


@router.get("/dashboard/overview", response_model=OverviewStats)
async def dashboard_overview(session: AsyncSession = Depends(get_db_session)) -> OverviewStats:
    service = AnalyticsService(CallRepository(session), NegotiationRepository(session), LoadRepository(session))
    payload = await service.overview()
    return OverviewStats(**payload)


@router.get("/dashboard/funnel", response_model=list[FunnelStage])
async def dashboard_funnel(session: AsyncSession = Depends(get_db_session)) -> list[FunnelStage]:
    service = AnalyticsService(CallRepository(session), NegotiationRepository(session), LoadRepository(session))
    return [FunnelStage(**row) for row in await service.funnel()]


@router.get("/dashboard/negotiations", response_model=list[NegotiationInsight])
async def dashboard_negotiations(session: AsyncSession = Depends(get_db_session)) -> list[NegotiationInsight]:
    service = AnalyticsService(CallRepository(session), NegotiationRepository(session), LoadRepository(session))
    return [NegotiationInsight(**row) for row in await service.negotiation_insights()]


@router.get("/dashboard/sentiment", response_model=list[SentimentPoint])
async def dashboard_sentiment(session: AsyncSession = Depends(get_db_session)) -> list[SentimentPoint]:
    service = AnalyticsService(CallRepository(session), NegotiationRepository(session), LoadRepository(session))
    return [SentimentPoint(**row) for row in await service.sentiment()]


@router.get("/dashboard/load-performance", response_model=list[LoadPerformancePoint])
async def dashboard_load_performance(session: AsyncSession = Depends(get_db_session)) -> list[LoadPerformancePoint]:
    service = AnalyticsService(CallRepository(session), NegotiationRepository(session), LoadRepository(session))
    return [LoadPerformancePoint(**row) for row in await service.load_performance()]
