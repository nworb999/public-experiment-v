"""
Event and route handlers for the visualization server
"""
from flask import request, jsonify, render_template
import requests
import time
from .config import VALID_AGENT_IDS
from stable_genius.utils.logger import logger

class Handlers:
    """Class to manage event and route handlers"""
    
    def __init__(self, app, socketio, agent_state, history, conversation):
        self.app = app
        self.socketio = socketio
        self.agent_state = agent_state
        self.history = history
        self.conversation = conversation
        
        # Set up routes
        self._setup_routes()
        # Set up socketio handlers
        self._setup_socketio_handlers()
    
    def _setup_routes(self):
        """Set up Flask routes"""
        self.app.route('/')(self.index)
        self.app.route('/api/update', methods=['POST'])(self.receive_update)
    
    def _setup_socketio_handlers(self):
        """Set up Socket.IO event handlers"""
        self.socketio.on('connect')(self.handle_connect)
        self.socketio.on('start_conversation')(self.handle_start_conversation)
        self.socketio.on('request_autostart')(self.handle_autostart_request)
    
    def index(self):
        """Handle root route"""
        return render_template('index.html')
    
    def receive_update(self):
        """Receive updates from the conversation API server"""
        update_data = request.json
        event_type = update_data.get('event_type')
        if event_type == 'config':
            self.socketio.emit('config', update_data.get('config', {}))
        elif event_type == 'initialize_agents':
            self._handle_initialize_agents(update_data)
        elif event_type == 'llm_interaction':
            self._handle_llm_interaction(update_data)
        # elif event_type == 'message':
        #     self._handle_message(update_data)
        elif event_type == 'add_message':
            self._handle_message(update_data)  # Reuse message handler for add_message events
        elif event_type == 'agent_update':
            self._handle_agent_update(update_data)
        elif event_type == 'pipeline_update':
            self._handle_pipeline_update(update_data)
        
        return jsonify({'status': 'success'})
    
    def _handle_initialize_agents(self, update_data):
        """Handle agent initialization event"""
        agents = update_data.get('agents', [])
        for agent in agents:
            agent_id = agent.get('agent_id')
            # Update pipeline components if available
            if 'components' in agent:
                self.agent_state.update_pipeline_components(agent_id, agent['components'])
            
            # Update agent info like goal, personality, etc.
            self.agent_state.update_agent_info(agent_id, agent)
                
        # Send initialization data for agents
        self.socketio.emit('initialize_agents', {
            'agents': update_data.get('agents', [])
        })
    
    def _handle_llm_interaction(self, update_data):
        """Handle LLM interaction event"""
        # Ensure we're getting the prompt and response properly
        prompt = update_data.get('prompt', '')
        response = update_data.get('response', '')
        step_title = update_data.get('step_title', '')
        elapsed_time = update_data.get('elapsed_time', '--')
        
        # Log the data we received for debugging
        logger.debug(f"LLM interaction received - Title: {step_title}")
        logger.debug(f"Prompt length: {len(prompt)}, Response length: {len(response)}")
        
        # Store in history
        self.history.add_interaction(prompt, response, step_title, elapsed_time)
        
        # Format elapsed time
        formatted_time = f"{elapsed_time}s" if elapsed_time not in [None, '--'] else '--'
        
        # Ensure we're explicitly including the prompt and response in the emit
        event_data = {
            'prompt': prompt,
            'response': response,
            'elapsed_time': formatted_time,
            'step_title': step_title
        }
        
        # Emit the event with the complete data
        self.socketio.emit('llm_interaction', event_data)
        
        # Forward to history server if configured
        self._forward_to_history_server(update_data)
    
    def _forward_to_history_server(self, update_data):
        """Forward LLM interactions to the history server"""
        history_server_url = self.app.config.get('HISTORY_SERVER_URL')
        if history_server_url:
            try:
                # Ensure we have a properly formatted event type
                forwarded_data = {
                    'event_type': 'llm_interaction',
                    'prompt': update_data.get('prompt', ''),
                    'response': update_data.get('response', ''),
                    'step_title': update_data.get('step_title', ''),
                    'elapsed_time': update_data.get('elapsed_time', '--'),
                    'timestamp': update_data.get('timestamp', time.time())
                }
                
                # Log what we're forwarding for debugging
                logger.debug(f"Forwarding LLM interaction to history server: {forwarded_data['step_title']}")
                
                requests.post(
                    f"{history_server_url}/api/update",
                    json=forwarded_data,
                    timeout=1
                )
            except requests.RequestException as e:
                logger.debug(f"Error forwarding to history server: {e}")
    
    def _handle_message(self, update_data):
        """Handle message event"""
        sender_id = update_data.get('sender_id')
        sender = update_data.get('sender', 'System')
        message = update_data.get('message', '')
        
        # Store message in conversation state
        self.history.add_message(sender, message, sender_id)
        
        # Update agent state if message is from an agent
        if sender_id in VALID_AGENT_IDS:
            self.agent_state.add_message(sender_id, message)
            
        # Skip system messages - don't emit them to the client
        if sender != 'System':
            self.socketio.emit('add_message', {
                'sender': sender,
                'sender_id': sender_id,
                'message': message
            })
        
        # Forward to history server
        history_server_url = self.app.config.get('HISTORY_SERVER_URL')
        if history_server_url:
            try:
                forwarded_data = {
                    'event_type': 'add_message',
                    'sender': sender,
                    'sender_id': sender_id,
                    'message': message,
                    'timestamp': time.time()
                }
                
                logger.debug(f"Forwarding message to history server: {sender}: {message[:50]}...")
                
                requests.post(
                    f"{history_server_url}/api/update",
                    json=forwarded_data,
                    timeout=1
                )
            except requests.RequestException as e:
                logger.debug(f"Error forwarding message to history server: {e}")
    
    def _handle_agent_update(self, update_data):
        """Handle agent update event"""
        agent_id = update_data.get('agent_id', 0)
        
        logger.debug(f"Handling agent_update for agent {agent_id}")
        logger.debug(f"Received update data: {update_data}")
        
        # Store original state before update to access cached values if needed
        cached_state = self.agent_state.states.get(agent_id, {})
        logger.debug(f"Cached state before update: {cached_state}")
        
        # Update agent info with new data
        self.agent_state.update_agent_info(agent_id, update_data)
                
        # Get goal from update_data if available, otherwise from plan,
        # and if neither is available, use cached value
        goal = update_data.get('goal', None)
        if goal is None:
            plan = update_data.get('plan', {})
            if plan and 'goal' in plan:
                goal = plan.get('goal')
                logger.debug(f"Using goal from plan: {goal}")
            else:
                # Use cached goal from existing state
                cached_plan = cached_state.get('plan', {})
                goal = cached_state.get('goal') or cached_plan.get('goal', None)
                logger.debug(f"Using cached goal: {goal}")
        else:
            logger.debug(f"Using goal from update_data: {goal}")
        
        # Get plan from update data or use cached plan
        plan = update_data.get('plan', cached_state.get('plan', {}))
        logger.debug(f"Using plan: {plan}")
        
        # Log plan details specifically
        if isinstance(plan, dict):
            logger.debug(f"Plan tactics: {plan.get('tactics')}")
            logger.debug(f"Plan active tactic: {plan.get('active_tactic')}")
        
        # Build the payload to emit
        payload = {
            'name': update_data.get('name', cached_state.get('name', '')),
            'personality': update_data.get('personality', cached_state.get('personality', '')),
            'tension': update_data.get('tension', cached_state.get('tension', 0)),
            'goal': goal,
            'plan': plan
        }
        logger.debug(f"Emitting update_agent{agent_id+1} with payload: {payload}")
        
        # Fixed emit to match what client is expecting
        self.socketio.emit(f'update_agent{agent_id+1}', payload)
    
    def _handle_pipeline_update(self, update_data):
        """Handle pipeline update event"""
        agent_id = update_data.get('agent_id', 0)
        
        # Update components if provided
        if 'data' in update_data and 'components' in update_data['data']:
            components = update_data['data']['components']
            if components:
                self.agent_state.update_pipeline_components(agent_id, components)
        
        # Update stage if provided
        if 'stage' in update_data:
            self.agent_state.update_pipeline_stage(agent_id, update_data['stage'])
        
            
        self.socketio.emit('pipeline_update', {
            'agent_id': agent_id,
            'agent_name': update_data.get('agent_name', ''),
            'stage': update_data.get('stage', ''),
            'data': update_data.get('data', {})
        })
    
    def handle_connect(self):
        """Handle client connection"""
        logger.info('Client connected')
        
        # Get messages and filter out system messages
        all_messages = self.history.get_messages()
        filtered_messages = [msg for msg in all_messages if msg.get('sender') != 'System']
        
        # Send current state to the client
        self.socketio.emit('restore_state', {
            'agent_states': self.agent_state.states,
            'conversation_history': self.history.get_history(),
            'messages': filtered_messages
        })
        
        # Send current conversation status
        self.socketio.emit('conversation_status', {
            'active': self.conversation.active,
            'conversation_id': self.conversation.conversation_id,
            'status': 'active' if self.conversation.active else 'waiting'
        })
    
    def handle_start_conversation(self):
        """Handle start conversation event from client"""
        logger.info("Received start_conversation event from client")
        api_url = self.app.config.get('API_URL')
        port = self.app.config.get('PORT')
        self.conversation.start_conversation(api_url, port)
    
    def handle_autostart_request(self):
        """Handle autostart request from client"""
        # Check if auto-start is enabled
        if self.app.config.get('AUTO_START', False) and not self.conversation.active:
            logger.info("Auto-starting conversation per client request")
            api_url = self.app.config.get('API_URL')
            port = self.app.config.get('PORT')
            self.conversation.start_conversation(api_url, port)
        else:
            # Notify client of current conversation status
            self.socketio.emit('conversation_status', {
                'active': self.conversation.active,
                'conversation_id': self.conversation.conversation_id,
                'status': 'waiting' if not self.conversation.active else 'active'
            }) 