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

import array
import os
import time

import numpy as np
import requests

from open_dubbing import logger
from open_dubbing.speech_to_text import SpeechToText


CAMB_API_BASE = "https://client.camb.ai/apis"

# Mapping from ISO 639-3 to CAMB AI numeric language IDs (for transcription)
ISO_639_3_TO_CAMB_LANG_ID = {
    "eng": 1,
    "spa": 54,
    "fra": 76,
    "deu": 31,
    "jpn": 88,
    "hin": 81,
    "por": 111,
    "zho": 139,
    "kor": 47,
    "ita": 86,
    "nld": 66,
    "rus": 120,
    "ara": 4,
    "tam": 131,
    "tel": 133,
    "ben": 13,
}

# Reverse mapping for language detection
CAMB_LANG_ID_TO_ISO_639_3 = {v: k for k, v in ISO_639_3_TO_CAMB_LANG_ID.items()}


class SpeechToTextCamb(SpeechToText):

    def __init__(self, *, device="cpu", model_name="camb", cpu_threads=0, api_key=""):
        super().__init__(device=device, model_name=model_name, cpu_threads=cpu_threads)
        self.api_key = api_key or os.getenv("CAMB_API_KEY", "")

    def _headers(self):
        return {"x-api-key": self.api_key}

    def load_model(self):
        # No local model to load for cloud API
        pass

    def get_languages(self):
        return sorted(ISO_639_3_TO_CAMB_LANG_ID.keys())

    def _transcribe(
        self,
        *,
        vocals_filepath: str,
        source_language_iso_639_1: str,
    ) -> str:
        # Convert ISO 639-1 to ISO 639-3 then to CAMB language ID
        from iso639 import Lang

        iso_639_3 = Lang(source_language_iso_639_1).pt3
        lang_id = ISO_639_3_TO_CAMB_LANG_ID.get(iso_639_3, 1)

        # Upload file for transcription
        with open(vocals_filepath, "rb") as f:
            files = {"media_file": (os.path.basename(vocals_filepath), f)}
            data = {"language": lang_id}
            response = requests.post(
                f"{CAMB_API_BASE}/transcribe",
                headers=self._headers(),
                files=files,
                data=data,
            )

        if not response.ok:
            logger().error(
                f"speech_to_text_camb: Transcription API error {response.status_code}: {response.text[:200]}"
            )
        response.raise_for_status()
        task_id = response.json()["task_id"]

        # Poll for completion
        max_attempts = 60
        for _ in range(max_attempts):
            status_response = requests.get(
                f"{CAMB_API_BASE}/transcribe/{task_id}",
                headers=self._headers(),
            )
            status_response.raise_for_status()
            status_data = status_response.json()
            status = status_data.get("status")

            if status == "SUCCESS":
                run_id = status_data.get("run_id")
                result_response = requests.get(
                    f"{CAMB_API_BASE}/transcription-result/{run_id}",
                    headers=self._headers(),
                )
                result_response.raise_for_status()
                result = result_response.json()

                # The API returns {"transcript": [{"text": "...", ...}, ...]}
                transcript_segments = result.get("transcript", [])
                if transcript_segments:
                    transcription = " ".join(
                        seg.get("text", "") for seg in transcript_segments
                    ).strip()
                else:
                    transcription = result.get("transcription", result.get("text", ""))

                logger().debug(
                    f"speech_to_text_camb._transcribe: '{transcription[:80]}'"
                )
                return transcription
            elif status in ("ERROR", "FAILED"):
                raise RuntimeError(
                    f"CAMB AI transcription failed for task {task_id}: {status_data}"
                )

            time.sleep(2)

        raise TimeoutError(f"CAMB AI transcription timed out for task {task_id}")

    def _get_audio_language(self, audio: array.array) -> str:
        # CAMB AI doesn't have a dedicated language detection endpoint,
        # so we default to English. For proper detection, use Whisper-based STT.
        logger().debug(
            "speech_to_text_camb._get_audio_language: defaulting to 'eng' (CAMB AI does not support language detection)"
        )
        return "eng"
