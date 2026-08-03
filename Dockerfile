# syntax=docker/dockerfile:1
# ============================================================================
# Qwen3-TTS Server Docker Image (multi-stage build)
#
# Nothing in the GPU stack is compiled from source:
#   - torch / torchaudio come from the PyTorch CUDA wheel index
#   - Flash Attention 2 comes from an official prebuilt wheel
# So the image needs no CUDA toolchain (nvcc) and the build takes minutes
# instead of hours. The CUDA runtime itself ships inside the torch wheels
# (nvidia-*-cu12), which is why a plain Python base image is enough: only the
# host NVIDIA driver is required, exposed via the NVIDIA Container Toolkit.
#
# PYTHON_IMAGE / TORCH_VERSION / TORCH_CUDA / FLASH_ATTN_WHEEL are a MATCHED
# SET. The wheel filename encodes the CUDA major, torch minor, C++ ABI and
# CPython version it was built against, so all four move together. Step 4 of
# the builder stage re-derives those constraints from the filename and fails
# the build if the installed environment does not satisfy them -- a mismatch
# must surface here, not hours later at inference time.
#
# Prebuilt wheels: https://github.com/Dao-AILab/flash-attention/releases
#
# Prerequisites: frontend/dist must exist (run ./run.sh or `npm run build`).
#
# Build:
#   docker build -t linkary/qwen-tts-server:latest .
# ============================================================================

ARG PYTHON_IMAGE=python:3.12-slim-bookworm

# ==========================================
# Stage 1: Builder (assembles the virtualenv)
# ==========================================
FROM ${PYTHON_IMAGE} AS builder

# Build arguments
ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_TRUSTED_HOST=

# Matched GPU stack -- see the header before changing any of these.
ARG TORCH_VERSION=2.8.0
ARG TORCH_CUDA=cu128
ARG FLASH_ATTN_VERSION=2.8.3.post1
ARG FLASH_ATTN_WHEEL=flash_attn-2.8.3.post1+cu12torch2.8cxx11abiTRUE-cp312-cp312-linux_x86_64.whl

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# build-essential is only a fallback for dependencies that ship no manylinux
# wheel for this interpreter; nothing here is expected to compile.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Isolate our dependencies in a venv that can be copied into the runtime stage.
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install packaging tools
RUN pip install --default-timeout=100 -i ${PIP_INDEX_URL} ${PIP_TRUSTED_HOST:+--trusted-host ${PIP_TRUSTED_HOST}} \
    --upgrade pip setuptools wheel

WORKDIR /app

# 1. Pin torch FIRST. requirements.txt deliberately omits it, so if this step
#    were missing, torch would arrive as a transitive dependency of
#    qwen-tts -> accelerate and resolve to whatever CUDA build PyPI currently
#    defaults to -- which is how this image silently ended up with a CUDA 13
#    torch on a CUDA 12 toolchain.
RUN pip install --default-timeout=100 --index-url https://download.pytorch.org/whl/${TORCH_CUDA} \
    torch==${TORCH_VERSION} torchaudio==${TORCH_VERSION}

# 2. Application dependencies. torch/torchaudio are already satisfied, and
#    there is no --upgrade, so pip leaves them untouched.
COPY requirements.txt .
RUN pip install --default-timeout=100 -i ${PIP_INDEX_URL} ${PIP_TRUSTED_HOST:+--trusted-host ${PIP_TRUSTED_HOST}} \
    -r requirements.txt

# 3. Flash Attention 2 from an official prebuilt wheel (no nvcc, no compile).
RUN pip install --default-timeout=100 \
    "https://github.com/Dao-AILab/flash-attention/releases/download/v${FLASH_ATTN_VERSION}/${FLASH_ATTN_WHEEL}"

# 4. Enforce the matched-set contract described in the header.
RUN FLASH_ATTN_WHEEL="${FLASH_ATTN_WHEEL}" \
    FLASH_ATTN_VERSION="${FLASH_ATTN_VERSION}" \
    TORCH_VERSION="${TORCH_VERSION}" \
    TORCH_CUDA="${TORCH_CUDA}" \
    python - <<'PY'
import os
import re
import sys
from importlib.metadata import version

import torch

wheel = os.environ['FLASH_ATTN_WHEEL']
spec = re.match(
    r'flash_attn-(?P<fa>.+?)\+cu(?P<cuda_major>\d+)torch(?P<torch_minor>[\d.]+)'
    r'cxx11abi(?P<abi>TRUE|FALSE)-(?P<cpython>cp\d+)-',
    wheel,
)
if spec is None:
    raise SystemExit(f'Cannot parse FLASH_ATTN_WHEEL: {wheel!r}')

torch_version, _, cuda_build = torch.__version__.partition('+')

# installed value -> value the pins and the wheel filename require
contract = {
    'torch version': (torch_version, os.environ['TORCH_VERSION']),
    'torch CUDA build': (cuda_build, os.environ['TORCH_CUDA']),
    'torch minor (wheel)': ('.'.join(torch_version.split('.')[:2]), spec['torch_minor']),
    'CUDA major (wheel)': ((torch.version.cuda or '').split('.')[0], spec['cuda_major']),
    'CPython (wheel)': ('cp{}{}'.format(*sys.version_info[:2]), spec['cpython']),
    'C++11 ABI (wheel)': (str(bool(torch._C._GLIBCXX_USE_CXX11_ABI)).upper(), spec['abi']),
    'flash_attn version': (version('flash_attn').partition('+')[0], os.environ['FLASH_ATTN_VERSION']),
}

drift = {name: pair for name, pair in contract.items() if pair[0] != pair[1]}
if drift:
    print('Pinned GPU stack is inconsistent:', file=sys.stderr)
    for name, (installed, required) in drift.items():
        print(f'  {name}: installed {installed!r}, requires {required!r}', file=sys.stderr)
    print('See the Dockerfile header: these pins move as a matched set.', file=sys.stderr)
    raise SystemExit(1)

print(f'GPU stack verified: torch {torch.__version__}, flash_attn {version("flash_attn")}')
PY

# ==========================================
# Stage 2: Runtime (slimmer image)
# ==========================================
FROM ${PYTHON_IMAGE} AS runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/venv/bin:$PATH"

# Kept for parity with the CUDA base images this stage replaced: the NVIDIA
# Container Toolkit reads these when a container is started with
# `runtime: nvidia` instead of `--gpus` / compose device reservations.
ENV NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility

# ffmpeg / libsndfile1 / sox: audio decode and resampling.
# libmagic1: python-magic, used by app/utils/audio.py for upload sniffing.
# libgomp1: OpenMP runtime needed by scikit-learn and onnxruntime.
# curl: HEALTHCHECK below.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    sox \
    libsox-fmt-all \
    libmagic1 \
    libgomp1 \
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
