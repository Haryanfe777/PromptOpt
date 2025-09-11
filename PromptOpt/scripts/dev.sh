#!/usr/bin/env bash
set -euo pipefail

OPENAI_KEY="${OPENAI_API_KEY:-${1:-}}"

pushd "$(dirname "$0")/.." >/dev/null

echo "== Backend setup =="
cd backend
python3 -m venv .venv || true
source .venv/bin/activate
pip install -r requirements.txt
if [ ! -f app.db ]; then
  alembic upgrade head
  python -m app.utils.seed
fi

( OPENAI_API_KEY="$OPENAI_KEY" uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 ) &
BACK_PID=$!

echo "== Frontend setup =="
cd ../frontend
npm install
( npm start ) &
FRONT_PID=$!

echo "Launched backend (PID $BACK_PID) and frontend (PID $FRONT_PID)."
wait
