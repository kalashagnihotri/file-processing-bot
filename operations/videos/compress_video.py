import os
import logging

try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

try:
    import ffmpeg
    FFMPEG_PYTHON_AVAILABLE = True
except ImportError:
    FFMPEG_PYTHON_AVAILABLE = False

try:
    import subprocess
    SUBPROCESS_AVAILABLE = True
except ImportError:
    SUBPROCESS_AVAILABLE = False

def compress_video(input_path, output_path, bitrate="1000k"):
    """
    Compress video using multiple methods with fallbacks.
    """
    try:
        # Method 1: Using MoviePy (preferred)
        if MOVIEPY_AVAILABLE:
            try:
                video = VideoFileClip(input_path)
                video.write_videofile(
                    output_path, 
                    codec='libx264',
                    bitrate=bitrate,
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True,
                    verbose=False,
                    logger=None
                )
                video.close()
                
                # Get file sizes for comparison
                original_size = os.path.getsize(input_path)
                compressed_size = os.path.getsize(output_path)
                reduction = ((original_size - compressed_size) / original_size) * 100
                
                return f"Compressed video using MoviePy: {output_path} (Reduced by {reduction:.1f}%)"
            except Exception as e:
                logging.warning(f"MoviePy compression failed: {e}, trying ffmpeg-python")
        
        # Method 2: Using ffmpeg-python
        if FFMPEG_PYTHON_AVAILABLE:
            try:
                (
                    ffmpeg
                    .input(input_path)
                    .output(output_path, vcodec='libx264', video_bitrate=bitrate)
                    .overwrite_output()
                    .run(quiet=True)
                )
                
                # Get file sizes for comparison
                original_size = os.path.getsize(input_path)
                compressed_size = os.path.getsize(output_path)
                reduction = ((original_size - compressed_size) / original_size) * 100
                
                return f"Compressed video using ffmpeg-python: {output_path} (Reduced by {reduction:.1f}%)"
            except Exception as e:
                logging.warning(f"ffmpeg-python compression failed: {e}, trying direct ffmpeg")
        
        # Method 3: Using direct ffmpeg command
        if SUBPROCESS_AVAILABLE:
            try:
                # Check if ffmpeg is available
                result = subprocess.run(['ffmpeg', '-version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Use ffmpeg directly
                    subprocess.run([
                        'ffmpeg', '-i', input_path,
                        '-c:v', 'libx264',
                        '-b:v', bitrate,
                        '-c:a', 'aac',
                        '-y',  # Overwrite output file
                        output_path
                    ], check=True, capture_output=True, timeout=300)
                    
                    # Get file sizes for comparison
                    original_size = os.path.getsize(input_path)
                    compressed_size = os.path.getsize(output_path)
                    reduction = ((original_size - compressed_size) / original_size) * 100
                    
                    return f"Compressed video using direct ffmpeg: {output_path} (Reduced by {reduction:.1f}%)"
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
                logging.warning(f"Direct ffmpeg compression failed: {e}")
        
        # If all methods fail
        missing_deps = []
        if not MOVIEPY_AVAILABLE:
            missing_deps.append("MoviePy (pip install moviepy)")
        if not FFMPEG_PYTHON_AVAILABLE:
            missing_deps.append("ffmpeg-python (pip install ffmpeg-python)")
        
        return f"Error: Video compression not available. Install: {', '.join(missing_deps)} or FFmpeg application"
        
    except Exception as e:
        return f"Error compressing video: {e}"