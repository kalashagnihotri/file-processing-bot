from PIL import Image
import os

def convert_image_to_pdf(input_path, output_path):
    try:
        img = Image.open(input_path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img.save(output_path, "PDF", quality=95)
        return f"Converted image to PDF: {output_path}"
    except Exception as e:
        return f"Error converting image to PDF: {e}"

def convert_images_to_pdf(input_paths, output_path):
    try:
        images = []
        for path in input_paths:
            img = Image.open(path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images.append(img)
        
        if images:
            images[0].save(output_path, "PDF", save_all=True, append_images=images[1:], quality=95)
            return f"Converted {len(images)} images to PDF: {output_path}"
        else:
            return "No images provided"
    except Exception as e:
        return f"Error converting images to PDF: {e}"