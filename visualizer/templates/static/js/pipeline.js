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

        // New: create a row for summaries
        const summaryRow = document.createElement('div');
        summaryRow.className = 'pipeline-summary-row';
        summaryRow.style.display = 'flex';
        summaryRow.style.flexDirection = 'row';
        summaryRow.style.justifyContent = 'space-between';
        summaryRow.style.width = '100%';
        summaryRow.style.marginTop = '8px';

        components.forEach((component, index) => {
            const stepContainer = document.createElement('div');
            stepContainer.className = 'pipeline-step';

            const circle = document.createElement('div');
            circle.className = 'pipeline-circle';
            circle.id = `${agentId}-${component}`;
            circle.textContent = component;
            stepContainer.appendChild(circle);

            // Move summary to summary row instead of inside step
            const summary = document.createElement('div');
            summary.className = 'pipeline-summary';
            summary.id = `${agentId}-${component}-summary`;
            summaryRow.appendChild(summary);

            // Add the step to the pipeline
            pipelineContainer.appendChild(stepContainer);

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
        
        // Append the new pipeline and summary row
        pipelineElement.appendChild(pipelineContainer);
        pipelineElement.appendChild(summaryRow);
    },

    /**
     * Updates the active stage in a pipeline visualization
     * @param {number} agentId - The ID of the agent (0 or 1)
     * @param {string} stage - The active stage name
     * @param {Object} data - The pipeline data including summary
     */
    updatePipelineStage(agentId, stage, data = {}) {
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

            // Update summary in the summary row
            const summary = document.getElementById(`${agentId}-${stage}-summary`);
            if (summary && data.summary) {
                summary.textContent = data.summary;
            }
        } else {
            console.warn(`Pipeline stage element not found: ${agentId}-${stage}`);
        }
    }
};

export default PipelineManager; 