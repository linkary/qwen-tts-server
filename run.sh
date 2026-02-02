#!/bin/bash

# Qwen3-TTS Server Run Script
# Unified launcher with support for conda/venv/docker modes
# Usage: ./run.sh [options]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ==============================================================================
# Help Function
# ==============================================================================
show_help() {
    cat << EOF
Qwen3-TTS Server - Unified Launch Script

USAGE:
    ./run.sh [OPTIONS]

OPTIONS:
    --help          Show this help message
    --ssl           Enable HTTPS with SSL certificates
    --setup         Setup mode: install dependencies (useful for first run)
    --docker        Run with Docker Compose
    --venv          Force using venv instead of conda
    --dev           Development mode: enable auto-reload

EXAMPLES:
    # Quick start (auto-detects conda environment)
    ./run.sh

    # First time setup with dependency installation
    ./run.sh --setup

    # Run with HTTPS
    ./run.sh --ssl

    # Run with Docker
    ./run.sh --docker

    # Force venv instead of conda
    ./run.sh --venv

ENVIRONMENT DETECTION:
    Priority: conda > venv > system Python
    - Searches for conda environments: qwen-tts, qwen3-tts
    - Falls back to venv if conda not found (creates if missing)
    - Use --venv to skip conda detection

CONFIGURATION:
    Edit .env file or use environment variables:
    - HOST (default: 0.0.0.0)
    - PORT (default: 8000)
    - SSL_CERTFILE (default: ./certs/cert.pem)
    - SSL_KEYFILE (default: ./certs/key.pem)

EOF
}

# ==============================================================================
# Parse Arguments
# ==============================================================================
USE_SSL=false
SETUP_MODE=false
DOCKER_MODE=false
FORCE_VENV=false
DEV_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            exit 0
            ;;
        --ssl)
            USE_SSL=true
            shift
            ;;
        --setup)
            SETUP_MODE=true
            shift
            ;;
        --docker)
            DOCKER_MODE=true
            shift
            ;;
        --venv)
            FORCE_VENV=true
            shift
            ;;
        --dev)
            DEV_MODE=true
            shift
            ;;
        *)
            echo "❌ Unknown option: $1"
            echo "Run './run.sh --help' for usage information"
            exit 1
            ;;
    esac
done

# ==============================================================================
# Docker Mode
# ==============================================================================
if [ "$DOCKER_MODE" = true ]; then
    echo "🐳 Starting with Docker Compose..."
    
    # Check if .env exists
    if [ ! -f .env ]; then
        echo "⚠️  .env file not found. Copying from .env.example..."
        cp .env.example .env
        echo "✅ Created .env file. Please edit if needed."
    fi
    
    # Load PORT from .env for display (simple extraction for docker mode)
    if [ -f .env ]; then
        PORT=$(grep "^PORT=" .env | cut -d'=' -f2)
    fi
    
    docker-compose up -d
    echo ""
    echo "✅ Server started in Docker!"
    echo "   API: http://localhost:${PORT:-8000}"
    echo "   Docs: http://localhost:${PORT:-8000}/docs"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
    exit 0
fi

# ==============================================================================
# Environment Setup
# ==============================================================================

# Check and initialize .env file
if [ ! -f .env ]; then
    echo "⚠️  .env file not found."
    if [ -f .env.example ]; then
        echo "📝 Copying from .env.example..."
        cp .env.example .env
        echo "✅ Created .env file."
        echo ""
        echo "⚠️  Please review and edit .env with your configuration,"
        echo "   then run this script again."
        echo ""
        exit 1
    else
        echo "❌ .env.example not found. Cannot initialize configuration."
        exit 1
    fi
fi

# Load environment variables from .env file
# Note: We explicitly export to override any existing shell variables
if [ -f .env ]; then
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ $key =~ ^#.*$ || -z $key ]] && continue
        # Remove quotes if present and export
        value="${value%\"}"
        value="${value#\"}"
        export "$key=$value"
    done < .env
fi

# Save critical server configuration before environment activation
# (conda/venv activation might override shell variables)
SERVER_HOST="${HOST:-0.0.0.0}"
SERVER_PORT="${PORT:-8000}"

# ==============================================================================
# Environment Detection & Activation
# ==============================================================================

activate_environment() {
    if [ "$FORCE_VENV" = true ]; then
        # Force venv mode
        activate_venv
    else
        # Try conda first
        CONDA_ENV=$(detect_conda_env)
        if [ -n "$CONDA_ENV" ]; then
            activate_conda "$CONDA_ENV"
        else
            # Fallback to venv
            activate_venv
        fi
    fi
}

# Detect available conda environment
detect_conda_env() {
    if command -v conda &> /dev/null; then
        for env in qwen-tts qwen3-tts; do
            if conda env list | grep -q "^$env "; then
                echo "$env"
                return
            fi
        done
    fi
    echo ""
}

# Activate conda environment
activate_conda() {
    local env_name=$1
    echo "🔧 Activating conda environment: $env_name"
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "$env_name"
    
    # Fix potential cuDNN conflicts by unsetting LD_LIBRARY_PATH
    unset LD_LIBRARY_PATH
    
    echo "✅ Conda environment activated"
}

# Activate or create venv
activate_venv() {
    if [ ! -d "venv" ]; then
        echo "📦 Virtual environment not found. Creating venv..."
        python3 -m venv venv
        echo "✅ Virtual environment created"
    fi
    
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated"
}

# ==============================================================================
# Dependency Installation
# ==============================================================================

if [ "$SETUP_MODE" = true ]; then
    echo ""
    echo "📦 Installing dependencies..."
    pip install --upgrade pip
    pip install -q -r requirements.txt
    echo "✅ Dependencies installed"
    echo ""
fi

# ==============================================================================
# Activate Environment
# ==============================================================================
activate_environment

# ==============================================================================
# SSL Configuration
# ==============================================================================

CMD="python -m uvicorn app.main:app --host $SERVER_HOST --port $SERVER_PORT"

# Add development mode flag
if [ "$DEV_MODE" = true ]; then
    CMD="$CMD --reload"
    echo "🔧 Development mode enabled (auto-reload)"
fi

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
fi

# ==============================================================================
# Start Server
# ==============================================================================

echo ""
echo "🚀 Starting Qwen3-TTS Server..."
echo "   URL: $([ "$USE_SSL" = true ] && echo 'https' || echo 'http')://$SERVER_HOST:$SERVER_PORT"
echo "   Docs: $([ "$USE_SSL" = true ] && echo 'https' || echo 'http')://$SERVER_HOST:$SERVER_PORT/docs"
echo ""

# Run the server
exec $CMD
