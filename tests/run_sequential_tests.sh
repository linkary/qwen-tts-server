#!/bin/bash
# Run all model tests sequentially with auto-cleanup
# This tests models one at a time to save disk space

set -e
cd "$(dirname "$0")/.."

echo "========================================"
echo "Sequential Model Testing (One at a Time)"
echo "========================================"
echo ""
echo "This will:"
echo "  1. Download CustomVoice (3.4GB) → Test → Clean up"
echo "  2. Download VoiceDesign (3.4GB) → Test → Clean up"
echo "  3. Download Base+Tokenizer (3.5GB) → Test → Clean up"
echo ""
echo "Estimated time: 20-30 minutes on CPU"
echo "========================================"
echo ""

# Test CustomVoice
echo "=== [1/3] Testing CustomVoice ==="
echo "Downloading CustomVoice model..."
python tests/download_single_model.py custom_voice
echo ""
echo "Running CustomVoice tests..."
pytest tests/real_model/test_custom_voice_real.py -v -s
echo ""
echo "Cleaning up CustomVoice..."
python tests/cleanup_models.py
echo ""

# Test VoiceDesign
echo "=== [2/3] Testing VoiceDesign ==="
echo "Downloading VoiceDesign model..."
python tests/download_single_model.py voice_design
echo ""
echo "Running VoiceDesign tests..."
pytest tests/real_model/test_voice_design_real.py -v -s
echo ""
echo "Cleaning up VoiceDesign..."
python tests/cleanup_models.py
echo ""

# Test Base (with tokenizer)
echo "=== [3/3] Testing Base Voice Cloning ==="
echo "Downloading Tokenizer (small, 50MB)..."
python tests/download_single_model.py tokenizer
echo "Downloading Base model..."
python tests/download_single_model.py base
echo ""
echo "Running Base voice cloning tests..."
pytest tests/real_model/test_base_clone_real.py -v -s
echo ""
echo "Cleaning up Base and Tokenizer..."
python tests/cleanup_models.py
echo ""

echo "========================================"
echo "✓ All models tested successfully!"
echo "========================================"
