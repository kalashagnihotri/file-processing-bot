from pdf2image import convert_from_path
import os

def convert_pdf_to_images(input_path, output_dir, format='PNG'):
    try:
        pages = convert_from_path(input_path)
        output_paths = []
        
        os.makedirs(output_dir, exist_ok=True)
        
        for i, page in enumerate(pages):
            output_path = os.path.join(output_dir, f"page_{i+1}.{format.lower()}")
            page.save(output_path, format)
            output_paths.append(output_path)
        
        return f"Converted PDF to {len(pages)} {format} images in: {output_dir}"
    except Exception as e:
        return f"Error converting PDF to images: {e}"