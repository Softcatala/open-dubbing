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

"""Tests for utility functions in video_processing.py."""

import os
import unittest

from unittest.mock import MagicMock, patch

from open_dubbing.video_processing import VideoProcessing


class TestVideoProcessing(unittest.TestCase):

    @patch("subprocess.run")
    def test_split_audio_video(self, mock_subprocess):
        # Mock subprocess.run to simulate ffmpeg execution without errors
        mock_subprocess.return_value = MagicMock(returncode=0)

        video_file = "sample_video.mp4"
        output_directory = "/tmp/output"
        expected_audio_file = os.path.join(output_directory, "sample_video_audio.mp3")
        expected_video_file = os.path.join(output_directory, "sample_video_video.mp4")

        # Call the method
        video_output, audio_output = VideoProcessing.split_audio_video(
            video_file=video_file, output_directory=output_directory
        )

        # Assert correct output
        self.assertEqual(video_output, expected_video_file)
        self.assertEqual(audio_output, expected_audio_file)

        # Assert subprocess was called with the correct command
        mock_subprocess.assert_called_once_with(
            [
                "ffmpeg",
                "-y",
                "-i",
                video_file,
                "-map",
                "0:a:0",
                "-b:a",
                "128K",
                expected_audio_file,
                "-map",
                "0:v:0",
                "-an",
                "-c:v",
                "copy",
                expected_video_file,
            ],
            check=True,
            stdout=unittest.mock.ANY,
            stderr=unittest.mock.ANY,
        )

    @patch("subprocess.run")
    def test_combine_audio_video(self, mock_subprocess):
        # Mock subprocess.run to simulate ffmpeg execution without errors
        mock_subprocess.return_value = MagicMock(returncode=0)

        video_file = "sample_video.mp4"
        dubbed_audio_file = "dubbed_audio.mp3"
        output_directory = "/tmp/output"
        target_language = "en-US"
        expected_output_file = os.path.join(output_directory, "dubbed_video_en_us.mp4")

        # Call the method
        output_file = VideoProcessing.combine_audio_video(
            video_file=video_file,
            dubbed_audio_file=dubbed_audio_file,
            output_directory=output_directory,
            target_language=target_language,
        )

        # Assert correct output
        self.assertEqual(output_file, expected_output_file)

        # Assert subprocess was called with the correct command
        mock_subprocess.assert_called_once_with(
            [
                "ffmpeg",
                "-y",
                "-i",
                video_file,
                "-i",
                dubbed_audio_file,
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                expected_output_file,
            ],
            check=True,
            stdout=unittest.mock.ANY,
            stderr=unittest.mock.ANY,
        )

    @patch("subprocess.run")
    def test_is_ffmpeg_installed(self, mock_subprocess):
        # Test when ffmpeg is installed
        mock_subprocess.return_value = MagicMock(returncode=0)
        assert VideoProcessing.is_ffmpeg_installed()

    @patch("subprocess.run")
    def test_is_ffmpeg_not_installed(self, mock_subprocess):
        mock_subprocess.side_effect = FileNotFoundError()
        assert not VideoProcessing.is_ffmpeg_installed()

    @patch("subprocess.run")
    def test_is_ffmpeg_exe_error(self, mock_subprocess):
        mock_subprocess.return_value = MagicMock(returncode=1)
        assert not VideoProcessing.is_ffmpeg_installed()
