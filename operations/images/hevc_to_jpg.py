from PIL import Image
import os

def convert_hevc_to_jpg(input_path, output_path):
    try:
        # Note: HEVC is primarily a video codec, but for images it would be HEIF
        # PIL with pillow-heif plugin can handle HEIF images
        img = Image.open(input_path).convert("RGB")
        img.save(output_path, "JPEG", quality=95)
        return f"Converted HEVC/HEIF to JPG: {output_path}"
    except Exception as e:
        return f"Error converting HEVC/HEIF to JPG: {e}"