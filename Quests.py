from enum import Enum, auto

class QuestType(Enum):
    WAIT = auto()
    TRVL = auto()
    LOAD = auto()
    UNLD = auto()
    MTNC = auto()


class Quest:
    def __init__(self,q_type,node1='',node2=''):
        self.q_type = q_type
        self.q_time = 0
        self.node1= node1
        self.node2= node2
        self.q_truck=""
