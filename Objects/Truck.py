import numpy as np
import pandas as pd
from Objects.Task import *
from enum import Enum, auto


class TruckState(Enum):
    WAIT = auto()
    TRVL = auto()
    LOAD = auto()
    UNLD = auto()


class TruckInfo:

    def __init__(self):
        self.current_task_id = -1
        self.last_node_id = -1
        self.next_node_id = -1
        self.action_state = None
        self.load_state = False
        self.route_progress = 0.0
        self.current_speed = 0.0


class Truck:
    time_load = 75
    time_unload = 35
    length = 0.03

    def __init__(self, t_start_node, t_id=0, t_brand='', t_model='', t_capacity=-1):
        self.id = t_id
        self.tasks = np.array([]).astype(Task)
        self.tasks_ids = np.array([])
        self.start_node = t_start_node
        self.brand = t_brand
        self.model = t_model
        self.capacity = t_capacity
        self.cost = -1
        self.avg_speed = np.array([])
        self.get_truck_data()

    def get_truck_data(self):
        pd_truck_data = pd.read_csv(f'OTR TRUCKS DATABASE - {self.brand.upper()}.csv')
        pd_truck_data = pd_truck_data[['MODEL', self.model]]
        self.cost = float(pd_truck_data[self.model].loc[0])
        self.capacity = float(pd_truck_data[self.model].loc[1])
        self.avg_speed = pd_truck_data[['MODEL', '770G']].loc[4:].set_index('MODEL')

    def add_task(self, task):
        self.tasks = np.append(self.tasks, task)
        task.assigned_truck_id = self.id

    def add_multiple_tasks(self, tasks):
        self.tasks = np.concatenate((self.tasks, tasks))
        for task in tasks:
            task.assigned_truck_id = self.id
