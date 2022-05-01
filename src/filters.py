from bs4 import BeautifulSoup
import sys
from message import Message
import re
from generic_filter import generic_content_filter


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


# Example filter: parse html and extract text
def habr_content_filter(entry):
    doc = BeautifulSoup(entry.summary, 'html.parser')
    text = doc.get_text()
    text = re.sub("Читать далее", "", text)
    text = re.sub("Читать дальше →", "", text)
    text = text.strip()

    link = entry.link
    # remove url parameters from link
    link = re.sub("\?.*", "", link)

    return Message(type="text", title=entry.title, source_url=link, text=text)
