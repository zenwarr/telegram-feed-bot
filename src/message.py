from dataclasses import dataclass
from message_with_entities import MessageWithEntities
import telegram

from utils import utf16_code_units_in_text

ELLIPSIS = "..."
ELLIPSIS_CODEPOINTS = utf16_code_units_in_text(ELLIPSIS)


@dataclass
class Message:
    type: str
    title: str = None
    text: str | MessageWithEntities = None
    source_url: str = None
    res_url: str = None

    def get_text_with_entities(self, max_length=None):
        entities = []

        title = self._get_title()
        if len(title):
            entities.append(telegram.MessageEntity(type=telegram.MessageEntity.BOLD, offset=0,
                                                   length=utf16_code_units_in_text(title)))

        footer = self._get_footer()

        content = self.text if isinstance(self.text, str) else self.text.text

        total_length = len(title) + len(content) + len(footer)
        if max_length is not None and total_length > max_length:
            content = content[:max_length - len(footer) - len(title) - len(ELLIPSIS)] + '...'

        if isinstance(self.text, MessageWithEntities):
            content_codeunits = utf16_code_units_in_text(content)
            for e in self.text.entities:
                if e.offset < content_codeunits:
                    fixed_length = e.length if e.offset + e.length <= content_codeunits else content_codeunits - e.offset - ELLIPSIS_CODEPOINTS
                    entities.append(
                        telegram.MessageEntity(type=e.type,
                                               offset=e.offset + utf16_code_units_in_text(title),
                                               length=fixed_length,
                                               url=e.url))

        if len(footer):
            entities.append(
                telegram.MessageEntity(type=telegram.MessageEntity.TEXT_LINK,
                                       offset=utf16_code_units_in_text(title) + utf16_code_units_in_text(content) + 2,
                                       length=utf16_code_units_in_text(footer) - 2,
                                       url=self.source_url)
            )

        return title + content + footer, entities

    def _get_title(self):
        if self.title is None or len(self.title) == 0:
            return ''

        return f'{self.title}\n\n'

    def _get_footer(self):
        if self.source_url is None or len(self.source_url) == 0:
            return ''

        if len(self.title) or len(self.text.text):
            return f'\n\nsource'
        else:
            return "source"
