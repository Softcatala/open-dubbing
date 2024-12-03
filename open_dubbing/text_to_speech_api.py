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
import tempfile

from typing import List
from urllib.parse import urljoin

import requests

from open_dubbing.text_to_speech import TextToSpeech, Voice


class TextToSpeechAPI(TextToSpeech):

    def __init__(self, device="cpu", server=""):
        super().__init__()
        self.server = server
        self.device = device
        self.voices = None

    def _get_voices(self):
        if not self.voices:
            url = urljoin(self.server, "/voices")
            response = requests.get(url)
            self.voices = response.json()

        return self.voices

    def get_available_voices(self, language_code: str) -> List[Voice]:
        voices = []

        for server_voice in self._get_voices():
            language = server_voice["language"]
            if language != language_code:
                continue

            voice = Voice(
                name=server_voice["id"],
                gender=server_voice["gender"],
                region=server_voice["region"],
            )
            voices.append(voice)

        logging.debug(
            f"text_to_speech_api.get_available_voices: {voices} for language {language_code}"
        )

        return voices

    def _does_voice_supports_speeds(self):
        return False

    def _convert_text_to_speech(
        self,
        *,
        assigned_voice: str,
        target_language: str,
        output_filename: str,
        text: str,
        speed: float,
    ) -> str:

        url = urljoin(self.server, "/speak")
        url = f"{url}?voice={assigned_voice}&text={text}"
        response = requests.get(url)

        temp_filename = None
        with tempfile.NamedTemporaryFile(delete=False) as temporary_file:
            temp_filename = temporary_file.name

            if response.status_code == 200:
                with open(temp_filename, "wb") as f:
                    f.write(response.content)
            else:
                logging.error(
                    f"Failed to download the file. Status code: {response.status_code}"
                )

            self._convert_to_mp3(temp_filename, output_filename)

        logging.debug(
            f"text_to_speech_api._convert_text_to_speech: assigned_voice: {assigned_voice}, output_filename: '{output_filename}'"
        )
        return output_filename

    def get_languages(self):
        languages = set()
        for server_voice in self._get_voices():
            language = server_voice["language"]
            languages.add(language)

        languages = sorted(list(languages))
        logging.debug(f"text_to_speech_api.get_languages: {languages}")
        return languages
