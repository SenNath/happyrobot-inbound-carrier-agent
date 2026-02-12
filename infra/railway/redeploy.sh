#!/usr/bin/env bash
set -euo pipefail

# Reproducible redeploy helper for already-linked project/services.
# Run once per service context (backend and frontend).
railway up --detach
railway status
