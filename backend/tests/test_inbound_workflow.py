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
        return FMCSAResult(eligible=True, verification="verified", legal_name="Carrier One", mc_number=mc_number)

    monkeypatch.setattr("app.services.fmcsa_client.FMCSAClient.verify_carrier", mock_verify)

    verify_resp = await client.post("/verify-carrier", json={"mc_number": "123456"}, headers=API_HEADERS)
    assert verify_resp.status_code == 200
    verify_payload = verify_resp.json()
    assert verify_payload["eligible"] is True
    assert verify_payload["verification"] == "verified"
    assert verify_payload["legal_name"] == "Carrier One"
    assert verify_payload["mc_number"] == "123456"

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
            "call_outcome": "booked",
            "sentiment": "positive",
            "mc_number": "123456",
            "carrier_verified": "true",
            "loads_returned_count": "3",
            "loads_presented_count": "1",
            "load_id_discussed": load.load_id,
            "initial_rate": "2100",
            "carrier_counter_rate": "2280",
            "final_rate": "2220",
            "negotiation_rounds": "2",
            "deal_margin_pressure": "medium",
            "equipment_type": "dry van",
            "origin_location": "Chicago IL",
            "driver_contact_collected": "true",
            "was_transferred": "false",
        },
        headers=API_HEADERS,
    )
    assert log_resp.status_code == 200
    assert log_resp.json()["status"] == "logged"


@pytest.mark.asyncio
async def test_ineligible_carrier(client, monkeypatch):
    async def mock_verify(self, mc_number: str):
        return FMCSAResult(
            eligible=False,
            verification="not_authorized",
            legal_name="Carrier Two",
            mc_number=mc_number,
        )

    monkeypatch.setattr("app.services.fmcsa_client.FMCSAClient.verify_carrier", mock_verify)

    response = await client.post("/verify-carrier", json={"mc_number": "999999"}, headers=API_HEADERS)
    assert response.status_code == 200
    assert response.json() == {
        "eligible": False,
        "verification": "not_authorized",
        "legal_name": "Carrier Two",
        "mc_number": "999999",
    }


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
async def test_search_loads_fuzzy_matching_and_time_order(client, db_session):
    near_pickup = datetime.now(timezone.utc) + timedelta(hours=2)
    far_pickup = datetime.now(timezone.utc) + timedelta(hours=16)

    near_load = Load(
        load_id="FZ-CHI-001",
        origin="Chicago, IL",
        destination="Nashville, TN",
        pickup_datetime=near_pickup,
        delivery_datetime=near_pickup + timedelta(hours=8),
        equipment_type="Dry Van",
        loadboard_rate=Decimal("1800.00"),
        notes="Near pickup test load",
        weight=30000,
        commodity_type="General Freight",
        miles=470,
        dimensions="53ft trailer",
        num_of_pieces=12,
        is_active=True,
    )
    far_load = Load(
        load_id="FZ-CHI-002",
        origin="Chicago, Illinois",
        destination="Memphis, TN",
        pickup_datetime=far_pickup,
        delivery_datetime=far_pickup + timedelta(hours=10),
        equipment_type="DryVan",
        loadboard_rate=Decimal("1900.00"),
        notes="Far pickup test load",
        weight=32000,
        commodity_type="General Freight",
        miles=530,
        dimensions="53ft trailer",
        num_of_pieces=14,
        is_active=True,
    )
    db_session.add_all([near_load, far_load])
    await db_session.commit()

    response = await client.post(
        "/search-loads",
        json={
            "equipment_type": "dryvan",
            "origin_location": "chicago il",
            "availability_time": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        },
        headers=API_HEADERS,
    )

    assert response.status_code == 200
    loads = response.json()["loads"]
    assert len(loads) >= 2
    assert loads[0]["load_id"] == "FZ-CHI-001"
    assert loads[1]["load_id"] == "FZ-CHI-002"


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
async def test_counter_offer_does_not_regress_across_rounds(client, db_session):
    load = await insert_load(db_session, load_id="NEG-MONO-001", rate=Decimal("2000.00"))

    round_one = await client.post(
        "/evaluate-offer",
        json={"load_id": load.load_id, "carrier_offer": 2280, "round_number": 1},
        headers=API_HEADERS,
    )
    assert round_one.status_code == 200
    round_one_payload = round_one.json()
    assert round_one_payload["decision"] == "counter"
    assert round_one_payload["counter_rate"] == 2120.0

    round_two = await client.post(
        "/evaluate-offer",
        json={"load_id": load.load_id, "carrier_offer": 2180, "round_number": 2},
        headers=API_HEADERS,
    )
    assert round_two.status_code == 200
    round_two_payload = round_two.json()
    assert round_two_payload["decision"] == "counter"
    assert round_two_payload["counter_rate"] == 2120.0


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
    assert payload["verification"] == "verification_unavailable"
    assert payload["mc_number"] == "123456"


@pytest.mark.asyncio
async def test_log_call_type_coercion_and_null_defaults(client):
    response = await client.post(
        "/log-call",
        json={
            "call_outcome": "booked",
            "sentiment": "positive",
            "mc_number": "123456",
            "carrier_verified": "true",
            "verification_failure_reason": "null",
            "loads_returned_count": "3",
            "loads_presented_count": "1",
            "carrier_interest_level": "high",
            "load_id_discussed": "LD1001",
            "initial_rate": "1900",
            "carrier_counter_rate": "2200",
            "final_rate": "2050",
            "negotiation_rounds": "3",
            "deal_margin_pressure": "high",
            "equipment_type": "dry van",
            "origin_location": "Dallas TX",
            "availability_time": "2026-02-13T16:09:01",
            "driver_contact_collected": "true",
            "was_transferred": "true",
            "transfer_reason": "booking_confirmed",
        },
        headers=API_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "logged"


@pytest.mark.asyncio
async def test_log_call_rejects_unknown_fields(client):
    response = await client.post(
        "/log-call",
        json={"call_outcome": "booked", "unexpected_key": "value"},
        headers=API_HEADERS,
    )
    assert response.status_code == 422
