#!/usr/bin/env bash
# =============================================================================
# snmp_trap.sh — Send SNMP trap notifications to Zabbix SNMP Trap Receiver
#
# This script sends SNMP v2c traps to a Zabbix server configured to receive
# SNMP traps (snmptrapd + Zabbix SNMP trap receiver).
#
# Usage:
#   bash /opt/fixit/scripts/snmp_trap.sh <event> [message]
#
# Events:
#   heartbeat   — periodic alive signal (call from cron every minute)
#   start       — application started
#   stop        — application stopped / about to stop
#   error       — generic error notification
#
# Prerequisites:
#   apt install snmp          # provides snmptrap
#
# Configuration:
#   Set variables below or export them as environment variables.
# =============================================================================
set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ZABBIX_HOST="${ZABBIX_HOST:-zabbix.example.com}"   # Zabbix server/proxy IP or hostname
SNMP_COMMUNITY="${SNMP_COMMUNITY:-public}"          # SNMP community string
SNMP_PORT="${SNMP_PORT:-162}"                        # SNMP trap port (default 162)
APP_NAME="FIXIT"
# Enterprise OID used for all FIXIT traps.
# We re-use the NET-SNMP demonstration/test OID subtree
# (.1.3.6.1.4.1.8072.2) since FIXIT does not have a registered PEN.
# Replace with your own Private Enterprise Number (PEN) if available:
#   https://www.iana.org/assignments/enterprise-numbers/
#
# OID hierarchy (under .1.3.6.1.4.1.8072.2.3):
#   .0.1    — enterprise trap OID (coldStart-equivalent, required by SNMPv2c)
#   .2.1    — fixit.heartbeat
#   .2.2    — fixit.start
#   .2.3    — fixit.stop
#   .2.4    — fixit.error
#   .2.10   — fixit.severity  (Integer: 1=info, 2=warning, 3=average, 4=high)
ENTERPRISE_OID=".1.3.6.1.4.1.8072.2.3.0.1"
EVENT="${1:-heartbeat}"
MESSAGE="${2:-}"

# ---------------------------------------------------------------------------
# Validate dependencies
# ---------------------------------------------------------------------------
if ! command -v snmptrap > /dev/null 2>&1; then
    echo "ERROR: 'snmptrap' not found. Install net-snmp-utils: apt install snmp" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Build OID and varbind based on event type
# ---------------------------------------------------------------------------
case "$EVENT" in
    heartbeat)
        SPECIFIC_OID=".1.3.6.1.4.1.8072.2.3.2.1"  # fixit.heartbeat
        SEVERITY=1
        [[ -z "$MESSAGE" ]] && MESSAGE="$APP_NAME heartbeat — $(date '+%Y-%m-%d %H:%M:%S')"
        ;;
    start)
        SPECIFIC_OID=".1.3.6.1.4.1.8072.2.3.2.2"  # fixit.start
        SEVERITY=1
        [[ -z "$MESSAGE" ]] && MESSAGE="$APP_NAME started — $(date '+%Y-%m-%d %H:%M:%S')"
        ;;
    stop)
        SPECIFIC_OID=".1.3.6.1.4.1.8072.2.3.2.3"  # fixit.stop
        SEVERITY=3
        [[ -z "$MESSAGE" ]] && MESSAGE="$APP_NAME stopped — $(date '+%Y-%m-%d %H:%M:%S')"
        ;;
    error)
        SPECIFIC_OID=".1.3.6.1.4.1.8072.2.3.2.4"  # fixit.error
        SEVERITY=4
        [[ -z "$MESSAGE" ]] && MESSAGE="$APP_NAME error — $(date '+%Y-%m-%d %H:%M:%S')"
        ;;
    *)
        echo "ERROR: unknown event '$EVENT'. Use: heartbeat | start | stop | error" >&2
        exit 1
        ;;
esac

# ---------------------------------------------------------------------------
# Send the SNMP trap
# ---------------------------------------------------------------------------
snmptrap -v 2c \
    -c "$SNMP_COMMUNITY" \
    "${ZABBIX_HOST}:${SNMP_PORT}" \
    "" \
    "$ENTERPRISE_OID" \
    "$SPECIFIC_OID" s "$MESSAGE" \
    ".1.3.6.1.4.1.8072.2.3.2.10" i "$SEVERITY"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] SNMP trap sent: event=$EVENT severity=$SEVERITY message='$MESSAGE'"
