/**
 * Pipeline Manager Module
 * Handles visualization and updates of the agent pipeline
 */

const PipelineManager = {
    // Track pipeline states
    pipelineStates: {
        0: { components: [], currentStep: 0, isActive: false },
        1: { components: [], currentStep: 0, isActive: false }
    },

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
        
        // Store components for this agent
        this.pipelineStates[agentId].components = components;
        this.pipelineStates[agentId].currentStep = 0;
        this.pipelineStates[agentId].isActive = false;
        
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
        
        const pipelineState = this.pipelineStates[agentId];
        const stageIndex = pipelineState.components.indexOf(stage);
        
        if (stageIndex !== -1) {
            pipelineState.currentStep = stageIndex;
        }
        
        // Remove current class from all summaries for this agent
        const summaries = document.querySelectorAll(`.pipeline-summary[id^="${agentId}-"]`);
        summaries.forEach(summary => summary.classList.remove('current'));
        
        // Add current class to current stage summary
        const currentSummary = document.getElementById(`${agentId}-${stage}-summary`);

        if (currentSummary) {
            currentSummary.classList.add('current');

            // Update summary content
            if (data.summary) {
                currentSummary.textContent = `"${data.summary}"`;
            }
            
            // Check if this is the last step
            if (stageIndex === pipelineState.components.length - 1) {
                // Last step updated, activate the flag and switch it
                pipelineState.isActive = true;
                this.switchActiveFlag(agentId);
            }
        } else {
            console.warn(`Pipeline stage element not found: ${agentId}-${stage}-summary`);
        }
    },

    /**
     * Switches the active flag state after the last pipeline step
     * @param {number} agentId - The ID of the agent
     */
    switchActiveFlag(agentId) {
        const pipelineState = this.pipelineStates[agentId];
        
        if (pipelineState.isActive) {
            // Toggle the active state
            pipelineState.isActive = !pipelineState.isActive;
            
            // Add visual indication or trigger any post-completion logic here
            console.log(`Agent ${agentId} pipeline completed and active flag switched`);
            
            // You can add additional logic here like:
            // - Triggering animations
            // - Enabling/disabling UI elements
            // - Starting next phase of processing
            
            // Example: Add a completed class to the pipeline
            const pipelineElement = agentId === 0 
                ? document.getElementById('agent1-pipeline') 
                : document.getElementById('agent2-pipeline');
            
            if (pipelineElement) {
                pipelineElement.classList.toggle('pipeline-completed');
            }
        }
    },

    /**
     * Gets the current active flag state for an agent
     * @param {number} agentId - The ID of the agent
     * @returns {boolean} - The active flag state
     */
    getActiveFlag(agentId) {
        return this.pipelineStates[agentId].isActive;
    }
};

export default PipelineManager; 