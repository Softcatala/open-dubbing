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
