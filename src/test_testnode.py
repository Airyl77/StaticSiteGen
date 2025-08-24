import unittest

from textnode import TextNode, TextType


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

if __name__ == "__main__":
    unittest.main()
