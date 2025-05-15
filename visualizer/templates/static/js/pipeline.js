/**
 * Pipeline Manager Module
 * Handles visualization and updates of the agent pipeline
 */

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
        const pipelineElement = agentId === 0 
            ? document.getElementById('agent1-pipeline') 
            : document.getElementById('agent2-pipeline');
        
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
        // TODO why 0-pipeline?
        if (currentCircle) {
            currentCircle.classList.add('active');
        } else {
            console.warn(`Pipeline stage element not found: ${agentId}-${stage}`);
        }
    }
};

export default PipelineManager; 