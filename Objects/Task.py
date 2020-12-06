

class Task:
    def __init__(self, node_load_id=0, node_unload_id=0):
        self.node_load_id = node_load_id
        self.node_unload_id = node_unload_id
        self.node_start_id = -1
        self.assigned_truck_id = -1
        self.route = []
