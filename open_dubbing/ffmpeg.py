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

import logging
import os
import shutil
import subprocess
import tempfile

from typing import List


class FFmpeg:

    def _run(self, *, command: str, fail: bool = True):
        with open(os.devnull, "wb") as devnull:
            try:
                result = subprocess.run(command, stdout=devnull, stderr=subprocess.PIPE)
                if result.returncode != 0:
                    raise subprocess.CalledProcessError(result.returncode, command)
            except subprocess.CalledProcessError as e:
                logging.error(
                    f"Error running command: {command} failed with exit code {e.returncode} and output '{result.stderr}'"
                )
                if fail:
                    raise

    def convert_to_format(self, *, source: str, target: str):
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-i",
            source,
            target,
        ]
        FFmpeg()._run(command=cmd)

    def remove_silence(self, *, filename: str):
        tmp_filename = ""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            tmp_filename = temp_file.name
            shutil.copyfile(filename, tmp_filename)
            cmd = [
                "ffmpeg",
                "-hide_banner",
                "-y",
                "-i",
                tmp_filename,
                "-af",
                "silenceremove=stop_periods=-1:stop_duration=0.1:stop_threshold=-50dB",
                filename,
            ]
            FFmpeg()._run(command=cmd, fail=False)

        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)

    def adjust_audio_speed(self, *, filename: str, speed: float):
        tmp_filename = ""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            tmp_filename = temp_file.name
            shutil.copyfile(filename, tmp_filename)
            cmd = [
                "ffmpeg",
                "-hide_banner",
                "-y",
                "-i",
                tmp_filename,
                "-filter:a",
                f"atempo={speed}",
                filename,
            ]
            FFmpeg()._run(command=cmd, fail=False)

        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)

    def embed_subtitles(
        self,
        *,
        video_file: str,
        subtitles_files: List[str],
        languages_iso_639_3: List[str],
    ) -> str:
        filename = ""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfile(video_file, temp_file.name)
            output_file = video_file  # Modify in-place

            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output files without asking
                "-i",
                temp_file.name,
            ]

            # Add subtitle inputs
            for subtitles_file in subtitles_files:
                cmd.extend(["-i", subtitles_file])

            # Map streams
            cmd.append("-map")
            cmd.append("0")  # Map all streams from the main video file
            for idx, language in enumerate(languages_iso_639_3):
                cmd.extend(
                    [
                        "-map",
                        str(idx + 1),  # Map each subtitle file
                        "-c:s",
                        "mov_text",  # Subtitle codec
                        "-metadata:s:s:" + str(idx),
                        f"language={language}",
                    ]
                )

            # Add codecs for video and audio
            cmd.extend(["-c:v", "copy", "-c:a", "copy", output_file])

            logging.debug(f"embbed_in_video. Command: {' '.join(cmd)}")

            # Run the command using the _run method
            self._run(command=cmd, fail=True)
            filename = temp_file.name

        if os.path.exists(filename):
            os.remove(filename)

        return output_file

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
