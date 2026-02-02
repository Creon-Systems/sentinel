import simpy
import numpy as np
import networkx as nx

class LogisticsNetwork:
    """
    Stores environment and metrics
    """

    def __init__(self, env, network):
        # initialise environment
        self.env = env
        self.network = network
        # metrics go here
        self.completed_deliveries = 0

class Order:
    """
    Defines order process and simulation loop
    """

    def __init__(self, lognet, order_id, source, target):
        self.lognet = lognet
        self.env = lognet.env
        self.network = lognet.network
        self.order_id = order_id
        self.source = source
        self.target = target
        self.current = source

        self.graph = nx.DiGraph()  # Directed graph
        for node, neighbors in self.network.items():
            for neighbor, weight in neighbors.items():
                self.graph.add_edge(node, neighbor, weight=weight)
       
    
    def get_shortest_path(self, source, target):
        path = nx.shortest_path(self.graph, source, target, weight='weight')
        return path

    def run(self):
        
        path = self.get_shortest_path(self.source, self.target) # e.g [Hub_A, Hub_B, C_0]

        while self.current != self.target:
            
            next_node = path[1]
            travel_time = self.network[self.current][next_node]
            print(f"Order {self.order_id} is in transit between {self.current} and {next_node} at {self.env.now}") 
            yield self.env.timeout(travel_time)

            print(f"Order {self.order_id} is now at {path[1]} at {self.env.now}")
            path.pop(0) # remove previous destination
            self.current = path[0] # update current location

        print(f"Order {self.order_id} has reached target destination {self.target} at {env.now}")
        self.lognet.completed_deliveries += 1


env = simpy.Environment()
network = {'Hub_A': {'Hub_B': 8, 'Hub_C': 5},
           'Hub_B': {'Hub_D': 10, 'Customer_0': 3},
           'Hub_C': {'Customer_1': 3, 'Customer_2': 3},
           'Hub_D': {'Customer_3': 1}
           }

lognet = LogisticsNetwork(env, network)

orders = [
    Order(lognet, 1, 'Hub_A', 'Customer_0'),
    Order(lognet, 2, 'Hub_A', 'Customer_1'),
    Order(lognet, 3, 'Hub_A', 'Customer_2'),
    Order(lognet, 4, 'Hub_A', 'Customer_3'),
]

for order in orders:
    env.process(order.run())

env.run(until=40)