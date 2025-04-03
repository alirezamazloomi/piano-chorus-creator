"""
API Module for Piano Chorus Creator

This module implements the FastAPI endpoints that connect all components
of the Piano Chorus Creator backend.
"""

import os
import uuid
import logging
import tempfile
import shutil
from typing import Dict, List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import uvicorn

from app.cors import setup_cors
from app.youtube_downloader import YouTubeDownloader
from app.audio_processor import AudioProcessor
from app.music_transcriber import MusicTranscriber
from app.melody_extractor import MelodyExtractor
from app.sheet_music_generator import SheetMusicGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Piano Chorus Creator API",
    description="API for generating piano sheet music from YouTube links or audio files",
    version="1.0.0"
)

# Setup CORS for frontend integration
setup_cors(app)

# Create a directory for storing files
UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "piano-chorus-creator")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize components
youtube_downloader = YouTubeDownloader(output_dir=UPLOAD_DIR)
audio_processor = AudioProcessor(output_dir=UPLOAD_DIR)
music_transcriber = MusicTranscriber(output_dir=UPLOAD_DIR)
melody_extractor = MelodyExtractor(output_dir=UPLOAD_DIR)
sheet_music_generator = SheetMusicGenerator(output_dir=UPLOAD_DIR)

# In-memory task storage
tasks = {}

# Models
class YouTubeRequest(BaseModel):
    url: HttpUrl
    title: Optional[str] = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: Optional[str] = None

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: Optional[int] = None
    message: Optional[str] = None
    download_url: Optional[str] = None

