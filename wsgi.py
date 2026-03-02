"""
WSGI entry point for production deployment.

Usage with Gunicorn:
    gunicorn wsgi:app -b 0.0.0.0:8000 -w 1

See DEPLOY.md for full deployment guide.
"""

from app import app, init_db

# Initialize database tables and default admin user on startup
init_db()

if __name__ == '__main__':
    app.run()
