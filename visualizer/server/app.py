"""
Main Flask application for the visualization server
"""
import signal
import sys
import argparse
from flask import Flask
from flask_socketio import SocketIO
from pathlib import Path

from .config import (
    CONFIG_DIR, TEMPLATE_DIR, DEFAULT_PORT, DEFAULT_API_URL,
    load_config
)
from .agent_state import AgentState
from .conversation_manager import ConversationHistory, ConversationManager
from .handlers import Handlers
from stable_genius.utils.logger import logger

class VisualizerApp:
    """Main visualizer application class"""
    
    def __init__(self):
        # Create directories if they don't exist
        CONFIG_DIR.mkdir(exist_ok=True)
        TEMPLATE_DIR.mkdir(exist_ok=True)
        
        # Initialize Flask app
        self.app = Flask(__name__, 
            template_folder=str(TEMPLATE_DIR),
            static_folder=str(TEMPLATE_DIR / "static"),
            static_url_path='/static'
        )
        self.socketio = SocketIO(self.app, async_mode='threading')
        
        # Initialize state managers
        self.agent_state = AgentState()
        self.history = ConversationHistory()
        self.conversation = ConversationManager(self.socketio)
        
        # Initialize config
        self.config = load_config()
        self.agents_config = self.config.get("agents", {})
        
        # Initialize handlers
        self.handlers = Handlers(
            self.app,
            self.socketio,
            self.agent_state,
            self.history,
            self.conversation
        )
    
    def poll_conversation_status(self):
        """Background task to poll the conversation status"""
        while True:
            api_url = self.app.config.get('API_URL', DEFAULT_API_URL)
            self.conversation.check_status(api_url)
            self.socketio.sleep(2)
    
    def run(self, port=DEFAULT_PORT, api_url=DEFAULT_API_URL, auto_start=True):
        """Run the Flask server"""
        # Set configuration
        self.app.config['PORT'] = port
        self.app.config['API_URL'] = api_url
        self.app.config['AUTO_START'] = auto_start
        
        # Start background task to poll conversation status
        self.socketio.start_background_task(self.poll_conversation_status)
        
        # Start server
        self.socketio.run(self.app, debug=False, host='0.0.0.0', port=port)


def signal_handler(sig, frame):
    """Handle keyboard interrupt gracefully"""
    logger.info("Keyboard interrupt detected. Shutting down gracefully...")
    sys.exit(0)


def main():
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run a visualization server for agent conversations")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to run the visualization server on")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="URL of the conversation API server")
    parser.add_argument("--no-auto-start", action="store_true", help="Disable auto-starting a conversation on connect")
    args = parser.parse_args()
    
    port = args.port
    api_url = args.api_url
    auto_start = not args.no_auto_start
    
    # Log server information
    logger.info(f"Starting visualization server on http://localhost:{port}")
    logger.info(f"Using conversation API server at: {api_url}")
    logger.info("Open this URL in your browser to view the agent conversation")
    
    if auto_start:
        logger.info("Will auto-start conversation when client connects")
    
    logger.info("Press Ctrl+C to exit")
    
    # Create and run the app
    app = VisualizerApp()
    app.run(port=port, api_url=api_url, auto_start=auto_start)
    return 0


if __name__ == "__main__":
    sys.exit(main()) 