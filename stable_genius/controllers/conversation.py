import asyncio
import json
import requests
from pathlib import Path
from flask import jsonify

from stable_genius.agents.personalities import create_agent
from stable_genius.core.components import TriggerComponent, IntentClassifierComponent
from stable_genius.utils.logger import logger
from stable_genius.models.psyche import Psyche

# Global variables for active conversations
active_conversations = {}

# Config directory and file
config_dir = Path(__file__).parent.parent.parent / "config"
CONFIG_FILE = config_dir / "agents_config.json"

def send_to_visualizer(data, visualizer_url="http://localhost:5000/api/update"):
    """Send data to visualization server"""
    # Log data being sent to visualizer
    if 'event_type' in data:
        if data['event_type'] == 'agent_update' and 'plan' in data:
            logger.debug(f"Sending agent_update to visualizer for agent {data.get('agent_id')}")
            logger.debug(f"Plan data: {data['plan']}")
            
        elif data['event_type'] == 'initialize_agents' and 'agents' in data:
            logger.debug(f"Sending initialize_agents to visualizer with {len(data['agents'])} agents")
            for i, agent in enumerate(data['agents']):
                logger.debug(f"Agent {i} data: name={agent.get('name')}, plan={agent.get('plan')}")
    
    # Send data to visualizer
    try:
        response = requests.post(visualizer_url, json=data, timeout=1)
        return response.status_code == 200
    except requests.RequestException:
        return False

def load_config():
    """Load agent configuration from file"""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}. Please create this file before running.")
    
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error loading config file: {e}")

def get_conversation_status(conversation_id):
    """Get the status of a specific conversation"""
    if conversation_id in active_conversations:
        return active_conversations[conversation_id]
    return None

def list_all_conversations():
    """List all active conversations"""
    return {
        'active_conversations': list(active_conversations.keys()),
        'conversation_count': len(active_conversations)
    }

def stop_conversation(conversation_id):
    """Stop an active conversation"""
    if conversation_id in active_conversations:
        active_conversations.pop(conversation_id)
        return {
            'status': 'stopped',
            'conversation_id': conversation_id
        }
    return {
        'status': 'error',
        'message': f'Conversation {conversation_id} not found'
    }, 404

async def create_agents(agents_config, llm_service):
    """Create agent instances based on configuration"""
    if len(agents_config) < 2:
        raise ValueError("Need at least 2 agents in config file")
    
    # Clear memories for all agents before starting
    logger.debug("Clearing memories from previous runs...")
    for agent_config in agents_config:
        Psyche.clear_all_memories(agent_config["name"])
    
    # Create agents
    agent1 = create_agent(agents_config[0]["name"], agents_config[0]["personality"], llm_service)
    agent2 = create_agent(agents_config[1]["name"], agents_config[1]["personality"], llm_service)
    
    return agent1, agent2

async def send_agent_data_to_visualizer(agents, visualizer_url):
    """Send initial agent information to visualizer"""
    for i, agent in enumerate(agents):
        agent_psyche = agent.get_psyche()
        logger.debug(f"send_agent_data_to_visualizer: agent {i} plan={agent_psyche.plan}, active_tactic={agent_psyche.active_tactic}")
        plan_payload = {
            "tactics": agent_psyche.plan or [],
            "active_tactic": agent_psyche.active_tactic
        }
        logger.debug(f"send_agent_data_to_visualizer: sending plan payload: {plan_payload}")
        send_to_visualizer({
            'event_type': 'agent_update',
            'agent_id': i,
            'name': agent.name,
            'personality': agent.personality,
            'tension': agent_psyche.tension_level,
            'memories': agent_psyche.memories,
            'plan': plan_payload
        }, visualizer_url)

async def send_agent_initialization(agents, visualizer_url):
    """Send initial static agent information to visualizer"""
    agents_data = []
    for i, agent in enumerate(agents):
        agent_psyche = agent.get_psyche()
        logger.debug(f"send_agent_initialization: agent {i} plan={agent_psyche.plan}, active_tactic={agent_psyche.active_tactic}")
        plan_payload = {
            "tactics": agent_psyche.plan or [],
            "active_tactic": agent_psyche.active_tactic
        }
        logger.debug(f"send_agent_initialization: sending plan payload: {plan_payload}")
        component_names = [component.name for component in agent.pipeline.components]
        agents_data.append({
            'agent_id': i,
            'name': agent.name,
            'personality': agent.personality,
            'tension': agent_psyche.tension_level,
            'goal': agent_psyche.goal,
            'plan': plan_payload,
            'components': component_names  # Include component names
        })
    logger.debug(f"Sending initialize_agents event with data: {agents_data}")
    send_to_visualizer({
        'event_type': 'initialize_agents',
        'agents': agents_data
    }, visualizer_url)

