import pandas as pd
import numpy as np
from Objects.Trucks import *

#read solution
trucks_used=np.array(solution[0,:]).unique
#add tasks to trucks used in solution
for i in range(0,len(trucks_used)):
    tasks_truck=solution[1,np.where(solution[0,:]==trucks_used[i])]
    trucks_used[i].addQuest(tasks_truck)

def get_state(node1):
    if node1.n_type in [BNKO,BNKW]:
        state='L'
    else:
        state='E'
    return state

def get_fixedtimes(node2):
    if node2.n_type in [BNKO,BNKW]:
        time=Truck.t_spottime+Truck.t_loadtime
    if node2.n_type in [DMNT,CSHR,WSHP]:
        time=Truck.spottime+Truck.t_unloadtime
    else:
        time=0
    return time



#calculate time for truck
timeframe=input('Please select time frames in seconds')
nodes_truck=np.array([])

schedule={}

for i in range(0,len(trucks_used)):
    quest_set=trucks_used[i].quest_set
    time_periods = np.array([])
    for j in range(0,len(quest_set)):
    np.append(nodes_truck[],(trucks_used[i].id,quest_set[j].route))
    route=nodes_truck[i,j]
        for k in range(0,len(route)-1):
            #call distance,friction and slope in edge)
            distance=G.edge(route[k],route[k]).distance
            friction=G.edge(route[k],route[k]).friction
            slope=G.edge(route[k],route[k]).slope
            time_travel= distance/trucks_used[i].t_avgspeed[str(friction+slope)+get_state(route[0])]
            travel_append=np.arange(len(time_periods),int(time_travel/timeframe)+len(time_periods),timeframe)
            fixed_append=np.arange(len(travel_append),get_fixedtimes(route[k+1])+len(travel_append),timeframe)

            time_periods=np.append(time_periods,travel_append)
            time_periods=np.append(time_periods,fixed_append)

            
            #considerar viaje y descarga/carga por iteracion
            for l in travel_append:
                schedule={travel_append[l]:{trucks_used[i]:np.array(route[k],route[k+1],get_state(route[0]),quest_set[j].route)}}
            for l in fixed_append:
                if len(fixed_append)>(15+20):
                    schedule={fixed_append[l]:{trucks_used[i]:np.array(route[k],route[k+1],'LD',quest_set[j].route)}}
                else:
                    schedule = {fixed_append[l]:{trucks_used[i]:np.array(route[k], route[k+1], 'ULD',quest_set[j].route)}}


#corregir indexacion

def score (schedule,trucks_used):
    total_time=max(list(schedule))
    crusher_counter=0
    travel_quantity_pertruck=np.array([])
    for i in schedule:
        for j in schedule[i]:
            crusher_counter=int(np.where(schedule[i][j][2]=='LD'))+crusher_counter
    for k in trucks_used:
        np.append(travel_quantity_pertruck,len(k.quest_set))



    return total_time,crusher_counter,travel_quantity_pertruck
