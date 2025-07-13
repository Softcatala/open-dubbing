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

import logging
import os
import sys
import warnings

import transformers

from iso639 import Lang

from open_dubbing import logger
from open_dubbing.command_line import CommandLine
from open_dubbing.dubbing import Dubber
from open_dubbing.exit_code import ExitCode
from open_dubbing.ffmpeg import FFmpeg
from open_dubbing.speech_to_text_faster_whisper import SpeechToTextFasterWhisper
from open_dubbing.speech_to_text_whisper_transformers import (
    SpeechToTextWhisperTransformers,
)
from open_dubbing.text_to_speech_api import TextToSpeechAPI
from open_dubbing.text_to_speech_cli import TextToSpeechCLI
from open_dubbing.text_to_speech_edge import TextToSpeechEdge
from open_dubbing.text_to_speech_mms import TextToSpeechMMS
from open_dubbing.translation_apertium import TranslationApertium
from open_dubbing.translation_nllb import TranslationNLLB


def _init_logging(log_level):
    logging.basicConfig(level=logging.ERROR)  # Suppress third-party loggers

    # Create your application logger
    app_logger = logging.getLogger("open_dubbing")
    app_logger.setLevel(log_level)
    app_logger.propagate = False

    # File handler for logging to a file
    file_handler = logging.FileHandler("open_dubbing.log")
    console_handler = logging.StreamHandler()

    # Formatter for log messages
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    app_logger.addHandler(file_handler)
    app_logger.addHandler(console_handler)

    transformers.logging.set_verbosity_error()
    warnings.filterwarnings("ignore", category=FutureWarning)


def log_error_and_exit(msg: str, code: ExitCode):
    logger().error(msg)
    exit(code)


def check_languages(
    source_language, target_language, _tts, translation, _stt, target_language_region
):
    spt = _stt.get_languages()
    translation_languages = translation.get_language_pairs()
    logger().debug(f"check_languages. Pairs {len(translation_languages)}")

    tts = _tts.get_languages()

    if source_language not in spt:
        msg = f"source language '{source_language}' is not supported by the speech recognition system. Supported languages: '{spt}'"
        log_error_and_exit(msg, ExitCode.INVALID_LANGUAGE_SPT)

    pair = (source_language, target_language)
    if pair not in translation_languages:
        msg = f"language pair '{pair}' is not supported by the translation system."
        log_error_and_exit(msg, ExitCode.INVALID_LANGUAGE_TRANS)

    if target_language not in tts:
        msg = f"target language '{target_language}' is not supported by the text to speech system. Supported languages: '{tts}'"
        log_error_and_exit(msg, ExitCode.INVALID_LANGUAGE_TTS)

    voices = _tts.get_available_voices(language_code=target_language)
    region_voices = _tts.get_voices_for_region_only(
        voices=voices, target_language_region=target_language_region
    )
    if len(region_voices) == 0:
        msg = f"filtering by '{target_language_region}' returns no voices for language '{target_language}' in the text to speech system"
        log_error_and_exit(msg, ExitCode.INVALID_LANGUAGE_TTS)


_ACCEPTED_VIDEO_FORMATS = ["mp4"]


def check_is_a_video(input_file: str):
    _, file_extension = os.path.splitext(input_file)
    file_extension = file_extension.lower().lstrip(".")

    if file_extension in _ACCEPTED_VIDEO_FORMATS:
        return
    msg = f"Unsupported file format: {file_extension}"
    log_error_and_exit(msg, ExitCode.INVALID_FILEFORMAT)


HUGGING_FACE_VARNAME = "HF_TOKEN"


def get_token(provided_token: str) -> str:
    token = provided_token or os.getenv(HUGGING_FACE_VARNAME)
    if not token:
        msg = "You must either provide the '--hugging_face_token' argument or"
        msg += f" set the '{HUGGING_FACE_VARNAME.upper()}' environment variable."
        log_error_and_exit(msg, ExitCode.MISSING_HF_KEY)
    return token


def _get_language_names(languages_iso_639_3):
    names = []
    for language in languages_iso_639_3:
        o = Lang(language)
        names.append(o.name)
    return sorted(names)


def list_supported_languages(_tts, translation, device):  # TODO: Not used
    s = SpeechToTextFasterWhisper(device=device)
    s.load_model()
    spt = s.get_languages()
    trans = translation.get_languages()
    tts = _tts.get_languages()

    source = _get_language_names(set(spt).intersection(set(trans)))
    print(f"Supported source languages: {source}")

    target = _get_language_names(set(tts).intersection(set(trans)))
    print(f"Supported target languages: {target}")


