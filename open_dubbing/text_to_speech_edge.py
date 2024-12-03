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

import asyncio
import logging
import re

from typing import List

import edge_tts

from edge_tts import VoicesManager, list_voices
from edge_tts.exceptions import NoAudioReceived
from iso639 import Lang

from open_dubbing.text_to_speech import TextToSpeech, Voice


class TextToSpeechEdge(TextToSpeech):

    async def _create_manager(self):
        voice_manager = await VoicesManager.create()
        return voice_manager

    def __init__(self, device="cpu"):
        super().__init__()
        self.device = device

    def get_available_voices(self, language_code: str) -> List[Voice]:
        voices = []
        iso_639_1 = self._get_iso_639_1(language_code)

        voice_manager = asyncio.run(self._create_manager())

        edge_voices = voice_manager.find(Language=iso_639_1)
        for edge_voice in edge_voices:
            if not all(key in edge_voice for key in ["ShortName", "Gender", "Locale"]):
                logging.warning(
                    f"Skipping voice '{edge_voice}' since is missing some fields"
                )
                continue

            voice = Voice(
                name=edge_voice["ShortName"],
                gender=edge_voice["Gender"],
                region=edge_voice["Locale"],
            )
            voices.append(voice)
            logging.debug(
                f'shortname: {edge_voice["ShortName"]}, gender: {edge_voice["Gender"]}, locale: {edge_voice["Locale"]}'
            )

        logging.debug(
            f"text_to_speech_edge.get_available_voices: {voices} for language {language_code}"
        )

        return voices

    def _get_iso_639_1(self, iso_639_3: str):
        o = Lang(iso_639_3)
        iso_639_1 = o.pt1
        return iso_639_1

    def _does_voice_supports_speeds(self):
        return True

    async def _save(self, text, speed, assigned_voice, output_filename):
        per = (100 * speed) - 100
        str_per = f"+{per:0.0f}%"
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                communicate = edge_tts.Communicate(text, assigned_voice, rate=str_per)
                await communicate.save(output_filename)
                return
            except NoAudioReceived:
                if attempt == max_retries:
                    logging.error(
                        "text_to_speech_edge._save. Max retries reached. Could not save audio."
                    )
                    raise
                else:
                    logging.warning(
                        f"text_to_speech_edge._save. No audio received, retrying attempt {attempt}."
                    )
                    await asyncio.sleep(30)

    def _convert_text_to_speech(
        self,
        *,
        assigned_voice: str,
        target_language: str,
        output_filename: str,
        text: str,
        speed: float,
    ) -> str:

        asyncio.run(self._save(text, speed, assigned_voice, output_filename))
        logging.debug(
            f"text_to_speech.client_edge.synthesize_speech: assigned_voice: {assigned_voice}, output_filename: '{output_filename}'"
        )
        return output_filename

    async def _get_list_voices(self):
        return await list_voices()

    def get_languages(self):
        voices = asyncio.run(self._get_list_voices())

        pattern = r"^([a-z]{2})-(.*)$"
        locales = set()
        for voice in voices:
            locale = voice["Locale"]
            _match = re.search(pattern, locale)
            if not _match:
                continue

            iso_639_1 = _match.group(1)
            o = Lang(iso_639_1)
            iso_639_3 = o.pt3

            locales.add(iso_639_3)
        languages = sorted(locales)
        logging.debug(f"text_to_speech.client_edge.get_languages: {languages}'")
        return languages
