# Qwen3-TTS Server Docker Image (Multi-stage Build)
# 
# Prerequisites: Run `./run.sh` or `npm run build` in frontend/ first
# 
# Build:
#   docker build -t linkary/qwen-tts-server:latest .
#   

# ==========================================
# Stage 1: Builder (with CUDA compiler)
# ==========================================
FROM pytorch/pytorch:2.2.1-cuda12.1-cudnn8-devel AS builder

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
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create virtual environment 
# Note: The base image likely has python in /opt/conda. 
# We'll use venv to keep our deps isolated and copyable.
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install packaging tools
RUN pip install --default-timeout=100 -i ${PIP_INDEX_URL} ${PIP_TRUSTED_HOST:+--trusted-host ${PIP_TRUSTED_HOST}} --upgrade pip wheel setuptools ninja packaging

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies from requirements.txt
# Note: torch is commented out in requirements.txt
RUN pip install --default-timeout=100 -i ${PIP_INDEX_URL} ${PIP_TRUSTED_HOST:+--trusted-host ${PIP_TRUSTED_HOST}} -r requirements.txt

# Install Flash Attention 2
# This requires nvcc which is present in the devel image
RUN pip install --default-timeout=100 -i ${PIP_INDEX_URL} ${PIP_TRUSTED_HOST:+--trusted-host ${PIP_TRUSTED_HOST}} flash-attn>=2.5.0 --no-build-isolation

# ==========================================
# Stage 2: Runtime (Slimmer image)
# ==========================================
FROM pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime AS runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
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
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
