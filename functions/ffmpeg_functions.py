"""
Author:
    Julio López B
Date Created:
    10-10-2023
Last Modified:
    27-07-2025
Description:
    This code include useful functions to use ffmpeg through subprocess.
Requirements
    Having ffmpeg installed on your PC.
"""

import os
import subprocess

VIDEO_EXTENSIONS = (".mp4", ".avi", ".mkv", ".mov")


def extract_audio(in_file: str, out_file: str | None = None,
                  extension: str | None = None) -> None:
    """
    This function extracts the audio from a video file using ffmpeg.

    :param str in_file: The path to the input video file.
    :param str | None out_file: The path to the output audio file. If
    not provided, a default name will be used.
    :param str | None extension: The audio codec to use for the output
    file. If not provided, 'libmp3lame' will be used.
    """
    # Get the directory and name of the input file
    in_path = os.path.dirname(in_file)
    in_name = os.path.splitext(os.path.basename(in_file))[0]

    # Set the default extension and file name
    # Map extension to codec and file extension
    codec_map = {
        "mp3": ("libmp3lame", ".mp3"),
        "aac": ("aac", ".aac"),
        "wav": ("pcm_s16le", ".wav"),
        "flac": ("flac", ".flac"),
        # Add more mappings as needed
    }

    if extension is None:
        codec, ex = codec_map["mp3"]
    else:
        lower = extension.lower()
        codec, ex = codec_map.get(lower, (extension, f".{extension}"))

    # Set the output file path and name
    if out_file is None:
        out_file = os.path.join(in_path, in_name + "_audio")
    else:
        out_file = os.path.splitext(out_file)[0]
    out_file_t = out_file + ex

    # FFmpeg command
    ffmpeg_cmd = ["ffmpeg", "-i", in_file, "-c:a", codec, out_file_t]
    stderr_arg = subprocess.PIPE
    try:
        subprocess.run(ffmpeg_cmd, check=True, stderr=stderr_arg, text=True)
        print(f"Conversion successful: {in_file} -> {out_file_t}")
    except subprocess.CalledProcessError as e:
        print(f"Conversion failed: {e}\nStderr: {e.stderr}")


def convert_to_mp4(in_file: str, out_file: str):
    """
    This function converts a video file to MP4 format using ffmpeg.
    This is currently not recommended, prefer using a video editor
    instead.

    :param str in_file: The path to the input video file.
    :param str out_file: The path to the output MP4 file.
    """

    # FFmpeg command
    ffmpeg_cmd = [
        "ffmpeg",
        "-i",
        in_file,
        "-c:v",
        "copy",  # Copying video stream without re-encoding
        "-c:a",
        "libmp3lame",  # Transcoding audio stream to mp3
        out_file,
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Conversion successful: {in_file} -> {out_file}")
    except subprocess.CalledProcessError as e:
        print(f"Conversion failed: {e}")


def process_videos(video_path: str, audio_path: str, audio_ext="mp3"):
    """
    This function searches all videos inside the video_path and copies
    them as audio in the audio_path.

    :param video_path: The path for the input video files.
    :param audio_path: The path for the output audio files.
    :param audio_ext: The extension/codec for the output audio files.
    """
    # Ensure the audio_path directory exists, or create it if necessary
    os.makedirs(audio_path, exist_ok=True)

    # Get a list of existing audio files in the audio_path
    existing_audio_files = set(os.listdir(audio_path))

    # Iterate through files in the video_path directory
    for file in os.listdir(video_path):
        if file.endswith(VIDEO_EXTENSIONS):
            video_file = os.path.join(video_path, file)
            audio_file = os.path.join(audio_path, os.path.splitext(file)[0])
            # Check if the corresponding audio file already exists
            audio_filename = audio_file + "." + audio_ext
            if os.path.basename(audio_filename) not in existing_audio_files:
                extract_audio(video_file, audio_file, audio_ext)
                print(f"Extracted audio from: {video_file}")
            else:
                print(f"Skipped: {video_file} (Audio already exists)")


if __name__ == "__main__":
    video = "video_clip_test.mp4"
    extract_audio(video)
