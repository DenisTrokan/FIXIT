#!/usr/bin/env bash
# =============================================================================
# check_and_start.sh — FIXIT watchdog script
#
# Checks whether the FIXIT Gunicorn process is running; if not, starts it.
# Designed to be called by cron (see ../crontab.example).
#
# Usage:
#   bash /opt/fixit/scripts/check_and_start.sh
# =============================================================================
set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration — adjust to match your deployment
# ---------------------------------------------------------------------------
APP_DIR="/opt/fixit"
VENV_BIN="$APP_DIR/venv/bin"
GUNICORN="$VENV_BIN/gunicorn"
GUNICORN_CONF="$APP_DIR/gunicorn.conf.py"
WSGI_MODULE="wsgi:app"
PID_FILE="/var/run/fixit/fixit.pid"
LOG_FILE="/var/log/fixit/watchdog.log"
HEALTH_URL="http://localhost:5000/health"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

is_running() {
    # Check PID file first, then fall back to process name
    if [[ -f "$PID_FILE" ]]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
    fi
    # Fallback: search for the gunicorn master process
    pgrep -f "gunicorn.*wsgi:app" > /dev/null 2>&1
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
mkdir -p "$(dirname "$LOG_FILE")"

if is_running; then
    # Process is up — optionally verify HTTP health endpoint
    if command -v curl > /dev/null 2>&1; then
        http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$HEALTH_URL" || true)
        if [[ "$http_code" == "200" ]]; then
            log "FIXIT is running and healthy (HTTP $http_code)."
        else
            log "WARNING: FIXIT process is alive but health check returned HTTP $http_code."
        fi
    else
        log "FIXIT is running (PID check passed; curl not available for HTTP check)."
    fi
else
    log "FIXIT is NOT running. Attempting to start..."
    cd "$APP_DIR"
    # shellcheck source=/dev/null
    source "$VENV_BIN/activate"
    "$GUNICORN" -c "$GUNICORN_CONF" "$WSGI_MODULE" \
        --daemon \
        >> /var/log/fixit/start.log 2>&1
    # Wait for the process to fully initialize before checking
    sleep "${STARTUP_WAIT_SECONDS:-3}"
    if is_running; then
        log "FIXIT started successfully."
    else
        log "ERROR: FIXIT failed to start. Check /var/log/fixit/ for details."
        exit 1
    fi
fi
