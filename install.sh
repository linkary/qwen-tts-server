#!/bin/bash
# Installation script for Qwen3-TTS Server
# Run with: bash install.sh

set -e  # Exit on error

echo "🚀 Qwen3-TTS Server Installation"
echo "================================"
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Error: conda not found. Please install Miniconda or Anaconda first."
    exit 1
fi

# Check if learn_ai environment exists
if ! conda env list | grep -q "learn_ai"; then
    echo "❌ Error: conda environment 'learn_ai' not found."
    echo "Please create it first with: conda create -n learn_ai python=3.10"
    exit 1
fi

echo "✓ Found conda environment: learn_ai"
echo ""

# Detect conda initialization
CONDA_BASE=$(conda info --base)
if [ -f "$CONDA_BASE/etc/profile.d/conda.sh" ]; then
    source "$CONDA_BASE/etc/profile.d/conda.sh"
else
    echo "❌ Error: Could not initialize conda"
    exit 1
fi

# Activate environment
echo "📦 Activating conda environment: learn_ai"
conda activate learn_ai || {
    echo "❌ Failed to activate learn_ai environment"
    exit 1
}

echo "✓ Environment activated"
echo ""

# Step 1: Install PyTorch
echo "📥 Step 1/3: Installing PyTorch with CUDA support..."
pip install torch>=2.1.0 --index-url https://download.pytorch.org/whl/cu121 || {
    echo "⚠️  CUDA version failed, trying CPU version..."
    pip install torch>=2.1.0 --index-url https://download.pytorch.org/whl/cpu
}
echo "✓ PyTorch installed"
echo ""

# Step 2: Install main dependencies
echo "📥 Step 2/3: Installing main dependencies..."
pip install -r requirements.txt
echo "✓ Main dependencies installed"
echo ""

# Step 3: Optional Flash Attention
echo "📥 Step 3/3: Flash Attention (optional)..."
read -p "Install Flash Attention? (requires CUDA, takes 5-15 min) [y/N]: " install_flash
if [[ $install_flash =~ ^[Yy]$ ]]; then
    echo "Installing Flash Attention (this may take a while)..."
    pip install flash-attn>=2.5.0 --no-build-isolation || {
        echo "⚠️  Flash Attention installation failed (this is OK)"
        echo "   The server will work without it. Set USE_FLASH_ATTENTION=false in .env"
    }
else
    echo "⏭️  Skipping Flash Attention"
    echo "   Remember to set USE_FLASH_ATTENTION=false in .env"
fi
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
fi

# Summary
echo "✅ Installation Complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your settings:"
echo "   - Set API_KEYS for authentication"
echo "   - Set USE_FLASH_ATTENTION=false if you skipped flash-attn"
echo ""
echo "2. Start the server:"
echo "   conda activate learn_ai"
echo "   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "3. Or use the start script:"
echo "   ./start.sh"
echo ""
echo "4. Test with quickstart:"
echo "   python quickstart.py"
echo ""
