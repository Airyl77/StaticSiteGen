from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
import markdown_split as ms


def main():
    node = TextNode("This is some anchor text", "link", "https://boot.dev")
    print(node)
    node = TextNode("This is some anchor text", "link", "https://boot.dev")
    print(node)

    node = HTMLNode("a", "myfirst site",children=None,props={"href":"https://boot.dev"})
    print(node)

    grandchild_node = LeafNode("b", "grandchild")
    grandchild_node_p = LeafNode("p", "second one")
    child_node = ParentNode("span", [grandchild_node, grandchild_node_p])
    parent_node = ParentNode("div", [child_node])
    print(parent_node.to_html())

    text = "here ![alt](http://img) and ![x](y)"
    test_node = TextNode(
        "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png) " \
        "and here we go with ![image](https://i.imgur.com/zjjcJKZ.png) again and we have a [to youtube](https://www.youtube.com/@bootdotdev) here too",
        TextType.TEXT,
    )
    new_hodes = ms.split_nodes_image([test_node])
    new_hodes = ms.split_nodes_link(new_hodes)
    print(new_hodes)
    

 

if __name__ == "__main__":
    main()