import unittest

from generic_filter import html_to_text_with_entities


class TestGenericFilter(unittest.TestCase):
    def test_basic_tag(self):
        self.assertEqual(html_to_text_with_entities("<div>text</div>").text, "text")

    def test_basic_text(self):
        self.assertEqual(html_to_text_with_entities("text").text, "text")

    def test_inserts_newline_between_paragraphs(self):
        self.assertEqual(html_to_text_with_entities("<p>text1</p><p>text2</p>").text, "text1\n\ntext2")

    def test_does_not_insert_newline_between_inline(self):
        self.assertEqual(html_to_text_with_entities("<span>text1</span><span>text2</span>").text, "text1text2")

    def test_combination_of_block_and_inline(self):
        self.assertEqual(html_to_text_with_entities("<p>text1</p><span>text2</span>").text, "text1\n\ntext2")

    def test_applies_simple_formatting(self):
        result = html_to_text_with_entities("text <b>bold text</b>")
        self.assertEqual(result.text, "text bold text")
        self.assertEqual(get_entity(result.entities[0]), ["bold", 5, 9])

    def test_nested_formatting(self):
        result = html_to_text_with_entities("text <b>bold <i>italic text</i></b>")
        self.assertEqual(result.text, "text bold italic text")
        self.assertEqual(get_entity(result.entities[1]), ["bold", 5, 16])
        self.assertEqual(get_entity(result.entities[0]), ["italic", 10, 11])

    def test_link(self):
        result = html_to_text_with_entities("text <a href=\"https://example.com\">link</a>")
        self.assertEqual(result.text, "text link")
        self.assertEqual(get_entity(result.entities[0]), ["url", 5, 4, "https://example.com"])


def get_entity(entity):
    r = [entity.type, entity.offset, entity.length]
    if "url" in entity.type:
        r.append(entity.url)
    return r
