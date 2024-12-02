# Copyright 2024 Jordi Mas i Hernàndez <jmas@softcatala.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess

from typing import Final

from open_dubbing.ffmpeg import FFmpeg

_DEFAULT_FPS: Final[int] = 30
_DEFAULT_DUBBED_VIDEO_FILE: Final[str] = "dubbed_video"
_DEFAULT_OUTPUT_FORMAT: Final[str] = ".mp4"


class VideoProcessing:

    @staticmethod
    def split_audio_video(*, video_file: str, output_directory: str) -> tuple[str, str]:
        """
        Splits an audio/video file into separate audio and video files using a single ffmpeg command.
        """

        base_filename = os.path.basename(video_file)
        filename, _ = os.path.splitext(base_filename)
        audio_output_file = os.path.join(output_directory, f"{filename}_audio.mp3")
        video_output_file = os.path.join(output_directory, f"{filename}_video.mp4")

        command = [
            "ffmpeg",
            "-y",
            "-i",
            video_file,  # Input video file
            "-map",
            "0:a:0",
            "-b:a",
            "128K",  # Set audio bitrate
            audio_output_file,  # Extract audio stream to MP3
            "-map",
            "0:v:0",
            "-an",
            "-c:v",
            "copy",
            video_output_file,  # Extract video without audio
        ]

        FFmpeg().run(command)
        return video_output_file, audio_output_file

    @staticmethod
    def combine_audio_video(
        *,
        video_file: str,
        dubbed_audio_file: str,
        output_directory: str,
        target_language: str,
    ) -> str:
        """Combines an audio file with a video file, ensuring they have the same duration.

        Returns:
          The path to the output video file with dubbed audio.
        """

        target_language_suffix = "_" + target_language.replace("-", "_").lower()
        dubbed_video_file = os.path.join(
            output_directory,
            _DEFAULT_DUBBED_VIDEO_FILE
            + target_language_suffix
            + _DEFAULT_OUTPUT_FORMAT,
        )

        command = [
            "ffmpeg",
            "-y",
            "-i",
            video_file,
            "-i",
            dubbed_audio_file,
            "-c:v",
            "copy",  # Copy the video stream (no re-encoding)
            "-c:a",
            "aac",  # Re-encode the audio to AAC format
            "-map",
            "0:v:0",  # Map the video stream from the first input (video)
            "-map",
            "1:a:0",  # Map the audio stream from the second input (audio)
            dubbed_video_file,
        ]

        FFmpeg().run(command)
        return dubbed_video_file

    @staticmethod
    def is_ffmpeg_installed():
        cmd = ["ffprobe", "-version"]
        try:
            if (
                subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                ).returncode
                == 0
            ):
                return True
        except FileNotFoundError:
            return False
        return False
