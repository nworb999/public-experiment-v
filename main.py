import asyncio
import argparse
import requests
import json
import sys
import signal
import logging
from pathlib import Path
from flask import Flask, request, jsonify
from flask_socketio import SocketIO

from stable_genius.utils.logger import logger
from stable_genius.utils.llm import OllamaLLM
from stable_genius.controllers.conversation import (
    run_conversation, 
    stop_conversation, 
    list_all_conversations, 
    get_conversation_status,
    active_conversations,
    send_to_visualizer
)

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

# Configure additional logging
logging.basicConfig(level=logging.INFO)
socketio_logger = logging.getLogger('socketio')
socketio_logger.setLevel(logging.INFO)

# Config directory and file
config_dir = Path(__file__).parent / "config"
config_dir.mkdir(exist_ok=True)
CONFIG_FILE = config_dir / "agents_config.json"

# Create a shared LLM instance
llm_service = OllamaLLM()

def signal_handler(sig, frame):
    """Handle keyboard interrupt gracefully"""
    logger.info("Keyboard interrupt detected. Shutting down gracefully...\n\n")
    logger.info("Thank you for using the application! ₍ᐢ._.ᐢ₎♡")
    sys.exit(0)

# Load config from file
def load_config():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}. Please create this file before running.")
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error loading config file: {e}")

def send_to_visualizer(data, visualizer_url="http://localhost:5000/api/update"):
    """Send data to visualization server"""
    # Log the data being sent
    logger.debug(f"Sending data to visualizer: {data}")
    
    try:
        response = requests.post(visualizer_url, json=data, timeout=1)
        return response.status_code == 200
    except requests.RequestException:
        return False

@app.route('/api/llm-interactions', methods=['GET'])
def get_llm_interactions():
    """Return all LLM prompts and responses"""
    return jsonify(llm_service.get_interactions())

@app.route('/api/start-conversation', methods=['POST'])
def start_conversation():
    """Start a new conversation between agents"""
    conversation_id = request.json.get('conversation_id', str(len(active_conversations) + 1))
    visualizer_url = request.json.get('visualizer_url', "http://localhost:5000/api/update")
    
    # Check if conversation already exists and is running
    existing_conv = get_conversation_status(conversation_id)
    if existing_conv and existing_conv.get('status') == 'running':
        return jsonify({
            'status': 'already_running',
            'conversation_id': conversation_id
        })
    
    # If conversation exists but is not running, stop it first
    if existing_conv:
        stop_conversation(conversation_id)
    
    def run_async_conversation():
        """Wrapper function to run the async conversation in a synchronous context"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_conversation(conversation_id, visualizer_url, llm_service))
        loop.close()
    
    # Schedule the conversation to run asynchronously
    socketio.start_background_task(run_async_conversation)
    
    return jsonify({
        'status': 'started',
        'conversation_id': conversation_id
    })

@app.route('/api/conversations', methods=['GET'])
def list_conversations():
    """List all active conversations"""
    return jsonify(list_all_conversations())

@app.route('/api/stop-conversation/<conversation_id>', methods=['POST'])
def api_stop_conversation(conversation_id):
    """Stop an active conversation"""
    result = stop_conversation(conversation_id)
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result)

@app.route('/api/conversation-status/<conversation_id>', methods=['GET'])
def conversation_status(conversation_id):
    """Get the status of a conversation"""
    status = get_conversation_status(conversation_id)
    if status:
        return jsonify(status)
    return jsonify({
        'status': 'not_found',
        'message': f'Conversation {conversation_id} not found'
    }), 404

@app.route('/api/clear-llm-interactions', methods=['POST'])
def clear_llm_interactions():
    """Clear all recorded LLM interactions"""
    llm_service.clear_interactions()
    return jsonify({
        'status': 'cleared',
        'message': 'Successfully cleared all LLM interactions'
    })

def main():
    # Register signal handler for CTRL+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run a Flask server for agent conversations")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the Flask server on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to run the Flask server on")
    parser.add_argument("--debug", action="store_true", help="Run Flask in debug mode")
    args = parser.parse_args()
    
    # Enable debug logging if in debug mode
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        socketio_logger = logging.getLogger('socketio')
        socketio_logger.setLevel(logging.DEBUG)
    else:
        # Disable Werkzeug access logs in non-debug mode
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
    
    logger.info(f"Starting conversation server on http://{args.host}:{args.port}")
    logger.info("Press Ctrl+C to exit")
    
    socketio.run(app, debug=args.debug, host=args.host, port=args.port)
    return 0

if __name__ == "__main__":
    sys.exit(main()) 