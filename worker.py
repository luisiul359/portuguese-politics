import os

import redis
from rq import Worker, Queue, Connection


redis_url = os.getenv("REDIS_URL")


if __name__ == '__main__':
    # connect to Redis
    conn = redis.from_url(redis_url)

    listen = ['high', 'default', 'low']

    # create the worker and process the request
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()