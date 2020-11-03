import numpy as np
import random
from Solver.Schedule import *


class Objective:
    def __init__(self, work_node_id, work_tons):
        self.work_node_id = work_node_id
        self.work_tons = work_tons
        self.completed = False


class Solution:

    def __init__(self, graph, task_array, trucks_array, solution=None, idx=None):
        self.graph = graph
        self.tasks = task_array
        self.trucks = trucks_array
        self.trucks_quantity = len(self.trucks)
        self.solution = np.empty((len(self.tasks), 2), dtype=int)
        self.tasks_per_truck = {}
        self.time_total = -1
        self.time_idle = -1
        self.idx = idx
        self.solution = solution
        if self.solution is None:
            self.generate_random_solution()

    def __repr__(self):
        return np.array2string(self.solution, max_line_width=np.inf).replace('\n', '')

    def generate_random_solution(self):
        self.solution = np.empty((len(self.tasks), 2), dtype=int)
        truck_ids = [i.id for i in self.trucks]
        task_counters = {t: 0 for t in truck_ids}
        task_orders_random = dict()
        for i in range(len(self.solution)):
            random_truck_id = self.trucks[random.randint(0, self.trucks_quantity-1)].id
            self.solution[i] = [random_truck_id, 0]
            task_counters[random_truck_id] += 1
        self.tasks_per_truck = task_counters.copy()
        for truck_id, count in task_counters.items():
            random_order = list(range(count))
            random.shuffle(random_order)
            task_orders_random[truck_id] = random_order
            task_counters[truck_id] = 0
        for i in range(len(self.solution)):
            truck_id = self.solution[i, 0]
            self.solution[i] = [truck_id, (task_orders_random[truck_id])[task_counters[truck_id]]]
            task_counters[truck_id] += 1

    def fix_task_order(self):
        truck_ids = [i.id for i in self.trucks]
        tasks_truck = {t: [] for t in truck_ids}
        tasks_order_truck = {t: [] for t in truck_ids}
        for i in range(len(self.solution)):
            tasks_truck[self.solution[i, 0]] += [i]
            tasks_order_truck[self.solution[i, 0]] += [self.solution[i, 1]]
        for truck_id, order in tasks_order_truck.items():
            fixed_order = np.argsort(order)
            for fixed in range(len(fixed_order)):
                self.solution[tasks_truck[truck_id][fixed_order[fixed]], 1] = fixed
            self.tasks_per_truck[truck_id] = len(fixed_order)

    def eval(self):
        schedule = Schedule(self.graph, self.tasks, self.trucks, self, 1)
        schedule.calculate_routes()
        # schedule.calculate_schedule()
