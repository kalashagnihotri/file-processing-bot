from moviepy.editor import VideoFileClip
import os

def convert_mp4_to_gif(input_path, output_path):
    """
    Convert MP4 video to GIF format.
    Uses MoviePy with optimized settings for GIF creation.
    
    Args:
        input_path (str): Path to input MP4 file
        output_path (str): Path for output GIF file
        
    Returns:
        str: Success message or error description
    """
    try:
        # Load video clip
        video = VideoFileClip(input_path)
        
        # Optimize for GIF creation - reduce fps and resize if too large
        duration = video.duration
        original_fps = video.fps
        
        # Adjust fps for reasonable GIF size (max 15 fps for GIFs)
        target_fps = min(15, original_fps) if original_fps else 10
        
        # Resize if video is too large (max width 800px for reasonable GIF size)
        if video.w > 800:
            video = video.resize(width=800)
        
        # Limit duration for very long videos (max 10 seconds for reasonable file size)
        if duration > 10:
            video = video.subclip(0, 10)
        
        # Write to GIF with optimized settings
        video.write_gif(
            output_path,
            fps=target_fps,
            verbose=False,
            logger=None
        )
        
        video.close()
        return f"Successfully converted MP4 to GIF: {os.path.basename(output_path)}"
        
    except Exception as e:
        return f"Error converting MP4 to GIF: {str(e)}"

def convert_mov_to_gif(input_path, output_path):
    """
    Convert MOV video to GIF format.
    Uses MoviePy with optimized settings for GIF creation.
    
    Args:
        input_path (str): Path to input MOV file
        output_path (str): Path for output GIF file
        
    Returns:
        str: Success message or error description
    """
    try:
        # Load video clip
        video = VideoFileClip(input_path)
        
        # Optimize for GIF creation
        duration = video.duration
        original_fps = video.fps
        
        # Adjust fps for reasonable GIF size
        target_fps = min(15, original_fps) if original_fps else 10
        
        # Resize if video is too large
        if video.w > 800:
            video = video.resize(width=800)
        
        # Limit duration for very long videos
        if duration > 10:
            video = video.subclip(0, 10)
        
        # Write to GIF
        video.write_gif(
            output_path,
            fps=target_fps,
            verbose=False,
            logger=None
        )
        
        video.close()
        return f"Successfully converted MOV to GIF: {os.path.basename(output_path)}"
        
    except Exception as e:
        return f"Error converting MOV to GIF: {str(e)}"

def convert_webm_to_gif(input_path, output_path):
    """
    Convert WebM video to GIF format.
    Uses MoviePy with optimized settings for GIF creation.
    
    Args:
        input_path (str): Path to input WebM file
        output_path (str): Path for output GIF file
        
    Returns:
        str: Success message or error description
    """
    try:
        # Load video clip
        video = VideoFileClip(input_path)
        
        # Optimize for GIF creation
        duration = video.duration
        original_fps = video.fps
        
        # Adjust fps for reasonable GIF size
        target_fps = min(15, original_fps) if original_fps else 10
        
        # Resize if video is too large
        if video.w > 800:
            video = video.resize(width=800)
        
        # Limit duration for very long videos
        if duration > 10:
            video = video.subclip(0, 10)
        
        # Write to GIF
        video.write_gif(
            output_path,
            fps=target_fps,
            verbose=False,
            logger=None
        )
        
        video.close()
        return f"Successfully converted WebM to GIF: {os.path.basename(output_path)}"
        
    except Exception as e:
        return f"Error converting WebM to GIF: {str(e)}"
