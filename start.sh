#!/bin/bash

# Start script for Qwen3-TTS API Server

set -e

echo "Starting Qwen3-TTS API Server..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration and run again."
    exit 1
fi

# Load environment variables
source .env

# Check if running with Docker
if [ "$1" = "docker" ]; then
    echo "Starting with Docker Compose..."
    docker-compose up -d
    echo "Server started! Access the API at http://localhost:${PORT:-8000}"
    echo "API Documentation: http://localhost:${PORT:-8000}/docs"
else
    echo "Starting locally..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
    
    # Start the server
    echo "Starting uvicorn server..."
    python -m uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000}
fi
