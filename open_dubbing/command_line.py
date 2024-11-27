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

import argparse

WHISPER_MODEL_NAMES = [
    "medium",
    "large-v2",
    "large-v3",
]


class NewlinePreservingHelpFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        # Split the text by explicit newlines first
        lines = text.splitlines()
        # Then apply the default behavior for line wrapping
        wrapped_lines = []
        for line in lines:
            wrapped_lines.extend(argparse.HelpFormatter._split_lines(self, line, width))
        return wrapped_lines


class CommandLine:

    @staticmethod
    def read_parameters():
        """Parses command-line arguments and runs the dubbing process."""
        parser = argparse.ArgumentParser(
            description="AI dubbing system which uses machine learning models to automatically translate and synchronize audio dialogue into different languages",
            formatter_class=NewlinePreservingHelpFormatter,
        )
        parser.add_argument(
            "--input_file",
            required=True,
            help="Path to the input video file.",
        )
        parser.add_argument(
            "--output_directory",
            default="output/",
            help="Directory to save output files.",
        )
        parser.add_argument(
            "--source_language",
            help="Source language (ISO 639-3)",
        )
        parser.add_argument(
            "--target_language",
            required=True,
            help="Target language for dubbing (ISO 639-3).",
        )
        parser.add_argument(
            "--hugging_face_token",
            default=None,
            help="Hugging Face API token.",
        )
        parser.add_argument(
            "--tts",
            type=str,
            default="mms",
            choices=["mms", "coqui", "edge", "cli", "api"],
            help=(
                "Text to Speech engine to use. Choices are:\n"
                "'mms': Meta Multilingual Speech engine, supports +1100 languages.\n"
                "'coqui': Coqui TTS, an open-source alternative for high-quality TTS.\n"
                "'edge': Microsoft Edge TSS.\n"
                "'cli': User defined TTS invoked from command line.\n"
                "'api': Implements a user defined TTS API contract to enable non supported TTS.\n"
            ),
        )
        parser.add_argument(
            "--stt",
            type=str,
            default="auto",
            choices=["auto", "faster-whisper", "transformers"],
            help=(
                "Speech to text. Choices are:\n"
                "'auto': Autoselect best implementation.\n"
                "'faster-whisper': Faster-whisper's OpenAI whisper implementation.\n"
                "'transformers': Transformers OpenAI whisper implementation.\n"
            ),
        )
        parser.add_argument(
            "--translator",
            type=str,
            default="nllb",
            choices=["nllb", "apertium"],
            help=(
                "Text to Speech engine to use. Choices are:\n"
                "'nllb': Meta's no Language Left Behind (NLLB).\n"
                "'apertium': Apertium compatible API server.\n"
            ),
        )
        parser.add_argument(
            "--apertium_server",
            type=str,
            default="",
            help=("Apertium's URL server to use"),
        )

        parser.add_argument(
            "--device",
            type=str,
            default="cpu",
            choices=["cpu", "cuda"],
            help=("Device to use"),
        )
        parser.add_argument(
            "--cpu_threads",
            type=int,
            default=0,
            help="number of threads used for CPU inference (if is not specified uses defaults for each framework)",
        )
        parser.add_argument(
            "--clean-intermediate-files",
            action="store_true",
            help="clean intermediate files used during the dubbing process",
        )

        parser.add_argument(
            "--nllb_model",
            type=str,
            default="nllb-200-3.3B",
            choices=["nllb-200-1.3B", "nllb-200-3.3B"],
            help="Meta NLLB translation model size. Choices are:\n"
            "'nllb-200-3.3B': gives best translation quality.\n"
            "'nllb-200-1.3B': is the fastest.\n",
        )

        parser.add_argument(
            "--whisper_model",
            default="large-v3",
            choices=WHISPER_MODEL_NAMES,
            help="name of the OpenAI Whisper speech to text model size to use",
        )

        parser.add_argument(
            "--target_language_region",
            default="",
            help="For some TTS you can specify the region of the language. For example, 'ES' will indicate accent from Spain.",
        )

        parser.add_argument(
            "--tts_cli_cfg_file",
            default="",
            help="JSon configuration file when using a TTS which is invoked from the command line.",
        )

        parser.add_argument(
            "--log_level",
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Set the logging level",
        )
        parser.add_argument(
            "--tts_api_server",
            type=str,
            default="",
            help=("TTS api server URL when using the 'API' tts"),
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update the dubbed video produced by a previous execution with the latest changes in utterance_metadata file",
        )

        parser.add_argument(
            "--original_subtitles",
            action="store_true",
            default=False,
            help="Add original subtitles as stream in the output video",
        )
        parser.add_argument(
            "--dubbed_subtitles",
            default=False,
            action="store_true",
            help="Add dubbed subtitles as stream in the output video",
        )

        return parser.parse_args()
