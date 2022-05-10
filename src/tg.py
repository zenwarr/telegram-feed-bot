import time
import os
import telegram
from telegram.ext import ExtBot

from src.message import Message
from src.post_db import add_post


def get_tg_bot() -> ExtBot:
    if get_tg_bot.value is None:
        get_tg_bot.value = ExtBot(os.environ.get("TELEGRAM_BOT_TOKEN"))
    return get_tg_bot.value


get_tg_bot.value = None


def queue_msg(msg: Message, channel: str):
    queue = get_tg_queue()
    queue.add(msg, channel)


class TelegramQueue:
    def __init__(self):
        self.queue = []

    def add(self, msg: Message, channel: str):
        self.queue.append((msg, channel))

    def process(self):
        for msg, channel in self.queue:
            try:
                send_msg(msg, channel)
                add_post(msg.feed, msg.post_id)
            except Exception as e:
                print(f"Error while sending message: {e}")
                add_post(msg.feed, msg.post_id, str(e))

            time.sleep(3)
        self.queue = []


def send_msg(msg: Message, channel: str):
    text, entities = msg.get_text_with_entities(telegram.MAX_MESSAGE_LENGTH if msg.type == 'text' else telegram.MAX_CAPTION_LENGTH)
    tg_bot = get_tg_bot()

    if msg.type == "text":
        tg_bot.send_message(chat_id=channel,
                            text=text,
                            entities=entities,
                            disable_web_page_preview=not msg.link_preview)
    elif msg.type == "image" and not msg.res_url.endswith(".gif"):
        tg_bot.send_photo(chat_id=channel,
                          photo=msg.res_url,
                          caption=text,
                          caption_entities=entities)
    elif msg.type == "image" and msg.res_url.endswith(".gif"):
        tg_bot.send_animation(chat_id=channel,
                              animation=msg.res_url,
                              caption=text,
                              caption_entities=entities)
    elif msg.type == "video":
        tg_bot.send_video(chat_id=channel,
                          video=msg.res_url,
                          caption=text,
                          caption_entities=entities)


def get_tg_queue():
    if get_tg_queue.value is None:
        get_tg_queue.value = TelegramQueue()
    return get_tg_queue.value


get_tg_queue.value = None
