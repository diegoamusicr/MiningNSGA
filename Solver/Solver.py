import numpy as np
import math
from Objects.Task import *
from Objects.Graph import *
from Solver.Solution import *


class NSGASolver:
    def __init__(self, graph, trucks_array, objectives_array):
        self.graph = graph
        self.trucks = trucks_array
        self.objectives = objectives_array
        self.truck_load = min([i.capacity for i in self.trucks])
        self.crusher_node_id = -1
        self.dump_node_id = []
        self.dump_node_count = []
        self.dump_strategy = 0
        self.task_array_strategy = 0
        self.get_types_id()

    def get_types_id(self):
        for i in self.graph.nodes:
            if i.type == NodeType.CRSH:
                self.crusher_node_id = i.id
            elif i.type == NodeType.DUMP:
                self.dump_node_id += [i.id]
                self.dump_node_count += [0]

    def get_available_dump_id(self):
        if self.dump_strategy == 0:  # Round Robin per dump
            sorted_idx = np.argsort(self.dump_node_count)
            min_node_pos = 0
            min_node_id = self.dump_node_id[sorted_idx[min_node_pos]]
            while min_node_pos < len(sorted_idx) and \
                    self.graph.nodes[min_node_id].load + self.truck_load > self.graph.nodes[min_node_id].capacity:
                if min_node_pos == len(sorted_idx)-1:
                    raise Exception('All Dump Nodes are full.')
                min_node_pos += 1
                min_node_id = self.dump_node_id[sorted_idx[min_node_pos]]
            self.dump_node_count[sorted_idx[min_node_pos]] += 1
            self.graph.nodes[min_node_id].load += self.truck_load
            return min_node_id

        elif self.dump_strategy == 1:  # Until full
            min_node_pos = 0
            min_node_id = self.dump_node_id[min_node_pos]
            while min_node_pos < len(self.dump_node_id) and \
                    self.graph.nodes[min_node_id].load + self.truck_load > self.graph.nodes[min_node_id].capacity:
                if min_node_pos == len(self.dump_node_id)-1:
                    raise Exception('All Dump Nodes are full.')
                min_node_pos += 1
                min_node_id = self.dump_node_id[min_node_pos]
            self.graph[min_node_id].load += self.truck_load
            return min_node_id

        return -1

    def generate_task_array(self):
        task_array = np.array([]).astype(Task)
        tasks_per_objective = []
        tasks_quantities = []
        for objective in self.objectives:
            tasks_quantity = math.ceil(objective.work_tons / self.truck_load)
            if self.graph.nodes[objective.work_node_id].type == NodeType.BNCH:
                tasks_objective = [Task(objective.work_node_id, self.crusher_node_id) for _ in range(tasks_quantity)]
            elif self.graph.nodes[objective.work_node_id].type == NodeType.CLEA:
                tasks_objective = [Task(objective.work_node_id, self.get_available_dump_id()) for _ in
                                   range(tasks_quantity)]
            else:
                raise Exception('Objectives should focus Nodes of type BNCH (Bench) or CLEA (Clearance)')
            tasks_per_objective += [tasks_objective]
            tasks_quantities += [tasks_quantity]

        if self.task_array_strategy == 0:  # Round Robin per objective
            max_tasks_number = max(tasks_quantities)
            for task_number in range(max_tasks_number):
                for tasks in tasks_per_objective:
                    if task_number < len(tasks):
                        task_array = np.concatenate((task_array, [tasks[task_number]]))

        elif self.task_array_strategy == 1:  # Join tasks in order of objectives
            for tasks in tasks_per_objective:
                task_array = np.concatenate((task_array, tasks))

        return task_array
