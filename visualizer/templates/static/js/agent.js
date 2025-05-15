/**
 * Agent Manager Module
 * Handles agent state updates and visualization
 */

import Logger from './logger.js';
import PipelineManager from './pipeline.js';

const AgentManager = {
    /**
     * Updates agent information in the UI
     * @param {number} agentId - The ID of the agent (0 or 1)
     * @param {Object} data - The data to update with
     */
    updateAgentInfo(agentId, data) {
        const agentName = agentId === 0 ? 'agent1' : 'agent2';
        const agent = {
            name: document.getElementById(`${agentName}-name`),
            personality: document.getElementById(`${agentName}-personality`),
            tension: document.getElementById(`${agentName}-tension`),
            goal: document.getElementById(`${agentName}-goal`),
            tactic: document.getElementById(`${agentName}-tactic`),
            plan: document.getElementById(`${agentName}-plan`)
        };
        
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
        
        // Update all agent info
        this.updateAgentInfo(agentId, agentState);
        
        // Restore pipeline if it exists
        if (agentState.pipeline && agentState.pipeline.components) {
            PipelineManager.createPipelineFlow(agentId, agentState.pipeline.components);
            if (agentState.pipeline.stage) {
                PipelineManager.updatePipelineStage(agentId, agentState.pipeline.stage);
            }
        }
    }
};

export default AgentManager; 