#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_HOST="${FRONTEND_HOST:-127.0.0.1}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  echo
  echo "Stopping PaperReader..."

  if [[ -n "${FRONTEND_PID}" ]] && kill -0 "${FRONTEND_PID}" 2>/dev/null; then
    kill "${FRONTEND_PID}" 2>/dev/null || true
  fi

  if [[ -n "${BACKEND_PID}" ]] && kill -0 "${BACKEND_PID}" 2>/dev/null; then
    kill "${BACKEND_PID}" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

ensure_port_free() {
  local host="$1"
  local port="$2"
  local label="$3"

  if command -v ss >/dev/null 2>&1 && ss -ltn "( sport = :${port} )" | grep -q ":${port}"; then
    echo "${label} port ${host}:${port} is already in use." >&2
    echo "Stop the existing service or override the port, for example:" >&2
    echo "  ${label^^}_PORT=$((port + 1)) scripts/start.sh" >&2
    exit 1
  fi
}

if [[ ! -x "${ROOT_DIR}/.venv/bin/python" ]]; then
  echo "Backend virtualenv not found: ${ROOT_DIR}/.venv/bin/python" >&2
  exit 1
fi

if [[ ! -d "${ROOT_DIR}/frontend/node_modules" ]]; then
  echo "frontend/node_modules not found. Installing frontend dependencies..."
  (cd "${ROOT_DIR}/frontend" && npm install)
fi

ensure_port_free "${BACKEND_HOST}" "${BACKEND_PORT}" "backend"
ensure_port_free "${FRONTEND_HOST}" "${FRONTEND_PORT}" "frontend"

echo "Starting PaperReader backend..."
(
  cd "${ROOT_DIR}"
  .venv/bin/python -m uvicorn app.main:app --host "${BACKEND_HOST}" --port "${BACKEND_PORT}" --reload
) &
BACKEND_PID=$!

echo "Starting PaperReader frontend..."
(
  cd "${ROOT_DIR}/frontend"
  npm run dev -- --host "${FRONTEND_HOST}" --port "${FRONTEND_PORT}"
) &
FRONTEND_PID=$!

cat <<EOF

PaperReader is starting:
  Backend:  http://${BACKEND_HOST}:${BACKEND_PORT}
  API Docs: http://${BACKEND_HOST}:${BACKEND_PORT}/docs
  Frontend: http://${FRONTEND_HOST}:${FRONTEND_PORT}

Press Ctrl+C to stop both services.
EOF

wait -n "${BACKEND_PID}" "${FRONTEND_PID}"
