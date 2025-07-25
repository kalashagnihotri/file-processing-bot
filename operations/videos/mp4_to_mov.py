try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
import os

def convert_mp4_to_mov(input_path, output_path):
    try:
        if not MOVIEPY_AVAILABLE:
            return "Error: Video conversion not available. MoviePy library not properly installed."
        
        video = VideoFileClip(input_path)
        video.write_videofile(output_path, codec='libx264')
        video.close()
        return f"Converted MP4 to MOV: {output_path}"
    except Exception as e:
        return f"Error converting MP4 to MOV: {e}"