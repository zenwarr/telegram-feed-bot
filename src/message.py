from dataclasses import dataclass


@dataclass
class Message:
    type: str
    text: str = None
    text_parts: list[str] = None
    res_url: str = None

    def build_text(self, max_length):
        if self.text_parts is not None:
            title, content, link = self.text_parts
            title = f'*{title}*' if title else ''
            link = f'[source]({link})' if link else ''
            content = content or ""

            min_length = 0
            if title:
                min_length += len(title) + 2
            if link and content:
                min_length += len(link) + 2

            if len(content) + min_length > max_length:
                content = content[:max_length - min_length] + '...'

            parts = list(filter(lambda x: x, [title, content, link]))
            return "\n\n".join(parts)
        else:
            return self.text
