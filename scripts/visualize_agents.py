#!/usr/bin/env python3
"""
Visualization dashboard for agent conversations with real-time updates
"""
import asyncio
import sys
import signal
import json
from pathlib import Path
from flask import Flask, render_template
from flask_socketio import SocketIO

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from stable_genius.agents.personalities import create_agent
from stable_genius.utils.logger import logger

template_dir = PROJECT_ROOT / "templates"
template_dir.mkdir(exist_ok=True)

index_template = template_dir / "index.html"

app = Flask(__name__, template_folder=str(template_dir))
socketio = SocketIO(app, async_mode='threading')

config_dir = PROJECT_ROOT / "config"
config_dir.mkdir(exist_ok=True)

CONFIG_FILE = config_dir / "agents_config.json"

def load_config():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}. Please create this file before running.")
    
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error loading config file: {e}")

config = load_config()
agents_config = config["agents"]

@app.route('/')
def index():
    return render_template('index.html')

agents = []
conversation_active = False

@socketio.on('get_config')
def handle_get_config():
    """Send configuration to client"""
    socketio.emit('config', config)

async def run_conversation(turns=None):
    """Run a simulated conversation between agents with UI updates"""
    global agents, conversation_active
    
    if turns is None:
        turns = config.get("turns", 5)
    
    try:
        conversation_active = True
        
        agents = []
        for i, agent_config in enumerate(agents_config):
            agent = create_agent(agent_config["name"], agent_config["personality"])
            agents.append(agent)
        
        if len(agents) < 2:
            socketio.emit('add_message', {
                'sender': 'Error', 
                'message': 'Need at least 2 agents in config file'
            })
            return
        
        for i, agent in enumerate(agents):
            socketio.emit(f'update_agent{i+1}', {
                'name': agent.name,
                'personality': agent.personality,
                'tension': agent.get_psyche().tension_level,
                'memories': agent.get_psyche().memories
            })
        
        message = "Hello there!"
        socketio.emit('add_message', {'sender': 'System', 'message': 'Starting conversation...'})
        
        for turn in range(turns):
            socketio.emit('add_message', {'sender': 'System', 'message': f'Turn {turn+1}'})
            
            # Agent 1's turn with pipeline visualization
            socketio.emit('add_message', {'sender': 'System', 'message': f'Agent {agents[0].name} processing...'})
            
            # Subscribe to pipeline updates for agent 1
            def agent1_pipeline_callback(stage, data):
                socketio.emit('pipeline_update', {
                    'agent_id': 0,
                    'agent_name': agents[0].name,
                    'stage': stage,
                    'data': data
                })
            
            # Register the callback
            agents[0].pipeline.register_callback(agent1_pipeline_callback)
            
            response1 = await agents[0].receive_message(message, agents[1].name)
            message1 = response1['speech']
            agent1_psyche = agents[0].get_psyche()
            
            socketio.emit('update_agent1', {
                'name': agents[0].name,
                'personality': agents[0].personality,
                'tension': agent1_psyche.tension_level,
                'memories': agent1_psyche.memories,
                'plan': response1.get('plan', {})
            })
            
            socketio.emit('add_message', {
                'sender': agents[0].name,
                'sender_id': 0,
                'message': message1
            })
            
            await asyncio.sleep(0.5)
            
            # Agent 2's turn with pipeline visualization
            socketio.emit('add_message', {'sender': 'System', 'message': f'Agent {agents[1].name} processing...'})
            
            # Subscribe to pipeline updates for agent 2
            def agent2_pipeline_callback(stage, data):
                socketio.emit('pipeline_update', {
                    'agent_id': 1,
                    'agent_name': agents[1].name,
                    'stage': stage,
                    'data': data
                })
            
            # Register the callback
            agents[1].pipeline.register_callback(agent2_pipeline_callback)
            
            response2 = await agents[1].receive_message(message1, agents[0].name)
            message = response2['speech']
            agent2_psyche = agents[1].get_psyche()
            
            socketio.emit('update_agent2', {
                'name': agents[1].name,
                'personality': agents[1].personality,
                'tension': agent2_psyche.tension_level,
                'memories': agent2_psyche.memories,
                'plan': response2.get('plan', {})
            })
            
            socketio.emit('add_message', {
                'sender': agents[1].name,
                'sender_id': 1,
                'message': message
            })
            
            await asyncio.sleep(0.5)
        
        socketio.emit('add_message', {'sender': 'System', 'message': 'Conversation ended'})
        
    except Exception as e:
        socketio.emit('add_message', {'sender': 'Error', 'message': f'Error: {str(e)}'})
    finally:
        conversation_active = False

def signal_handler(sig, frame):
    """Handle keyboard interrupt gracefully"""
    logger.info("\nKeyboard interrupt detected. Shutting down gracefully...")
    if socketio:
        socketio.emit('add_message', {'sender': 'System', 'message': 'Server shutting down...'})
    sys.exit(0)

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    socketio.emit('add_message', {'sender': 'System', 'message': 'Connected to server successfully!'})
    if not conversation_active:
        asyncio.run(run_conversation())

def run_flask(port=5000):
    socketio.run(app, debug=True, host='0.0.0.0', port=port)

def main():
    global config, agents_config
    
    signal.signal(signal.SIGINT, signal_handler)
    
    port = 5000
    
    logger.info(f"Starting visualization server on http://localhost:{port}")
    logger.info("Open this URL in your browser to view the agent conversation")
    logger.info(f"Using agents: {', '.join([a['name'] for a in agents_config])}")
    logger.info(f"Conversation turns: {config.get('turns', 5)}")
    logger.info("Press Ctrl+C to exit")
    
    run_flask(port)
    return 0

if __name__ == "__main__":
    sys.exit(main()) 