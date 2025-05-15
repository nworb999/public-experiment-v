/**
 * Socket Event Handler Module
 * Handles all Socket.IO events for the application
 */

import State from './state.js';
import ChatManager from './chat.js';
import AgentManager from './agent.js';
import PipelineManager from './pipeline.js';
import ConversationManager from './conversation-ui.js';
import Logger from './logger.js';

let socket = null;

/**
 * Initialize socket event handlers
 * @param {Object} io - The Socket.IO client library
 */
function initializeSocketEvents(io) {
    socket = io();

    socket.on('connect', () => {
        console.log('Connected to server');
        
        // Only request autostart if no conversation is active
        if (!State.conversationActive) {
            socket.emit('request_autostart');
        }
    });

    // Restore state event
    socket.on('restore_state', (data) => {
        console.log('Restoring state from server');
        
        // Clear existing messages
        ChatManager.clearMessages();
        
        // Restore agent states
        if (data.agent_states) {
            if (data.agent_states[0]) {
                AgentManager.restoreAgent(data.agent_states[0], 0);
                if (data.agent_states[0].name) {
                    State.agents[0].name = data.agent_states[0].name;
                }
            }
            if (data.agent_states[1]) {
                AgentManager.restoreAgent(data.agent_states[1], 1);
                if (data.agent_states[1].name) {
                    State.agents[1].name = data.agent_states[1].name;
                }
            }
        }
        
        // Restore conversation history
        if (data.conversation_history) {
            ConversationManager.restoreConversationHistory(data.conversation_history);
        }
        
        // Restore conversation messages if present
        if (data.messages && Array.isArray(data.messages)) {
            data.messages.forEach(msg => {
                ChatManager.addMessage(msg.sender, msg.message, msg.sender_id);
            });
        }
    });

    socket.on('initialize_agents', (data) => {
        console.log('Initializing agents:', data);
        
        data.agents.forEach(agent => {
            // Log the agent data
            Logger.log(`Initializing agent ${agent.agent_id} with data:`, agent);
            
            // Log plan data specifically
            if (agent.plan) {
                Logger.log(`Agent ${agent.agent_id} plan data:`, agent.plan);
                Logger.log(`Agent ${agent.agent_id} tactics:`, agent.plan.tactics);
                Logger.log(`Agent ${agent.agent_id} active tactic:`, agent.plan.active_tactic);
            } else {
                Logger.log(`Agent ${agent.agent_id} has no plan data`);
            }
            
            // Update agent state
            AgentManager.updateAgentInfo(agent.agent_id, agent);
            
            // Create pipeline visualization if components exist
            if (agent.components && agent.components.length > 0) {
                PipelineManager.createPipelineFlow(agent.agent_id, agent.components);
            }
            
            // Store agent name in state
            State.agents[agent.agent_id] = {
                name: agent.name
            };
        });
    });

    socket.on('config', (data) => {
        if (data.config && data.config.agents && data.config.agents.length >= 2) {
            const agent1Name = document.getElementById('agent1-name');
            const agent2Name = document.getElementById('agent2-name');
            const agent1Personality = document.getElementById('agent1-personality');
            const agent2Personality = document.getElementById('agent2-personality');
            
            if (agent1Name) agent1Name.textContent = data.config.agents[0].name;
            if (agent2Name) agent2Name.textContent = data.config.agents[1].name;
            if (agent1Personality) agent1Personality.textContent = data.config.agents[0].personality || '--';
            if (agent2Personality) agent2Personality.textContent = data.config.agents[1].personality || '--';
        }
    });

    socket.on('llm_interaction', (data) => {
        ConversationManager.updateConversation(data);
    });

    // Handle agent messages
    socket.on('message', (data) => {
        console.log('Received message:', data);
        ChatManager.addMessage(data.sender, data.message, data.sender_id);
    });

    socket.on('add_message', (data) => {
        console.log('Received add_message:', data);
        ChatManager.addMessage(data.sender, data.message, data.sender_id);
    });

    socket.on('conversation_status', (data) => {
        // Update conversation state
        State.conversationActive = data.active;
        State.currentConversationId = data.conversation_id;
        
        // Add message to UI if status changed
        const message = `Conversation status: ${data.status}`;
        ChatManager.addMessage('System', message);
    });

    // Listen for agent updates
    socket.on('update_agent1', (data) => {
        Logger.log('Received update_agent1 event with data:', data);
        
        // Log plan data specifically
        if (data.plan) {
            Logger.log('Plan data for agent 1:', data.plan);
            Logger.log('Plan tactics for agent 1:', data.plan.tactics);
            Logger.log('Plan active tactic for agent 1:', data.plan.active_tactic);
        } else {
            Logger.log('No plan data in update_agent1 event');
        }
        
        AgentManager.updateAgentInfo(0, data);
    });

    socket.on('update_agent2', (data) => {
        Logger.log('Received update_agent2 event with data:', data);
        
        // Log plan data specifically
        if (data.plan) {
            Logger.log('Plan data for agent 2:', data.plan);
            Logger.log('Plan tactics for agent 2:', data.plan.tactics);
            Logger.log('Plan active tactic for agent 2:', data.plan.active_tactic);
        } else {
            Logger.log('No plan data in update_agent2 event');
        }
        
        AgentManager.updateAgentInfo(1, data);
    });

    socket.on('pipeline_update', (data) => {  
        console.log('Pipeline update:', data);      
        const agentId = data.agent_id;
        const stage = data.stage;
        const pipelineData = data.data || {};
        
        // Update pipeline stage if provided
        if (stage) {
            PipelineManager.updatePipelineStage(agentId, stage, pipelineData);
        }
    });

    // Agent update handler - store agent names in state
    socket.on('agent_update', (data) => {
        Logger.log('Agent update received:', data);
        
        // Log plan data specifically
        if (data.plan) {
            Logger.log(`Plan data for agent ${data.agent_id}:`, data.plan);
            Logger.log(`Tactics for agent ${data.agent_id}:`, data.plan.tactics);
            Logger.log(`Active tactic for agent ${data.agent_id}:`, data.plan.active_tactic);
        } else {
            Logger.log(`No plan data in update for agent ${data.agent_id}`);
        }
        
        AgentManager.updateAgentInfo(data.agent_id, data);
        
        // Store agent name in state for message handling
        if (data.name) {
            State.agents[data.agent_id] = { 
                name: data.name,
                ...State.agents[data.agent_id]
            };
        }
    });
}

export { initializeSocketEvents, socket }; 