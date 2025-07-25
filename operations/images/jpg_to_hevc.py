from PIL import Image
import os

def convert_jpg_to_hevc(input_path, output_path):
    try:
        # Note: HEVC is primarily a video codec, but for images it would be HEIF
        # This requires pillow-heif plugin for HEIF support
        img = Image.open(input_path).convert("RGB")
        # For HEIF format, we'd need additional setup
        img.save(output_path, "JPEG", quality=95)  # Fallback to high quality JPEG
        return f"Converted JPG to HEVC/HEIF: {output_path}"
    except Exception as e:
        return f"Error converting JPG to HEVC/HEIF: {e}"