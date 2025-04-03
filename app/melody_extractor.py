"""
Melody Extractor Module for Piano Chorus Creator

This module handles the extraction of the main melody or chorus from transcribed music.
It builds on the music transcription functionality to identify the most recognizable parts.
"""

import os
import logging
import tempfile
from typing import Dict, Optional, Tuple, List
import numpy as np
import pretty_midi
from collections import Counter, defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MelodyExtractor:
    """
    Class for extracting the main melody or chorus from transcribed music.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the melody extractor.
        
        Args:
            output_dir: Directory to save extracted melody files.
                        If None, a temporary directory will be used.
        """
        self.output_dir = output_dir or tempfile.mkdtemp()
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Melody extractor initialized with output directory: {self.output_dir}")
    
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
            
            # Find the chorus/main part by identifying repeated patterns
            chorus_notes = self._identify_chorus(best_instrument.notes)
            
            # Add the chorus notes to the melody instrument
            for note in chorus_notes:
                melody_instrument.notes.append(note)
            
            melody_midi.instruments.append(melody_instrument)
            
            # Save the melody MIDI
            melody_midi.write(melody_midi_path)
            
            # Extract basic information
            melody_info = {
                "original_instrument": best_instrument.name or "Unknown",
                "program": best_instrument.program,
                "total_notes": len(best_instrument.notes),
                "chorus_notes": len(chorus_notes),
                "duration": melody_midi.get_end_time()
            }
            
            logger.info(f"Successfully extracted melody to MIDI: {melody_midi_path}")
            return True, melody_info, melody_midi_path
                
        except Exception as e:
            logger.error(f"Error extracting melody: {str(e)}")
            return False, {"error": str(e)}, ""
    
    def _identify_chorus(self, notes: List[pretty_midi.Note]) -> List[pretty_midi.Note]:
        """
        Identify the chorus or main part of a song by finding repeated patterns.
        
        Args:
            notes: List of MIDI notes
            
        Returns:
            List of notes that are part of the chorus
        """
        if not notes:
            return []
        
        # Sort notes by start time
        sorted_notes = sorted(notes, key=lambda note: note.start)
        
        # Divide the song into segments
        song_duration = max(note.end for note in notes)
        segment_duration = 4.0  # 4 seconds per segment
        num_segments = int(song_duration / segment_duration) + 1
        
        # Create a representation of each segment
        segments = [[] for _ in range(num_segments)]
        for note in sorted_notes:
            segment_idx = int(note.start / segment_duration)
            if segment_idx < num_segments:
                segments[segment_idx].append(note)
        
        # Create a fingerprint for each segment based on note patterns
        segment_fingerprints = []
        for segment in segments:
            if not segment:
                segment_fingerprints.append("")
                continue
                
            # Create a simple fingerprint based on relative pitch changes
            pitches = [note.pitch for note in sorted(segment, key=lambda n: n.start)]
            if len(pitches) <= 1:
                segment_fingerprints.append("")
                continue
                
            # Calculate pitch differences
            pitch_diffs = [pitches[i+1] - pitches[i] for i in range(len(pitches)-1)]
            fingerprint = ",".join(map(str, pitch_diffs))
            segment_fingerprints.append(fingerprint)
        
        # Count occurrences of each fingerprint
        fingerprint_counts = Counter(segment_fingerprints)
        
        # Find the most common fingerprint (excluding empty ones)
        most_common = None
        max_count = 0
        for fingerprint, count in fingerprint_counts.items():
            if fingerprint and count > max_count:
                most_common = fingerprint
                max_count = count
        
        if not most_common:
            # If no repeated patterns found, return all notes
            return notes
        
        # Find segments with the most common fingerprint
        chorus_segments = [i for i, fp in enumerate(segment_fingerprints) if fp == most_common]
        
        # Collect notes from chorus segments
        chorus_notes = []
        for segment_idx in chorus_segments:
            chorus_notes.extend(segments[segment_idx])
        
        # If we didn't find enough notes, return the original notes
        if len(chorus_notes) < len(notes) * 0.2:
            return notes
        
        return chorus_notes
    
    def extract_with_accompaniment(self, midi_path: str, task_id: str) -> Tuple[bool, Dict, str]:
        """
        Extract the main melody with basic chord accompaniment.
        
        Args:
            midi_path: Path to the MIDI file
            task_id: Unique identifier for the task
            
        Returns:
            Tuple containing:
                - Success status (bool)
                - Dictionary of arrangement data
                - Path to the generated arrangement MIDI file
        """
        if not os.path.exists(midi_path):
            logger.error(f"MIDI file does not exist: {midi_path}")
            return False, {"error": "MIDI file not found"}, ""
        
        arrangement_midi_path = os.path.join(self.output_dir, f"{task_id}_arrangement.mid")
        
        try:
            logger.info(f"Creating piano arrangement from MIDI: {midi_path}")
            
            # Load the MIDI file
            midi_data = pretty_midi.PrettyMIDI(midi_path)
            
            # First extract the melody
            success, melody_info, melody_midi_path = self.extract_main_melody(midi_path, task_id)
            if not success:
                return False, melody_info, ""
            
            # Load the melody MIDI
            melody_midi = pretty_midi.PrettyMIDI(melody_midi_path)
            if not melody_midi.instruments or not melody_midi.instruments[0].notes:
                return False, {"error": "No melody notes found"}, ""
            
            melody_notes = melody_midi.instruments[0].notes
            
            # Create a new MIDI file for the arrangement
            arrangement_midi = pretty_midi.PrettyMIDI()
            
            # Copy tempo and time signature information
            for tempo_change in midi_data.get_tempo_changes()[1]:
                arrangement_midi._tick_scales.append((0, 60.0 / tempo_change))
            
            for ts in midi_data.time_signature_changes:
                arrangement_midi.time_signature_changes.append(ts)
            
            for ks in midi_data.key_signature_changes:
                arrangement_midi.key_signature_changes.append(ks)
            
            # Create a right hand (treble) instrument for the melody
            right_hand = pretty_midi.Instrument(
                program=0,  # Acoustic Grand Piano
                name="Right Hand"
            )
            
            # Add the melody notes to the right hand
            for note in melody_notes:
                right_hand.notes.append(note)
            
            # Create a left hand (bass) instrument for accompaniment
            left_hand = pretty_midi.Instrument(
                program=0,  # Acoustic Grand Piano
                name="Left Hand"
            )
            
            # Generate basic chord accompaniment based on the melody
            accompaniment_notes = self._generate_accompaniment(melody_notes)
            
            # Add the accompaniment notes to the left hand
            for note in accompaniment_notes:
                left_hand.notes.append(note)
            
            arrangement_midi.instruments.append(right_hand)
            arrangement_midi.instruments.append(left_hand)
            
            # Save the arrangement MIDI
            arrangement_midi.write(arrangement_midi_path)
            
            # Extract basic information
            arrangement_info = {
                "melody_notes": len(melody_notes),
                "accompaniment_notes": len(accompaniment_notes),
                "duration": arrangement_midi.get_end_time()
            }
            
            logger.info(f"Successfully created arrangement: {arrangement_midi_path}")
            return True, arrangement_info, arrangement_midi_path
                
        except Exception as e:
            logger.error(f"Error creating arrangement: {str(e)}")
            return False, {"error": str(e)}, ""
    
    def _generate_accompaniment(self, melody_notes: List[pretty_midi.Note]) -> List[pretty_midi.Note]:
        """
        Generate basic chord accompaniment for a melody.
        
        Args:
            melody_notes: List of melody notes
            
        Returns:
            List of accompaniment notes
        """
        if not melody_notes:
            return []
        
        # Sort notes by start time
        sorted_notes = sorted(melody_notes, key=lambda note: note.start)
        
        # Determine the song duration
        song_duration = max(note.end for note in sorted_notes)
        
        # Divide the song into measures (assuming 4/4 time signature)
        measure_duration = 2.0  # 2 seconds per measure (moderate tempo)
        num_measures = int(song_duration / measure_duration) + 1
        
        # Group notes by measure
        measures = [[] for _ in range(num_measures)]
        for note in sorted_notes:
            measure_idx = int(note.start / measure_duration)
            if measure_idx < num_measures:
                measures[measure_idx].append(note)
        
        # Generate chords for each measure
        accompaniment_notes = []
        for measure_idx, measure_notes in enumerate(measures):
            if not measure_notes:
                continue
            
            # Find the most common pitches in the measure
            pitches = [note.pitch % 12 for note in measure_notes]  # Normalize to octave
            pitch_counts = Counter(pitches)
            
            # Get the most common pitch as the root note
            root_pitch = pitch_counts.most_common(1)[0][0] if pitch_counts else 0
            
            # Create a simple triad chord (root, third, fifth)
            # Major chord: root, root+4, root+7
            # Minor chord: root, root+3, root+7
            
            # Determine if major or minor based on the third most common in the melody
            has_major_third = (root_pitch + 4) % 12 in pitches
            has_minor_third = (root_pitch + 3) % 12 in pitches
            
            # Default to major if can't determine
            is_major = True
            if has_minor_third and not has_major_third:
                is_major = False
            
            # Create the chord in a lower octave
            base_octave = 4  # Middle C octave
            root_note = root_pitch + (base_octave - 1) * 12  # One octave lower
            
            third_interval = 4 if is_major else 3
            chord_pitches = [
                root_note,  # Root
                root_note + third_interval,  # Third
                root_note + 7  # Fifth
            ]
            
            # Add the chord notes
            measure_start = measure_idx * measure_duration
            measure_end = (measure_idx + 1) * measure_duration
            
            for pitch in chord_pitches:
                # Create a whole note for the chord
                chord_note = pretty_midi.Note(
                    velocity=70,  # Slightly softer than melody
                    pitch=pitch,
                    start=measure_start,
                    end=measure_end
                )
                accompaniment_notes.append(chord_note)
        
        return accompaniment_notes


# Example usage
if __name__ == "__main__":
    # This code will only run if the file is executed directly
    extractor = MelodyExtractor()
    
    # Example with a test file
    test_file = "path/to/test/midi.mid"  # Replace with an actual file path for testing
    
    if os.path.exists(test_file):
        # Extract melody
        success, melody_info, melody_midi_path = extractor.extract_main_melody(test_file, "test_task")
        if success:
            print(f"Melody extracted to: {melody_midi_path}")
            print(f"Melody info: {melody_info}")
            
            # Create arrangement
            success, arrangement_info, arrangement_midi_path = extractor.extract_with_accompaniment(test_file, "test_task")
            if success:
                print(f"Arrangement created at: {arrangement_midi_path}")
                print(f"Arrangement info: {arrangement_info}")
            else:
                print(f"Arrangement creation failed: {arrangement_info}")
        else:
            print(f"Melody extraction failed: {melody_info}")
    else:
        print(f"Test file not found: {test_file}")
