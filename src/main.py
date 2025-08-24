from textnode import TextNode
from htmlnode import HTMLNode


def main():
    node = TextNode("This is some anchor text", "link", "https://boot.dev")
    print(node)

    node = HTMLNode("a", "myfirst site",children=None,props={"href":"https://boot.dev"})
    print(node)

if __name__ == "__main__":
    main()