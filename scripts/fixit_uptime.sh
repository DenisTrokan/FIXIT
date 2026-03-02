#!/usr/bin/env bash
# =============================================================================
# fixit_uptime.sh — Returns the uptime (in seconds) of the FIXIT Gunicorn
#                   master process, or 0 if it is not running.
#
# Called by the Zabbix UserParameter:
#   UserParameter=fixit.process.uptime,/opt/fixit/scripts/fixit_uptime.sh
# =============================================================================
set -euo pipefail

# Find the oldest (master) gunicorn process for fixit
pid=$(pgrep -o -f "gunicorn.*wsgi:app" 2>/dev/null || true)

if [[ -z "$pid" ]]; then
    echo 0
    exit 0
fi

# /proc/<pid>/stat field 22 is the process start time in clock ticks since boot
start_ticks=$(awk '{print $22}' "/proc/$pid/stat" 2>/dev/null || echo "")
if [[ -z "$start_ticks" ]]; then
    echo 0
    exit 0
fi

clk_tck=$(getconf CLK_TCK 2>/dev/null || echo 100)
btime=$(awk '/^btime/{print $2; exit}' /proc/stat 2>/dev/null || echo 0)

start_epoch=$(( btime + start_ticks / clk_tck ))
now=$(date +%s)
uptime=$(( now - start_epoch ))

echo $(( uptime > 0 ? uptime : 0 ))
