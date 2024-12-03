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

from unittest.mock import patch

import pytest

from open_dubbing.command_line import CommandLine


class TestCommandLine:

    def test_test_input_file(self):
        with patch(
            "sys.argv",
            [
                "program_name",
                "--input_file",
                "test video.mp4",
                "--output_directory",
                "test_output",
                "--target_language",
                "fra",
            ],
        ):
            args = CommandLine.read_parameters()

            assert args.input_file == "test video.mp4"
            assert args.output_directory == "test_output"
            assert args.target_language == "fra"

    def test_missing_required_argument(self):
        with patch(
            "sys.argv",
            [
                "program_name",
                "--output_directory",
                "test_output",
                "--target_language",
                "fra",
            ],
        ), pytest.raises(SystemExit):
            CommandLine.read_parameters()
            assert False  # should not arrive here
