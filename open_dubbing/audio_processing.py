# Copyright 2024 Google LLC
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
import os
import warnings

from typing import Final, Mapping, Sequence

import torch

from pyannote.audio import Pipeline
from pydub import AudioSegment

_DEFAULT_DUBBED_VOCALS_AUDIO_FILE: Final[str] = "dubbed_vocals.mp3"
_DEFAULT_DUBBED_AUDIO_FILE: Final[str] = "dubbed_audio"
_DEFAULT_OUTPUT_FORMAT: Final[str] = ".mp3"


def create_pyannote_timestamps(
    *,
    audio_file: str,
    pipeline: Pipeline,
    device: str = "cpu",
) -> Sequence[Mapping[str, float]]:
    """Creates timestamps from a vocals file using Pyannote speaker diarization.

    Returns:
        A list of dictionaries containing start and end timestamps for each
        speaker segment.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        if device == "cuda":
            pipeline.to(torch.device("cuda"))
        diarization = pipeline(audio_file)
        utterance_metadata = [
            {"start": segment.start, "end": segment.end, "speaker_id": speaker}
            for segment, _, speaker in diarization.itertracks(yield_label=True)
        ]
        return utterance_metadata


def _cut_and_save_audio(
    *,
    audio: AudioSegment,
    utterance: Mapping[str, str | float],
    prefix: str,
    output_directory: str,
) -> str:
    """Cuts a specified segment from an audio file, saves it as an MP3, and returns the path of the saved file.

    Args:
        audio: The audio file from which to extract the segment.
        utterance: A dictionary containing the start and end times of the segment
          to be cut. - 'start': The start time of the segment in seconds. - 'end':
          The end time of the segment in seconds.
        prefix: A string to be used as a prefix in the filename of the saved audio
          segment.
        output_directory: The directory path where the cut audio segment will be
          saved.

    Returns:
        The path of the saved MP3 file.
    """
    start_time_ms = int(utterance["start"] * 1000)
    end_time_ms = int(utterance["end"] * 1000)
    chunk = audio[start_time_ms:end_time_ms]
    chunk_filename = f"{prefix}_{utterance['start']}_{utterance['end']}.mp3"
    chunk_path = os.path.join(output_directory, chunk_filename)
    chunk.export(chunk_path, format="mp3")
    return chunk_path


def run_cut_and_save_audio(
    *,
    utterance_metadata: Sequence[Mapping[str, float]],
    audio_file: str,
    output_directory: str,
) -> Sequence[Mapping[str, float]]:
    """Cuts an audio file into chunks based on provided time ranges and saves each chunk to a file.

    Returns:
        A list of dictionaries, each containing the path to the saved chunk, and
        the original start and end times.
    """

    audio = AudioSegment.from_file(audio_file)
    key = "path"
    prefix = "chunk"
    updated_utterance_metadata = []
    for utterance in utterance_metadata:
        chunk_path = _cut_and_save_audio(
            audio=audio,
            utterance=utterance,
            prefix=prefix,
            output_directory=output_directory,
        )
        utterance_copy = utterance.copy()
        utterance_copy[key] = chunk_path
        updated_utterance_metadata.append(utterance_copy)
    return updated_utterance_metadata


def insert_audio_at_timestamps(
    *,
    utterance_metadata: Sequence[Mapping[str, str | float]],
    background_audio_file: str,
    output_directory: str,
) -> str:
    """Inserts audio chunks into a background audio track at specified timestamps."""
    background_audio = AudioSegment.from_mp3(background_audio_file)
    total_duration = background_audio.duration_seconds
    output_audio = AudioSegment.silent(duration=total_duration * 1000)
    for item in utterance_metadata:
        _file = ""
        try:
            for_dubbing = item["for_dubbing"]
            _file = item["dubbed_path"]

            if for_dubbing is False:
                start = int(item["start"])
                end = int(item["end"])
                logging.debug(
                    f"insert_audio_at_timestamps. Skipping {_file} at start time {start} and end at {end}"
                )
                continue

            start_time = int(item["start"] * 1000)
            logging.debug(f"insert_audio_at_timestamps. Open: {_file}")
            audio_chunk = AudioSegment.from_mp3(_file)
            output_audio = output_audio.overlay(
                audio_chunk, position=start_time, loop=False
            )
        except Exception as e:
            start = int(item["start"])
            end = int(item["end"])
            logging.error(
                f"insert_audio_at_timestamps. Error on file: {_file} at start time {start} and end at {end}, error: {e}"
            )

    dubbed_vocals_audio_file = os.path.join(
        output_directory, _DEFAULT_DUBBED_VOCALS_AUDIO_FILE
    )
    output_audio.export(dubbed_vocals_audio_file, format="mp3")
    return dubbed_vocals_audio_file


def merge_background_and_vocals(
    *,
    background_audio_file: str,
    dubbed_vocals_audio_file: str,
    output_directory: str,
    target_language: str,
    vocals_volume_adjustment: float = 5.0,
    background_volume_adjustment: float = 0.0,
) -> str:
    """Mixes background music and vocals tracks, normalizes the volume, and exports the result.

    Returns:
      The path to the output audio file with merged dubbed vocals and original
      background audio.
    """

    background = AudioSegment.from_mp3(background_audio_file)
    vocals = AudioSegment.from_mp3(dubbed_vocals_audio_file)
    background = background.normalize()
    vocals = vocals.normalize()
    background = background + background_volume_adjustment
    vocals = vocals + vocals_volume_adjustment
    shortest_length = min(len(background), len(vocals))
    background = background[:shortest_length]
    vocals = vocals[:shortest_length]
    mixed_audio = background.overlay(vocals)
    target_language_suffix = "_" + target_language.replace("-", "_").lower()
    dubbed_audio_file = os.path.join(
        output_directory,
        _DEFAULT_DUBBED_AUDIO_FILE + target_language_suffix + _DEFAULT_OUTPUT_FORMAT,
    )
    mixed_audio.export(dubbed_audio_file, format="mp3")
    return dubbed_audio_file
