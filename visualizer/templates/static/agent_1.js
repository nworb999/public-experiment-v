let socket;
let lastEmotion = 'neutral';
let currentMessage = '';
let typingTimeout = null;

const aliceImg = document.getElementById('alice-img');
const dialogueContent = document.getElementById('dialogue-content');

function updateAgentImage(emotion) {
    if (!emotion) emotion = 'neutral';
    if (lastEmotion === emotion) return;
    lastEmotion = emotion;
    aliceImg.src = `/static/alice/${emotion}.png`;
    console.log(`Alice emotion updated to: ${emotion}`);
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
    console.log(`Alice dialogue updated: ${message.substring(0, 50)}...`);
    
    // Use typewriter effect to display the message
    typeWriterEffect(message, dialogueContent, 30); // 30ms between characters
}

function clearDialogueBox() {
    dialogueContent.innerHTML = '<span class="agent-1-placeholder-text">Waiting for Alice to speak...</span>';
    dialogueContent.classList.remove('has-message');
    currentMessage = '';
    console.log('Alice dialogue cleared');
}

function findLatestAgentMessage(messages) {
    // Find the most recent message from this agent (sender_id = 0)
    for (let i = messages.length - 1; i >= 0; i--) {
        const msg = messages[i];
        if (msg.sender_id === 0 && msg.message && msg.message.trim() !== '') {
            return msg;
        }
    }
    return null;
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('Alice agent page loaded');
    socket = io();

    function handleMessage(data) {
        console.log('Alice received message event:', data);
        
        // Check if this message is for Alice (agent 0)
        if (data.sender_id !== 0) return;
        
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
        console.log('Alice received state restore:', data);
        
        // Restore the latest message from Alice if available
        if (data.messages && Array.isArray(data.messages)) {
            const latestMessage = findLatestAgentMessage(data.messages);
            if (latestMessage) {
                console.log('Restoring Alice message:', latestMessage.message.substring(0, 50));
                
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
        console.log('Alice received conversation status:', data);
        if (data.status === 'started') {
            clearDialogueBox();
        }
    });

    socket.on('connect', () => {
        console.log('Alice agent page connected to socket');
    });

    socket.on('disconnect', () => {
        console.log('Alice agent page disconnected from socket');
    });
}); 