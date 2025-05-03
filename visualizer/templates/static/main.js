/**
 * Agent Conversation UI
 * Main JavaScript file for handling agent interactions and UI updates
 */

// DOM Elements
const UI = {
    // Conversation container
    conversationMessages: document.getElementById('conversation-messages'),
    
    // Prompt and response elements
    promptBoxes: [
        document.getElementById('prompt-box-1'),
        document.getElementById('prompt-box-2'),
        document.getElementById('prompt-box-3')
    ],
    promptTitles: [
        document.getElementById('prompt-title-1'),
        document.getElementById('prompt-title-2'),
        document.getElementById('prompt-title-3')
    ],
    responseBoxes: [
        document.getElementById('response-box-1'),
        document.getElementById('response-box-2'),
        document.getElementById('response-box-3')
    ],
    responseTimeDisplays: [
        document.getElementById('response-time-1'),
        document.getElementById('response-time-2'),
        document.getElementById('response-time-3')
    ],
    
    // Agent 1 elements
    agent1: {
        name: document.getElementById('agent1-name'),
        pipeline: document.getElementById('agent1-pipeline'),
        personality: document.getElementById('agent1-personality'),
        tension: document.getElementById('agent1-tension'),
        goal: document.getElementById('agent1-goal'),
        tactic: document.getElementById('agent1-tactic'),
        plan: document.getElementById('agent1-plan')
    },
    
    // Agent 2 elements
    agent2: {
        name: document.getElementById('agent2-name'),
        pipeline: document.getElementById('agent2-pipeline'),
        personality: document.getElementById('agent2-personality'),
        tension: document.getElementById('agent2-tension'),
        goal: document.getElementById('agent2-goal'),
        tactic: document.getElementById('agent2-tactic'),
        plan: document.getElementById('agent2-plan')
    }
};

// Application state
const State = {
    conversationActive: false,
    currentConversationId: null,
    agents: {
        0: { name: 'Agent 1' },
        1: { name: 'Agent 2' }
    }
};

// Logging helper
const Logger = {
    log(message, data) {
        console.log(`[DEBUG] ${message}`, data);
    }
};

// Chat message management
const ChatManager = {
    /**
     * Adds a message to the conversation chat
     * @param {string} sender - Name of the message sender
     * @param {string} message - The message content
     * @param {number} [senderId] - The sender ID (0 or 1) for agents
     */
    addMessage(sender, message, senderId) {
        if (!UI.conversationMessages) return;
        
        // Skip System messages
        if (sender === 'System') return;
        
        const messageElement = document.createElement('div');
        
        // Determine message type
        let messageClass = 'message';
        if (sender === 'Error') {
            messageClass += ' message-error';
        } else if (senderId === 0) {
            messageClass += ' message-left';
        } else if (senderId === 1) {
            messageClass += ' message-right';
        } else {
            messageClass += ' message-system';
        }
        
        messageElement.className = messageClass;
        
        // Add sender name
        const senderElement = document.createElement('div');
        senderElement.className = 'message-sender';
        senderElement.textContent = sender;
        messageElement.appendChild(senderElement);
        
        // Add message content
        const contentElement = document.createElement('div');
        contentElement.textContent = message;
        messageElement.appendChild(contentElement);
        
        // Add to conversation
        UI.conversationMessages.appendChild(messageElement);
        
        // Scroll to bottom
        UI.conversationMessages.scrollTop = UI.conversationMessages.scrollHeight;
    },
    
    /**
     * Clears all messages from the conversation
     */
    clearMessages() {
        if (UI.conversationMessages) {
            UI.conversationMessages.innerHTML = '';
        }
    }
};

// Conversation control functions
const ConversationController = {
    /**
     * Start a new conversation
     */
    startConversation() {
        if (State.conversationActive) {
            console.log("A conversation is already active");
            return;
        }

        // Clear previous messages
        ChatManager.clearMessages();
        
        // Emit event to server to start conversation
        socket.emit('start_conversation');
    }
};

