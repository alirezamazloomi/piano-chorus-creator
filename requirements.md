# Piano Chorus Creator - Backend Requirements

## Overview
The Piano Chorus Creator is a web application that allows users to generate simple piano sheet music from YouTube links or audio files. The application focuses on extracting the main recognizable part or chorus of a song and converting it into piano sheet music suitable for beginner to intermediate players.

## Frontend Analysis
The frontend is already developed using Lovable and is deployed at https://piano-chorus-creator.lovable.app/. The frontend provides:
- A simple interface for users to input YouTube URLs or upload audio files
- Tabs to switch between YouTube link and audio file input methods
- A "Generate" button to initiate the sheet music generation process

## Backend Requirements

### Core Functionality
1. **YouTube Link Processing**
   - Accept YouTube URLs from the frontend
   - Download and extract audio from YouTube videos
   - Handle various YouTube URL formats

2. **Audio File Processing**
   - Accept audio file uploads from the frontend
   - Support common audio formats (MP3, WAV, etc.)
   - Process and prepare audio for analysis

3. **Main Melody/Chorus Extraction**
   - Analyze audio to identify the main recognizable part or chorus
   - Extract the most prominent melodic line
   - Filter out background instruments and noise

4. **Music Transcription**
   - Convert the extracted melody into musical notation
   - Identify notes, rhythm, and key signature
   - Determine appropriate tempo

5. **Sheet Music Generation**
   - Create traditional music notation with both treble and bass clefs
   - Include melody with basic chord accompaniment
   - Format sheet music for beginner to intermediate piano players
   - Generate PDF output

6. **API Endpoints**
   - `/api/youtube` - Process YouTube links
   - `/api/audio` - Process audio file uploads
   - `/api/status` - Check processing status
   - `/api/download` - Download generated sheet music PDF

### Technical Requirements
1. **Performance**
   - Efficient audio processing to minimize wait times
   - Asynchronous processing for longer tasks

2. **Scalability**
   - Handle multiple concurrent requests
   - Queue system for processing tasks

3. **Error Handling**
   - Graceful handling of invalid YouTube links
   - Proper error messages for unsupported audio formats
   - Recovery mechanisms for failed processing

4. **Security**
   - Validate and sanitize all inputs
   - Secure file handling for uploads and downloads
   - Rate limiting to prevent abuse

## Implementation Considerations
- Backend technology: To be determined based on available libraries for audio processing and music transcription
- Deployment: Independent deployment or using user's Render and GitHub credentials
- Integration: RESTful API endpoints for frontend communication
