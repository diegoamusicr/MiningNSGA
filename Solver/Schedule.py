import pandas as pd
import numpy as np
from Objects.Truck import *
from Objects.Graph import *
import copy


class Schedule:

    def __init__(self, graph, trucks, tasks, solution, time_delta):
        self.graph = graph
        self.trucks = trucks
        self.tasks = tasks
        self.solution = solution
        self.time_delta = time_delta
        my_trucks = copy.deepcopy(self.trucks)
        my_tasks = copy.deepcopy(self.tasks)
        self.schedule = {}

        # Sort Tasks by order and add tasks to trucks
        for i in my_trucks:
            tasks_truck = np.where(solution[0, :] == i.id).sort()
            i.add_multiple_tasks(my_tasks[tasks_truck])

        def get_fixed_times(node_id):
            node = graph.nodes[node_id]
            if node.type in [NodeType.BNCH, NodeType.CLEA]:
                time = Truck.time_spot + Truck.time_load
            elif node.type in [NodeType.DUMP, NodeType.CRSH]:
                time = Truck.time_spot + Truck.time_unload
            else:
                time = 0
            return time

        # calculate time for truck

        for i in my_trucks:
            time_periods = np.array([])
            for j in i.my_tasks:
                load_node_pos = j.route.index(j.node_load_id)
                for k in range(len(j.route) - 1):
                    # call distance,friction and slope in edge)
                    distance = graph.edges[j.route[k], j.route[k + 1]].distance
                    friction = graph.edges[j.route[k], j.route[k + 1]].friction
                    slope = G.edges[j.route[k], j.route[k + 1]].slope
                    time_travel = distance/i.avg_speed[str(friction+slope) + 'E' if k < load_node_pos else 'L']
                    travel_append = np.arange(len(time_periods),
                                              int(time_travel/timeframe) + len(time_periods), timeframe)
                    time_periods = np.append(time_periods, travel_append)
                    for l in travel_append:
                        if len(schedule[travel_append[l]][1]) == 0:
                            # First second of the first trip from any node to any node
                            schedule[travel_append[l]][0] = {'trucks': {i.id: np.array(route[k], route[k+1],
                                                                                       l/max(travel_append), 'E' if k < load_node_pos else 'L')}}
                            schedule[travel_append[l]][1] = 'C/W'
                            schedule[travel_append[l]][2] = [[graph.nodes[np.where(graph.nodes.n_type == 'DUMP')].n_id],
                                                             ['D/R' for _ in [np.where(graph.nodes.n_type == 'DUMP')]]]
                            schedule[travel_append[l]][3] = [[graph.nodes[np.where(graph.nodes.n_type == 'CLEA')].n_id],
                                                             ['CL/R' for _ in [np.where(graph.nodes.n_type == 'CLEA')]]]
                            schedule[travel_append[l]][4] = [[graph.nodes[np.where(graph.nodes.n_type == 'BNCH')].n_id],
                                                             ['B/R' for _ in [np.where(graph.nodes.n_type == 'BNCH')]]]

                        else:
                            # Keep the status of the last second since this is a travel time and there are no changes in the work stations

                            schedule[travel_append[l]][0] = {'trucks': {
                                i.id: np.array(route[k], route[k + 1], l / max(travel_append),
                                               'E' if k < load_node_pos else 'L')}}
                            schedule[travel_append[l]][1] = schedule[travel_append[l-1]][1]
                            schedule[travel_append[l]][2] = schedule[travel_append[l-1]][2]
                            schedule[travel_append[l]][3] = schedule[travel_append[l-1]][3]
                            schedule[travel_append[l]][4] = schedule[travel_append[l-1]][4]
                        # add fixed and  waiting time if node is a load/unload node
                    if j.route[k+1].n_type in [NodeType.BNCH, NodeType.CLEA, NodeType.DUMP, NodeType.CRSH]:
                        # analyze if there is waiting time
                        counter_trucks_w = 0
                        index=-1
                        # counting trucks waiting in line to be loaded/ ask if optimized?

                        for t in list(schedule[travel_append[len(travel_append)]][0]): # count in the next second after finishing travelling all the trucks waiting in line for loading/unloading
                            if schedule[travel_append[len(travel_append)]][0][t][1] == route[k + 1] \
                                    and schedule[travel_append[len(travel_append)]][0][t][3] == ('LD' or 'ULD'):
                                index = t

                            if schedule[travel_append[len(travel_append)]][0][t][1] == route[k + 1] \
                                    and schedule[travel_append[len(travel_append)]][0][t][3] == ('W/LD' or 'W/ULD'):
                                counter_trucks_w = counter_trucks_w + 1
                        if index != -1:  # counting time until loading finishes and add time to waiting append
                            counter_trucks_w = get_fixed_times(j.route[k + 1]) * (
                                    (1-schedule[travel_append[len(travel_append)]][0][index][2]) + counter_trucks_w)

                        waiting_append = np.arange(len(time_periods),
                                                 int(counter_trucks_w/timeframe) + len(time_periods), timeframe)

                        if graph.nodes[j.route[k+1]].type in [NodeType.BNCH, NodeType.CLEA]:
                            # ask if loading or unloading node ( BNCH/CLEA vs CRSH/DUMP)
                            for l in waiting_append:
                                # Change status of truck to waiting for loading('W/LD')
                                schedule[waiting_append[l]][1] = {'trucks': {i.id: np.array(route[k], route[k + 1], l / max(waiting_append), 'W/LD')}}
                                schedule[waiting_append[l]][2] = schedule[waiting_append[l - 1]][2]
                                schedule[waiting_append[l]][3] = schedule[waiting_append[l - 1]][3]
                                schedule[waiting_append[l]][4] = schedule[waiting_append[l - 1]][4]

                        else:
                            for l in waiting_append:
                                schedule[waiting_append[l]][1] = {'trucks': {i.id: np.array(route[k], route[k + 1], l / max(waiting_append), 'W/ULD')}}
                                schedule[waiting_append[l]][2] = schedule[waiting_append[l-1]][2]
                                schedule[waiting_append[l]][3] = schedule[waiting_append[l - 1]][3]
                                schedule[waiting_append[l]][4] = schedule[waiting_append[l - 1]][4]

                        time_periods = np.append(time_periods, waiting_append)
                        fixed_append = np.arange(len(time_periods), get_fixed_times(j.route[k + 1]) + len(time_periods), timeframe)
                         #create fixed time if it truck is located at a load/unload node

                        #cambiar 2 ifs por 4 elifs
                            #define if whether the destiny node is a loading or unloading node

                        #CORREGIR DE 1 LINEA A 4 LINEAS PARA HACER EL UPDATE

                        # if loading node, define if BNCH or CLEA
                        if graph.nodes[j.route[k+1]].type =='BNCH':
                            #if BNCH, update schedule
                            for l in fixed_append:
                                schedule[fixed_append[l]][0] = {'trucks':{i.id: np.array(route[k], route[k + 1], l/max(fixed_append),'LD')}}
                                schedule[fixed_append[l]][1] = schedule[fixed_append[l - 1]][1]
                                schedule[fixed_append[l]][2] = schedule[fixed_append[l - 1]][2]
                                schedule[fixed_append[l]][3] = schedule[fixed_append[l - 1]][3]
                                for a in schedule[fixed_append[l]][4]:
                                    if schedule[fixed_append[l]][4][a][0]==j.node_load_id: #if loading node of the route == current node of the route, update, maintain otherwise
                                        schedule[fixed_append[l]][4][a][1]='B/W'
                                    else:

                                        schedule[fixed_append[l]][4][a]=schedule[fixed_append[l-1]][4][a]

                        elif graph.nodes[j.route[k+1]].type == 'CLEA':

                            for l in fixed_append:
                                schedule[fixed_append[l]][0] = {'trucks': {i.id: np.array(route[k], route[k + 1], l / max(fixed_append), 'LD')}}
                                schedule[fixed_append[l]][1] = schedule[fixed_append[l-1]][1]
                                schedule[fixed_append[l]][2] = schedule[fixed_append[l - 1]][2]
                                schedule[fixed_append[l]][4] = schedule[fixed_append[l - 1]][4]
                                for a in schedule[fixed_append[l]][3]:
                                    if schedule[fixed_append[l]][3][a][0] == j.node_load_id:
                                        # if loading node of the route == current node of the route, update, maintain otherwise
                                        schedule[fixed_append[l]][3][a][1] = 'C/W'
                                    else:
                                        schedule[fixed_append[l]][3][a] = schedule[fixed_append[l - 1]][3][a]

                        elif graph.nodes[j.route[k+1]].type == 'CRSH':
                            for l in fixed_append:
                                schedule[fixed_append[l]][0] = {'trucks': {i.id: np.array(route[k], route[k + 1], l / max(fixed_append), 'ULD')}}
                                schedule[fixed_append[l]][1] = 'C/W'
                                schedule[fixed_append[l]][2] = schedule[fixed_append[l - 1]][2]
                                schedule[fixed_append[l]][4] = schedule[fixed_append[l - 1]][4]

                        elif graph.nodes[j.route[k+1]].type =='DUMP':
                            for l in fixed_append:
                                schedule[fixed_append[l]][0] = {'trucks': {i.id: np.array(route[k], route[k + 1], l / max(fixed_append), 'ULD')}}
                                schedule[fixed_append[l]][1] = schedule[fixed_append[l-1]][1]
                                schedule[fixed_append[l]][3] = schedule[fixed_append[l - 1]][3]
                                schedule[fixed_append[l]][4] = schedule[fixed_append[l - 1]][4]
                                for a in schedule[fixed_append[l]][2]:
                                    if schedule[fixed_append[l]][2][a][0] == j.node_load_id:
                                        # if loading node of the route == current node of the route, update, maintain otherwise
                                        schedule[fixed_append[l]][2][a][1] = 'C/W'
                                    else:
                                        schedule[fixed_append[l]][2][a] = schedule[fixed_append[l - 1]][2]


