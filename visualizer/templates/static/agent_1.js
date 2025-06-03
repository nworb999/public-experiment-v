let socket;
let lastEmotion = 'neutral';

const aliceImg = document.getElementById('alice-img');

function updateAgentImage(emotion) {
    if (!emotion) emotion = 'neutral';
    if (lastEmotion === emotion) return; // Only update if changed
    lastEmotion = emotion;
    aliceImg.src = `/static/alice/${emotion}.png`;
}

document.addEventListener('DOMContentLoaded', () => {
    socket = io();

    function handleMessage(data) {
        if (data.sender_id !== 0) return;
        const emotion = data.emotion || 'neutral';
        updateAgentImage(emotion);
    }

    socket.on('add_message', handleMessage);
    socket.on('message', handleMessage);
}); 