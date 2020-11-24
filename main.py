from Objects.Truck import *
from Solver.Solver import *
from Solver.Schedule import *
import time


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    G = Graph()
    G.add_node(Node(NodeType.ROUT))  # 0
    G.add_node(Node(NodeType.ROUT))  # 1
    G.add_node(Node(NodeType.DUMP, n_capacity=1500))  # 2
    G.add_node(Node(NodeType.BNCH))  # 3
    G.add_node(Node(NodeType.BNCH))  # 4
    G.add_node(Node(NodeType.CRSH))  # 5
    G.add_node(Node(NodeType.DUMP, n_capacity=1000000))  # 6
    G.add_node(Node(NodeType.CLEA))  # 7
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

    trucks = [Truck(0, t_capacity=300, t_id=0, t_brand='CAT', t_model='770G'),
              Truck(0, t_capacity=300, t_id=1, t_brand='CAT', t_model='770G'),
              Truck(2, t_capacity=200, t_id=2, t_brand='CAT', t_model='770G'),
              Truck(1, t_capacity=250, t_id=3, t_brand='CAT', t_model='770G'),
              Truck(1, t_capacity=200, t_id=4, t_brand='CAT', t_model='770G'),
              Truck(4, t_capacity=200, t_id=5, t_brand='CAT', t_model='770G'),
              Truck(0, t_capacity=200, t_id=6, t_brand='CAT', t_model='770G'),
              Truck(0, t_capacity=200, t_id=7, t_brand='CAT', t_model='770G'),
              Truck(0, t_capacity=200, t_id=8, t_brand='CAT', t_model='770G'),
              Truck(0, t_capacity=200, t_id=9, t_brand='CAT', t_model='770G'),
              Truck(3, t_capacity=200, t_id=10, t_brand='CAT', t_model='770G'),]
              # Truck(3, t_capacity=200, t_id=11, t_brand='CAT', t_model='770G'),
              # Truck(3, t_capacity=200, t_id=12, t_brand='CAT', t_model='770G'),
              # Truck(3, t_capacity=200, t_id=13, t_brand='CAT', t_model='770G'),
              # Truck(3, t_capacity=200, t_id=14, t_brand='CAT', t_model='770G'),
              # Truck(3, t_capacity=200, t_id=15, t_brand='CAT', t_model='770G'),
              # Truck(4, t_capacity=200, t_id=16, t_brand='CAT', t_model='770G'),
              # Truck(3, t_capacity=200, t_id=17, t_brand='CAT', t_model='770G'),
              # Truck(3, t_capacity=200, t_id=18, t_brand='CAT', t_model='770G'),
              # Truck(0, t_capacity=300, t_id=19, t_brand='CAT', t_model='770G'),
              # Truck(2, t_capacity=200, t_id=20, t_brand='CAT', t_model='770G'),
              # Truck(3, t_capacity=250, t_id=21, t_brand='CAT', t_model='770G'),
              # Truck(1, t_capacity=200, t_id=22, t_brand='CAT', t_model='770G'),
              # Truck(4, t_capacity=200, t_id=23, t_brand='CAT', t_model='770G'),
              # Truck(2, t_capacity=200, t_id=24, t_brand='CAT', t_model='770G'),
              # Truck(0, t_capacity=200, t_id=25, t_brand='CAT', t_model='770G'),
              # Truck(1, t_capacity=200, t_id=26, t_brand='CAT', t_model='770G'),
              # Truck(5, t_capacity=200, t_id=27, t_brand='CAT', t_model='770G'),
              # Truck(0, t_capacity=200, t_id=28, t_brand='CAT', t_model='770G'),
              # Truck(2, t_capacity=200, t_id=29, t_brand='CAT', t_model='770G'),
              # Truck(3, t_capacity=200, t_id=30, t_brand='CAT', t_model='770G'),
              # Truck(4, t_capacity=200, t_id=31, t_brand='CAT', t_model='770G'),
              # Truck(5, t_capacity=200, t_id=32, t_brand='CAT', t_model='770G')]

    objectives = [Objective(3, 500), Objective(4, 600), Objective(7, 1110)]

    start_time = time.time()
    N = NSGASolver(G, trucks, objectives)
    N.generate_task_array()
    N.run()
    print("--- %s seconds ---" % (time.time() - start_time))
    # tasks = N.generate_task_array()

    # S1 = Solution(G, N.task_array, trucks)
    # SC1 = Schedule(G, N.task_array,  trucks, S1, 10)
    # SC1.calculate_routes()
    # SC1.calculate_schedule()
    pass
