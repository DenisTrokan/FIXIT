#!/usr/bin/env bash
set -euo pipefail

# Safe deploy for FIXIT on Linux/Lightsail
# - creates a timestamped SQLite backup
# - performs git pull with fast-forward only
# - optionally restarts service
# - prints quick pre/post DB checks

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
DB_PATH="${DB_PATH:-instance/tickets.db}"
BACKUP_DIR="${BACKUP_DIR:-instance/backups}"
BRANCH="${BRANCH:-main}"
RESTART_CMD="${RESTART_CMD:-}"
KEEP_BACKUPS="${KEEP_BACKUPS:-20}"

timestamp() { date +"%Y%m%d-%H%M%S"; }
log() { echo "[$(date +"%F %T")] $*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Comando richiesto non trovato: $1"
}

db_count() {
  local db_file="$1"
  if command -v sqlite3 >/dev/null 2>&1; then
    sqlite3 "$db_file" "SELECT COUNT(*) FROM tickets;" 2>/dev/null || echo "N/A"
  else
    echo "sqlite3-non-installato"
  fi
}

cleanup_old_backups() {
  local keep="$1"
  mapfile -t files < <(ls -1t "$BACKUP_DIR"/tickets.db.*.bak 2>/dev/null || true)
  if (( ${#files[@]} > keep )); then
    for old in "${files[@]:keep}"; do
      rm -f "$old"
    done
  fi
}

require_cmd git
require_cmd cp
require_cmd ls

cd "$APP_DIR"

log "Safe deploy avviato in: $APP_DIR"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || fail "La cartella non è un repository git"

if [[ -n "$(git status --porcelain)" ]]; then
  fail "Working tree non pulita. Esegui commit/stash prima del deploy."
fi

[[ -f "$DB_PATH" ]] || fail "Database non trovato: $DB_PATH"

pre_size="$(ls -lh "$DB_PATH" | awk '{print $5}')"
pre_count="$(db_count "$DB_PATH")"
log "Pre-check DB -> file: $DB_PATH | size: $pre_size | tickets: $pre_count"

mkdir -p "$BACKUP_DIR"
backup_file="$BACKUP_DIR/tickets.db.$(timestamp).bak"
cp "$DB_PATH" "$backup_file"
log "Backup creato: $backup_file"

if command -v sha256sum >/dev/null 2>&1; then
  sha256sum "$backup_file" > "$backup_file.sha256"
  log "Checksum creato: $backup_file.sha256"
fi

cleanup_old_backups "$KEEP_BACKUPS"

log "Eseguo pull fast-forward only sul branch: $BRANCH"
git fetch origin "$BRANCH"
git pull --ff-only origin "$BRANCH"

if [[ -n "$RESTART_CMD" ]]; then
  log "Riavvio servizio: $RESTART_CMD"
  bash -lc "$RESTART_CMD"
fi

post_size="$(ls -lh "$DB_PATH" | awk '{print $5}')"
post_count="$(db_count "$DB_PATH")"
log "Post-check DB -> file: $DB_PATH | size: $post_size | tickets: $post_count"

log "Deploy completato con successo."
