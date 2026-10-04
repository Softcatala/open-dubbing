# Copyright 2024 Softcatala
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

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
OUTPUT_DIR = BASE_DIR / "data" / "output"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_job_name(name: str) -> str:
    """Sanitize filename to use as job directory name."""
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip(".-")
    return slug or "job"


def list_outputs(directory: Path) -> list[str]:
    """List all output files in the job directory."""
    if not directory.exists():
        return []
    files = []
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            files.append(path.relative_to(directory).as_posix())
    return files


@app.route("/", methods=["GET"])
def index():
    """Render the main page."""
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    """Process a video upload and run the dubbing pipeline."""
    uploaded_file = request.files.get("video")
    if uploaded_file is None or not uploaded_file.filename:
        return "Missing video input.", 400

    target_language = (request.form.get("target_language") or "").strip()
    if not target_language:
        return "Target language is required.", 400

    source_language = (request.form.get("source_language") or "").strip()
    hf_token = (request.form.get("hugging_face_token") or "").strip()
    tts = request.form.get("tts", "mms")
    translator = request.form.get("translator", "nllb")
    device = request.form.get("device", "cpu")

    # Save uploaded file
    original_name = secure_filename(uploaded_file.filename)
    upload_path = UPLOAD_DIR / original_name
    uploaded_file.save(upload_path)

    # Create output directory
    job_slug = sanitize_job_name(Path(original_name).stem)
    job_dir = OUTPUT_DIR / job_slug
    job_dir.mkdir(parents=True, exist_ok=True)

    # Build command
    cmd = [
        "open-dubbing",
        "--input_file",
        str(upload_path),
        "--output_directory",
        str(job_dir),
        "--target_language",
        target_language,
    ]

    if source_language:
        cmd.extend(["--source_language", source_language])
    if hf_token:
        cmd.extend(["--hugging_face_token", hf_token])
    if tts and tts != "mms":
        cmd.extend(["--tts", tts])
    if translator and translator != "nllb":
        cmd.extend(["--translator", translator])
    if device and device != "cpu":
        cmd.extend(["--device", device])

    env = os.environ.copy()
    if hf_token:
        env["HF_TOKEN"] = hf_token

    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600,
            env=env,
            cwd=str(BASE_DIR),
        )
    except subprocess.TimeoutExpired as exc:
        return render_template(
            "index.html",
            result={
                "status": "error",
                "stdout": "",
                "stderr": f"Processing timed out after 3600 seconds.\n{exc}",
                "files": [],
                "command": " ".join(cmd),
            },
        )

    result = {
        "status": "success" if completed.returncode == 0 else "error",
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "files": list_outputs(job_dir),
        "command": " ".join(cmd),
    }
    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
