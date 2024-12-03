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

import json
import logging
import urllib

from open_dubbing.translation import Translation


class TranslationApertium(Translation):

    def load_model(self):
        pass

    def set_server(self, server):
        if not server.endswith("/"):
            server = server + "/"

        self.server = server

    def _do_api_call(self, url):
        response = urllib.request.urlopen(url)
        r = response.read().decode("utf-8")
        data = json.loads(r)
        return data["responseData"]

    def _translate_text(
        self, source_language: str, target_language: str, text: str
    ) -> str:

        langpair = f"{source_language}|{target_language}"
        text = urllib.parse.quote_plus(text.encode("utf-8"))
        method = "translate"
        url = f"{self.server}{method}?q={text}&langpair={langpair}&markUnknown=no"
        translated = self._do_api_call(url)
        translated = translated["translatedText"]
        return translated.rstrip()

    def get_language_pairs(self):
        method = "listPairs"
        url = f"{self.server}{method}"

        pairs = self._do_api_call(url)
        results = set()
        for pair in pairs:
            source = pair["sourceLanguage"]
            target = pair["targetLanguage"]
            if len(source) != 3 or len(target) != 3:
                logging.warning(
                    f"Discarding Apertium language pair: '{source}-{target}'"
                )
                continue

            pair = (pair["sourceLanguage"], pair["targetLanguage"])
            results.add(pair)

        return results
