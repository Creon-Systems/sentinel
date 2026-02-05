import simpy
import numpy as np
import random
import networkx as nx

# -------- Simulation Logic  ------- #
class LogisticsNetwork:
    """
    Stores environment and metrics
    """

    def __init__(self, env, network, node_properties):
        # initialise environment
        self.env = env
        self.network = network
        # metrics go here
        self.completed_deliveries = 0
        self.node_properties = node_properties

        # build graph for distance calculations
        self.graph = nx.DiGraph()  # Directed graph
        for node, neighbors in self.network.items():
            for neighbor, weight in neighbors.items():
                self.graph.add_edge(node, neighbor, weight=weight)

        # generate simpy resources according to node properties
        self.node_resources = {}
        for node_name, properties in node_properties.items():
            capacity = properties['Capacity']
            self.node_resources[node_name] = simpy.Resource(env, capacity=capacity)   
       

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

        while self.current != self.target:
            
            next_node = path[1]
            travel_weight = self.network[self.current][next_node] # weight of edge from current to next node
            travel_time = random.randint(travel_weight-1, travel_weight+1)
            print(f"Order {self.order_id} is in transit between {self.current} and {next_node} at {self.env.now}") 
            
            yield self.env.timeout(travel_time)
            print(f"Order {self.order_id} is now at {next_node} at {self.env.now}")

            if next_node in self.lognet.node_resources:

                # Check capacity of node
                hub_resource = self.lognet.node_resources[next_node]
                with hub_resource.request() as req:
                    yield req
                    
                    # when accepted into the hub, update pos and path
                    path.pop(0) # remove previous destination
                    self.current = path[0] # update current location
            else:
                path.pop(0)
                self.current = path[0]  # This will be the target (Customer node)
                break # reached terminal node
            

        print(f"Order {self.order_id} has reached target destination {self.target} at {env.now}")
        self.lognet.completed_deliveries += 1
# -------- Simulation Logic  ------- #


# --------- Parameter Logic -------- #
env = simpy.Environment()
network = {'Hub_A': {'Hub_B': 8, 'Hub_C': 5},
           'Hub_B': {'Hub_D': 10, 'Customer_0': 3},
           'Hub_C': {'Customer_1': 3, 'Customer_2': 3},
           'Hub_D': {'Customer_3': 1},
           'Customer_0': {},  
           'Customer_1': {},
           'Customer_2': {},
           'Customer_3': {}
           }

node_properties = {'Hub_A': {'Capacity': 1},
                   'Hub_B': {'Capacity': 1},
                   'Hub_C': {'Capacity': 1},
                   'Hub_D': {'Capacity': 1}
                   }

lognet = LogisticsNetwork(env, network, node_properties)

orders = [
    Order(lognet, 1, 'Hub_A', 'Customer_0'),
    Order(lognet, 2, 'Hub_A', 'Customer_1'),
    Order(lognet, 3, 'Hub_A', 'Customer_2'),
    Order(lognet, 4, 'Hub_A', 'Customer_3'),
]

for order in orders:
    env.process(order.run())

env.run(until=40)
# --------- Parameter Logic -------- #