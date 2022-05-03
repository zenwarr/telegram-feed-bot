import telegram
from bs4 import BeautifulSoup
import sys
from message import Message
import re
from generic_filter import generic_content_filter, html_to_text_with_entities, rtrim_text
from utils import utf16_codeunit_index_to_pos, utf16_codeunits_in_text


def get_content_filter(name: str | None):
    if name is None or name == "generic":
        return generic_content_filter
    return getattr(sys.modules[__name__], name + "_content_filter")


# Example filter: extract image from post
def xkcd_content_filter(entry):
    doc = BeautifulSoup(entry.summary, 'html.parser')
    image = doc.find("img")
    if image is not None:
        image_url = image.get("src")
        image_alt = image.get("alt")
        return Message(type="image", title=entry.title, source_url=entry.link, text=image_alt, res_url=image_url)


HABR_LINK_TEXTS = ["Читать далее", "Читать дальше →"]


# Example filter: parse html and extract text
def habr_content_filter(entry):
    text = html_to_text_with_entities(entry.summary)

    links = list(filter(lambda e: e.type == telegram.MessageEntity.TEXT_LINK, text.entities))
    if len(links):
        last_link = links[-1]
        print(last_link.offset + last_link.length, utf16_codeunits_in_text(text.text))
        if last_link.offset + last_link.length == utf16_codeunits_in_text(text.text):
            e_start = utf16_codeunit_index_to_pos(text.text, last_link.offset)
            e_end = utf16_codeunit_index_to_pos(text.text, last_link.offset + last_link.length)
            text.text = text.text[:e_start] + text.text[e_end:]
            del text.entities[text.entities.index(last_link)]

    rtrim_text(text)

    link = entry.link
    # remove url parameters from link
    link = re.sub("\?.*", "", link)

    return Message(type="text", title=entry.title, source_url=link, text=text)
