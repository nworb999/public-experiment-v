/**
 * Application State Module
 * Manages the global application state
 */

const State = {
    conversationActive: false,
    currentConversationId: null,
    agents: {
        0: { name: 'Agent 1' },
        1: { name: 'Agent 2' }
    }
};

export default State; 