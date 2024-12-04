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
import tempfile

from open_dubbing.subtitles import Subtitles


class TestSubtitles:

    def _get_lines_from_file(self, filename):
        with open(filename, "r") as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
        return lines

    def _get_utterances(self):
        return [
            {
                "id": 1,
                "start": 1.26284375,
                "end": 3.94596875,
                "text": "Good morning, my name is Jordi Mas.",
                "translated_text": "Bon dia, el meu nom és Jordi Mas.",
            },
            {
                "id": 2,
                "start": 5.24534375,
                "end": 6.629093750000001,
                "text": "I am from Barcelona.",
                "translated_text": "Sóc de Barcelona.",
            },
        ]

    def test_write_original(self):
        subtitles = Subtitles()
        srt_file = tempfile.NamedTemporaryFile(suffix=".srt", delete=False).name

        directory = os.path.dirname(srt_file)
        filename = os.path.basename(srt_file)
        subtitles.write(
            utterance_metadata=self._get_utterances(),
            directory=directory,
            filename=filename,
            translated=False,
        )

        lines = self._get_lines_from_file(srt_file)
        os.remove(srt_file)
        assert lines == [
            "1",
            "00:00:01,262 --> 00:00:03,945",
            "Good morning, my name is Jordi Mas.",
            "",
            "2",
            "00:00:05,245 --> 00:00:06,629",
            "I am from Barcelona.",
            "",
        ]

    def test_write_dubbed(self):
        subtitles = Subtitles()
        srt_file = tempfile.NamedTemporaryFile(suffix=".srt", delete=False).name

        directory = os.path.dirname(srt_file)
        filename = os.path.basename(srt_file)
        subtitles.write(
            utterance_metadata=self._get_utterances(),
            directory=directory,
            filename=filename,
            translated=True,
        )

        lines = self._get_lines_from_file(srt_file)
        os.remove(srt_file)
        assert lines == [
            "1",
            "00:00:01,262 --> 00:00:03,945",
            "Bon dia, el meu nom és Jordi Mas.",
            "",
            "2",
            "00:00:05,245 --> 00:00:06,629",
            "Sóc de Barcelona.",
            "",
        ]

    def _get_srt(self):
        return [
            "1",
            "00:00:01,262 --> 00:00:03,945",
            "Bon dia, el meu nom és Jordi Mas.",
            "",
            "2",
            "00:00:05,245 --> 00:00:06,629",
            "Sóc de Barcelona.",
            "",
        ]
