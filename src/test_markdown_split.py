import unittest
from markdown_split import (
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
    markdown_to_blocks,
    block_to_block_type,
    markdown_to_html_node,
    extract_title,
    BlockType
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

    def test_markdown_exception(self):
        node = TextNode(
            "This is text with a **bolded word and **another**", TextType.TEXT
        )
        with self.assertRaises(Exception):
            split_nodes_delimiter([node], "**", TextType.BOLD)

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

    def test_text_to_textnodes_plain(self):
        nodes = text_to_textnodes("plain text")
        self.assertEqual(nodes, [TextNode("plain text", TextType.TEXT)])

    def test_text_to_textnodes_combined_formatting(self):
        s = "Here `code` and **bold** and _ital_"
        nodes = text_to_textnodes(s)
        self.assertEqual(
            nodes,
            [
                TextNode("Here ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" and ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("ital", TextType.ITALIC),
            ],
        )

    def test_text_to_textnodes_images_and_links(self):
        s = "prefix ![a](i) mid [b](u) suffix"
        nodes = text_to_textnodes(s)
        self.assertEqual(
            nodes,
            [
                TextNode("prefix ", TextType.TEXT),
                TextNode("a", TextType.IMAGE, "i"),
                TextNode(" mid ", TextType.TEXT),
                TextNode("b", TextType.LINK, "u"),
                TextNode(" suffix", TextType.TEXT),
            ],
        )

    def test_nested_markdown(self):
        # Test nested formatting: bold containing italic
        s = "before **bold _ital_ end** after"
        nodes = text_to_textnodes(s)
        # The current implementation splits in this order: code, bold, italic
        # So italic splitting happens after bold splitting; expected behavior
        # Current parser only splits delimiters on TEXT nodes, so the italic
        # markup remains inside the BOLD node. We assert the current behavior
        # so the test documents it.
        self.assertEqual(
            nodes,
            [
                TextNode("before ", TextType.TEXT),
                TextNode("bold _ital_ end", TextType.BOLD),
                TextNode(" after", TextType.TEXT),
            ],
        )

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

 This is a third line   

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "This is a third line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_basic(self):
        markdown = "This is a paragraph.\n\nThis is another paragraph."
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, ["This is a paragraph.", "This is another paragraph."])

    def test_markdown_to_blocks_single_block(self):
        markdown = "Single block of text."
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, ["Single block of text."])

    def test_markdown_to_blocks_empty_string(self):
        markdown = ""
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_with_empty_blocks(self):
        markdown = "First paragraph.\n\n\n\nSecond paragraph."
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, ["First paragraph.", "Second paragraph."])

    def test_markdown_to_blocks_with_whitespace_only_blocks(self):
        markdown = "First paragraph.\n\n   \n\nSecond paragraph."
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, ["First paragraph.", "Second paragraph."])

    def test_markdown_to_blocks_leading_trailing_whitespace(self):
        markdown = "  First paragraph.  \n\n  Second paragraph.  "
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, ["First paragraph.", "Second paragraph."])

    def test_markdown_to_blocks_multiple_newlines(self):
        markdown = "First\n\n\n\nSecond"
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, ["First", "Second"])

    def test_blocktype_paragraph(self):
        md = "This is **bolded** paragraph"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [md])
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.PARAGRAPH)

    def test_blocktype_single_line_code(self):
        md = "```This is **bolded** paragraph```"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.CODE)
        
    def test_blocktype_multi_line_code(self):
        md = "```This is **bolded** \n paragraph```"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.CODE)

    def test_blocktype_heading_level1(self):
        md = "# Heading 1"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.HEADING)

    def test_blocktype_heading_level6(self):
        md = "###### Heading 6"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.HEADING)

    def test_blocktype_not_heading(self):
        md = "####### Heading 7"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.PARAGRAPH)

    def test_blocktype_quote(self):
        md = "> Quote1\n> Quote2"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.QUOTE)

    def test_blocktype_unordered_list(self):
        md = "- Quote1\n- Quote2"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.UNORDERED_LIST)

    def test_blocktype_ordered_list(self):
        md = "1. Item 1\n2. Item 2"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.ORDERED_LIST)

    def test_blocktype_ordered_list_error(self):
        md = "1. Item 1\n2. Item 2\n2. Item 3"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.PARAGRAPH)

    # Missing test cases to add:

    def test_blocktype_heading_level2(self):
        md = "## Heading 2"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.HEADING)

    def test_blocktype_heading_level3(self):
        md = "### Heading 3"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.HEADING)

    def test_blocktype_heading_level4(self):
        md = "#### Heading 4"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.HEADING)

    def test_blocktype_heading_level5(self):
        md = "##### Heading 5"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.HEADING)

    def test_blocktype_code_with_language(self):
        md = "```python\nprint('hello')\n```"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.CODE)

    def test_blocktype_empty_block(self):
        md = ""
        blocks = markdown_to_blocks(md)
        # Empty string results in empty list, so no blocks to test
        self.assertEqual(len(blocks), 0)

    def test_blocktype_whitespace_only(self):
        md = "   \n  \n\t"
        blocks = markdown_to_blocks(md)
        # Should be filtered out as empty
        self.assertEqual(len(blocks), 0)

    def test_blocktype_unordered_list_partial(self):
        md = "- Item1\n- Item2\nNot a list item"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.PARAGRAPH)

    def test_blocktype_ordered_list_non_sequential(self):
        md = "1. Item 1\n3. Item 2\n2. Item 3"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.PARAGRAPH)

    def test_blocktype_mixed_content(self):
        md = "Some text\n- list item\nMore text"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.PARAGRAPH)

    def test_blocktype_quote_partial(self):
        md = "> Quote line\nRegular paragraph line"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.PARAGRAPH)

    def test_blocktype_heading_with_special_chars(self):
        md = "# Heading with @#$%^&*()"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.HEADING)

    def test_blocktype_long_line(self):
        md = "# " + "A" * 1000  # Very long heading
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.HEADING)

    def test_blocktype_unordered_list_with_spaces(self):
        md = "-  Item with leading space\n- Another item"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.UNORDERED_LIST)

    def test_blocktype_ordered_list_with_extra_spaces(self):
        md = "1.   Item with extra spaces\n2. Another item"
        blocks = markdown_to_blocks(md)
        self.assertEqual(block_to_block_type(blocks[0]), BlockType.ORDERED_LIST)

    def test_markdown_to_html_node_paragraph(self):
        md = "This is a simple paragraph."
        node = markdown_to_html_node(md)
        self.assertEqual(node.tag, "div")
        self.assertEqual(len(node.children), 1)
        self.assertEqual(node.children[0].tag, "p")
        self.assertIn("This is a simple paragraph.", node.children[0].to_html())

    def test_markdown_to_html_node_heading(self):
        md = "# Heading 1"
        node = markdown_to_html_node(md)
        self.assertEqual(len(node.children), 1)
        self.assertEqual(node.children[0].tag, "h1")
        self.assertIn("Heading 1", node.children[0].to_html())

    def test_markdown_to_html_node_code(self):
        md = "```print('hello')```"
        node = markdown_to_html_node(md)
        self.assertEqual(len(node.children), 1)
        self.assertEqual(node.children[0].tag, "pre")
        self.assertEqual(node.children[0].children[0].tag, "code")
        self.assertIn("print('hello')", node.children[0].children[0].to_html())

    def test_markdown_to_html_node_quote(self):
        md = "> This is a quote\n> with two lines"
        node = markdown_to_html_node(md)
        self.assertEqual(len(node.children), 1)
        self.assertEqual(node.children[0].tag, "blockquote")
        self.assertIn("This is a quote with two lines", node.children[0].to_html())

    def test_markdown_to_html_node_unordered_list(self):
        md = "- Item 1\n- Item 2"
        node = markdown_to_html_node(md)
        self.assertEqual(len(node.children), 1)
        self.assertEqual(node.children[0].tag, "ul")
        self.assertEqual(len(node.children[0].children), 2)
        self.assertEqual(node.children[0].children[0].tag, "li")
        self.assertIn("Item 1", node.children[0].children[0].to_html())

    def test_markdown_to_html_node_ordered_list(self):
        md = "1. First\n2. Second"
        node = markdown_to_html_node(md)
        self.assertEqual(len(node.children), 1)
        self.assertEqual(node.children[0].tag, "ol")
        self.assertEqual(len(node.children[0].children), 2)
        self.assertEqual(node.children[0].children[1].tag, "li")
        self.assertIn("Second", node.children[0].children[1].to_html())

    def test_markdown_to_html_node_multiple_blocks(self):
        md = "# Heading\n\nParagraph text\n\n- List1\n- List2"
        node = markdown_to_html_node(md)
        self.assertEqual(node.tag, "div")
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].tag, "h1")
        self.assertEqual(node.children[1].tag, "p")
        self.assertEqual(node.children[2].tag, "ul")

    def test_markdown_to_html_node_empty(self):
        md = ""
        node = markdown_to_html_node(md)
        self.assertEqual(node.tag, "div")
        self.assertEqual(len(node.children), 0)

    def test_markdown_to_html_node_mixed_content(self):
        md = "# Heading\n\nParagraph\n\n```code block```\n\n> Quote"
        node = markdown_to_html_node(md)
        self.assertEqual([c.tag for c in node.children], ["h1", "p", "pre", "blockquote"])

    def test_extract_title_found(self):
        md = "# Heading\n\nParagraph\n\n```code block```\n\n> Quote"
        header = extract_title(md)
        self.assertEqual(header, "Heading")
    
    def test_extract_title_not_found(self):
        md = "## Heading\n\nParagraph\n\n```code block```\n\n> Quote"
        with self.assertRaises(Exception):
            extract_title(md)


if __name__ == "__main__":
    unittest.main(verbosity=1)
    # unittest.main(verbosity=2) # Verbose output
    # unittest.main() --- IGNORE --- # Default output
