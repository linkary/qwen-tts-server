#!/bin/bash

# Docker Hub publish script for Qwen3-TTS Server
# Usage: ./scripts/docker-publish.sh [VERSION]
# Example: ./scripts/docker-publish.sh 1.0.0
#
# This is the local/manual publishing path. CI publishes through
# .github/workflows/docker-publish.yml instead, so that it can use buildx
# layer caching and docker/metadata-action tagging.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# ==============================================================================
# Configuration
# ==============================================================================

# Load .env file from scripts directory if it exists (for local development)
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "📄 Loading configuration from $SCRIPT_DIR/.env..."
    # Export variables from .env
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi

# Docker Hub configuration
DOCKER_HUB_USER="${DOCKERHUB_USER:-${DOCKER_HUB_USER:-linkary}}"
IMAGE_NAME="qwen-tts-server"
FULL_IMAGE_NAME="${DOCKER_HUB_USER}/${IMAGE_NAME}"

# Get version from argument
VERSION="${1:-latest}"

echo "========================================"
echo "🚀 Qwen3-TTS Server - Docker Publish"
echo "========================================"
echo "Image:   ${FULL_IMAGE_NAME}"
echo "Version: ${VERSION}"
echo "User:    ${DOCKER_HUB_USER}"
echo "========================================"
echo ""

# ==============================================================================
# 1. Frontend Build (Always Force Rebuild)
# ==============================================================================

echo "📦 Building Frontend..."

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed. Please install Node.js."
    echo "   (Required for building the frontend assets)"
    exit 1
fi

cd frontend

echo "   Running npm ci..."
npm ci

echo "   Running npm run build..."
npm run build

cd ..
echo "✅ Frontend build complete."
echo ""

# ==============================================================================
# 2. Docker Authentication
# ==============================================================================

# Check if DOCKERHUB_TOKEN is provided (CI or local .env)
if [ -n "$DOCKERHUB_TOKEN" ]; then
    echo "🔐 Logging in to Docker Hub..."
    # Use print phrase to avoid leaking token in logs if command fails
    echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKER_HUB_USER" --password-stdin
else
    # Check if already logged in
    if ! docker info 2>/dev/null | grep -q "Username"; then
        echo "⚠️  Not logged in to Docker Hub and DOCKERHUB_TOKEN not found."
        echo "   Please run 'docker login' or set DOCKERHUB_TOKEN in scripts/.env"
        exit 1
    else
        echo "✅ Already logged in to Docker Hub (interactive mode)"
    fi
fi
echo ""

# ==============================================================================
# 3. Build & Push Docker Image
# ==============================================================================

echo "🐳 Building Docker image..."
# Use --platform linux/amd64 if on ARM/M1 for compatibility, OR allow multi-arch if needed.
# For now, we rely on default or host architecture, but ideally for Hub we want amd64.
# Adding --platform for stability on Docker Hub (usually expected to be amd64 for servers)
# ERROR: If we use --platform linux/amd64 on M1 mac without buildx setup, it might be slow.
# Users should use buildx for multi-arch. For simple script, we stick to standard build.

docker build -t "${FULL_IMAGE_NAME}:${VERSION}" .

echo "🏷️  Tagging as latest..."
docker tag "${FULL_IMAGE_NAME}:${VERSION}" "${FULL_IMAGE_NAME}:latest"

echo "📤 Pushing to Docker Hub..."
docker push "${FULL_IMAGE_NAME}:${VERSION}"

if [ "$VERSION" != "latest" ]; then
    echo "📤 Pushing latest tag..."
    docker push "${FULL_IMAGE_NAME}:latest"
fi

echo ""
echo "========================================"
echo "✅ Successfully published!"
echo "========================================"
echo "Run with:"
echo "  docker run -d --gpus all -p 8000:8000 ${FULL_IMAGE_NAME}:${VERSION}"
echo ""
