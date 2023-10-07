import os
import signal

import schedule
import sys
import time
from dotenv import load_dotenv

from src.post_db import close_db
from src.reddit import fetch_reddit_feeds
from src.rss import fetch_feeds


def exit_program():
    close_db()
    sys.exit(0)


def run():
    signal.signal(signal.SIGTERM, lambda a, b: exit_program())
    signal.signal(signal.SIGINT, lambda a, b: exit_program())

    env_file_path = os.environ.get("ENV_FILE_PATH")
    load_dotenv(env_file_path)

    fetch_feeds()

    schedule.every(10).minutes.do(fetch_feeds)
    schedule.every().hour.at(":05").do(fetch_reddit_feeds)

    while True:
        schedule.run_pending()
        time.sleep(55)
