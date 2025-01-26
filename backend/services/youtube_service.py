import os
import requests
import re
import logging
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def extract_video_id(url):
    """Extract YouTube video ID from various URL formats."""
    # Regular YouTube URL
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in {'www.youtube.com', 'youtube.com'}:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # If nothing is found
    raise ValueError(f'Invalid YouTube URL: {url}')

def download_youtube_audio(url, output_path):
    """
    Download audio from a YouTube video using Fast YouTube to MP3 Converter API.
    
    Args:
        url (str): YouTube video URL
        output_path (str): Directory to save the audio file
        
    Returns:
        str: Path to the downloaded audio file
    """
    try:
        logger.info(f"Processing YouTube URL: {url}")
        
        # Extract video ID
        video_id = extract_video_id(url)
        logger.info(f"Extracted video ID: {video_id}")
        
        # API endpoint
        api_url = "https://youtube-mp36.p.rapidapi.com/dl"
        querystring = {"id": video_id}
        
        headers = {
            "X-RapidAPI-Key": os.getenv('RAPIDAPI_KEY'),
            "X-RapidAPI-Host": "youtube-mp36.p.rapidapi.com"
        }
        
        logger.info("Requesting conversion from RapidAPI...")
        response = requests.get(api_url, headers=headers, params=querystring)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"API Response: {data}")
        
        if 'link' not in data:
            raise Exception(f"Unexpected API response: {data}")
            
        download_url = data['link']
        if not download_url:
            raise Exception("No download URL received from API")
            
        # Download the converted file
        logger.info("Downloading converted audio file...")
        audio_response = requests.get(download_url, stream=True)
        audio_response.raise_for_status()
        
        # Save the file
        output_file = os.path.join(output_path, f"{video_id}.mp3")
        with open(output_file, 'wb') as f:
            for chunk in audio_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        logger.info(f"Audio file saved to: {output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"Error downloading YouTube audio: {str(e)}", exc_info=True)
        raise Exception(f"Failed to download YouTube audio: {str(e)}")
