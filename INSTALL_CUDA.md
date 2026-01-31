# CUDA Installation Guide

## Quick Start (Linux with CUDA)

For systems with NVIDIA GPU and CUDA support, use the automated installation script:

```bash
# Make script executable
chmod +x install_cuda.sh

# Run installation
./install_cuda.sh
```

The script will:
1. ✅ Create conda environment (qwen-tts)
2. ✅ Install PyTorch with CUDA support
3. ✅ Install all dependencies
4. ✅ Install Flash Attention 2 (for faster inference)
5. ✅ Download all models (~10-12 GB)
6. ✅ Create .env configuration
7. ✅ Create startup script

## System Requirements

### Hardware
- NVIDIA GPU with CUDA Compute Capability 7.0+ (e.g., V100, A100, RTX 2080+)
- At least 8 GB GPU memory (16 GB recommended)
- 15 GB disk space for models
- 8 GB RAM

### Software
- Linux (Ubuntu 20.04+ or similar)
- NVIDIA Driver 450.80.02+
- CUDA 11.8 or 12.1+
- conda or miniconda

## CUDA Version Selection

The script supports two CUDA versions:

### CUDA 11.8 (cu118)
- For older systems
- Compatible with most GPUs
- PyTorch 2.1.0 with CUDA 11.8

### CUDA 12.1+ (cu121) [Recommended]
- For newer systems
- Better performance
- PyTorch 2.1.0 with CUDA 12.1

**Check your CUDA version:**
```bash
nvidia-smi
# Look for "CUDA Version: X.X"
```

## Installation Steps

### 1. Verify Prerequisites

```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA toolkit (optional)
nvcc --version

# Check conda
conda --version
```

### 2. Clone Repository

```bash
git clone <repository-url>
cd qwen-tts-server
```

### 3. Run Installation Script

```bash
./install_cuda.sh
```

The script will:
- Detect your CUDA version
- Create conda environment
- Install PyTorch with CUDA
- Install all dependencies
- Compile Flash Attention 2
- Download models (optional)

### 4. Configure Environment

Edit `.env` file:
```bash
nano .env
```

Update these settings:
```bash
# Set your API key
API_KEYS=your-secure-api-key-here

# GPU selection (0 for first GPU, 1 for second, etc.)
CUDA_DEVICE=0

# Enable Flash Attention for faster inference
USE_FLASH_ATTENTION=true
```

### 5. Start Server

```bash
# Start with CUDA support
./start_cuda.sh
```

## Flash Attention 2

Flash Attention 2 provides significant speedup for inference:

**Benefits:**
- 2-4x faster inference
- Lower memory usage
- Better efficiency

**Requirements:**
- CUDA 11.8 or 12.1+
- GPU with compute capability 7.0+ (Volta, Turing, Ampere, Ada, Hopper)

**Installation:**
The script automatically installs Flash Attention. If compilation fails, the server will fall back to standard attention (slower but functional).

**Supported GPUs:**
- ✅ V100 (compute 7.0)
- ✅ RTX 2080, 2080 Ti (compute 7.5)
- ✅ RTX 3090, 3080 (compute 8.6)
- ✅ RTX 4090, 4080 (compute 8.9)
- ✅ A100 (compute 8.0)
- ✅ H100 (compute 9.0)

## Model Downloads

Models are downloaded automatically during installation. Total size: ~10-12 GB

**Models:**
1. `Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice` (~3.4 GB)
2. `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign` (~3.4 GB)
3. `Qwen/Qwen3-TTS-12Hz-1.7B-Base` (~3.4 GB)
4. `Qwen/Qwen3-TTS-Tokenizer-12Hz` (~50 MB)

**Manual download:**
```bash
conda activate qwen-tts
python tests/download_complete_model.py custom_voice
python tests/download_complete_model.py voice_design
python tests/download_complete_model.py base
python tests/download_complete_model.py tokenizer
```

## Performance Expectations

### With CUDA + Flash Attention
- **Generation time**: 1-3 seconds per request
- **RTF**: 0.1-0.5 (10-50x faster than real-time)
- **Throughput**: 20-60 requests/minute (depending on GPU)

### Without Flash Attention (CUDA only)
- **Generation time**: 3-5 seconds per request
- **RTF**: 0.5-1.0 (1-2x faster than real-time)
- **Throughput**: 12-20 requests/minute

