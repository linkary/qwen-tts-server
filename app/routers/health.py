"""
Health check endpoints
"""
from fastapi import APIRouter
from app.models.schemas import HealthResponse, ModelsHealthResponse
from app.models.manager import model_manager
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
