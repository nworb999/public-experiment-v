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
    
    // Initialize Socket.IO connection
    if (typeof io !== 'undefined') {
        const socket = io();
        
        // Handle incoming messages
        socket.on('add_message', (data) => {
            ChatManager.addMessage(data.sender, data.message, data.sender_id);
        });
        
        // Handle connection events
        socket.on('connect', () => {
            console.log('Connected to server');
        });
        
        socket.on('disconnect', () => {
            console.log('Disconnected from server');
        });
        
        // Request conversation history on connect
        socket.on('connect', () => {
            // Auto-start conversation if not already active
            socket.emit('request_autostart');
        });
        
    } else {
        console.error('Socket.IO not loaded! Check your script tags.');
    }
}); 