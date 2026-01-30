"""
Main FastAPI application
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import __version__
from app.config import settings
from app.models.manager import model_manager
from app.routers import health, custom_voice, voice_design, base

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler
    """
    logger.info("Starting Qwen3-TTS API Server")
    logger.info(f"Version: {__version__}")
    
    # Preload models if configured
    if settings.preload_models:
        logger.info("Preloading models on startup...")
        model_manager.preload_all_models()
    else:
        logger.info("Models will be loaded on first request (lazy loading)")
    
    yield
    
    logger.info("Shutting down Qwen3-TTS API Server")


# Create FastAPI application
app = FastAPI(
    title="Qwen3-TTS API Server",
    description="API server for Qwen3-TTS models supporting CustomVoice, VoiceDesign, and Base (voice cloning) models",
    version=__version__,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(custom_voice.router)
app.include_router(voice_design.router)
app.include_router(base.router)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Qwen3-TTS API Server",
        "version": __version__,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
