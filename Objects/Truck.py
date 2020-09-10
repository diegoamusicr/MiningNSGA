import numpy as np
import pandas as pd
from Objects.Task import *


class Truck:
    time_spot = 15
    time_load = 60
    time_unload = 20
    def __init__(self, t_start_node, t_id=0, t_brand='', t_model='', t_rate=0, t_duration=0, t_capacity=-1):
        self.id = t_id
        self.tasks = np.array([]).astype(Task)
        self.start_node = t_start_node
        self.maintenance = (t_rate, t_duration)
        self.brand = t_brand
        self.model = t_model
        self.capacity = t_capacity
        self.cost = -1
        self.avg_speed = -1

        #self.get_truck_data()

    def get_truck_data(self):

        pd_truck_data = pd.read_csv(f'OTR TRUCKS DATABASE - {self.brand.upper()}.csv')
        pd_truck_data = pd_truck_data[self.model]
        self.cost = pd_truck_data.iloc['HOURLY COST ($/h)']
        self.capacity = pd_truck_data.iloc['PAYLOAD(t)']
        self.avg_speed = pd_truck_data.iloc['6:']

    def add_task(self, task):
        self.tasks = np.append(self.tasks, task)
        task.assigned_truck_id = self

    def add_multiple_tasks(self, tasks):
        self.tasks = np.append(self.tasks, tasks)
        for task in tasks:
            task.assigned_truck_id = self
