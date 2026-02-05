import simpy
import matplotlib.pyplot as plt
import networkx as nx
from utils.network import LogisticsNetwork
from utils.process import Order

# --------- Parameter Logic -------- #
env = simpy.Environment()
network = {'Hub_A': {'Hub_B': 8, 'Hub_C': 5},
           'Hub_B': {'Hub_D': 10, 'Customer_0': 3},
           'Hub_C': {'Customer_1': 3, 'Customer_2': 3},
           'Hub_D': {'Customer_3': 1},
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

lognet = LogisticsNetwork(env, network, node_properties)

orders = [
    Order(lognet, 1, 'Hub_A', 'Customer_0'),
    Order(lognet, 2, 'Hub_A', 'Customer_1'),
    Order(lognet, 3, 'Hub_A', 'Customer_2'),
    Order(lognet, 4, 'Hub_A', 'Customer_3'),
]

for order in orders:
    env.process(order.run())

def visualize_from_events(lognet):
    """Create a simple visualization from logged events"""
    
    # Get network layout
    pos = nx.spring_layout(lognet.graph, seed=42)
    
    # Get all unique times from events
    times = sorted(set(e['time'] for e in lognet.events))
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    def get_order_positions_at_time(t):
        """Reconstruct where each order is at time t"""
        positions = {}  # {order_id: (location, status)}
        
        for event in lognet.events:
            if event['time'] > t:
                break
            
            order_id = event['order_id']
            
            if event['type'] == 'spawned':
                positions[order_id] = (event['location'], 'at_node')
            
            elif event['type'] == 'departed':
                positions[order_id] = ((event['from_node'], event['to_node']), 'in_transit')
            
            elif event['type'] == 'arrived':
                positions[order_id] = (event['location'], 'at_node')
            
            elif event['type'] == 'delivered':
                positions[order_id] = (event['destination'], 'delivered')
        
        return positions
    
    # Animate through time steps
    from matplotlib.animation import FuncAnimation
    
    def animate(frame):
        ax.clear()
        t = times[min(frame, len(times)-1)]
        
        # Draw network
        hubs = [n for n in lognet.graph.nodes() if n.startswith('Hub')]
        customers = [n for n in lognet.graph.nodes() if n.startswith('Customer')]
        
        nx.draw_networkx_edges(lognet.graph, pos, ax=ax, alpha=0.3)
        nx.draw_networkx_nodes(lognet.graph, pos, nodelist=hubs, 
                              node_color='lightblue', node_size=1000, ax=ax)
        nx.draw_networkx_nodes(lognet.graph, pos, nodelist=customers, 
                              node_color='lightgreen', node_size=700, ax=ax)
        nx.draw_networkx_labels(lognet.graph, pos, ax=ax)
        
        # Get order positions at this time
        positions = get_order_positions_at_time(t)
        
        # Draw orders
        colors = plt.cm.Set1(range(10))
        for order_id, (location, status) in positions.items():
            if status == 'at_node' or status == 'delivered':
                node_pos = pos[location]
                color = colors[order_id % 10]
                alpha = 0.3 if status == 'delivered' else 1.0
                
                ax.scatter(node_pos[0], node_pos[1], s=300, c=[color], 
                          marker='o', edgecolors='black', linewidths=2, 
                          alpha=alpha, zorder=10)
                ax.text(node_pos[0], node_pos[1], str(order_id), 
                       ha='center', va='center', fontweight='bold')
            
            elif status == 'in_transit':
                from_node, to_node = location
                # Draw on edge (simplified - just at midpoint)
                from_pos = pos[from_node]
                to_pos = pos[to_node]
                mid_pos = ((from_pos[0] + to_pos[0])/2, (from_pos[1] + to_pos[1])/2)
                
                color = colors[order_id % 10]
                ax.scatter(mid_pos[0], mid_pos[1], s=300, c=[color], 
                          marker='D', edgecolors='black', linewidths=2, zorder=10)
                ax.text(mid_pos[0], mid_pos[1], str(order_id), 
                       ha='center', va='center', fontweight='bold', fontsize=9)
        
        ax.set_title(f'Logistics Network at t={t}', fontsize=14, fontweight='bold')
        ax.axis('off')
    
    anim = FuncAnimation(fig, animate, frames=len(times), interval=500, repeat=True)
    plt.tight_layout()
    plt.show()
    
    return anim


# After running simulation:
env.run(until=40)
print(f"Completed: {lognet.completed_deliveries}")

# Print events for debugging
print("\n=== EVENT LOG ===")
for event in lognet.events[:20]:  # First 20 events
    print(f"t={event['time']:>3}: {event['type']:<15} {event}")

# Visualize
anim = visualize_from_events(lognet)
# --------- Parameter Logic -------- #