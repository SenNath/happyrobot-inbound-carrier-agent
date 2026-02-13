# API Reference

All endpoints (except `/health`) require:
- Header: `X-API-Key: <INTERNAL_API_KEY>`

Base URL examples:
- Local: `http://localhost:8000`
- Production: `https://<backend-domain>`

## POST /verify-carrier
Verify DOT authority status through FMCSA.

### Request JSON
```json
{
  "mc_number": "123456"
}
```

### Response JSON
```json
{
  "eligible": true,
  "verification": "verified",
  "legal_name": "D & J TRANSPORTATION INC",
  "mc_number": "382168"
}
```

`verification` values:
- `verified`
- `not_authorized`
- `invalid_mc`
- `verification_unavailable`

## POST /search-loads
Search eligible loads by fuzzy matching equipment and origin, then sort by pickup proximity to `availability_time`.

### Request JSON
```json
{
  "equipment_type": "Dry Van",
  "origin_location": "Chicago, IL",
  "availability_time": "2026-02-12T13:00:00Z"
}
```

Matching behavior:
- `equipment_type`: case-insensitive partial match with normalization (e.g., `dryvan` -> `dry van`)
- `origin_location`: city/state substring token matching
- `availability_time`: used for ranking by closest pickup time (not strict equality filtering)

### Response JSON
```json
{
  "loads": [
    {
      "load_id": "HR-CHI-ATL-001",
      "origin": "Chicago, IL",
      "destination": "Atlanta, GA",
      "pickup_datetime": "2026-02-12T18:00:00Z",
      "delivery_datetime": "2026-02-13T08:00:00Z",
      "equipment_type": "Dry Van",
      "loadboard_rate": 2450.0,
      "notes": "Drop and hook at shipper, FCFS receiver.",
      "weight": 40120,
      "commodity_type": "Retail Goods",
      "miles": 716,
      "dimensions": "53ft trailer",
      "num_of_pieces": 24
    }
  ]
}
```

## POST /evaluate-offer
Evaluate carrier price proposal for a load.

### Request JSON
```json
{
  "load_id": "HR-CHI-ATL-001",
  "carrier_offer": 2550,
  "round_number": 2
}
```

### Response JSON
```json
{
  "decision": "counter",
  "counter_rate": 2490.0,
  "reasoning": "Countering toward indexed market rate."
}
```

Possible `decision` values:
- `accept`
- `counter`
- `reject`
- `needs_more_info`

## POST /log-call
Persist structured analytics payload from HappyRobot AI Extract node.

### Request JSON
```json
{
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
  "transfer_reason": "booking_confirmed"
}
```

Rules:
- `call_outcome` is required.
- all other fields are optional.
- missing fields are stored as `NULL`.
- string booleans/numbers are coerced to typed values.
- server-side `server_timestamp` is added automatically.

### Response JSON
```json
{
  "status": "logged",
  "call_id": 1
}
```

## Dashboard data endpoints
- `GET /dashboard/overview`
- `GET /dashboard/funnel`
- `GET /dashboard/negotiations`
- `GET /dashboard/sentiment`
- `GET /dashboard/sentiment-distribution`
- `GET /dashboard/load-performance`

## Health
- `GET /health`
