import datetime
import re
from dataclasses import dataclass
import feedparser
from config import get_config
from filters import get_content_filter
from post_db import is_post_sent, update_fetch_date
from tg import queue_msg, get_tg_queue


def fetch_feeds():
    print("fetching feeds")

    config = get_config()
    for feed in config.get('feeds', []):
        try:
            fetch_feed(feed)
        except Exception as e:
            print("error fetching feed {}: {}".format(feed.get("url"), e))

    get_tg_queue().process()

    print("fetching feeds done, waiting till next scheduled run")


def fetch_feed(feed):
    feed_id = feed.get("id") or feed.get("url")
    print("fetching feed {}".format(feed_id))

    new_last_fetch = datetime.datetime.now()
    entries = feedparser.parse(feed['url'])

    for entry in entries.entries:
        post_id = entry.get("link")
        if is_post_sent(feed_id, post_id):
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
            print('malformed post "{}", content is empty'.format(post_id, feed_id))
            continue

        if not matches_conditions(feed, msg):
            continue

        msg.feed = feed_id
        msg.post_id = post_id
        msg.link_preview = feed.get("link_preview", True)
        msg.enable_footer = feed.get("footer", True)

        queue_msg(msg, feed.get("channel"))

    update_fetch_date(feed_id, new_last_fetch)


def matches_conditions(feed, msg):
    full_msg_text, entities = msg.get_text_with_entities()

    match_re = feed.get("should_match")
    if match_re is not None:
        if not re.search(match_re, full_msg_text, re.IGNORECASE):
            return False

    not_match_re = feed.get("should_not_match")
    if not_match_re is not None:
        patterns = not_match_re if isinstance(not_match_re, list) else [not_match_re]
        for pattern in patterns:
            if re.search(pattern, full_msg_text, re.IGNORECASE):
                return False

    return True



@dataclass
class FeedEntry:
    content: str
    summary: str
    title: str
    link: str
