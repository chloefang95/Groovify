from pydub import AudioSegment
import librosa
import numpy as np
import os

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
        # Load the audio file
        audio = AudioSegment.from_file(input_path)
        
        # Detect original BPM using librosa
        y, sr = librosa.load(input_path)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        
        # Calculate speed ratio
        speed_ratio = target_bpm / tempo if tempo > 0 else target_bpm / 100.0
        
        # Apply time stretching while preserving pitch
        stretched = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed_ratio)
        }).set_frame_rate(audio.frame_rate)
        
        # Export the processed audio
        stretched.export(output_path, format="mp3")
        
        return output_path
        
    except Exception as e:
        raise Exception(f"Error processing audio: {str(e)}")
