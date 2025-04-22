"""
Agent state management for the visualization server
"""
from .config import VALID_AGENT_IDS, MAX_AGENT_MESSAGES

class AgentState:
    """Class to manage agent state and updates"""
    
    def __init__(self):
        self.states = {
            0: self._create_default_state(),
            1: self._create_default_state()
        }
        
    def _create_default_state(self):
        """Create default state for an agent"""
        return {
            'name': 'Waiting for agent...',
            'personality': '--',
            'tension': 0,
            'goal': '--',
            'pipeline': {
                'components': [],
                'stage': ''
            }
        }
    
    def update_pipeline_components(self, agent_id, components):
        """Update pipeline components for an agent"""
        if agent_id in VALID_AGENT_IDS and isinstance(components, list):
            self.states[agent_id]['pipeline']['components'] = components
    
    def update_pipeline_stage(self, agent_id, stage):
        """Update pipeline stage for an agent"""
        if agent_id in VALID_AGENT_IDS and stage and not stage.endswith('_start'):
            self.states[agent_id]['pipeline']['stage'] = stage
    
    def update_agent_info(self, agent_id, update_data):
        """Update basic agent information"""
        if agent_id not in VALID_AGENT_IDS:
            return
            
        # Update name, personality and tension if present
        for key in ['name', 'personality', 'tension']:
            if key in update_data:
                self.states[agent_id][key] = update_data[key]
        
        # Update goal if present directly in update_data
        if 'goal' in update_data:
            self.states[agent_id]['goal'] = update_data['goal']
        # Also check for goal in plan if present
        elif 'plan' in update_data and 'goal' in update_data['plan']:
            self.states[agent_id]['goal'] = update_data['plan']['goal']
            
    def add_message(self, agent_id, message):
        """Add a message from an agent to its state"""
        if agent_id in VALID_AGENT_IDS and message:
            # If the agent state doesn't already have a messages list, create one
            if 'messages' not in self.states[agent_id]:
                self.states[agent_id]['messages'] = []
                
            # Add the message and keep only the most recent MAX_AGENT_MESSAGES
            self.states[agent_id]['messages'].append(message)
            if len(self.states[agent_id]['messages']) > MAX_AGENT_MESSAGES:
                self.states[agent_id]['messages'] = self.states[agent_id]['messages'][-MAX_AGENT_MESSAGES:] 