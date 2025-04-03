"""
YouTube Downloader Module for Piano Chorus Creator

This module handles downloading audio from YouTube videos using yt-dlp.
"""

import os
import logging
import tempfile
from typing import Dict, Optional, Tuple
import yt_dlp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """
    Class for downloading audio from YouTube videos.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the YouTube downloader.
        
        Args:
            output_dir: Directory to save downloaded audio files.
                        If None, a temporary directory will be used.
        """
        self.output_dir = output_dir or tempfile.mkdtemp()
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"YouTube downloader initialized with output directory: {self.output_dir}")
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if the URL is a valid YouTube URL.
        
        Args:
            url: YouTube URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        extractors = yt_dlp.extractor.gen_extractors()
        for e in extractors:
            if e.suitable(url) and e.IE_NAME != 'generic':
                return True
        return False
    
    def download_audio(self, url: str, task_id: str) -> Tuple[bool, str, Dict]:
        """
        Download audio from a YouTube video.
        
        Args:
            url: YouTube URL to download from
            task_id: Unique identifier for the task
            
        Returns:
            Tuple containing:
                - Success status (bool)
                - Path to downloaded audio file (str)
                - Additional info about the download (Dict)
        """
        if not self.validate_url(url):
            logger.error(f"Invalid YouTube URL: {url}")
            return False, "", {"error": "Invalid YouTube URL"}
        
        output_file = os.path.join(self.output_dir, f"{task_id}.mp3")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_file.replace('.mp3', ''),  # yt-dlp adds extension automatically
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': False,
        }
        
        try:
            logger.info(f"Downloading audio from {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
            if os.path.exists(output_file):
                logger.info(f"Successfully downloaded audio to {output_file}")
                return True, output_file, {
                    "title": info.get('title', ''),
                    "duration": info.get('duration', 0),
                    "uploader": info.get('uploader', ''),
                }
            else:
                logger.error(f"Download completed but file not found: {output_file}")
                return False, "", {"error": "Download completed but file not found"}
                
        except Exception as e:
            logger.error(f"Error downloading from YouTube: {str(e)}")
            return False, "", {"error": str(e)}
    
    def get_video_info(self, url: str) -> Dict:
        """
        Get information about a YouTube video without downloading.
        
        Args:
            url: YouTube URL
            
        Returns:
            Dict containing video information
        """
        if not self.validate_url(url):
            logger.error(f"Invalid YouTube URL: {url}")
            return {"error": "Invalid YouTube URL"}
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
            return {
                "title": info.get('title', ''),
                "duration": info.get('duration', 0),
                "uploader": info.get('uploader', ''),
                "thumbnail": info.get('thumbnail', ''),
            }
                
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return {"error": str(e)}


# Example usage
if __name__ == "__main__":
    # This code will only run if the file is executed directly
    downloader = YouTubeDownloader()
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Example URL
    
    # Get video info
    info = downloader.get_video_info(test_url)
    print(f"Video info: {info}")
    
    # Download audio
    success, file_path, download_info = downloader.download_audio(test_url, "test_task")
    if success:
        print(f"Downloaded to: {file_path}")
        print(f"Download info: {download_info}")
    else:
        print(f"Download failed: {download_info}")
