import unittest

from src.filters import get_content_filter
from src.generic_filter import html_to_text_with_entities


class TestGenericFilter(unittest.TestCase):
    def test_basic_tag(self):
        self.assertEqual(html_to_text_with_entities("<div>text</div>").text, "text")

    def test_basic_text(self):
        self.assertEqual(html_to_text_with_entities("text").text, "text")

    def test_inserts_newline_between_paragraphs(self):
        self.assertEqual(
            html_to_text_with_entities("<p>text1</p><p>text2</p>").text,
            "text1\n\ntext2",
        )

    def test_does_not_insert_newline_between_inline(self):
        self.assertEqual(
            html_to_text_with_entities("<span>text1</span><span>text2</span>").text,
            "text1text2",
        )

    def test_combination_of_block_and_inline(self):
        self.assertEqual(
            html_to_text_with_entities("<p>text1</p><span>text2</span>").text,
            "text1\n\ntext2",
        )

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
        result = html_to_text_with_entities(
            'text <a href="https://example.com">link</a>'
        )
        self.assertEqual(result.text, "text link")
        self.assertEqual(
            get_entity(result.entities[0]), ["url", 5, 4, "https://example.com"]
        )

    def test_complex(self):
        result = html_to_text_with_entities(
            """<p><img src="https://effectivetypescript.com/images/twitch-screengrab.jpg" title="Screengrab from Twitch" width="320"
        height="180" style="float: right; margin-left: 10px;">I made my <a
    href="https://www.twitch.tv/videos/1455722291">Twitch debut</a> last week with <a
    href="https://twitter.com/JoshuaKGoldberg">Josh Goldberg</a>, who&#39;s writing O&#39;Reilly&#39;s upcoming <a
    href="https://learning.oreilly.com/library/view/learning-typescript/9781098110321/"><em>Learning TypeScript</em></a>
  title.</p><p>We talked through a <a href="https://github.com/JoshuaKGoldberg/eslint-plugin-expect-type/pull/47">recent
  PR</a> I created to add TwoSlash support for Josh&#39;s expect-type eslint plugin. That syntax looks like this:</p>
<figure class="highlight ts">
  <table>
    <tr>
      <td class="code">
        <pre><code class="hljs ts"><span class="hljs-keyword">let</span> four = <span
            class="hljs-number">4</span>;<br><span class="hljs-comment">// ^? let four: number</span><br></code></pre>
      </td>
    </tr>
  </table>
</figure><span id="more"></span><p>The eslint plugin will then check that TypeScript reports <code>let four:
  number</code> when you get quickinfo for <code>four</code>. This lets you write tests for <a
    href="https://effectivetypescript.com/2022/02/25/gentips-4-display/">the display of types</a>. The idea is similar
  to <a href="https://github.com/microsoft/dtslint">dtslint</a> and <a
      href="https://effectivetypescript.com/2020/06/30/literate-ts/">literate-ts</a>, but with a few key advantages:</p>
<ol>
  <li>It uses a widely-adopted syntax (TwoSlash is even supported on the TypeScript playground).</li>
  <li>It&#39;s implemented through an eslint plugin, so you don&#39;t need another tool to make type assertions.</li>
  <li>It has an autofixer, which makes this pleasant to use.</li>
</ol><p>Once the PR is merged, this will be my new preferred way to test types, and I&#39;ll have to update the
  recommendations from my <a href="https://www.youtube.com/watch?v=nygcFEwOG8w">TSConf 2019 talk</a> as well as Item 52
  in <a href="https://amzn.to/38s1oCK"><em>Effective TypeScript</em></a> (&quot;Be Aware of the Pitfalls of Testing
  Types&quot;). I&#39;m already using it on my latest open source project, <a
      href="https://github.com/danvk/crudely-typed/">crudely-typed</a> (more on that soon!).</p><p>I had a great time
  chatting with Josh, and I think we both learned a thing or two. Hopefully you will,
  too!</p><!-- Add a placeholder for the Twitch embed -->
<div id="twitch-embed"></div><!-- Load the Twitch embed script -->
<script
    src="https://player.twitch.tv/js/embed/v1.js"></script><!-- Create a Twitch.Player object. This will render within the placeholder div -->
<script type="text/javascript"> new Twitch.Player("twitch-embed", {
  video: "1455722291",
  width: 620,
  height: 378,
  autoplay: false,
});</script>"""
        )

        self.assertEqual(result.text, "")

    def test_filter_loading(self):
        self.assertIsNotNone(get_content_filter("xkcd"))
        self.assertRaises(RuntimeError, lambda: get_content_filter("missing"))


def get_entity(entity):
    r = [entity.type, entity.offset, entity.length]
    if "url" in entity.type:
        r.append(entity.url)
    return r
