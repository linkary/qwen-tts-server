# Qwen3-TTS API Server

A production-ready FastAPI server for Qwen3-TTS models, supporting CustomVoice (preset speakers), VoiceDesign (natural language voice design), and Base models (voice cloning).

## Features

- **Multiple Model Support**: CustomVoice, VoiceDesign, and Base (voice cloning) models
- **Streaming & Batch Generation**: Real-time streaming or batch processing
- **API Key Authentication**: Secure access control
- **Docker Support**: Easy deployment with GPU support
- **Auto-generated Documentation**: Interactive API docs with Swagger UI
- **Lazy Model Loading**: Efficient memory usage by loading models on-demand
- **RESTful API**: Standard HTTP endpoints with JSON responses

## Quick Start

### Prerequisites

- Python 3.12 or higher
- NVIDIA GPU with CUDA support (recommended)
- At least 16GB GPU memory for 1.7B models
- Docker and docker-compose (for Docker deployment)

### Local Installation

1. **Clone the repository**

```bash
cd qwen-tts-server
```

2. **Create virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment**

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Start the server**

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or use the start script:

```bash
chmod +x start.sh
./start.sh
```

### Docker Installation

1. **Build and start with Docker Compose**

```bash
docker-compose up -d
```

2. **Check logs**

```bash
docker-compose logs -f
```

3. **Stop the server**

```bash
docker-compose down
```

## Configuration

Edit `.env` file to configure the server:

```bash
# Model Configuration
QWEN_TTS_CUSTOM_VOICE_MODEL=Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice
QWEN_TTS_VOICE_DESIGN_MODEL=Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign
QWEN_TTS_BASE_MODEL=Qwen/Qwen3-TTS-12Hz-1.7B-Base
QWEN_TTS_TOKENIZER=Qwen/Qwen3-TTS-Tokenizer-12Hz

# Device Configuration
CUDA_DEVICE=cuda:0
MODEL_DTYPE=bfloat16
USE_FLASH_ATTENTION=true

# API Configuration
API_KEYS=your-api-key-1,your-api-key-2,your-api-key-3
HOST=0.0.0.0
PORT=8000

# Model Caching
HF_HOME=/app/models
MODEL_CACHE_DIR=/app/models

# Logging
LOG_LEVEL=INFO

# Preload models on startup (requires more GPU memory)
PRELOAD_MODELS=false
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

### Health Check

#### `GET /health`
Basic health check

```bash
curl http://localhost:8000/health
```

#### `GET /health/models`
Check which models are loaded

```bash
curl http://localhost:8000/health/models
```

### CustomVoice API

#### `POST /api/v1/custom-voice/generate`
Generate speech with preset speakers

```bash
curl -X POST http://localhost:8000/api/v1/custom-voice/generate \
  -H "X-API-Key: your-api-key-1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test of the Qwen TTS system.",
    "language": "English",
    "speaker": "Ryan",
    "instruct": "Speak in a cheerful and energetic tone",
    "response_format": "wav"
  }' \
  --output output.wav
```

#### `POST /api/v1/custom-voice/generate-stream`
Stream generation with Server-Sent Events

```bash
curl -X POST http://localhost:8000/api/v1/custom-voice/generate-stream \
  -H "X-API-Key: your-api-key-1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is streaming audio generation.",
    "language": "English",
    "speaker": "Aiden"
  }'
```

#### `GET /api/v1/custom-voice/speakers`
List available speakers

```bash
curl http://localhost:8000/api/v1/custom-voice/speakers \
  -H "X-API-Key: your-api-key-1"
```

#### `GET /api/v1/custom-voice/languages`
List supported languages

```bash
curl http://localhost:8000/api/v1/custom-voice/languages \
  -H "X-API-Key: your-api-key-1"
```

### VoiceDesign API

#### `POST /api/v1/voice-design/generate`
Generate speech with natural language voice description

```bash
curl -X POST http://localhost:8000/api/v1/voice-design/generate \
  -H "X-API-Key: your-api-key-1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Welcome to the future of voice synthesis.",
    "language": "English",
    "instruct": "A warm, professional female voice with a slight British accent, speaking confidently and clearly",
    "response_format": "wav"
  }' \
  --output voice_design.wav
