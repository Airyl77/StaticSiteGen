import re
from typing import List
from enum import Enum
from textnode import TextNode, TextType, text_node_to_html_node
from htmlnode import ParentNode, LeafNode

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def split_nodes_delimiter(old_nodes: List[TextNode], delimiter, text_type: TextType):
    """
    Splits each TextNode in old_nodes by the given delimiter and assigns the specified text_type to the delimited segments.

    Parameters:
        old_nodes (List[TextNode]): List of TextNode objects to process.
        delimiter (str): The delimiter string to split the text.
        text_type (TextType): The TextType to assign to the delimited segments.

    Returns:
        List[TextNode]: A new list of TextNode objects with segments split and assigned appropriate text types.

    Raises:
        Exception: If the markdown syntax is invalid (even number of segments after splitting).
    """
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        split_nodes = []
        splitted_list = node.text.split(delimiter)
        if len(splitted_list) % 2 == 0:
            raise Exception("invalid Markdown syntax")
        for i in range(len(splitted_list)):
            if splitted_list[i] == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(splitted_list[i], TextType.TEXT))
            else:
                split_nodes.append(TextNode(splitted_list[i], text_type))
        new_nodes.extend(split_nodes)
    return new_nodes


def extract_markdown_images(text):
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return list(matches)


def extract_markdown_links(text):
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return list(matches)


def _split_nodes_by_matches(old_nodes, match_fn, make_literal, node_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        matches = match_fn(text)  # list of tuples, e.g. (alt, url) or (label, url)
        if not matches:
            new_nodes.append(node)
            continue

        for a, b in matches:
            literal = make_literal(a, b)
            before, sep, after = text.partition(literal)
            # partition is like split(..., 1) but keeps the separator presence clear
            if sep == "":
                # literal not found (edge-case if extractor and literal disagree)
                break
            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))
            new_nodes.append(TextNode(a, node_type, b))
            text = after

        if text:
            new_nodes.append(TextNode(text, TextType.TEXT))

    return new_nodes


def split_nodes_image(old_nodes):
    return _split_nodes_by_matches(
        old_nodes,
        match_fn=extract_markdown_images,                    # returns [(alt, url), ...]
        make_literal=lambda alt, url: f"![{alt}]({url})",
        node_type=TextType.IMAGE,
    )


def split_nodes_link(old_nodes):
    return _split_nodes_by_matches(
        old_nodes,
        match_fn=extract_markdown_links,                     # returns [(label, url), ...]
        make_literal=lambda label, url: f"[{label}]({url})",
        node_type=TextType.LINK,
    )


def text_to_textnodes(text) -> List[TextNode]:
    initial_node = TextNode(text, TextType.TEXT)
    # Split code segments
    code_nodes = split_nodes_delimiter([initial_node], "`", TextType.CODE)
    # Split bold segments
    bold_nodes = split_nodes_delimiter(code_nodes, "**", TextType.BOLD)
    # Split italic segments
    italic_nodes = split_nodes_delimiter(bold_nodes, "_", TextType.ITALIC)
    # Split image segments
    image_nodes = split_nodes_image(italic_nodes)
    # Split link segments
    nodes = split_nodes_link(image_nodes)
    return nodes


def markdown_to_blocks(markdown):
    """
    Splits a markdown string into a list of non-empty blocks.

    A block is defined as a section of text separated by two or more newlines.
    Leading and trailing whitespace is removed from each block, and empty blocks are omitted.

    Args:
        markdown (str): The markdown content to split.

    Returns:
        list[str]: A list of non-empty, stripped markdown blocks.
    """
    all_blocks = markdown.split('\n\n')
    clean_blocks = [stripped for block in all_blocks if (stripped := block.strip())]
    return clean_blocks


