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
  "verification_status": "eligible"
}
```

## POST /search-loads
Search eligible loads by equipment, origin, and available time.

### Request JSON
```json
{
  "equipment_type": "Dry Van",
  "origin_location": "Chicago, IL",
  "availability_time": "2026-02-12T13:00:00Z"
}
```

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
  "call_sid": "CA_001",
  "mc_number": "123456",
  "load_id": "HR-CHI-ATL-001",
  "final_decision": "accept",
  "transcript": "...",
  "sentiment_score": 0.67,
  "call_duration_seconds": 344,
  "analytics_payload": {
    "intent": "book",
    "objections": ["rate"]
  }
}
```

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
- `GET /dashboard/load-performance`

## Health
- `GET /health`
