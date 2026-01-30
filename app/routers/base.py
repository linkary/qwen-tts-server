"""
Base model API endpoints for voice cloning
"""
import logging
import uuid
import time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File, Form
from sse_starlette.sse import EventSourceResponse
from app.auth import verify_api_key
from app.config import settings
from app.models.schemas import (
    VoiceCloneRequest,
    CreatePromptRequest,
    CreatePromptResponse,
    GenerateWithPromptRequest,
    AudioResponse,
)
from app.models.manager import (
    model_manager,
    store_voice_clone_prompt,
    get_voice_clone_prompt,
)
from app.utils.audio import (
    numpy_to_wav_bytes,
    numpy_to_base64,
    prepare_ref_audio,
    apply_speed,
)
from app.utils.streaming import stream_audio_base64_chunks, create_sse_message
from app.utils.caching import get_voice_cache
from app.utils.metrics import PerformanceTracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/base", tags=["base"])


@router.post("/clone")
async def clone_voice(
    request: VoiceCloneRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Generate speech using Base model with voice cloning from reference audio
    
    Returns audio file (WAV) or base64 encoded audio based on response_format
    """
    # Initialize performance tracker
    tracker = PerformanceTracker()
    tracker.start()
    
    try:
        logger.info("Generating voice clone")
        
        # Validate inputs
        if not request.ref_audio_url and not request.ref_audio_base64:
            raise HTTPException(
                status_code=400,
                detail="Either ref_audio_url or ref_audio_base64 must be provided"
            )
        
        if not request.x_vector_only_mode and not request.ref_text:
            raise HTTPException(
                status_code=400,
                detail="ref_text is required when x_vector_only_mode is False"
            )
        
        # Get model
        model = model_manager.get_base_model()
        
        # Prepare reference audio (with preprocessing)
        ref_audio = await prepare_ref_audio(
            ref_audio_url=request.ref_audio_url,
            ref_audio_base64=request.ref_audio_base64,
            preprocess=True,
            validate=False,  # URL/base64 already validated by client
        )
        
        if ref_audio is None:
            raise HTTPException(status_code=400, detail="Failed to load reference audio")
        
        audio_data, sample_rate = ref_audio
        
        # Try to use cache if enabled
        voice_prompt = None
        if settings.voice_cache_enabled:
            cache = get_voice_cache()
            voice_prompt = cache.get(
                audio_data,
                sample_rate,
                request.ref_text,
                request.x_vector_only_mode
            )
            if voice_prompt is not None:
                tracker.set_cache_status("hit")
                logger.debug("Using cached voice prompt")
        
        # Create prompt if not cached
        if voice_prompt is None:
            tracker.set_cache_status("miss")
            voice_prompt = model.create_voice_clone_prompt(
                ref_audio=(audio_data, sample_rate),
                ref_text=request.ref_text if not request.x_vector_only_mode else None,
                x_vector_only_mode=request.x_vector_only_mode,
            )
            
            # Cache the prompt if enabled
            if settings.voice_cache_enabled:
                cache = get_voice_cache()
                cache.put(
                    audio_data,
                    sample_rate,
                    request.ref_text,
                    request.x_vector_only_mode,
                    voice_prompt
                )
                logger.debug("Cached voice prompt")
        
        # Generate audio with voice clone prompt
        wavs, sr = model.generate_voice_clone(
            text=request.text,
            language=request.language,
            voice_clone_prompt=voice_prompt,
        )
        
        # Track metrics
        tracker.mark_generation()
        audio_duration = len(wavs[0]) / sr
        tracker.set_audio_duration(audio_duration)
        
        # Log performance
        if settings.enable_performance_logging:
            tracker.log_metrics(logger)
        
        # Return based on format
        if request.response_format == "base64":
            audio_base64 = numpy_to_base64(wavs[0], sr)
            return AudioResponse(
                audio=audio_base64,
                sample_rate=sr,
                format="wav"
            )
        else:
            # Return WAV file with performance headers
            wav_bytes = numpy_to_wav_bytes(wavs[0], sr)
            response = Response(
                content=wav_bytes,
                media_type="audio/wav",
                headers={
                    "Content-Disposition": "attachment; filename=voice_clone.wav",
                    **tracker.get_headers()
                }
            )
            return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating voice clone: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clone-stream")
async def clone_voice_stream(
    request: VoiceCloneRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Generate speech using Base model with voice cloning and streaming output
    
    Returns Server-Sent Events with audio chunks
    """
    # Initialize performance tracker
    tracker = PerformanceTracker()
    tracker.start()
    
    try:
        logger.info("Generating voice clone stream")
        
        # Validate inputs
        if not request.ref_audio_url and not request.ref_audio_base64:
            raise HTTPException(
                status_code=400,
                detail="Either ref_audio_url or ref_audio_base64 must be provided"
            )
        
        if not request.x_vector_only_mode and not request.ref_text:
            raise HTTPException(
                status_code=400,
                detail="ref_text is required when x_vector_only_mode is False"
            )
        
        # Get model
        model = model_manager.get_base_model()
        
        # Prepare reference audio (with preprocessing)
        ref_audio = await prepare_ref_audio(
            ref_audio_url=request.ref_audio_url,
            ref_audio_base64=request.ref_audio_base64,
            preprocess=True,
            validate=False,
        )
        
        if ref_audio is None:
            raise HTTPException(status_code=400, detail="Failed to load reference audio")
        
        audio_data, sample_rate = ref_audio
        
        # Try to use cache if enabled
        voice_prompt = None
        if settings.voice_cache_enabled:
            cache = get_voice_cache()
            voice_prompt = cache.get(
                audio_data,
                sample_rate,
                request.ref_text,
                request.x_vector_only_mode
            )
            if voice_prompt is not None:
                tracker.set_cache_status("hit")
                logger.debug("Using cached voice prompt")
        
        # Create prompt if not cached
        if voice_prompt is None:
            tracker.set_cache_status("miss")
            voice_prompt = model.create_voice_clone_prompt(
                ref_audio=(audio_data, sample_rate),
                ref_text=request.ref_text if not request.x_vector_only_mode else None,
                x_vector_only_mode=request.x_vector_only_mode,
            )
            
            # Cache the prompt if enabled
            if settings.voice_cache_enabled:
                cache = get_voice_cache()
                cache.put(
                    audio_data,
                    sample_rate,
                    request.ref_text,
                    request.x_vector_only_mode,
                    voice_prompt
                )
                logger.debug("Cached voice prompt")
        
        # Generate audio with voice clone prompt
        wavs, sr = model.generate_voice_clone(
            text=request.text,
            language=request.language,
            voice_clone_prompt=voice_prompt,
        )
        
        # Apply speed adjustment if requested
        audio_data = wavs[0]
        if request.speed != 1.0:
            audio_data = apply_speed(audio_data, sr, request.speed)
        
        # Track metrics
        tracker.mark_generation()
        audio_duration = len(audio_data) / sr
        tracker.set_audio_duration(audio_duration)
        
        # Log performance
        if settings.enable_performance_logging:
            tracker.log_metrics(logger)
        
        # Stream audio chunks
        async def generate():
            # Send metadata with performance info
            metadata = {
                "sample_rate": sr,
                **tracker.get_metrics()
            }
            yield create_sse_message(str(metadata).replace("'", '"'), "metadata")
            
            async for chunk_base64 in stream_audio_base64_chunks(audio_data, sr):
                yield create_sse_message(chunk_base64, "audio")
            
            yield create_sse_message("complete", "done")
        
        return EventSourceResponse(generate())
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating voice clone stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-prompt", response_model=CreatePromptResponse)
async def create_voice_clone_prompt(
    request: CreatePromptRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Create a reusable voice clone prompt from reference audio
    
    Returns a prompt_id that can be used for subsequent generation requests
    """
    try:
        logger.info("Creating voice clone prompt")
        
        # Validate inputs
        if not request.ref_audio_url and not request.ref_audio_base64:
            raise HTTPException(
                status_code=400,
                detail="Either ref_audio_url or ref_audio_base64 must be provided"
            )
        
        if not request.x_vector_only_mode and not request.ref_text:
            raise HTTPException(
                status_code=400,
                detail="ref_text is required when x_vector_only_mode is False"
            )
        
        # Get model
        model = model_manager.get_base_model()
        
        # Prepare reference audio
        ref_audio = await prepare_ref_audio(
            ref_audio_url=request.ref_audio_url,
            ref_audio_base64=request.ref_audio_base64,
        )
        
        if ref_audio is None:
            raise HTTPException(status_code=400, detail="Failed to load reference audio")
        
        # Create voice clone prompt
        prompt_items = model.create_voice_clone_prompt(
            ref_audio=ref_audio,
            ref_text=request.ref_text if not request.x_vector_only_mode else None,
            x_vector_only_mode=request.x_vector_only_mode,
        )
        
        # Generate unique prompt ID
        prompt_id = str(uuid.uuid4())
        
        # Store prompt
        store_voice_clone_prompt(prompt_id, {
            "prompt_items": prompt_items,
            "ref_text": request.ref_text,
            "x_vector_only_mode": request.x_vector_only_mode,
        })
        
        logger.info(f"Created voice clone prompt with ID: {prompt_id}")
        
        return CreatePromptResponse(
            prompt_id=prompt_id,
            message="Prompt created successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating voice clone prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-with-prompt")
async def generate_with_voice_clone_prompt(
    request: GenerateWithPromptRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Generate speech using a saved voice clone prompt
    
    Returns audio file (WAV) or base64 encoded audio based on response_format
    """
    try:
        logger.info(f"Generating with voice clone prompt: {request.prompt_id}")
        
        # Get stored prompt
        prompt_data = get_voice_clone_prompt(request.prompt_id)
        if prompt_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Prompt ID not found: {request.prompt_id}"
            )
        
        # Get model
        model = model_manager.get_base_model()
        
        # Generate audio with saved prompt
        wavs, sr = model.generate_voice_clone(
            text=request.text,
            language=request.language,
            voice_clone_prompt=prompt_data["prompt_items"],
        )
        
        # Return based on format
        if request.response_format == "base64":
            audio_base64 = numpy_to_base64(wavs[0], sr)
            return AudioResponse(
                audio=audio_base64,
                sample_rate=sr,
                format="wav"
            )
        else:
            # Return WAV file
            wav_bytes = numpy_to_wav_bytes(wavs[0], sr)
            return Response(
                content=wav_bytes,
                media_type="audio/wav",
                headers={
                    "Content-Disposition": "attachment; filename=voice_clone_prompt.wav"
                }
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating with voice clone prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-ref-audio")
async def upload_reference_audio(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    """
    Upload reference audio file and get base64 encoded data
    
    Utility endpoint for converting uploaded files to base64 for use in other endpoints
    """
    try:
        logger.info(f"Uploading reference audio: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Validate it's audio
        if not file.content_type or not file.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Must be audio file."
            )
        
        # Convert to base64
        import base64
        audio_base64 = base64.b64encode(content).decode("utf-8")
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "audio_base64": audio_base64,
            "message": "File uploaded and encoded successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading reference audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/stats")
async def get_cache_stats(api_key: str = Depends(verify_api_key)):
    """
    Get voice prompt cache statistics
    
    Returns cache hit rate, size, and other metrics
    """
    if not settings.voice_cache_enabled:
        return {
            "enabled": False,
            "message": "Voice cache is disabled"
        }
    
    try:
        cache = get_voice_cache()
        stats = cache.get_stats()
        
        return {
            "enabled": True,
            **stats
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear")
async def clear_cache(api_key: str = Depends(verify_api_key)):
    """
    Clear all cached voice prompts
    
    Useful for freeing memory or forcing re-extraction
    """
    if not settings.voice_cache_enabled:
        return {
            "enabled": False,
            "message": "Voice cache is disabled"
        }
    
    try:
        cache = get_voice_cache()
        cache.clear()
        
        return {
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))
