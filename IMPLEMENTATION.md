# Piano Chorus Creator - Implementation Details

This document provides detailed information about the implementation of the Piano Chorus Creator backend.

## Architecture Overview

The backend follows a modular architecture with the following components:

1. **Input Handling**: Processes YouTube URLs and audio file uploads
2. **Audio Processing**: Extracts and preprocesses audio
3. **Music Transcription**: Converts audio to MIDI
4. **Melody Extraction**: Identifies and extracts the main melody/chorus
5. **Sheet Music Generation**: Creates piano sheet music
6. **API Layer**: Provides endpoints for frontend interaction

## Component Details

### YouTube Downloader (`app/youtube_downloader.py`)

This component handles downloading audio from YouTube videos using the yt-dlp library.

**Key Features:**
- URL validation
- Audio extraction in MP3 format
- Video metadata retrieval
- Error handling for invalid URLs

**Implementation Notes:**
- Uses yt-dlp's post-processing to extract audio
- Configures audio quality to 192kbps for optimal transcription
- Stores downloaded files in a configurable output directory

### Audio Processor (`app/audio_processor.py`)

This component handles audio file processing using the librosa library.

**Key Features:**
- Audio file validation
- Format normalization
- Audio feature extraction
- Signal processing

**Implementation Notes:**
- Supports multiple audio formats (MP3, WAV, OGG, FLAC, M4A)
- Normalizes audio to ensure consistent volume levels
- Extracts spectral features for melody analysis
- Uses librosa for high-quality audio processing

### Music Transcriber (`app/music_transcriber.py`)

This component transcribes audio to MIDI using Spotify's Basic Pitch library.

**Key Features:**
- Audio to MIDI conversion
- Note detection with pitch and timing
- MIDI file generation
- Transcription metadata extraction

**Implementation Notes:**
- Uses Basic Pitch's neural network for accurate note detection
- Configures onset and frame thresholds for optimal transcription
- Extracts basic information from the MIDI for further processing
- Handles polyphonic audio with multiple instruments

### Melody Extractor (`app/melody_extractor.py`)

This component identifies and extracts the main melody or chorus from transcribed music.

**Key Features:**
- Main melody identification
- Chorus detection using pattern recognition
- Accompaniment generation
- Piano arrangement creation

**Implementation Notes:**
- Uses heuristics to identify the melody based on pitch and note density
- Implements pattern recognition to find repeated sections (chorus)
- Generates basic chord accompaniment for the left hand
- Creates a piano-friendly arrangement with separated hands

### Sheet Music Generator (`app/sheet_music_generator.py`)

This component generates piano sheet music using music21 and LilyPond.

**Key Features:**
- MIDI to sheet music conversion
- PDF generation
- Piano-specific notation
- Beginner-friendly simplification

**Implementation Notes:**
- Uses music21 for music theory operations
- Integrates with LilyPond for high-quality engraving
- Separates music into treble and bass clefs for piano
- Simplifies complex rhythms for beginner to intermediate players

### API Layer (`app/api.py`)

This component provides RESTful API endpoints using FastAPI.

**Key Features:**
- YouTube URL processing endpoint
- Audio file upload endpoint
- Task status checking
- Sheet music download
- Background task processing

**Implementation Notes:**
- Uses FastAPI for high-performance API handling
- Implements background tasks for long-running operations
- Provides detailed task status updates
- Handles file uploads and downloads
- Includes CORS configuration for frontend integration

## Data Flow

1. **Input**: YouTube URL or audio file upload
2. **Processing**: 
   - YouTube URL → Download audio → Process audio
   - Audio file → Process audio
3. **Transcription**: Audio → MIDI
4. **Melody Extraction**: Full MIDI → Melody + Accompaniment
5. **Sheet Music Generation**: Arrangement MIDI → PDF
6. **Output**: Sheet music PDF

## Dependencies

### Python Libraries
- yt-dlp: YouTube downloading
- librosa: Audio processing
- basic-pitch: Music transcription
- pretty_midi: MIDI manipulation
- music21: Music theory and notation
- fastapi: API framework
- uvicorn: ASGI server

### System Dependencies
- LilyPond: Sheet music engraving
- FFmpeg: Audio processing

## Performance Considerations

- Audio processing and transcription are computationally intensive
- Background task processing prevents blocking API responses
- Temporary file storage with cleanup to manage disk space
- Task status updates to provide progress information to users

## Security Considerations

- Input validation for all user-provided data
- Temporary file storage with unique task IDs
- No persistent storage of user data
- CORS configuration to restrict access to authorized domains

## Future Improvements

- Improved melody detection using machine learning
- More sophisticated chord detection for better accompaniment
- User preferences for sheet music complexity
- Caching of previously processed YouTube videos
- Support for more input formats and sources
