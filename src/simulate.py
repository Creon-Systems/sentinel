import simpy
import matplotlib.pyplot as plt
import networkx as nx

from utils.network import LogisticsNetwork
from utils.process import Order
from utils.analysis import log_analysis
from utils.graphgen import *

# --------- Initialise Parameters -------- #
env = simpy.Environment()
network = {'Hub_A': {'Hub_B': {'weight': 8}, 'Hub_C': {'weight': 5}},
           'Hub_B': {'Hub_D': {'weight': 10}, 'Customer_0': {'weight': 3}},
           'Hub_C': {'Customer_1': {'weight': 3}, 'Customer_2': {'weight': 3}},
           'Hub_D': {'Customer_3': {'weight': 3}},
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

# --------- Load Variables -------- #
lognet = LogisticsNetwork(env, network, node_properties)

orders = [
    Order(lognet, 1, 'Hub_A', 'Customer_0'),
    Order(lognet, 2, 'Hub_A', 'Customer_1'),
    Order(lognet, 3, 'Hub_A', 'Customer_2'),
    Order(lognet, 4, 'Hub_A', 'Customer_3'),
]


# --------- Run Simulation -------- #
for order in orders:
    env.process(order.run())

env.run(until=40)

analysis = log_analysis(lognet)
analysis.build_time_log()

