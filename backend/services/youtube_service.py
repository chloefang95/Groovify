from pytube import YouTube
import os

def download_youtube_audio(youtube_link, output_path):
    """
    Download audio from a YouTube video.
    
    Args:
        youtube_link (str): YouTube video URL
        output_path (str): Directory to save the audio file
        
    Returns:
        str: Path to the downloaded audio file
    """
    try:
        # Create YouTube object
        yt = YouTube(youtube_link)
        
        # Get audio stream
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        # Generate safe filename
        filename = f"{yt.title.replace(' ', '_')[:50]}.mp3"
        safe_filename = "".join(x for x in filename if x.isalnum() or x in "._- ")
        
        # Download the file
        output_file = os.path.join(output_path, safe_filename)
        audio_stream.download(output_path=output_path, filename=safe_filename)
        
        return output_file
        
    except Exception as e:
        raise Exception(f"Error downloading YouTube audio: {str(e)}")
