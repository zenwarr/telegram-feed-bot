import requests

from config import get_config
from message import Message
from post_db import is_post_sent, add_post
from tg import queue_msg, get_tg_queue
from urllib.parse import urlparse


def get_top_subreddit_posts(subreddit, limit):
    try:
        url = f'https://www.reddit.com/r/{subreddit}/top.json?sort=top&t=day&limit={limit}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 '
                          'Safari/537.36 '
        }
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            posts = r.json()['data']['children']

            posts = filter(lambda x: x.get("kind") == "t3", posts)
            posts = map(lambda x: x.get("data"), posts)
            posts = map(lambda x: {
                "title": x.get("title"),
                "content": x.get("selftext"),
                "link": x.get("url"),
                "link_type": "video" if x.get("is_video") else get_post_type(x.get("url")),
                "permalink": get_full_url(x.get("permalink")),
            }, posts)
            posts = filter(lambda x: x.get("link_type") in ["image", "video"], posts)
            return list(posts)
    except Exception as e:
        print("failed to get top posts from reddit: ", e)
        return None


def fetch_reddit_feeds():
    print("fetching reddit feeds")

    config = get_config()
    for feed in config.get('reddit', []):
        try:
            fetch_subreddit(feed)
        except Exception as e:
            print("error fetching reddit feed {}: {}".format(feed.get("url"), e))

    get_tg_queue().process()
    print("fetching reddit feeds done, waiting till next scheduled run")


def fetch_subreddit(feed):
    reddit_name = feed.get("name")
    posts = get_top_subreddit_posts(reddit_name, 40)

    for post in posts:
        if is_post_sent(reddit_name, post.get("link")):
            continue

        msg = Message(type=post.get("link_type"), res_url=post.get("link"), title=post.get("title"), text="", source_url=post.get("permalink"))
        msg.feed = reddit_name
        msg.post_id = post.get("link")

        queue_msg(msg, feed.get("channel"))

        break


def get_post_type(url):
    domain = urlparse(url).netloc
    if url.endswith(".mp4"):
        return "video"
    elif domain in ["i.redd.it", "i.imgur.com"]:
        return "image"
    else:
        return "other"


def get_full_url(permalink):
    return f"https://www.reddit.com{permalink}"
