#!/usr/bin/env bash
set -euo pipefail

# Double-clickable toggle for Streamlit app (port 8502)
# Starts/stops the AI-MA web UI and opens the browser on start.

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PORT="8502"
URL="http://127.0.0.1:${PORT}/"
VENV_ACTIVATE="${APP_DIR}/venv/bin/activate"
RUN_DIR="${APP_DIR}/.run"
PID_FILE="${RUN_DIR}/streamlit_${PORT}.pid"
LOG_FILE="${RUN_DIR}/streamlit_${PORT}.log"

mkdir -p "${RUN_DIR}"

is_listening() {
  lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1
}

stop_server() {
  echo "[AI-MA] Stopping server on port ${PORT}..."

  # Prefer pidfile if present
  if [[ -f "${PID_FILE}" ]]; then
    pid="$(cat "${PID_FILE}" || true)"
    if [[ -n "${pid}" ]] && kill -0 "${pid}" >/dev/null 2>&1; then
      kill "${pid}" || true
      # Give it a moment
      sleep 0.6
      if kill -0 "${pid}" >/dev/null 2>&1; then
        kill -9 "${pid}" || true
      fi
    fi
    rm -f "${PID_FILE}" || true
  fi

  # Fallback: stop by command match
  pkill -f "streamlit run app.py.*--server\.port=${PORT}" >/dev/null 2>&1 || true

  echo "[AI-MA] Stopped."
}

start_server() {
  echo "[AI-MA] Starting server on port ${PORT}..."

  if [[ ! -f "${VENV_ACTIVATE}" ]]; then
    echo "[AI-MA] ERROR: venv not found at ${VENV_ACTIVATE}"
    echo "Press Enter to close..."
    read -r
    exit 1
  fi

  # Avoid port conflict
  if is_listening; then
    echo "[AI-MA] Port ${PORT} already in use. Attempting to stop existing service first..."
    stop_server
  fi

  (
    cd "${APP_DIR}"
    # shellcheck disable=SC1090
    source "${VENV_ACTIVATE}"
    nohup streamlit run app.py --server.headless=true --server.port="${PORT}" >"${LOG_FILE}" 2>&1 &
    echo $! > "${PID_FILE}"
  )

  # Give it a moment to bind
  sleep 1.0

  if is_listening; then
    echo "[AI-MA] Started. Opening ${URL}"
    open "${URL}" >/dev/null 2>&1 || true
  else
    echo "[AI-MA] WARNING: Server did not bind to port ${PORT} yet."
    echo "[AI-MA] Check logs: ${LOG_FILE}"
  fi
}

echo "[AI-MA] Toggle Streamlit UI"
echo "[AI-MA] App dir: ${APP_DIR}"

if is_listening; then
  stop_server
else
  start_server
fi

echo
echo "Done. (Logs: ${LOG_FILE})"
echo "Press Enter to close..."
read -r

