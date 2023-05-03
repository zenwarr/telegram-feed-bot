from dataclasses import dataclass
import telegram

from src.text_with_entities import TextWithEntities
from src.utils import utf16_codeunits_in_text

ELLIPSIS = "…"
ELLIPSIS_CODEPOINTS = utf16_codeunits_in_text(ELLIPSIS)


@dataclass
class Button:
    text: str
    url: str

    def get_inline_keyboard_button(self):
        return telegram.InlineKeyboardButton(text=self.text, url=self.url)


@dataclass
class Message:
    type: str
    title: str = None
    text: str | TextWithEntities = None
    source_url: str = None
    res_url: str = None
    feed: str = None
    post_id: str = None
    link_preview: bool = True

    # if True, footer with source link is going to be appended to the end of the message
    enable_footer: bool = True

    # if True, the title itself is going to be a link to source post.
    # If this option is enabled, footer is going to be hidden automatically.
    title_link: bool = True

    # if set to non-None value, a small anchor emoji is going to be added to the title link
    # this emoji is going to be a link that is going to be picked by telegram for preview instead of the `title_link`
    title_link_preview: str = None

    button_links: list[Button] = None

    def get_reply_markup(self):
        if not self.button_links:
            return None

        buttons = [b.get_inline_keyboard_button() for b in self.button_links]
        return telegram.InlineKeyboardMarkup([buttons])

    def get_text_with_entities(self, max_length=None):
        entities = []

        title = self._get_title()
        if title:
            entities.append(telegram.MessageEntity(type=telegram.MessageEntity.BOLD,
                                                   offset=0,
                                                   length=utf16_codeunits_in_text(title)))

        original_title_codepoint_count = utf16_codeunits_in_text(title)
        title_link_offset = 0
        if self.title_link_preview and title:
            title_link_icon = "🗒"
            title = f"{title_link_icon} {title}"
            entities.append(telegram.MessageEntity(type=telegram.MessageEntity.TEXT_LINK,
                                                   offset=0,
                                                   length=utf16_codeunits_in_text(title_link_icon),
                                                   url=self.title_link_preview))
            title_link_offset += utf16_codeunits_in_text(title_link_icon + " ")

        if self.title_link and self.source_url:
            entities.append(telegram.MessageEntity(type=telegram.MessageEntity.TEXT_LINK,
                                                   offset=title_link_offset,
                                                   length=original_title_codepoint_count,
                                                   url=self.source_url))

        footer = self._get_footer()
        content = self._get_text()

        total_length = len(title) + len(content) + len(footer)
        if max_length is not None and total_length > max_length:
            content = content[:max_length - len(footer) - len(title) - len(ELLIPSIS)] + ELLIPSIS

        if isinstance(self.text, TextWithEntities):
            content_codeunits = utf16_codeunits_in_text(content)
            for e in self.text.entities:
                if e.offset < content_codeunits - ELLIPSIS_CODEPOINTS:
                    fixed_length = e.length if e.offset + e.length <= content_codeunits else content_codeunits - e.offset - ELLIPSIS_CODEPOINTS
                    entities.append(
                        telegram.MessageEntity(type=e.type,
                                               offset=e.offset + utf16_codeunits_in_text(title),
                                               length=fixed_length,
                                               url=e.url))

        if footer:
            entities.append(
                telegram.MessageEntity(type=telegram.MessageEntity.TEXT_LINK,
                                       offset=utf16_codeunits_in_text(title) + utf16_codeunits_in_text(content) + 2,
                                       length=utf16_codeunits_in_text(footer) - 2,
                                       url=self.source_url)
            )

        return title + content + footer, entities

    def _get_text(self):
        return self.text if isinstance(self.text, str) else self.text.text

    def _get_title(self):
        if not self.title:
            return ''

        return f'{self.title}\n\n' if self._get_text() else self.title

    def _get_footer(self):
        if not self.source_url or not self.enable_footer or self.title_link:
            return ''

        if self.title or self.text.text:
            return f'\n\nsource'
        else:
            return "source"
