import numpy as np
import pandas as pd




class Truck:
    def __init__(self,t_startnode,t_cost=0, t_capacity=0, t_maintenance='NO'):
        self.quest_set = np.array([]).astype(Quest)
        self.t_cost= t_cost
        self.t_capacity = t_capacity
        self.t_maintenance= t_maintenance
        self.t_startnode=t_startnode


        self.getTruckData()

    def getTruckData(self):

        prompt='please type 1 for CAT trucks or 2 for KOMATSU trucks'
        code=0
        while code != 1 or 2:
            code= int(input(prompt))
        if code==1:
            pd_TruckData=pd.read_csv('OTR TRUCKS DATABASE - CAT.csv')
        if code==2:
            pd_TruckData=pd.read_csv('OTR TRUCKS DATABASE - KOMATSU.csv')
        prompt='please type your truck model'
        code=input(prompt)
        pd_TruckData=pd_TruckData[code]
        t_cost=pd_TruckData.iloc['HOURLY COST ($/h)']
        t_capacity = pd_TruckData.iloc['PAYLOAD(t)']
        prompt='please type the approximate frequence in days where maintenance service is done'
        rate=input(prompt)
        prompt = 'please type the approximate time in minutes of the maintenance service duration'
        duration = input(prompt)
        t_maintenance=np.array([rate,duration])
        return t_cost,t_capacity,t_maintenance

    def addQuest(self,quest):
        self.quest_set = np.append(self.quest_set, quest)
        quest.q_truck=self
