import datetime
import logging
import sys

import azure.functions as func
import requests

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    if mytimer.past_due:
        logger.info("APP: The timer is past due!")

    logger.info("APP: Portuguese Politics daily function ran at %s", utc_timestamp)

    # the goal is just to send a request to avoid the Heroku Dyno to sleep
    requests.get("https://portuguese-politics.herokuapp.com/docs")

    logger.info("APP: Done.")