// Pipeline visualization utilities
const PipelineManager = {
    /**
     * Creates a visual pipeline flow for an agent
     * @param {number} agentId - The ID of the agent (0 or 1)
     * @param {Array} components - Array of pipeline component names
     */
    createPipelineFlow(agentId, components) {
        if (!components || !Array.isArray(components) || components.length === 0) {
            console.warn(`Cannot create pipeline flow: Invalid components for agent ${agentId}`);
            return;
        }
        
        const pipelineContainer = document.createElement('div');
        pipelineContainer.className = 'pipeline-flow';

        components.forEach((component, index) => {
            const circle = document.createElement('div');
            circle.className = 'pipeline-circle';
            circle.id = `${agentId}-${component}`;
            circle.textContent = component;
            pipelineContainer.appendChild(circle);

            if (index < components.length - 1) {
                const arrow = document.createElement('div');
                arrow.className = 'pipeline-arrow';
                arrow.textContent = '→';
                pipelineContainer.appendChild(arrow);
            }
        });

        // Get the correct pipeline element
        const pipelineElement = agentId === 0 ? UI.agent1.pipeline : UI.agent2.pipeline;
        
        // Clear entire pipeline content
        pipelineElement.innerHTML = ''; 
        
        // Append the new pipeline
        pipelineElement.appendChild(pipelineContainer);
    },

    /**
     * Updates the active stage in a pipeline visualization
     * @param {number} agentId - The ID of the agent (0 or 1)
     * @param {string} stage - The active stage name
     */
    updatePipelineStage(agentId, stage) {
        if (!stage) {
            console.warn(`Cannot update pipeline stage: No stage provided for agent ${agentId}`);
            return;
        }
        
        // Remove active class from all circles for this agent
        const circles = document.querySelectorAll(`.pipeline-circle[id^="${agentId}-"]`);
        circles.forEach(circle => circle.classList.remove('active'));
        
        // Add active class to current stage
        const currentCircle = document.getElementById(`${agentId}-${stage}`);
        if (currentCircle) {
            currentCircle.classList.add('active');
        } else {
            console.warn(`Pipeline stage element not found: ${agentId}-${stage}`);
        }
    }
};

// Agent state management
const AgentManager = {
    /**
     * Updates agent information in the UI
     * @param {number} agentId - The ID of the agent (0 or 1)
     * @param {Object} data - The data to update with
     */
    updateAgentInfo(agentId, data) {
        const agent = agentId === 0 ? UI.agent1 : UI.agent2;
        
        Logger.log(`Updating agent ${agentId} with data:`, data);
        
        if (data.name) {
            agent.name.textContent = data.name;
        }
        if (data.personality) {
            agent.personality.textContent = data.personality;
        }
        if (data.tension !== undefined) {
            agent.tension.textContent = data.tension;
        }
        
        // Handle goal directly or from plan object
        if (data.goal) {
            Logger.log(`Setting goal for agent ${agentId}:`, data.goal);
            agent.goal.textContent = data.goal;
        } else if (data.plan?.goal) {
            Logger.log(`Setting goal from plan for agent ${agentId}:`, data.plan.goal);
            agent.goal.textContent = data.plan.goal;
        }
        
        // Handle active tactic from plan
        if (data.plan?.active_tactic) {
            Logger.log(`Setting active tactic for agent ${agentId}:`, data.plan.active_tactic);
            agent.tactic.textContent = data.plan.active_tactic;
        } else {
            Logger.log(`No active tactic found for agent ${agentId}`, data.plan);
        }
        
        // Handle plan tactics
        if (data.plan?.tactics) {
            Logger.log(`Setting tactics for agent ${agentId}:`, data.plan.tactics);
            agent.plan.textContent = data.plan.tactics.join(', ');
        } else {
            Logger.log(`No tactics found for agent ${agentId}`, data.plan);
        }
    },
    
    /**
     * Adds a message to agent terminal
     * @param {number} agentId - The ID of the agent (0 or 1) 
     * @param {string} message - The message to add
     */
    addMessage(agentId, message) {
        // No-op: we don't want to display messages in the agent container
        // Just keeping the method to avoid breaking code that calls it
        return;
    },
    
    /**
     * Restores agent state from saved data
     * @param {Object} agentState - The agent state data
     * @param {number} agentId - The ID of the agent (0 or 1)
     */
    restoreAgent(agentState, agentId) {
        if (!agentState) return;
        
        Logger.log(`Restoring agent ${agentId} from state:`, agentState);
        
        const agent = agentId === 0 ? UI.agent1 : UI.agent2;
        
        agent.name.textContent = agentState.name;
        agent.personality.textContent = agentState.personality;
        agent.tension.textContent = agentState.tension;
        agent.goal.textContent = agentState.goal;
        
        // Log and restore active tactic if exists
        if (agentState.plan && agentState.plan.active_tactic) {
            Logger.log(`Restoring active tactic for agent ${agentId}:`, agentState.plan.active_tactic);
            agent.tactic.textContent = agentState.plan.active_tactic;
        } else {
            Logger.log(`No active tactic to restore for agent ${agentId}`, agentState.plan);
        }
        
        // Log and restore tactics if they exist
        if (agentState.plan && agentState.plan.tactics) {
            Logger.log(`Restoring tactics for agent ${agentId}:`, agentState.plan.tactics);
            agent.plan.textContent = agentState.plan.tactics.join(', ');
        } else {
            Logger.log(`No tactics to restore for agent ${agentId}`, agentState.plan);
        }
        
        // Restore pipeline if it exists
        if (agentState.pipeline && agentState.pipeline.components) {
            PipelineManager.createPipelineFlow(agentId, agentState.pipeline.components);
            if (agentState.pipeline.stage) {
                PipelineManager.updatePipelineStage(agentId, agentState.pipeline.stage);
            }
        }
    }
};

