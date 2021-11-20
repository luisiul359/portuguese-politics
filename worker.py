import os

import redis
from rq import Worker, Queue


redis_url = os.getenv("REDIS_URL")


if __name__ == '__main__':
    # connect to Redis
    conn = redis.from_url(redis_url)
    q = Queue(connection=conn)

    # create the worker and process the request
    worker = Worker(q)
    worker.work()