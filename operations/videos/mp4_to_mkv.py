from moviepy.editor import VideoFileClip
import os

def convert_mp4_to_mkv(input_path, output_path):
    try:
        video = VideoFileClip(input_path)
        video.write_videofile(output_path, codec='libx264')
        video.close()
        return f"Converted MP4 to MKV: {output_path}"
    except Exception as e:
        return f"Error converting MP4 to MKV: {e}"