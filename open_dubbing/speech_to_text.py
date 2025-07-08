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

import array
import os
import re
import pysrt

from abc import ABC, abstractmethod
from typing import Mapping, Sequence

from iso639 import Lang

from open_dubbing import logger
from open_dubbing.pydub_audio_segment import AudioSegment
from open_dubbing.voice_gender_classifier import VoiceGenderClassifier


class SpeechToText(ABC):

    def __init__(self, *, model_name="medium", device="cpu", cpu_threads=0):
        self.model_name = model_name
        self._model = None
        self.device = device
        self.cpu_threads = cpu_threads
        self.MIN_SECS = 0.5

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @abstractmethod
    def load_model(self):
        pass

    @abstractmethod
    def get_languages(self):
        pass

    def _get_iso_639_1(self, iso_639_3: str):
        o = Lang(iso_639_3)
        iso_639_1 = o.pt1
        return iso_639_1

    def _get_iso_639_3(self, iso_639_1: str):
        if iso_639_1 == "jw":
            iso_639_1 = "jv"

        o = Lang(iso_639_1)
        iso_639_3 = o.pt3
        return iso_639_3

    @abstractmethod
    def _transcribe(
        self,
        *,
        vocals_filepath: str,
        source_language_iso_639_1: str,
    ) -> str:
        pass

    # Whisper sometimes includes spaces at the begining of sentences or multiple spaces between words
    def _make_sure_single_space(self, sentence: str) -> str:
        fixed = re.sub(r"\s{2,}", " ", sentence)
        fixed = fixed.strip()
        return fixed

    def _srt_time_to_seconds(self, t):
        return t.hours * 3600 + t.minutes * 60 + t.seconds + t.milliseconds / 1000.0

    def transcribe_audio_chunks(
        self,
        *,
        utterance_metadata: Sequence[Mapping[str, float | str]],
        source_language: str,
        no_dubbing_phrases: Sequence[str],
        input_srt: str | None = None,
    ) -> Sequence[Mapping[str, float | str]]:

        logger().debug(f"transcribe_audio_chunks: {source_language}")
        iso_639_1 = self._get_iso_639_1(source_language)

        if input_srt:
            logger().debug(f"transcribe_audio_chunks: read transcripts from from {input_srt}")
            subs = pysrt.open(input_srt)

        updated_utterance_metadata = []
        for item in utterance_metadata:
            new_item = item.copy()
            path = ""
            try:
                if not input_srt:
                    path = item["path"]
                    duration = item["end"] - item["start"]
                    if self._is_short_audio(duration=duration):
                        transcribed_text = ""
                        logger().debug(
                            f"speech_to_text._is_short_audio. Audio is less than {self.MIN_SECS} second, skipping transcription of '{path}'."
                        )
                    else:
                        transcribed_text = self._transcribe(
                            vocals_filepath=path,
                            source_language_iso_639_1=iso_639_1,
                        )
                        transcribed_text = self._make_sure_single_space(transcribed_text)
                else:
                    match = None
                    time_tolerance=0.05
                    for sub in subs:
                        target_start = item["start"]
                        target_end = item["end"]
                        sub_start = self._srt_time_to_seconds(sub.start)
                        sub_end = self._srt_time_to_seconds(sub.end)
            
                        if (abs(sub_start - target_start) <= time_tolerance and
                            abs(sub_end - target_end) <= time_tolerance):
            
                            # Remove the [SPEAKER_XX]: tag
                            clean_text = re.sub(r'^\[SPEAKER_\d{2}\]:\s*', '', sub.text.strip())
                            match = clean_text
                            break
            
                    if match is None:
                        print(f"\n⚠️ WARNING: No subtitle match found for time range {target_start:.3f}–{target_end:.3f} seconds "
                              f"(speaker {meta.get('speaker_id', 'UNKNOWN')})\n")
                        transcribed_text = self._make_sure_single_space("")
                    else:
                        transcribed_text = self._make_sure_single_space(match)
            except Exception as e:
                logger().error(
                    f"speech_to_text.transcribe_audio_chunks. file '{path}', error: '{e}'"
                )
                transcribed_text = ""

            dubbing = len(transcribed_text) > 0
            logger().debug(
                f"transcribe_audio_chunks. text: '{transcribed_text}' - dubbing: {dubbing}"
            )
            new_item["text"] = transcribed_text
            new_item["for_dubbing"] = dubbing
            updated_utterance_metadata.append(new_item)
        return updated_utterance_metadata

    #  Returns a list of unique speakers with the largest audio sample for the speaker
    def _get_unique_speakers_largest_audio(self, utterance_metadata):
        speakers = {}
        for chunk in utterance_metadata:
            speaker = chunk["speaker_id"]
            length = chunk["end"] - chunk["start"]
            dubbed_path = chunk["path"]

            speaker_data = speakers.get(speaker, {})
            save = False
            if len(speaker_data) == 0:
                save = True
            else:
                if length > speaker_data["length"]:
                    save = True

            if save:
                speaker_data["length"] = length
                speaker_data["path"] = dubbed_path
                speakers[speaker] = speaker_data

        speaker_tuple = [(speaker, data["path"]) for speaker, data in speakers.items()]
        logger().debug(
            f"text_to_speech._get_unique_speakers_largest_audio: {speaker_tuple}"
        )
        return speaker_tuple

    def predict_gender(
        self,
        *,
        file: str,
        utterance_metadata: Sequence[Mapping[str, str | float]],
    ) -> Sequence[tuple[str, str]]:

        speaker_gender = {}
        classifier = VoiceGenderClassifier(self.device)
        speakers = self._get_unique_speakers_largest_audio(utterance_metadata)
        for speaker, path in speakers:
            gender = classifier.get_gender_for_file(path)
            speaker_gender[speaker] = gender

        r = []
        for chunk in utterance_metadata:
            speaker = chunk["speaker_id"]
            gender = speaker_gender[speaker]
            _tuple = (speaker, gender)
            r.append(_tuple)

        logger().debug(f"text_to_speech.diarize_speakers. Returns: {r}")
        return r

    def add_speaker_info(
        self,
        utterance_metadata: Sequence[Mapping[str, str | float]],
        speaker_info: Sequence[tuple[str, str]],
    ) -> Sequence[Mapping[str, str | float]]:
        if len(utterance_metadata) != len(speaker_info):
            raise Exception(
                "The length of 'utterance_metadata' and 'speaker_info' must be the"
                " same."
            )
        updated_utterance_metadata = []
        for utterance, (speaker_id, gender) in zip(utterance_metadata, speaker_info):
            new_utterance = utterance.copy()
            new_utterance["speaker_id"] = speaker_id
            new_utterance["gender"] = gender
            updated_utterance_metadata.append(new_utterance)
        return updated_utterance_metadata

    @abstractmethod
    def _get_audio_language(self, audio: array.array) -> str:
        pass

    def detect_language(self, filename: str) -> str:
        DURATION_SECS = 30
        audio = AudioSegment.from_file(filename)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)

        first_seconds = audio[: DURATION_SECS * 1000].get_array_of_samples()
        return self._get_audio_language(first_seconds)

    # To prevent Whisper hallucinations with very short audios
    def _is_short_audio(self, *, duration: float):
        if duration < self.MIN_SECS:
            return True

        return False

    def dump_transcriptions(
        self,
        *,
        output_directory: str,
        utterance_metadata: str,
    ) -> None:

        output_filename = os.path.join(output_directory, "transcription.txt")

        with open(output_filename, "w") as _file:
            for utterance in utterance_metadata:
                text = utterance["text"]
                _file.write(text + "\n")
