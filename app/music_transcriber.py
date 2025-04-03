"""
Music Transcription Module for Piano Chorus Creator

This module handles music transcription using Basic Pitch from Spotify.
It converts audio files to MIDI and extracts musical notes.
"""

import os
import logging
import tempfile
from typing import Dict, Optional, Tuple
import numpy as np
import pretty_midi
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MusicTranscriber:
    """
    Class for transcribing audio files to musical notes using Basic Pitch.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the music transcriber.
        
        Args:
            output_dir: Directory to save transcribed files.
                        If None, a temporary directory will be used.
        """
        self.output_dir = output_dir or tempfile.mkdtemp()
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Music transcriber initialized with output directory: {self.output_dir}")
    
    def transcribe_audio(self, audio_path: str, task_id: str) -> Tuple[bool, Dict, str]:
        """
        Transcribe an audio file to MIDI using Basic Pitch.
        
        Args:
            audio_path: Path to the audio file
            task_id: Unique identifier for the task
            
        Returns:
            Tuple containing:
                - Success status (bool)
                - Dictionary of transcription data
                - Path to the generated MIDI file
        """
        if not os.path.exists(audio_path):
            logger.error(f"Audio file does not exist: {audio_path}")
            return False, {"error": "Audio file not found"}, ""
        
        midi_path = os.path.join(self.output_dir, f"{task_id}.mid")
        
        try:
            logger.info(f"Transcribing audio file: {audio_path}")
            
            # Predict pitches and onsets using Basic Pitch
            model_output, midi_data, note_events = predict(
                audio_path,
                model_or_model_path=ICASSP_2022_MODEL_PATH,
                onset_threshold=0.5,
                frame_threshold=0.3,
                minimum_note_length=58,  # in ms
                minimum_frequency=30,  # in Hz
                maximum_frequency=1000,  # in Hz
                multiple_pitch_bends=False
            )
            
            # Save MIDI file
            midi_data.write(midi_path)
            
            # Extract basic information from the MIDI
            midi_info = self._extract_midi_info(midi_data)
            
            logger.info(f"Successfully transcribed audio to MIDI: {midi_path}")
            return True, midi_info, midi_path
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return False, {"error": str(e)}, ""
    
    def _extract_midi_info(self, midi_data: pretty_midi.PrettyMIDI) -> Dict:
        """
        Extract basic information from a MIDI file.
        
        Args:
            midi_data: PrettyMIDI object
            
        Returns:
            Dictionary containing MIDI information
        """
        # Get tempo
        tempo_changes = midi_data.get_tempo_changes()
        tempos = tempo_changes[1] if len(tempo_changes) > 1 else [120.0]
        
        # Get time signature
        time_signature_changes = midi_data.time_signature_changes
        time_signature = "4/4"  # Default
        if time_signature_changes:
            time_signature = f"{time_signature_changes[0].numerator}/{time_signature_changes[0].denominator}"
        
        # Get key signature
        key_signature_changes = midi_data.key_signature_changes
        key_signature = "C major"  # Default
        if key_signature_changes:
            key_signature = key_signature_changes[0].key_name
        
        # Count notes per instrument
        instruments_info = []
        total_notes = 0
        
        for instrument in midi_data.instruments:
            num_notes = len(instrument.notes)
            total_notes += num_notes
            
            instruments_info.append({
                "name": instrument.name or "Unknown",
                "program": instrument.program,
                "is_drum": instrument.is_drum,
                "num_notes": num_notes
            })
        
        # Get duration
        duration = midi_data.get_end_time()
        
        return {
            "tempo": tempos[0],
            "time_signature": time_signature,
            "key_signature": key_signature,
            "duration": duration,
            "total_notes": total_notes,
            "instruments": instruments_info
        }
    
    def extract_main_melody(self, midi_path: str, task_id: str) -> Tuple[bool, Dict, str]:
        """
        Extract the main melody from a MIDI file.
        
        Args:
            midi_path: Path to the MIDI file
            task_id: Unique identifier for the task
            
        Returns:
            Tuple containing:
                - Success status (bool)
                - Dictionary of melody data
                - Path to the generated melody MIDI file
        """
        if not os.path.exists(midi_path):
            logger.error(f"MIDI file does not exist: {midi_path}")
            return False, {"error": "MIDI file not found"}, ""
        
        melody_midi_path = os.path.join(self.output_dir, f"{task_id}_melody.mid")
        
        try:
            logger.info(f"Extracting main melody from MIDI: {midi_path}")
            
            # Load the MIDI file
            midi_data = pretty_midi.PrettyMIDI(midi_path)
            
            # Find the instrument with the most notes in the highest pitch range
            # This is a simple heuristic for finding the melody
            best_instrument = None
            highest_score = -1
            
            for instrument in midi_data.instruments:
                if instrument.is_drum:
                    continue
                
                if not instrument.notes:
                    continue
                
                # Calculate the average pitch
                pitches = [note.pitch for note in instrument.notes]
                avg_pitch = sum(pitches) / len(pitches)
                
                # Calculate a score based on number of notes and average pitch
                # Higher pitches and more notes are more likely to be the melody
                score = len(instrument.notes) * (avg_pitch / 127.0)
                
                if score > highest_score:
                    highest_score = score
                    best_instrument = instrument
            
            if best_instrument is None:
                logger.error("No suitable melody instrument found in MIDI")
                return False, {"error": "No suitable melody instrument found"}, ""
            
            # Create a new MIDI file with just the melody
            melody_midi = pretty_midi.PrettyMIDI()
            
            # Copy tempo and time signature information
            for tempo_change in midi_data.get_tempo_changes()[1]:
                melody_midi._tick_scales.append((0, 60.0 / tempo_change))
            
            for ts in midi_data.time_signature_changes:
                melody_midi.time_signature_changes.append(ts)
            
            for ks in midi_data.key_signature_changes:
                melody_midi.key_signature_changes.append(ks)
            
            # Create a new instrument for the melody
            melody_instrument = pretty_midi.Instrument(
                program=best_instrument.program,
                name="Melody"
            )
            
            # Add the notes from the best instrument
            for note in best_instrument.notes:
                melody_instrument.notes.append(note)
            
            melody_midi.instruments.append(melody_instrument)
            
            # Save the melody MIDI
            melody_midi.write(melody_midi_path)
            
            # Extract basic information from the melody MIDI
            melody_info = self._extract_midi_info(melody_midi)
            melody_info["original_instrument"] = best_instrument.name or "Unknown"
            
            logger.info(f"Successfully extracted melody to MIDI: {melody_midi_path}")
            return True, melody_info, melody_midi_path
                
        except Exception as e:
            logger.error(f"Error extracting melody: {str(e)}")
            return False, {"error": str(e)}, ""


# Example usage
if __name__ == "__main__":
    # This code will only run if the file is executed directly
    transcriber = MusicTranscriber()
    
    # Example with a test file
    test_file = "path/to/test/audio.mp3"  # Replace with an actual file path for testing
    
    if os.path.exists(test_file):
        # Transcribe audio
        success, midi_info, midi_path = transcriber.transcribe_audio(test_file, "test_task")
        if success:
            print(f"Transcribed to: {midi_path}")
            print(f"MIDI info: {midi_info}")
            
            # Extract melody
            success, melody_info, melody_midi_path = transcriber.extract_main_melody(midi_path, "test_task")
            if success:
                print(f"Melody extracted to: {melody_midi_path}")
                print(f"Melody info: {melody_info}")
            else:
                print(f"Melody extraction failed: {melody_info}")
        else:
            print(f"Transcription failed: {midi_info}")
    else:
        print(f"Test file not found: {test_file}")
