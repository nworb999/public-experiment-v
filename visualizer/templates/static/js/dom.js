/**
 * DOM Elements Module
 * Contains references to all DOM elements used in the application
 */

const UI = {
    // Conversation container
    conversationMessages: document.getElementById('conversation-messages'),
    
    // Prompt and response elements
    promptBoxes: [
        document.getElementById('prompt-box-1'),
        document.getElementById('prompt-box-2'),
        document.getElementById('prompt-box-3')
    ],
    promptTitles: [
        document.getElementById('prompt-title-1'),
        document.getElementById('prompt-title-2'),
        document.getElementById('prompt-title-3')
    ],
    responseBoxes: [
        document.getElementById('response-box-1'),
        document.getElementById('response-box-2'),
        document.getElementById('response-box-3')
    ],
    responseTimeDisplays: [
        document.getElementById('response-time-1'),
        document.getElementById('response-time-2'),
        document.getElementById('response-time-3')
    ],
    
    // Agent 1 elements
    agent1: {
        name: document.getElementById('agent1-name'),
        pipeline: document.getElementById('agent1-pipeline'),
        personality: document.getElementById('agent1-personality'),
        tension: document.getElementById('agent1-tension'),
        goal: document.getElementById('agent1-goal'),
        tactic: document.getElementById('agent1-tactic'),
        plan: document.getElementById('agent1-plan')
    },
    
    // Agent 2 elements
    agent2: {
        name: document.getElementById('agent2-name'),
        pipeline: document.getElementById('agent2-pipeline'),
        personality: document.getElementById('agent2-personality'),
        tension: document.getElementById('agent2-tension'),
        goal: document.getElementById('agent2-goal'),
        tactic: document.getElementById('agent2-tactic'),
        plan: document.getElementById('agent2-plan')
    }
};

export default UI; 