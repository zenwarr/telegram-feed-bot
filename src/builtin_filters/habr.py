import telegram
import re
from src.message import Message, Button
from src.utils import utf16_codeunits_in_text, utf16_codeunit_index_to_pos
from src.generic_filter import html_to_text_with_entities, rtrim_text


HABR_LINK_TEXTS = ["Читать далее", "Читать дальше →"]


def content_filter(entry):
    text = html_to_text_with_entities(entry.summary)

    links = list(filter(lambda e: e.type == telegram.MessageEntity.TEXT_LINK, text.entities))
    if len(links):
        last_link = links[-1]
        if last_link.offset + last_link.length == utf16_codeunits_in_text(text.text):
            e_start = utf16_codeunit_index_to_pos(text.text, last_link.offset)
            e_end = utf16_codeunit_index_to_pos(text.text, last_link.offset + last_link.length)
            text.text = text.text[:e_start] + text.text[e_end:]
            del text.entities[text.entities.index(last_link)]

    rtrim_text(text)

    link = entry.link
    # remove url parameters from link
    link = re.sub("\\?.*", "", link)

    return Message(type="text", title=entry.title, source_url=link, text=text)
