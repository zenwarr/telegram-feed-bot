import datetime
import re
from dataclasses import dataclass
import feedparser
from config import get_config
from filters import get_content_filter
from post_db import is_post_sent, add_post, update_fetch_date
from tg import send_msg, get_tg_queue


def fetch_feeds():
    print("fetching feeds")

    config = get_config()
    for feed in config['feeds']:
        try:
            fetch_feed(feed)
        except Exception as e:
            print("error fetching feed {}: {}".format(feed.get("url"), e))

    get_tg_queue().process()

    print("fetching feeds done, waiting till next scheduled run")


def fetch_feed(feed, sender=None):
    feed_id = feed.get("id") or feed.get("url")
    print("fetching feed {}".format(feed_id))

    new_last_fetch = datetime.datetime.now()
    entries = feedparser.parse(feed['url'])

    for entry in entries.entries:
        post_id = entry.get("link")
        if is_post_sent(feed_id, post_id):
            print('ignoring post "{}" from "{}", already sent'.format(post_id, feed_id))
            continue

        title = entry.get("title")
        title_prefix = feed.get("title_prefix")
        if title_prefix:
            title = f"[{title_prefix}] {title}"

        summary = entry.get("summary")

        content = entry.get("content")
        content = content[0].value if content is not None and len(content) >= 1 else ""

        link = entry.get("link")

        content_filter = get_content_filter(feed.get("filter"))
        msg = content_filter(FeedEntry(title=title, summary=summary, content=content, link=link))
        if msg is None:
            print('malformed post "{}" from "{}", content is empty'.format(post_id, feed_id))
            continue

        match_re = feed.get("match")
        if match_re is not None:
            full_msg_text = msg.build_text()
            if not re.match(match_re, full_msg_text, re.MULTILINE & re.IGNORECASE):
                print('ignoring post "{}" from "{}", does not match pattern'.format(post_id, feed_id))

        print('sending post "{}" from "{}"'.format(post_id, feed_id))
        if (sender or send_msg)(msg, feed.get("channel")):
            add_post(feed_id, post_id)

    update_fetch_date(feed_id, new_last_fetch)


@dataclass
class FeedEntry:
    content: str
    summary: str
    title: str
    link: str
