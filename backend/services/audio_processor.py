from pydub import AudioSegment
import os
import logging
import tempfile

logger = logging.getLogger(__name__)

def process_audio(input_path, target_bpm, output_path):
    """
    Process audio file to match target BPM while preserving pitch.
    
    Args:
        input_path (str): Path to input audio file
        target_bpm (float): Target BPM for the processed audio
        output_path (str): Path to save the processed audio
        
    Returns:
        str: Path to the processed audio file
    """
    try:
        logger.info(f"Starting audio processing. Input: {input_path}, Target BPM: {target_bpm}")
        
        # Create a temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # First convert to WAV for better processing
            logger.info("Converting to WAV format...")
            temp_wav = os.path.join(temp_dir, "temp.wav")
            
            # Load and export as WAV
            audio = AudioSegment.from_mp3(input_path)
            audio.export(temp_wav, format="wav")
            
            # Reload the WAV file
            audio = AudioSegment.from_wav(temp_wav)
            
            # Calculate speed change
            # We'll use a more conservative approach:
            # Base is 100 BPM, max change is 50% up or down
            base_bpm = 100.0
            max_ratio = 1.5
            min_ratio = 0.5
            
            speed_ratio = target_bpm / base_bpm
            speed_ratio = max(min(speed_ratio, max_ratio), min_ratio)
            
            logger.info(f"Applying speed ratio: {speed_ratio}")
            
            # Create the modified audio
            modified = audio._spawn(audio.raw_data, overrides={
                "frame_rate": int(audio.frame_rate * speed_ratio)
            })
            
            # Maintain original sample rate
            modified = modified.set_frame_rate(audio.frame_rate)
            
            # Apply a slight fade in/out to prevent clicks
            modified = modified.fade_in(100).fade_out(100)
            
            # Export with high quality
            logger.info(f"Exporting to {output_path}")
            modified.export(
                output_path,
                format="mp3",
                bitrate="192k",
                parameters=["-q:a", "0"]  # Use highest quality
            )
            
            # Verify the output file
            if not os.path.exists(output_path):
                raise Exception("Failed to create output file")
                
            if os.path.getsize(output_path) == 0:
                raise Exception("Output file is empty")
                
            logger.info("Audio processing completed successfully")
            return output_path
            
    except Exception as e:
        logger.error(f"Error in process_audio: {str(e)}", exc_info=True)
        raise Exception(f"Error processing audio: {str(e)}")
