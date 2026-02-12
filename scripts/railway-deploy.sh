#!/usr/bin/env bash
set -euo pipefail

if ! command -v railway >/dev/null 2>&1; then
  echo "Railway CLI is required: https://docs.railway.com/develop/cli"
  exit 1
fi

if [[ ! -f .env ]]; then
  echo "Missing .env file in repo root."
  exit 1
fi

# 1) Login and link
railway login
railway link

# 2) Ensure variables are loaded for current service context
set -a
source .env
set +a

# 3) Deploy current service
railway up --detach

echo "Deployment triggered. Configure service variables in Railway UI for backend and frontend as documented in DEPLOYMENT.md"
