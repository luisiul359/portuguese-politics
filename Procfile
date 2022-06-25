web: newrelic-admin run-program gunicorn src.app.main:app -w 1 -k uvicorn.workers.UvicornWorker --log-file -
clock: newrelic-admin run-program python src/daily_updater/main.py