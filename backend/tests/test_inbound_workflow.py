from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.models import Load
from app.services.fmcsa_client import FMCSAResult, FMCSAServiceError

API_HEADERS = {"x-api-key": "test-api-key"}


async def insert_load(db_session, load_id: str = "TEST-LOAD-001", rate: Decimal = Decimal("2000.00")) -> Load:
    pickup = datetime.now(timezone.utc) + timedelta(hours=4)
    delivery = pickup + timedelta(hours=16)
    load = Load(
        load_id=load_id,
        origin="Chicago, IL",
        destination="Atlanta, GA",
        pickup_datetime=pickup,
        delivery_datetime=delivery,
        equipment_type="Dry Van",
        loadboard_rate=rate,
        notes="Live load",
        weight=38000,
        commodity_type="General Freight",
        miles=705,
        dimensions="53ft trailer",
        num_of_pieces=22,
        is_active=True,
    )
    db_session.add(load)
    await db_session.commit()
    await db_session.refresh(load)
    return load


@pytest.mark.asyncio
async def test_successful_booking_flow(client, db_session, monkeypatch):
    load = await insert_load(db_session, load_id="BOOK-LOAD-001", rate=Decimal("2200.00"))

    async def mock_verify(self, mc_number: str):
        return FMCSAResult(eligible=True, verification_status="eligible")

    monkeypatch.setattr("app.services.fmcsa_client.FMCSAClient.verify_carrier", mock_verify)

    verify_resp = await client.post("/verify-carrier", json={"mc_number": "123456"}, headers=API_HEADERS)
    assert verify_resp.status_code == 200
    assert verify_resp.json()["eligible"] is True

    search_resp = await client.post(
        "/search-loads",
        json={
            "equipment_type": "Dry Van",
            "origin_location": "Chicago, IL",
            "availability_time": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        },
        headers=API_HEADERS,
    )
    assert search_resp.status_code == 200
    loads = search_resp.json()["loads"]
    assert len(loads) == 1
    assert loads[0]["load_id"] == load.load_id

    eval_resp = await client.post(
        "/evaluate-offer",
        json={"load_id": load.load_id, "carrier_offer": 2220, "round_number": 1},
        headers=API_HEADERS,
    )
    assert eval_resp.status_code == 200
    assert eval_resp.json()["decision"] == "accept"

    log_resp = await client.post(
        "/log-call",
        json={
            "call_sid": "CA_SUCCESS_001",
            "mc_number": "123456",
            "load_id": load.load_id,
            "final_decision": "accept",
            "sentiment_score": 0.81,
            "call_duration_seconds": 372,
            "analytics_payload": {"intent": "book_load", "objections": ["rate"]},
        },
        headers=API_HEADERS,
    )
    assert log_resp.status_code == 200
    assert log_resp.json()["status"] == "logged"


@pytest.mark.asyncio
async def test_ineligible_carrier(client, monkeypatch):
    async def mock_verify(self, mc_number: str):
        return FMCSAResult(eligible=False, verification_status="ineligible")

    monkeypatch.setattr("app.services.fmcsa_client.FMCSAClient.verify_carrier", mock_verify)

    response = await client.post("/verify-carrier", json={"mc_number": "999999"}, headers=API_HEADERS)
    assert response.status_code == 200
    assert response.json() == {"eligible": False, "verification_status": "ineligible"}


@pytest.mark.asyncio
async def test_no_loads_returned(client, db_session):
    await insert_load(db_session, load_id="LOAD-OTHER-001")
    response = await client.post(
        "/search-loads",
        json={
            "equipment_type": "Reefer",
            "origin_location": "Miami, FL",
            "availability_time": datetime.now(timezone.utc).isoformat(),
        },
        headers=API_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()["loads"] == []


@pytest.mark.asyncio
async def test_three_round_negotiation_failure(client, db_session):
    load = await insert_load(db_session, load_id="NEG-FAIL-001", rate=Decimal("2000.00"))
    response = await client.post(
        "/evaluate-offer",
        json={"load_id": load.load_id, "carrier_offer": 2450, "round_number": 3},
        headers=API_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()["decision"] == "reject"


@pytest.mark.asyncio
async def test_needs_more_info_flow(client):
    response = await client.post(
        "/evaluate-offer",
        json={"load_id": "UNKNOWN-LOAD", "carrier_offer": 1500, "round_number": 1},
        headers=API_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()["decision"] == "needs_more_info"


@pytest.mark.asyncio
async def test_empty_mc_number_validation(client):
    response = await client.post("/verify-carrier", json={"mc_number": ""}, headers=API_HEADERS)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_tool_failure_fallback(client, monkeypatch):
    async def mock_verify(self, mc_number: str):
        raise FMCSAServiceError("upstream timeout")

    monkeypatch.setattr("app.services.fmcsa_client.FMCSAClient.verify_carrier", mock_verify)

    response = await client.post("/verify-carrier", json={"mc_number": "123456"}, headers=API_HEADERS)
    assert response.status_code == 200
    payload = response.json()
    assert payload["eligible"] is False
    assert payload["verification_status"] == "verification_unavailable"
