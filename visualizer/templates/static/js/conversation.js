/**
 * Conversation Controller Module
 * Handles starting and managing conversations
 */

import State from './state.js';
import ChatManager from './chat.js';

// Get the socket instance from global scope
const socket = window.socket;

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

export default ConversationController; 