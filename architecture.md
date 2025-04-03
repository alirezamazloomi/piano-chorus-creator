# Piano Chorus Creator - Backend Architecture

## Overview

The Piano Chorus Creator backend is designed to process YouTube links or audio files, extract the main melody/chorus, and generate piano sheet music in PDF format. The architecture follows a modular approach to handle different stages of the audio processing pipeline.

## Technology Stack

Based on our research, we'll use the following technologies:

1. **Programming Language**: Python 3.10+
2. **Web Framework**: FastAPI (for RESTful API endpoints)
3. **Audio Processing**:
   - yt-dlp: For downloading audio from YouTube links
   - librosa: For audio processing and feature extraction
4. **Music Transcription**:
   - Omnizart: For automatic music transcription and melody extraction
5. **Sheet Music Generation**:
   - music21: For music notation and manipulation
   - LilyPond: For high-quality sheet music rendering to PDF
6. **Deployment**:
   - Docker: For containerization
   - Render: For cloud deployment

## System Architecture

The backend will follow a pipeline architecture with the following components:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Input     │    │   Audio     │    │   Melody    │    │   Sheet     │    │   Output    │
│  Handler    │───▶│  Processor  │───▶│  Extractor  │───▶│   Music     │───▶│  Generator  │
│             │    │             │    │             │    │  Generator  │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### 1. Input Handler

Responsible for receiving and validating input from the frontend:
- YouTube URL validation and processing
- Audio file upload handling and validation

### 2. Audio Processor

Handles the extraction and preprocessing of audio:
- YouTube audio extraction (using yt-dlp)
- Audio file format conversion
- Audio normalization and preprocessing

### 3. Melody Extractor

Analyzes the audio to identify and extract the main melody/chorus:
- Uses Omnizart for music transcription
- Identifies the most prominent/repeated melodic sections
- Extracts the main melody and basic chord structure

### 4. Sheet Music Generator

Converts the extracted melody into piano sheet music:
- Uses music21 to create music notation
- Arranges the melody for piano with both treble and bass clefs
- Adds basic chord accompaniment
- Formats the sheet music for beginner to intermediate players

### 5. Output Generator

Creates the final output and delivers it to the frontend:
- Generates PDF using LilyPond
- Provides download links
- Handles cleanup of temporary files

## API Endpoints

The backend will expose the following RESTful API endpoints:

### 1. YouTube Processing

```
POST /api/youtube
```
- **Description**: Process a YouTube URL to generate piano sheet music
- **Request Body**:
  ```json
  {
    "url": "https://www.youtube.com/watch?v=..."
  }
  ```
- **Response**:
  ```json
  {
    "task_id": "unique-task-id",
    "status": "processing"
  }
  ```

### 2. Audio File Processing

```
POST /api/audio
```
- **Description**: Process an uploaded audio file to generate piano sheet music
- **Request Body**: Multipart form data with audio file
- **Response**:
  ```json
  {
    "task_id": "unique-task-id",
    "status": "processing"
  }
  ```

### 3. Task Status

```
GET /api/status/{task_id}
```
- **Description**: Check the status of a processing task
- **Response**:
  ```json
  {
    "task_id": "unique-task-id",
    "status": "completed|processing|failed",
    "progress": 75,
    "message": "Optional status message"
  }
  ```

### 4. Download Sheet Music

```
GET /api/download/{task_id}
```
- **Description**: Download the generated sheet music PDF
- **Response**: PDF file

## Data Flow

1. User submits a YouTube URL or uploads an audio file through the frontend
2. Backend validates the input and creates a processing task
3. For YouTube URLs, the backend downloads the audio using yt-dlp
4. Audio is preprocessed using librosa
5. Omnizart analyzes the audio to identify and extract the main melody/chorus
6. music21 converts the extracted melody into music notation
7. LilyPond renders the notation as a high-quality PDF
8. The PDF is made available for download through the API
9. Frontend displays the sheet music or provides a download link

## Error Handling

The backend will implement comprehensive error handling:
- Input validation errors (invalid YouTube URLs, unsupported audio formats)
- Processing errors (failed downloads, transcription failures)
- System errors (out of memory, disk space issues)

All errors will be logged and appropriate error messages will be returned to the frontend.

## Asynchronous Processing

Since audio processing and transcription can be time-consuming, the backend will implement asynchronous processing:
- Tasks will be processed in the background
- The frontend can poll for status updates
- Completed tasks will be stored temporarily for download

## Security Considerations

- Input validation to prevent malicious URLs or files
- Rate limiting to prevent abuse
- Temporary file cleanup to manage disk space
- Secure file handling for uploads and downloads

## Deployment Strategy

The backend will be containerized using Docker for easy deployment:
- All dependencies will be included in the Docker image
- Configuration will be managed through environment variables
- The service will be deployed to Render or a similar cloud platform

## Scaling Considerations

- Horizontal scaling for handling multiple concurrent requests
- Queue system for managing processing tasks
- Caching of results to improve performance for popular songs
