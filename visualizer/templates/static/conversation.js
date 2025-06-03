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

// Conversation Page JavaScript for fullscreen agent images

let socket;
let lastEmotion = { 0: 'neutral', 1: 'neutral' };

const aliceImg = document.getElementById('alice-img');
const morganImg = document.getElementById('morgan-img');

function updateAgentImage(agentId, emotion) {
    if (!emotion) emotion = 'neutral';
    if (lastEmotion[agentId] === emotion) return; // Only update if changed
    lastEmotion[agentId] = emotion;
    if (agentId === 0) {
        aliceImg.src = `/static/alice/${emotion}.png`;
    } else if (agentId === 1) {
        morganImg.src = `/static/morgan/${emotion}.png`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    socket = io();

    function handleMessage(data) {
        if (typeof data.sender_id !== 'number') return;
        const agentId = data.sender_id;
        const emotion = data.emotion || 'neutral';
        updateAgentImage(agentId, emotion);
    }

    socket.on('add_message', handleMessage);
    socket.on('message', handleMessage);
}); 