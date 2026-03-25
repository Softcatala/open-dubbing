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

from enum import IntEnum


class ExitCode(IntEnum):
    INVALID_LANGUAGE_SPT = 100
    INVALID_LANGUAGE_TRANS = 101
    INVALID_LANGUAGE_TTS = 102
    INVALID_FILEFORMAT = 103
    MISSING_HF_KEY = 104
    NO_FFMPEG = 105
    NO_COQUI_TTS = 106
    NO_COQUI_ESPEAK = 107
    NO_CLI_CFG_FILE = 108
    NO_APERTIUM_SERVER = 109
    NO_TTS_API_SERVER = 110
    UPDATE_MISSING_FILES = 111
    NO_OPENAI_TTS = 112
    NO_OPENAI_KEY = 113
    NO_CAMB_KEY = 114
