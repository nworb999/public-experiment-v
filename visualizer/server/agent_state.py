"""
Agent state management for the visualization server
"""
import logging
from .config import VALID_AGENT_IDS, MAX_AGENT_MESSAGES

# Setup logging
logger = logging.getLogger(__name__)

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
            'personality': ' ' * 100,
            'tension': 0,
            'goal': ' ' * 120,
            'conversation_memory': '',
            'plan': {
                'tactics': [' ' * 80],
                'active_tactic': ' ' * 90
            },
            'pipeline': {
                'components': [],
                'stage': ''
            },
            'interior': {
                'summary': '',
                'principles': ' ' * 100
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
            
        logger.debug(f"Updating agent {agent_id} with data: {update_data}")
            
        # Update name, personality, tension, conversation_memory and interior if present
        for key in ['name', 'personality', 'conversation_memory', 'interior']:
            if key in update_data:
                self.states[agent_id][key] = update_data[key]
        # Handle tension logic: use numerical tension_level, not tension_interpretation
        if 'tension_level' in update_data:
            self.states[agent_id]['tension'] = update_data['tension_level']
        elif 'tension' in update_data:
            self.states[agent_id]['tension'] = update_data['tension']
        
        # Update goal if present directly in update_data (including None values)
        if 'goal' in update_data:
            goal_value = update_data['goal']
            # Convert None to a more user-friendly display
            self.states[agent_id]['goal'] = goal_value if goal_value is not None else 'No goal set'
            logger.debug(f"Updated goal for agent {agent_id}: {update_data['goal']} -> display: {self.states[agent_id]['goal']}")
        # Also check for goal in plan if present
        elif 'plan' in update_data and isinstance(update_data['plan'], dict) and 'goal' in update_data['plan']:
            goal_value = update_data['plan']['goal']
            self.states[agent_id]['goal'] = goal_value if goal_value is not None else 'No goal set'
            logger.debug(f"Updated goal from plan for agent {agent_id}: {update_data['plan']['goal']} -> display: {self.states[agent_id]['goal']}")
            
        # Handle plan updates
        if 'plan' in update_data:
            plan_data = update_data['plan']
            logger.debug(f"Processing plan data for agent {agent_id}: {plan_data}")
            
            # Handle different plan formats
            if isinstance(plan_data, list):
                # If plan is a list, assume it's tactics
                logger.debug(f"Plan is a list, treating as tactics for agent {agent_id}")
                self.states[agent_id]['plan']['tactics'] = plan_data
                
                # If active_tactic isn't set and we have tactics, set the first one
                if (self.states[agent_id]['plan'].get('active_tactic') is None and 
                    len(plan_data) > 0):
                    self.states[agent_id]['plan']['active_tactic'] = plan_data[0]
                    logger.debug(f"Set first tactic as active for agent {agent_id}: {plan_data[0]}")
            elif isinstance(plan_data, dict):
                logger.debug(f"Plan is a dictionary for agent {agent_id}")
                if self.states[agent_id].get('plan') is None:
                    self.states[agent_id]['plan'] = {}
                    
                # Copy all plan fields
                for key, value in plan_data.items():
                    self.states[agent_id]['plan'][key] = value
                    logger.debug(f"Updated plan.{key} for agent {agent_id} to: {value}")
                    
                # Convert tactic to tactics array if present
                if 'tactic' in plan_data and 'tactics' not in plan_data:
                    self.states[agent_id]['plan']['tactics'] = [plan_data['tactic']]
                    logger.debug(f"Converted single tactic to tactics array for agent {agent_id}")
                
                # Check for tactics in the plan data
                if 'tactics' in plan_data:
                    logger.debug(f"Found tactics in plan data for agent {agent_id}: {plan_data['tactics']}")
                    self.states[agent_id]['plan']['tactics'] = plan_data['tactics']
                
                # Update active_tactic if present
                if 'active_tactic' in plan_data:
                    self.states[agent_id]['plan']['active_tactic'] = plan_data['active_tactic']
                    logger.debug(f"Updated active_tactic for agent {agent_id} to: {plan_data['active_tactic']}")
                # Set first tactic as active if we have tactics but no active_tactic
                elif ('tactics' in plan_data and plan_data['tactics'] and 
                      'active_tactic' not in self.states[agent_id]['plan']):
                    self.states[agent_id]['plan']['active_tactic'] = plan_data['tactics'][0]
                    logger.debug(f"Set first tactic from tactics as active for agent {agent_id}: {plan_data['tactics'][0]}")
            
            # Log the final plan state
            logger.debug(f"Final plan state for agent {agent_id}: {self.states[agent_id]['plan']}")
            
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