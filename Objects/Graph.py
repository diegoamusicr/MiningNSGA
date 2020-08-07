import numpy as np
from enum import Enum, auto


class NodeType(Enum):
    BANK = auto()
    DMNT = auto()
    ROUT = auto()


class Node:
    def __init__(self, n_type, n_name='', n_id=0):
        self.n_type = n_type
        self.n_name = n_name
        self.n_id = n_id


class Edge:

    def __init__(self, distance=np.inf, friction=0.0, slope=0.0):
        self.distance = distance
        self.friction = friction
        self.slope = slope


class Graph:

    def __init__(self):
        self.nodes = np.array([]).astype(Node)
        self.edges = np.array([]).astype(Edge).reshape(0, 1)

    def add_node(self, node):
        node.n_id = len(self.nodes)
        self.nodes = np.append(self.nodes, node)
        tmp_col = [Edge() for i in range(self.edges.shape[0])]
        tmp_row = [Edge() for i in range(self.edges.shape[0])]
        tmp_row += [Edge(0.0)]
        self.edges = np.hstack((self.edges, np.array([tmp_col]).T)) if len(tmp_col) else self.edges
        self.edges = np.vstack((self.edges, np.array([tmp_row])))

    def add_edge(self, node1_id, node2_id, edge):
        edge_inv = Edge(edge.distance, edge.friction, -edge.slope)
        self.edges[node1_id, node2_id] = edge
        self.edges[node2_id, node1_id] = edge_inv


