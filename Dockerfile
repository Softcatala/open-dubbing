FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    espeak-ng \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY setup.py README.md ./
COPY open_dubbing ./open_dubbing
RUN pip install -e .

COPY webui/requirements.txt ./webui/
RUN pip install -r webui/requirements.txt

COPY webui ./webui

RUN mkdir -p /app/data/uploads /app/data/output

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "webui.app:app", "--workers", "1"]
