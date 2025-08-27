import unittest

from textnode import TextNode, TextType, text_node_to_html_node


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq(self):
        node = TextNode("This is a text node", TextType.BOLD, url=None)
        node2 = TextNode("This is a text node", TextType.CODE)
        self.assertNotEqual(node, node2)

    def test_inequality_different_type(self):
        node1 = TextNode("a", TextType.ITALIC)
        node2 = TextNode("a", TextType.CODE)
        self.assertNotEqual(node1, node2)

    def test_inequality_different_url(self):
        node1 = TextNode("link", TextType.LINK, url="http://a")
        node2 = TextNode("link", TextType.LINK, url="http://b")
        self.assertNotEqual(node1, node2)

    def test_url_none_vs_string(self):
        node_none = TextNode("x", TextType.LINK, url=None)
        node_str = TextNode("x", TextType.LINK, url="http://x")
        self.assertNotEqual(node_none, node_str)

    def test_text_type_accepts_enum_and_string(self):
        node_enum = TextNode("t", TextType.IMAGE)
        node_str = TextNode("t", "image")
        self.assertEqual(node_enum, node_str)
        self.assertIs(node_str.text_type, TextType.IMAGE)

    def test_invalid_text_type_raises_valueerror(self):
        with self.assertRaises(ValueError):
            TextNode("t", "not-a-type")

    def test_repr_format(self):
        node = TextNode("hi", TextType.CODE, url="u")
        self.assertEqual(repr(node), "TextNode(hi, code, u)")

    # Unit test for text_node_to_html_node()

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("This is a text node", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is a text node")

    def test_italic(self):
        node = TextNode("italics", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "italics")

    def test_code(self):
        node = TextNode("fmt", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "fmt")

    def test_link(self):
        node = TextNode("click", TextType.LINK, url="http://a")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "click")
        self.assertEqual(html_node.props, {"href": "http://a"})

    def test_image(self):
        node = TextNode("alt text", TextType.IMAGE, url="http://img")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        # implementation returns empty string as value for images
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": "http://img", "alt": "alt text"})

    def test_text_node_to_html_node_invalid_type_raises(self):
        class Dummy:
            # create an object that mimics TextNode but has an unknown text_type
            def __init__(self):
                self.text = "x"
                self.text_type = None
                self.url = None

        with self.assertRaises(ValueError):
            text_node_to_html_node(Dummy())

if __name__ == "__main__":
    unittest.main()
