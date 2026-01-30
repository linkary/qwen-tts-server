# Installation Guide

## Prerequisites

- Python 3.10-3.12
- (Optional) NVIDIA GPU with CUDA support for GPU acceleration
- (Optional) CUDA Toolkit 11.8+ for Flash Attention

## Installation Methods

### Method 1: Standard Installation (Recommended)

```bash
# Activate your conda environment
conda activate learn_ai

# Install dependencies in order
pip install torch>=2.1.0 --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

### Method 2: CPU-Only Installation

```bash
conda activate learn_ai

# Install CPU-only PyTorch
pip install torch>=2.1.0 --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### Method 3: With Flash Attention (Advanced)

Flash Attention significantly improves performance but requires:
- NVIDIA GPU (Ampere or newer: RTX 3000/4000 series, A100, H100, etc.)
- CUDA Toolkit 11.8+
- Patience (compilation takes 5-15 minutes)

```bash
conda activate learn_ai

# Step 1: Install PyTorch with CUDA
pip install torch>=2.1.0 --index-url https://download.pytorch.org/whl/cu121

# Step 2: Install other dependencies
pip install -r requirements.txt

# Step 3: Install Flash Attention (this will compile from source)
pip install flash-attn>=2.5.0 --no-build-isolation
```

**Note:** If flash-attn installation fails, the server will work fine without it. Set `USE_FLASH_ATTENTION=false` in your `.env` file.

## Troubleshooting

### Flash Attention Installation Fails

**Error:** `ModuleNotFoundError: No module named 'torch'`

**Solution:** Install torch first before flash-attn:
```bash
pip install torch>=2.1.0 --index-url https://download.pytorch.org/whl/cu121
pip install flash-attn>=2.5.0 --no-build-isolation
```

**Error:** `CUDA not available` during flash-attn build

**Solution:** Either:
1. Install CUDA Toolkit from NVIDIA
2. Skip flash-attn and set `USE_FLASH_ATTENTION=false` in `.env`

### python-magic Installation Issues

**macOS:**
```bash
brew install libmagic
pip install python-magic
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libmagic1
pip install python-magic
```

**Error:** `ImportError: failed to find libmagic`

**Solution:** Audio validation will work without python-magic, but with reduced accuracy.

### pydub/librosa Issues

These require ffmpeg for some audio formats:

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

## Verification

After installation, verify everything works:

```bash
conda activate learn_ai
python quickstart.py
```

You should see:
```
✓ Server is running
✓ API key authentication is working
✓ Health check passed
```

## Environment Setup

Copy the example environment file and configure:

```bash
cp .env.example .env
# Edit .env with your settings
```

Minimum required settings:
```bash
API_KEYS=your-secret-key-here
CUDA_DEVICE=cuda:0  # or "cpu" for CPU-only
USE_FLASH_ATTENTION=false  # Set to true if you installed flash-attn
```

## Running the Server

```bash
conda activate learn_ai
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or use the start script:
```bash
chmod +x start.sh
./start.sh
```

## Docker Installation (Alternative)

If you prefer Docker:

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

Docker automatically handles all dependencies including flash-attn.
