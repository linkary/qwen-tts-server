#!/bin/bash
# Installation script for Qwen3-TTS Server
# Run with: bash install.sh
# Auto-detects current conda environment, CUDA, and Flash Attention compatibility

set -e  # Exit on error

echo "🚀 Qwen3-TTS Server Installation"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ============================================
# Step 1: Detect and validate conda environment
# ============================================
if [[ -z "$CONDA_DEFAULT_ENV" ]]; then
    echo -e "${RED}❌ Error: No conda environment is activated.${NC}"
    echo "Please activate a conda environment first:"
    echo "  conda activate <your-env-name>"
    echo ""
    echo "Or create a new one:"
    echo "  conda create -n qwen-tts python=3.12"
    echo "  conda activate qwen-tts"
    exit 1
fi

CONDA_ENV="$CONDA_DEFAULT_ENV"
echo -e "${GREEN}✓ Using conda environment: ${CONDA_ENV}${NC}"
echo ""

# ============================================
# Step 2: Detect CUDA availability
# ============================================
echo "🔍 Detecting CUDA availability..."

CUDA_AVAILABLE=false
CUDA_VERSION=""

# Method 1: Check nvidia-smi
if command -v nvidia-smi &> /dev/null; then
    if nvidia-smi &> /dev/null; then
        CUDA_AVAILABLE=true
        CUDA_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -n1 || echo "")
        echo -e "${GREEN}✓ NVIDIA GPU detected (Driver: ${CUDA_VERSION})${NC}"
    fi
fi

# Method 2: Check nvcc
if ! $CUDA_AVAILABLE && command -v nvcc &> /dev/null; then
    CUDA_AVAILABLE=true
    CUDA_VERSION=$(nvcc --version | grep "release" | sed 's/.*release //' | sed 's/,.*//')
    echo -e "${GREEN}✓ CUDA Toolkit detected (Version: ${CUDA_VERSION})${NC}"
fi

if ! $CUDA_AVAILABLE; then
    echo -e "${YELLOW}⚠️  No CUDA detected - will install CPU-only version${NC}"
fi
echo ""

# ============================================
# Step 3: Install PyTorch
# ============================================
echo "📥 Step 1/3: Installing PyTorch..."

if $CUDA_AVAILABLE; then
    echo "Installing PyTorch with CUDA support..."
    pip install torch>=2.1.0 --index-url https://download.pytorch.org/whl/cu121 || {
        echo -e "${YELLOW}⚠️  CUDA version failed, trying CPU version...${NC}"
        pip install torch>=2.1.0 --index-url https://download.pytorch.org/whl/cpu
        CUDA_AVAILABLE=false
    }
else
    echo "Installing CPU-only PyTorch..."
    pip install torch>=2.1.0 --index-url https://download.pytorch.org/whl/cpu
fi

echo -e "${GREEN}✓ PyTorch installed${NC}"
echo ""

# ============================================
# Step 4: Install main dependencies
# ============================================
echo "📥 Step 2/3: Installing main dependencies..."
pip install -r requirements.txt
echo -e "${GREEN}✓ Main dependencies installed${NC}"
echo ""

# ============================================
# Step 5: Detect Flash Attention compatibility and install
# ============================================
echo "📥 Step 3/3: Flash Attention (auto-detection)..."

FLASH_ATTN_COMPATIBLE=false
FLASH_ATTN_INSTALLED=false

if $CUDA_AVAILABLE; then
    # Check GPU architecture (Ampere or newer required)
    echo "Checking GPU compatibility for Flash Attention..."
    
    GPU_ARCH=$(python3 -c "
import torch
if torch.cuda.is_available():
    cap = torch.cuda.get_device_capability()
    print(f'{cap[0]}.{cap[1]}')
else:
    print('none')
" 2>/dev/null || echo "none")
    
    if [[ "$GPU_ARCH" != "none" ]]; then
        # Flash Attention requires SM 8.0+ (Ampere: 8.0, Ada: 8.9, Hopper: 9.0)
        MAJOR_VERSION=$(echo "$GPU_ARCH" | cut -d'.' -f1)
        if [[ "$MAJOR_VERSION" -ge 8 ]]; then
            FLASH_ATTN_COMPATIBLE=true
            GPU_NAME=$(python3 -c "import torch; print(torch.cuda.get_device_name(0))" 2>/dev/null || echo "Unknown")
            echo -e "${GREEN}✓ GPU compatible with Flash Attention: ${GPU_NAME} (SM ${GPU_ARCH})${NC}"
        else
            echo -e "${YELLOW}⚠️  GPU architecture SM ${GPU_ARCH} is too old for Flash Attention${NC}"
            echo "   Flash Attention requires SM 8.0+ (RTX 3000/4000 series, A100, H100)"
        fi
    else
        echo -e "${YELLOW}⚠️  Could not detect GPU architecture${NC}"
    fi
fi

if $FLASH_ATTN_COMPATIBLE; then
    echo ""
    echo "Installing Flash Attention (this may take 5-15 minutes)..."
    if pip install flash-attn>=2.5.0 --no-build-isolation 2>&1; then
        FLASH_ATTN_INSTALLED=true
        echo -e "${GREEN}✓ Flash Attention installed successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Flash Attention installation failed (this is OK)${NC}"
        echo "   The server will work without it."
    fi
else
    echo -e "${YELLOW}⏭️  Skipping Flash Attention (not compatible or no CUDA)${NC}"
fi
echo ""

# ============================================
# Step 6: Create and configure .env file
# ============================================
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
fi

# Auto-configure USE_FLASH_ATTENTION based on installation result
if $FLASH_ATTN_INSTALLED; then
    sed -i 's/USE_FLASH_ATTENTION=false/USE_FLASH_ATTENTION=true/' .env 2>/dev/null || true
    echo -e "${GREEN}✓ Enabled Flash Attention in .env${NC}"
else
    sed -i 's/USE_FLASH_ATTENTION=true/USE_FLASH_ATTENTION=false/' .env 2>/dev/null || true
fi

# Auto-configure device based on CUDA availability
if $CUDA_AVAILABLE; then
    echo -e "${GREEN}✓ CUDA device configured in .env${NC}"
else
    sed -i 's/CUDA_DEVICE=cuda:0/CUDA_DEVICE=cpu/' .env 2>/dev/null || true
    echo -e "${YELLOW}✓ CPU device configured in .env${NC}"
fi
echo ""

# ============================================
# Summary
# ============================================
echo "============================================"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "============================================"
echo ""
echo "Configuration:"
echo "  • Environment: $CONDA_ENV"
if $CUDA_AVAILABLE; then
    echo -e "  • Device: ${GREEN}CUDA${NC}"
else
    echo -e "  • Device: ${YELLOW}CPU${NC}"
fi
if $FLASH_ATTN_INSTALLED; then
    echo -e "  • Flash Attention: ${GREEN}Enabled${NC}"
else
    echo -e "  • Flash Attention: ${YELLOW}Disabled${NC}"
fi
echo ""
echo "Next steps:"
echo "1. Edit .env file to set your API_KEYS"
echo ""
echo "2. Start the server:"
echo "   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "3. Test with quickstart:"
echo "   python quickstart.py"
echo ""
