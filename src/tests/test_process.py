import pytest
import simpy
import networkx as nx
import random
from src.utils.process import Order


class DummyLognet():
    def __init__(self):
        self.env = simpy.Environment()
        # metrics go here
        self.completed_deliveries = 0
        #self.node_properties = {'A': {'Capacity': 1}, 'B':{'Capacity': 2}, 'C': {'Capacity': 3}}
        self.network = {'A': {'B': {'weight': 5}}, 
                        'B': {'C': {'weight': 2}}}
        self.node_resources = {}
        self.events = []
        
        # build graph for distance calculations
        self.graph = nx.from_dict_of_dicts(self.network, create_using=nx.Graph())

    def log_event(self, event_type, **data):
        pass

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