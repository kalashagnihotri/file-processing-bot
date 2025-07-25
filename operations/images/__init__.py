# Image processing operations
from .jpg_to_png import convert_jpg_to_png
from .png_to_jpg import convert_png_to_jpg
from .jpg_to_webp import convert_jpg_to_webp
from .webp_to_jpg import convert_webp_to_jpg
from .compress_image import compress_image
from .hevc_to_jpg import convert_hevc_to_jpg
from .jpg_to_hevc import convert_jpg_to_hevc

# SVG support with fallback handling
try:
    from .svg_to_png import convert_svg_to_png
    SVG_AVAILABLE = True
except ImportError:
    SVG_AVAILABLE = False
    def convert_svg_to_png(input_path, output_path):
        return "Error: SVG conversion not available. Please install cairosvg or svglib."

__all__ = [
    'convert_jpg_to_png',
    'convert_png_to_jpg', 
    'convert_jpg_to_webp',
    'convert_webp_to_jpg',
    'convert_svg_to_png',
    'compress_image',
    'convert_hevc_to_jpg',
    'convert_jpg_to_hevc'
]
