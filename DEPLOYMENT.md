# Deployment

## Purpose
This guide covers:
- How to access running deployments.
- How to reproduce deployments from scratch (local Docker and Railway).
- How to run a quick end-to-end validation after deployment.

## Prerequisites
- Docker + Docker Compose (for local full-stack deployment).
- Python 3.11 (for backend-only workflows).
- Railway CLI (`railway`) if deploying to Railway.

## Environment variables
Required for backend:
- `DATABASE_URL`
- `FMCSA_API_KEY`
- `INTERNAL_API_KEY`
- `CORS_ORIGINS` (lock to HappyRobot + your dashboard domains)
- `ALLOWED_HOSTS` (backend public hostname only in production)
- `RATE_LIMIT_PER_MINUTE`
- `SEED_ON_STARTUP`
- `FORCE_HTTPS_REDIRECT`

Required for frontend:
- `NEXT_PUBLIC_API_BASE_URL`
- `BACKEND_API_KEY`

## Docker deployment
```bash
docker compose up --build -d
```

Access local services:
- Backend API: `http://localhost:8000`
- Frontend dashboard: `http://localhost:3000`

## Railway deployment (recommended)

### 1. Create services
- PostgreSQL service
- Backend service (from repo root, Dockerfile path: `Dockerfile.backend`)
- Frontend service (from repo root, Dockerfile path: `Dockerfile.frontend`)

### 2. Backend Railway variables
- `DATABASE_URL` (from Railway Postgres)
- `FMCSA_API_KEY`
- `INTERNAL_API_KEY`
- `CORS_ORIGINS` (set exact HappyRobot + dashboard domains; comma-separated)
- `ALLOWED_HOSTS=<your-backend-railway-domain>`
- `FORCE_HTTPS_REDIRECT=true`
- `RATE_LIMIT_PER_MINUTE=120`
- `SEED_ON_STARTUP=true`

### 3. Frontend Railway variables
- `NEXT_PUBLIC_API_BASE_URL=https://<backend-public-domain>`
- `BACKEND_API_KEY=<same internal key as backend>`

### 4. Startup commands
- Backend container entrypoint already runs:
  - `alembic upgrade head`
  - `uvicorn app.main:app ...`
- Frontend runs `next start`

### 5. Ensure loads exist (required for HappyRobot E2E)
HappyRobot flows require at least one active load in `loads`. Use this idempotent append seed command to insert any missing seed `load_id`s even when data already exists.

- Local:
```bash
cd backend
python -m app.db.seed --mode append
```

- Railway backend service:
```bash
railway run -s backend -- bash -lc "cd backend && ./.venv/bin/python -m app.db.seed --mode append"
```

You can re-run this safely; existing seed IDs are skipped.

## Health checks
- Backend health: `GET /health`
- Verify API auth by calling `/health` (no auth) and `/dashboard/overview` (requires `X-API-Key`)

## HTTPS
- **Railway**: HTTPS is terminated at Railway edge with managed certificates (Let’s Encrypt-equivalent).
- **Backend app**: set `FORCE_HTTPS_REDIRECT=true` so HTTP requests are redirected to HTTPS.
- **Local**: use either:
  - `./scripts/generate-local-cert.sh` + `./scripts/run-backend-https.sh`
  - `docker compose -f docker-compose.https.yml up --build` (Caddy local certs)

## Accessing deployment
1. Open Railway project dashboard.
2. Select backend service and copy public domain.
3. Verify:
   - `GET https://<backend-domain>/health`
   - `POST https://<backend-domain>/verify-carrier` with `X-API-Key`.
4. For dashboard access, open the frontend public domain and verify pages load:
   - Overview
   - Funnel
   - Sentiment
   - Load performance

## Reproducible redeploy
### Manual
1. Link services in Railway.
2. Set env vars exactly as above.
3. Deploy from repo using each Dockerfile.

### Shell scripts
- First-time helper: `./scripts/railway-deploy.sh`
- Repeat deploy helper: `./infra/railway/redeploy.sh`

### CLI deployment commands (explicit)
If not using helper scripts:
```bash
railway up -s backend --path-as-root backend --detach
railway up -s frontend --path-as-root frontend --detach
```

## End-to-end smoke test checklist
Run this after deploy (local or Railway) so any reviewer can validate the full workflow quickly:

1. Append seed loads (`python -m app.db.seed --mode append`).
2. `GET /health` returns `{"status":"ok"}`.
3. `POST /verify-carrier` with a known MC number returns `eligible` + `verification`.
4. `POST /search-loads` for `Dry Van` + valid origin returns at least one load.
5. `POST /evaluate-offer` returns deterministic `accept|counter|reject|needs_more_info`.
6. `POST /log-call` with extract payload returns `{"status":"logged","call_id":...}`.
7. `GET /dashboard/overview` returns KPI payload including booking rate and negotiation metrics.

## Current live deployment (this project)
- GitHub repo: `https://github.com/SenNath/happyrobot-inbound-carrier-agent`
- Railway backend: `https://happyagent-backend.up.railway.app`
- Railway frontend: `https://happyagent-console.up.railway.app`

## GitHub-linked Railway note
- If `railway add --repo ...` returns `repo not found`, install/authorize the Railway GitHub app for that repository in GitHub settings.
- Until that is enabled, deploy via CLI using:
  - `railway up -s backend --path-as-root backend`
  - `railway up -s frontend --path-as-root frontend`

## Production hardening checklist
- Rotate `INTERNAL_API_KEY`
- Restrict `CORS_ORIGINS` to known domains only
- Configure Railway private networking between services
- Add observability (logs/metrics/alerts)
