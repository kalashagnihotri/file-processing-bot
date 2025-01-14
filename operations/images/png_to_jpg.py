from PIL import Image
import os

def convert_png_to_jpg(input_path, output_path):
    try:
        img = Image.open(input_path).convert("RGB")
        img.save(output_path, "JPEG")
        return f"Converted PNG to JPG: {output_path}"
    except Exception as e:
        return f"Error converting PNG to JPG: {e}"
