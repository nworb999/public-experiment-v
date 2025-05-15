/**
 * Conversation UI Manager Module
 * Handles the display of conversation UI elements
 */

import UI from './dom.js';

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

export default ConversationManager; 