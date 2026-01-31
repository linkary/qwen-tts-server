#!/bin/bash
# =============================================================================
# Qwen3-TTS Server Installation Script for Linux with CUDA
# =============================================================================
# This script installs all dependencies and downloads models for GPU inference
#
# Requirements:
# - Linux system with NVIDIA GPU
# - CUDA 11.8+ or 12.1+ installed
# - conda or miniconda installed
# - At least 15 GB disk space for models
#
# Usage:
#   chmod +x install_cuda.sh
#   ./install_cuda.sh
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONDA_ENV_NAME="qwen-tts"
PYTHON_VERSION="3.10"
PYTORCH_VERSION="2.1.0"
CUDA_VERSION="cu121"  # Options: cu118, cu121

# Model list
MODELS=(
    "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"
    "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
    "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
    "Qwen/Qwen3-TTS-Tokenizer-12Hz"
)

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo -e "${BLUE}=================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=================================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

check_cuda() {
    if ! command -v nvidia-smi &> /dev/null; then
        print_error "nvidia-smi not found. Please install NVIDIA drivers and CUDA toolkit."
        exit 1
    fi
    
    print_info "CUDA Information:"
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
}

# =============================================================================
# Main Installation
# =============================================================================

print_header "Qwen3-TTS Server Installation (CUDA Version)"

# Check prerequisites
print_info "Checking prerequisites..."
check_command "conda"
check_cuda

# Ask user for CUDA version
echo ""
print_info "Detected CUDA version:"
nvidia-smi | grep "CUDA Version"
echo ""
echo "Please select your CUDA version:"
echo "  1) CUDA 11.8 (cu118)"
echo "  2) CUDA 12.1+ (cu121) [Default]"
read -p "Enter choice [1-2]: " cuda_choice

case $cuda_choice in
    1)
        CUDA_VERSION="cu118"
        print_info "Using CUDA 11.8"
        ;;
    2|"")
        CUDA_VERSION="cu121"
        print_info "Using CUDA 12.1+"
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

# Create conda environment
print_header "Step 1: Creating Conda Environment"
if conda env list | grep -q "^${CONDA_ENV_NAME} "; then
    print_warning "Environment '${CONDA_ENV_NAME}' already exists."
    read -p "Remove and recreate? [y/N]: " recreate
    if [[ $recreate =~ ^[Yy]$ ]]; then
        conda env remove -n ${CONDA_ENV_NAME} -y
        print_success "Removed existing environment"
    else
        print_info "Using existing environment"
    fi
fi

if ! conda env list | grep -q "^${CONDA_ENV_NAME} "; then
    conda create -n ${CONDA_ENV_NAME} python=${PYTHON_VERSION} -y
    print_success "Created conda environment: ${CONDA_ENV_NAME}"
fi

# Activate environment
print_info "Activating environment..."
eval "$(conda shell.bash hook)"
conda activate ${CONDA_ENV_NAME}

# Install PyTorch with CUDA
print_header "Step 2: Installing PyTorch with CUDA ${CUDA_VERSION}"
if [[ $CUDA_VERSION == "cu118" ]]; then
    pip install torch==${PYTORCH_VERSION} torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
elif [[ $CUDA_VERSION == "cu121" ]]; then
    pip install torch==${PYTORCH_VERSION} torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
fi
print_success "PyTorch installed"

# Verify CUDA is available
print_info "Verifying CUDA availability..."
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}'); print(f'Device count: {torch.cuda.device_count()}')"

# Install core dependencies
print_header "Step 3: Installing Core Dependencies"
pip install -r requirements.txt
print_success "Core dependencies installed"

# Install Flash Attention
print_header "Step 4: Installing Flash Attention 2"
print_info "This may take several minutes to compile..."
pip install flash-attn --no-build-isolation
if [ $? -eq 0 ]; then
    print_success "Flash Attention 2 installed successfully"
else
    print_warning "Flash Attention 2 installation failed. GPU inference will be slower."
    print_info "You can continue without it, but performance will be reduced."
fi

# Download models
print_header "Step 5: Downloading Qwen3-TTS Models"
print_info "This will download ~10-12 GB of models"
print_warning "Make sure you have sufficient disk space and network bandwidth"

read -p "Download models now? [Y/n]: " download_choice
if [[ ! $download_choice =~ ^[Nn]$ ]]; then
    # Create download script
    cat > download_models_cuda.py << 'EOF'
#!/usr/bin/env python3
"""Download all Qwen3-TTS models for production use"""
import os
import sys
from huggingface_hub import snapshot_download

# Model cache directory
cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
os.makedirs(cache_dir, exist_ok=True)

models = [
    "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
    "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    "Qwen/Qwen3-TTS-Tokenizer-12Hz",
]

print("=" * 70)
print("Downloading Qwen3-TTS Models")
print("=" * 70)
print(f"Cache directory: {cache_dir}")
print(f"Total models: {len(models)}")
print(f"Estimated size: 10-12 GB")
print()

