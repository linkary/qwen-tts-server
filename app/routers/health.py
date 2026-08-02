"""
Health check endpoints
"""
from typing import Any, Dict

from fastapi import APIRouter
from app.models.schemas import HealthResponse, ModelsHealthResponse
from app.models.manager import model_manager
from app.utils.inference import get_inference_stats
from app import __version__

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint
    
    Returns service status and version
    """
    return HealthResponse(
        status="healthy",
        version=__version__
    )


@router.get("/health/models", response_model=ModelsHealthResponse)
async def models_health_check():
    """
    Check which models are currently loaded
    
    Returns status of all model types
    """
    return ModelsHealthResponse(
        custom_voice_loaded=model_manager.is_loaded("custom_voice"),
        voice_design_loaded=model_manager.is_loaded("voice_design"),
        base_loaded=model_manager.is_loaded("base"),
        tokenizer_loaded=True  # Tokenizer is part of model loading
    )


@router.get("/health/inference")
async def inference_health_check() -> Dict[str, Any]:
    """
    Inference concurrency and queue state.

    /health cannot detect a wedged inference: it deliberately does not touch the
    inference path, so it stays green while the GPU permits are all held. This
    endpoint exposes the state that distinguishes "idle" from "saturated" from
    "stuck":

    - in_flight == max_concurrent with queued > 0 and a climbing rejected_total
      means the server is saturated. If it never drops, an inference is not
      returning and the process needs recycling — a running native GPU call
      cannot be cancelled from Python.
    - Returns a plain dict rather than a response model because the shape is an
      operational detail, not part of the audio API contract.
    """
    return get_inference_stats()
