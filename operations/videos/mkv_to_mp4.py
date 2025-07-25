from moviepy.editor import VideoFileClip
import os

def convert_mkv_to_mp4(input_path, output_path):
    try:
        video = VideoFileClip(input_path)
        video.write_videofile(output_path, codec='libx264')
        video.close()
        return f"Converted MKV to MP4: {output_path}"
    except Exception as e:
        return f"Error converting MKV to MP4: {e}"