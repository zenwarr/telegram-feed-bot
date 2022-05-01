import time

import os

import telegram
from telegram.ext import ExtBot
from message import Message
from typing import Callable


def get_tg_bot() -> ExtBot:
    if get_tg_bot.value is None:
        get_tg_bot.value = ExtBot(os.environ.get("TELEGRAM_BOT_TOKEN"))
    return get_tg_bot.value


get_tg_bot.value = None


def send_msg(msg: Message, channel: str) -> bool:
    tg_bot = get_tg_bot()
    queue = get_tg_queue()

    text, entities = msg.get_text_with_entities(
        telegram.MAX_MESSAGE_LENGTH if msg.type == 'text' else telegram.MAX_CAPTION_LENGTH)

    if msg.type == "text":
        queue.add(lambda: tg_bot.send_message(chat_id=channel,
                                              text=text,
                                              entities=entities))
    elif msg.type == "image" and not msg.res_url.endswith(".gif"):
        queue.add(lambda: tg_bot.send_photo(chat_id=channel,
                                            photo=msg.res_url,
                                            caption=text,
                                            entities=entities))
    elif msg.type == "image" and msg.res_url.endswith(".gif"):
        queue.add(lambda: tg_bot.send_animation(chat_id=channel,
                                                animation=msg.res_url,
                                                caption=text,
                                                entities=entities))
    elif msg.type == "video":
        queue.add(lambda: tg_bot.send_video(chat_id=channel,
                                            video=msg.res_url,
                                            caption=text,
                                            entities=entities))

    return True


class TelegramQueue:
    def __init__(self):
        self.queue = []

    def add(self, callback: Callable[[], None]):
        self.queue.append(callback)

    def process(self):
        for callback in self.queue:
            try:
                callback()
            except Exception as e:
                print(f"Error while sending message: {e}")

            time.sleep(3)
        self.queue = []


def get_tg_queue():
    if get_tg_queue.value is None:
        get_tg_queue.value = TelegramQueue()
    return get_tg_queue.value


get_tg_queue.value = None
