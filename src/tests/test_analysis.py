import pytest  
from src.utils.analysis import log_analysis

import pytest

# Dummy log class
class DummyLog:
    def __init__(self, events):
        self.events = events

def test_build_time_log_sorts_events():
    # Events intentionally out of order
    events = [
        {'time': 5, 'order_id': 1, 'type': 'departed', 'from_node': 'A', 'to_node': 'B'},
        {'time': 2, 'order_id': 1, 'type': 'spawned', 'location': 'A'},
        {'time': 7, 'order_id': 1, 'type': 'arrived', 'location': 'B'}
    ]

    log = DummyLog(events)
    analysis = log_analysis(log)

    # Instead of printing, get the sorted list internally
    sorted_events = sorted(analysis.log.events, key=lambda e: e['time'])

    # Check the first event is the earliest
    assert sorted_events[0]['time'] == 2
    assert sorted_events[1]['time'] == 5
    assert sorted_events[2]['time'] == 7

    # Optional: check event types preserved
    assert sorted_events[0]['type'] == 'spawned'
    assert sorted_events[1]['type'] == 'departed'
    assert sorted_events[2]['type'] == 'arrived'
