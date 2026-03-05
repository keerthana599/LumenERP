from app import create_app

# Expose a WSGI application named `app` so commands like
# `gunicorn main:app` work out of the box.
app = create_app()

