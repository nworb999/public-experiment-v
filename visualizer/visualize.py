#!/usr/bin/env python3
"""
Combined visualization dashboard for agent conversations with real-time updates.
Runs both the main agent visualization server and the history server.
"""
import sys
import signal
import argparse
import threading
import time
import logging
import requests
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from visualizer.server.config import (
    CONFIG_DIR, TEMPLATE_DIR, DEFAULT_PORT, DEFAULT_API_URL, 
    load_config
)
from visualizer.server.agent_state import AgentState
from visualizer.server.conversation_manager import ConversationHistory, ConversationManager
from visualizer.server.handlers import Handlers
from stable_genius.utils.logger import logger

# Default port for history server
HISTORY_PORT = 5001

# Global flag for shutdown
shutdown_requested = False
# Global reference to history server URL for forwarding events
history_server_url = None

class MainVisualizerApp:
    """Main visualizer application class"""
    
    def __init__(self):
        # Create directories if they don't exist
        CONFIG_DIR.mkdir(exist_ok=True)
        TEMPLATE_DIR.mkdir(exist_ok=True)
        
        # Initialize Flask app
        self.app = Flask('agent-visualizer', 
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
        
        # Initialize regular handlers
        self.handlers = Handlers(
            self.app,
            self.socketio,
            self.agent_state,
            self.history,
            self.conversation
        )
        
        # Set global history server URL
        self.app.config['HISTORY_SERVER_URL'] = history_server_url
    
    def poll_conversation_status(self):
        """Background task to poll the conversation status"""
        while not shutdown_requested:
            api_url = self.app.config.get('API_URL', DEFAULT_API_URL)
            self.conversation.check_status(api_url)
            self.socketio.sleep(2)
    
    def run(self, port=DEFAULT_PORT, api_url=DEFAULT_API_URL, auto_start=True):
        """Run the Flask server"""
        # Set configuration
        self.app.config['PORT'] = port
        self.app.config['API_URL'] = api_url
        self.app.config['AUTO_START'] = auto_start
        
        # Disable Werkzeug access logs
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        
        # Start background task to poll conversation status
        self.socketio.start_background_task(self.poll_conversation_status)
        
        # Start server
        self.socketio.run(self.app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)


class HistoryVisualizerApp:
    """History visualizer application class"""
    
    def __init__(self):
        # Initialize Flask app
        self.app = Flask('llm-history', 
            template_folder=str(TEMPLATE_DIR),
            static_folder=str(TEMPLATE_DIR / "static"),
            static_url_path='/static'
        )
        self.socketio = SocketIO(self.app, async_mode='threading')
        
        # Initialize history storage
        self.history_items = []
        
        # Set up routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Set up Flask routes"""
        @self.app.route('/')
        def index():
            return render_template('history.html')
            
        @self.app.route('/api/update', methods=['POST'])
        def receive_update():
            """Receive updates from the conversation API server"""
            # Forward all events to clients
            update_data = request.json
            event_type = update_data.get('event_type')
            
            # Store LLM interactions for history
            if event_type == 'llm_interaction':
                # Store with timestamp
                if 'timestamp' not in update_data:
                    update_data['timestamp'] = time.time()
                
                # Add to history
                self.history_items.append(update_data)
                
                # Only keep the most recent 100 items
                if len(self.history_items) > 100:
                    self.history_items = self.history_items[-100:]
                
                # Debug logging
                logger.debug(f"History server received interaction: {update_data.get('step_title', '--')}")
                logger.debug(f"Prompt length: {len(update_data.get('prompt', ''))}, Response length: {len(update_data.get('response', ''))}")
            
            # Store agent messages in history too
            elif event_type == 'add_message':
                # Add timestamp if not present
                if 'timestamp' not in update_data:
                    update_data['timestamp'] = time.time()
                logger.debug(f"History server received message: {update_data.get('sender', '--')}: {update_data.get('message', '')[:50]}...")
            
            # Broadcast the event to clients
            self.socketio.emit(event_type, update_data)
            
            return jsonify({'status': 'success'})
        
        @self.socketio.on('connect')
        def handle_connect():
            """Send history to newly connected clients"""
            logger.debug(f"Client connected to history server, sending {len(self.history_items)} history items")
            self.socketio.emit('restore_state', {
                'conversation_history': self.history_items
            })
    
    def run(self, port=HISTORY_PORT):
        """Run the Flask server"""
        # Disable Werkzeug access logs
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        
        # Start server
        self.socketio.run(self.app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)


def run_main_server(port, api_url, auto_start, history_port, server_ready_event):
    """Run the main visualization server in a thread"""
    global history_server_url
    history_server_url = f"http://localhost:{history_port}"
    
    logger.info(f"Starting main visualization server on http://localhost:{port}")
    app = MainVisualizerApp()
    server_ready_event.set()  # Signal that server is ready
    app.run(port=port, api_url=api_url, auto_start=auto_start)


def run_history_server(port, server_ready_event):
    """Run the history server in a thread"""
    logger.info(f"Starting history visualization server on http://localhost:{port}")
    app = HistoryVisualizerApp()
    server_ready_event.set()  # Signal that server is ready
    app.run(port=port)


def signal_handler(sig, frame):
    """Handle keyboard interrupt gracefully"""
    global shutdown_requested
    shutdown_requested = True
    
    logger.info("\nKeyboard interrupt detected. Shutting down gracefully...\n")
    logger.info("Please wait while servers are shutting down...")
    logger.info("Thank you for using the application! ₍ᐢ._.ᐢ₎♡")
    
    # Give servers a moment to receive the shutdown signal
    time.sleep(1)
    sys.exit(0)


def main():
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run visualization servers for agent conversations")
    parser.add_argument("--main-port", type=int, default=DEFAULT_PORT, help="Port to run the main visualization server on")
    parser.add_argument("--history-port", type=int, default=HISTORY_PORT, help="Port to run the history visualization server on")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="URL of the conversation API server")
    parser.add_argument("--no-auto-start", action="store_true", help="Disable auto-starting a conversation on connect")
    parser.add_argument("--main-only", action="store_true", help="Run only the main visualization server")
    parser.add_argument("--history-only", action="store_true", help="Run only the history visualization server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        # Configure logging level
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    main_port = args.main_port
    history_port = args.history_port
    api_url = args.api_url
    auto_start = not args.no_auto_start
    
    # Log server information
    if not args.history_only:
        logger.info(f"Main visualization server will run on http://localhost:{main_port}")
    if not args.main_only:
        logger.info(f"History visualization server will run on http://localhost:{history_port}")
    
    logger.info(f"Using conversation API server at: {api_url}")
    logger.info("Open these URLs in your browser to view the agent conversation")
    
    if auto_start and not args.history_only:
        logger.info("Will auto-start conversation when client connects to main server")
    
    logger.info("Press Ctrl+C to exit")
    
    # Events to signal when servers are ready
    main_server_ready = threading.Event()
    history_server_ready = threading.Event()
    
    # Start servers in separate threads
    threads = []
    
    if not args.history_only:
        main_thread = threading.Thread(
            target=run_main_server,
            args=(main_port, api_url, auto_start, history_port, main_server_ready),
            daemon=True
        )
        main_thread.start()
        threads.append(main_thread)
    
    if not args.main_only:
        history_thread = threading.Thread(
            target=run_history_server,
            args=(history_port, history_server_ready),
            daemon=True
        )
        history_thread.start()
        threads.append(history_thread)
    
    try:
        # Keep the main thread alive to handle signals properly
        while not shutdown_requested:
            time.sleep(0.5)
    except KeyboardInterrupt:
        # This block shouldn't be needed due to signal handler,
        # but just in case signal handler doesn't catch it
        signal_handler(signal.SIGINT, None)
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 