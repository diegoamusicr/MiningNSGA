import numpy as np
import random


class Objective:
    def __init__(self, work_node_id, work_tons):
        self.work_node_id = work_node_id
        self.work_tons = work_tons
        self.completed = False


class Solution:

    def __init__(self, task_array, trucks_array):
        self.tasks = task_array
        self.trucks = trucks_array
        self.trucks_quantity = len(self.trucks)
        self.solution = np.empty((len(self.tasks), 2), dtype=int)
        self.tasks_per_truck = {}

    def generate_random_solution(self):
        self.solution = np.empty((len(self.tasks), 2), dtype=int)
        truck_ids = [i.id for i in self.trucks]
        task_counters = dict(zip(truck_ids, [0] * self.trucks_quantity))
        task_orders_random = dict(zip(truck_ids, [] * self.trucks_quantity))
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
