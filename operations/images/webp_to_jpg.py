from PIL import Image
import os

def convert_webp_to_jpg(input_path, output_path):
    try:
        img = Image.open(input_path).convert("RGB")
        img.save(output_path, "JPEG")
        return f"Converted WebP to JPG: {output_path}"
    except Exception as e:
        return f"Error converting WebP to JPG: {e}"
