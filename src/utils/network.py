import simpy
import numpy as np
import random
import networkx as nx

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

        self.events = []
        
    def log_event(self, event_type, **data):
        # Log an event with timestamp and event type
        self.events.append({
            'time': self.env.now,
            'type': event_type,
            **data
        })