"""
Gunicorn configuration for FIXIT production deployment.

Start with:
    gunicorn -c gunicorn.conf.py wsgi:app
"""
import multiprocessing
import os

# ---------------------------------------------------------------------------
# Server socket
# ---------------------------------------------------------------------------
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:5000")

# ---------------------------------------------------------------------------
# Worker processes
# ---------------------------------------------------------------------------
# (2 * CPU cores) + 1  is the standard recommendation for sync workers
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
threads = 1
timeout = 120
keepalive = 5

# Recycle workers periodically to avoid memory leaks
max_requests = 1000
max_requests_jitter = 100

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
_log_dir = "/var/log/fixit"
try:
    os.makedirs(_log_dir, exist_ok=True)
except PermissionError:
    _log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(_log_dir, exist_ok=True)

accesslog = os.path.join(_log_dir, "access.log")
errorlog = os.path.join(_log_dir, "error.log")
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sus'

# ---------------------------------------------------------------------------
# Process naming & PID
# ---------------------------------------------------------------------------
proc_name = "fixit"
pidfile = "/var/run/fixit/fixit.pid"

# Ensure the PID directory exists
try:
    os.makedirs(os.path.dirname(pidfile), exist_ok=True)
except PermissionError:
    pidfile = os.path.join(os.path.dirname(__file__), "fixit.pid")

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
limit_request_line = 8190
limit_request_fields = 100
forwarded_allow_ips = os.getenv("FORWARDED_ALLOW_IPS", "127.0.0.1")
