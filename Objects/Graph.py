import numpy as np
from enum import Enum, auto
import pandas as pd


class NodeType(Enum):
    BNCH = auto()
    CLEA = auto()
    CRSH = auto()
    DUMP = auto()
    ROUT = auto()


class Node:
    def __init__(self, n_type, n_name='', n_capacity=0, n_id=0, n_grade=0.0):
        self.type = n_type
        self.name = n_name
        self.id = n_id
        self.capacity = n_capacity
        self.grade = n_grade
        self.load = 0


class Edge:
    def __init__(self, distance=np.inf, friction=0.0, slope=0.0):
        self.distance = distance
        self.friction = friction
        self.slope = slope


class Graph:
    def __init__(self):
        self.nodes = np.array([]).astype(Node)
        self.edges = np.array([]).astype(Edge).reshape(0, 1)
        self.next = np.array([])
        self.distances = np.array([])
        self.paths = np.array([])
        self.bench_qty = 0

    def load_nodes_txt(self, filename):
        dataframe = pd.read_csv(filename, sep=';')
        if not dataframe.empty:
            for _, row in dataframe.iterrows():
                self.add_node(Node(
                    NodeType(int(row['NODE_TYPE'])),
                    row['NODE_NAME'],
                    (int(row['NODE_CAPACITY']) if not np.isnan(row['NODE_CAPACITY']) else 0),
                    int(row['NODE_ID']),
                    (float(row['NODE_GRADE']) if not np.isnan(row['NODE_GRADE']) else 0.0)))
        else:
            raise Exception("File is empty")

    def load_edges_txt(self, filename):
        dataframe = pd.read_csv(filename, sep=';')
        if not dataframe.empty:
            for _, row in dataframe.iterrows():
                self.add_edge(int(row['NODE_1_ID']),
                              int(row['NODE_2_ID']),
                              Edge(float(row['DISTANCE']),
                                   float(row['FRICTION']),
                                   float(row['SLOPE'])))
        else:
            raise Exception("File is empty")

    def add_node(self, node):
        node.id = len(self.nodes)
        self.nodes = np.append(self.nodes, node)
        tmp_col = [Edge() for _ in range(self.edges.shape[0])]
        tmp_row = [Edge() for _ in range(self.edges.shape[0])]
        tmp_row += [Edge(0.0)]
        self.edges = np.hstack((self.edges, np.array([tmp_col]).T)) if len(tmp_col) else self.edges
        self.edges = np.vstack((self.edges, np.array([tmp_row])))
        self.bench_qty += node.type == NodeType.BNCH

    def add_edge(self, node1_id, node2_id, edge):
        #friction and slope should contain 2 decimals maximum
        #distance in km
        edge_inv = Edge(edge.distance, edge.friction, -edge.slope)
        self.edges[node1_id, node2_id] = edge
        self.edges[node2_id, node1_id] = edge_inv

    def floyd_warshall_path(self):
        self.distances = np.full((len(self.nodes), len(self.nodes)), np.inf)
        self.next = np.full((len(self.nodes), len(self.nodes)), -1)
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes)):
                if self.edges[i, j].distance != np.inf:
                    self.distances[i, j] = self.edges[i, j].distance
                    self.next[i, j] = j
        for node in self.nodes:
            self.distances[node.id, node.id] = 0
            self.next[node.id, node.id] = node.id
        for k in range(len(self.nodes)):
            for i in range(len(self.nodes)):
                for j in range(len(self.nodes)):
                    if self.distances[i, j] > self.distances[i, k] + self.distances[k, j]:
                        self.distances[i, j] = self.distances[i, k] + self.distances[k, j]
                        self.next[i, j] = self.next[i, k]

    def get_path(self, node1_id, node2_id):
        if self.next[node1_id, node2_id] == -1:
            return np.array([])
        path = np.array([node1_id])
        while node1_id != node2_id:
            node1_id = self.next[node1_id, node2_id]
            path = np.append(path, node1_id)
        return path

    def calculate_paths(self):
        self.paths = np.empty((len(self.nodes), len(self.nodes)), dtype=object)
        self.floyd_warshall_path()
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes)):
                self.paths[i, j] = self.get_path(i, j)