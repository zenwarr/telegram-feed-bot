from bs4 import BeautifulSoup
from src.message import Message


def content_filter(entry):
    doc = BeautifulSoup(entry.summary, 'html.parser')
    image = doc.find("img")
    if image is not None:
        image_url = image.get("src")
        image_alt = image.get("alt")
        return Message(type="image", title=entry.title, source_url=entry.link, text=image_alt, res_url=image_url)
