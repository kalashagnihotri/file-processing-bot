import os
import logging

try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except (ImportError, OSError) as e:
    # Handle both import errors and Cairo library missing errors
    CAIROSVG_AVAILABLE = False
    logging.warning(f"CairoSVG not available: {e}")

try:
    from PIL import Image
    from reportlab.graphics import renderPM
    from svglib.svglib import renderSVG
    ALTERNATIVE_SVG_AVAILABLE = True
except ImportError:
    ALTERNATIVE_SVG_AVAILABLE = False

try:
    import subprocess
    INKSCAPE_AVAILABLE = True
except ImportError:
    INKSCAPE_AVAILABLE = False

def convert_svg_to_png(input_path, output_path):
    """
    Convert SVG to PNG using multiple fallback methods.
    """
    try:
        # Method 1: Using cairosvg (preferred)
        if CAIROSVG_AVAILABLE:
            try:
                cairosvg.svg2png(url=input_path, write_to=output_path)
                return f"Converted SVG to PNG using CairoSVG: {output_path}"
            except Exception as e:
                logging.warning(f"CairoSVG failed: {e}, trying alternative method")
        
        # Method 2: Using svglib + reportlab
        if ALTERNATIVE_SVG_AVAILABLE:
            try:
                # Read SVG and convert to PNG
                drawing = renderSVG.renderSVG(input_path)
                renderPM.drawToFile(drawing, output_path, fmt='PNG')
                return f"Converted SVG to PNG using svglib: {output_path}"
            except Exception as e:
                logging.warning(f"svglib failed: {e}, trying Inkscape method")
        
        # Method 3: Using Inkscape command line (if available)
        if INKSCAPE_AVAILABLE:
            try:
                # Check if Inkscape is available in PATH
                result = subprocess.run(['inkscape', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Use Inkscape to convert
                    subprocess.run([
                        'inkscape', 
                        '--export-type=png',
                        f'--export-filename={output_path}',
                        input_path
                    ], check=True, timeout=30)
                    return f"Converted SVG to PNG using Inkscape: {output_path}"
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
                logging.warning(f"Inkscape method failed: {e}")
        
        # Method 4: Simple fallback using Pillow (very limited SVG support)
        try:
            from PIL import Image
            # This works for very simple SVGs only
            with Image.open(input_path) as img:
                img.save(output_path, 'PNG')
            return f"Converted SVG to PNG using Pillow (basic): {output_path}"
        except Exception as e:
            logging.warning(f"Pillow method failed: {e}")
        
        # If all methods fail
        return "Error: SVG conversion not available. Install CairoSVG (pip install cairosvg) or svglib (pip install svglib reportlab) or Inkscape application"
        
    except Exception as e:
        return f"Error converting SVG to PNG: {e}"
