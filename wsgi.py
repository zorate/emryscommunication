# wsgi.py — Production entry point for Gunicorn / Render / any WSGI server
# Usage: gunicorn wsgi:app
from app import create_app

app = create_app()
