#!/usr/bin/env bash
set -euo pipefail

BASE="${1:-http://127.0.0.1:8000}"
USER="${2:-admin}"
PASS="${3:-admin}"

echo "== Health =="
curl -sf "$BASE/health"

echo "\n== Login =="
TOKEN=$(curl -sf -X POST "$BASE/login" -H 'Content-Type: application/x-www-form-urlencoded' -d "username=$USER&password=$PASS" | sed -E 's/.*"access_token"\s*:\s*"([^"]+)".*/\1/')
[ -n "$TOKEN" ] || { echo "No token"; exit 1; }

echo "== Me =="
curl -sf -H "Authorization: Bearer $TOKEN" "$BASE/me"

echo "\n== Prompts =="
curl -sf "$BASE/prompts"

echo "\n== Chat =="
curl -sf -X POST "$BASE/chat" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"message":"What are our PTO policies?","evaluate":true}'

echo "\nSmoke tests completed."
