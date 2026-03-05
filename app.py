from app import create_app

# WSGI entrypoint for production (e.g. gunicorn: app is module-level)
app = create_app()

if __name__ == "__main__":
    # Fallback for environments that just run `python app.py`
    app.run(host="0.0.0.0", port=8000)

