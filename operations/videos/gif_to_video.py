from moviepy.editor import VideoFileClip
import os

def convert_gif_to_mp4(input_path, output_path):
    """
    Convert GIF to MP4 video format.
    Uses MoviePy with fallback error handling.
    
    Args:
        input_path (str): Path to input GIF file
        output_path (str): Path for output MP4 file
        
    Returns:
        str: Success message or error description
    """
    try:
        # Load GIF as video clip
        video = VideoFileClip(input_path)
        
        # Write to MP4 with optimized settings for GIF conversion
        video.write_videofile(
            output_path, 
            codec='libx264',
            fps=video.fps,
            audio=False,  # GIFs don't have audio
            verbose=False,
            logger=None
        )
        
        video.close()
        return f"Successfully converted GIF to MP4: {os.path.basename(output_path)}"
        
    except Exception as e:
        return f"Error converting GIF to MP4: {str(e)}"

def convert_gif_to_webm(input_path, output_path):
    """
    Convert GIF to WebM video format.
    Uses MoviePy with optimized settings for web playback.
    
    Args:
        input_path (str): Path to input GIF file
        output_path (str): Path for output WebM file
        
    Returns:
        str: Success message or error description
    """
    try:
        # Load GIF as video clip
        video = VideoFileClip(input_path)
        
        # Write to WebM with optimized settings
        video.write_videofile(
            output_path, 
            codec='libvpx-vp9',
            fps=video.fps,
            audio=False,  # GIFs don't have audio
            verbose=False,
            logger=None
        )
        
        video.close()
        return f"Successfully converted GIF to WebM: {os.path.basename(output_path)}"
        
    except Exception as e:
        return f"Error converting GIF to WebM: {str(e)}"