```

#### `POST /api/v1/voice-design/generate-stream`
Stream voice design generation

```bash
curl -X POST http://localhost:8000/api/v1/voice-design/generate-stream \
  -H "X-API-Key: your-api-key-1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Streaming with custom voice design.",
    "language": "English",
    "instruct": "Deep male voice, calm and soothing"
  }'
```

### Base Model (Voice Cloning) API

#### `POST /api/v1/base/clone`
Clone voice from reference audio

```bash
curl -X POST http://localhost:8000/api/v1/base/clone \
  -H "X-API-Key: your-api-key-1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is cloned speech using the reference voice.",
    "language": "English",
    "ref_audio_url": "https://example.com/reference.wav",
    "ref_text": "This is the transcript of the reference audio.",
    "response_format": "wav"
  }' \
  --output cloned.wav
```

#### `POST /api/v1/base/create-prompt`
Create reusable voice clone prompt

```bash
curl -X POST http://localhost:8000/api/v1/base/create-prompt \
  -H "X-API-Key: your-api-key-1" \
  -H "Content-Type: application/json" \
  -d '{
    "ref_audio_url": "https://example.com/reference.wav",
    "ref_text": "This is the transcript of the reference audio.",
    "x_vector_only_mode": false
  }'
```

Response:
```json
{
  "prompt_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Prompt created successfully"
}
```

#### `POST /api/v1/base/generate-with-prompt`
Generate using saved prompt

```bash
curl -X POST http://localhost:8000/api/v1/base/generate-with-prompt \
  -H "X-API-Key: your-api-key-1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "New text to synthesize with the saved voice.",
    "language": "English",
    "prompt_id": "550e8400-e29b-41d4-a716-446655440000",
    "response_format": "wav"
  }' \
  --output prompt_output.wav
```

#### `POST /api/v1/base/upload-ref-audio`
Upload reference audio file

```bash
curl -X POST http://localhost:8000/api/v1/base/upload-ref-audio \
  -H "X-API-Key: your-api-key-1" \
  -F "file=@reference.wav"
```

## Python Client Examples

### CustomVoice Example

```python
import requests
import base64

API_KEY = "your-api-key-1"
BASE_URL = "http://localhost:8000"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Generate with CustomVoice
response = requests.post(
    f"{BASE_URL}/api/v1/custom-voice/generate",
    headers=headers,
    json={
        "text": "Hello from Python!",
        "language": "English",
        "speaker": "Ryan",
        "instruct": "Speak enthusiastically",
        "response_format": "base64"
    }
)

if response.status_code == 200:
    result = response.json()
    audio_data = base64.b64decode(result["audio"])
    
    with open("output.wav", "wb") as f:
        f.write(audio_data)
    
    print(f"Audio saved! Sample rate: {result['sample_rate']} Hz")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### VoiceDesign Example

```python
import requests

API_KEY = "your-api-key-1"
BASE_URL = "http://localhost:8000"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Generate with VoiceDesign
response = requests.post(
    f"{BASE_URL}/api/v1/voice-design/generate",
    headers=headers,
    json={
        "text": "Custom voice design in action.",
        "language": "English",
        "instruct": "A young male voice, 20-25 years old, speaking with excitement and energy",
        "response_format": "wav"
    }
)

if response.status_code == 200:
    with open("voice_design.wav", "wb") as f:
        f.write(response.content)
    print("Voice design audio saved!")
```

### Voice Cloning Example

```python
import requests
import base64

API_KEY = "your-api-key-1"
BASE_URL = "http://localhost:8000"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Read reference audio and encode to base64
with open("reference.wav", "rb") as f:
    ref_audio_base64 = base64.b64encode(f.read()).decode()

# Clone voice
response = requests.post(
    f"{BASE_URL}/api/v1/base/clone",
    headers=headers,
    json={
        "text": "This is my cloned voice speaking new words.",
        "language": "English",
        "ref_audio_base64": ref_audio_base64,
        "ref_text": "Original text from reference audio.",
        "x_vector_only_mode": False,
        "response_format": "wav"
    }
)

if response.status_code == 200:
    with open("cloned.wav", "wb") as f:
        f.write(response.content)
    print("Cloned voice saved!")
```

### Streaming Example

