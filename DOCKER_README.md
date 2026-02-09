# Qwen3-TTS API Server

A high-performance FastAPI server for **Qwen2.5-Math-7B-Instruct** based Text-to-Speech models.
This server provides a RESTful API compatible with various TTS clients and supports voice cloning, voice design, and preset speakers.

## Features

- **High Performance**: Optimized with Flash Attention 2 and CUDA.
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

## API Endpoints

The server exposes the following main endpoints:

- `GET /health` - Server health check
- `POST /api/v1/cv/generate` - CustomVoice generation (Preset speakers)
- `POST /api/v1/vd/generate` - VoiceDesign generation (Description based)
- `POST /api/v1/base/generate` - Voice Cloning generation (Reference audio)

Full API documentation (Swagger UI) is available at `http://localhost:8000/docs` when running the container.

## Volumes

- `/app/models`: Mount this to persist downloaded models (saves bandwidth).
- `/app/output`: Mount this to access generated audio files directly.

## More Information

For source code, issues, and advanced configuration, visit the [GitHub Repository](https://github.com/linkary/qwen-tts-server).
