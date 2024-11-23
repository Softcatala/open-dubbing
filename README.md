[![PyPI version](https://img.shields.io/pypi/v/open-dubbing.svg?logo=pypi&logoColor=FFE873)](https://pypi.org/project/open-dubbing/)
[![PyPI downloads](https://img.shields.io/pypi/dm/open-dubbing.svg)](https://pypistats.org/packages/open-dubbing)
[![codecov](https://codecov.io/github/softcatala/open-dubbing/graph/badge.svg?token=TI6SIB9SGK)](https://codecov.io/github/softcatala/open-dubbing)

# Introduction

Open dubbing is an AI dubbing system uses machine learning models to automatically translate and synchronize audio dialogue into different languages.
It is designed as a command line tool.

At the moment, it is pure *experimental* and an excuse to help me to understand better STT, TTS and translation systems combined together.

# Features

* Build on top of open source models and able to run it locally
* Dubs automatically a video from a source to a target language
* Supports multiple Text To Speech (TTS): Coqui, MMS, Edge
 * Allows to use any non-supported one by configuring an API or CLI
* Gender voice detection to allow to assign properly synthetic voice
* Support for multiple translation engines (Meta's NLLB, Apertium API, etc)
* Automatic detection of the source language of the video (using Whisper)

# Roadmap

Areas what we will like to explore:

* Better control of voice used for dubbing
* Optimize it for long videos and less resource usage
* Support for multiple video input formats

# Demo

This video on propose shows the strengths and limitations of the system.

*Original English video*

https://github.com/user-attachments/assets/54c0d37f-0cc8-4ea2-8f8d-fd2d2f4eeccc

*Automatic dubbed video in Catalan*


https://github.com/user-attachments/assets/99936655-5851-4d0c-827b-f36f79f56190


# Limitations

* This is an experimental project
* Automatic video dubbing includes speech recognition, translation, vocal recognition, etc. At each one of these steps errors can be introduced

# Supported languages

The support languages depends on the combination of text to speech, translation system and text to speech system used. With Coqui TTS, these are the languages supported (I only tested a very few of them):

Supported source languages: Afrikaans, Amharic, Armenian, Assamese, Bashkir, Basque, Belarusian, Bengali, Bosnian, Bulgarian, Burmese, Catalan, Chinese, Croatian, Czech, Danish, Dutch, English, Estonian, Faroese, Finnish, French, Galician, Georgian, German, Gujarati, Haitian, Hausa, Hebrew, Hindi, Hungarian, Icelandic, Indonesian, Italian, Japanese, Javanese, Kannada, Kazakh, Khmer, Korean, Lao, Lingala, Lithuanian, Luxembourgish, Macedonian, Malayalam, Maltese, Maori, Marathi, Modern Greek (1453-), Norwegian Nynorsk, Occitan (post 1500), Panjabi, Polish, Portuguese, Romanian, Russian, Sanskrit, Serbian, Shona, Sindhi, Sinhala, Slovak, Slovenian, Somali, Spanish, Sundanese, Swedish, Tagalog, Tajik, Tamil, Tatar, Telugu, Thai, Tibetan, Turkish, Turkmen, Ukrainian, Urdu, Vietnamese, Welsh, Yoruba, Yue Chinese

Supported target languages: Achinese, Akan, Amharic, Assamese, Awadhi, Ayacucho Quechua, Balinese, Bambara, Bashkir, Basque, Bemba (Zambia), Bengali, Bulgarian, Burmese, Catalan, Cebuano, Central Aymara, Chhattisgarhi, Crimean Tatar, Dutch, Dyula, Dzongkha, English, Ewe, Faroese, Fijian, Finnish, Fon, French, Ganda, German, Guarani, Gujarati, Haitian, Hausa, Hebrew, Hindi, Hungarian, Icelandic, Iloko, Indonesian, Javanese, Kabiyè, Kabyle, Kachin, Kannada, Kazakh, Khmer, Kikuyu, Kinyarwanda, Kirghiz, Korean, Lao, Magahi, Maithili, Malayalam, Marathi, Minangkabau, Modern Greek (1453-), Mossi, North Azerbaijani, Northern Kurdish, Nuer, Nyanja, Odia, Pangasinan, Panjabi, Papiamento, Polish, Portuguese, Romanian, Rundi, Russian, Samoan, Sango, Shan, Shona, Somali, South Azerbaijani, Southwestern Dinka, Spanish, Sundanese, Swahili (individual language), Swedish, Tagalog, Tajik, Tamasheq, Tamil, Tatar, Telugu, Thai, Tibetan, Tigrinya, Tok Pisin, Tsonga, Turkish, Turkmen, Uighur, Ukrainian, Urdu, Vietnamese, Waray (Philippines), Welsh, Yoruba

# Installation

To install the open_dubbing in all platforms:

```shell
pip install open_dubbing
```

If you want to install also Coqui-tts, do:

```shell
pip install open_dubbing[coqui]
```

## Linux additional dependencies

In Linux you also need to install:

```shell
sudo apt install ffmpeg
```

If you are going to use Coqui-tts you also need to install espeak-ng:

```shell
sudo apt install espeak-ng
```

## macOS additional dependencies

In macOS you also need to install:

```shell
brew install ffmpeg
```

If you are going to use Coqui-tts you also need to install espeak-ng:

```shell
brew install espeak-ng
```

## Windows additional dependencies

Windows currently works but it has not been tested extensively.

You also need to install [ffmpeg](https://www.ffmpeg.org/download.html) for Windows. Make sure that is the system path.

## Accept pyannote license

1. Go to and Accept [`pyannote/segmentation-3.0`](https://hf.co/pyannote/segmentation-3.0) user conditions
2. Accept [`pyannote/speaker-diarization-3.1`](https://hf.co/pyannote/speaker-diarization-3.1) user conditions
3. Go to and access token at [`hf.co/settings/tokens`](https://hf.co/settings/tokens).

# Quick start

Quick start

```shell
 open-dubbing --input_file video.mp4 --target_language=cat --hugging_face_token=TOKEN
```

Where:
- _TOKEN_ is the HuggingFace token that allows to access the models
- _cat_ in this case is the target language using iso ISO 639-3 language codes

By default, the source language is predicted using the first 30 seconds of the video. If this does not work (e.g. there is only music at the beginning), use the parameter _source_language_ to specify the source language using ISO 639-3 language codes (e.g. 'eng' for English).

To get a list of available options:

```shell
open-dubbing --help

```
# Post editing automatic generated dubbed files

There are cases where you want to manually adjust the text generated automatically for dubbing, the voice used or the timings.

After you have executed _open-dubbing_ you have the intermediate files and the outcome dubbed file in the selected output directory.

You can edit the file _utterance_metadata_XXX.json_ (where XXX is the target language code), make manual adjustments, and generate the video again.

See an example JSON:

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
            "translated_text": **"I m'encanta aquesta ciutat."**,
            "assigned_voice": "ca-ES-EnricNeural",
            "speed": 1.3,
            "dubbed_path": "short/dubbed_chunk_7.607843750000001_8.687843750000003.mp3",
            "hash": "b11d7f0e2aa5475e652937469d89ef0a178fecea726f076095942d552944089f"
        },
```

Imagine that you have changed the **translated_text**. To generated the post-edited video:

```shell
 open-dubbing --input_file video.mp4 --target_language=cat --hugging_face_token=TOKEN --update
```

The _update_ parameter changes the behavior of _open-dubbing_ and instead of producing a full dubbing it rebuilds the already existing dubbing incorporating any change made into the JSON file.

Fields that are usefull to modify are: translated_text, gender (of the voice) or speed.

# Documentation

For more detailed documentation on how the tool works and how to use it, see our [documentation page](./DOCUMENTATION.md).

# Appreciation

Core libraries used:
* [demucs](https://github.com/facebookresearch/demucs) to separate vocals from the audio
* [pyannote-audio](https://github.com/pyannote/pyannote-audio) to diarize speakers
* [faster-whisper](https://github.com/SYSTRAN/faster-whisper) for audio to speech
* [NLLB-200](https://github.com/facebookresearch/fairseq/tree/nllb) for machine translation
* TTS
  * [coqui-tts](https://github.com/idiap/coqui-ai-TTS)
  * Meta [mms](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)
  * Microsoft [Edge TTS](https://github.com/rany2/edge-tts)

And very special thanks to [ariel](https://github.com/google-marketing-solutions/ariel) from which we leveraged parts of their code base.

# License

See [license](./LICENSE)

# Contact

Email address: Jordi Mas: jmas@softcatala.org