```python
import requests
import json
import base64

API_KEY = "your-api-key-1"
BASE_URL = "http://localhost:8000"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Stream audio generation
response = requests.post(
    f"{BASE_URL}/api/v1/custom-voice/generate-stream",
    headers=headers,
    json={
        "text": "Streaming audio in real-time.",
        "language": "English",
        "speaker": "Aiden"
    },
    stream=True
)

chunks = []
for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            data = line_str[6:]  # Remove 'data: ' prefix
            if data != "complete":
                try:
                    chunks.append(data)
                except:
                    pass

print(f"Received {len(chunks)} audio chunks")
```

## Available Speakers (CustomVoice)

| Speaker | Description | Native Language |
|---------|-------------|-----------------|
| Vivian | Bright, slightly edgy young female voice | Chinese |
| Serena | Warm, gentle young female voice | Chinese |
| Uncle_Fu | Seasoned male voice with a low, mellow timbre | Chinese |
| Dylan | Youthful Beijing male voice with a clear, natural timbre | Chinese (Beijing Dialect) |
| Eric | Lively Chengdu male voice with a slightly husky brightness | Chinese (Sichuan Dialect) |
| Ryan | Dynamic male voice with strong rhythmic drive | English |
| Aiden | Sunny American male voice with a clear midrange | English |
| Ono_Anna | Playful Japanese female voice with a light, nimble timbre | Japanese |
| Sohee | Warm Korean female voice with rich emotion | Korean |

## Supported Languages

- Auto (automatic language detection)
- Chinese
- English
- Japanese
- Korean
- German
- French
- Russian
- Portuguese
- Spanish
- Italian

## Troubleshooting

### GPU Memory Issues

If you encounter out-of-memory errors:

1. Use the 0.6B models instead of 1.7B:
   ```bash
   QWEN_TTS_CUSTOM_VOICE_MODEL=Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice
   QWEN_TTS_BASE_MODEL=Qwen/Qwen3-TTS-12Hz-0.6B-Base
   ```

2. Set `PRELOAD_MODELS=false` to load models on-demand

3. Reduce batch sizes in requests

### Flash Attention Issues

If Flash Attention fails to install or causes issues:

1. Set `USE_FLASH_ATTENTION=false` in `.env`
2. The model will fall back to standard attention

### Model Download Issues

Models are automatically downloaded on first use. If you have download issues:

1. Pre-download models using ModelScope or HuggingFace CLI
2. Set `MODEL_CACHE_DIR` to point to your download location
3. Use local model paths instead of HuggingFace IDs

### API Key Issues

If authentication fails:

- Verify `API_KEYS` is set in `.env`
- Ensure you're passing `X-API-Key` header in requests
- For development without authentication, leave `API_KEYS` empty

## Performance Tips

1. **Preload Models**: Set `PRELOAD_MODELS=true` for faster first request (requires more memory)
2. **Use Prompts**: For voice cloning, create reusable prompts to avoid re-extracting features
3. **Batch Requests**: Use batch endpoints for multiple texts to improve throughput
4. **Flash Attention**: Enable for faster inference on supported GPUs
5. **Model Size**: Use 0.6B models for faster inference with slightly lower quality

## License

This project follows the Qwen3-TTS license. See the [official repository](https://github.com/QwenLM/Qwen3-TTS) for details.

## Citation

If you use this API server, please cite the Qwen3-TTS paper:

```bibtex
@article{Qwen3-TTS,
  title={Qwen3-TTS Technical Report},
  author={Hangrui Hu and Xinfa Zhu and Ting He and Dake Guo and Bin Zhang and Xiong Wang and Zhifang Guo and Ziyue Jiang and Hongkun Hao and Zishan Guo and Xinyu Zhang and Pei Zhang and Baosong Yang and Jin Xu and Jingren Zhou and Junyang Lin},
  journal={arXiv preprint arXiv:2601.15621},
  year={2026}
}
```

## Support

- **Official Qwen3-TTS**: https://github.com/QwenLM/Qwen3-TTS
- **Issues**: Report issues on the GitHub repository
- **Documentation**: Visit the interactive API docs at `/docs`

## Acknowledgments

This API server is built on top of the excellent [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) project by the Qwen team at Alibaba Cloud.
