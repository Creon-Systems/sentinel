import simpy
import numpy as np
import random
import networkx as nx
from .node_status import NodeState

class Order:
    """
    Defines order process and simulation loop
    """

    def __init__(self, lognet, order_id, source, target):
        # grab variables from lognet
        self.lognet = lognet

        # order variables
        self.order_id = order_id
        self.source = source
        self.target = target
        self.current = source     

    
    def get_shortest_path(self, source, target):
        """
        Compute shortest path excluding failed nodes.
        Returns path from source to target (including both), or None if no route exists.
        """
        # Create a copy of graph and remove failed nodes
        G = self.lognet.graph.copy()
        failed_nodes = [n for n, state in self.lognet.node_status_manager.node_states.items()
                        if state == NodeState.FAILED]
        G.remove_nodes_from(failed_nodes)
        
        try:
            path = nx.shortest_path(G, source, target, weight='weight')
            return path
        except nx.NetworkXNoPath:
            return None

    def run(self):
        path = self.get_shortest_path(self.source, self.target)
        
        if path is None:
            self.lognet.log_event('failed', order_id=self.order_id, reason='no_route_available')
            return
        
        self.lognet.log_event('spawned', order_id=self.order_id, location=self.current)
        
        # Path includes current location, so skip it
        path = path[1:]  # Now path[0] is next_node
        
        while path:
            next_node = path[0]
            
            # Check if next node is operational before traveling
            if not self.lognet.is_node_operational(next_node):
                self.lognet.log_event('reroute_triggered', order_id=self.order_id, 
                                      blocked_node=next_node, current=self.current)
                # Recompute path
                path = self.get_shortest_path(self.current, self.target)
                if path is None:
                    self.lognet.log_event('failed', order_id=self.order_id, reason='no_route_after_failure')
                    return
                path = path[1:]  # Skip current location
                continue
            
            travel_weight = self.lognet.network[self.current][next_node]['weight']
            travel_time = random.randint(travel_weight - 1, travel_weight + 1)
            
            self.lognet.log_event('departed', order_id=self.order_id,
                                  from_node=self.current, to_node=next_node,
                                  travel_time=travel_time)
            
            yield self.lognet.env.timeout(travel_time)
            
            self.lognet.log_event('arrived', order_id=self.order_id, location=next_node)
            
            if next_node in self.lognet.node_resources:
                hub_resource = self.lognet.node_resources[next_node]
                
                self.lognet.log_event('queue_entered', order_id=self.order_id,
                                      hub=next_node, queue_length=len(hub_resource.queue))
                
                with hub_resource.request() as req:
                    yield req
                    
                    self.lognet.log_event('capacity_secured', order_id=self.order_id, hub=next_node)
                    
                    # Move to next node in path
                    self.current = next_node
                    path.pop(0)
            else:
                # Not a hub, but could be intermediate node or target
                self.current = next_node
                path.pop(0)
                
                if self.current == self.target:
                    break  # Reached the target
        
        self.lognet.log_event('delivered', order_id=self.order_id, destination=self.target)
        self.lognet.completed_deliveries += 1

