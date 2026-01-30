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
        
        # Run warmup if enabled
        if settings.enable_warmup:
            await warmup_models()
    else:
        logger.info("Models will be loaded on first request (lazy loading)")
    
    yield
    
    logger.info("Shutting down Qwen3-TTS API Server")


async def warmup_models():
    """
    Warm up loaded models with test generations
    """
    logger.info("Running model warmup...")
    
    try:
        # Warmup CustomVoice if loaded
        if model_manager.is_loaded("custom_voice"):
            logger.info("Warming up CustomVoice model...")
            model = model_manager.get_custom_voice_model()
            _ = model.generate_custom_voice(
                text=settings.warmup_text,
                language="Auto",
                speaker="Ryan",
                instruct="",
            )
            logger.info("CustomVoice model warmed up")
        
        # Warmup VoiceDesign if loaded
        if model_manager.is_loaded("voice_design"):
            logger.info("Warming up VoiceDesign model...")
            model = model_manager.get_voice_design_model()
            _ = model.generate_voice_design(
                text=settings.warmup_text,
                language="Auto",
                instruct="A clear professional voice",
            )
            logger.info("VoiceDesign model warmed up")
        
        # Warmup Base model if loaded (requires creating a dummy voice prompt)
        if model_manager.is_loaded("base"):
            logger.info("Warming up Base model...")
            model = model_manager.get_base_model()
            
            # Create a simple sine wave as dummy reference audio
            import numpy as np
            duration = 1.0  # 1 second
            sample_rate = 24000
            frequency = 440.0  # A4 note
            t = np.linspace(0, duration, int(sample_rate * duration))
            dummy_audio = np.sin(2 * np.pi * frequency * t).astype(np.float32)
            
            # Create dummy voice prompt
            dummy_prompt = model.create_voice_clone_prompt(
                ref_audio=(dummy_audio, sample_rate),
                ref_text=settings.warmup_text,
                x_vector_only_mode=False,
            )
            
            # Generate with dummy prompt
            _ = model.generate_voice_clone(
                text=settings.warmup_text,
                language="Auto",
                voice_clone_prompt=dummy_prompt,
            )
            logger.info("Base model warmed up")
        
        logger.info("Model warmup complete")
        
    except Exception as e:
        logger.warning(f"Warmup failed (non-critical): {e}")


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
