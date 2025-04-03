# Piano Chorus Creator Backend

This repository contains the backend implementation for the Piano Chorus Creator application, which generates piano sheet music from YouTube links or audio files.

## Features

- Extract audio from YouTube videos
- Process uploaded audio files
- Transcribe audio to MIDI
- Extract the main melody/chorus
- Generate beginner-friendly piano sheet music
- Provide PDF output

## Architecture

The backend is built with a modular architecture consisting of the following components:

1. **YouTube Downloader**: Downloads audio from YouTube videos using yt-dlp
2. **Audio Processor**: Processes audio files using librosa
3. **Music Transcriber**: Transcribes audio to MIDI using Basic Pitch
4. **Melody Extractor**: Extracts the main melody and generates accompaniment
5. **Sheet Music Generator**: Creates piano sheet music using music21 and LilyPond
6. **API**: FastAPI endpoints that connect all components

## Requirements

- Python 3.10+
- LilyPond
- FFmpeg
- Various Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/piano-chorus-creator-backend.git
cd piano-chorus-creator-backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install -y lilypond ffmpeg
```

## Usage

### Running the server locally

```bash
python main.py
```

The server will start on http://localhost:8000

### API Endpoints

- `GET /`: Check if the API is running
- `POST /api/youtube`: Process a YouTube URL
- `POST /api/audio`: Process an audio file
- `GET /api/status/{task_id}`: Check the status of a task
- `GET /api/download/{task_id}`: Download the generated sheet music

## Integration with Frontend

The backend is designed to work with the Piano Chorus Creator frontend available at:
https://github.com/UfrostJulien/piano-chorus-creator

The frontend is deployed at:
https://piano-chorus-creator.lovable.app/

To integrate with the frontend:

1. Deploy this backend service
2. Update the frontend API configuration to point to your deployed backend URL

## Deployment

The backend can be deployed to various platforms:

### Render

1. Create a new Web Service on Render
2. Connect to your GitHub repository
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `python main.py`
5. Add environment variables if needed

### Heroku

1. Create a new app on Heroku
2. Connect to your GitHub repository
3. Add the Python buildpack
4. Add the Apt buildpack for LilyPond and FFmpeg
5. Create an `Aptfile` with:
```
lilypond
ffmpeg
```

## License

MIT
