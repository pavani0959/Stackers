#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  echo "Missing .env file. Creating from .env.example..."
  cp .env.example .env
fi

if [[ ! -d node_modules ]]; then
  echo "Installing frontend dependencies..."
  npm install
fi

if [[ ! -d backend/venv ]]; then
  echo "Missing backend/venv. Creating virtual environment..."
  python3 -m venv backend/venv
  source backend/venv/bin/activate
  echo "Installing backend dependencies..."
  pip install -r backend/requirements.txt
fi

cleanup() {
  [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true
  [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Preparing database..."
(
  cd backend
  source venv/bin/activate
  # The bootstrap script ensures DB is prepared
  python scripts/bootstrap_legacy_sqlite.py
  alembic upgrade head
  # The seed script is idempotent (safe to run multiple times)
  python seed.py
)

echo "Starting FastAPI on port 8000..."
(
  cd backend
  source venv/bin/activate
  uvicorn main:app --reload --port 8000
) &
BACKEND_PID=$!

echo "Starting Vite on port 5173..."
npm run dev &
FRONTEND_PID=$!

echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"

wait
