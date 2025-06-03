let socket;
let lastEmotion = 'neutral';

const morganImg = document.getElementById('morgan-img');

function updateAgentImage(emotion) {
    if (!emotion) emotion = 'neutral';
    if (lastEmotion === emotion) return; // Only update if changed
    lastEmotion = emotion;
    morganImg.src = `/static/morgan/${emotion}.png`;
}

document.addEventListener('DOMContentLoaded', () => {
    socket = io();

    function handleMessage(data) {
        if (data.sender_id !== 1) return;
        const emotion = data.emotion || 'neutral';
        updateAgentImage(emotion);
    }

    socket.on('add_message', handleMessage);
    socket.on('message', handleMessage);
}); 