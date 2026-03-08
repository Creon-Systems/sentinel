"""
Unit tests for NodeStatusManager
"""
import pytest
import simpy
from src.utils.node_status import NodeStatusManager, NodeState


@pytest.fixture
def env():
    """Create a SimPy environment for testing"""
    return simpy.Environment()


@pytest.fixture
def manager(env):
    """Create a NodeStatusManager with test nodes"""
    nodes = ['node_A', 'node_B', 'node_C']
    return NodeStatusManager(env, nodes)


class TestNodeStatusManager:
    """Test suite for NodeStatusManager"""
    
    def test_initialization(self, manager):
        """Test that all nodes start in ACTIVE state"""
        assert manager.get_node_state('node_A') == NodeState.ACTIVE
        assert manager.get_node_state('node_B') == NodeState.ACTIVE
        assert manager.get_node_state('node_C') == NodeState.ACTIVE
    
    def test_fail_node(self, manager):
        """Test failing a node"""
        manager.fail_node('node_A')
        assert manager.get_node_state('node_A') == NodeState.FAILED
        assert not manager.is_operational('node_A')
    
    def test_recover_node(self, manager):
        """Test recovering a failed node"""
        manager.fail_node('node_A')
        assert manager.get_node_state('node_A') == NodeState.FAILED
        
        manager.recover_node('node_A')
        assert manager.get_node_state('node_A') == NodeState.ACTIVE
        assert manager.is_operational('node_A')
    
    def test_degrade_node(self, manager):
        """Test degrading a node's capacity"""
        manager.degrade_node('node_B', capacity_reduction=0.5)
        assert manager.get_node_state('node_B') == NodeState.DEGRADED
        assert manager.is_operational('node_B')  # Still operational
    
    def test_is_operational(self, manager):
        """Test is_operational for different states"""
        # ACTIVE should be operational
        assert manager.is_operational('node_A')
        
        # DEGRADED should be operational
        manager.degrade_node('node_A')
        assert manager.is_operational('node_A')
        
        # FAILED should not be operational
        manager.fail_node('node_A')
        assert not manager.is_operational('node_A')
    
    def test_unknown_node_is_operational(self, manager):
        """Test that unknown nodes are assumed operational"""
        assert manager.is_operational('unknown_node')
    
    def test_invalid_node_raises_error(self, manager):
        """Test that operations on invalid nodes raise errors"""
        with pytest.raises(ValueError):
            manager.set_node_state('invalid_node', NodeState.FAILED)
    
    def test_get_status_summary(self, manager):
        """Test getting status summary of all nodes"""
        manager.fail_node('node_A')
        manager.degrade_node('node_B')
        
        summary = manager.get_status_summary()
        
        assert summary['node_A'] == 'failed'
        assert summary['node_B'] == 'degraded'
        assert summary['node_C'] == 'active'
    
    def test_status_history(self, manager):
        """Test that status changes are recorded in history"""
        assert len(manager.status_history) == 0
        
        manager.fail_node('node_A')
        assert len(manager.status_history) == 1
        
        manager.degrade_node('node_B', capacity_reduction=0.5)
        assert len(manager.status_history) == 2
        
        # Check the recorded history
        history_entry = manager.status_history[0]
        assert history_entry['node'] == 'node_A'
        assert history_entry['old_state'] == NodeState.ACTIVE
        assert history_entry['new_state'] == NodeState.FAILED
    
    def test_status_history_timestamps(self, env, manager):
        """Test that status changes record correct timestamps"""
        manager.fail_node('node_A')
        assert manager.status_history[0]['time'] == 0
        
        env.run(until=10)
        manager.fail_node('node_B')
        assert manager.status_history[1]['time'] == 10
    
    def test_multiple_state_transitions(self, manager):
        """Test multiple state transitions on the same node"""
        manager.fail_node('node_A')
        assert manager.get_node_state('node_A') == NodeState.FAILED
        
        manager.recover_node('node_A')
        assert manager.get_node_state('node_A') == NodeState.ACTIVE
        
        manager.degrade_node('node_A', capacity_reduction=0.3)
        assert manager.get_node_state('node_A') == NodeState.DEGRADED
        
        assert len(manager.status_history) == 3
