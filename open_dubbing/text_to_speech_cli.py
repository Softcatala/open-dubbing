# Copyright 2024 Jordi Mas i Herǹadez <jmas@softcatala.org>
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

import json
import logging
import os

from typing import List

from open_dubbing.text_to_speech import TextToSpeech, Voice


class TextToSpeechCLI(TextToSpeech):

    def __init__(self, device="cpu", configuration_file=None):
        super().__init__()
        self.device = device
        self.configuration = self.load_json(configuration_file)
        self.output_dir = os.path.abspath("tts-output/")

    def load_json(self, configuration_file):
        with open(configuration_file, "r") as file:
            data = json.load(file)

        return data

    def get_available_voices(self, language_code: str) -> List[Voice]:
        voices = []

        for voice_cfg in self.configuration["voices"]:
            if voice_cfg["language"] != language_code:
                continue

            voice = Voice(
                name=voice_cfg["id"],
                gender=voice_cfg["gender"],
                region=voice_cfg["region"],
            )
            voices.append(voice)

        logging.debug(
            f"text_to_speech_cli.get_available_voices: {voices} for language {language_code}"
        )
        return voices

    def _get_command(self, *, assigned_voice: str, directory: str, text: str):
        command = self.configuration["command"]
        text = text.replace('"', "")
        cmd = command.format(
            assigned_voice=assigned_voice,
            text=text,
            directory=directory,
            device=self.device,
        )
        return cmd

    def _get_output_pattern(self, *, assigned_voice: str, directory: str, text: str):

        output_pattern = self.configuration["output_pattern"]
        pattern = output_pattern.format(
            assigned_voice=assigned_voice, text=text, directory=directory
        )
        return pattern

    def _convert_text_to_speech(
        self,
        *,
        assigned_voice: str,
        target_language: str,
        output_filename: str,
        text: str,
        speed: float,
    ) -> str:

        cmd = self._get_command(
            assigned_voice=assigned_voice, text=text, directory=self.output_dir
        )
        return_code = os.system(cmd)
        if return_code != 0:
            raise RuntimeError(
                f"Command '{cmd}' failed with return code: {return_code}"
            )

        wav_file = self._get_output_pattern(
            assigned_voice=assigned_voice,
            text=text,
            directory=self.output_dir,
        )
        self._convert_to_mp3(wav_file, output_filename)

        logging.debug(f"text_to_speech_cli._convert_text_to_speech: {text}")
        return output_filename

    def get_languages(self):
        languages = set()
        for voice_cfg in self.configuration["voices"]:
            language = voice_cfg["language"]
            languages.add(language)

        languages_list = list(languages)

        logging.debug(f"text_to_speech_cli.get_languages: {languages_list}")
        return languages_list
