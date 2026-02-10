import pytest
import simpy
import networkx as nx
from src.utils.network import LogisticsNetwork

def test_graph_construction():
    env = simpy.Environment()
    network = {
        'A': {'B': 5},
        'B': {'C': 2}
    }
    node_proerties = {}

    lognet = LogisticsNetwork(env, network, node_proerties)
    distAB = nx.shortest_path_length(lognet.graph, 'A', 'B', weight='weight')
    distAC = nx.shortest_path_length(lognet.graph, 'A', 'C', weight='weight')
    pathAC = nx.shortest_path(lognet.graph, 'A', 'C', weight='weight')

    assert distAB == 5
    assert distAC == 7
    assert pathAC == ['A', 'B', 'C']

def test_node_resources():
    env = simpy.Environment()
    network = {
        'A': {},
        'B': {}
    }
    node_properties = {'A': {'Capacity': 5}, 'B': {'Capacity': 3}}

    lognet = LogisticsNetwork(env, network, node_properties)

    assert lognet.node_resources['A'].capacity == 5
    assert lognet.node_resources['B'].capacity == 3

def test_log_event():

    env = simpy.Environment()
    network = {}
    node_properties = {}

    lognet = LogisticsNetwork(env, network, node_properties)

    lognet.log_event('test_event', data1='a', data2="hello", data3=1)
    assert lognet.events[0] == {'time':0, 'type':'test_event', 'data1':'a', 'data2':"hello", 'data3':1}