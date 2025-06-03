/**
 * Chat Manager Module
 * Handles displaying and managing conversation messages
 */

import UI from './dom.js';

const ChatManager = {
    /**
     * Adds a message to the conversation chat
     * @param {string} sender - Name of the message sender
     * @param {string} message - The message content
     * @param {number} [senderId] - The sender ID (0 or 1) for agents
     * @param {Object} [data] - Additional message data (e.g., emotion, original_speech)
     */
    addMessage(sender, message, senderId, data = {}) {
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
        
        // Add message content - use emotion if available, otherwise use message
        const contentElement = document.createElement('div');
        const displayText = data.emotion ? `[${data.emotion}]` : message;
        contentElement.textContent = displayText;
        
        // Add emotion styling if it's an emotion
        if (data.emotion) {
            contentElement.className = 'emotion-display';
            
            // Add the original speech as a title attribute for hover
            if (data.original_speech) {
                contentElement.title = `Original speech: "${data.original_speech}"`;
            }
        }
        
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

export default ChatManager; 