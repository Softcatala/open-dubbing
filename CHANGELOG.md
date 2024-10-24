# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.0.9]

### Added
- Support for TTS which implement an API contract (allows your own TTS)
- Error values to control externally why open-dubbing is exiting (see exit_code.py)

### Fixed
- Do not need to merge back audios that have not been dubbed
- If a file merge file fails, do not fail the whole batch

## [0.0.8]

### Added
- Allow to pass the select device to an external TTS activated by cli
- Coqui as optional dependency
- Allow to select logging level
- Updated dependencies

## [0.0.7]

### Added
- Support for any TTS which can be invoked from the command line

## [0.0.6]

### Added
- Support for building in Windows. Tests pass.
- Allow to define region for target language (like ES-MX) used for TTS

## [0.0.5]

### Added

- Only speed audios when it's really needed improving quality of final audio synthesis
- Support for Apertium API as translation engine
- Allow to select between different model sizes for NLLB translation engine
- Allow to select between different model sizes for Whisper speech to text engine

## [0.0.4]

### Added

- Check if ffmpeg is installed and report if it is not

## [0.0.3]

### Added

- Autodetect language using Whisper if source language is not specified
- Use Edge TTS native speed parameter when need to increase the speed
- Better performance when separating vocals

## [0.0.2]

### Added

- Support for Microsoft Edge TTS
- Gender classifier to identify gender in the original video and produce the synthetic voices in target language that match the gender

## [0.0.1]

### Added
- Initial version
