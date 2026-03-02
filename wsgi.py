"""
WSGI entry point for production deployment with Gunicorn.

Usage:
    gunicorn -c gunicorn.conf.py wsgi:app
"""
from app import app, init_db

# Initialize the database (idempotent - safe to call on every startup)
init_db()
