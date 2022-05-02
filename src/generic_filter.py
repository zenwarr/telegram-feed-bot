from bs4 import BeautifulSoup
import telegram
from message import Message
from message_with_entities import MessageWithEntities
from utils import utf16_code_units_in_text
from urllib.parse import urlparse


def generic_content_filter(entry):
    title_msg = html_to_text_with_entities(entry.title)

    return Message(type="text",
                   title=title_msg.text,
                   text=html_to_text_with_entities(entry.summary),
                   source_url=entry.link)


def html_to_text_with_entities(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    result = MessageWithEntities(text="", entities=[])

    def walker(node):
        if isinstance(node, str):
            result.text = append_with_collapsing_space(result.text, node)
        elif node.name == "br":
            result.text = append_newline(result.text)
        else:
            mod_start = utf16_code_units_in_text(result.text)
            cur_entity = get_modifier_for_tag(node, mod_start)

            for child in node.children:
                walker(child)

            mod_end = utf16_code_units_in_text(result.text)
            if cur_entity is not None and mod_start != mod_end:
                cur_entity.length = mod_end - mod_start
                result.entities.append(cur_entity)

            if mod_end != mod_start and is_block_tag(node):
                result.text = append_newline(result.text)

    walker(soup)

    result.text = result.text.rstrip()
    new_result_codepoints = utf16_code_units_in_text(result.text)
    result.entities = list(filter(lambda e: e.offset < new_result_codepoints, result.entities))
    for e in result.entities:
        if e.offset + e.length > new_result_codepoints:
            e.length = new_result_codepoints - e.offset

    return result


def append_newline(text):
    if len(text) == 0:
        return text

    return text + "\n\n" if not text.endswith("\n") else text


def append_with_collapsing_space(text, suffix):
    if not text:
        return suffix.lstrip()

    if len(suffix) == 0:
        return text

    # if suffix has only spaces, append missing space to text and return it
    if suffix.strip() == "":
        return append_space_if_missing(text)

    if suffix[-1].isspace() and suffix[-1] != "\n":
        suffix = suffix.rstrip() + " "

    suffix_has_leading_space = suffix[0].isspace()
    if not suffix_has_leading_space:
        return text + suffix

    if len(text) > 0 and text[-1] == "\n":
        return text + suffix.lstrip()
    elif len(text) > 0 and text[-1].isspace():
        return text + " " + suffix.lstrip()
    else:
        return text + suffix


def append_space_if_missing(text):
    return text + " " if not (text.endswith(" ") or text.endswith("\n")) else text


inline_tags = ["a", "b", "i", "em", "strong", "span", "sub", "sup", "u", "small", "big", "del", "ins", "mark", "code",
               "samp", "kbd", "var", "cite", "abbr", "dfn", "time", "span"]


def is_block_tag(node):
    if node is None or node.name in ["[document]", "html", "body"]:
        return False

    return node.name not in inline_tags


tag_modifiers = {
    "b": "bold",
    "i": "italic",
    "s": "strikethrough",
    "code": "code",
    "em": "italic",
    "pre": "pre",
}


def get_modifier_for_tag(node, offset):
    if node.name in tag_modifiers:
        return telegram.MessageEntity(type=tag_modifiers[node.name], offset=offset, length=0)
    elif node.name == "a":
        link_url = node.get("href")
        if not is_valid_url(link_url):
            return None

        return telegram.MessageEntity(type=telegram.MessageEntity.TEXT_LINK, offset=offset, url=link_url, length=0)

    return None


def is_valid_url(url):
    if not url:
        return False

    try:
        result = urlparse(url)
        return result.scheme in ["http", "https"] and result.netloc != ""
    except:
        return False
