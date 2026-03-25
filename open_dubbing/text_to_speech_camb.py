# Copyright 2025 CAMB AI
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

from typing import List

import requests

from open_dubbing import logger
from open_dubbing.text_to_speech import TextToSpeech, Voice


CAMB_API_BASE = "https://client.camb.ai/apis"

# Mapping from ISO 639-3 to CAMB AI BCP-47 TTS language codes
ISO_639_3_TO_CAMB_TTS = {
    "eng": "en-us",
    "spa": "es-es",
    "fra": "fr-fr",
    "deu": "de-de",
    "jpn": "ja-jp",
    "hin": "hi-in",
    "por": "pt-br",
    "zho": "zh-cn",
    "kor": "ko-kr",
    "ita": "it-it",
    "nld": "nl-nl",
    "rus": "ru-ru",
    "ara": "ar-sa",
    "tam": "ta-in",
    "tel": "te-in",
    "ben": "bn-in",
}


class TextToSpeechCamb(TextToSpeech):

    def __init__(self, device="cpu", api_key=""):
        super().__init__()
        self.api_key = api_key or os.getenv("CAMB_API_KEY", "")
        self._voices_cache = {}

    def _headers(self):
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def get_available_voices(self, language_code: str) -> List[Voice]:
        if language_code in self._voices_cache:
            return self._voices_cache[language_code]

        camb_lang = ISO_639_3_TO_CAMB_TTS.get(language_code)
        if not camb_lang:
            return []

        try:
            response = requests.get(
                f"{CAMB_API_BASE}/list-voices",
                headers={"x-api-key": self.api_key},
            )
            response.raise_for_status()
            voice_data = response.json()
        except requests.RequestException as e:
            logger().error(f"text_to_speech_camb: Failed to fetch voices: {e}")
            return [Voice(name="147320", gender=self._SSML_MALE, region="")]

        voices = []
        for v in voice_data:
            gender = self._SSML_FEMALE if v.get("gender") == 2 else self._SSML_MALE
            voice = Voice(
                name=str(v.get("voice_id", "")),
                gender=gender,
                region="",
            )
            voices.append(voice)

        if not voices:
            voices = [Voice(name="147320", gender=self._SSML_MALE, region="")]

        self._voices_cache[language_code] = voices
        logger().debug(
            f"text_to_speech_camb.get_available_voices: {len(voices)} voices for {language_code}"
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
        camb_lang = ISO_639_3_TO_CAMB_TTS.get(target_language, "en-us")

        try:
            voice_id = int(assigned_voice)
        except (ValueError, TypeError):
            voice_id = 147320
            logger().warning(
                f"text_to_speech_camb: Invalid voice '{assigned_voice}', falling back to default voice {voice_id}"
            )

        payload = {
            "text": text,
            "voice_id": voice_id,
            "language": camb_lang,
            "speech_model": "mars-flash",
            "output_configuration": {"format": "wav"},
        }

        logger().debug(
            f"text_to_speech_camb._convert_text_to_speech: voice={voice_id}, lang={camb_lang}, text='{text[:50]}...'"
        )

        response = requests.post(
            f"{CAMB_API_BASE}/tts-stream",
            headers=self._headers(),
            json=payload,
        )
        if not response.ok:
            logger().error(
                f"text_to_speech_camb: TTS API error {response.status_code}: {response.text[:200]}"
            )
        response.raise_for_status()

        if not response.content:
            raise RuntimeError(
                f"text_to_speech_camb: TTS API returned empty audio for text '{text[:50]}'"
            )

        with open(output_filename, "wb") as f:
            f.write(response.content)

        return output_filename

    def get_languages(self):
        return sorted(ISO_639_3_TO_CAMB_TTS.keys())
