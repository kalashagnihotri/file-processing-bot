from PIL import Image
import os

def convert_jpg_to_png(input_path, output_path):
    try:
        img = Image.open(input_path).convert("RGBA")
        img.save(output_path, "PNG")
        return f"Converted JPG to PNG: {output_path}"
    except Exception as e:
        return f"Error converting JPG to PNG: {e}"
