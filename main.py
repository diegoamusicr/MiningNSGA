from Objects.Truck import *
from Solver.Solver import *
from Solver.Schedule import *


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
    G.add_edge(0, 1, Edge(5, 0.08, 0.2))
    G.add_edge(1, 3, Edge(8, 0.05, 0.04))
    G.add_edge(1, 4, Edge(8, 0.07, 0.07))
    G.add_edge(2, 4, Edge(3, 0.06, 0.09))
    G.add_edge(3, 4, Edge(4, 0.02, 0.1))
    G.add_edge(3, 6, Edge(10, 0.05, 0.08))
    G.add_edge(4, 5, Edge(2, 0.03, 0.2))
    G.add_edge(7, 1, Edge(1, 0.05, 0.2))
    G.add_edge(7, 3, Edge(4, 0.06, 0.1))
    G.add_edge(7, 4, Edge(3, 0.09, 0.03))
    G.calculate_paths()

    trucks = [Truck(0, t_capacity=300, t_id=0, t_brand='CAT', t_model='770G'), Truck(0, t_capacity=200, t_id=1, t_brand='CAT', t_model='770G'), Truck(0, t_capacity=250, t_id=2, t_brand='CAT', t_model='770G')]

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
    SC1 = Schedule(G, trucks, tasks, S1, 1)
    SC2 = Schedule(G, trucks, tasks, S2, 1)
    SC3 = Schedule(G, trucks, tasks, S3, 1)
    SC4 = Schedule(G, trucks, tasks, S4, 1)
    SC1.calculate_routes()
    SC2.calculate_routes()
    SC3.calculate_routes()
    SC4.calculate_routes()
    SC1.trucks_data()
    SC2.trucks_data()
    SC3.trucks_data()
    SC4.trucks_data()
    SC1.calculate_schedule()
    SC2.calculate_schedule()
    SC3.calculate_schedule()
    SC4.calculate_schedule()
    pass