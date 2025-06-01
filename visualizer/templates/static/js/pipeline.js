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
            // Create a column that contains both title and summary
            const columnContainer = document.createElement('div');
            columnContainer.className = 'pipeline-column';

            // Create the step container for the title
            const stepContainer = document.createElement('div');
            stepContainer.className = 'pipeline-step';

            // Create the title element
            const title = document.createElement('div');
            title.className = 'pipeline-title';
            title.id = `${agentId}-${component}-title`;
            title.textContent = component;
            stepContainer.appendChild(title);

            // Create the summary for this column
            const summary = document.createElement('div');
            summary.className = 'pipeline-summary';
            summary.id = `${agentId}-${component}-summary`;

            // Add both to the column
            columnContainer.appendChild(stepContainer);
            columnContainer.appendChild(summary);

            // Add the column to the pipeline
            pipelineContainer.appendChild(columnContainer);

            // Add arrow between columns (not taking flex space)
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
        
        // Append the new pipeline structure
        pipelineElement.appendChild(pipelineContainer);
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
        
        // Remove active class from all summaries for this agent
        const summaries = document.querySelectorAll(`.pipeline-summary[id^="${agentId}-"]`);
        summaries.forEach(summary => summary.classList.remove('active'));
        
        // Add active class to current stage summary
        const currentSummary = document.getElementById(`${agentId}-${stage}-summary`);

        if (currentSummary) {
            currentSummary.classList.add('active');

            // Update summary content
            if (data.summary) {
                currentSummary.textContent = data.summary;
            }
        } else {
            console.warn(`Pipeline stage element not found: ${agentId}-${stage}-summary`);
        }
    }
};

export default PipelineManager; 