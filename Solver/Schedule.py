import pandas as pd
import numpy as np
from Objects.Truck import *
from Objects.Graph import *
import copy


route = [2, 0, 5, 8, 7]
               L     U
#Schedule param: graph, trucks, tasks, solution
#my_trucks --> self.trucks = copy.deepcopy(trucks)
#'' lo mismo para tasks
trucks = []
tasks = np.array([])
my_trucks = copy.deepcopy(trucks)
my_tasks = copy.deepcopy(tasks)
#add tasks to trucks used in solution

#Ordenar por orden(segundo valor)
for i in my_trucks:
    tasks_truck = np.where(solution[0,:] == i.id)
    i.add_multiple_tasks(tasks[tasks_truck])

def get_fixed_times(node_id):
    node = graph.nodes[node_id]
    if node.type in [NodeType.BNCH, NodeType.CLEA]:
        time = Truck.time_spot + Truck.time_load
    elif node.type in [NodeType.DUMP, NodeType.CRSH]:
        time = Truck.time_spot + Truck.time_unload
    else:
        time = 0
    return time



#calculate time for truck
timeframe = input('Please select time frames in seconds') #self.time_delta
nodes_truck = np.array([])

schedule = {}

for i in my_trucks:
    time_periods = np.array([])
    for j in i.my_tasks:
        load_node_pos = j.route.index(j.node_load_id)
        for k in range(len(j.route) - 1):
            #call distance,friction and slope in edge)
            distance = G.edges[j.route[k], j.route[k + 1]].distance
            friction = G.edges[j.route[k], j.route[k + 1]].friction
            slope = G.edges[j.route[k], j.route[k + 1]].slope
            time_travel = distance/i.avg_speed[str(friction+slope) + 'E' if k < load_node_pos else 'L']
            travel_append = np.arange(len(time_periods), int(time_travel/timeframe) + len(time_periods), timeframe)
            fixed_append = np.arange(len(travel_append), get_fixed_times(j.route[k + 1]) + len(travel_append), timeframe)

            time_periods = np.append(time_periods, travel_append)
            time_periods = np.append(time_periods, fixed_append)

            
            #considerar viaje y descarga/carga por iteracion
            for l in travel_append:
                schedule[travel_append[l]] = {i.id: np.array(route[k], route[k+1], l/max(travel_append), 'E' if k < load_node_pos else 'L')}
            for l in fixed_append:
                if len(fixed_append) > (Truck.time_spot + Truck.time_unload):
                    schedule[fixed_append[l]] = {i.id: np.array(route[k], route[k+1], 'LD', j.route)}
                else:
                    schedule[fixed_append[l]] = {i.id: np.array(route[k], route[k+1], 'ULD', j.route)}

#schedule[i] = [{id:[]}, is_crsh_busy, {id:is_dump_busy}, {id:is_}, ]
#corregir indexacion

def get_scores (schedule, my_trucks):
    total_time = max(list(schedule))
    crusher_counter = 0
    for i in schedule:
        for j in schedule[i]:
            crusher_counter = int(np.where(schedule[i][j][2]=='LD')) + crusher_counter
    #self.total_time = xx
    #self.crusher_prod_time = xx

