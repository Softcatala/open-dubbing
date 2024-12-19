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

from datetime import timedelta


class Subtitles:

    def write(self, *, utterance_metadata, directory, filename, translated):
        srt_file_path = os.path.join(directory, filename)

        with open(srt_file_path, "w", encoding="utf-8") as subtitles_file:
            for i, utterance in enumerate(utterance_metadata):
                start_time = self.format_srt_time(utterance["start"])
                end_time = self.format_srt_time(utterance["end"])

                idx = i + 1
                srt_content = f"{idx}\n"
                srt_content += f"{start_time} --> {end_time}\n"

                text = utterance["translated_text"] if translated else utterance["text"]
                srt_content += f"{text}\n\n"
                subtitles_file.write(srt_content)
        return srt_file_path

    @staticmethod
    def format_srt_time(seconds):
        """Format seconds as HH:MM:SS,mmm for SRT files."""
        time_delta = timedelta(seconds=seconds)
        total_seconds = int(time_delta.total_seconds())
        milliseconds = int((time_delta.total_seconds() - total_seconds) * 1000)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"