async def setup_agent_pipeline(agent, agent_id, conversation_id, turn, visualizer_url, conversation_start=False):
    """Setup the agent's pipeline with appropriate callbacks"""
    # Clear existing callbacks to prevent accumulation
    agent.pipeline.callbacks = []
    
    # If conversation_start is True, temporarily remove the trigger and intent classification components
    original_components = None
    if conversation_start:
        original_components = agent.pipeline.components.copy()
        agent.pipeline.components = [
            c for c in original_components 
            if not isinstance(c, (TriggerComponent, IntentClassifierComponent))
        ]
    
    # Define pipeline callback
    def pipeline_callback(stage, data):
        if stage == "llm_call":
            # Add context to the interaction data
            interaction_context = {
                'conversation_id': conversation_id,
                'turn': turn,
                'agent': agent.name
            }
            
            # Update LLM data with context
            data.update(interaction_context)
            
            # Send LLM interaction to visualizer
            send_to_visualizer({
                'event_type': 'llm_interaction',
                'prompt': data.get('prompt', ''),
                'response': data.get('response', ''),
                'elapsed_time': data.get('elapsed_time', '--'),
                'agent': agent.name,
                'turn': turn,
                'step_title': data.get('step_title', '')
            }, visualizer_url)
        
        send_to_visualizer({
            'event_type': 'pipeline_update',
            'agent_id': agent_id,
            'agent_name': agent.name,
            'stage': stage,
            'data': data
        }, visualizer_url)
    
    # Register pipeline callback
    agent.pipeline.register_callback(pipeline_callback)
    
    # Return a cleanup function to restore original components if needed
    def cleanup():
        if original_components is not None:
            agent.pipeline.components = original_components
    
    return cleanup

async def process_agent_turn(agent, other_agent_name, message, agent_id, visualizer_url, turn=0):
    """Process a single agent's turn in the conversation"""
    try:
        response = await agent.receive_message(message, other_agent_name)
        message_out = response['speech']
        # Get current psyche state
        agent_psyche = agent.get_psyche()
        logger.debug(f"process_agent_turn: agent {agent_id} plan={agent_psyche.plan}, active_tactic={agent_psyche.active_tactic}")
        plan_payload = {
            "tactics": agent_psyche.plan or [],
            "active_tactic": agent_psyche.active_tactic
        }
        logger.debug(f"process_agent_turn: sending plan payload: {plan_payload}")
        logger.info(f"{agent.name} ({agent_psyche.tension_level}/100 tension):")
        logger.info(f"  \"{message_out}\"\n")
        # Send agent update to visualizer
        send_to_visualizer({
            'event_type': 'agent_update',
            'agent_id': agent_id,
            'name': agent.name,
            'personality': agent.personality,
            'tension': agent_psyche.tension_level,
            'memories': agent_psyche.memories,
            'conversation_memory': agent_psyche.conversation_memory,
            'plan': plan_payload
        }, visualizer_url)
        send_to_visualizer({
            'event_type': 'add_message',
            'sender': agent.name,
            'sender_id': agent_id,
            'message': message_out
        }, visualizer_url)
        return message_out, response
    except Exception as e:
        logger.error(f"Error during agent turn: {str(e)}")
        send_to_visualizer({
            'event_type': 'add_message',
            'sender': 'Error',
            'message': f'Error during agent turn: {str(e)}'
        }, visualizer_url)
        return "I'm not sure I understood that. Can you try again?", None

async def initialize_conversation(conversation_id, config, visualizer_url, llm_service):
    """Initialize a new conversation between agents"""
    # Mark conversation as active
    active_conversations[conversation_id] = {'status': 'running', 'turn': 0}
    
    # Get agent configs and validate
    agents_config = config["agents"]
    
    # Send config to visualizer
    send_to_visualizer({
        'event_type': 'config',
        'config': config
    }, visualizer_url)
    
    send_to_visualizer({
        'event_type': 'add_message',
        'sender': 'System',
        'message': f'Starting conversation {conversation_id}...'
    }, visualizer_url)
    
    # Create and initialize agents
    agent1, agent2 = await create_agents(agents_config, llm_service)
    
    # Send initialization data for static properties
    await send_agent_initialization([agent1, agent2], visualizer_url)
    
    # Send regular agent data updates
    await send_agent_data_to_visualizer([agent1, agent2], visualizer_url)
    
    # Log start of conversation
    turns = config.get("turns", 5)
    logger.info(f"========== Starting Conversation {conversation_id} between {agent1.name} and {agent2.name} ==========\n")
    logger.info(f"Conversation turns: {turns}\n")
    
    return agent1, agent2, turns

