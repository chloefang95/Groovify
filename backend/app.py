from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from services.youtube_service import download_youtube_audio
from services.audio_processor import process_audio
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Create necessary directories
UPLOAD_FOLDER = 'temp'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Emoji to BPM mapping
EMOJI_BPM_MAP = {
    "😍": {"bpm": 90, "name": "in_love"},    # Romantic/jazzy vibe
    "🥳": {"bpm": 120, "name": "party"},     # Party Time (EDM vibe)
    "😎": {"bpm": 100, "name": "feeling_good"}, # Feeling Good
    "😢": {"bpm": 80, "name": "sad"},        # Sad
    "😂": {"bpm": 110, "name": "happy"},     # Happy
    "🤬": {"bpm": 140, "name": "angry"},     # Angry
    "❤️": {"bpm": 85, "name": "love"},      # Love
    "🔥": {"bpm": 130, "name": "fire"},     # Fire
    "💃": {"bpm": 115, "name": "dance"}     # Dance
}

@app.route('/process', methods=['POST'])
def process_song():
    try:
        data = request.get_json()
        youtube_link = data.get('youtubeLink')
        emoji = data.get('emoji')

        if not youtube_link or not emoji:
            return jsonify({'error': 'Missing required parameters'}), 400

        if emoji not in EMOJI_BPM_MAP:
            return jsonify({'error': 'Unsupported emoji'}), 400

        # Get target BPM from emoji
        target_bpm = EMOJI_BPM_MAP[emoji]['bpm']
        emotion = EMOJI_BPM_MAP[emoji]['name']

        # Download YouTube audio
        audio_path = download_youtube_audio(youtube_link, UPLOAD_FOLDER)
        
        # Process audio with target BPM
        output_path = os.path.join(OUTPUT_FOLDER, f"{emotion}_{os.path.basename(audio_path)}")
        processed_path = process_audio(audio_path, target_bpm, output_path)

        # Clean up original file
        os.remove(audio_path)

        # Return the processed file
        return send_file(processed_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
