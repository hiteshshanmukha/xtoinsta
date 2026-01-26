"""Configuration settings for X to Instagram Reel Converter."""

import os
from pathlib import Path

# Project directories
BASE_DIR = Path(__file__).resolve().parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
DOWNLOADS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Video settings
REEL_WIDTH = 1080
REEL_HEIGHT = 1920
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "aac"
VIDEO_PRESET = os.getenv("VIDEO_PRESET", "veryfast")  # Changed to "veryfast" for better Railway compatibility
VIDEO_FPS = 24  # Reduced from 30 to 24 for faster processing

# Text overlay settings
AVATAR_SIZE = 80
AVATAR_BORDER_WIDTH = 3
USERNAME_FONT_SIZE = 32
DISPLAY_NAME_FONT_SIZE = 24
CAPTION_FONT_SIZE = 26
METRICS_FONT_SIZE = 28
TIMESTAMP_FONT_SIZE = 22

# Caption settings
MAX_CAPTION_LENGTH = 150
CAPTION_MAX_WIDTH = 900
CAPTION_Y_POSITION = 600

# Footer settings
FOOTER_HEIGHT = 300
FOOTER_ALPHA = 180

# Processing settings
MAX_PROCESSING_TIMEOUT = int(os.getenv("MAX_PROCESSING_TIMEOUT", "900"))  # 15 minutes

# Flask settings
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# API settings
API_URL = os.getenv("API_URL", "http://127.0.0.1:5000")

# yt-dlp settings
YTDLP_FORMAT = "best[ext=mp4]"
YTDLP_RETRIES = 3
