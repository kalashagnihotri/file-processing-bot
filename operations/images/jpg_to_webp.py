from PIL import Image
import os

def convert_jpg_to_webp(input_path, output_path):
    try:
        img = Image.open(input_path).convert("RGB")
        img.save(output_path, "WEBP", quality=95)
        return f"Converted JPG to WebP: {output_path}"
    except Exception as e:
        return f"Error converting JPG to WebP: {e}"
