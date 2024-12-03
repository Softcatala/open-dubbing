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

"""Tests for utility functions in audio_processing.py."""

import os
import tempfile

from unittest.mock import MagicMock

import numpy as np
import pytest

from moviepy.audio.AudioClip import AudioArrayClip
from pyannote.audio import Pipeline
from pydub import AudioSegment

from open_dubbing import audio_processing


class TestCreatePyannoteTimestamps:

    def test_create_timestamps_with_silence(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temporary_file:
            silence_duration = 10
            silence = AudioArrayClip(
                np.zeros((int(44100 * silence_duration), 2), dtype=np.int16),
                fps=44100,
            )
            silence.write_audiofile(temporary_file.name)
            mock_pipeline = MagicMock(spec=Pipeline)
            mock_pipeline.return_value.itertracks.return_value = [
                (MagicMock(start=0.0, end=silence_duration), None, "SPEAKER_00")
            ]
            timestamps = audio_processing.create_pyannote_timestamps(
                audio_file=temporary_file.name,
                pipeline=mock_pipeline,
            )
            assert timestamps == [{"start": 0.0, "end": 10, "speaker_id": "SPEAKER_00"}]


class TestCutAndSaveAudio:

    def test_cut_and_save_audio_no_clone(self):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temporary_file:
            silence_duration = 10
            silence = AudioArrayClip(
                np.zeros((int(44100 * silence_duration), 2), dtype=np.int16),
                fps=44100,
            )
            silence.write_audiofile(temporary_file.name)
            with tempfile.TemporaryDirectory() as output_directory:
                audio = AudioSegment.from_file(temporary_file.name)
                audio_processing._cut_and_save_audio(
                    audio=audio,
                    utterance=dict(start=0.1, end=0.2),
                    prefix="chunk",
                    output_directory=output_directory,
                )
                expected_file = os.path.join(output_directory, "chunk_0.1_0.2.mp3")
                assert os.path.exists(expected_file)


class TestRunCutAndSaveAudio:

    def test_run_cut_and_save_audio(self):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temporary_file:
            silence_duration = 10
            silence = AudioArrayClip(
                np.zeros((int(44100 * silence_duration), 2), dtype=np.int16),
                fps=44100,
            )
            silence.write_audiofile(temporary_file.name)
            utterance_metadata = [{"start": 0.0, "end": 5.0}]
            with tempfile.TemporaryDirectory() as output_directory:
                # TODO: Add assert on results on this method
                _ = audio_processing.run_cut_and_save_audio(
                    utterance_metadata=utterance_metadata,
                    audio_file=temporary_file.name,
                    output_directory=output_directory,
                )
                expected_file = os.path.join(output_directory, "chunk_0.0_5.0.mp3")
                _ = {
                    "path": os.path.join(output_directory, "chunk_0.0_5.0.mp3"),
                    "start": 0.0,
                    "end": 5.0,
                }
                assert os.path.exists(expected_file)


class TestInsertAudioAtTimestamps:

    @pytest.mark.parametrize(
        "for_dubbing, expected_file_size",
        [
            (False, 20524),
            (True, 160749),
        ],
    )
    def test_insert_audio_at_timestamps(self, for_dubbing, expected_file_size):

        with tempfile.TemporaryDirectory() as temporary_directory:
            background_audio_file = f"{temporary_directory}/test_background.mp3"
            silence_duration = 10
            silence = AudioArrayClip(
                np.zeros((int(44100 * silence_duration), 2), dtype=np.int16),
                fps=44100,
            )
            silence.write_audiofile(background_audio_file)
            audio_chunk_path = f"{temporary_directory}/test_chunk.mp3"
            chunk_duration = 2
            chunk = AudioArrayClip(
                np.zeros((int(44100 * chunk_duration), 2), dtype=np.int16),
                fps=44100,
            )
            chunk.write_audiofile(audio_chunk_path)
            utterance_metadata = [
                {
                    "start": 3.0,
                    "end": 5.0,
                    "for_dubbing": for_dubbing,
                    "dubbed_path": audio_chunk_path,
                }
            ]
            output_path = audio_processing.insert_audio_at_timestamps(
                utterance_metadata=utterance_metadata,
                background_audio_file=background_audio_file,
                output_directory=temporary_directory,
            )
            file_size = os.path.getsize(output_path)
            assert os.path.exists(output_path)

            tolerance = 1  # Allow for a 1-byte difference across platforms
            assert abs(expected_file_size - file_size) <= tolerance


class TestMixMusicAndVocals:

    def test_mix_music_and_vocals(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            background_audio_path = f"{temporary_directory}/test_background.mp3"
            vocals_audio_path = f"{temporary_directory}/test_vocals.mp3"
            silence_duration = 10
            silence_background = AudioArrayClip(
                np.zeros((int(44100 * silence_duration), 2), dtype=np.int16),
                fps=44100,
            )
            silence_background.write_audiofile(background_audio_path)
            silence_duration = 5
            silence_vocals = AudioArrayClip(
                np.zeros((int(44100 * silence_duration), 2), dtype=np.int16),
                fps=44100,
            )
            silence_vocals.write_audiofile(vocals_audio_path)
            output_audio_path = audio_processing.merge_background_and_vocals(
                background_audio_file=background_audio_path,
                dubbed_vocals_audio_file=vocals_audio_path,
                output_directory=temporary_directory,
                target_language="en-US",
            )
            assert os.path.exists(output_audio_path)
