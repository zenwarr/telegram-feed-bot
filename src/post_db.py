import sqlite3
import os

from src.config import get_data_dir


def get_post_db():
    if get_post_db.value is None:
        get_post_db.value = sqlite3.connect(
            os.environ.get("POST_DB_PATH") or (os.path.join(get_data_dir(), "posts.db")),
            detect_types=sqlite3.PARSE_DECLTYPES)
        init_db_structure(get_post_db.value)
    return get_post_db.value


get_post_db.value = None


def close_db():
    if get_post_db.value is not None:
        get_post_db.value.close()
        get_post_db.value = None


def init_db_structure(db):
    cur = db.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS feeds (
            id TEXT PRIMARY KEY,
            last_fetch_date TIMESTAMP DEFAULT current_timestamp
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            feed TEXT,
            post_url TEXT,
            send_ts TIMESTAMP DEFAULT current_timestamp,
            send_error TEXT DEFAULT NULL,
            FOREIGN KEY (feed) REFERENCES feeds(id)
        )
    """)

    db.commit()


def get_feed(feed_id):
    cur = get_post_db().cursor()
    cur.execute("SELECT * FROM feeds WHERE id = ?", (feed_id,))
    record = cur.fetchone()
    return {
        "id": record[0],
        "last_fetch_date": record[1]
    } if record is not None else None


def update_fetch_date(feed_id, ts):
    cur = get_post_db().cursor()
    cur.execute(
        "INSERT OR replace INTO feeds(id, last_fetch_date) VALUES (:feed, :ts)",
        {"feed": feed_id, "ts": ts})
    get_post_db().commit()


def add_post(feed_id, post_url, err=None):
    cur = get_post_db().cursor()

    # create feed if not exists
    cur.execute(
        "INSERT OR IGNORE INTO feeds(id) VALUES (:feed)",
        {"feed": feed_id})

    # insert post
    cur.execute(
        "INSERT INTO posts(feed, post_url, send_error) VALUES (:feed, :post_url, :err)",
        {"feed": feed_id, "post_url": post_url, "err": err})
    get_post_db().commit()


def is_post_sent(feed_id, post_url):
    cur = get_post_db().cursor()
    cur.execute(
        "SELECT * FROM posts WHERE feed = :feed AND post_url = :post_url",
        {"feed": feed_id, "post_url": post_url})
    return cur.fetchone() is not None
