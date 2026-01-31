# Installation Guide

## Prerequisites

- Python 3.10-3.12
- Conda or Miniconda
- (Optional) NVIDIA GPU with CUDA support for GPU acceleration

### System Dependencies

Install required audio tools:

```bash
# Ubuntu/Debian
sudo apt-get install -y sox libsox-dev ffmpeg

# macOS
brew install sox ffmpeg
```

## Quick Install (Recommended)

The install script auto-detects your environment, CUDA, and GPU compatibility:

```bash
# Create and activate environment
conda create -n qwen-tts python=3.12
conda activate qwen-tts

# Run auto-install (detects CUDA and Flash Attention automatically)
bash install.sh
```

The script will:
1. ✅ Detect your current conda environment
2. ✅ Auto-detect CUDA availability
3. ✅ Install PyTorch (CUDA or CPU version)
4. ✅ Install all dependencies
5. ✅ Check GPU compatibility for Flash Attention (requires RTX 3000+, A100, H100)
6. ✅ Auto-install Flash Attention if compatible
7. ✅ Configure `.env` file automatically

## Manual Installation

### Standard (with CUDA)

```bash
conda activate <your-env-name>
pip install torch>=2.1.0 --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

### CPU-Only

```bash
conda activate <your-env-name>
pip install torch>=2.1.0 --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### With Flash Attention

Flash Attention requires:
- NVIDIA GPU with SM 8.0+ (RTX 3000/4000 series, A100, H100)
- CUDA Toolkit 11.8+

```bash
pip install flash-attn>=2.5.0 --no-build-isolation
```

## Troubleshooting

### Flash Attention Installation Fails

**Solution:** The server works fine without it. Set `USE_FLASH_ATTENTION=false` in `.env`.

### python-magic Issues

```bash
# macOS
brew install libmagic

# Ubuntu/Debian
sudo apt-get install libmagic1
```

### pydub/librosa Issues

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg
```

## Verification

```bash
python quickstart.py
```

## Running the Server

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or with Docker:
```bash
docker-compose up -d
```
