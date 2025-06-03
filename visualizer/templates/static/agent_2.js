let socket;
let lastEmotion = 'neutral';
let currentMessage = '';
let typingTimeout = null;

const morganImg = document.getElementById('morgan-img');
const dialogueContent = document.getElementById('dialogue-content');

function updateAgentImage(emotion) {
    if (!emotion) emotion = 'neutral';
    if (lastEmotion === emotion) return;
    lastEmotion = emotion;
    morganImg.src = `/static/morgan/${emotion}.png`;
    console.log(`Morgan emotion updated to: ${emotion}`);
}

function typeWriterEffect(text, element, speed = 50) {
    // Clear any existing typing animation
    if (typingTimeout) {
        clearTimeout(typingTimeout);
        typingTimeout = null;
    }
    
    // Escape HTML to prevent XSS
    const escapedText = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    
    // Clear the element and show it has a message
    element.innerHTML = '';
    element.classList.add('has-message');
    
    let index = 0;
    
    function typeNextCharacter() {
        if (index < escapedText.length) {
            element.innerHTML += escapedText.charAt(index);
            index++;
            typingTimeout = setTimeout(typeNextCharacter, speed);
        }
    }
    
    // Start typing
    typeNextCharacter();
}

function updateDialogueBox(message) {
    if (!message || message.trim() === '') return;
    
    currentMessage = message;
    console.log(`Morgan dialogue updated: ${message.substring(0, 50)}...`);
    
    // Use typewriter effect to display the message
    typeWriterEffect(message, dialogueContent, 30); // 30ms between characters
}

function clearDialogueBox() {
    dialogueContent.innerHTML = '<span class="agent-2-placeholder-text">Waiting for Morgan to speak...</span>';
    dialogueContent.classList.remove('has-message');
    currentMessage = '';
    console.log('Morgan dialogue cleared');
}

function findLatestAgentMessage(messages) {
    // Find the most recent message from this agent (sender_id = 1)
    for (let i = messages.length - 1; i >= 0; i--) {
        const msg = messages[i];
        if (msg.sender_id === 1 && msg.message && msg.message.trim() !== '') {
            return msg;
        }
    }
    return null;
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('Morgan agent page loaded');
    socket = io();

    function handleMessage(data) {
        console.log('Morgan received message event:', data);
        
        // Check if this message is for Morgan (agent 1)
        if (data.sender_id !== 1) return;
        
        const emotion = data.emotion || 'neutral';
        updateAgentImage(emotion);
        
        // Determine what text to display - prioritize the styled message
        let speechToDisplay = '';
        if (data.speech) {
            // Use speech field if available (styled speech from ActionComponent)
            speechToDisplay = data.speech;
        } else if (data.original_speech) {
            // Fallback to original speech if styled speech not available
            speechToDisplay = data.original_speech;
        } else if (data.message && typeof data.message === 'string') {
            // Last fallback to message field if it's a string (not emotion data)
            speechToDisplay = data.message;
        }
        
        // Update dialogue box with the speech content
        if (speechToDisplay && speechToDisplay.trim() !== '') {
            updateDialogueBox(speechToDisplay);
        }
    }

    function handleStateRestore(data) {
        console.log('Morgan received state restore:', data);
        
        // Restore the latest message from Morgan if available
        if (data.messages && Array.isArray(data.messages)) {
            const latestMessage = findLatestAgentMessage(data.messages);
            if (latestMessage) {
                console.log('Restoring Morgan message:', latestMessage.message.substring(0, 50));
                
                // Determine what speech to display for restoration
                let speechToDisplay = '';
                if (latestMessage.original_speech) {
                    speechToDisplay = latestMessage.original_speech;
                } else if (latestMessage.message && typeof latestMessage.message === 'string') {
                    speechToDisplay = latestMessage.message;
                }
                
                if (speechToDisplay && speechToDisplay.trim() !== '') {
                    updateDialogueBox(speechToDisplay);
                }
                
                if (latestMessage.emotion) {
                    updateAgentImage(latestMessage.emotion);
                }
            }
        }
    }

    socket.on('add_message', handleMessage);
    socket.on('message', handleMessage);
    socket.on('restore_state', handleStateRestore);
    
    // Clear dialogue when conversation starts
    socket.on('conversation_status', (data) => {
        console.log('Morgan received conversation status:', data);
        if (data.status === 'started') {
            clearDialogueBox();
        }
    });

    socket.on('connect', () => {
        console.log('Morgan agent page connected to socket');
    });

    socket.on('disconnect', () => {
        console.log('Morgan agent page disconnected from socket');
    });
}); 