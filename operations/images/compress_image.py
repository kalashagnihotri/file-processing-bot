from PIL import Image

def compress_image(input_path, output_path, quality=60):
    try:
        img = Image.open(input_path)
        img.save(output_path, optimize=True, quality=quality)
        return f"Compressed Image: {output_path} at quality {quality}"
    except Exception as e:
        return f"Error compressing image: {e}"
