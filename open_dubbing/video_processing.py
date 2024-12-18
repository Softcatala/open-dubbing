# Copyright 2024 Google LLC
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
import warnings

from typing import Final

from moviepy import AudioFileClip, VideoFileClip, concatenate_videoclips

_DEFAULT_FPS: Final[int] = 30
_DEFAULT_DUBBED_VIDEO_FILE: Final[str] = "dubbed_video"
_DEFAULT_OUTPUT_FORMAT: Final[str] = ".mp4"


class VideoProcessing:

    @staticmethod
    def split_audio_video(*, video_file: str, output_directory: str) -> tuple[str, str]:
        """Splits an audio/video file into separate audio and video files."""

        base_filename = os.path.basename(video_file)
        filename, _ = os.path.splitext(base_filename)
        with VideoFileClip(video_file) as video_clip, warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            audio_clip = video_clip.audio
            audio_output_file = os.path.join(output_directory, filename + "_audio.mp3")
            audio_clip.write_audiofile(audio_output_file, logger=None)
            video_clip_without_audio = video_clip.with_audio(None)
            fps = video_clip.fps or _DEFAULT_FPS

            video_output_file = os.path.join(output_directory, filename + "_video.mp4")
            video_clip_without_audio.write_videofile(
                video_output_file, codec="libx264", fps=fps, logger=None
            )
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

        video = VideoFileClip(video_file)
        audio = AudioFileClip(dubbed_audio_file)
        duration_difference = video.duration - audio.duration
        if duration_difference > 0:
            silence = AudioFileClip(duration=duration_difference).set_duration(
                duration_difference
            )
            audio = concatenate_videoclips([audio, silence])
        elif duration_difference < 0:
            audio = audio.subclipped(0, video.duration)
        final_clip = video.with_audio(audio)
        target_language_suffix = "_" + target_language.replace("-", "_").lower()
        dubbed_video_file = os.path.join(
            output_directory,
            _DEFAULT_DUBBED_VIDEO_FILE
            + target_language_suffix
            + _DEFAULT_OUTPUT_FORMAT,
        )
        final_clip.write_videofile(
            dubbed_video_file,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            logger=None,
        )
        return dubbed_video_file
