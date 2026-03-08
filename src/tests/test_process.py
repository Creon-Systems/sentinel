import pytest
import simpy
import networkx as nx
import random
from src.utils.process import Order
from src.utils.node_status import NodeStatusManager, NodeState


class DummyLognet():
    def __init__(self):
        self.env = simpy.Environment()
        # metrics go here
        self.completed_deliveries = 0
        self.network = {'A': {'B': {'weight': 5}}, 
                        'B': {'C': {'weight': 2}}}
        self.node_resources = {}
        self.events = []
        
        # build graph for distance calculations
        self.graph = nx.from_dict_of_dicts(self.network, create_using=nx.DiGraph())
        
        # Initialize node status manager
        self.node_status_manager = NodeStatusManager(self.env, ['A', 'B', 'C'])

    def log_event(self, event_type, **data):
        self.events.append({
            'time': self.env.now,
            'type': event_type,
            **data
        })
    
    def is_node_operational(self, node):
        """Check if a node is operational"""
        return self.node_status_manager.is_operational(node)

@pytest.fixture
def dummy_lognet():
    return DummyLognet()

def test_shortest_path(dummy_lognet):

    test_order = Order(dummy_lognet, 1, 'A', 'C')
    path = test_order.get_shortest_path(test_order.source, test_order.target)

    assert path == ['A', 'B', 'C']

def test_run_travel(dummy_lognet):

    random.seed(0)
    test_order = Order(dummy_lognet, 1, 'A', 'C')
    dummy_lognet.env.process(test_order.run()) #lognet contains env, not order
    dummy_lognet.env.run()

    assert 5 <= dummy_lognet.env.now <= 9

def test_run_capacity(dummy_lognet):

    dummy_lognet.node_resources = {'A': simpy.Resource(dummy_lognet.env, capacity=1),
                                   'B': simpy.Resource(dummy_lognet.env, capacity=1) }

    def occupy_resource(resource):
        with resource.request() as req:
            yield req
            yield dummy_lognet.env.timeout(1000)  # hold it “forever” (or long enough for the test)

    # start occupying
    dummy_lognet.env.process(occupy_resource(dummy_lognet.node_resources['B']))

    # create order that will now wait in queue
    test_order = Order(dummy_lognet, 1, 'A', 'C')
    dummy_lognet.env.process(test_order.run())

    # run simulation a little while
    dummy_lognet.env.run(until=10)

    # assert the order is still waiting
    queue_len = len(dummy_lognet.node_resources['B'].queue)
    assert queue_len == 1


class TestRerouting:
    """Tests for Order rerouting around failed nodes"""
    
    def test_path_excludes_failed_nodes(self, dummy_lognet):
        """Test that get_shortest_path excludes failed nodes"""
        # Fail node B
        dummy_lognet.node_status_manager.fail_node('B')
        
        # Try to find path A -> C (must skip B)
        test_order = Order(dummy_lognet, 1, 'A', 'C')
        path = test_order.get_shortest_path('A', 'C')
        
        # Should be None (no alternate path in simple network)
        assert path is None
    
    def test_expanded_network_with_failed_node(self):
        """Test rerouting in a network with alternate paths"""
        env = simpy.Environment()
        
        # Network with alternate paths: A->B->C and A->D->C
        network = {
            'A': {'B': {'weight': 5}, 'D': {'weight': 3}},
            'B': {'C': {'weight': 2}},
            'D': {'C': {'weight': 4}}
        }
        
        lognet = DummyLognet()
        lognet.env = env
        lognet.network = network
        lognet.graph = nx.from_dict_of_dicts(network, create_using=nx.DiGraph())
        lognet.node_status_manager = NodeStatusManager(env, ['A', 'B', 'C', 'D'])
        
        # Without failures, should take cheaper path A->B->C
        order = Order(lognet, 1, 'A', 'C')
        path = order.get_shortest_path('A', 'C')
        assert path == ['A', 'B', 'C']
        
        # Fail node B, should reroute to A->D->C
        lognet.node_status_manager.fail_node('B')
        path = order.get_shortest_path('A', 'C')
        assert path == ['A', 'D', 'C']
    
    def test_order_fails_no_route_available(self):
        """Test that order fails when no route exists"""
        env = simpy.Environment()
        
        # Simple linear network
        network = {'A': {'B': {'weight': 1}}, 'B': {'C': {'weight': 1}}}
        
        lognet = DummyLognet()
        lognet.env = env
        lognet.network = network
        lognet.graph = nx.from_dict_of_dicts(network, create_using=nx.DiGraph())
        lognet.node_status_manager = NodeStatusManager(env, ['A', 'B', 'C'])
        lognet.node_resources = {}
        
        # Fail B, blocking the only route
        lognet.node_status_manager.fail_node('B')
        
        order = Order(lognet, 1, 'A', 'C')
        lognet.env.process(order.run())
        lognet.env.run()
        
        # Order should be marked as failed
        failed_events = [e for e in lognet.events if e['type'] == 'failed']
        assert len(failed_events) == 1
        assert failed_events[0]['reason'] == 'no_route_available'
    
    def test_order_no_reroute_after_node_operational(self):
        """Test that order doesn't reroute if stopped node becomes operational again"""
        env = simpy.Environment()
        
        network = {
            'A': {'B': {'weight': 2}, 'D': {'weight': 3}},
            'B': {'C': {'weight': 2}},
            'D': {'C': {'weight': 3}}
        }
        
        lognet = DummyLognet()
        lognet.env = env
        lognet.network = network
        lognet.graph = nx.from_dict_of_dicts(network, create_using=nx.DiGraph())
        lognet.node_status_manager = NodeStatusManager(env, ['A', 'B', 'C', 'D'])
        lognet.node_resources = {}
        
        order = Order(lognet, 1, 'A', 'C')
        lognet.env.process(order.run())
        
        # Fail B, then recover it quickly
        def fail_and_recover():
            yield env.timeout(1)
            lognet.node_status_manager.fail_node('B')
            yield env.timeout(1)
            lognet.node_status_manager.recover_node('B')
        
        env.process(fail_and_recover())
        env.run()
        
        # Order should complete successfully
        assert lognet.completed_deliveries == 1
        
        # Should have been delivered
        delivered = [e for e in lognet.events if e['type'] == 'delivered']
        assert len(delivered) == 1