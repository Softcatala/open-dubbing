# Open Dubbing 🚀
### Lokalny system AI do automatycznego dubbingu wideo

> Open dubbing tłumaczy i synchronizuje dialog z wideo na inny język modelem STT, translacji i TTS. Cały pipeline da się odpalić lokalnie, z CLI albo z Web UI.

---

<p align="center">

<img src="https://img.shields.io/github/stars/SQ2MTG/open-dubbing?style=for-the-badge" />
<img src="https://img.shields.io/github/forks/SQ2MTG/open-dubbing?style=for-the-badge" />
<img src="https://img.shields.io/github/issues/SQ2MTG/open-dubbing?style=for-the-badge" />
<img src="https://img.shields.io/github/license/SQ2MTG/open-dubbing?style=for-the-badge" />

<br/>

[![PyPI version](https://img.shields.io/pypi/v/open-dubbing.svg?logo=pypi&logoColor=FFE873)](https://pypi.org/project/open-dubbing/)
[![PyPI downloads](https://img.shields.io/pypi/dm/open-dubbing.svg)](https://pypistats.org/packages/open-dubbing)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![codecov](https://codecov.io/github/softcatala/open-dubbing/graph/badge.svg?token=TI6SIB9SGK)](https://codecov.io/github/softcatala/open-dubbing)

</p>

<p align="center">
  <strong>Wersja pakietu:</strong> 0.2.3 &nbsp;·&nbsp;
  <strong>CLI:</strong> <code>open-dubbing</code> &nbsp;·&nbsp;
  <strong>Web UI:</strong> <code>http://localhost:8000</code>
</p>

---

## 📖 Description

Open dubbing is an AI dubbing system which uses machine learning models to automatically translate and synchronize audio dialogue into different languages. It is designed as a command line tool, with an additional Web UI for upload, engine selection and progress.

At the moment, it is pure *experimental* and an excuse to understand STT, TTS and translation systems combined together.

_If you want to see a live system running you can do it at [https://www.softcatala.org/doblatge/](https://www.softcatala.org/doblatge/) (accepts only English and Spanish and dubs only to Catalan). It combines this project, [subdub-editor](https://github.com/Softcatala/subdub-editor) (an editor) and [dubbing-service](https://github.com/Softcatala/dubbing-service) (web service)._

Pipeline:

1. FFmpeg wyciąga audio ze źródłowego wideo.
2. Demucs oddziela wokal od tła.
3. pyannote diarizuje mówców, a klasyfikator płci przypisuje głos syntetyczny.
4. faster-whisper (albo Whisper przez Transformers) robi STT i wykrywa język źródłowy z pierwszych 30 sekund.
5. NLLB-200 albo Apertium tłumaczy wypowiedzi (kody ISO 639-3).
6. TTS (Edge, MMS, Coqui, OpenAI albo własny API/CLI) generuje dubbing dopasowany czasowo.
7. Ścieżka jest składana z powrotem do wideo. Po drodze powstaje `utterance_metadata_<lang>.json` do ręcznej korekty.

Upstream: [Softcatala/open-dubbing](https://github.com/Softcatala/open-dubbing). Ten fork trzyma SQ2MTG.

---

## ✨ Features

- ✅ Zbudowany na otwartych modelach, da się odpalić lokalnie
- ✅ Automatyczny dubbing wideo ze źródła na język docelowy
- ✅ Wiele silników TTS: Coqui, MMS, Edge, OpenAI TTS
- ✅ Dowolny nieobsługiwany TTS przez własne API albo CLI
- ✅ Detekcja płci głosu, żeby przypisać właściwy głos syntetyczny
- ✅ Wiele silników translacji (Meta NLLB, Apertium API i inne)
- ✅ Automatyczne wykrywanie języka źródłowego (Whisper)
- ✅ CLI (`open-dubbing`) i Web UI (upload, logi, pobranie wyniku)
- ✅ Docker / Podman, CPU albo CUDA
- ✅ Post-editing: `--update` przebudowuje dubbing po ręcznej edycji JSON

---

## 🎬 Demo

This video on purpose shows the strengths and limitations of the system.

*Original English video*

https://github.com/user-attachments/assets/54c0d37f-0cc8-4ea2-8f8d-fd2d2f4eeccc

*Automatic dubbed video in Catalan*

https://github.com/user-attachments/assets/99936655-5851-4d0c-827b-f36f79f56190

Lokalne sample: `samples/jobinterview.mp4`, `samples/dubbed_video_cat.mp4`.

---

## ⚠️ Limitations

- This is an experimental project
- Automatic video dubbing includes speech recognition, translation, vocal recognition, etc. At each one of these steps errors can be introduced

---

## 🛠️ Technologies & Tools

<p align="center">

<img src="https://skillicons.dev/icons?i=python,bash,linux,docker,pytorch,fastapi,html,css,git,github,vscode"/>

</p>

| Warstwa | Narzędzie |
|---------|-----------|
| STT | faster-whisper, Whisper (Transformers) |
| Separacja wokalu | Demucs |
| Diarization | pyannote.audio |
| Translacja | NLLB-200, Apertium API |
| TTS | Edge TTS, Meta MMS, Coqui TTS, OpenAI TTS, własne API/CLI |
| Audio / wideo | FFmpeg, MoviePy |
| Runtime | Python ≥ 3.10 (testowane 3.11–3.13), PyTorch, CUDA opcjonalnie |
| UI | Web UI na porcie 8000 |

Szczegóły: [DOCUMENTATION.md](./DOCUMENTATION.md).

---

## 🌍 Supported languages

The supported languages depend on the combination of speech-to-text, translation system and text-to-speech system used. With Coqui TTS, these are the languages supported (only a very few of them have been tested):

**Supported source languages:** Afrikaans, Amharic, Armenian, Assamese, Bashkir, Basque, Belarusian, Bengali, Bosnian, Bulgarian, Burmese, Catalan, Chinese, Croatian, Czech, Danish, Dutch, English, Estonian, Faroese, Finnish, French, Galician, Georgian, German, Gujarati, Haitian, Hausa, Hebrew, Hindi, Hungarian, Icelandic, Indonesian, Italian, Japanese, Javanese, Kannada, Kazakh, Khmer, Korean, Lao, Lingala, Lithuanian, Luxembourgish, Macedonian, Malayalam, Maltese, Maori, Marathi, Modern Greek (1453-), Norwegian Nynorsk, Occitan (post 1500), Panjabi, Polish, Portuguese, Romanian, Russian, Sanskrit, Serbian, Shona, Sindhi, Sinhala, Slovak, Slovenian, Somali, Spanish, Sundanese, Swedish, Tagalog, Tajik, Tamil, Tatar, Telugu, Thai, Tibetan, Turkish, Turkmen, Ukrainian, Urdu, Vietnamese, Welsh, Yoruba, Yue Chinese

**Supported target languages:** Achinese, Akan, Amharic, Assamese, Awadhi, Ayacucho Quechua, Balinese, Bambara, Bashkir, Basque, Bemba (Zambia), Bengali, Bulgarian, Burmese, Catalan, Cebuano, Central Aymara, Chhattisgarhi, Crimean Tatar, Dutch, Dyula, Dzongkha, English, Ewe, Faroese, Fijian, Finnish, Fon, French, Ganda, German, Guarani, Gujarati, Haitian, Hausa, Hebrew, Hindi, Hungarian, Icelandic, Iloko, Indonesian, Javanese, Kabiyè, Kabyle, Kachin, Kannada, Kazakh, Khmer, Kikuyu, Kinyarwanda, Kirghiz, Korean, Lao, Magahi, Maithili, Malayalam, Marathi, Minangkabau, Modern Greek (1453-), Mossi, North Azerbaijani, Northern Kurdish, Nuer, Nyanja, Odia, Pangasinan, Panjabi, Papiamento, Polish, Portuguese, Romanian, Rundi, Russian, Samoan, Sango, Shan, Shona, Somali, South Azerbaijani, Southwestern Dinka, Spanish, Sundanese, Swahili (individual language), Swedish, Tagalog, Tajik, Tamasheq, Tamil, Tatar, Telugu, Thai, Tibetan, Tigrinya, Tok Pisin, Tsonga, Turkish, Turkmen, Uighur, Ukrainian, Urdu, Vietnamese, Waray (Philippines), Welsh, Yoruba

Kody języków: ISO 639-3 (`eng`, `pol`, `cat`, `spa`, …).

---

## 📂 Project Structure

```text
open-dubbing/
├── open_dubbing/          # pipeline: STT, TTS, translacja, diarization, FFmpeg
│   ├── main.py            # entrypoint CLI
│   ├── dubbing.py
│   ├── text_to_speech_*.py
│   ├── translation_*.py
│   └── speech_to_text_*.py
├── webui/                 # Web UI (upload, silniki, logi) — port 8000
├── tests/                 # testy jednostkowe
├── e2e-tests/             # testy end-to-end
├── samples/               # przykładowe wideo
├── .github/workflows/     # CI
├── Dockerfile
├── docker-compose.yml
├── DOCUMENTATION.md
├── DOCKER.md
├── CHANGELOG.md
└── README.md
```

---

## ⚙️ Installation

To install open_dubbing on all platforms:

```shell
pip install open_dubbing
```

Coqui TTS:

```shell
pip install open_dubbing[coqui]
```

OpenAI:

```shell
pip install open_dubbing[openai]
```

Ze źródeł:

```bash
git clone https://github.com/SQ2MTG/open-dubbing.git
cd open-dubbing

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
pip install -e ".[dev]"
```

### Linux additional dependencies

```shell
sudo apt install ffmpeg
```

Coqui TTS additionally needs espeak-ng:

```shell
sudo apt install espeak-ng
```

### macOS additional dependencies

```shell
brew install ffmpeg
```

Coqui TTS:

```shell
brew install espeak-ng
```

### Windows additional dependencies

Windows currently works but it has not been tested extensively.

You also need to install [ffmpeg](https://www.ffmpeg.org/download.html) for Windows. Make sure it is on the system path.

### Accept pyannote license

1. Accept [`pyannote/segmentation-3.0`](https://hf.co/pyannote/segmentation-3.0) user conditions
2. Accept [`pyannote/speaker-diarization-3.1`](https://hf.co/pyannote/speaker-diarization-3.1) user conditions
3. Create an access token at [`hf.co/settings/tokens`](https://hf.co/settings/tokens)

---

## 🚀 Usage

```shell
open-dubbing --input_file video.mp4 --target_language=cat --hugging_face_token=TOKEN
```

Where:

- _TOKEN_ is the Hugging Face token that allows access to the models
- _cat_ is the target language using ISO 639-3 language codes

By default, the source language is predicted using the first 30 seconds of the video. If this does not work (for example there is only music at the beginning), use `--source_language` with an ISO 639-3 code (for example `eng` for English).

```shell
open-dubbing --help
```

Polski przykład:

```shell
open-dubbing --input_file video.mp4 --source_language=eng --target_language=pol --hugging_face_token=TOKEN
```

---

## 🔧 Configuration

Skopiuj `.env.example` do `.env`:

```env
# Hugging Face API token (required)
# https://huggingface.co/settings/tokens
HF_TOKEN=hf_your_token_here

# OpenAI API key (optional, only for OpenAI TTS)
OPENAI_API_KEY=sk_your_key_here
```

CLI przyjmuje token też jako `--hugging_face_token`. Źródło języka, język docelowy, silnik TTS i silnik translacji ustawiasz flagami (`open-dubbing --help`) albo w formularzu Web UI.

---

## ✏️ Post editing automatic generated dubbed files

There are cases where you want to manually adjust the text generated automatically for dubbing, the voice used or the timings.

After you have executed `open-dubbing` you have the intermediate files and the outcome dubbed file in the selected output directory.

You can edit the file `utterance_metadata_XXX.json` (where XXX is the target language code), make manual adjustments, and generate the video again.

Example JSON:

```json
"utterances": [
    {
        "start": 7.607843750000001,
        "end": 8.687843750000003,
        "speaker_id": "SPEAKER_00",
        "path": "short/chunk_7.607843750000001_8.687843750000003.mp3",
        "text": "And I love this city.",
        "for_dubbing": true,
        "gender": "Male",
        "translated_text": "I m'encanta aquesta ciutat.",
        "assigned_voice": "ca-ES-EnricNeural",
        "speed": 1.3,
        "dubbed_path": "short/dubbed_chunk_7.607843750000001_8.687843750000003.mp3",
        "hash": "b11d7f0e2aa5475e652937469d89ef0a178fecea726f076095942d552944089f"
    }
]
```

Imagine that you have changed the **translated_text**. To generate the post-edited video:

```shell
open-dubbing --input_file video.mp4 --target_language=cat --hugging_face_token=TOKEN --update
```

The `--update` parameter changes the behavior of `open-dubbing`: instead of producing a full dubbing it rebuilds the already existing dubbing, incorporating any change made in the JSON file.

Fields that are useful to modify: `translated_text`, `gender` (of the voice), `speed`.

---

## 🌐 Web Interface

Po `docker compose up` UI jest na `http://localhost:8000`. Szczegóły: [DOCKER.md](./DOCKER.md).

| Funkcja | Opis |
|---------|------|
| Video upload | Drag & drop albo wybór pliku MP4 |
| Language selection | Źródło i cel, kody ISO 639-3 |
| TTS engine | MMS, Edge, OpenAI, Coqui |
| Translation engine | NLLB albo Apertium |
| Device | CPU albo CUDA |
| Real-time output | Logi i wygenerowane pliki do pobrania |

Wyniki lądują w `./data/output/` na hoście.

---

## 🐳 Docker

```bash
cp .env.example .env
# uzupełnij HF_TOKEN
docker compose up --build
```

```yaml
services:
  open-dubbing:
    build: .
    ports:
      - "8000:8000"
    environment:
      HF_TOKEN: ${HF_TOKEN:-}
      OPENAI_API_KEY: ${OPENAI_API_KEY:-}
    volumes:
      - .:/app
      - ./data:/app/data
    restart: unless-stopped
```

Podman: `podman-compose up --build`. GPU wymaga NVIDIA Container Runtime i sensownej VRAM (orientacyjnie od 8 GB). Port zajęty — zmień mapowanie w `docker-compose.yml`.

---

## 📈 Roadmap

Areas we would like to explore:

- [ ] Better control of the voice used for dubbing
- [ ] Optimize for long videos and lower resource usage
- [ ] Support for multiple video input formats

---

## 🙏 Appreciation

Core libraries used:

- [demucs](https://github.com/adefossez/demucs) to separate vocals from the audio
- [pyannote-audio](https://github.com/pyannote/pyannote-audio) to diarize speakers
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) for speech to text
- [NLLB-200](https://github.com/facebookresearch/fairseq/tree/nllb) for machine translation
- TTS
  - [coqui-tts](https://github.com/idiap/coqui-ai-TTS)
  - Meta [mms](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)
  - Microsoft [Edge TTS](https://github.com/rany2/edge-tts)
  - [OpenAI TTS](https://platform.openai.com/docs/guides/text-to-speech)

And very special thanks to [ariel](https://github.com/google-marketing-solutions/ariel), from which parts of the code base were leveraged.

---

## 🤝 Contributing

Pull requests are welcome.

For major changes:

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Open a Pull Request

Testy: `pytest`. Lint z extra `dev` (`flake8`, `black`, `isort`).

---

## 📜 License

Apache License 2.0. See [LICENSE](./LICENSE).

---

## 👨‍💻 Author

Oryginalny autor: Jordi Mas — [jmas@softcatala.org](mailto:jmas@softcatala.org) · [Softcatalà](https://github.com/Softcatala/open-dubbing)

Fork:

- Callsign: **SQ2MTG**
- GitHub: https://github.com/SQ2MTG

---

## ⭐ Support

If you like this project:

- ⭐ Star the repository
- 🍴 Fork the project
- 📢 Share it with others

---

<p align="center">
  Made with ❤️ by SQ2MTG · upstream Softcatalà
</p>
