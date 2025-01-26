// Emoji data with labels
const emojis = [
    { symbol: "😍", label: "In Love" },
    { symbol: "🥳", label: "Party Time" },
    { symbol: "😎", label: "Feeling Cool" },
    { symbol: "😢", label: "Sad Vibes" },
    { symbol: "😂", label: "LOL Mood" },
    { symbol: "🤬", label: "Angry AF" },
    { symbol: "❤️", label: "Pure Love" },
    { symbol: "🔥", label: "Fire Track" },
    { symbol: "💃", label: "Dance Mood" }
];

// DOM Elements
const youtubeInput = document.getElementById('youtube-link');
const previewBtn = document.getElementById('preview-btn');
const videoPreview = document.getElementById('video-preview');
const messageDiv = document.getElementById('message');
const emojiGrid = document.querySelector('.emoji-grid');

// Initialize emoji grid
function initializeEmojiGrid() {
    emojiGrid.innerHTML = emojis.map(emoji => `
        <div class="emoji-container">
            <button class="emoji-btn" data-emoji="${emoji.symbol}">${emoji.symbol}</button>
            <div class="emoji-label">${emoji.label}</div>
        </div>
    `).join('');
}

// YouTube URL parsing regex
const youtubeRegex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;

// State
let selectedEmoji = null;
let currentVideoId = null;

// Functions
function extractVideoId(url) {
    const match = url.match(youtubeRegex);
    return match ? match[1] : null;
}

function updateVideoPreview(videoId) {
    if (!videoId) {
        videoPreview.innerHTML = '<p class="error">Invalid YouTube URL</p>';
        return;
    }

    currentVideoId = videoId;
    const embedUrl = `https://www.youtube.com/embed/${videoId}`;
    videoPreview.innerHTML = `
        <iframe
            src="${embedUrl}"
            title="YouTube video player"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
        </iframe>
    `;
}

function handleEmojiSelection(emoji, button) {
    // Remove selection from previously selected emoji container
    document.querySelector('.emoji-container.selected')?.classList.remove('selected');
    
    // Find the container of the clicked button
    const container = button.closest('.emoji-container');
    
    // Update selection
    selectedEmoji = emoji;
    container.classList.add('selected');
    
    // Show message
    messageDiv.textContent = `You chose ${emoji}!`;
    messageDiv.style.opacity = 1;

    // Fade out message after 2 seconds
    setTimeout(() => {
        messageDiv.style.opacity = 0;
    }, 2000);
}

// Event Listeners
previewBtn.addEventListener('click', () => {
    const url = youtubeInput.value.trim();
    const videoId = extractVideoId(url);
    updateVideoPreview(videoId);
});

youtubeInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const url = youtubeInput.value.trim();
        const videoId = extractVideoId(url);
        updateVideoPreview(videoId);
    }
});

// Initialize emoji grid and set up event listeners
initializeEmojiGrid();

// Add click event listeners to emoji buttons
document.querySelectorAll('.emoji-btn').forEach(button => {
    button.addEventListener('click', async () => {
        const emoji = button.getAttribute('data-emoji');
        handleEmojiSelection(emoji, button);

        if (!currentVideoId) {
            messageDiv.textContent = 'Please preview a video first!';
            messageDiv.style.opacity = 1;
            setTimeout(() => {
                messageDiv.style.opacity = 0;
            }, 2000);
            return;
        }

        const youtubeLink = youtubeInput.value;

        messageDiv.textContent = 'Processing your audio... Please wait...';
        messageDiv.style.opacity = 1;
        button.classList.add('selected');

        try {
            const response = await fetch('http://localhost:5000/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    youtubeLink,
                    emoji: selectedEmoji
                })
            });

            if (!response.ok) {
                throw new Error('Failed to process audio');
            }

            // Get the blob from the response
            const blob = await response.blob();
            
            // Create a URL for the blob
            const url = window.URL.createObjectURL(blob);
            
            // Create an audio element
            const audio = document.createElement('audio');
            audio.controls = true;
            audio.src = url;
            
            // Add the audio element to the page
            const audioContainer = document.createElement('div');
            audioContainer.className = 'audio-preview';
            audioContainer.innerHTML = `
                <h3>Processed Audio 🎵</h3>
                <a href="${url}" download="processed_audio.mp3" class="download-btn">Download</a>
            `;
            audioContainer.prepend(audio);
            
            // Remove any existing audio preview
            const existingPreview = document.querySelector('.audio-preview');
            if (existingPreview) {
                existingPreview.remove();
            }
            
            // Add the new audio preview after the video preview
            videoPreview.after(audioContainer);
            
            messageDiv.textContent = 'Audio processed successfully! You can now play or download it.';
            messageDiv.style.opacity = 1;
            setTimeout(() => {
                messageDiv.style.opacity = 0;
            }, 2000);
        } catch (error) {
            messageDiv.textContent = 'Error processing audio: ' + error.message;
            messageDiv.style.opacity = 1;
            setTimeout(() => {
                messageDiv.style.opacity = 0;
            }, 2000);
        } finally {
            button.classList.remove('selected');
        }
    });
});

// Add input validation visual feedback
youtubeInput.addEventListener('input', () => {
    const url = youtubeInput.value.trim();
    const isValid = youtubeRegex.test(url);
    youtubeInput.style.borderColor = isValid ? 'var(--primary-color)' : '#ff3333';
});
