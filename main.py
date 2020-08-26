from Objects.Graph import *


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    G = Graph()
    G.add_node(Node(NodeType.BANK))
    G.add_node(Node(NodeType.BANK))
    G.add_node(Node(NodeType.BANK))
    G.add_node(Node(NodeType.ROUT))
    G.add_node(Node(NodeType.ROUT))
    G.add_node(Node(NodeType.ROUT))
    G.add_edge(0, 1, Edge(5, 0.8, 0.2))
    G.add_edge(1, 3, Edge(8, 0.5, 0.4))
    G.add_edge(1, 4, Edge(8, 0.75, 0.7))
    G.add_edge(2, 3, Edge(3, 0.6, 0.9))
    G.add_edge(3, 4, Edge(4, 0.2, 0.1))
    pass