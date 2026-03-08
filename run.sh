#!/bin/bash

# Qwen3-TTS Server Run Script
# Unified launcher with Conda environment support
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

ENVIRONMENT:
    Requires Conda with one of these environments: qwen-tts, qwen3-tts
    
    Create environment:
        conda create -n qwen-tts python=3.12
        conda activate qwen-tts
        ./run.sh --setup

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
    
    # Load PORT and API_KEYS from .env for display
    if [ -f .env ]; then
        PORT=$(grep "^PORT=" .env | cut -d'=' -f2)
        _DOCKER_API_KEYS=$(grep "^API_KEYS=" .env | cut -d'=' -f2-)
    fi
    
    # Build auth display for Docker
    if [ -n "$_DOCKER_API_KEYS" ]; then
        IFS=',' read -ra _DKEYS <<< "$_DOCKER_API_KEYS"
        _DMASKED=()
        for _dk in "${_DKEYS[@]}"; do
            _dk=$(echo "$_dk" | xargs)
            _dlen=${#_dk}
            if [ "$_dlen" -le 4 ]; then
                _DMASKED+=("****")
            else
                _DMASKED+=("${_dk:0:2}****${_dk: -2}")
            fi
        done
        _DOCKER_AUTH="🔑 Auth: $(IFS=', '; echo "${_DMASKED[*]}")"
    else
        _DOCKER_AUTH="🔓 Auth: No authentication (open access)"
    fi
    
    docker-compose up -d
    echo ""
    echo "✅ Server started in Docker!"
    echo "   API: http://localhost:${PORT:-8000}"
    echo "   Docs: http://localhost:${PORT:-8000}/docs"
    echo "   $_DOCKER_AUTH"
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
        
        # Only export if not already set in shell environment
        if [ -z "${!key}" ]; then
            export "$key=$value"
        fi
    done < .env
fi

# Save critical server configuration before environment activation
# (conda activation might override shell variables)
SERVER_HOST="${HOST:-0.0.0.0}"
SERVER_PORT="${PORT:-8000}"

# ==============================================================================
# Environment Detection & Activation
# ==============================================================================

activate_environment() {
    CONDA_ENV=$(detect_conda_env)
    if [ -n "$CONDA_ENV" ]; then
        activate_conda "$CONDA_ENV"
    else
        echo "❌ Error: No Conda environment found."
        echo ""
        echo "This project requires Conda. Please create an environment:"
        echo "    conda create -n qwen-tts python=3.12"
        echo "    conda activate qwen-tts"
        echo "    ./run.sh --setup"
        echo ""
        echo "Or use Docker:"
        echo "    ./run.sh --docker"
        exit 1
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
# Frontend Build (ensure latest React app is served)
# ==============================================================================
build_frontend() {
    local frontend_dir="$SCRIPT_DIR/frontend"
    local dist_dir="$frontend_dir/dist"
    
    # Check if frontend directory exists
    if [ ! -d "$frontend_dir" ]; then
        echo "⚠️  Frontend directory not found, skipping build"
        return
    fi
    
    # Check if node_modules exists
    if [ ! -d "$frontend_dir/node_modules" ]; then
        echo "📦 Installing frontend dependencies..."
        (cd "$frontend_dir" && npm install)
    fi
    
    # Check if build is needed (dist missing or source newer than dist)
    local needs_build=false
    
    if [ ! -d "$dist_dir" ]; then
        needs_build=true
        echo "📦 Frontend build not found, building..."
    elif [ -n "$(find "$frontend_dir/src" -newer "$dist_dir/index.html" 2>/dev/null)" ]; then
        needs_build=true
        echo "📦 Frontend source changed, rebuilding..."
    fi
    
    if [ "$needs_build" = true ]; then
        echo "🔨 Building frontend..."
        (cd "$frontend_dir" && npm run build)
        echo "✅ Frontend built successfully"
    else
        echo "✅ Frontend is up to date"
    fi
}

# Build frontend (skip in dev mode as Vite handles it)
if [ "$DEV_MODE" != true ]; then
    build_frontend
fi

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

# Build auth state display
AUTH_DISPLAY=""
if [ -n "$API_KEYS" ]; then
    # Mask each key: show first 2 and last 2 chars, replace middle with ****
    IFS=',' read -ra KEYS <<< "$API_KEYS"
    MASKED_KEYS=()
    for key in "${KEYS[@]}"; do
        key=$(echo "$key" | xargs)  # trim whitespace
        local_len=${#key}
        if [ "$local_len" -le 4 ]; then
            MASKED_KEYS+=("****")
        else
            MASKED_KEYS+=("${key:0:2}****${key: -2}")
        fi
    done
    AUTH_DISPLAY="🔑 Auth: $(IFS=', '; echo "${MASKED_KEYS[*]}")"
else
    AUTH_DISPLAY="🔓 Auth: No authentication (open access)"
fi

echo ""
echo "🚀 Starting Qwen3-TTS Server..."
echo "   URL: $([ "$USE_SSL" = true ] && echo 'https' || echo 'http')://$SERVER_HOST:$SERVER_PORT"
echo "   Docs: $([ "$USE_SSL" = true ] && echo 'https' || echo 'http')://$SERVER_HOST:$SERVER_PORT/docs"
echo "   $AUTH_DISPLAY"
echo ""

# Run the server
exec $CMD
