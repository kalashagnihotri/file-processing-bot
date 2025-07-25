import os
import tempfile
import time
from typing import Optional

class TempFileManager:
    """Manages temporary files for the bot operations"""
    
    def __init__(self, base_dir: str = "temp"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
    
    def create_temp_file(self, extension: str = "", prefix: str = "bot_") -> str:
        """Create a temporary file and return its path"""
        timestamp = str(int(time.time()))
        filename = f"{prefix}{timestamp}{extension}"
        return os.path.join(self.base_dir, filename)
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Remove temporary files older than max_age_hours"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for filename in os.listdir(self.base_dir):
            file_path = os.path.join(self.base_dir, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getctime(file_path)
                if file_age > max_age_seconds:
                    try:
                        os.remove(file_path)
                        print(f"Cleaned up old temp file: {filename}")
                    except Exception as e:
                        print(f"Error cleaning up {filename}: {e}")
    
    def get_output_filename(self, original_filename: str, operation: str) -> str:
        """Generate output filename based on operation"""
        name, ext = os.path.splitext(original_filename)
        timestamp = str(int(time.time()))
        
        # Define output extensions based on operation
        operation_extensions = {
            'convert_jpg_to_png': '.png',
            'convert_png_to_jpg': '.jpg',
            'convert_jpg_to_webp': '.webp',
            'convert_webp_to_jpg': '.jpg',
            'convert_svg_to_png': '.png',
            'compress_image': ext,
            'convert_mp4_to_mov': '.mov',
            'convert_mov_to_mp4': '.mp4',
            'convert_ts_to_mp4': '.mp4',
            'compress_video': ext,
            'compress_pdf': '.pdf',
            'merge_pdfs': '.pdf',
            'convert_pdf_to_images': '.zip',  # Will contain multiple images
            'convert_image_to_pdf': '.pdf',
        }
        
        output_ext = operation_extensions.get(operation, ext)
        return f"{name}_{operation}_{timestamp}{output_ext}"

# Global temp file manager instance
temp_manager = TempFileManager()
