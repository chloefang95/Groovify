from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv
from services.youtube_service import download_youtube_audio
from services.audio_processor import process_audio
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        logger.info("Received process request")
        data = request.get_json()
        
        if not data:
            logger.error("No JSON data received")
            return jsonify({'error': 'No data received'}), 400
            
        youtube_link = data.get('youtubeLink')
        emoji = data.get('emoji')
        
        logger.info(f"Processing request for YouTube link: {youtube_link} with emoji: {emoji}")
        
        if not youtube_link:
            logger.error("Missing YouTube link")
            return jsonify({'error': 'Missing YouTube link'}), 400
            
        if not emoji:
            logger.error("Missing emoji")
            return jsonify({'error': 'Missing emoji'}), 400
            
        if emoji not in EMOJI_BPM_MAP:
            logger.error(f"Unsupported emoji: {emoji}")
            return jsonify({'error': 'Unsupported emoji'}), 400
            
        # Get target BPM from emoji
        target_bpm = EMOJI_BPM_MAP[emoji]['bpm']
        emotion = EMOJI_BPM_MAP[emoji]['name']
        
        # Download YouTube audio
        try:
            audio_path = download_youtube_audio(youtube_link, UPLOAD_FOLDER)
            logger.info(f"Audio downloaded successfully to: {audio_path}")
            
            if not os.path.exists(audio_path):
                raise Exception(f"Downloaded file not found at {audio_path}")
                
            file_size = os.path.getsize(audio_path)
            logger.info(f"Downloaded file size: {file_size} bytes")
            
            if file_size == 0:
                raise Exception("Downloaded file is empty")
                
        except Exception as e:
            logger.error(f"Error downloading YouTube audio: {str(e)}", exc_info=True)
            return jsonify({'error': f'Failed to download YouTube audio: {str(e)}'}), 500
            
        # Process audio with target BPM
        try:
            output_path = os.path.join(OUTPUT_FOLDER, f"{emotion}_{os.path.basename(audio_path)}")
            logger.info(f"Processing audio to {target_bpm} BPM...")
            
            processed_path = process_audio(audio_path, target_bpm, output_path)
            logger.info(f"Audio processed successfully to: {processed_path}")
            
            if not os.path.exists(processed_path):
                raise Exception(f"Processed file not found at {processed_path}")
                
            processed_size = os.path.getsize(processed_path)
            logger.info(f"Processed file size: {processed_size} bytes")
            
            if processed_size == 0:
                raise Exception("Processed file is empty")
                
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}", exc_info=True)
            if os.path.exists(audio_path):
                os.remove(audio_path)
            return jsonify({'error': f'Failed to process audio: {str(e)}'}), 500
            
        # Clean up original file
        try:
            os.remove(audio_path)
            logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file: {str(e)}")
            
        # Return the processed file
        try:
            logger.info("Sending processed file to client")
            return send_file(processed_path, 
                           as_attachment=True,
                           download_name=f"{emotion}_audio.mp3",
                           mimetype='audio/mpeg')
        except Exception as e:
            logger.error(f"Error sending processed file: {str(e)}", exc_info=True)
            return jsonify({'error': f'Failed to send processed file: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if not os.getenv('RAPIDAPI_KEY'):
        logger.error("RAPIDAPI_KEY not found in environment variables")
        exit(1)
    logger.info("Starting Flask server...")
    app.run(debug=True, port=5000)
