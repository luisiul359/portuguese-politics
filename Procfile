web: gunicorn src.app.main:app -w 1 -k uvicorn.workers.UvicornWorker --log-file -
clock: python src/daily_updater/main.py