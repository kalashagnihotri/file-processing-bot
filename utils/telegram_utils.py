import requests
import os
from typing import Tuple, Optional

def download_telegram_file(bot, file_id: str, save_path: str) -> bool:
    """Download a file from Telegram and save it locally"""
    try:
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        
        response = requests.get(file_url)
        response.raise_for_status()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def get_file_info(message) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Extract file information from message"""
    file_id = None
    file_name = None
    file_size = None
    
    if message.content_type == 'document':
        file_id = message.document.file_id
        file_name = message.document.file_name
        file_size = message.document.file_size
    elif message.content_type == 'photo':
        # Get the largest photo
        file_id = message.photo[-1].file_id
        file_name = f"photo_{file_id[:10]}.jpg"
        file_size = message.photo[-1].file_size
    elif message.content_type == 'video':
        file_id = message.video.file_id
        file_name = f"video_{file_id[:10]}.mp4"
        file_size = message.video.file_size
    
    return file_id, file_name, file_size

def validate_file_size(file_size: int, max_size_mb: int = 50) -> bool:
    """Check if file size is within limits"""
    if file_size is None:
        return True  # Allow if size is unknown
    
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes

def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase"""
    return os.path.splitext(filename)[1].lower() if filename else ""