### CPU-only (for comparison)
- **Generation time**: 30-70 seconds per request
- **RTF**: 15-30 (15-30x slower than real-time)
- **Throughput**: 1-2 requests/minute

## Testing

### Quick Health Check
```bash
curl http://localhost:8000/health
```

### Run Test Suite
```bash
# Unit tests (no models required)
./run_tests.sh unit

# Integration tests (mocked models)
./run_tests.sh integration

# Real model tests (requires models, 15-25 min on GPU)
./run_tests.sh real
```

## Troubleshooting

### CUDA Out of Memory
**Symptom:** `RuntimeError: CUDA out of memory`

**Solutions:**
1. Use smaller batch size
2. Reduce concurrent requests
3. Use GPU with more memory
4. Set `WORKERS=1` in .env

### Flash Attention Installation Failed
**Symptom:** Compilation errors during `flash-attn` installation

**Solutions:**
1. Check CUDA version: `nvidia-smi`
2. Verify GPU compute capability: [NVIDIA GPU list](https://developer.nvidia.com/cuda-gpus)
3. Update NVIDIA driver
4. Continue without Flash Attention (slower but functional)

### Models Not Found
**Symptom:** `Model not found` errors

**Solution:**
```bash
conda activate qwen-tts
python tests/download_complete_model.py custom_voice
python tests/download_complete_model.py voice_design
python tests/download_complete_model.py base
python tests/download_complete_model.py tokenizer
```

### Slow Inference Despite GPU
**Check:**
1. GPU is being used: Check GPU utilization with `nvidia-smi`
2. Flash Attention is enabled: Check logs for "Using Flash Attention"
3. CUDA_DEVICE is correct: `echo $CUDA_DEVICE`

### Port Already in Use
**Symptom:** `Address already in use`

**Solution:**
Change port in `.env`:
```bash
PORT=8001
```

## Multi-GPU Setup

For multiple GPUs, you can run multiple server instances:

### GPU 0
```bash
export CUDA_DEVICE=0
export PORT=8000
./start_cuda.sh
```

### GPU 1
```bash
export CUDA_DEVICE=1
export PORT=8001
./start_cuda.sh
```

## Production Deployment

### Using systemd (Linux)

Create service file `/etc/systemd/system/qwen-tts.service`:

```ini
[Unit]
Description=Qwen3-TTS Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/qwen-tts-server
Environment="PATH=/home/your-user/miniconda3/envs/qwen-tts/bin"
ExecStart=/path/to/qwen-tts-server/start_cuda.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable qwen-tts
sudo systemctl start qwen-tts
sudo systemctl status qwen-tts
```

### Using Docker

See `DOCKER.md` for containerized deployment.

### Using Nginx Reverse Proxy

Configure Nginx for production:
```nginx
upstream qwen_tts {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://qwen_tts;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }
}
```

## Environment Variables Reference

See `.env.example` for all configuration options.

### Key Settings for CUDA

| Variable | Default | Description |
|----------|---------|-------------|
| `CUDA_DEVICE` | `0` | GPU device ID |
| `USE_FLASH_ATTENTION` | `true` | Enable Flash Attention 2 |
| `MODEL_CACHE_DIR` | `~/.cache/huggingface/hub` | Model storage location |
| `WORKERS` | `1` | Uvicorn workers (keep at 1 for GPU) |

## Benchmarking

To benchmark your GPU setup:

```bash
conda activate qwen-tts
python benchmark.py --device cuda --flash-attn
```

Expected results (RTX 3090):
- CustomVoice: ~1.5s per request (RTF: 0.3)
- VoiceDesign: ~1.2s per request (RTF: 0.25)
- Base: ~2.0s per request (RTF: 0.4)

## Upgrading

To update to the latest version:

```bash
git pull
conda activate qwen-tts
pip install -r requirements.txt --upgrade
```

## Uninstallation

```bash
# Remove conda environment
conda env remove -n qwen-tts

# Remove models (optional)
rm -rf ~/.cache/huggingface/hub/models--Qwen--Qwen3-TTS*
```

## Support

For issues related to:
- **CUDA/GPU**: Check NVIDIA forums and PyTorch documentation
- **Flash Attention**: See [flash-attention GitHub](https://github.com/Dao-AILab/flash-attention)
- **Models**: See [Qwen3-TTS HuggingFace](https://huggingface.co/Qwen)

## License

See `LICENSE` file for details.
