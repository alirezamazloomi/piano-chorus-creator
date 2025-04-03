"""
Sheet Music Generator Module for Piano Chorus Creator

This module handles the generation of piano sheet music in PDF format
from MIDI files using music21 and LilyPond.
"""

import os
import logging
import tempfile
from typing import Dict, Optional, Tuple, List
import pretty_midi
from music21 import converter, stream, note, chord, clef, meter, key, tempo, metadata
from music21 import environment, midi

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SheetMusicGenerator:
    """
    Class for generating piano sheet music from MIDI files.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the sheet music generator.
        
        Args:
            output_dir: Directory to save generated sheet music files.
                        If None, a temporary directory will be used.
        """
        self.output_dir = output_dir or tempfile.mkdtemp()
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Sheet music generator initialized with output directory: {self.output_dir}")
        
        # Configure music21 environment to use LilyPond
        self.env = environment.Environment()
        try:
            # Check if LilyPond is installed
            lilypond_path = self.env.get('lilypondPath')
            if not lilypond_path:
                # Try to set the default path
                self.env['lilypondPath'] = '/usr/bin/lilypond'
                logger.info("Set LilyPond path to /usr/bin/lilypond")
            else:
                logger.info(f"Using LilyPond at: {lilypond_path}")
        except Exception as e:
            logger.warning(f"Could not configure LilyPond: {str(e)}")
    
    def generate_sheet_music(self, midi_path: str, task_id: str, title: str = "Piano Arrangement") -> Tuple[bool, Dict, str]:
        """
        Generate piano sheet music from a MIDI file.
        
        Args:
            midi_path: Path to the MIDI file
            task_id: Unique identifier for the task
            title: Title for the sheet music
            
        Returns:
            Tuple containing:
                - Success status (bool)
                - Dictionary of sheet music data
                - Path to the generated PDF file
        """
        if not os.path.exists(midi_path):
            logger.error(f"MIDI file does not exist: {midi_path}")
            return False, {"error": "MIDI file not found"}, ""
        
        pdf_path = os.path.join(self.output_dir, f"{task_id}.pdf")
        
        try:
            logger.info(f"Generating sheet music from MIDI: {midi_path}")
            
            # Load the MIDI file with music21
            midi_score = converter.parse(midi_path)
            
            # Create a piano score
            piano_score = self._create_piano_score(midi_score, title)
            
            # Write to PDF using LilyPond
            try:
                # First try to write directly to PDF
                piano_score.write(fmt='lily.pdf', fp=pdf_path)
            except Exception as e:
                logger.warning(f"Direct PDF generation failed: {str(e)}")
                
                # If direct PDF generation fails, try the two-step process
                lily_path = os.path.join(self.output_dir, f"{task_id}.ly")
                piano_score.write(fmt='lily', fp=lily_path)
                
                # Run LilyPond manually
                import subprocess
                cmd = ['/usr/bin/lilypond', '--pdf', '-o', os.path.splitext(pdf_path)[0], lily_path]
                subprocess.run(cmd, check=True)
            
            if os.path.exists(pdf_path):
                logger.info(f"Successfully generated sheet music: {pdf_path}")
                
                # Extract basic information
                sheet_music_info = {
                    "title": title,
                    "format": "PDF",
                    "path": pdf_path,
                    "measures": len(piano_score.getElementsByClass('Measure')),
                    "duration": piano_score.duration.quarterLength
                }
                
                return True, sheet_music_info, pdf_path
            else:
                logger.error(f"PDF file was not generated: {pdf_path}")
                return False, {"error": "PDF file was not generated"}, ""
                
        except Exception as e:
            logger.error(f"Error generating sheet music: {str(e)}")
            return False, {"error": str(e)}, ""
    
    def _create_piano_score(self, midi_score: stream.Score, title: str) -> stream.Score:
        """
        Create a piano score from a MIDI score.
        
        Args:
            midi_score: music21 Score object from MIDI
            title: Title for the sheet music
            
        Returns:
            music21 Score object formatted for piano
        """
        # Create a new score
        piano_score = stream.Score()
        
        # Add metadata
        piano_score.metadata = metadata.Metadata()
        piano_score.metadata.title = title
        
        # Extract time signature, key signature, and tempo from the original score
        time_sig = meter.TimeSignature('4/4')  # Default
        key_sig = key.Key('C')  # Default
        tempo_mark = tempo.MetronomeMark(number=120)  # Default
        
        for element in midi_score.flat:
            if isinstance(element, meter.TimeSignature):
                time_sig = element
            elif isinstance(element, key.KeySignature):
                key_sig = element
            elif isinstance(element, tempo.MetronomeMark):
                tempo_mark = element
        
        # Create right hand (treble) and left hand (bass) parts
        right_hand = stream.Part()
        left_hand = stream.Part()
        
        # Add clefs
        right_hand.append(clef.TrebleClef())
        left_hand.append(clef.BassClef())
        
        # Add time signature, key signature, and tempo
        right_hand.append(time_sig)
        left_hand.append(time_sig)
        right_hand.append(key_sig)
        left_hand.append(key_sig)
        right_hand.append(tempo_mark)
        
        # Separate notes into right and left hand
        # For simplicity, we'll use a pitch threshold (middle C = 60)
        # Notes above middle C go to right hand, notes below go to left hand
        pitch_threshold = 60
        
        # Get all notes and chords
        notes_and_chords = midi_score.flat.notesAndRests
        
        # Group by offset (start time)
        offset_dict = {}
        for element in notes_and_chords:
            offset = element.offset
            if offset not in offset_dict:
                offset_dict[offset] = []
            offset_dict[offset].append(element)
        
        # Process each offset group
        for offset, elements in sorted(offset_dict.items()):
            right_hand_elements = []
            left_hand_elements = []
            
            for element in elements:
                if element.isRest:
                    # Add rests to both hands
                    right_hand_elements.append(element)
                    left_hand_elements.append(element)
                elif element.isNote:
                    # Assign notes based on pitch
                    if element.pitch.midi >= pitch_threshold:
                        right_hand_elements.append(element)
                    else:
                        left_hand_elements.append(element)
                elif element.isChord:
                    # Split chord between hands if it spans the threshold
                    right_notes = []
                    left_notes = []
                    
                    for pitch in element.pitches:
                        if pitch.midi >= pitch_threshold:
                            right_notes.append(pitch)
                        else:
                            left_notes.append(pitch)
                    
                    if right_notes:
                        if len(right_notes) == 1:
                            n = note.Note(right_notes[0])
                            n.duration = element.duration
                            right_hand_elements.append(n)
                        else:
                            c = chord.Chord(right_notes)
                            c.duration = element.duration
                            right_hand_elements.append(c)
                    
                    if left_notes:
                        if len(left_notes) == 1:
                            n = note.Note(left_notes[0])
                            n.duration = element.duration
                            left_hand_elements.append(n)
                        else:
                            c = chord.Chord(left_notes)
                            c.duration = element.duration
                            left_hand_elements.append(c)
            
            # Add elements to the respective hands
            for element in right_hand_elements:
                right_hand.insert(offset, element)
            
            for element in left_hand_elements:
                left_hand.insert(offset, element)
        
        # Add the parts to the score
        piano_score.append(right_hand)
        piano_score.append(left_hand)
        
        # Make the score more readable for beginners
        self._simplify_for_beginners(piano_score)
        
        return piano_score
    
    def _simplify_for_beginners(self, score: stream.Score) -> None:
        """
        Simplify the score to make it more suitable for beginner to intermediate players.
        
        Args:
            score: music21 Score object to simplify
        """
        # Simplify complex rhythms
        for part in score.parts:
            for measure in part.getElementsByClass('Measure'):
                for note_or_chord in measure.notesAndRests:
                    # Simplify very short durations (32nd notes and shorter)
                    if note_or_chord.duration.quarterLength < 0.125:
                        note_or_chord.duration.quarterLength = 0.125  # 32nd note
        
        # Add fingering suggestions (simplified approach)
        # This would require more complex logic for proper fingering
        
        # Add dynamics (simplified)
        # This would require more complex analysis for proper dynamics
        
        # Add phrase markings (simplified)
        # This would require more complex analysis for proper phrasing


# Example usage
if __name__ == "__main__":
    # This code will only run if the file is executed directly
    generator = SheetMusicGenerator()
    
    # Example with a test file
    test_file = "path/to/test/midi.mid"  # Replace with an actual file path for testing
    
    if os.path.exists(test_file):
        # Generate sheet music
        success, sheet_info, pdf_path = generator.generate_sheet_music(test_file, "test_task", "My Piano Arrangement")
        if success:
            print(f"Sheet music generated at: {pdf_path}")
            print(f"Sheet info: {sheet_info}")
        else:
            print(f"Sheet music generation failed: {sheet_info}")
    else:
        print(f"Test file not found: {test_file}")
