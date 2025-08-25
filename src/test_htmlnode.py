import unittest

from htmlnode import HTMLNode, LeafNode

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

    # LeafNode tests
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")
    
    def test_leaf_to_html_a(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_leaf_to_html_div(self):
        node = LeafNode("div", "Hello, world!")
        self.assertEqual(node.to_html(), "<div>Hello, world!</div>")

    def test_leaf_to_html_notag(self):
        node = LeafNode("", "Hello, world!")
        self.assertEqual(node.to_html(), "Hello, world!")


if __name__ == "__main__":
    unittest.main()
