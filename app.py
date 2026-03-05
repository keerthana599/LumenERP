import os
from app import create_app

# WSGI entrypoint for production (e.g. gunicorn: app is module-level)
app = create_app()

if __name__ == "__main__":
    # Fallback for environments that just run `python app.py`
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)

