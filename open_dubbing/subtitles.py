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
import platform
import shutil
import tempfile

from datetime import timedelta
from typing import List


class Subtitles:

    def write(self, *, utterance_metadata, directory, filename, translated):
        srt_file_path = filename
        srt_file_path = os.path.join(directory, srt_file_path)

        with open(srt_file_path, "w", encoding="utf-8") as subtitles_file:
            for i, utterance in enumerate(utterance_metadata):
                start_time = str(timedelta(seconds=utterance["start"]))[:-3]
                end_time = str(timedelta(seconds=utterance["end"]))[:-3]
                start_time = start_time.replace(".", ",").zfill(12)
                end_time = end_time.replace(".", ",").zfill(12)
                srt_content = f"{i+1}\n"
                srt_content += (
                    f"{start_time.replace('.', ',')} --> {end_time.replace('.', ',')}\n"
                )

                text = utterance["translated_text"] if translated else utterance["text"]
                srt_content += f"{text}\n\n"
                subtitles_file.write(srt_content)
        return srt_file_path

    def embbed_in_video(
        self,
        *,
        video_file: str,
        subtitles_files: List[str],
        languages_iso_639_3: List[str],
    ) -> str:

        filename = ""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfile(video_file, temp_file.name)
            null_device = (
                "NUL" if platform.system().lower() == "windows" else "/dev/null"
            )

            cmd = f"ffmpeg -y -i {temp_file.name}"
            for subtitles_file in subtitles_files:
                cmd += f" -i {subtitles_file}"

            cmd += " -map 0"
            idx = 0
            for language in languages_iso_639_3:
                _map = 1 + idx
                cmd += f" -map {_map} -c:s mov_text -metadata:s:s:{idx} language={language}"
                idx += 1

            cmd += f" -c:v copy -c:a copy {video_file} > {null_device} 2>&1"
            logging.debug(f"embbed_in_video. Command: {cmd}")
            os.system(cmd)
            filename = temp_file.name

        if os.path.exists(filename):
            os.remove(filename)
