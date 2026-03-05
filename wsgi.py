import os
from app import create_app

# WSGI entrypoint for production (e.g. gunicorn: wsgi:app)
app = create_app()

if __name__ == "__main__":
    # Fallback for environments that just run `python wsgi.py`
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)
