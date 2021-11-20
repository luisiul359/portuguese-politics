web: gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker --log-file -
worker: python worker.py
clock: python clock.py