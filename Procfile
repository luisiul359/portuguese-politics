web: gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker --log-file -
clock: python clock.py
worker: python worker.py