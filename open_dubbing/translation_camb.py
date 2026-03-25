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
import time

import requests

from open_dubbing import logger
from open_dubbing.translation import Translation


CAMB_API_BASE = "https://client.camb.ai/apis"

# Mapping from ISO 639-3 to CAMB AI numeric language IDs
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


class TranslationCamb(Translation):

    def __init__(self, device="cpu", api_key=""):
        super().__init__(device)
        self.api_key = api_key or os.getenv("CAMB_API_KEY", "")
        self._language_pairs_cache = None

    def _headers(self):
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def load_model(self, name=None):
        # No local model to load for cloud API
        pass

    def _translate_text(
        self, source_language: str, target_language: str, text: str
    ) -> str:
        source_id = ISO_639_3_TO_CAMB_LANG_ID.get(source_language)
        target_id = ISO_639_3_TO_CAMB_LANG_ID.get(target_language)

        if source_id is None or target_id is None:
            raise ValueError(
                f"Language pair ({source_language}, {target_language}) not supported by CAMB AI"
            )

        # Create translation task
        payload = {
            "texts": [text],
            "source_language": source_id,
            "target_language": target_id,
        }
        response = requests.post(
            f"{CAMB_API_BASE}/translate",
            headers=self._headers(),
            json=payload,
        )
        if not response.ok:
            logger().error(
                f"translation_camb: Translation API error {response.status_code}: {response.text[:200]}"
            )
        response.raise_for_status()
        task_id = response.json()["task_id"]

        # Poll for completion
        max_attempts = 60
        for _ in range(max_attempts):
            status_response = requests.get(
                f"{CAMB_API_BASE}/translate/{task_id}",
                headers=self._headers(),
            )
            status_response.raise_for_status()
            status_data = status_response.json()
            status = status_data.get("status")

            if status == "SUCCESS":
                run_id = status_data.get("run_id")
                result_response = requests.get(
                    f"{CAMB_API_BASE}/translation-result/{run_id}",
                    headers=self._headers(),
                )
                result_response.raise_for_status()
                result = result_response.json()
                texts = result.get("texts", [])
                translated_text = texts[0] if texts else result.get("translation", result.get("text", ""))
                logger().debug(
                    f"translation_camb._translate_text: '{text[:50]}...' -> '{translated_text[:50]}...'"
                )
                return translated_text
            elif status in ("ERROR", "FAILED"):
                raise RuntimeError(
                    f"CAMB AI translation failed for task {task_id}: {status_data}"
                )

            time.sleep(2)

        raise TimeoutError(f"CAMB AI translation timed out for task {task_id}")

    def get_language_pairs(self):
        if self._language_pairs_cache is not None:
            return self._language_pairs_cache

        supported = list(ISO_639_3_TO_CAMB_LANG_ID.keys())
        pairs = set()
        for source in supported:
            for target in supported:
                if source != target:
                    pairs.add((source, target))

        self._language_pairs_cache = pairs
        return pairs