async def execute_conversation_turn(i, conversation_id, agent1, agent2, message, visualizer_url):
    """Execute a single turn of conversation between two agents"""
    if conversation_id not in active_conversations:
        # Conversation was stopped externally
        return None
        
    active_conversations[conversation_id]['turn'] = i + 1
    logger.debug(f"\n\n---------- Turn {i+1} ----------\n")
    
    send_to_visualizer({
        'event_type': 'add_message',
        'sender': 'System',
        'message': f'Turn {i+1}'
    }, visualizer_url)
    
    # Agent 1's turn
    send_to_visualizer({
        'event_type': 'add_message',
        'sender': 'System',
        'message': f'Agent {agent1.name} processing...'
    }, visualizer_url)
    
    # Skip trigger and intent classification for first agent's first utterance
    cleanup1 = await setup_agent_pipeline(agent1, 0, conversation_id, i + 1, visualizer_url, conversation_start=(i == 0))
    message1, _ = await process_agent_turn(agent1, agent2.name, message, 0, visualizer_url, i + 1)
    cleanup1()  # Restore original components
    
    # Agent 2's turn
    send_to_visualizer({
        'event_type': 'add_message',
        'sender': 'System',
        'message': f'Agent {agent2.name} processing...'
    }, visualizer_url)
    
    cleanup2 = await setup_agent_pipeline(agent2, 1, conversation_id, i + 1, visualizer_url)
    message2, _ = await process_agent_turn(agent2, agent1.name, message1, 1, visualizer_url, i + 1)
    cleanup2()  # Restore original components
    
    return message2

async def finalize_conversation(conversation_id, agent1, agent2, visualizer_url):
    """Finalize and clean up a conversation"""
    # Log conversation summary
    await log_conversation_summary(agent1, agent2)
    
    # Notify visualizer
    send_to_visualizer({
        'event_type': 'add_message',
        'sender': 'System',
        'message': 'Conversation ended'
    }, visualizer_url)
    
    # Update conversation status
    active_conversations[conversation_id]['status'] = 'completed'

async def handle_conversation_error(conversation_id, error, visualizer_url):
    """Handle any errors that occur during conversation"""
    error_message = str(error)
    logger.error(f"An unexpected error occurred: {error_message}")
    
    # Notify visualizer of error
    send_to_visualizer({
        'event_type': 'add_message',
        'sender': 'Error',
        'message': f'An unexpected error occurred: {error_message}'
    }, visualizer_url)
    
    # Update conversation status
    active_conversations[conversation_id]['status'] = 'error'
    active_conversations[conversation_id]['error'] = error_message

async def run_conversation(conversation_id, visualizer_url="http://localhost:5000/api/update", llm_service=None):
    """Run a simulated conversation between two agents"""
    if llm_service is None:
        raise ValueError("LLM service must be provided")
        
    try:
        # Load config and initialize conversation
        config = load_config()
        agent1, agent2, turns = await initialize_conversation(
            conversation_id, config, visualizer_url, llm_service
        )
        
        # Start with a greeting
        # TODO make this dynamic
        message = "Hello there!"
        
        # Run conversation turns
        for i in range(turns):
            new_message = await execute_conversation_turn(
                i, conversation_id, agent1, agent2, message, visualizer_url
            )
            if new_message is None:
                # Conversation was stopped externally
                break
            message = new_message
        
        # Finalize the conversation
        await finalize_conversation(conversation_id, agent1, agent2, visualizer_url)
        
    except Exception as e:
        # Handle any errors
        await handle_conversation_error(conversation_id, e, visualizer_url)

async def log_conversation_summary(agent1, agent2):
    """Log summary information about the conversation"""
    logger.info("\n\n========== Conversation Ended ==========\n")
    agent1_psyche = agent1.get_psyche()
    agent2_psyche = agent2.get_psyche()
    logger.debug(f"{agent1.name}'s final state: {agent1_psyche.tension_level}/100 tension")
    logger.debug(f"{agent2.name}'s final state: {agent2_psyche.tension_level}/100 tension")
    logger.debug(f"{agent1.name}'s memories:")
    for memory in agent1_psyche.memories:
        logger.debug(f"  - {memory}")
    logger.debug(f"{agent2.name}'s memories:")
    for memory in agent2_psyche.memories:
        logger.debug(f"  - {memory}")

# Simple module test
if __name__ == "__main__":
    from stable_genius.utils.llm import OllamaLLM
    import asyncio
    
    async def test_run():
        print("Starting test conversation...")
        llm = OllamaLLM()
        conversation_id = "test_conversation"
        try:
            await run_conversation(conversation_id, llm_service=llm)
            print(f"Conversation completed with state: {active_conversations.get(conversation_id, {})}")
        except Exception as e:
            print(f"Test failed with error: {str(e)}")
    
    asyncio.run(test_run())
