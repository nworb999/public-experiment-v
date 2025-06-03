/**
 * Conversation Page JavaScript
 * Handles Socket.IO connection and chat messages for the conversation-only page
 */

import ChatManager from './js/chat.js';

// Initialize the UI after the document has loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('Conversation page loaded');
    
    // Verify conversation container exists
    const conversationContainer = document.getElementById('conversation-messages');
    if (conversationContainer) {
        console.log('Conversation container found:', conversationContainer);
    } else {
        console.error('Conversation container not found! Check your HTML.');
        return;
    }
    
    // Note: Socket.IO connection is handled by the main application via socket-events.js
    // This avoids duplicate connections and auto-start requests
    console.log('Socket.IO connection managed by main application');
}); 