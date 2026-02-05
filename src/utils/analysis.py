# import libraries

class log_analysis:

    def __init__(self, log):
        self.log = log 

    def build_time_log(self):
        
        time_log = sorted(self.log.events, key=lambda event: event['time'])

        print("SIMULATION EVENT LOG")
        print("="*70)
        
        for event in time_log:
            t = event['time']
            order_id = event['order_id']
            event_type = event['type']
            
            if event_type == 'departed':
                print(f"[t={t:>3}] Order {order_id}: {event['from_node']} → {event['to_node']}")
            elif event_type == 'arrived':
                print(f"[t={t:>3}] Order {order_id}: Arrived at {event['location']}")
            elif event_type == 'queue_entered':
                print(f"[t={t:>3}] Order {order_id}: Waiting at {event['hub']} (queue: {event['queue_length']})")
            elif event_type == 'capacity_secured':
                print(f"[t={t:>3}] Order {order_id}: Secured capacity at {event['hub']}")
            elif event_type == 'delivered':
                print(f"[t={t:>3}] Order {order_id}: Delivered to {event['destination']}")
    
    print("="*70)
    