for i, model_id in enumerate(models, 1):
    print(f"[{i}/{len(models)}] Downloading {model_id}...")
    try:
        snapshot_download(
            repo_id=model_id,
            cache_dir=cache_dir,
            resume_download=True
        )
        print(f"✓ {model_id} downloaded successfully\n")
    except Exception as e:
        print(f"✗ Failed to download {model_id}: {e}")
        sys.exit(1)

print("=" * 70)
print("✓ All models downloaded successfully!")
print(f"Models cached in: {cache_dir}")
print("=" * 70)
EOF

    chmod +x download_models_cuda.py
    python download_models_cuda.py
    
    if [ $? -eq 0 ]; then
        print_success "All models downloaded successfully"
        rm -f download_models_cuda.py
    else
        print_error "Model download failed"
        exit 1
    fi
else
    print_info "Skipping model download. You can download later by running:"
    print_info "  python tests/download_complete_model.py custom_voice"
    print_info "  python tests/download_complete_model.py voice_design"
    print_info "  python tests/download_complete_model.py base"
    print_info "  python tests/download_complete_model.py tokenizer"
fi

# Create .env file
print_header "Step 6: Creating Environment Configuration"
if [ ! -f .env ]; then
    cat > .env << EOF
# =============================================================================
# Qwen3-TTS Server Configuration (CUDA Version)
# =============================================================================

# CUDA Configuration
CUDA_DEVICE=0
USE_FLASH_ATTENTION=true

# Model Configuration
MODEL_CACHE_DIR=~/.cache/huggingface/hub

# API Configuration
API_KEYS=your-secret-api-key-here
HOST=0.0.0.0
PORT=8000

# Feature Flags
VOICE_CACHE_ENABLED=true
VOICE_CACHE_SIZE=100
VOICE_CACHE_TTL=3600

AUDIO_PREPROCESSING_ENABLED=true
AUDIO_MAX_SIZE_MB=25
AUDIO_MIN_DURATION=1.0
AUDIO_MAX_DURATION=30.0

# Performance
ENABLE_PERFORMANCE_LOGGING=true
WORKERS=1

# Warmup
WARMUP_ON_STARTUP=true

# Logging
LOG_LEVEL=INFO
EOF
    print_success "Created .env file"
    print_warning "Please update API_KEYS in .env file with your secure key"
else
    print_info ".env file already exists, skipping"
fi

# Create startup script
print_header "Step 7: Creating Startup Script"
cat > start_cuda.sh << 'EOF'
#!/bin/bash
# Start Qwen3-TTS Server with CUDA support

# Activate conda environment
eval "$(conda shell.bash hook)"
conda activate qwen-tts

# Check CUDA
if ! command -v nvidia-smi &> /dev/null; then
    echo "Warning: nvidia-smi not found. GPU may not be available."
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start server
echo "Starting Qwen3-TTS Server with CUDA support..."
echo "CUDA Device: ${CUDA_DEVICE:-0}"
echo "Flash Attention: ${USE_FLASH_ATTENTION:-true}"
echo ""

uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --workers ${WORKERS:-1}
EOF

chmod +x start_cuda.sh
print_success "Created start_cuda.sh"

# Verification
print_header "Step 8: Verification"
print_info "Running verification checks..."

echo ""
print_info "Python version:"
python --version

echo ""
print_info "PyTorch version:"
python -c "import torch; print(f'PyTorch: {torch.__version__}')"

echo ""
print_info "CUDA availability:"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA devices: {torch.cuda.device_count()}'); print(f'Current device: {torch.cuda.current_device() if torch.cuda.is_available() else \"N/A\"}'); print(f'Device name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

echo ""
print_info "Flash Attention:"
python -c "try: import flash_attn; print('Flash Attention 2: Installed ✓'); except: print('Flash Attention 2: Not installed (optional)')"

echo ""
print_info "Qwen TTS:"
python -c "try: import qwen_tts; print('qwen-tts: Installed ✓'); except Exception as e: print(f'qwen-tts: {e}')"

# Final summary
print_header "Installation Complete!"
echo ""
print_success "Qwen3-TTS Server is ready to use with CUDA acceleration!"
echo ""
print_info "Next steps:"
echo "  1. Update API_KEYS in .env file with a secure key"
echo "  2. Start the server:"
echo "     ./start_cuda.sh"
echo ""
echo "  3. Test the API:"
echo "     curl http://localhost:8000/health"
echo ""
print_info "For testing:"
echo "  - Run unit tests: ./run_tests.sh unit"
echo "  - Run integration tests: ./run_tests.sh integration"
echo "  - Run real model tests: ./run_tests.sh real"
echo ""
print_info "Expected Performance (with GPU):"
echo "  - Generation time: 1-3 seconds per request"
echo "  - RTF (Real-Time Factor): 0.1-0.5 (10-50x faster than CPU)"
echo ""
print_info "Conda environment: ${CONDA_ENV_NAME}"
echo "  Activate: conda activate ${CONDA_ENV_NAME}"
echo "  Deactivate: conda deactivate"
echo ""
print_success "Happy voice synthesis! 🎤"
