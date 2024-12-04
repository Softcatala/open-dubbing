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

import os
import shutil
import tempfile

from unittest.mock import MagicMock, patch

from open_dubbing.ffmpeg import FFmpeg


class TestFFmpeg:

    def _get_lines_from_file(self, filename):
        with open(filename, "r") as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
        return lines

    def _get_srt(self):
        return [
            "1",
            "00:00:01,262 --> 00:00:03,945",
            "Bon dia, el meu nom és Jordi Mas.",
            "",
            "2",
            "00:00:05,245 --> 00:00:06,629",
            "Sóc de Barcelona.",
            "",
        ]

    def _get_copied_tmp_mp4(self):
        mp4_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        directory = os.path.dirname(os.path.realpath(__file__))
        video_file = os.path.join(directory, "data/englishvideo.mp4")
        shutil.copyfile(video_file, mp4_file.name)
        return mp4_file

    def _get_write_srt_test(self):
        srt_file_fh = tempfile.NamedTemporaryFile(suffix=".srt", delete=False, mode="w")
        # Write subtitles
        for line in self._get_srt():
            srt_file_fh.write(f"{line}\n")

        srt_file_fh.close()
        return srt_file_fh

    def _read_str_from_video(self, filename):
        tmp_srt = tempfile.NamedTemporaryFile(suffix=".srt", delete=False, mode="w")

        cmd = f"ffmpeg -y -i {filename} -map 0:s:0 {tmp_srt.name}"
        os.system(cmd)

        return self._get_lines_from_file(tmp_srt.name)

    def test_embed_subtitles(self):
        tmp_mp4_file = self._get_copied_tmp_mp4()
        tmp_str_test = self._get_write_srt_test()

        FFmpeg().embed_subtitles(
            video_file=tmp_mp4_file.name,
            subtitles_files=[tmp_str_test.name],
            languages_iso_639_3=["cat"],
        )

        subtitles = self._read_str_from_video(tmp_mp4_file.name)

        [os.remove(f) for f in [tmp_mp4_file.name, tmp_str_test.name]]
        expected = self._get_srt()
        assert subtitles == expected

    @patch("subprocess.run")
    def test_is_ffmpeg_installed(self, mock_subprocess):
        # Test when ffmpeg is installed
        mock_subprocess.return_value = MagicMock(returncode=0)
        assert FFmpeg.is_ffmpeg_installed()

    @patch("subprocess.run")
    def test_is_ffmpeg_not_installed(self, mock_subprocess):
        mock_subprocess.side_effect = FileNotFoundError()
        assert not FFmpeg.is_ffmpeg_installed()

    @patch("subprocess.run")
    def test_is_ffmpeg_exe_error(self, mock_subprocess):
        mock_subprocess.return_value = MagicMock(returncode=1)
        assert not FFmpeg.is_ffmpeg_installed()
