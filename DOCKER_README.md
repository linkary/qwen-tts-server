# Qwen3-TTS API Server

A FastAPI server for **Qwen3-TTS** based Text-to-Speech models.
This server provides a RESTful API compatible with various TTS clients and supports voice cloning, voice design, and preset speakers.

## Features

- **Multiple Models**: 
  - **CustomVoice**: 9 preset speakers with instruction control.
  - **VoiceDesign**: Create voices using natural language descriptions.
  - **Base**: Voice cloning from a 3-second reference audio.
- **Voice Cloning**: Support for cross-lingual voice cloning and reusable voice prompts.
- **Streaming**: Real-time audio streaming support via Server-Sent Events (SSE).
- **Docker Support**: Ready-to-use Docker images for GPU and CPU.

## Quick Start (Docker)

### Prerequisites

- **GPU Mode**: NVIDIA GPU with drivers installed + [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).
- **CPU Mode**: No special requirements (performance will be slower).

### Run with GPU (Recommended)

```bash
docker run -d \
  --name qwen-tts \
  --gpus all \
  -p 8000:8000 \
  -v ./models:/app/models \
  -v ./output:/app/output \
  linkary/qwen-tts-server:latest
```

### Run with CPU (No GPU)

```bash
docker run -d \
  --name qwen-tts \
  -p 8000:8000 \
  -e CUDA_DEVICE=cpu \
  -v ./models:/app/models \
  -v ./output:/app/output \
  linkary/qwen-tts-server:latest
```

## Configuration

You can configure the server using environment variables (`-e KEY=VALUE`).

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEYS` | `""` | Comma-separated list of API keys for authentication. |
| `CUDA_DEVICE` | `cuda:0` | GPU device to use (or `cpu`). |
| `MODEL_DTYPE` | `bfloat16` | Model precision (`float16`, `bfloat16`, `float32`). |
| `USE_FLASH_ATTENTION` | `true` | Enable Flash Attention 2 (GPU only). |
| `PRELOAD_MODELS` | `false` | Preload all models on startup (requires ~16GB VRAM). |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |

### Example with Auth & Config

```bash
docker run -d \
  --gpus all \
  -p 8000:8000 \
  -e API_KEYS="my-secret-key-123" \
  -e LOG_LEVEL="DEBUG" \
  -e PRELOAD_MODELS="true" \
  linkary/qwen-tts-server:latest
```

## API Usage (curl)

Once the container is running, generate speech with a single curl command:

```bash
# Text-to-Speech with a preset speaker
curl -X POST http://localhost:8000/api/v1/custom-voice/generate \
  -H "X-API-Key: my-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello from Docker! This is the Qwen 3 TTS server.",
    "language": "English",
    "speaker": "Ryan",
    "response_format": "wav"
  }' \
  --output hello.wav
```

```bash
# Text-to-Speech with a custom voice description
curl -X POST http://localhost:8000/api/v1/voice-design/generate \
  -H "X-API-Key: my-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Welcome to our broadcast.",
    "language": "English",
    "instruct": "A deep, calm male voice with a professional tone",
    "response_format": "wav"
  }' \
  --output broadcast.wav
```

> **Tip:** If `API_KEYS` is not set, omit the `-H "X-API-Key: ..."` header.

## API Endpoints

The server exposes the following main endpoints:

- `GET /health` — Server health check
- `GET /health/models` — Check loaded models
- `POST /api/v1/custom-voice/generate` — Preset speaker TTS
- `POST /api/v1/voice-design/generate` — Natural language voice design TTS
- `POST /api/v1/base/clone` — Voice cloning from reference audio

Full API documentation (Swagger UI) is available at `http://localhost:8000/docs` when running the container.

## Volumes

- `/app/models`: Mount this to persist downloaded models (saves bandwidth).
- `/app/output`: Mount this to access generated audio files directly.

## More Information

For source code, issues, and advanced configuration, visit the [GitHub Repository](https://github.com/linkary/qwen-tts-server).
