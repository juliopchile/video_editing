"""
Author:
    Julio López B
Date Created:
    10-10-2023
Description:
    This code includes useful functions to use ffmpeg through subprocess.
Requirements:
    Having ffmpeg installed on your PC.
"""

import os
import subprocess


def extract_audio(in_file: str, out_file: str = None, extension: str = None):
    """
    This function extracts the audio from a video file using ffmpeg.

    Parameters:
    :param in_file: The path to the input video file.
    :param out_file: The path to the output audio file. If not provided, a default name will be used.
    :param extension: The audio codec to use for the output file. If not provided, 'libmp3lame' will be used.
    :return:

    Examples:
        - extract_audio('video.mp4')  # Output: video_audio.mp3
        - extract_audio('video.mp4', 'audio.wav')  # Output: audio.wav
        - extract_audio('video.mp4', extension='aac')  # Output: video_audio.aac
    """

    # Get the directory and name of the input file
    in_path = os.path.dirname(in_file)
    in_name = os.path.splitext(os.path.basename(in_file))[0]

    # Set the default extension and file name
    if extension is None:
        extension = 'libmp3lame'
        ex = '.mp3'
    else:
        ex = '.' + extension

    # Set the output file path and name
    if out_file is None:
        out_file = os.path.join(in_path, in_name + '_audio')
    else:
        out_file = os.path.splitext(out_file)[0]
        out_path = os.path.split(out_file)[0]
        if out_path == '':
            out_file = os.path.join(in_path, out_file)

    out_file_t = out_file + ex

    # FFmpeg command

    ffmpeg_cmd = [
        'ffmpeg',
        '-i', in_file,
        out_file_t
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Conversion successful: {in_file} -> {out_file_t}")
    except subprocess.CalledProcessError as e:
        print(f"Conversion failed: {e.cmd}")


def convert_to_mp4(in_file: str, out_file: str):
    """
    This function converts a video file to MP4 format using ffmpeg. This is currently not recommended, prefer using a
    video editor instead.

    :param in_file: The path to the input video file.
    :param out_file: The path to the output MP4 file.
    :return:

    Examples:
        - convert_to_mp4('video.avi', 'video.mp4')
    """

    # FFmpeg command
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', in_file,
        '-c:v', 'copy',  # Copying video stream without re-encoding
        '-c:a', 'libmp3lame',  # Transcoding audio stream to mp3
        out_file
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Conversion successful: {in_file} -> {out_file}")
    except subprocess.CalledProcessError as e:
        print(f"Conversion failed: {e}")


def process_videos(video_path, audio_path, audio_ext='mp3'):
    """
    This function search all videos inside the video_path and copy them as audio in the audio_path.
    :param video_path: The path for the input video files.
    :param audio_path: The path for the output audio files.
    :return:
    """
    # Ensure the audio_path directory exists, or create it if necessary
    os.makedirs(audio_path, exist_ok=True)

    # Get a list of existing audio files in the audio_path
    existing_audio_files = set(os.listdir(audio_path))

    # Iterate through files in the video_path directory
    for filename in os.listdir(video_path):
        if filename.endswith(('.mp4', '.avi', '.mkv', '.mov')):  # You can add more video extensions if needed
            video_file = os.path.join(video_path, filename)
            audio_file = os.path.join(audio_path, os.path.splitext(filename)[0])
            print('\n\n')

            # Check if the corresponding audio file already exists
            if os.path.basename(audio_file+'.'+audio_ext) not in existing_audio_files:
                extract_audio(video_file, audio_file, audio_ext)
                print(f"Extracted audio from: {video_file}")
            else:
                print(f"Skipped: {video_file} (Audio already exists)")


if __name__ == "__main__":
    video = "video_clip_test.mp4"
    extract_audio(video)
