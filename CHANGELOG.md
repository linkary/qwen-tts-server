# Changelog

All notable changes to the Qwen3-TTS API Server project.

## [1.0.0] - 2026-01-30

### Initial Release

#### Added
- FastAPI-based REST API server for Qwen3-TTS models
- Support for three model types:
  - CustomVoice (9 preset speakers with instruction control)
  - VoiceDesign (natural language voice description)
  - Base (voice cloning with 3-second reference audio)
- API key authentication system
- Comprehensive API endpoints:
  - Health check and model status
  - CustomVoice generation (batch and streaming)
  - VoiceDesign generation (batch and streaming)
  - Voice cloning with reference audio
  - Reusable voice clone prompts
  - Reference audio upload utility
- Environment-based configuration with Pydantic Settings
- Lazy model loading with thread-safe caching
- Streaming support via Server-Sent Events (SSE)
- Multiple response formats (WAV file, base64 JSON)
- Audio processing utilities (URL, base64, file upload support)
- Docker support with NVIDIA GPU
- docker-compose configuration for production deployment
- docker-compose.dev.yml for development with hot reload
- Comprehensive README with usage examples
- API test suite (test_api.py)
- Complete usage examples (examples.py)
- Quick start health check script (quickstart.py)
- Makefile for common tasks
- Implementation documentation (IMPLEMENTATION.md)
- CORS middleware for cross-origin requests
- Structured logging with configurable levels
- Auto-generated API documentation (Swagger UI, ReDoc)

#### Technical Features
- Python 3.12 support
- Type hints throughout codebase
- Pydantic models for request/response validation
- Async/await for I/O operations
- Thread-safe model management
- Flash Attention 2 support for faster inference
- Graceful error handling and HTTP status codes
- Model preloading option for faster first request
- Support for HuggingFace model IDs and local paths

#### Documentation
- Comprehensive README with installation and usage
- API examples in curl and Python
- Docker deployment guide
- Configuration reference
- Troubleshooting section
- Performance tuning tips
- List of all available speakers and languages

#### Development Tools
- Test scripts for API validation
- Example scripts demonstrating all features
- Makefile for common development tasks
- Development docker-compose override
- Git ignore configuration
- Environment template (.env.example)

### Code Statistics
- ~2,100 lines of Python code
- 26 project files
- 5 main modules (config, auth, models, routers, utils)
- 4 API routers (health, custom_voice, voice_design, base)
- 30+ API endpoints

### Supported Features
- ✅ 9 preset speakers (CustomVoice)
- ✅ 10 languages (Auto-detect + 9 explicit)
- ✅ Instruction-based voice control
- ✅ Natural language voice design
- ✅ 3-second voice cloning
- ✅ Reusable voice clone prompts
- ✅ Streaming and batch generation
- ✅ Multiple response formats
- ✅ API authentication
- ✅ Docker deployment
- ✅ GPU support

### Known Limitations
- Voice clone prompts stored in memory (not persistent)
- No request queuing system
- No distributed model loading
- No built-in rate limiting per key
- No metrics/monitoring integration

### Future Enhancements
See IMPLEMENTATION.md for planned enhancements including:
- Redis for persistent prompt storage
- Rate limiting middleware
- Prometheus metrics
- Celery task queue
- Multi-GPU support
- Model quantization options
- WebSocket streaming
- Admin dashboard

---

## Version Format

This project follows [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for backward-compatible functionality additions
- PATCH version for backward-compatible bug fixes
