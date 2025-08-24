import unittest

from htmlnode import HTMLNode


class TestTextNode(unittest.TestCase):

    def test_repr_format(self):
        node = HTMLNode("a", "myfirst site",children=None,props={"href":"https://boot.dev"})
        self.assertEqual(repr(node), "HTMLNode(tag='a', value='myfirst site', children=None, props={'href': 'https://boot.dev'})")

    def test_props(self):
        node = HTMLNode("a", "myfirst site",children=None,props={"href":"https://boot.dev", "target":"_blank"})
        self.assertEqual(node.props_to_html(), ' href="https://boot.dev" target="_blank"')

    def test_empty_props(self):
        node = HTMLNode("a", "myfirst site")
        self.assertEqual(node.props_to_html(), "")


if __name__ == "__main__":
    unittest.main()
