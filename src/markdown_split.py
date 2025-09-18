import re
from typing import List
from textnode import TextNode, TextType


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

def text_to_textnodes(text):
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