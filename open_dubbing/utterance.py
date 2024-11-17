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

import dataclasses
import hashlib
import json
import logging
import os
import shutil
import tempfile

from typing import Final, List, Tuple

from open_dubbing.preprocessing import PreprocessingArtifacts


class Utterance:

    def __init__(self, target_language: str, output_directory: str):
        self.target_language = target_language
        self.output_directory = output_directory

    def _get_file_name(self):
        _UTTERNACE_METADATA_FILE_NAME: Final[str] = "utterance_metadata"

        target_language_suffix = "_" + self.target_language.replace("-", "_").lower()
        utterance_metadata_file = os.path.join(
            self.output_directory,
            _UTTERNACE_METADATA_FILE_NAME + target_language_suffix + ".json",
        )
        return utterance_metadata_file

    def load_utterances(self) -> tuple[str, str]:
        utterance_metadata_file = self._get_file_name()

        with open(utterance_metadata_file, "r") as file:
            data = json.load(file)
            utterance_metadata = data["utterances"]
            preprocesing_output = PreprocessingArtifacts(
                **data["PreprocessingArtifacts"]
            )

        return utterance_metadata, preprocesing_output

    def save_utterances(
        self,
        *,
        utterance_metadata: str,
        preprocesing_output: str,
        source_language: str,
        do_hash: bool = True,
        unique_id: bool = True,
    ) -> None:
        """Saves a Python dictionary to a JSON file.

        Returns:
          A path to the saved uttterance metadata.
        """
        utterance_metadata_file = self._get_file_name()

        try:
            all_data = {}
            if unique_id:
                utterance_metadata = self._add_unique_ids(utterance_metadata)

            if do_hash:
                utterance_metadata = self._hash_utterances(utterance_metadata)

            all_data["utterances"] = utterance_metadata
            if preprocesing_output:
                all_data["PreprocessingArtifacts"] = dataclasses.asdict(
                    preprocesing_output
                )
            all_data["source_language"] = source_language
            json_data = json.dumps(all_data, ensure_ascii=False, indent=4)
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, encoding="utf-8"
            ) as temporary_file:

                temporary_file.write(json_data)
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            shutil.copy(temporary_file.name, utterance_metadata_file)
            os.remove(temporary_file.name)
            logging.debug(
                "Utterance metadata saved successfully to"
                f" '{utterance_metadata_file}'"
            )
        except Exception as e:
            logging.warning(f"Error saving utterance metadata: {e}")
        self.save_utterance_metadata_output = utterance_metadata_file

    def _hash_utterances(self, utterance_metadata):
        for utterance in utterance_metadata:
            dict_str = json.dumps(utterance, sort_keys=True)
            _hash = hashlib.sha256(dict_str.encode()).hexdigest()
            utterance["hash"] = _hash

        return utterance_metadata

    def _add_unique_ids(self, utterance_metadata):
        for idx, utterance in enumerate(utterance_metadata, start=1):
            new_utterance = {"id": idx}
            new_utterance.update(utterance)
            utterance_metadata[idx - 1] = new_utterance

        return utterance_metadata

    def get_files_paths(self, utterance_metadata) -> Tuple[List[str], List[str]]:
        dubbed_paths = []
        paths = []
        for chunk in utterance_metadata:
            if "path" in chunk:
                paths.append(chunk["path"])
            if "dubbed_path" in chunk:
                dubbed_paths.append(chunk["dubbed_path"])

        return paths, dubbed_paths

    def get_modified_utterances(self, utterance_metadata):
        modified = []
        for utterance in utterance_metadata:
            _hash_utterance = utterance["hash"]
            del utterance["hash"]
            dict_str = json.dumps(utterance, sort_keys=True)

            _hash = hashlib.sha256(dict_str.encode()).hexdigest()
            if _hash_utterance != _hash:
                modified.append(utterance)

        logging.info(f"Modified {len(modified)} utterances")
        return modified

    def get_without_empty_blocks(self, utterance_metadata):
        new_utterance = []

        for utterance in utterance_metadata:
            text = utterance["text"]
            if len(text) == 0:
                logging.debug(f"Removing empty block: {utterance}")
                continue

            new_utterance.append(utterance)

        return new_utterance

    def update_utterances(self, utterance_master, utterance_update):
        id_to_update = {}
        utterance_new = []

        for utterance in utterance_update:
            id = utterance["id"]
            id_to_update[id] = utterance

        for utterance in utterance_master:
            id = utterance["id"]
            update = id_to_update.get(id, None)
            if not update:
                utterance_new.append(utterance)
                continue

            operation = update.get("operation", None)
            if not operation:
                raise ValueError("No operation field defined")

            if operation == "delete":
                continue

            if operation != "update":
                raise ValueError(f"Invalid operation {operation}")

            updateable_fields = [
                "speaker_id",
                "translated_text",
                "speed",
                "assigned_voice",
                "for_dubbing",
                "gender",
                "start",
                "end",
            ]
            for field in updateable_fields:
                value = update.get(field, None)
                if not value:
                    continue

                utterance[field] = value

            utterance_new.append(utterance)

        return utterance_new
