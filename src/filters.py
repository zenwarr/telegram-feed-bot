from bs4 import BeautifulSoup
import sys
from message import Message
import re
import html2text
import html
import googletrans


def get_content_filter(name: str | None):
    if name is None:
        return generic_content_filter
    return getattr(sys.modules[__name__], name + "_content_filter")


# Example filter: extract image from post
def xkcd_content_filter(entry):
    doc = BeautifulSoup(entry.summary, 'html.parser')
    image = doc.find("img")
    if image is not None:
        image_url = image.get("src")
        image_alt = image.get("alt")
        return Message(type="image", text_parts=[entry.title, image_alt, entry.link], res_url=image_url)


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

    return Message(type="text", text_parts=[entry.title, text, link])


def generic_translate_content_filter(entry):
    msg = generic_content_filter(entry)
    msg.text_parts = [translate(t) for t in msg.text_parts]
    return msg


translator = googletrans.Translator()


def translate(text):
    translator.translate(text, src="en", dest="ru")


h = html2text.HTML2Text()
h.ignore_tables = True
h.ignore_images = True


def generic_content_filter(entry):
    text = h.handle(entry.summary)
    text = clean_text(text)

    link = entry.link

    return Message(type="text", text_parts=[entry.title, text, link])


def clean_text(text):
    groups = re.split("\n[\s]*\n+", text)

    # remove empty groups
    groups = [g for g in groups if g.strip() != ""]

    for i in range(len(groups)):
        # remove newlines
        groups[i] = re.sub("\n", "", groups[i])

        # replace multiple spaces not at the start of line
        groups[i] = re.sub(" +", " ", groups[i])

        # split into lines, trim lines and join back
        groups[i] = " ".join(line.strip() for line in groups[i].split("\n"))

        groups[i] = html.unescape(groups[i])

    return "\n\n".join(groups)
