"""
Node status manager tracks the health state of each node in logistics network:
ACTIVE = Node works normally
DEGRADED = Node works but with reduced capacity (e.g., warehouse only handles 50% of orders)
FAILED = Node is completely down (orders can't use it)
"""
from enum import Enum
import simpy


class NodeState(Enum):
    """Defines possible states for a network node"""
    ACTIVE = "active"
    DEGRADED = "degraded"  # Reduced capacity
    FAILED = "failed"      # Completely unavailable


class NodeStatusManager:
    """
    Manages the operational status of nodes in the logistics network.
    Allows nodes to be dynamically failed, recovered, or degraded.
    """
    
    def __init__(self, env, initial_nodes):
        """
        Args:
            env: SimPy environment
            initial_nodes: List of node names to track
        """
        self.env = env
        self.node_states = {node: NodeState.ACTIVE for node in initial_nodes}
        self.node_original_capacity = {}  # Store original capacities
        self.status_history = []  # Track all status changes
        
    def set_node_state(self, node, state, capacity_reduction=None):
        """
        Change a node's operational state.
        
        Args:
            node: Node identifier
            state: NodeState enum value
            capacity_reduction: For DEGRADED state, fraction of capacity lost (0.0-1.0)
        """
        if node not in self.node_states:
            raise ValueError(f"Node {node} not tracked")
        
        old_state = self.node_states[node]
        self.node_states[node] = state
        
        self.status_history.append({
            'time': self.env.now,
            'node': node,
            'old_state': old_state,
            'new_state': state,
            'capacity_reduction': capacity_reduction
        })
        
    def is_operational(self, node):
        """Returns True if node is ACTIVE or DEGRADED, False if FAILED"""
        if node not in self.node_states:
            return True  # Unknown nodes are assumed operational
        return self.node_states[node] != NodeState.FAILED
    
    def get_node_state(self, node):
        """Get the current state of a node"""
        return self.node_states.get(node, NodeState.ACTIVE)
    
    def fail_node(self, node):
        """Fail a node (make it completely unavailable)"""
        self.set_node_state(node, NodeState.FAILED)
    
    def recover_node(self, node):
        """Recover a failed node back to active state"""
        self.set_node_state(node, NodeState.ACTIVE)
    
    def degrade_node(self, node, capacity_reduction=0.5):
        """
        Degrade a node's capacity.
        
        Args:
            node: Node identifier
            capacity_reduction: Fraction of capacity lost (0.0-1.0)
        """
        self.set_node_state(node, NodeState.DEGRADED, capacity_reduction)
    
    def get_status_summary(self):
        """Get summary of all node statuses"""
        summary = {}
        for node, state in self.node_states.items():
            summary[node] = state.value
        return summary
