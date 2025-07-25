import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')

# File size limits (in MB)
MAX_FILE_SIZE_MB = 50

# Supported file types
SUPPORTED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
SUPPORTED_PDF_EXTENSIONS = ['.pdf']
SUPPORTED_VIDEO_EXTENSIONS = ['.mp4', '.mov', '.mkv', '.webm', '.ts', '.gif']

# SVG support will be checked dynamically in the bot

# Conversion quality settings
IMAGE_QUALITY = {
    'webp': 95,
    'jpeg': 95,
    'compression': 60
}

VIDEO_QUALITY = {
    'bitrate': '1000k',
    'codec': 'libx264'
}

# Temporary file settings
TEMP_DIR = 'temp'
CLEANUP_INTERVAL_HOURS = 24

# Error messages
ERROR_MESSAGES = {
    'unsupported_file': "Unsupported file type. Please send an image, PDF, or video file.",
    'file_too_large': f"File too large. Maximum size allowed is {MAX_FILE_SIZE_MB}MB.",
    'download_failed': "Failed to download the file. Please try again.",
    'conversion_failed': "Conversion failed. Please check the file and try again.",
    'invalid_operation': "Invalid operation selected.",
}

# Success messages
SUCCESS_MESSAGES = {
    'file_received': "File received successfully! Choose an operation:",
    'conversion_complete': "Conversion completed successfully!",
    'file_processed': "File processed and ready for download.",
}
