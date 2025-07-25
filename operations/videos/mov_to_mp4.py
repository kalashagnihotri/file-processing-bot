import os
import logging

logger = logging.getLogger(__name__)

try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

def convert_mov_to_mp4(input_path, output_path):
    """
    Convert MOV to MP4 format with comprehensive error handling.
    
    Args:
        input_path (str): Path to input MOV file
        output_path (str): Path for output MP4 file
        
    Returns:
        str: Success message or detailed error description
    """
    try:
        # Check if MoviePy is available
        if not MOVIEPY_AVAILABLE:
            return "Error: Video conversion not available. MoviePy library not installed. Please install: pip install moviepy"
        
        # Validate input file exists
        if not os.path.exists(input_path):
            return f"Error: Input MOV file does not exist: {input_path}"
        
        # Check file size (50MB limit for Telegram)
        file_size = os.path.getsize(input_path)
        if file_size == 0:
            return f"Error: Input MOV file is empty: {input_path}"
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            return f"Error: MOV file too large ({file_size / 1024 / 1024:.1f}MB). Maximum: 50MB"
        
        # Validate output directory
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                return f"Error: Cannot create output directory: {e}"
        
        # Load and process video
        video = None
        try:
            video = VideoFileClip(input_path)
            
            # Validate video properties
            if video.duration is None or video.duration <= 0:
                return f"Error: Invalid video duration in MOV file"
            
            if video.duration > 300:  # 5 minutes limit
                return f"Error: Video too long ({video.duration:.1f}s). Maximum: 300 seconds"
            
            # Convert to MP4
            video.write_videofile(
                output_path, 
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
        except Exception as e:
            if "codec" in str(e).lower():
                return f"Error: Unsupported video codec in MOV file: {e}"
            elif "audio" in str(e).lower():
                return f"Error: Audio processing failed: {e}"
            else:
                return f"Error: Cannot process MOV file: {e}"
        finally:
            if video:
                try:
                    video.close()
                except:
                    pass
        
        # Verify output file
        if not os.path.exists(output_path):
            return f"Error: MP4 file was not created successfully"
        
        output_size = os.path.getsize(output_path)
        if output_size == 0:
            return f"Error: Output MP4 file is empty (conversion failed)"
        
        # Success message with file info
        output_mb = output_size / 1024 / 1024
        logger.info(f"Successfully converted MOV to MP4: {os.path.basename(input_path)} -> {os.path.basename(output_path)} ({output_mb:.2f}MB)")
        return f"Successfully converted MOV to MP4: {os.path.basename(output_path)} ({output_mb:.2f}MB)"
        
    except MemoryError:
        return f"Error: Video file too large to process (insufficient memory)"
    except PermissionError:
        return f"Error: Permission denied accessing video files"
    except Exception as e:
        logger.error(f"Unexpected error in MOV to MP4 conversion: {e}")
        return f"Error converting MOV to MP4: {str(e)}"