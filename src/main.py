from textnode import TextNode
from htmlnode import HTMLNode, LeafNode, ParentNode


def main():
    node = TextNode("This is some anchor text", "link", "https://boot.dev")
    print(node)

    node = HTMLNode("a", "myfirst site",children=None,props={"href":"https://boot.dev"})
    print(node)

    grandchild_node = LeafNode("b", "grandchild")
    grandchild_node_p = LeafNode("p", "secod one")
    child_node = ParentNode("span", [grandchild_node, grandchild_node_p])
    parent_node = ParentNode("div", [child_node])
    print(parent_node.to_html())

if __name__ == "__main__":
    main()