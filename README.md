# HappyRobot Inbound Carrier Sales Agent

Production-grade full-stack project for HappyRobot voice workflow tool webhooks and operations analytics.

## What this project includes
- FastAPI backend with webhook endpoints:
  - `POST /verify-carrier`
  - `POST /search-loads`
  - `POST /evaluate-offer`
  - `POST /log-call`
- FMCSA carrier verification via `FMCSA_API_KEY`
- PostgreSQL persistence with SQLAlchemy 2 + Alembic
- Seeded realistic freight loads
- Next.js 15 analytics dashboard (Overview, Funnel, Negotiation, Sentiment, Load Performance)
- API-key middleware, strict CORS, rate limiting, env-only secrets
- Pytest scenario suite with 7 inbound call flows
- Dockerized backend + frontend + Postgres
- Railway deployment-ready configuration/docs

## Documentation map
- Start here for platform and API overview.
- Deployment access + reproducibility instructions are in `DEPLOYMENT.md`.
- Endpoint-level contracts are in `API_REFERENCE.md`.
- System design details are in `ARCHITECTURE.md`.

## Live access
- Backend API (Railway): `https://happyagent-backend.up.railway.app`
- Frontend dashboard (Railway): `https://happyagent-console.up.railway.app`
- HappyRobot inbound carrier sales Agent:
  - `https://platform.happyrobot.ai/fdesenthilnathan/workflow/nml021tw7tyj/editor/vfyfokyvyldl`
  - requires HappyRobot platform/workspace access

## Project structure
```text
backend/
  app/
    api/
    core/
    db/
    middleware/
    models/
    repositories/
    schemas/
    services/
  alembic/
  tests/
frontend/
  app/
  components/
  lib/
Dockerfile.backend
Dockerfile.frontend
docker-compose.yml
```

## Local development
1. Copy env file:
```bash
cp .env.example .env
```
2. Start full stack:
```bash
docker compose up --build
```
3. Open:
- API: `http://localhost:8000`
- Dashboard: `http://localhost:3000`

## API keys
- `INTERNAL_API_KEY` secures backend endpoints.
- `BACKEND_API_KEY` is the key the dashboard uses to call backend APIs.
- In this project they should be the same value.

## Backend-only (without Docker)
```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .[test]
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

## Local HTTPS
Option A (no Docker, self-signed cert):
```bash
./scripts/generate-local-cert.sh
./scripts/run-backend-https.sh
```
Then call `https://localhost:8443`.

Option B (Docker with local TLS proxy):
```bash
docker compose -f docker-compose.https.yml up --build
```
Then call `https://localhost` (Caddy local cert).

## Running tests
```bash
cd backend
pytest -q
```

## HappyRobot workflow integration
- This system is wired for the HappyRobot inbound carrier sales workflow (`verify_carrier` -> `search_loads` -> `evaluate_offer` -> `log_call`).
- Production workflow URL: `https://platform.happyrobot.ai/fdesenthilnathan/workflow/nml021tw7tyj/editor/vfyfokyvyldl`
- The workflow URL requires access to the owning HappyRobot workspace.

## HappyRobot API integration notes
- Configure HappyRobot tools to hit your backend base URL.
- Send `X-API-Key` header matching `INTERNAL_API_KEY`.
- Required request keys are implemented exactly as specified:
  - `mc_number`
  - `equipment_type`
  - `origin_location`
  - `availability_time`
  - `load_id`
  - `carrier_offer`
  - `round_number`
- `POST /log-call` accepts AI Extract analytics payload with `call_outcome` required and all other fields optional; missing fields are stored as `NULL`.

For deployment access and full reproducible deployment steps, see `DEPLOYMENT.md`.
