from Objects.Truck import *
from Solver.Solver import *

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    G = Graph()
    G.add_node(Node(NodeType.ROUT))                     # 0
    G.add_node(Node(NodeType.ROUT))                     # 1
    G.add_node(Node(NodeType.DUMP, n_capacity=500))     # 2
    G.add_node(Node(NodeType.BNCH))                     # 3
    G.add_node(Node(NodeType.BNCH))                     # 4
    G.add_node(Node(NodeType.CRSH))                     # 5
    G.add_node(Node(NodeType.DUMP, n_capacity=100000))  # 6
    G.add_node(Node(NodeType.CLEA))                     # 7
    G.add_edge(0, 1, Edge(5, 0.8, 0.2))
    G.add_edge(1, 3, Edge(8, 0.5, 0.4))
    G.add_edge(1, 4, Edge(8, 0.75, 0.7))
    G.add_edge(2, 4, Edge(3, 0.6, 0.9))
    G.add_edge(3, 4, Edge(4, 0.2, 0.1))
    G.add_edge(3, 6, Edge(10, 0.5, 0.8))
    G.add_edge(4, 5, Edge(2, 0.3, 0.2))
    G.add_edge(7, 1, Edge(1, 0.5, 0.2))
    G.add_edge(7, 3, Edge(4, 0.6, 0.1))
    G.add_edge(7, 4, Edge(3, 0.9, 0.3))

    trucks = [Truck(0, t_capacity=300, t_id=0), Truck(0, t_capacity=200, t_id=1), Truck(0, t_capacity=250, t_id=2)]
    objectives = [Objective(3, 5000), Objective(4, 6000), Objective(7, 2400)]

    N = NSGASolver(G, trucks, objectives)
    tasks = N.generate_task_array()

    S1 = Solution(tasks, trucks)
    S2 = Solution(tasks, trucks)
    S3 = Solution(tasks, trucks)
    S4 = Solution(tasks, trucks)
    S1.generate_random_solution()
    S2.generate_random_solution()
    S3.generate_random_solution()
    S4.generate_random_solution()
    pass