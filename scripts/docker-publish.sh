#!/bin/bash

# Docker Hub publish script for Qwen3-TTS Server
# Usage: ./scripts/docker-publish.sh [VERSION]
# Example: ./scripts/docker-publish.sh 1.0.0

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Configuration
DOCKER_HUB_USER="${DOCKER_HUB_USER:-linkary}"
IMAGE_NAME="qwen-tts-server"
FULL_IMAGE_NAME="${DOCKER_HUB_USER}/${IMAGE_NAME}"

# Get version from argument or package.json
VERSION="${1:-latest}"

echo "========================================"
echo "Qwen3-TTS Server - Docker Publish"
echo "========================================"
echo ""
echo "Image: ${FULL_IMAGE_NAME}"
echo "Version: ${VERSION}"
echo ""

# Check if logged in to Docker Hub
if ! docker info 2>/dev/null | grep -q "Username"; then
    echo "⚠️  Not logged in to Docker Hub"
    echo "Please run: docker login"
    exit 1
fi

# Build the image
echo "🔨 Building Docker image..."
docker build -t "${FULL_IMAGE_NAME}:${VERSION}" .

# Tag as latest if not already latest
if [ "$VERSION" != "latest" ]; then
    echo "🏷️  Tagging as latest..."
    docker tag "${FULL_IMAGE_NAME}:${VERSION}" "${FULL_IMAGE_NAME}:latest"
fi

# Push to Docker Hub
echo "📤 Pushing to Docker Hub..."
docker push "${FULL_IMAGE_NAME}:${VERSION}"

if [ "$VERSION" != "latest" ]; then
    docker push "${FULL_IMAGE_NAME}:latest"
fi

echo ""
echo "========================================"
echo "✅ Successfully published!"
echo "========================================"
echo ""
echo "Pull with:"
echo "  docker pull ${FULL_IMAGE_NAME}:${VERSION}"
echo ""
echo "Run with:"
echo "  docker run -d --gpus all -p 8000:8000 ${FULL_IMAGE_NAME}:${VERSION}"
echo ""
