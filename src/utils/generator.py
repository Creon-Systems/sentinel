""" Create a random network and random capacities in a dict of dict format """
import networkx as nx
import random 

from utils.process import Order


def network_generation(base_topology, n, p, weight_low, weight_upper, seed=None):
    # three types of graph
    # 1. random (erdos-reyni)
    if base_topology == "ER":
        graph = nx.erdos_renyi_graph(n, p, seed, directed=True)
        sccs = list(nx.strongly_connected_components(graph))

        # If already strongly connected, add weights
        if len(sccs) == 1:
            pass
        else: # connect first node of each group to each other
            connect_nodes = [next(iter(component)) for component in sccs]
            # stich them up
            for i in range(len(connect_nodes)):
                u = connect_nodes[i]
                v = connect_nodes[(i+1) % len(connect_nodes)]
                graph.add_edge(u,v)

        for u,v in graph.edges():
            graph[u][v]['weight'] = random.randint(weight_low, weight_upper)


        dict_of_dicts = nx.to_dict_of_dicts(graph)
        return dict_of_dicts
    
def node_property_generation(dict_of_dicts, cap_low, cap_high):
    attr_dict = {}
    for node in dict_of_dicts.keys():
        attr_dict[node]= {'Capacity': random.randint(cap_low, cap_high)}
    return attr_dict
    
def order_gen(network, num_orders):
    orders = []
    for id in range(num_orders):
        source = random.choice(list(network.graph.nodes()))
        reachable_nodes = list(nx.descendants(network.graph, source))
        if not reachable_nodes:
            continue  # or pick a new source
        target = random.choice(reachable_nodes)
        orders.append(Order(network, id, source, target))
    return orders