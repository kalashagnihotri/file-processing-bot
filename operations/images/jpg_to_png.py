from PIL import Image
import os
import logging

logger = logging.getLogger(__name__)

def convert_jpg_to_png(input_path, output_path):
    """
    Convert JPG to PNG format with comprehensive error handling.
    
    Args:
        input_path (str): Path to input JPG file
        output_path (str): Path for output PNG file
        
    Returns:
        str: Success message or detailed error description
    """
    try:
        # Validate input file exists
        if not os.path.exists(input_path):
            return f"Error: Input file does not exist: {input_path}"
        
        # Validate input file size
        if os.path.getsize(input_path) == 0:
            return f"Error: Input file is empty: {input_path}"
        
        # Validate output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                return f"Error: Cannot create output directory: {e}"
        
        # Load and convert image
        try:
            img = Image.open(input_path)
        except Exception as e:
            return f"Error: Cannot open image file (invalid JPG?): {e}"
        
        # Convert to RGBA for PNG with transparency support
        try:
            img = img.convert("RGBA")
        except Exception as e:
            return f"Error: Cannot convert image format: {e}"
        
        # Save as PNG
        try:
            img.save(output_path, "PNG", optimize=True)
        except Exception as e:
            return f"Error: Cannot save PNG file: {e}"
        finally:
            img.close()
        
        # Verify output file was created successfully
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            return f"Error: Output file was not created successfully"
        
        logger.info(f"Successfully converted JPG to PNG: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
        return f"Successfully converted JPG to PNG: {os.path.basename(output_path)}"
        
    except MemoryError:
        return f"Error: Image too large to process (insufficient memory)"
    except PermissionError:
        return f"Error: Permission denied accessing files"
    except Exception as e:
        logger.error(f"Unexpected error in JPG to PNG conversion: {e}")
        return f"Error converting JPG to PNG: {str(e)}"
