#!/bin/bash

# Qwen3-TTS Server Run Script
# Usage: ./run.sh [--ssl]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Parse arguments
USE_SSL=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --ssl)
            USE_SSL=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./run.sh [--ssl]"
            exit 1
            ;;
    esac
done

# Auto-detect conda environment
detect_conda_env() {
    if command -v conda &> /dev/null; then
        for env in learn_ai qwen3-tts qwen-tts; do
            if conda env list | grep -q "^$env "; then
                echo "$env"
                return
            fi
        done
    fi
    echo ""
}

# Activate conda environment if found
CONDA_ENV=$(detect_conda_env)
if [ -n "$CONDA_ENV" ]; then
    echo "🔧 Activating conda environment: $CONDA_ENV"
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "$CONDA_ENV"
    
    # Fix potential cuDNN conflicts by unsetting LD_LIBRARY_PATH
    unset LD_LIBRARY_PATH
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Build uvicorn command
CMD="python -m uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000}"

# Add SSL options if requested
if [ "$USE_SSL" = true ]; then
    CERT_FILE="${SSL_CERTFILE:-./certs/cert.pem}"
    KEY_FILE="${SSL_KEYFILE:-./certs/key.pem}"
    
    # Check if certificates exist
    if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
        echo "❌ SSL certificates not found!"
        echo ""
        echo "Generate certificates with:"
        echo "  ./scripts/generate_ssl_certs.sh"
        echo ""
        exit 1
    fi
    
    CMD="$CMD --ssl-certfile $CERT_FILE --ssl-keyfile $KEY_FILE"
    echo "🔐 HTTPS enabled with certificates:"
    echo "   Cert: $CERT_FILE"
    echo "   Key:  $KEY_FILE"
    echo ""
fi

echo "🚀 Starting Qwen3-TTS Server..."
echo "   URL: $([ "$USE_SSL" = true ] && echo 'https' || echo 'http')://${HOST:-0.0.0.0}:${PORT:-8000}"
echo ""

# Run the server
exec $CMD
