/**
 * Agent Conversation UI
 * Main JavaScript file for handling agent interactions and UI updates
 */

// DOM Elements
const UI = {
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
        goal: document.getElementById('agent1-goal')
    },
    
    // Agent 2 elements
    agent2: {
        name: document.getElementById('agent2-name'),
        pipeline: document.getElementById('agent2-pipeline'),
        personality: document.getElementById('agent2-personality'),
        tension: document.getElementById('agent2-tension'),
        goal: document.getElementById('agent2-goal')
    }
};

// Application state
const State = {
    conversationActive: false,
    currentConversationId: null
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
            agent.goal.textContent = data.goal;
        } else if (data.plan?.goal) {
            agent.goal.textContent = data.plan.goal;
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
        
        const agent = agentId === 0 ? UI.agent1 : UI.agent2;
        
        agent.name.textContent = agentState.name;
        agent.personality.textContent = agentState.personality;
        agent.tension.textContent = agentState.tension;
        agent.goal.textContent = agentState.goal;
        
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
    
    // Request to start a conversation (if auto-start is enabled)
    // This will be handled by the server according to its AUTO_START configuration
    socket.emit('request_autostart');
});

// Handle state restoration
socket.on('restore_state', (data) => {
    const { agent_states, conversation_history } = data;
    
    // Restore agent states
    if (agent_states) {
        AgentManager.restoreAgent(agent_states[0], 0);
        AgentManager.restoreAgent(agent_states[1], 1);
    }
    
    // Restore conversation history
    ConversationManager.restoreConversationHistory(conversation_history);
});

socket.on('initialize_agents', (data) => {
    if (data.agents && data.agents.length >= 2) {
        // Initialize agent 1
        if (data.agents[0]) {
            UI.agent1.name.textContent = data.agents[0].name || 'Agent 1';
            UI.agent1.personality.textContent = data.agents[0].personality || '--';
            UI.agent1.tension.textContent = data.agents[0].tension || 0;
            UI.agent1.goal.textContent = data.agents[0].goal || '--';
            if (data.agents[0].components && Array.isArray(data.agents[0].components)) {
                PipelineManager.createPipelineFlow(0, data.agents[0].components);
            }
        }
        
        // Initialize agent 2
        if (data.agents[1]) {
            UI.agent2.name.textContent = data.agents[1].name || 'Agent 2';
            UI.agent2.personality.textContent = data.agents[1].personality || '--';
            UI.agent2.tension.textContent = data.agents[1].tension || 0;
            UI.agent2.goal.textContent = data.agents[1].goal || '--';
            if (data.agents[1].components && Array.isArray(data.agents[1].components)) {
                PipelineManager.createPipelineFlow(1, data.agents[1].components);
            }
        }
    }
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

socket.on('message', (data) => {
    if (data.sender_id === 0 || data.sender_id === 1) {
        AgentManager.addMessage(data.sender_id, data.message);
    }
});

socket.on('add_message', (data) => {
    if (data.sender_id === 0 || data.sender_id === 1) {
        AgentManager.addMessage(data.sender_id, data.message);
    } else {
        // System message - show in both terminals
        const message = `[${data.sender}] ${data.message}`;
        AgentManager.addMessage(0, message);
        AgentManager.addMessage(1, message);
    }
});

socket.on('conversation_status', (data) => {
    // Update conversation state
    State.conversationActive = data.active;
    State.currentConversationId = data.conversation_id;
    
    // Add message to UI
    const message = `Conversation status: ${data.status}`;
    AgentManager.addMessage(0, message);
    AgentManager.addMessage(1, message);
});

// Listen for agent updates
socket.on('update_agent1', (data) => {
    AgentManager.updateAgentInfo(0, data);
});

socket.on('update_agent2', (data) => {
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

// Initialize the UI after the document has loaded
document.addEventListener('DOMContentLoaded', () => {
    // Auto-start is handled by the server configuration
}); 