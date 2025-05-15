/**
 * Main application entry point
 * Sets up the Socket.IO connection and initializes the application
 */

import { initializeSocketEvents } from './socket-events.js';
import ChatManager from './chat.js';

// Initialize the UI after the document has loaded
document.addEventListener('DOMContentLoaded', () => {
    // Debug check for conversation container
    console.log('DOMContentLoaded event fired');
    const conversationContainer = document.getElementById('conversation-messages');
    if (conversationContainer) {
        console.log('Conversation container found:', conversationContainer);
        // Add a test message to verify container is working
        ChatManager.addMessage('Debug', 'Container initialized successfully', null);
    } else {
        console.error('Conversation container not found! Check your HTML.');
    }
    
    // Initialize Socket.IO connection and event handlers
    if (typeof io !== 'undefined') {
        initializeSocketEvents(io);
    } else {
        console.error('Socket.IO not loaded! Check your script tags.');
    }
}); 