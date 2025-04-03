"""
Audio Processor Module for Piano Chorus Creator

This module handles audio file processing, including format conversion,
normalization, and feature extraction for melody analysis.
"""

import os
import logging
import tempfile
from typing import Dict, Optional, Tuple
import librosa
import numpy as np
import soundfile as sf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AudioProcessor:
    """
    Class for processing audio files for melody extraction.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the audio processor.
        
        Args:
            output_dir: Directory to save processed audio files.
                        If None, a temporary directory will be used.
        """
        self.output_dir = output_dir or tempfile.mkdtemp()
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Audio processor initialized with output directory: {self.output_dir}")
        
        # Supported audio formats
        self.supported_formats = ['.mp3', '.wav', '.ogg', '.flac', '.m4a']
    
    def is_valid_audio_file(self, file_path: str) -> bool:
        """
        Check if the file is a valid audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            return False
            
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.supported_formats:
            logger.error(f"Unsupported audio format: {file_ext}")
            return False
            
        try:
            # Try to load a small portion of the file to verify it's valid
            y, sr = librosa.load(file_path, sr=None, duration=1.0)
            return True
        except Exception as e:
            logger.error(f"Error loading audio file: {str(e)}")
            return False
    
    def process_audio(self, file_path: str, task_id: str) -> Tuple[bool, str, Dict]:
        """
        Process an audio file for melody extraction.
        
        Args:
            file_path: Path to the audio file
            task_id: Unique identifier for the task
            
        Returns:
            Tuple containing:
                - Success status (bool)
                - Path to processed audio file (str)
                - Additional info about the processing (Dict)
        """
        if not self.is_valid_audio_file(file_path):
            return False, "", {"error": "Invalid audio file"}
        
        output_file = os.path.join(self.output_dir, f"{task_id}_processed.wav")
        
        try:
            logger.info(f"Processing audio file: {file_path}")
            
            # Load audio file
            y, sr = librosa.load(file_path, sr=None)
            
            # Get audio duration
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Normalize audio
            y_normalized = librosa.util.normalize(y)
            
            # Save processed audio
            sf.write(output_file, y_normalized, sr)
            
            logger.info(f"Successfully processed audio to {output_file}")
            return True, output_file, {
                "duration": duration,
                "sample_rate": sr,
                "channels": 1 if y.ndim == 1 else y.shape[0]
            }
                
        except Exception as e:
            logger.error(f"Error processing audio file: {str(e)}")
            return False, "", {"error": str(e)}
    
    def extract_features(self, file_path: str) -> Dict:
        """
        Extract audio features for melody analysis.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dict containing extracted features
        """
        if not self.is_valid_audio_file(file_path):
            return {"error": "Invalid audio file"}
        
        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=None)
            
            # Extract features
            # Spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            # Rhythmic features
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            
            # Harmonic features
            harmonic, percussive = librosa.effects.hpss(y)
            chroma = librosa.feature.chroma_cqt(y=harmonic, sr=sr)
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            return {
                "duration": librosa.get_duration(y=y, sr=sr),
                "sample_rate": sr,
                "tempo": tempo,
                "spectral_centroid_mean": np.mean(spectral_centroid),
                "spectral_bandwidth_mean": np.mean(spectral_bandwidth),
                "spectral_rolloff_mean": np.mean(spectral_rolloff),
                "mfccs_mean": np.mean(mfccs, axis=1).tolist(),
                "chroma_mean": np.mean(chroma, axis=1).tolist()
            }
                
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            return {"error": str(e)}


# Example usage
if __name__ == "__main__":
    # This code will only run if the file is executed directly
    processor = AudioProcessor()
    
    # Example with a test file
    test_file = "path/to/test/audio.mp3"  # Replace with an actual file path for testing
    
    if os.path.exists(test_file):
        # Process audio
        success, file_path, process_info = processor.process_audio(test_file, "test_task")
        if success:
            print(f"Processed to: {file_path}")
            print(f"Process info: {process_info}")
            
            # Extract features
            features = processor.extract_features(file_path)
            print(f"Extracted features: {features}")
        else:
            print(f"Processing failed: {process_info}")
    else:
        print(f"Test file not found: {test_file}")
