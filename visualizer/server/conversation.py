"""
Conversation management for the visualization server
"""
import requests
from .config import MAX_HISTORY_ITEMS, DEFAULT_API_URL
from stable_genius.utils.logger import logger

class ConversationHistory:
    """Class to manage conversation history"""
    
    def __init__(self):
        self.history = {
            'prompts': [],
            'responses': [],
            'titles': [],
            'times': []
        }
    
    def add_interaction(self, prompt, response, title, elapsed_time):
        """Add a new interaction to history"""
        self.history['prompts'].insert(0, prompt)
        self.history['responses'].insert(0, response)
        self.history['titles'].insert(0, title)
        self.history['times'].insert(0, elapsed_time)
        
        # Trim history to maximum size
        for key in self.history:
            self.history[key] = self.history[key][:MAX_HISTORY_ITEMS]
    
    def get_history(self):
        """Get current history"""
        return self.history

class ConversationManager:
    """Class to manage conversations with the API server"""
    
    def __init__(self, socketio):
        self.socketio = socketio
        self.active = False
        self.conversation_id = None
        self.api_url = DEFAULT_API_URL
    
    def set_api_url(self, url):
        """Set the API URL"""
        self.api_url = url
    
    def start_conversation(self, api_url, port):
        """Start a new conversation"""
        if self.active:
            logger.info("A conversation is already active")
            self._emit_system_message('A conversation is already active')
            self._emit_status('active')
            return
        
        try:
            # Set up the visualization URL
            vis_url = f"http://localhost:{port}/api/update"
            
            # Call the conversation API server
            response = requests.post(
                f"{api_url}/api/start-conversation",
                json={'visualizer_url': vis_url},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.active = True
                self.conversation_id = data.get('conversation_id')
                logger.info(f"Started conversation with ID: {self.conversation_id}")
                self._emit_system_message(f'Started conversation with ID: {self.conversation_id}')
                self._emit_status('started')
            else:
                error_msg = f"Failed to start conversation: {response.status_code} {response.text}"
                logger.error(error_msg)
                self._emit_error_message(error_msg)
                self._emit_error_status(f'Failed to start conversation: {response.status_code}')
        except requests.RequestException as e:
            error_msg = f"Error connecting to conversation API server: {str(e)}"
            logger.error(error_msg)
            self._emit_error_message(error_msg)
            self._emit_error_status(f'Connection error: {str(e)}')
    
    def check_status(self, api_url):
        """Check the status of the current conversation"""
        if not self.conversation_id:
            return
        
        try:
            response = requests.get(
                f"{api_url}/api/conversation-status/{self.conversation_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                # Send status update to client
                self.socketio.emit('conversation_status', {
                    'active': status == 'running',
                    'conversation_id': self.conversation_id,
                    'status': status
                })
                
                if status in ['completed', 'error']:
                    self.active = False
                    self._emit_system_message(f'Conversation {self.conversation_id} {status}')
                    self.conversation_id = None
            elif response.status_code == 404:
                self.active = False
                self.conversation_id = None
                
                # Send status update to client
                self.socketio.emit('conversation_status', {
                    'active': False,
                    'conversation_id': None,
                    'status': 'not_found'
                })
        except requests.RequestException:
            # Ignore connection errors during status checks
            pass
    
    def _emit_system_message(self, message):
        """Emit a system message"""
        self.socketio.emit('add_message', {
            'sender': 'System',
            'message': message
        })
    
    def _emit_error_message(self, message):
        """Emit an error message"""
        self.socketio.emit('add_message', {
            'sender': 'Error',
            'message': message
        })
    
    def _emit_status(self, status):
        """Emit conversation status"""
        self.socketio.emit('conversation_status', {
            'active': True,
            'conversation_id': self.conversation_id,
            'status': status
        })
    
    def _emit_error_status(self, message):
        """Emit error status"""
        self.socketio.emit('conversation_status', {
            'active': False,
            'status': 'error',
            'message': message
        }) 