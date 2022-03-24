import os

import schedule
import time

from reddit import fetch_reddit_feeds
from rss import fetch_feeds
from dotenv import load_dotenv


env_file_path = os.environ.get("ENV_FILE_PATH")
if env_file_path is not None:
    load_dotenv(env_file_path)


fetch_feeds()

schedule.every(10).minutes.do(fetch_feeds)
schedule.every().hour.at(":05").do(fetch_reddit_feeds)

while True:
    schedule.run_pending()
    time.sleep(55)
