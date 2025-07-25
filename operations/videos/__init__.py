# Video processing operations
try:
    from .mp4_to_mov import convert_mp4_to_mov
    from .mov_to_mp4 import convert_mov_to_mp4
    from .ts_to_mp4 import convert_ts_to_mp4
    from .mp4_to_ts import convert_mp4_to_ts
    from .mkv_to_mp4 import convert_mkv_to_mp4
    from .mp4_to_mkv import convert_mp4_to_mkv
    from .webm_to_mp4 import convert_webm_to_mp4
    from .mp4_to_webm import convert_mp4_to_webm
    from .compress_video import compress_video
    from .gif_to_video import convert_gif_to_mp4, convert_gif_to_webm
    from .video_to_gif import convert_mp4_to_gif, convert_mov_to_gif, convert_webm_to_gif
    
    MOVIEPY_AVAILABLE = True
    
    __all__ = [
        'convert_mp4_to_mov',
        'convert_mov_to_mp4',
        'convert_ts_to_mp4',
        'convert_mp4_to_ts',
        'convert_mkv_to_mp4',
        'convert_mp4_to_mkv',
        'convert_webm_to_mp4',
        'convert_mp4_to_webm',
        'compress_video',
        'convert_gif_to_mp4',
        'convert_gif_to_webm',
        'convert_mp4_to_gif',
        'convert_mov_to_gif',
        'convert_webm_to_gif'
    ]
    
except ImportError:
    MOVIEPY_AVAILABLE = False
    
    # Create dummy functions that return error messages
    def convert_mp4_to_mov(input_path, output_path):
        return "Error: Video operations not available. Please install moviepy and ffmpeg."
    
    def convert_mov_to_mp4(input_path, output_path):
        return "Error: Video operations not available. Please install moviepy and ffmpeg."
    
    def convert_ts_to_mp4(input_path, output_path):
        return "Error: Video operations not available. Please install moviepy and ffmpeg."
    
    def convert_mp4_to_ts(input_path, output_path):
        return "Error: Video operations not available. Please install moviepy and ffmpeg."
    
    def convert_mkv_to_mp4(input_path, output_path):
        return "Error: Video operations not available. Please install moviepy and ffmpeg."
    
    def convert_mp4_to_mkv(input_path, output_path):
        return "Error: Video operations not available. Please install moviepy and ffmpeg."
    
    def convert_webm_to_mp4(input_path, output_path):
        return "Error: Video operations not available. Please install moviepy and ffmpeg."
    
    def convert_mp4_to_webm(input_path, output_path):
        return "Error: Video operations not available. Please install moviepy and ffmpeg."
    
    def compress_video(input_path, output_path):
        return "Error: Video operations not available. Please install moviepy and ffmpeg."
    
    def convert_gif_to_mp4(input_path, output_path):
        return "Error: Video operations not available. Please install moviepy and ffmpeg."
    
    def convert_gif_to_webm(input_path, output_path):
        return "Error: Video operations not available. Please install moviepy and ffmpeg."
    
    def convert_mp4_to_gif(input_path, output_path):
        return "Error: Video operations not available. Please install moviepy and ffmpeg."
    
    def convert_mov_to_gif(input_path, output_path):
        return "Error: Video operations not available. Please install moviepy and ffmpeg."
    
    def convert_webm_to_gif(input_path, output_path):
        return "Error: Video operations not available. Please install moviepy and ffmpeg."
    
    __all__ = [
        'convert_mp4_to_mov',
        'convert_mov_to_mp4',
        'convert_ts_to_mp4',
        'convert_mp4_to_ts',
        'convert_mkv_to_mp4',
        'convert_mp4_to_mkv',
        'convert_webm_to_mp4',
        'convert_mp4_to_webm',
        'compress_video',
        'convert_gif_to_mp4',
        'convert_gif_to_webm',
        'convert_mp4_to_gif',
        'convert_mov_to_gif',
        'convert_webm_to_gif'
    ]
