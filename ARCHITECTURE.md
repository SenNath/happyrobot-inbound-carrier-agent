# Architecture

## System boundary
HappyRobot hosts the voice workflow and calls backend tools. This project provides:
- Tool execution APIs
- Carrier and negotiation logic
- Analytics storage + aggregation
- Operator dashboard

## Backend design
- **Framework:** FastAPI (async)
- **Data layer:** SQLAlchemy 2 async ORM + repository pattern
- **Schema layer:** Pydantic request/response models
- **Service layer:**
  - `CarrierService` + `FMCSAClient`
  - `LoadService`
  - `NegotiationService`
  - `AnalyticsService`
- **Security:** API key middleware, CORS allowlist, rate limiting (SlowAPI)

### Data model
- `loads`: freight offers and baseline economics
- `calls`: structured analytics logs per call
- `negotiations`: round-level offer outcomes

## API flow
1. `POST /verify-carrier`
- Validates API key
- Calls FMCSA docket-number endpoint (`/carriers/docket-number/{mc}`)
- Returns `eligible` plus `verification` (`verified`, `not_authorized`, `invalid_mc`, `verification_unavailable`)
- Includes carrier metadata (`legal_name`, `mc_number`)

2. `POST /search-loads`
- Uses fuzzy equipment + origin matching and ranks by pickup-time proximity to availability
- Returns `loads[]` with exact required fields

3. `POST /evaluate-offer`
- Evaluates offer against loadboard rate and negotiation round
- Returns one of `accept | counter | reject | needs_more_info`
- Persists negotiation rows for analytics

4. `POST /log-call`
- Stores HappyRobot AI Extract analytics fields as typed columns with 1:1 key mapping
- `call_outcome` required; all other extract fields optional and nullable
- server timestamp is generated on insert

## Dashboard design
- **Framework:** Next.js 15 App Router + TypeScript
- **UI:** Tailwind + shadcn-style components
- **Charts:** Recharts
- **Pages:**
  - Overview KPIs
  - Conversion Funnel
  - Negotiation Insights
  - Sentiment Analytics
  - Load Performance

## Reliability and operations
- Stateless API containers
- PostgreSQL as source of truth
- Idempotent load seeding paths:
  - startup seed (only when `loads` is empty)
  - append seed command (`python -m app.db.seed --mode append`) for reproducible E2E test data
- Docker and Railway deployment paths
