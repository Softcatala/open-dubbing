import json
import os
import platform
import tempfile

import numpy as np
import pytest

from faster_whisper import WhisperModel


class TestCmd:

    # TODO:
    #   - To check transcription out of the final video
    #   - Check speed in macOS
    def _get_transcription(self, filename):
        model = WhisperModel("medium")
        segments, info = model.transcribe(filename, language="ca", temperature=[0])
        text = ""
        for segment in segments:
            text += segment.text
        return text.strip(), info.language

    @pytest.mark.parametrize("tts_engine", ["edge", "mms"])
    def test_translations_with_tts(self, tts_engine):
        full_path = os.path.realpath(__file__)
        path, _ = os.path.split(full_path)

        _file = os.path.join(path, "englishvideo.mp4")
        dir_obj = tempfile.TemporaryDirectory()
        directory = dir_obj.name
        command = (
            "open-dubbing "
            f"--input_file={_file} "
            f"--output_directory={directory} "
            "--source_language=eng "
            "--target_language=cat "
            "--nllb_model=nllb-200-1.3B "
            "--whisper_model=medium "
            f"--tts={tts_engine}"
        )
        cmd = f"cd {directory} && {command}"
        os.system(cmd)
        operating = platform.system().lower()

        metadata_file = os.path.join(directory, "utterance_metadata_cat.json")
        with open(metadata_file, encoding="utf-8") as json_data:
            data = json.load(json_data)
            utterances = data["utterances"]
            text_array = [entry["translated_text"] for entry in utterances]

            # Common
            assert all(
                "Male" == entry["gender"] for entry in utterances
            ), "Utterance gender check failed"

            starts = [entry["start"] for entry in utterances]
            ends = [entry["end"] for entry in utterances]
            speeds = [entry["speed"] for entry in utterances]

            if operating == "darwin":
                assert 4 == len(utterances)

                assert np.allclose(
                    [
                        1.26284375,
                        2.44409375,
                        5.24534375,
                        7.607843750000001,
                    ],
                    starts,
                    atol=0.1,
                ), "Utterance start check failed"

                assert np.allclose(
                    [
                        2.17409375,
                        3.94596875,
                        6.61221875,
                        8.687843750000003,
                    ],
                    ends,
                    atol=0.1,
                ), "Utterance end check failed"

                assert "- Bon dia. - Bé." == text_array[0], "translated text 0"
                assert "Em dic Jordi Mas." == text_array[1], "translated text 1"
                assert "Sóc de Barcelona." == text_array[2], "translated text 2"
                assert (
                    "I m'encanta aquesta ciutat." == text_array[3]
                ), "translated text 3"

            else:
                assert 3 == len(utterances)

                assert np.allclose(
                    [
                        1.26284375,
                        5.24534375,
                        7.607843750000001,
                    ],
                    starts,
                    atol=0.1,
                ), "Utterance start check failed"

                assert np.allclose(
                    [
                        3.94596875,
                        6.629093750000001,
                        8.687843750000003,
                    ],
                    ends,
                    atol=0.1,
                ), "Utterance end check failed"

                assert np.allclose(
                    [
                        1.0,
                        1.0,
                        1.0,
                    ],
                    speeds,
                    atol=0.1,
                ), "Utterance speed check failed"

                assert (
                    "Bon dia, em dic Jordi Mas." == text_array[0]
                ), "translated text 0"
                assert "Sóc de Barcelona." == text_array[1], "translated text 1"
                assert (
                    "I m'encanta aquesta ciutat." == text_array[2]
                ), "translated text 2"
