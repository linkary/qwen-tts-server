"""
VoiceDesign API endpoints
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Response
from sse_starlette.sse import EventSourceResponse
from app.auth import verify_api_key
from app.models.schemas import (
    VoiceDesignRequest,
    VoiceDesignBatchRequest,
    AudioResponse,
    BatchAudioResponse,
)
from app.models.manager import model_manager
from app.utils.audio import numpy_to_wav_bytes, numpy_to_base64
from app.utils.streaming import stream_audio_base64_chunks, create_sse_message

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
                    "Content-Disposition": "attachment; filename=voice_design.wav"
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
        
        # Stream audio chunks
        async def generate():
            yield create_sse_message(f'{{"sample_rate": {sr}}}', "metadata")
            
            async for chunk_base64 in stream_audio_base64_chunks(wavs[0], sr):
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
