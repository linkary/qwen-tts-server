# Qwen3-TTS Server Docker Image (Multi-stage Build)
# 
# Prerequisites: Run `./run.sh` or `npm run build` in frontend/ first
# 
# Build:
#   docker build -t linkary/qwen-tts-server:latest .
#   
# Build with Chinese pip mirror:
#   docker build --build-arg PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ -t linkary/qwen-tts-server:latest .

# ==========================================
# Stage 1: Builder (with CUDA compiler)
# ==========================================
FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04 AS builder

# Build arguments
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    build-essential \
    git \
    wget \
    curl \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create virtual environment
RUN python3.12 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install packaging tools
RUN pip install -i ${PIP_INDEX_URL} ${PIP_TRUSTED_HOST:+--trusted-host ${PIP_TRUSTED_HOST}} --upgrade pip wheel setuptools ninja packaging

# Install PyTorch first (required for flash-attn)
# We install CPU version first if possible to save space? No, flash-attn needs CUDA torch.
# But we are in a CUDA image, so we should install CUDA torch.
# The requirements.txt specifies torch>=2.1.0, which usually pulls CUDA version on Linux.
# To be safe and fast, let's install from the index provided or default to official pytorch wheel if not specified in requirements.
# Actually, let's just follow requirements.txt but use the index url provided.

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies from requirements.txt
RUN pip install -i ${PIP_INDEX_URL} ${PIP_TRUSTED_HOST:+--trusted-host ${PIP_TRUSTED_HOST}} -r requirements.txt

# Install Flash Attention 2
# This requires nvcc which is present in the devel image
RUN pip install -i ${PIP_INDEX_URL} ${PIP_TRUSTED_HOST:+--trusted-host ${PIP_TRUSTED_HOST}} flash-attn>=2.5.0 --no-build-isolation

# ==========================================
# Stage 2: Runtime (Slimmer image)
# ==========================================
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04 AS runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-venv \
    ffmpeg \
    libsndfile1 \
    sox \
    libsox-fmt-all \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/venv /app/venv

# Copy application code
COPY app/ ./app/
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
