import simpy
import numpy as np
import random
import networkx as nx

class Order:
    """
    Defines order process and simulation loop
    """

    def __init__(self, lognet, order_id, source, target):
        # grab variables from lognet
        self.lognet = lognet
        self.node_properties = lognet.node_properties
        self.env = lognet.env
        self.network = lognet.network

        self.node_resources = lognet.node_resources
        self.graph = lognet.graph

        # order variables
        self.order_id = order_id
        self.source = source
        self.target = target
        self.current = source     

    
    def get_shortest_path(self, source, target):
        path = nx.shortest_path(self.graph, source, target, weight='weight')
        return path

    def run(self):
        
        path = self.get_shortest_path(self.source, self.target) # e.g [Hub_A, Hub_B, C_0]
        self.lognet.log_event('spawned', order_id=self.order_id, location=self.current)

        while self.current != self.target:
            
            next_node = path[1]
            travel_weight = self.network[self.current][next_node] # weight of edge from current to next node
            travel_time = random.randint(travel_weight-1, travel_weight+1)

            self.lognet.log_event('departed', order_id=self.order_id, 
                             from_node=self.current, to_node=next_node, 
                             travel_time=travel_time)
            
            yield self.env.timeout(travel_time)

            self.lognet.log_event('arrived', order_id=self.order_id, location=next_node)

            if next_node in self.lognet.node_resources:

                # Check capacity of node
                hub_resource = self.lognet.node_resources[next_node]

                self.lognet.log_event('queue_entered', order_id=self.order_id, 
                                 hub=next_node, queue_length=len(hub_resource.queue))
            
                with hub_resource.request() as req:
                    yield req

                    self.lognet.log_event('capacity_secured', order_id=self.order_id, hub=next_node)
                    
                    # when accepted into the hub, update pos and path
                    path.pop(0) # remove previous destination
                    self.current = path[0] # update current location
            else:
                path.pop(0)
                self.current = path[0]  # This will be the target (Customer node)
                break # reached terminal node
            

        self.lognet.log_event('delivered', order_id=self.order_id, destination=self.target)
        self.lognet.completed_deliveries += 1

