# Installation Fix - Flash Attention Issue

## Problem

When running `pip install -r requirements.txt`, flash-attn fails to build with:
```
ModuleNotFoundError: No module named 'torch'
```

## Root Cause

Flash Attention requires torch to be installed **before** it can be built, but pip tries to install all dependencies in parallel.

## Solution

We've restructured the installation process:

### 1. Updated requirements.txt

Removed flash-attn from main requirements and added clear installation order:
- Install torch first
- Then install other dependencies
- Flash-attn is now optional

### 2. Created Separate Files

- `requirements.txt` - Main dependencies (no flash-attn)
- `requirements-flash-attn.txt` - Optional flash-attn installation
- `INSTALL.md` - Comprehensive installation guide
- `install.sh` - Automated installation script

### 3. Updated Configuration

- `.env.example` now defaults `USE_FLASH_ATTENTION=false`
- Added clear documentation about flash-attn being optional

## Quick Fix for Your Current Issue

Run these commands in your conda environment:

```bash
# Activate your conda environment
conda activate <your-env-name>

# Step 1: Install PyTorch first
pip install torch>=2.1.0 --index-url https://download.pytorch.org/whl/cu121

# Step 2: Install main dependencies (no flash-attn)
pip install -r requirements.txt

# Step 3 (Optional): Install flash-attn if you have CUDA
pip install flash-attn>=2.5.0 --no-build-isolation
```

If flash-attn installation still fails, **that's OK**! Just:
1. Skip it
2. Set `USE_FLASH_ATTENTION=false` in your `.env` file
3. The server works perfectly without it

## Automated Installation

Use the installation script:

```bash
# Create and activate environment
conda create -n qwen-tts python=3.12
conda activate qwen-tts

# Run install script (defaults to 'qwen-tts' env)
bash install.sh

# Or specify a custom environment
CONDA_ENV=my-custom-env bash install.sh
```

The script will:
1. Check for conda and the specified environment
2. Install torch first
3. Install other dependencies
4. Optionally install flash-attn (with user confirmation)
5. Create .env file if needed

## Why Flash Attention is Optional

**Flash Attention provides:**
- ~20-30% faster inference
- Lower memory usage

**But requires:**
- NVIDIA GPU (Ampere or newer: RTX 3000/4000+)
- CUDA Toolkit 11.8+
- 5-15 minutes to compile
- torch installed first

**Without Flash Attention:**
- Server works perfectly fine
- Slightly slower inference
- No compilation headaches
- Works on any hardware (CPU, older GPUs)

## Recommendation

For development:
1. **Skip flash-attn** for now - it's not critical
2. Set `USE_FLASH_ATTENTION=false` in `.env`
3. Focus on development
4. Install flash-attn later if you need the performance boost

## Files Changed

1. `requirements.txt` - Reorganized, removed flash-attn
2. `requirements-flash-attn.txt` - New file for optional installation
3. `INSTALL.md` - New comprehensive guide
4. `install.sh` - New automated installation script
5. `.env.example` - Updated USE_FLASH_ATTENTION default to false
6. `README.md` - Updated installation instructions

## Testing

After installation, verify everything works:

```bash
conda activate <your-env-name>
python quickstart.py
```

Expected output:
```
✓ Server is running
✓ API key authentication is working
✓ Health check passed
```
