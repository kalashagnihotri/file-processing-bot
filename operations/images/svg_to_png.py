import cairosvg

def convert_svg_to_png(input_path, output_path):
    try:
        cairosvg.svg2png(url=input_path, write_to=output_path)
        return f"Converted SVG to PNG: {output_path}"
    except Exception as e:
        return f"Error converting SVG to PNG: {e}"
