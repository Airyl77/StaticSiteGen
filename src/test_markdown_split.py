import unittest
from markdown_split import (
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
)

from textnode import TextNode, TextType


class TestInlineMarkdown(unittest.TestCase):
    def test_delim_bold(self):
        node = TextNode("This is text with a **bolded** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded", TextType.BOLD),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_delim_bold_double(self):
        node = TextNode(
            "This is text with a **bolded** word and **another**", TextType.TEXT
        )
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded", TextType.BOLD),
                TextNode(" word and ", TextType.TEXT),
                TextNode("another", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_delim_bold_multiword(self):
        node = TextNode(
            "This is text with a **bolded word** and **another**", TextType.TEXT
        )
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded word", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("another", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_delim_italic(self):
        node = TextNode("This is text with an _italic_ word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_delim_bold_and_italic(self):
        node = TextNode("**bold** and _italic_", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        new_nodes = split_nodes_delimiter(new_nodes, "_", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
            ],
            new_nodes,
        )

    def test_delim_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_extract_markdown_images_basic(self):
        text = "here ![alt](http://img) and ![x](y)"
        imgs = extract_markdown_images(text)
        self.assertEqual(imgs, [("alt", "http://img"), ("x", "y")])

    def test_extract_markdown_images_empty_alt(self):
        text = "![](u)"
        imgs = extract_markdown_images(text)
        self.assertEqual(imgs, [("", "u")])

    def test_extract_markdown_links_basic(self):
        text = "a [link](http://a) and [b](c)"
        links = extract_markdown_links(text)
        self.assertEqual(links, [("link", "http://a"), ("b", "c")])

    def test_extract_markdown_links_ignores_images(self):
        text = "a ![alt](u) and [link](v)"
        links = extract_markdown_links(text)
        self.assertEqual(links, [("link", "v")])

    def test_extract_markdown_links_no_match_returns_empty(self):
        text = "no links here"
        self.assertEqual(extract_markdown_links(text), [])

    def test_split_nodes_image_basic(self):
        nodes = [TextNode("here ![alt](http://img) end", TextType.TEXT)]
        out = split_nodes_image(nodes)
        self.assertEqual(
            out,
            [
                TextNode("here ", TextType.TEXT),
                TextNode("alt", TextType.IMAGE, "http://img"),
                TextNode(" end", TextType.TEXT),
            ],
        )

    def test_split_nodes_link_basic(self):
        nodes = [TextNode("go [link](http://a)", TextType.TEXT)]
        out = split_nodes_link(nodes)
        self.assertEqual(
            out,
            [
                TextNode("go ", TextType.TEXT),
                TextNode("link", TextType.LINK, "http://a"),
            ],
        )

    def test_split_nodes_image_and_link_combined(self):
        # This sample contains both an image and a link; run image splitter then link splitter
        nodes = [TextNode("start ![i](im) middle [l](u) end", TextType.TEXT)]
        out = split_nodes_image(nodes)
        out = split_nodes_link(out)
        self.assertEqual(
            out,
            [
                TextNode("start ", TextType.TEXT),
                TextNode("i", TextType.IMAGE, "im"),
                TextNode(" middle ", TextType.TEXT),
                TextNode("l", TextType.LINK, "u"),
                TextNode(" end", TextType.TEXT),
            ],
        )

    def test_adjacent_images_and_links(self):
        # adjacent items without intervening text
        nodes = [TextNode("![a](u)![b](v)[c](w)", TextType.TEXT)]
        out = split_nodes_image(nodes)
        out = split_nodes_link(out)
        self.assertEqual(
            out,
            [
                TextNode("a", TextType.IMAGE, "u"),
                TextNode("b", TextType.IMAGE, "v"),
                TextNode("c", TextType.LINK, "w"),
            ],
        )

    def test_no_markdown_returns_same(self):
        # strings without markdown should be returned unchanged by splitters
        nodes = [TextNode("plain text without markdown", TextType.TEXT)]
        self.assertEqual(split_nodes_image(nodes), nodes)
        self.assertEqual(split_nodes_link(nodes), nodes)


if __name__ == "__main__":
    unittest.main()
