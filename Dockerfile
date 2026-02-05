# Qwen3-TTS Server Docker Image
# 
# Prerequisites: Run `./run.sh` or `npm run build` in frontend/ first
# 
# Build:
#   docker build -t linkary/qwen-tts-server:latest .
#   
# Build with Chinese pip mirror:
#   docker build --build-arg PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ -t linkary/qwen-tts-server:latest .

FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

# Build arguments
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies (single layer)
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    git \
    wget \
    curl \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set Python 3.12 as default and install pip
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with configurable pip source
RUN pip install -i ${PIP_INDEX_URL} ${PIP_TRUSTED_HOST:+--trusted-host ${PIP_TRUSTED_HOST}} -r requirements.txt

# Try to install flash-attn (may fail on some systems)
RUN pip install flash-attn>=2.5.0 --no-build-isolation 2>/dev/null || \
    echo "Warning: flash-attn installation failed, continuing without it"

# Copy application code
COPY app/ ./app/

# Copy pre-built frontend (run ./run.sh or npm run build first)
COPY frontend/dist ./frontend/dist

# Create directories for models and outputs
RUN mkdir -p /app/models /app/output

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
