#!/usr/bin/env python3
"""
Visualization dashboard for agent conversations with real-time updates
"""
import asyncio
import sys
import signal
import json
import requests
import argparse
from pathlib import Path
from flask import Flask, render_template, request, url_for, jsonify
from flask_socketio import SocketIO

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from stable_genius.utils.logger import logger

template_dir = PROJECT_ROOT / "templates"
template_dir.mkdir(exist_ok=True)

index_template = template_dir / "index.html"

app = Flask(__name__, 
    template_folder=str(template_dir),
    static_folder=str(template_dir),
    static_url_path=''
)
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

# Track conversation state
conversation_active = False
current_conversation_id = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/update', methods=['POST'])
def receive_update():
    """Receive updates from the conversation API server"""
    update_data = request.json
    event_type = update_data.get('event_type')
    
    if event_type == 'config':
        socketio.emit('config', update_data.get('config', {}))
    elif event_type == 'initialize_agents':
        # Send initialization data for agents
        socketio.emit('initialize_agents', {
            'agents': update_data.get('agents', [])
        })
    elif event_type == 'llm_interaction':
        socketio.emit('llm_interaction', {
            'prompt': update_data.get('prompt', ''),
            'response': update_data.get('response', ''),
            'elapsed_time': f"{update_data.get('elapsed_time', '--')}s" if update_data.get('elapsed_time') not in [None, '--'] else '--'
        })
    elif event_type == 'message':
        socketio.emit('add_message', {
            'sender': update_data.get('sender', 'System'),
            'sender_id': update_data.get('sender_id', None),
            'message': update_data.get('message', '')
        })
    elif event_type == 'agent_update':
        agent_id = update_data.get('agent_id', 0)
        socketio.emit(f'update_agent{agent_id+1}', {
            'name': update_data.get('name', ''),
            'personality': update_data.get('personality', ''),
            'tension': update_data.get('tension', 0),
            'memories': update_data.get('memories', []),
            'plan': update_data.get('plan', {})
        })
    elif event_type == 'pipeline_update':
        socketio.emit('pipeline_update', {
            'agent_id': update_data.get('agent_id', 0),
            'agent_name': update_data.get('agent_name', ''),
            'stage': update_data.get('stage', ''),
            'data': update_data.get('data', {})
        })
    
    return jsonify({'status': 'success'})

@socketio.on('get_config')
def handle_get_config():
    """Send configuration to client"""
    socketio.emit('config', config)

def start_conversation(api_url):
    """Start a new conversation by calling the conversation API server"""
    global conversation_active, current_conversation_id
    
    if conversation_active:
        logger.info("A conversation is already active")
        return
    
    try:
        # Set up the visualization URL
        vis_url = f"http://localhost:{app.config['PORT']}/api/update"
        
        # Call the conversation API server to start a conversation
        response = requests.post(
            f"{api_url}/api/start-conversation",
            json={
                'visualizer_url': vis_url
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            conversation_active = True
            current_conversation_id = data.get('conversation_id')
            logger.info(f"Started conversation with ID: {current_conversation_id}")
            socketio.emit('add_message', {
                'sender': 'System',
                'message': f'Started conversation with ID: {current_conversation_id}'
            })
        else:
            logger.error(f"Failed to start conversation: {response.status_code} {response.text}")
            socketio.emit('add_message', {
                'sender': 'Error',
                'message': f'Failed to start conversation: {response.status_code} {response.text}'
            })
    except requests.RequestException as e:
        logger.error(f"Error connecting to conversation API server: {str(e)}")
        socketio.emit('add_message', {
            'sender': 'Error',
            'message': f'Error connecting to conversation API server: {str(e)}'
        })

def check_conversation_status(api_url):
    """Check the status of the current conversation"""
    global conversation_active, current_conversation_id
    
    if not current_conversation_id:
        return
    
    try:
        response = requests.get(
            f"{api_url}/api/conversation-status/{current_conversation_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            
            if status in ['completed', 'error']:
                conversation_active = False
                socketio.emit('add_message', {
                    'sender': 'System',
                    'message': f'Conversation {current_conversation_id} {status}'
                })
                current_conversation_id = None
        elif response.status_code == 404:
            conversation_active = False
            current_conversation_id = None
    except requests.RequestException:
        # Ignore connection errors during status checks
        pass

def signal_handler(sig, frame):
    """Handle keyboard interrupt gracefully"""
    logger.info("Keyboard interrupt detected. Shutting down gracefully...")
    if socketio:
        socketio.emit('add_message', {'sender': 'System', 'message': 'Server shutting down...'})
    sys.exit(0)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    socketio.emit('add_message', {'sender': 'System', 'message': 'Connected to server successfully!'})
    
    # Only auto-start if not in debug mode and no conversation is active
    if not conversation_active and app.config.get('AUTO_START', False) and not app.debug:
        start_conversation(app.config.get('API_URL', 'http://localhost:8000'))

def poll_conversation_status():
    """Background task to poll the conversation status"""
    while True:
        check_conversation_status(app.config.get('API_URL', 'http://localhost:8000'))
        socketio.sleep(2)

def run_flask(port=5000, api_url='http://localhost:8000', auto_start=True):
    """Run the Flask server"""
    app.config['PORT'] = port
    app.config['API_URL'] = api_url
    app.config['AUTO_START'] = auto_start
    
    # Start background task to poll conversation status
    socketio.start_background_task(poll_conversation_status)
    
    socketio.run(app, debug=False, host='0.0.0.0', port=port)

def main():
    global config, agents_config
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run a visualization server for agent conversations")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the visualization server on")
    parser.add_argument("--api-url", default="http://localhost:8000", help="URL of the conversation API server")
    parser.add_argument("--no-auto-start", action="store_true", help="Disable auto-starting a conversation on connect")
    args = parser.parse_args()
    
    port = args.port
    api_url = args.api_url
    auto_start = not args.no_auto_start
    
    logger.info(f"Starting visualization server on http://localhost:{port}")
    logger.info(f"Using conversation API server at: {api_url}")
    logger.info("Open this URL in your browser to view the agent conversation")
    
    if auto_start:
        logger.info("Will auto-start conversation when client connects")
    
    logger.info("Press Ctrl+C to exit")
    
    run_flask(port=port, api_url=api_url, auto_start=auto_start)
    return 0

if __name__ == "__main__":
    sys.exit(main()) 