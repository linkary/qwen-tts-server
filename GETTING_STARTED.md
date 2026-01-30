# Getting Started with Qwen3-TTS API Server

## Quick Start (5 minutes)

### Prerequisites
- Python 3.12+ or Docker
- NVIDIA GPU with 16GB+ VRAM (recommended)
- CUDA 12.1+ installed (for local deployment)

### Option A: Docker (Recommended)

1. **Setup environment**
```bash
cd qwen-tts-server
cp .env.example .env
# Edit .env and set your API_KEYS
```

2. **Start the server**
```bash
docker-compose up -d
```

3. **Verify it's running**
```bash
python quickstart.py
```

4. **Access the API**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Option B: Local Python

1. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup environment**
```bash
cp .env.example .env
# Edit .env and set your API_KEYS
```

4. **Start the server**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## First API Call

Once the server is running, try this:

```bash
curl -X POST http://localhost:8000/api/v1/custom-voice/generate \
  -H "X-API-Key: your-api-key-1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello! This is Qwen3-TTS speaking.",
    "language": "English",
    "speaker": "Ryan",
    "response_format": "wav"
  }' \
  --output hello.wav

# Play the audio
# macOS: afplay hello.wav
# Linux: aplay hello.wav
# Windows: start hello.wav
```

## Try the Examples

We've included complete working examples:

```bash
# Make sure server is running, then:
python examples.py
```

This will generate 4 audio files demonstrating:
1. CustomVoice (preset speakers)
2. VoiceDesign (custom voice description)
3. Voice cloning (from reference audio)
4. Reusable voice clone prompts

## Next Steps

### 1. Explore the API Documentation
Visit http://localhost:8000/docs for interactive API documentation where you can:
- Browse all endpoints
- Try API calls directly in the browser
- See request/response schemas
- Test with different parameters

### 2. Try Different Speakers
```bash
# List available speakers
curl http://localhost:8000/api/v1/custom-voice/speakers \
  -H "X-API-Key: your-api-key-1"

# Try different speakers
# - Ryan: Dynamic male voice (English)
# - Aiden: Sunny American male (English)
# - Vivian: Bright young female (Chinese)
# - Serena: Warm gentle female (Chinese)
# - Ono_Anna: Playful female (Japanese)
# - Sohee: Warm female (Korean)
```

### 3. Voice Design with Natural Language
```bash
curl -X POST http://localhost:8000/api/v1/voice-design/generate \
  -H "X-API-Key: your-api-key-1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Voice design lets you describe any voice you want.",
    "language": "English",
    "instruct": "A professional news anchor voice, male, 40-50 years old, authoritative yet friendly",
    "response_format": "wav"
  }' \
  --output news_anchor.wav
```

### 4. Clone Your Own Voice

```bash
# First, prepare a 3-10 second audio clip of your voice
# Then clone it:

curl -X POST http://localhost:8000/api/v1/base/clone \
  -H "X-API-Key: your-api-key-1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Now I can speak with the cloned voice!",
    "language": "English",
    "ref_audio_url": "https://your-audio-url.com/reference.wav",
    "ref_text": "The transcript of your reference audio.",
    "response_format": "wav"
  }' \
  --output my_voice.wav
```

## Using Python

```python
import requests

API_KEY = "your-api-key-1"
BASE_URL = "http://localhost:8000"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Generate speech
response = requests.post(
    f"{BASE_URL}/api/v1/custom-voice/generate",
    headers=headers,
    json={
        "text": "Hello from Python!",
        "language": "English",
        "speaker": "Ryan",
        "response_format": "wav"
    }
)

# Save audio
if response.status_code == 200:
    with open("output.wav", "wb") as f:
        f.write(response.content)
    print("Audio saved to output.wav")
```

## Common Tasks

### Switch to Smaller Models (Faster, Less Memory)
Edit `.env`:
```bash
QWEN_TTS_CUSTOM_VOICE_MODEL=Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice
QWEN_TTS_BASE_MODEL=Qwen/Qwen3-TTS-12Hz-0.6B-Base
```

### Preload Models for Faster First Request
Edit `.env`:
```bash
PRELOAD_MODELS=true
```
Note: Requires more GPU memory (all models loaded at startup)

### Change Port
Edit `.env`:
```bash
PORT=9000
```

### Disable Flash Attention (if incompatible GPU)
Edit `.env`:
```bash
USE_FLASH_ATTENTION=false
```

### Run Tests
```bash
# Quick health check
python quickstart.py

# Full test suite
python test_api.py

# Complete examples
python examples.py
```

## Troubleshooting

### Server won't start
1. Check if port 8000 is already in use
2. Verify CUDA is installed: `nvidia-smi`
3. Check logs: `docker-compose logs` (for Docker)

### Out of GPU memory
1. Use smaller models (0.6B instead of 1.7B)
2. Set `PRELOAD_MODELS=false`
3. Close other GPU applications

### Authentication errors
1. Check API_KEYS in `.env`
2. Verify X-API-Key header in requests
3. For testing, leave API_KEYS empty (no auth)

### Models download slowly
1. Models auto-download on first use (~4-8GB each)
2. Be patient on first request
3. Pre-download with HuggingFace CLI if needed

## Production Deployment

For production:
1. Set strong API keys
2. Configure CORS appropriately
3. Use HTTPS (nginx/traefik reverse proxy)
4. Set resource limits in docker-compose.yml
5. Set up monitoring and logging
6. Consider Redis for prompt storage
7. Implement rate limiting

See README.md for detailed production setup.

## Support

- **API Docs**: http://localhost:8000/docs
- **README**: Complete documentation
- **IMPLEMENTATION.md**: Technical details
- **examples.py**: Working code examples
- **GitHub**: https://github.com/QwenLM/Qwen3-TTS

## What's Next?

After getting comfortable with the basics:
1. Integrate into your application
2. Batch process multiple texts
3. Use streaming for real-time apps
4. Create reusable voice profiles
5. Experiment with voice design descriptions
6. Clone voices for consistent characters

Happy voice synthesis! 🎙️
