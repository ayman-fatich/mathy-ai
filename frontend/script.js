const promptInput = document.getElementById('prompt');
const chatHistory = document.getElementById('chat-history');
const videoPlayer = document.getElementById('videoPlayer');
const videoWrapper = document.getElementById('video-wrapper');
const placeholder = document.getElementById('placeholder-state');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');

// Auto-resize textarea
promptInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// Handle Enter key
promptInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

function addMessage(text, isUser = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user' : 'system'}`;
    
    msgDiv.innerHTML = `
        <div class="avatar">
            <i class="fa-solid ${isUser ? 'fa-user' : 'fa-robot'}"></i>
        </div>
        <div class="bubble">${text}</div>
    `;
    
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

async function sendMessage() {
    const text = promptInput.value.trim();
    const provider = document.getElementById('provider').value;
    
    if (!text) return;

    // 1. Add User Message
    addMessage(text, true);
    promptInput.value = '';
    promptInput.style.height = 'auto';

    // 2. Show Loading State
    loadingOverlay.classList.remove('hidden');
    videoWrapper.classList.remove('hidden'); // Ensure wrapper is visible to show overlay on top
    placeholder.style.display = 'none';
    
    // Cycle loading texts
    loadingText.innerText = "🧠 AI is writing the script...";
    const loadingInterval = setInterval(() => {
        const states = [
            "🧠 AI is writing the script...",
            "🎨 Setting up the scene...",
            "🎬 Rendering frames...",
            "🔊 Generating audio...",
            "📦 Finalizing video..."
        ];
        // Pick a random state roughly every 3 seconds to keep it alive
        const randomState = states[Math.floor(Math.random() * states.length)];
        loadingText.innerText = randomState;
    }, 3000);

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: text, provider: provider })
        });

        const data = await response.json();

        clearInterval(loadingInterval);
        loadingOverlay.classList.add('hidden');

        if (data.status === 'success') {
            // 3. Update Video
            const timestamp = new Date().toLocaleTimeString();
            document.getElementById('renderTime').innerText = `Rendered at ${timestamp}`;
            
            // Force browser to reload video by appending random query param
            const videoUrl = `${data.video_path}?t=${Date.now()}`;
            
            videoPlayer.src = videoUrl;
            videoPlayer.load();
            videoPlayer.play(); // Auto-play the new version
            
            document.getElementById('downloadLink').href = videoUrl;
            
            addMessage("I've updated the video based on your request. How does it look?");
        } else {
            throw new Error(data.log || "Unknown error");
        }

    } catch (error) {
        clearInterval(loadingInterval);
        loadingOverlay.classList.add('hidden');
        addMessage(`❌ Error: ${error.message}`);
        console.error(error);
    }
}
