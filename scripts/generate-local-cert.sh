#!/usr/bin/env bash
set -euo pipefail

CERT_DIR="${1:-./certs}"
mkdir -p "$CERT_DIR"

openssl req \
  -x509 \
  -newkey rsa:4096 \
  -sha256 \
  -days 365 \
  -nodes \
  -keyout "$CERT_DIR/dev.key" \
  -out "$CERT_DIR/dev.crt" \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

echo "Generated: $CERT_DIR/dev.crt and $CERT_DIR/dev.key"
