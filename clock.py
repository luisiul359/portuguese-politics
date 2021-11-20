import os
import redis

from rq import Queue
from apscheduler.schedulers.blocking import BlockingScheduler
from utils import test


redis_url = os.getenv("REDIS_URL")
sched = BlockingScheduler()


@sched.scheduled_job('cron', day_of_week='sat', hour=18, minute=20)
def scheduled_job():
    # connect to Redis
    conn = redis.from_url(redis_url)
    q = Queue(connection=conn)

    # send request to the queu
    q.enqueue(test, 'worked?')

sched.start()