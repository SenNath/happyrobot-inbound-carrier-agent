#!/usr/bin/env bash
set -euo pipefail

CERT_DIR="${1:-./certs}"
HOST="${2:-0.0.0.0}"
PORT="${3:-8443}"

if [[ ! -f "$CERT_DIR/dev.crt" || ! -f "$CERT_DIR/dev.key" ]]; then
  echo "Missing certs in $CERT_DIR. Run ./scripts/generate-local-cert.sh first."
  exit 1
fi

cd backend
source .venv/bin/activate
uvicorn app.main:app \
  --host "$HOST" \
  --port "$PORT" \
  --ssl-certfile "../$CERT_DIR/dev.crt" \
  --ssl-keyfile "../$CERT_DIR/dev.key"
