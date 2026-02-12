# Deployment

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

## Reproducible redeploy
### Manual
1. Link services in Railway.
2. Set env vars exactly as above.
3. Deploy from repo using each Dockerfile.

### Shell scripts
- First-time helper: `./scripts/railway-deploy.sh`
- Repeat deploy helper: `./infra/railway/redeploy.sh`

## Production hardening checklist
- Rotate `INTERNAL_API_KEY`
- Restrict `CORS_ORIGINS` to known domains only
- Configure Railway private networking between services
- Add observability (logs/metrics/alerts)
