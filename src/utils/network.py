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

        # build graph for distance calculations
        self.graph = nx.from_dict_of_dicts(network, create_using=nx.Graph())

        # generate simpy resources according to node properties
        self.node_resources = {}
        for node_name, properties in node_properties.items():
            capacity = properties['Capacity']
            self.node_resources[node_name] = simpy.Resource(env, capacity=capacity)

        # metrics for logging and analysis
        self.events = []
        self.completed_deliveries = 0
        
    def log_event(self, event_type, **data):
        # Log an event with timestamp and event type
        self.events.append({
            'time': self.env.now,
            'type': event_type,
            **data
        })