// Conversation management
const ConversationManager = {
    /**
     * Updates the conversation boxes with new content
     * @param {Object} data - The data containing prompt and response information
     */
    updateConversation(data) {
        // Move content down to other boxes first
        UI.promptBoxes[2].textContent = UI.promptBoxes[1].textContent;
        UI.promptTitles[2].textContent = UI.promptTitles[1].textContent;
        UI.responseBoxes[2].textContent = UI.responseBoxes[1].textContent;
        UI.responseTimeDisplays[2].textContent = UI.responseTimeDisplays[1].textContent;
        
        UI.promptBoxes[1].textContent = UI.promptBoxes[0].textContent;
        UI.promptTitles[1].textContent = UI.promptTitles[0].textContent;
        UI.responseBoxes[1].textContent = UI.responseBoxes[0].textContent;
        UI.responseTimeDisplays[1].textContent = UI.responseTimeDisplays[0].textContent;
        
        // Add new content to first box
        UI.promptBoxes[0].textContent = data.prompt;
        UI.promptTitles[0].textContent = `Step: ${data.step_title || '--'}`;
        UI.responseBoxes[0].textContent = data.response;
        UI.responseTimeDisplays[0].textContent = `Time elapsed: ${data.elapsed_time || '--'}`;
    },
    
    /**
     * Restores conversation history from saved data
     * @param {Object} conversationHistory - The saved conversation history
     */
    restoreConversationHistory(conversationHistory) {
        if (!conversationHistory) return;
        
        const { prompts, responses, titles, times } = conversationHistory;
        
        // Update prompt boxes
        for (let i = 0; i < Math.min(prompts.length, 3); i++) {
            UI.promptBoxes[i].textContent = prompts[i] || '';
            UI.promptTitles[i].textContent = `Step: ${titles[i] || '--'}`;
            UI.responseBoxes[i].textContent = responses[i] || '';
            UI.responseTimeDisplays[i].textContent = `Time elapsed: ${times[i] || '--'}`;
        }
    }
};

// Socket event handling
const socket = io();

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
        UI.agent1.name.textContent = data.config.agents[0].name;
        UI.agent2.name.textContent = data.config.agents[1].name;
        UI.agent1.personality.textContent = data.config.agents[0].personality || '--';
        UI.agent2.personality.textContent = data.config.agents[1].personality || '--';
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
    const { agent_id, stage, data: pipelineData } = data;
    
    // If we receive components data, recreate the pipeline
    if (pipelineData && pipelineData.components && Array.isArray(pipelineData.components)) {
        PipelineManager.createPipelineFlow(agent_id, pipelineData.components);
    }
    
    // Only update on non-start events
    if (stage && !stage.endsWith('_start')) {
        PipelineManager.updatePipelineStage(agent_id, stage);
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

// Initialize the UI after the document has loaded
document.addEventListener('DOMContentLoaded', () => {
    // Debug check for conversation container
    console.log('DOMContentLoaded event fired');
    const conversationContainer = document.getElementById('conversation-messages');
    if (conversationContainer) {
        console.log('Conversation container found:', conversationContainer);
        // Add a test message to verify container is working
        ChatManager.addMessage('Debug', 'Container initialized successfully', null);
    } else {
        console.error('Conversation container not found! Check your HTML.');
    }
}); 