def _get_selected_tts(
    selected_tts: str,
    tts_cli_cfg_file: str,
    tts_api_server: str,
    device: str,
    openai_api_key: str,
):
    if selected_tts == "mms":
        tts = TextToSpeechMMS(device)
    elif selected_tts == "edge":
        tts = TextToSpeechEdge(device)
    elif selected_tts == "coqui":
        try:
            from open_dubbing.coqui import Coqui
            from open_dubbing.text_to_speech_coqui import TextToSpeechCoqui
        except Exception:
            msg = "Make sure that Coqui-tts is installed by running 'pip install open-dubbing[coqui]'"
            log_error_and_exit(msg, ExitCode.NO_COQUI_TTS)

        tts = TextToSpeechCoqui(device)
        if not Coqui.is_espeak_ng_installed():
            msg = "To use Coqui-tts you have to have espeak or espeak-ng installed"
            log_error_and_exit(msg, ExitCode.NO_COQUI_ESPEAK)
    elif selected_tts == "cli":
        if len(tts_cli_cfg_file) == 0:
            msg = "When using the tts CLI you need to provide a configuration file which describes the commands and voices to use."
            log_error_and_exit(msg, ExitCode.NO_CLI_CFG_FILE)

        tts = TextToSpeechCLI(device, tts_cli_cfg_file)
    elif selected_tts == "api":
        tts = TextToSpeechAPI(device, tts_api_server)
        if len(tts_api_server) == 0:
            msg = "When using TTS's API, you need to specify with --tts_api_server the URL of the server"
            log_error_and_exit(msg, ExitCode.NO_TTS_API_SERVER)
    elif selected_tts == "openai":
        try:
            from open_dubbing.text_to_speech_openai import TextToSpeechOpenAI
        except Exception:
            msg = "Make sure that OpenAI library is installed by running 'pip install open-dubbing[openai]'"
            log_error_and_exit(msg, ExitCode.NO_OPENAI_TTS)

        key = _get_openai_key(key=openai_api_key)
        tts = TextToSpeechOpenAI(device=device, api_key=key)
    else:
        raise ValueError(f"Invalid tts value {selected_tts}")

    return tts


def _get_selected_translator(
    translator: str, nllb_model: str, apertium_server: str, device: str
):
    if translator == "nllb":
        translation = TranslationNLLB(device)
        translation.load_model(nllb_model)
    elif translator == "apertium":
        server = apertium_server
        if len(server) == 0:
            msg = "When using Apertium's API, you need to specify with --apertium_server the URL of the server"
            log_error_and_exit(msg, ExitCode.NO_APERTIUM_SERVER)

        translation = TranslationApertium(device)
        translation.set_server(server)
    else:
        raise ValueError(f"Invalid translator value {translator}")

    return translation


def _get_openai_key(*, key: str):
    if key:
        return key

    VAR = "OPENAI_API_KEY"
    key = os.getenv(VAR)
    if key:
        return key

    msg = f"OpenAI TTS selected but no key has been pass as argument or defined in the environment variable {VAR}"
    log_error_and_exit(msg, ExitCode.NO_OPENAI_KEY)


def main():

    args = CommandLine.read_parameters()
    _init_logging(args.log_level)

    check_is_a_video(args.input_file)

    hugging_face_token = get_token(args.hugging_face_token)

    if not FFmpeg.is_ffmpeg_installed():
        msg = "You need to have ffmpeg (which includes ffprobe) installed."
        log_error_and_exit(msg, ExitCode.NO_FFMPEG)

    tts = _get_selected_tts(
        args.tts,
        args.tts_cli_cfg_file,
        args.tts_api_server,
        args.device,
        args.openai_api_key,
    )

    if sys.platform == "darwin":
        os.environ["TOKENIZERS_PARALLELISM"] = "false"

    stt_type = args.stt
    stt_text = args.stt
    if stt_type == "faster-whisper" or (
        stt_type == "auto" and sys.platform != "darwin"
    ):
        stt = SpeechToTextFasterWhisper(
            model_name=args.whisper_model,
            device=args.device,
            cpu_threads=args.cpu_threads,
            vad=args.vad,
        )
        if args.vad:
            stt_text += " (with vad filter)"
    else:
        stt = SpeechToTextWhisperTransformers(
            model_name=args.whisper_model,
            device=args.device,
            cpu_threads=args.cpu_threads,
        )
        if args.vad:
            logger().warning(
                "Vad filter is only supported in fasterwhisper Speech to Text library"
            )

    stt.load_model()
    source_language = args.source_language
    if not source_language:
        source_language = stt.detect_language(args.input_file)
        logger().info(f"Detected language '{source_language}'")

    translation = _get_selected_translator(
        args.translator, args.nllb_model, args.apertium_server, args.device
    )

    check_languages(
        source_language,
        args.target_language,
        tts,
        translation,
        stt,
        args.target_language_region,
    )

    if not os.path.exists(args.output_directory):
        os.makedirs(args.output_directory)

    dubber = Dubber(
        input_file=args.input_file,
        output_directory=args.output_directory,
        source_language=source_language,
        target_language=args.target_language,
        target_language_region=args.target_language_region,
        hugging_face_token=hugging_face_token,
        tts=tts,
        translation=translation,
        stt=stt,
        device=args.device,
        device_pyannote=args.device_pyannote,
        cpu_threads=args.cpu_threads,
        clean_intermediate_files=args.clean_intermediate_files,
        original_subtitles=args.original_subtitles,
        dubbed_subtitles=args.dubbed_subtitles,
        input_srt=args.input_srt,
    )

    logger().info(
        f"Processing '{args.input_file}' file with stt '{stt_text}', tts '{args.tts}' and device '{args.device}'"
    )
    if args.update:
        dubber.update()
    else:
        dubber.dub()


if __name__ == "__main__":
    main()