def block_to_block_type(block):
    """
    Determines the type of a Markdown block.
    Analyzes the given block of text and returns its corresponding BlockType,
    such as HEADING, CODE, QUOTE, UNORDERED_LIST, ORDERED_LIST, or PARAGRAPH,
    based on Markdown syntax rules.
    Args:
        block (str): The block of text to classify.
    Returns:
        BlockType: The type of the block, as defined by the BlockType enum.
    """
    heading = r'^#{1,6}\s.*$'
    code_block = r'^```.*```$'

    # Check for heading (single line)
    if re.match(heading, block):
        return BlockType.HEADING
    
    # Check for code block (single line fenced)
    if re.match(code_block, block, re.DOTALL):
        return BlockType.CODE
    
    # For multi-line blocks, check each line
    lines = block.split('\n')
    if not lines:
        return BlockType.PARAGRAPH
    
    # Check for quote (all non-empty lines must start with >)
    if all(line.startswith('>') for line in lines if line.strip()):
        return BlockType.QUOTE
    
    # Check for unordered list (all non-empty lines must start with -)
    if all(line.startswith('-') for line in lines if line.strip()):
        return BlockType.UNORDERED_LIST
    # Check for ordered list (all non-empty lines must start with a number followed by .)
    
    list_numbering = 1
    ordered_list = True
    for line in lines:
        if not line.startswith(str(list_numbering)+". "):
            ordered_list = False
            break
        list_numbering += 1
    
    return BlockType.ORDERED_LIST if ordered_list else BlockType.PARAGRAPH


def markdown_to_html_node(markdown):
    """
    Converts a markdown string into a hierarchical HTML node structure.

    Args:
        markdown (str): The markdown text to be converted.

    Returns:
        ParentNode: The root HTML node containing child nodes representing the parsed markdown blocks.

    The function splits the input markdown into blocks, determines the type of each block,
    and appends the corresponding HTML node (code, paragraph, heading, quote, unordered list, or ordered list)
    as a child to the root "div" node.
    """
    parent_node = ParentNode("div", [])
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        # print(block)
        block_type = block_to_block_type(block)
        if block_type == BlockType.CODE:
            parent_node.children.append(block_to_code_node(block))
        if block_type == BlockType.PARAGRAPH:
            parent_node.children.append(block_to_paragraph_node(block))
        if block_type == BlockType.HEADING:
            parent_node.children.append(block_to_heading_node(block))
        if block_type == BlockType.QUOTE:
            parent_node.children.append(block_to_quote_node(block))
        if block_type == BlockType.UNORDERED_LIST:
            parent_node.children.append(block_to_unordered_list_node(block))
        if block_type == BlockType.ORDERED_LIST:
            parent_node.children.append(block_to_ordered_list_node(block))      

    return parent_node


def text_to_children(text: str) -> List[LeafNode]:
    out_nodes = []
    list_of_nodes = text_to_textnodes(text)
    for node in list_of_nodes:
        out_nodes.append(text_node_to_html_node(node))
    return out_nodes


def block_to_paragraph_node(text):
    out_text = " ".join(text.split("\n"))
    parent = ParentNode("p", text_to_children(out_text))
    return parent


def block_to_heading_node(text):
    splitted_text = text.split(" ")
    heading_value = len(splitted_text[0])
    node = LeafNode(f"h{heading_value}", " ".join(splitted_text[1:]))
    return node


def block_to_code_node(text):
    leaf = LeafNode("code", text)
    parent = ParentNode("pre", [leaf])
    return parent


def block_to_quote_node(text):
    lines = text.split('\n')
    cleaned_lines = [line.lstrip('> ').rstrip() for line in lines]
    combined_text = ' '.join(cleaned_lines)
    parent = ParentNode("blockquote", text_to_children(combined_text))
    return parent


def block_to_unordered_list_node(text):
    lines = text.split('\n')
    cleaned_lines = [line.lstrip('- ').rstrip() for line in lines]
    parent = ParentNode("ul", [])
    for line in cleaned_lines:
        li_parent = ParentNode("li", text_to_children(line))
        parent.children.append(li_parent)    
    return parent


def block_to_ordered_list_node(text):
    lines = text.split('\n')
    cleaned_lines = [re.split(r'\d+\.\s', line, maxsplit=1)[1] for line in lines if line.strip()]
    parent = ParentNode("ol", [])
    for line in cleaned_lines:
        li_parent = ParentNode("li", text_to_children(line))
        parent.children.append(li_parent)    
    return parent


def extract_title(markdown):
    blocks = markdown_to_blocks(markdown)
    if blocks[0].startswith("# "):
        return blocks[0].lstrip("# ").strip()
    raise Exception("Header not found")
