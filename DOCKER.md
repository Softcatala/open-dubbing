# Docker & Web UI Setup

This guide explains how to run Open Dubbing using Docker and the included Web UI.

## Prerequisites

- Docker and Docker Compose installed
- Hugging Face API token (get from https://huggingface.co/settings/tokens)
- Optional: OpenAI API key (only if using OpenAI TTS)

## Quick Start

1. **Clone and navigate to the repository:**
   ```bash
   git clone https://github.com/Softcatala/open-dubbing.git
   cd open-dubbing
   ```

2. **Create `.env` file with your tokens:**
   ```bash
   cp .env.example .env
   # Edit .env and add your HF_TOKEN and optional OPENAI_API_KEY
   ```

3. **Start the container:**
   ```bash
   docker compose up --build
   ```

4. **Open Web UI:**
   - Navigate to `http://localhost:8000` in your browser
   - Upload a video file
   - Configure options (target language, TTS engine, etc.)
   - Click "Start Dubbing"
   - Monitor progress and download results

## Web UI Features

- **Video Upload**: Drag & drop or select MP4 files
- **Language Selection**: Specify source and target languages (ISO 639-3 codes)
- **TTS Engine Selection**: Choose between MMS, Edge, OpenAI, or Coqui
- **Translation Engine**: Select NLLB or Apertium
- **Device Selection**: Use CPU or CUDA (GPU)
- **Real-time Output**: View processing logs and generated files

## Using Podman

If you prefer Podman instead of Docker:

```bash
podman-compose up --build
```

## Docker Volume Mounts

By default, docker-compose mounts:
- `.` (entire repo) → `/app` in container
- `./data` → `/app/data` for uploads and output

Generated files are saved to `./data/output/` on your host.

## Stopping the Container

```bash
docker compose down
```

To remove all data including volumes:

```bash
docker compose down -v
```

## Common Issues

### Port 8000 already in use
Edit `docker-compose.yml` and change the port mapping:
```yaml
ports:
  - "8080:8000"  # Use 8080 instead
```

### Out of memory
For large videos, you may need to increase Docker's memory limit in your Docker Desktop settings or pass memory limits in the compose file.

### GPU Support (CUDA)

To use GPU acceleration, ensure:
1. NVIDIA Docker runtime is installed
2. Your GPU has sufficient VRAM (at least 8GB recommended)
3. Set `device: cuda` in the web form or environment
