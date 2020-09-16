import pandas as pd
import numpy as np
from Objects.Truck import *
from Objects.Graph import *
import copy

class Schedule:

    def __init__(self, graph, trucks,tasks,solution,time_delta)
        self.graph=graph
        self.trucks=trucks
        self.tasks=tasks
        self.solution=solution
        self.time_delta=time_delta
        my_trucks=copy.deepcopy(self.trucks)
        my_tasks=copy.deepcopy(self.tasks)




        #Ordenar por orden(segundo valor)
        for i in my_trucks:
            tasks_truck = np.where(solution[0,:] == i.id).sort()
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
                    time_periods = np.append(time_periods, travel_append)
                    for l in travel_append:
                        if len(schedule[travel_append[l]][1])==0: #First second of the first trip from any node to any node
                            schedule[travel_append[l]] = [{'trucks':{i.id:np.array(route[k], route[k+1], l/max(travel_append),
                                        'E' if k < load_node_pos else 'L')}},'C/R',
                                                             [[G.nodes.[np.where(G.nodes.n_type=='DUMP'].n_id],
                                                             ['D/R' for _ in [np.where(G.nodes.n_type=='DUMP']]],[[G.nodes.[np.where(G.nodes.n_type=='CLEA')].n_id],['CL/R' for _ in [np.where(G.nodes.n_type=='CLEA')]]],
                                                                [[G.nodes.[np.where(G.nodes.n_type=='BNCH')].n_id],['B/R' for _ in [np.where(G.nodes.n_type=='BNCH')]]]]
                        else: #Keep the status of the last second since this is a travel time and there are no changes in the work stations
                            schedule[travel_append[l]] = [{'trucks':{i.id:np.array(route[k], route[k + 1], l / max(travel_append),
                                         'E' if k < load_node_pos else 'L')}}, schedule[travel_append[l-1][1]],schedule[travel_append[l-1][2]],schedule[travel_append[l-1][3]],schedule[travel_append[l-1][4]]]


                            # add fixed and  waiting time if node is a load/unload node
                    if j.route[k+1].n_type in [NodeType.BNCH,NodeType.CLEA,NodeType.DUMP,NodeType.CRSH]: #analyze if there is waiting/fixed time according to where the truck is located at a loading/unloading node or not

                        # analyze if there is waiting time
                        counter_trucks_w = 0
                        try:  # counting trucks waiting in line to be loaded/ ask if optimized?

                            for _ in list(schedule[travel_append[len(travel_append)]][0]): #count in the next second after finishing travelling all the trucks waiting in line for loading/unloading
                                if  schedule[travel_append[len(travel_append)]][0][_][1] == route[k + 1] and schedule[travel_append[len(travel_append)]][0][_][3]==('LD' or 'ULD')
                                    index=_
                                if schedule[travel_append[len(travel_append)]][0][_][1] == route[k + 1] and schedule[travel_append[len(travel_append)]][0][_][3] == ('W/LD' or  'W/ULD') :
                                    counter_trucks_w = counter_trucks_w + 1
                        except:
                            pass
                        try:  # counting time until loading finishes and add time to waiting append
                            counter_trucks_w =  get_fixed_times(j.route[k + 1])*((1 -schedule[travel_append[len(travel_append)]][0][index][2]) + counter_trucks_w)
                        except:
                            pass

                        waiting_append=np.arange(len(time_periods), int(counter_trucks_w/timeframe) + len(time_periods), timeframe)
                        if get_fixed_times(j.route[k+1])>Truck.time_spot+Truck.time_unload:
                            # ask if loading or unloading node ( BNCH/CLEA vs CRSH/DUMP)
                            for l in waiting_append:

                                # Change status of truck to waiting for loading('W/LD')

                                schedule[waiting_append[l]] = [{'trucks': {i.id: np.array(route[k], route[k + 1], l / max(waiting_append),'W/LD')}},
                                                               schedule[waiting_append[l-1]][1],schedule[waiting_append[l-1]][2],
                                                               schedule[waiting_append[l-1]][3],schedule[waiting_append[l-1]][4]]


                        else:
                            for l in waiting_append:
                                schedule[waiting_append[l]] = [{'trucks': {
                                    i.id: np.array(route[k], route[k + 1], l / max(waiting_append), 'W/ULD')}},
                                                               schedule[waiting_append[l - 1]][1],
                                                               schedule[waiting_append[l - 1]][2],
                                                               schedule[waiting_append[l - 1]][3],
                                                               schedule[waiting_append[l - 1]][4]]

                        fixed_append= np.arange(len(time_periods), get_fixed_times(j.route[k + 1]) + len(time_periods), timeframe) #create fixed time if it truck is located at a load/unload node

                            #define if whether the destiny node is a loading or unloading node
                            if get_fixed_times(j.route[k+1])>Truck.time_spot+Truck.time_unload:
                                # if loading node, define if BNCH or CLEA
                                if j.route[k+1].n_type =='BNCH':
                                    #if BNCH, update schedule
                                    for l in fixed_append:
                                        schedule[fixed_append[l]][0][1][2][3] = [{'trucks':{i.id: np.array(route[k], route[k + 1], l/max(fixed_append),'LD')}},
                                            schedule[fixed_append[l - 1]][1],
                                            schedule[fixed_append[l - 1]][2],
                                            schedule[fixed_append[l - 1]][3]]
                                        #optimize
                                        schedule[fixed_append[l]][4]=[schedule[fixed_append[l]][4][x][1]='B/W' if schedule[fixed_append[l-1]][4][x][0]==j.node_load_id  for x in schedule[fixed_append[l-1]][4][x][0]]

                                else:
                                    for l in fixed_append:
                                        schedule[fixed_append[l]][0][1][2][4] = [{'trucks': {
                                            i.id: np.array(route[k], route[k + 1], l / max(fixed_append), 'LD')}},
                                                                                 schedule[fixed_append[l - 1]][1],
                                                                                 schedule[fixed_append[l - 1]][2],
                                                                                 schedule[fixed_append[l - 1]][4]]
                                        # optimize
                                        schedule[fixed_append[l]][3] = [schedule[fixed_append[l]][3][x][1] = 'CL/W' if
                                        schedule[fixed_append[l - 1]][3][x][0] == j.node_load_id
                                        for x in schedule[fixed_append[l - 1]][3][x][0]]

                            else:#change status for CRSH and DUMPS
                                if j.route[k + 1].n_type == 'CRSH':
                                    # if CRSH, update schedule for crusher and truck, maintain for other arrays
                                    for l in fixed_append:
                                        schedule[fixed_append[l]][0][2][3][4] = [{'trucks': {
                                            i.id: np.array(route[k], route[k + 1], l / max(fixed_append), 'ULD')}},
                                                                                 schedule[fixed_append[l - 1]][2],
                                                                                 schedule[fixed_append[l - 1]][3],
                                                                                 schedule[fixed_append[l - 1]][4]]
                                        # optimize
                                        schedule[fixed_append[l]][1] = 'C/W'

                                else:
                                    #if DUMP update schedule for dump array and truck, maintain for other arrays
                                    for l in fixed_append:
                                        schedule[fixed_append[l]][0][1][3][4] = [{'trucks': {
                                            i.id: np.array(route[k], route[k + 1], l / max(fixed_append), 'ULD')}},
                                                                                 schedule[fixed_append[l - 1]][1],
                                                                                 schedule[fixed_append[l - 1]][3],
                                                                                 schedule[fixed_append[l - 1]][4]]
                                        # optimize
                                        schedule[fixed_append[l]][2] = [schedule[fixed_append[l]][2][x][1] = 'D/W' if
                                        schedule[fixed_append[l - 1]][2][x][0] == j.node_load_id
                                        for x in schedule[fixed_append[l - 1]][2][x][0]]


                        #repeat for fixed time




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

