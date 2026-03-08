""" Create a random network and random capacities in a dict of dict format """
import networkx as nx
import random 

from utils.process import Order


def network_generation(base_topology: str, n: int, seed=None, **overrides):
    """ Generate a random directed graph in dict of dict format. 
    The graph is guaranteed to be strongly connected. """
    DEFAULTS = {
    "ER": {"p": 0.1, "weight_low": 1, "weight_upper": 10},
    "BA": {"m": 2, "weight_low": 1, "weight_upper": 10},
    "WS": {"k": 4, "p": 0.1, "weight_low": 1, "weight_upper": 10},
    }
    params = DEFAULTS[base_topology].copy()
    params.update(overrides)  # overrides from CLI

    # three types of graph
    # 1. random (Erdos-Reyni)
    if base_topology == 'ER':
        p = params.get("p")
        G = nx.erdos_renyi_graph(n, p=p, seed=seed, directed=True)
    
    # 2. preferential (Barabasi Albert) 
    elif base_topology == 'BA':
        m = params.get("m")
        G = nx.barabasi_albert_graph(n, m=m, seed=seed)
        G = nx.DiGraph(G)  # Make directed

    # 3. scale-free (Watts-Strogatz)
    elif base_topology == 'WS':
        p = params.get("p")
        k = params.get("k")
        G = nx.watts_strogatz_graph(n, k=k, p=p, seed=seed)
        G = nx.DiGraph(G)  # Make directed

    else:
        raise ValueError("Invalid base topology, choose ER, BA, or WS")

    # stitch sccs if not strongly connected
    sccs = list(nx.strongly_connected_components(G))
    if len(sccs) > 1:
        reps = [next(iter(c)) for c in sccs]
        for i in range(len(reps)):
            u = reps[i]
            v = reps[(i+1) % len(reps)]
            G.add_edge(u, v)

    # assign weights to all edges
    for u, v in G.edges():
        weight_low = params.get("weight_low")
        weight_upper = params.get("weight_upper")
        G[u][v]['weight'] = random.randint(weight_low, weight_upper)

    return nx.to_dict_of_dicts(G)

    
def node_property_generation(dict_of_dicts, cap_low, cap_high):
    """ Generate random node properties (e.g., capacity) in a dict format. """
    attr_dict = {}
    for node in dict_of_dicts.keys():
        attr_dict[node]= {'Capacity': random.randint(cap_low, cap_high)}
    return attr_dict
    
def order_gen(network, num_orders):
    """ Generate random orders with source and target nodes. 
    Ensure that the target is reachable from the source. """
    orders = []
    for id in range(num_orders):
        source = random.choice(list(network.graph.nodes()))
        reachable_nodes = list(nx.descendants(network.graph, source))
        if not reachable_nodes:
            continue  # or pick a new source
        target = random.choice(reachable_nodes)
        orders.append(Order(network, id, source, target))
    return orders