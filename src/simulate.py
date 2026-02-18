import simpy
import matplotlib.pyplot as plt
import networkx as nx

from utils.network import LogisticsNetwork
from utils.process import Order
from utils.analysis import log_analysis
from utils.generator import *

import random

# --------- Initialise Parameters -------- #
env = simpy.Environment()

random.seed(3)
network = network_generation('ER', n=5, p=0.3, weight_low=1, weight_upper=10)
node_properties = node_property_generation(network, 1, 3)

print(network)
print(node_properties)

# --------- Load Variables -------- #
lognet = LogisticsNetwork(env, network, node_properties)
orders = order_gen(lognet, num_orders=10)

# --------- Run Simulation -------- #
for order in orders:
    env.process(order.run())

env.run(until=40)

analysis = log_analysis(lognet)
analysis.build_time_log()