# Helper functions
def process_youtube_task(task_id: str, url: str, title: Optional[str] = None):
    """
    Process a YouTube URL to generate sheet music.
    
    Args:
        task_id: Unique task identifier
        url: YouTube URL
        title: Optional title for the sheet music
    """
    try:
        tasks[task_id]["status"] = "downloading"
        tasks[task_id]["progress"] = 10
        
        # Download audio from YouTube
        success, audio_path, download_info = youtube_downloader.download_audio(url, task_id)
        if not success:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["message"] = f"Failed to download audio: {download_info.get('error', 'Unknown error')}"
            return
        
        # Use video title if no title provided
        if not title:
            title = download_info.get("title", "Piano Arrangement")
        
        tasks[task_id]["progress"] = 30
        tasks[task_id]["status"] = "processing"
        
        # Process the audio
        success, processed_audio_path, process_info = audio_processor.process_audio(audio_path, task_id)
        if not success:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["message"] = f"Failed to process audio: {process_info.get('error', 'Unknown error')}"
            return
        
        tasks[task_id]["progress"] = 50
        tasks[task_id]["status"] = "transcribing"
        
        # Transcribe the audio to MIDI
        success, midi_info, midi_path = music_transcriber.transcribe_audio(processed_audio_path, task_id)
        if not success:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["message"] = f"Failed to transcribe audio: {midi_info.get('error', 'Unknown error')}"
            return
        
        tasks[task_id]["progress"] = 70
        tasks[task_id]["status"] = "extracting_melody"
        
        # Extract the main melody with accompaniment
        success, arrangement_info, arrangement_midi_path = melody_extractor.extract_with_accompaniment(midi_path, task_id)
        if not success:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["message"] = f"Failed to extract melody: {arrangement_info.get('error', 'Unknown error')}"
            return
        
        tasks[task_id]["progress"] = 85
        tasks[task_id]["status"] = "generating_sheet_music"
        
        # Generate sheet music
        success, sheet_info, pdf_path = sheet_music_generator.generate_sheet_music(arrangement_midi_path, task_id, title)
        if not success:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["message"] = f"Failed to generate sheet music: {sheet_info.get('error', 'Unknown error')}"
            return
        
        tasks[task_id]["progress"] = 100
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["message"] = "Sheet music generated successfully"
        tasks[task_id]["pdf_path"] = pdf_path
        tasks[task_id]["download_url"] = f"/api/download/{task_id}"
        
    except Exception as e:
        logger.error(f"Error processing YouTube task: {str(e)}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["message"] = f"An unexpected error occurred: {str(e)}"

def process_audio_task(task_id: str, audio_path: str, title: Optional[str] = None):
    """
    Process an audio file to generate sheet music.
    
    Args:
        task_id: Unique task identifier
        audio_path: Path to the audio file
        title: Optional title for the sheet music
    """
    try:
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 20
        
        # Process the audio
        success, processed_audio_path, process_info = audio_processor.process_audio(audio_path, task_id)
        if not success:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["message"] = f"Failed to process audio: {process_info.get('error', 'Unknown error')}"
            return
        
        tasks[task_id]["progress"] = 40
        tasks[task_id]["status"] = "transcribing"
        
        # Transcribe the audio to MIDI
        success, midi_info, midi_path = music_transcriber.transcribe_audio(processed_audio_path, task_id)
        if not success:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["message"] = f"Failed to transcribe audio: {midi_info.get('error', 'Unknown error')}"
            return
        
        tasks[task_id]["progress"] = 60
        tasks[task_id]["status"] = "extracting_melody"
        
        # Extract the main melody with accompaniment
        success, arrangement_info, arrangement_midi_path = melody_extractor.extract_with_accompaniment(midi_path, task_id)
        if not success:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["message"] = f"Failed to extract melody: {arrangement_info.get('error', 'Unknown error')}"
            return
        
        tasks[task_id]["progress"] = 80
        tasks[task_id]["status"] = "generating_sheet_music"
        
        # Generate sheet music
        if not title:
            title = "Piano Arrangement"
            
        success, sheet_info, pdf_path = sheet_music_generator.generate_sheet_music(arrangement_midi_path, task_id, title)
        if not success:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["message"] = f"Failed to generate sheet music: {sheet_info.get('error', 'Unknown error')}"
            return
        
        tasks[task_id]["progress"] = 100
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["message"] = "Sheet music generated successfully"
        tasks[task_id]["pdf_path"] = pdf_path
        tasks[task_id]["download_url"] = f"/api/download/{task_id}"
        
    except Exception as e:
        logger.error(f"Error processing audio task: {str(e)}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["message"] = f"An unexpected error occurred: {str(e)}"

def cleanup_task_files(task_id: str):
    """
    Clean up files associated with a task.
    
    Args:
        task_id: Task identifier
    """
    try:
        # Keep the PDF file but remove other temporary files
        for filename in os.listdir(UPLOAD_DIR):
            if task_id in filename and not filename.endswith(".pdf"):
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    except Exception as e:
        logger.error(f"Error cleaning up task files: {str(e)}")

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint to check if the API is running."""
    return {"message": "Piano Chorus Creator API is running"}

@app.post("/api/youtube", response_model=TaskResponse)
async def process_youtube(request: YouTubeRequest, background_tasks: BackgroundTasks):
    """
    Process a YouTube URL to generate piano sheet music.
    
    Args:
        request: YouTube request containing URL and optional title
        background_tasks: FastAPI background tasks
        
    Returns:
        Task response with task ID and status
    """
    # Validate YouTube URL
    if not youtube_downloader.validate_url(request.url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    # Create a new task
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "queued",
        "progress": 0,
        "message": "Task queued for processing"
    }
    
    # Process the task in the background
    background_tasks.add_task(process_youtube_task, task_id, str(request.url), request.title)
    
    return TaskResponse(task_id=task_id, status="queued")

@app.post("/api/audio", response_model=TaskResponse)
async def process_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None)
):
    """
    Process an audio file to generate piano sheet music.
    
    Args:
        background_tasks: FastAPI background tasks
        file: Uploaded audio file
        title: Optional title for the sheet music
        
    Returns:
        Task response with task ID and status
    """
    # Create a new task
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "uploading",
        "progress": 0,
        "message": "Uploading audio file"
    }
    
    # Save the uploaded file
    file_path = os.path.join(UPLOAD_DIR, f"{task_id}_original{os.path.splitext(file.filename)[1]}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Error saving uploaded file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving uploaded file: {str(e)}")
    finally:
        file.file.close()
    
    # Validate audio file
    if not audio_processor.is_valid_audio_file(file_path):
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Invalid audio file format")
    
    tasks[task_id]["status"] = "queued"
    tasks[task_id]["progress"] = 10
    tasks[task_id]["message"] = "Task queued for processing"
    
    # Process the task in the background
    background_tasks.add_task(process_audio_task, task_id, file_path, title)
    
    return TaskResponse(task_id=task_id, status="queued")

@app.get("/api/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get the status of a task.
    
    Args:
        task_id: Task identifier
        
    Returns:
        Task status response
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    response = TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task.get("progress"),
        message=task.get("message")
    )
    
    if task["status"] == "completed":
        response.download_url = task["download_url"]
    
    return response

@app.get("/api/download/{task_id}")
async def download_sheet_music(task_id: str, background_tasks: BackgroundTasks):
    """
    Download the generated sheet music PDF.
    
    Args:
        task_id: Task identifier
        background_tasks: FastAPI background tasks
        
    Returns:
        PDF file response
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Sheet music not ready yet")
    
    if "pdf_path" not in task:
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    pdf_path = task["pdf_path"]
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    # Schedule cleanup of task files (except the PDF)
    background_tasks.add_task(cleanup_task_files, task_id)
    
    return FileResponse(
        path=pdf_path,
        filename=f"piano_arrangement_{task_id}.pdf",
        media_type="application/pdf"
    )

# Run the application
if __name__ == "__main__":
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)
