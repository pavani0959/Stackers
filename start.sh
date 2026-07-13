#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  echo "Missing .env. Run: cp .env.example .env"
  exit 1
fi

if [[ ! -d backend/venv ]]; then
  echo "Missing backend/venv. Create it and install backend/requirements.txt first."
  exit 1
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
  alembic upgrade head
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
