from Objects.Truck import *
from Objects.Graph import *
import copy
import math


class Schedule:

    def __init__(self, graph, tasks, trucks, solution, time_delta):
        self.graph = graph
        self.trucks = copy.deepcopy(trucks)
        self.tasks = copy.deepcopy(tasks)
        self.solution = solution
        self.time_delta = time_delta
        self.schedule = {}
        self.grades = {}
        self.time_crsh_use = 0
        self.time_crsh_idle = 0
        self.time_total = 0
        self.grade_variance = np.inf
        self.distance_policy = 2 * Truck.length
        self.unload_discrete_time = math.ceil(Truck.time_unload / self.time_delta)
        self.window_size = self.unload_discrete_time * (self.graph.bench_qty + 1)
        self.window_qty = math.ceil(solution.unloads_qty * self.unload_discrete_time / self.window_size)
        self.window_avg = np.array([])
        self.assign_tasks()

    # Sort Tasks by order and add tasks to trucks
    def assign_tasks(self):
        for truck in self.trucks:
            assigned_tasks_idx = self.solution.solution[:, 0] == truck.id
            tasks_truck = np.where(assigned_tasks_idx)[0][np.argsort(self.solution.solution[assigned_tasks_idx][:, 1])]
            truck.tasks_ids = tasks_truck
            truck.add_multiple_tasks(self.tasks[tasks_truck])

    # Calculate route for each task already assigned to the trucks
    def calculate_routes(self):
        for truck in self.trucks:
            initial_node = truck.start_node
            for task in truck.tasks:
                task.node_start_id = initial_node
                task.route = np.concatenate((self.graph.paths[initial_node, task.node_load_id],
                                             self.graph.paths[task.node_load_id, task.node_unload_id][1:]))
                initial_node = task.node_unload_id

    # Get the max time the truck has to wait to avoid breaking the distance policy
    def wait_time_collision(self, second, last_node_id, next_node_id, route_progress):
        if second in self.schedule:
            wait_times = [0]
            trucks_in_edge = (self.schedule[second][2].get(last_node_id, {})).get(next_node_id, [])
            position = self.graph.edges[last_node_id, next_node_id].distance * route_progress
            for truck_id in trucks_in_edge:
                truck_progress = self.schedule[second][0][truck_id].route_progress
                truck_position = self.graph.edges[last_node_id, next_node_id].distance * truck_progress
                truck_distance = truck_position - position
                truck_speed = self.schedule[second][0][truck_id].current_speed
                if truck_distance < self.distance_policy:
                    wait_time = math.ceil((self.distance_policy - truck_distance) / truck_speed*3600 / self.time_delta)
                    wait_times += [wait_time]
            return max(wait_times)
        return 0

    # Get the time the truck has to wait to load / unload on the node
    def wait_time_node(self, second, next_node_id):
        if second in self.schedule:
            return self.schedule[second][1].get(next_node_id, 0)
        return 0

    def truck_wait(self, truck_id, start_time, finish_time, truck_info):
        for second in range(start_time, finish_time):
            frame_info = TruckInfo()
            frame_info.current_task_id = truck_info.current_task_id
            frame_info.last_node_id = truck_info.last_node_id
            frame_info.next_node_id = truck_info.next_node_id
            frame_info.action_state = TruckState.WAIT
            frame_info.load_state = truck_info.load_state
            frame_info.route_progress = truck_info.route_progress
            frame_info.current_speed = 0.0
            frame_second = self.schedule.setdefault(second, [{}, {}, {}])
            frame_second[0][truck_id] = frame_info

    def truck_wait_node(self, truck_id, start_time, finish_time, total_time, truck_info):
        for second in range(start_time, finish_time):
            frame_info = TruckInfo()
            frame_info.current_task_id = truck_info.current_task_id
            frame_info.last_node_id = truck_info.last_node_id
            frame_info.next_node_id = truck_info.next_node_id
            frame_info.action_state = TruckState.WAIT
            frame_info.load_state = truck_info.load_state
            frame_info.route_progress = 1.0
            frame_info.current_speed = 0.0
            frame_second = self.schedule.setdefault(second, [{}, {}, {}])
            frame_second[0][truck_id] = frame_info
            frame_second[1][frame_info.next_node_id] = total_time - second

    def truck_travel(self, truck_id, start_time, finish_time, truck_info):
        for second in range(start_time, finish_time):
            frame_info = TruckInfo()
            frame_info.current_task_id = truck_info.current_task_id
            frame_info.last_node_id = truck_info.last_node_id
            frame_info.next_node_id = truck_info.next_node_id
            frame_info.action_state = TruckState.TRVL
            frame_info.load_state = truck_info.load_state
            frame_info.route_progress = (second - start_time) / (finish_time - start_time)
            frame_info.current_speed = truck_info.current_speed
            frame_second = self.schedule.setdefault(second, [{}, {}, {}])
            frame_second[0][truck_id] = frame_info
            frame_edge = frame_second[2].setdefault(frame_info.last_node_id, {})
            frame_edge[frame_info.next_node_id] = frame_edge.get(frame_info.next_node_id, []) + [truck_id]

    def truck_work(self, truck_id, start_time, finish_time, truck_info):
        using_crusher = truck_info.action_state == TruckState.UNLD and \
                        self.graph.nodes[truck_info.next_node_id].type == NodeType.CRSH
        for second in range(start_time, finish_time):
            frame_info = TruckInfo()
            frame_info.current_task_id = truck_info.current_task_id
            frame_info.last_node_id = truck_info.last_node_id
            frame_info.next_node_id = truck_info.next_node_id
            frame_info.action_state = truck_info.action_state
            frame_info.load_state = truck_info.load_state
            frame_info.route_progress = 1.0
            frame_info.current_speed = 0.0
            frame_second = self.schedule.setdefault(second, [{}, {}, {}])
            frame_second[0][truck_id] = frame_info
            frame_second[1][frame_info.next_node_id] = finish_time - second
            self.time_crsh_use += using_crusher
        if using_crusher:
            self.grades[start_time] = self.graph.nodes[self.tasks[truck_info.current_task_id].node_load_id].grade

    def calculate_schedule(self):
        # self.schedule =
        # { second(int):
        #   [
        #       (0){truck_id   :  TruckInfo:
        #                           (0)current_task_id,
        #                           (1)last_node_id,
        #                           (2)next_node_id,
        #                           (3)action_state(TruckState),
        #                           (4)load_state(bool),
        #                           (5)route_progress(float),
        #                           (6)current_speed(float)},
        #       (1){node_id    :    time_occupied(int)},
        #       (2){node_id1   :    {node_id2: [id_truck1, id_truck2, ...]}}
        #   ]
        # }
        for truck in self.trucks:
            current_time = 0
            for t in range(len(truck.tasks)):
                task = truck.tasks[t]
                task_id = truck.tasks_ids[t]
                task_load_pos = np.where(task.route == task.node_load_id)[0][0]
                for node in range(len(task.route) - 1):
                    last_node_id = task.route[node]
                    next_node_id = task.route[node + 1]
                    route_progress = 0.0

                    distance = self.graph.edges[last_node_id, next_node_id].distance
                    friction = self.graph.edges[last_node_id, next_node_id].friction
                    slope = self.graph.edges[last_node_id, next_node_id].slope
                    resistance = int(max(0, friction + slope) * 100)
                    is_loaded = task_load_pos <= node
                    # velocity = truck.avg_speed[resistance][is_loaded]
                    velocity = 20

                    truck_info = TruckInfo()
                    truck_info.current_task_id = task_id
                    truck_info.last_node_id = last_node_id
                    truck_info.next_node_id = next_node_id
                    truck_info.load_state = is_loaded
                    truck_info.route_progress = route_progress
                    truck_info.current_speed = velocity

                    # Wait for possible collisions
                    wait_time = self.wait_time_collision(current_time, last_node_id, next_node_id, route_progress)
                    while wait_time > 0:
                        finish_time = current_time + wait_time
                        self.truck_wait(truck.id, current_time, finish_time, truck_info)
                        current_time = finish_time
                        wait_time = self.wait_time_collision(current_time, last_node_id, next_node_id, route_progress)

                    # Travel
                    time_travel = int(distance / velocity * 3600) // self.time_delta
                    finish_time = current_time + time_travel
                    self.truck_travel(truck.id, current_time, finish_time, truck_info)
                    current_time = finish_time

                    # Check if truck has load / unload work now
                    if self.graph.nodes[truck_info.next_node_id].type in [NodeType.BNCH, NodeType.CLEA, NodeType.DUMP, NodeType.CRSH]:

                        # Wait for node to be unoccupied
                        if self.graph.nodes[next_node_id].type in [NodeType.BNCH, NodeType.CLEA]:
                            time_work = math.ceil(Truck.time_load / self.time_delta)
                            truck_info.action_state = TruckState.LOAD
                        else:
                            time_work = math.ceil(Truck.time_unload / self.time_delta)
                            truck_info.action_state = TruckState.UNLD
                        wait_time = self.wait_time_node(current_time, next_node_id)
                        finish_time = current_time + wait_time
                        total_time = finish_time + time_work
                        self.truck_wait_node(truck.id, current_time, finish_time, total_time, truck_info)
                        current_time = finish_time

                        # Load / Unload
                        finish_time = current_time + time_work
                        self.truck_work(truck.id, current_time, finish_time, truck_info)
                        current_time = finish_time

        self.time_total = len(self.schedule) * self.time_delta
        self.time_crsh_use *= self.time_delta
        self.time_crsh_idle = self.time_total - self.time_crsh_use

    def calculate_grade_variance(self):
        ordered_grades = np.array(list(self.grades.values()))[np.argsort(list(self.grades))]
        self.window_avg = [np.mean(window) for window in np.array_split(ordered_grades, self.window_qty)]
        self.grade_variance = np.var(self.window_avg)
