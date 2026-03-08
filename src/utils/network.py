import simpy
import numpy as np
import random
import networkx as nx
from .node_status import NodeStatusManager

class LogisticsNetwork:
    """
    Stores environment and metrics
    """

    def __init__(self, env, network, node_properties):
        # initialise environment
        self.env = env
        self.network = network

        # build graph for distance calculations
        self.graph = nx.from_dict_of_dicts(network, create_using=nx.DiGraph())

        # generate simpy resources according to node properties
        self.node_resources = {}
        self.node_original_capacity = {}  # Store original capacities
        for node_name, properties in node_properties.items():
            capacity = properties['Capacity']
            self.node_resources[node_name] = simpy.Resource(env, capacity=capacity)
            self.node_original_capacity[node_name] = capacity

        # initialize node status manager
        self.node_status_manager = NodeStatusManager(env, list(node_properties.keys()))

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
    
    def is_node_operational(self, node):
        """Check if a node is operational (not failed)"""
        return self.node_status_manager.is_operational(node)
    
    def get_node_effective_capacity(self, node):
        """Get effective capacity of a node (reduced if degraded)"""
        if node not in self.node_original_capacity:
            return None
        
        original = self.node_original_capacity[node]
        # For now, just return original - can be extended when status changes are applied
        return original