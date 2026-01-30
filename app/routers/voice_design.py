"""
VoiceDesign API endpoints
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Response
from sse_starlette.sse import EventSourceResponse
from app.auth import verify_api_key
from app.config import settings
from app.models.schemas import (
    VoiceDesignRequest,
    VoiceDesignBatchRequest,
    AudioResponse,
    BatchAudioResponse,
)
from app.models.manager import model_manager
from app.utils.audio import numpy_to_wav_bytes, numpy_to_base64, apply_speed
from app.utils.streaming import stream_audio_base64_chunks, create_sse_message
from app.utils.metrics import PerformanceTracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/voice-design", tags=["voice-design"])


@router.post("/generate")
async def generate_voice_design(
    request: VoiceDesignRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Generate speech using VoiceDesign model with natural language voice description
    
    Returns audio file (WAV) or base64 encoded audio based on response_format
    """
    # Initialize performance tracker
    tracker = PerformanceTracker()
    tracker.start()
    
    try:
        logger.info(f"Generating voice design with instruct: {request.instruct[:50]}...")
        
        # Get model
        model = model_manager.get_voice_design_model()
        
        # Generate audio
        wavs, sr = model.generate_voice_design(
            text=request.text,
            language=request.language,
            instruct=request.instruct,
        )
        
        # Apply speed adjustment if requested
        audio_data = wavs[0]
        if hasattr(request, 'speed') and request.speed != 1.0:
            audio_data = apply_speed(audio_data, sr, request.speed)
        
        # Track metrics
        tracker.mark_generation()
        audio_duration = len(audio_data) / sr
        tracker.set_audio_duration(audio_duration)
        
        # Log performance
        if settings.enable_performance_logging:
            tracker.log_metrics(logger)
        
        # Return based on format
        if request.response_format == "base64":
            audio_base64 = numpy_to_base64(audio_data, sr)
            return AudioResponse(
                audio=audio_base64,
                sample_rate=sr,
                format="wav"
            )
        else:
            # Return WAV file with performance headers
            wav_bytes = numpy_to_wav_bytes(audio_data, sr)
            return Response(
                content=wav_bytes,
                media_type="audio/wav",
                headers={
                    "Content-Disposition": "attachment; filename=voice_design.wav",
                    **tracker.get_headers()
                }
            )
    
    except Exception as e:
        logger.error(f"Error generating voice design: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-stream")
async def generate_voice_design_stream(
    request: VoiceDesignRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Generate speech using VoiceDesign model with streaming output
    
    Returns Server-Sent Events with audio chunks
    """
    # Initialize performance tracker
    tracker = PerformanceTracker()
    tracker.start()
    
    try:
        logger.info(f"Generating voice design stream with instruct: {request.instruct[:50]}...")
        
        # Get model
        model = model_manager.get_voice_design_model()
        
        # Generate audio
        wavs, sr = model.generate_voice_design(
            text=request.text,
            language=request.language,
            instruct=request.instruct,
        )
        
        # Apply speed adjustment if requested
        audio_data = wavs[0]
        if hasattr(request, 'speed') and request.speed != 1.0:
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
    
    except Exception as e:
        logger.error(f"Error generating voice design stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def generate_voice_design_batch(
    request: VoiceDesignBatchRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Generate multiple speech samples using VoiceDesign model
    
    Returns base64 encoded audio array
    """
    try:
        logger.info(f"Batch generating {len(request.texts)} voice design samples")
        
        # Validate input lengths
        if len(request.texts) != len(request.languages) or len(request.texts) != len(request.instructs):
            raise HTTPException(
                status_code=400,
                detail="texts, languages, and instructs must have the same length"
            )
        
        # Get model
        model = model_manager.get_voice_design_model()
        
        # Generate audio
        wavs, sr = model.generate_voice_design(
            text=request.texts,
            language=request.languages,
            instruct=request.instructs,
        )
        
        # Convert to base64
        audio_base64_list = [numpy_to_base64(wav, sr) for wav in wavs]
        
        return BatchAudioResponse(
            audios=audio_base64_list,
            sample_rate=sr,
            format="wav"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating voice design batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))
