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
        self.time_trck_idle= 0
        self.trucks_tasks_assigned = 0
        self.assign_tasks()
        self.speed_reduction = 5 #analyze if this should be fixed or input of the user
        self.trucks_reduced_speed = np.array([])

    # Sort Tasks by order and add tasks to trucks
    def assign_tasks(self):
        counter = 0
        for truck in self.trucks:
            assigned_tasks_idx = self.solution.solution[:, 0] == truck.id
            tasks_truck = np.where(assigned_tasks_idx)[0][np.argsort(self.solution.solution[assigned_tasks_idx][:, 1])]
            truck.tasks_ids = tasks_truck
            truck.add_multiple_tasks(self.tasks[tasks_truck])
        for truck in self.trucks:
            if len(truck.tasks) > counter:
                counter = len(truck.tasks)
        self.trucks_tasks_assigned = counter

    def trucks_data(self):
        for truck in self.trucks:
            truck.get_truck_data()


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
        colision = False
        for i in self.trucks:
            #create schedule for each truck
            time_periods = np.array([])
            for j in i.tasks:
                #create schedule for each task of the i truck
                load_node_pos = j.node_load_id
                for k in range(0, len(j.route) - 1):
                    #create schedule for each route of the j taks of the i truck

                    # call distance,friction and slope in edge)
                    distance = self.graph.edges[j.route[k], j.route[k + 1]].distance
                    friction = self.graph.edges[j.route[k], j.route[k + 1]].friction
                    slope = self.graph.edges[j.route[k], j.route[k + 1]].slope
                    name=str(round((0 if friction+slope <= 0 else (friction+slope)),2))
                    state='E' if k < load_node_pos else 'L'
                    time_travel = distance/int(i.avg_speed[i.model].loc[name+state])*3600
                    travel_append = np.arange(len(time_periods),
                                              int(time_travel/self.time_delta) + len(time_periods), self.time_delta)

                    for l in travel_append:
                        #create schedule for each second the i truck must travel in the k,k+1 route of the j task

                        if len(self.schedule) == 0:
                            # First second of the first trip from any node to any node, creates schedule for the first time
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
                            self.schedule = {l: [{'trucks': {i.id: np.array([j.route[k], j.route[k + 1],
                                                                        l / max(travel_append),
                                                                        'E' if k < load_node_pos else 'L'])}},'C/R',dump_list,clea_list,bnch_list]}


                        else:
                            #updates schedule once the first key is created


                            if l not in self.schedule:
                                #If second does not exists in schedule, update schedule for the trucks dictionary, maintain status of the last second for the other parameters

                                self.schedule[l] = [{'trucks': {
                                    i.id: np.array([j.route[k], j.route[k + 1], l / max(travel_append),
                                        'E' if k < load_node_pos else 'L'])}}, self.schedule[l-1][1], self.schedule[l-1][2],
                                            self.schedule[l-1][3], self.schedule[l-1][4]]
                            else:
                                #if second does exists in schedule, define if i truck is not overlapping over any other truck before
                                trucks_in_route = np.array([])

                                for a in self.schedule[l][0]['trucks']:

                                    # iterate the trucks dictionary over the first travel second to compare if there are trucks overlapping in
                                    # the same route, same direction and without proper distancing (distance policy * truck lenght)

                                    if self.schedule[l][0]['trucks'][a][0:2].astype(int) in np.array([j.route[k], j.route[k+1]]) and self.schedule[l][0]['trucks'][a][3] == ('E' if k < load_node_pos else 'L') and (distance * (float(self.schedule[l][0]['trucks'][a][2])) < Truck.length*Truck.distance_policy/1000):
                                        #if there are trucks overlapping append the distancing
                                        trucks_in_route = np.append(trucks_in_route, float(self.schedule[l][0]['trucks'][a][2]))

                                if len(trucks_in_route) > 1:
                                    #if trucks overlapping where found for that very second, define delay in the i truck to prevent overlap , update travel and second break former iteration with former travel append
                                    travel_time_displaced = int(((Truck.length * Truck.distance_policy) / 1000 - min(trucks_in_route)) / int(i.avg_speed[i.model].loc[name + state]) * 3600)
                                    travel_append = travel_append + travel_time_displaced

                                    break #check break position

                                for l in travel_append:
                                    #re-iterate for updated travel seconds
                                    if len(self.schedule) > 0:
                                        # this update should only overwrite schedule if schedule is already created
                                        if l not in self.schedule:
                                            # update trucks dictionary if second does not exist in schedule, maintain other parameters
                                            self.schedule[l] = [{'trucks': {
                                                i.id: np.array([j.route[k], j.route[k + 1], l / max(travel_append),
                                                                'E' if k < load_node_pos else 'L'])}},
                                                self.schedule[l - 1][1],
                                                self.schedule[l - 1][2],
                                                self.schedule[l - 1][3], self.schedule[l - 1][4]]

                                        else:
                                            #only update trucks dictionary if second does exists in schedule
                                            self.schedule[l][0]['trucks'][i.id] = np.array(
                                                [j.route[k], j.route[k + 1], l / max(travel_append),
                                                 'E' if k < load_node_pos else 'L'])


                                else:
                                    #in the case iteration was not broken, overwrite trucks dictionary for existing second in schedule
                                    self.schedule[l][0]['trucks'][i.id] = np.array(
                                        [j.route[k], j.route[k + 1], l / max(travel_append),
                                         'E' if k < load_node_pos else 'L'])

                    time_periods = np.append(time_periods, travel_append)
                    #update total seconds of the schedule for the i truck with travel time of the k,k+1 route of the j task

                    # Analyze if node is route or load/unload one
                    if self.graph.nodes[j.route[k+1]].type in [NodeType.BNCH, NodeType.CLEA, NodeType.DUMP, NodeType.CRSH]:
                        # analyze if there is waiting time
                        counter_trucks_w = 0
                        index=-1
                        # counting trucks waiting in line to be loaded/ ask if optimized?

                        for t in list(self.schedule[l][0]['trucks']):
                            # count in the next second after finishing travelling all the trucks waiting in line for loading/unloading
                            if int(self.schedule[l][0]['trucks'][t][1]) == j.route[k + 1] and \
                                    self.schedule[l][0]['trucks'][t][3] in ['LD', 'ULD']:
                                #retrieve index of the truck in the same destiny node k+1 and status is currently loading(LD) or currently unloading (ULD)
                                index = t
                                #get index of the truck currently loading or unloading in the destiny node of the i truck for the j task

                            if int(self.schedule[l][0]['trucks'][t][1]) == j.route[k + 1] and \
                                    self.schedule[l][0]['trucks'][t][3] in ['W/LD', 'W/ULD']:
                                counter_trucks_w = counter_trucks_w + 1
                                #count trucks waiting in the same destiny node k+1 and waiting for loading (W/LD) or waiting for unloading (W/ULD)

                        if index != -1:
                            # if it was a truck loading/unloading at the same destiny node, calculate total seconds that the i truck must wait to load/unload, this comes from the remaining time unloading/unloading + the waiting time of the trucks in line

                            counter_trucks_w = self.get_fixed_times(j.route[k + 1]) * (1-float(self.schedule[travel_append[len(travel_append)-1]][0]['trucks'][index][2]) + counter_trucks_w)

                            time_travel_delayed = distance/int(i.avg_speed[i.model].loc[name+state]-self.speed_reduction)*3600
                            #define delayed travel time reducing the travel speed of the truck, DELAYED TIME IS BY NATURE LARGER THAN TIME TRAVEL

                            if time_travel_delayed < time_travel + counter_trucks_w:
                                #if delayed travel time is less than time travel and time waiting, it means reducing the speed helps the overall scheduling
                                time_periods = time_periods[0:travel_append[0]-1]
                                #reduce total seconds of the i truck taking out travel seconds
                                travel_append_delayed = np.arange(len(time_periods), int(time_travel_delayed/self.time_delta) + len(time_periods), self.time_delta)
                                #create array of travel seconds with reduced speed
                                time_periods = np.append(time_periods, travel_append_delayed)
                                #update total seconds of the i truck appending the augmented travel time
                                for l in travel_append_delayed:
                                    #overwrite schedule with new travel time
                                    if l not in self.schedule:
                                        #If second not in schedule, create key of the schedule, update trucks dictionary and maintain for other parameters

                                        self.schedule[l] = [{'trucks': {
                                            i.id: np.array([j.route[k], j.route[k + 1], l / max(travel_append),
                                                            'E' if k < load_node_pos else 'L'])}},
                                            self.schedule[l - 1][1], self.schedule[l - 1][2],
                                            self.schedule[l - 1][3], self.schedule[l - 1][4]]
                                    else:
                                        #if second in schedule, only update trucks dictionary
                                        self.schedule[l][0]['trucks'][i.id] = np.array(
                                            [j.route[k], j.route[k + 1], l / max(travel_append),
                                             'E' if k < load_node_pos else 'L'])

                                counter_trucks_w = counter_trucks_w - (time_travel_delayed - time_travel)
                                #define new waiting time with new travel time due to speed reduction
                                self.trucks_reduced_speed = np.append(self.trucks_reduced_speed,
                                                                      np.array([i, len(travel_append_delayed)]))
                                #append reduced truck id and seconds delayed to asses quality of the schedule

                        waiting_append = np.arange(len(time_periods), int(counter_trucks_w/self.time_delta) + len(time_periods), self.time_delta)
                        #create waiting array with waiting time

                        if self.graph.nodes[j.route[k+1]].type in [NodeType.BNCH, NodeType.CLEA]:
                            # ask if node k+1 is a loading or unloading node ( BNCH/CLEA vs CRSH/DUMP)
                            for l in waiting_append:
                                # If node k+1 loading Node, Update schedule for waiting seconds of the i truck
                                if l not in self.schedule:
                                    #if second not in schedule, create schedule for the l second, updating truck with W/LD and maintaining for other parameters
                                    self.schedule[waiting_append[l]] = [{'trucks': {i.id: np.array(j.route[k], j.route[k+ 1], l / max(waiting_append), 'W/LD')}}, self.schedule[waiting_append[l - 1]][2], self.schedule[waiting_append[l - 1]][3], self.schedule[waiting_append[l - 1]][4]]
                                    self.time_trck_idle = self.time_trck_idle+1
                                    #accumulate idle time of the truck to asses schedule
                                else:
                                    #if second in schedule, only update truck dictionary with W/LD
                                    self.schedule[l][0]['trucks'][i.id] = np.array(
                                        [j.route[k], j.route[k + 1], l / max(travel_append),
                                         'W/LD'])
                                    self.time_trck_idle = self.time_trck_idle + 1
                                    # accumulate idle time of the truck to asses schedule
                        else:
                            # if node is unloading node
                            for l in waiting_append:

                                if l not in self.schedule:
                                    # if second not in schedule, create schedule for the l second, updating truck with W/ULD and maintaining for other parameters
                                    self.schedule[waiting_append[l]] = [{'trucks': {i.id: np.array(j.route[k], j.route[k + 1], l / max(waiting_append), 'W/ULD')}}, self.schedule[waiting_append[l - 1]][2], self.schedule[waiting_append[l - 1]][3], self.schedule[waiting_append[l - 1]][4]]
                                    self.time_trck_idle = self.time_trck_idle + 1
                                    # accumulate idle time of the truck to asses schedule
                                else:
                                    # if second in schedule, only update truck dictionary with W/LD
                                    self.schedule[l][0]['trucks'][i.id] = np.array(
                                        [j.route[k], j.route[k + 1], l / max(travel_append),
                                         'W/ULD'])
                                    self.time_trck_idle = self.time_trck_idle + 1
                                    # accumulate idle time of the truck to asses schedule
                        time_periods = np.append(time_periods, waiting_append)
                        #update total time of the schedule of the truck with the waiting time
                        fixed_append = np.arange(len(time_periods), self.get_fixed_times(j.route[k + 1]) + len(time_periods), self.time_delta)
                        #create fixed time if it truck is already located at a load/unload node, use get fixed time function


                        if self.graph.nodes[j.route[k+1]].type == NodeType.BNCH:
                            #if node k+1 == BNCH, update schedule
                            for l in fixed_append:
                                #update/create schedule over fixed time seconds
                                if l not in self.schedule:
                                    #if second not in schedule, update trucks dictionary and maintain for others
                                    self.schedule[l] = [{'trucks': {
                                        i.id: np.array([j.route[k], j.route[k + 1], l / max(fixed_append),'LD'])}}, self.schedule[l - 1][1], self.schedule[l - 1][2],
                                        self.schedule[l - 1][3], self.schedule[l - 1][4]]

                                    counter = 0
                                    #counter to find the index of the BNCH node being Loaded
                                    for a in self.schedule[l][4]:
                                        #iterate over the BNCHs array to find index of the k+1 node
                                        if a[0] == j.node_load_id:
                                            #if loading node of the route == current node of the route, update node status of the BNCH array to 'B/W' , maintain otherwise
                                            self.schedule[l][4][counter][1] = 'B/W'
                                        counter = counter+1

                                else:
                                    #if second in schedule, only update trucks dictionary
                                    self.schedule[l][0]['trucks'][i.id] = np.array(
                                        [j.route[k], j.route[k + 1], l / max(travel_append),
                                         'LD'])
                                    counter = 0

                                    for a in self.schedule[l][4]:
                                        # iterate over the BNCHs array to find index of the k+1 node
                                        if a[0] == j.node_load_id:
                                            # if loading node of the route == current node of the route, update node status of the BNCH array to 'B/W' , maintain otherwise
                                            self.schedule[l][4][counter][1] = 'B/W'
                                        counter = counter + 1

                        elif self.graph.nodes[j.route[k+1]].type == NodeType.CLEA:
                            #if node k+1 == CLEA, update schedule
                            for l in fixed_append:

                                if l not in self.schedule:
                                    # if second not in schedule, update trucks dictionary and maintain for others
                                    self.schedule[l] = [{'trucks': {
                                        i.id: np.array([j.route[k], j.route[k + 1], l / max(fixed_append),
                                                        'LD'])}},
                                        self.schedule[l - 1][1], self.schedule[l - 1][2], self.schedule[l - 1][3], self.schedule[l - 1][4]]

                                    counter = 0
                                    # counter to find the index of the CLEA node being Loaded
                                    for a in self.schedule[l][3]:
                                        #iterate over CLEA array in schedule for the second
                                        if a[0] == j.node_load_id:
                                            # if loading node of the route == current node of the route, update node status of the BNCH array to 'B/W' , maintain otherwise
                                            self.schedule[l][3][counter][1] = 'CL/W'
                                        counter = counter + 1
                                else:
                                    #if second in schedule, update trucks dictionary
                                    self.schedule[l][0]['trucks'][i.id] = np.array(
                                        [j.route[k], j.route[k + 1], l / max(travel_append),
                                         'LD'])
                                    counter = 0

                                    for a in self.schedule[l][3]:
                                        # iterate over CLEA array in schedule for the second
                                        if a[0] == j.node_load_id:
                                            # if loading node of the route == current node of the route, update, maintain otherwise
                                            self.schedule[l][3][counter][1] = 'CL/W'
                                        counter = counter + 1

                        elif self.graph.nodes[j.route[k+1]].type == NodeType.CRSH:
                            # if k+1 node == Crush
                            for l in fixed_append:
                                #if second not in schedule
                                if l not in self.schedule:
                                    #iterate over fixed time seconds to create schedule, change crusher status to C/W,
                                    self.schedule[l] = [{'trucks': {
                                        i.id: np.array([j.route[k], j.route[k + 1], l / max(fixed_append),
                                                        'ULD'])}}, 'C/W', self.schedule[l - 1][2], self.schedule[l - 1][3],
                                                            self.schedule[l - 1][4]]
                                    self.time_crsh_idle = self.time_crsh_idle-1
                                    #reduce idle time of the crusher to asses schedule
                                else:
                                    # if second exists in schedule, update trucks dictionary and crusher state
                                    self.schedule[l][0]['trucks'][i.id] = np.array(
                                        [j.route[k], j.route[k + 1], l / max(travel_append),
                                         'ULD'])

                                    self.schedule[l][1] = 'C/W'
                                    self.time_crsh_idle = self.time_crsh_idle - 1
                                # reduce idle time of the crusher to asses schedule
                        else :
                            #if k+1 node is DUMP node
                            for l in fixed_append:

                                if l not in self.schedule:
                                    # if second not in schedule, create schedule for the fixed time seconds
                                    self.schedule[l] = [{'trucks': {
                                        i.id: np.array([j.route[k], j.route[k + 1], l / max(fixed_append),
                                                        'ULD'])}},
                                        self.schedule[l - 1][1], self.schedule[l - 1][2],
                                        self.schedule[l - 1][3], self.schedule[l - 1][4]]

                                    counter = 0

                                    for a in self.schedule[l][2]:
                                        #iterate over the DUMP array of the schedule for the l second

                                        if a[0] == j.node_unload_id:
                                            # if loading node of the route == current node of the route, update, maintain otherwise
                                            self.schedule[l][2][counter][1] = 'D/W'

                                        counter = counter + 1
                                else:
                                    #if second in schedule update trucks dictionary and DUMP array

                                    self.schedule[l][0]['trucks'][i.id] = np.array(
                                        [j.route[k], j.route[k + 1], l / max(travel_append),
                                         'ULD'])

                                    counter = 0

                                    for a in self.schedule[l][2]:
                                        #iterate over dump array to find the index of the dump node working
                                        if a[0] == j.node_unload_id:
                                            # if loading node of the route == current node of the route, update, maintain otherwise
                                            self.schedule[l][2][counter][1] = 'D/W'

                                        counter = counter + 1

        self.time_crsh_idle = len(self.schedule)+self.time_crsh_idle
        self.time_trck_idle = self.time_trck_idle
        self.time_total = len(self.schedule)
