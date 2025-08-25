import unittest

from htmlnode import ParentNode, LeafNode

class TestParentNode(unittest.TestCase):
    def test_renders_children_inside_tag(self):
        children = [LeafNode("span", "x"), LeafNode("b", "y")]
        node = ParentNode("div", children)
        self.assertEqual(node.to_html(), "<div><span>x</span><b>y</b></div>")

    def test_raises_when_tag_is_none(self):
        children = [LeafNode("span", "x")]
        node = ParentNode(None, children)
        with self.assertRaises(Exception):
            node.to_html()

    def test_raises_when_tag_is_empty(self):
        children = [LeafNode("span", "x")]
        node = ParentNode("", children)
        with self.assertRaises(Exception):
            node.to_html()

    def test_raises_when_children_is_none(self):
        node = ParentNode("div", None)
        with self.assertRaises(Exception):
            node.to_html()

    def test_raises_when_children_is_empty(self):
        node = ParentNode("div", [])
        with self.assertRaises(Exception):
            node.to_html()

    def test_nested_parent_renders(self):
        inner = ParentNode("li", [LeafNode(None, "item")])
        outer = ParentNode("ul", [inner])
        self.assertEqual(outer.to_html(), "<ul><li>item</li></ul>")

    def test_props_are_ignored_in_parent_output(self):
        children = [LeafNode("span", "x")]
        node = ParentNode("div", children, props={"id": "main"})
        # ParentNode.to_html does not include props in tag output
        self.assertEqual(node.to_html(), "<div><span>x</span></div>")


if __name__ == "__main__":
    unittest.main()
