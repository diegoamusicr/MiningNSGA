import pandas as pd
import numpy as np
from Objects.Truck import *
from Objects.Graph import *
import copy


class Schedule:

    def __init__(self, graph, trucks, tasks, solution, time_delta):
        self.graph = graph
        self.trucks = copy.deepcopy(trucks)
        self.tasks = copy.deepcopy(tasks)
        self.solution = solution
        self.time_delta = time_delta
        self.schedule = {}
        self.time_crsh_idle = 0
        self.time_total = 0
        self.assign_tasks()

    # Sort Tasks by order and add tasks to trucks
    def assign_tasks(self):
        for truck in self.trucks:
            assigned_tasks_idx = self.solution.solution[:, 0] == truck.id
            tasks_truck = np.where(assigned_tasks_idx)[0][np.argsort(self.solution.solution[assigned_tasks_idx][:, 1])]
            truck.tasks_ids = tasks_truck
            truck.add_multiple_tasks(self.tasks[tasks_truck])

    def calculate_routes(self):
        for truck in self.trucks:
            initial_node = truck.start_node
            for task in truck.tasks:
                task.node_start_id = initial_node
                task.route = np.concatenate((self.graph.paths[initial_node, task.node_load_id],
                                             self.graph.paths[task.node_load_id, task.node_unload_id][1:]))
                initial_node = task.node_unload_id

    def get_fixed_times(self, node_id):
        node = self.graph.nodes[node_id]
        if node.type in [NodeType.BNCH, NodeType.CLEA]:
            time = Truck.time_spot + Truck.time_load
        elif node.type in [NodeType.DUMP, NodeType.CRSH]:
            time = Truck.time_spot + Truck.time_unload
        else:
            time = 0
        return time

    # calculate time for truck

    # decide if whether route includes ID or node itself,
    def calculate_schedule(self):
        for i in self.trucks:
            time_periods = np.array([])
            for j in i.tasks:
                load_node_pos = j.node_load_id
                for k in range(0, len(j.route) - 1):
                    # call distance,friction and slope in edge)
                    distance = self.graph.edges[j.route[k].id, j.route[k + 1].id].distance
                    friction = self.graph.edges[j.route[k].id, j.route[k + 1].id].friction
                    slope = self.graph.edges[j.route[k].id, j.route[k + 1].id].slope
                    time_travel = distance/i.avg_speed[str(friction+slope) + 'E' if k < load_node_pos else 'L']*3600
                    travel_append = np.arange(len(time_periods),
                                              int(time_travel/self.time_delta) + len(time_periods), self.time_delta)
                    time_periods = np.append(time_periods, travel_append)
                    for l in travel_append:
                        if len(self.schedule) == 0:
                            # First second of the first trip from any node to any node
                            dump_list = []
                            clea_list = []
                            bnch_list = []
                            for a in self.graph.nodes:
                                if a.type == NodeType.DUMP:
                                    dump_list.append([a.id, 'D/R'])
                                elif a.type == NodeType.CLEA:
                                    clea_list.append([a.id, 'CL/R'])
                                elif a.type == NodeType.BNCH:
                                    bnch_list.append([a.id, 'B/R'])
                            self.schedule = {l: [{'trucks': {i.id: np.array([j.route[k].id, j.route[k + 1].id,
                                                                        l / max(travel_append),
                                                                        'E' if k < load_node_pos else 'L'])}},'C/R',dump_list,clea_list,bnch_list]}


                        else:

                            if l not in self.schedule:# Keep the status of the last second since this is a travel time and there are no changes in the work stations

                                self.schedule[l] = [{'trucks': {
                                    i.id: np.array([j.route[k].id, j.route[k + 1].id, l / max(travel_append),
                                        'E' if k < load_node_pos else 'L'])}}, self.schedule[travel_append[l-1]][1], self.schedule[travel_append[l-1]][2],
                                            self.schedule[travel_append[l-1]][3], self.schedule[travel_append[l-1]][4]]
                            else:
                                self.schedule[l][0]['trucks'][i.id] = np.array([j.route[k].id, j.route[k + 1].id, l / max (travel_append),
                                        'E' if k < load_node_pos else 'L'])


                        # add fixed and  waiting time if node is a load/unload node
                    if j.route[k+1].type in [NodeType.BNCH, NodeType.CLEA, NodeType.DUMP, NodeType.CRSH]:
                        # analyze if there is waiting time
                        counter_trucks_w = 0
                        index=-1
                        # counting trucks waiting in line to be loaded/ ask if optimized?

                        for t in list(self.schedule[len(travel_append)-1][0]['trucks']): # count in the next second after finishing travelling all the trucks waiting in line for loading/unloading
                            if int(self.schedule[len(travel_append)-1][0]['trucks'][t][1]) == j.route[k + 1].id and self.schedule[len(travel_append)-1][0]['trucks'][t][3] in ['LD','ULD']:
                                index = t

                            if int(self.schedule[travel_append[len(travel_append)-1]][0]['trucks'][t][1]) == j.route[k + 1].id and self.schedule[travel_append[len(travel_append)-1]][0]['trucks'][t][3] in ['W/LD','W/ULD']:
                                counter_trucks_w = counter_trucks_w + 1
                        if index != -1:  # counting time until loading finishes and add time to waiting append
                            counter_trucks_w = self.get_fixed_times(j.route[k + 1]) * ((1-self.schedule[travel_append[len(travel_append)]][0][index][2]) + counter_trucks_w)

                        waiting_append = np.arange(len(time_periods),
                                                 int(counter_trucks_w/self.time_delta) + len(time_periods), self.time_delta)

                        if j.route[k+1].type in [NodeType.BNCH, NodeType.CLEA]:
                            # ask if loading or unloading node ( BNCH/CLEA vs CRSH/DUMP)
                            for l in waiting_append:
                                # Change status of truck to waiting for loading('W/LD')
                                if l not in self.schedule:

                                    self.schedule[waiting_append[l]] = [{'trucks': {i.id: np.array(j.route[k].id, j.route[k + 1].id, l / max(waiting_append), 'W/LD')}}, self.schedule[waiting_append[l - 1]][2], self.schedule[waiting_append[l - 1]][3], self.schedule[waiting_append[l - 1]][4]]

                                else:

                                    self.schedule[l][0]['trucks'][i.id] = np.array(
                                        [j.route[k].id, j.route[k + 1].id, l / max(travel_append),
                                         'W/LD'])


                        else:
                            for l in waiting_append:

                                if l not in self.schedule:

                                    self.schedule[waiting_append[l]] = [{'trucks': {i.id: np.array(j.route[k].id, j.route[k + 1].id, l / max(waiting_append), 'W/ULD')}}, self.schedule[waiting_append[l - 1]][2], self.schedule[waiting_append[l - 1]][3], self.schedule[waiting_append[l - 1]][4]]

                                else:
                                    self.schedule[l][0]['trucks'][i.id] = np.array(
                                        [j.route[k].id, j.route[k + 1].id, l / max(travel_append),
                                         'W/ULD'])

                        time_periods = np.append(time_periods, waiting_append)
                        fixed_append = np.arange(len(time_periods), self.get_fixed_times(j.route[k + 1].id) + len(time_periods), self.time_delta)
                         #create fixed time if it truck is located at a load/unload node

                        #falta corregir sobre escritura
                        # if loading node, define if BNCH or CLEA
                        if j.route[k+1].type == NodeType.BNCH:
                            #if BNCH, update schedule
                            for l in fixed_append:

                                if l not in self.schedule:
                                    self.schedule[l] = [{'trucks': {
                                        i.id: np.array([j.route[k].id, j.route[k + 1].id, l / max(fixed_append),'LD'])}}, self.schedule[l - 1][1], self.schedule[l - 1][2],
                                        self.schedule[l - 1][3], self.schedule[l - 1][4]]

                                    counter = 0

                                    for a in self.schedule[l][4]:

                                        if a[0] == j.node_load_id:
                                            #if loading node of the route == current node of the route, update, maintain otherwise
                                            self.schedule[l][4][counter][1] = 'B/W'
                                        counter = counter+1

                                else:

                                    self.schedule[l][0]['trucks'][i.id] = np.array(
                                        [j.route[k].id, j.route[k + 1].id, l / max(travel_append),
                                         'LD'])
                                    counter=0
                                    for a in self.schedule[l][4]:

                                        if a[0] == j.node_load_id:
                                            # if loading node of the route == current node of the route, update, maintain otherwise
                                            self.schedule[l][4][counter][1] = 'B/W'
                                        counter = counter + 1

                        elif j.route[k+1].type == NodeType.CLEA:

                            for l in fixed_append:

                                if l not in self.schedule[l]:

                                    self.schedule[l] = [{'trucks': {
                                        i.id: np.array([j.route[k].id, j.route[k + 1].id, l / max(fixed_append),
                                                        'LD'])}},
                                        self.schedule[l - 1][1], self.schedule[l - 1][2], self.schedule[l - 1][3], self.schedule[l - 1][4]]

                                    counter = 0

                                    for a in self.schedule[l][3]:
                                        if a[0] == j.node_load_id:
                                            # if loading node of the route == current node of the route, update, maintain otherwise
                                            self.schedule[l][3][counter][1] = 'CL/W'
                                        counter = counter + 1
                                else:

                                    self.schedule[l][0]['trucks'][i.id] = np.array(
                                        [j.route[k].id, j.route[k + 1].id, l / max(travel_append),
                                         'LD'])
                                    counter = 0

                                    for a in self.schedule[l][3]:
                                        if a[0] == j.node_load_id:
                                            # if loading node of the route == current node of the route, update, maintain otherwise
                                            self.schedule[l][3][counter][1] = 'CL/W'
                                        counter = counter + 1

                        elif j.route[k+1].type == NodeType.CRSH:

                            if l not in self.schedule[l]:

                                for l in fixed_append:
                                    self.schedule[l] = [{'trucks': {
                                        i.id: np.array([j.route[k].id, j.route[k + 1].id, l / max(fixed_append),
                                                        'ULD'])}},'C/W', self.schedule[l - 1][2], self.schedule[l - 1][3],
                                                            self.schedule[l - 1][4]]

                            else:

                                self.schedule[l][0]['trucks'][i.id] = np.array(
                                    [j.route[k].id, j.route[k + 1].id, l / max(travel_append),
                                     'ULD'])

                                self.schedule[l][1] = 'C/W'

                        elif j.route[k+1].type == NodeType.DUMP:

                            if l not in self.schedule[l]:

                                for l in fixed_append:

                                    self.schedule[l] = [{'trucks': {
                                        i.id: np.array([j.route[k].id, j.route[k + 1].id, l / max(fixed_append),
                                                        'ULD'])}},
                                        self.schedule[l - 1][1], self.schedule[l - 1][2],
                                        self.schedule[l - 1][3], self.schedule[l - 1][4]]

                                    counter = 0

                                    for a in self.schedule[l][2]:

                                        if a[0] == j.node_unload_id:
                                            # if loading node of the route == current node of the route, update, maintain otherwise
                                            self.schedule[l][2][counter][1] = 'D/W'

                                        counter = counter + 1
                            else:

                                self.schedule[l][0]['trucks'][i.id] = np.array(
                                    [j.route[k].id, j.route[k + 1].id, l / max(travel_append),
                                     'ULD'])

                                counter = 0

                                for a in self.schedule[l][2]:
                                    if a[0] == j.node_unload_id:
                                        # if loading node of the route == current node of the route, update, maintain otherwise
                                        self.schedule[l][2][counter][1] = 'D/W'

                                    counter = counter + 1