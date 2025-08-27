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

node = TextNode("This is text with a `code block` word, and a second `code block 2` inside", TextType.TEXT)
node2 = TextNode("This is text with a `code block 3` word, and a second `code block 4` inside", TextType.TEXT)
node3 = TextNode("This is text with a `code block` word, and a second `code block 2` inside", TextType.BOLD)
new_nodes = split_nodes_delimiter([node, node2, node3], "`", TextType.CODE)
print(new_nodes)