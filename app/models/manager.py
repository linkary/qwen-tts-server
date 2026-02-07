"""
Model manager for lazy loading and caching TTS models
"""
import logging
import threading
from typing import Optional, Dict, Any
from qwen_tts import Qwen3TTSModel
from app.config import settings

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages TTS model loading and caching"""
    
    def __init__(self):
        self._models: Dict[str, Optional[Qwen3TTSModel]] = {
            "custom_voice": None,
            "voice_design": None,
            "base": None,
        }
        self._locks = {
            "custom_voice": threading.Lock(),
            "voice_design": threading.Lock(),
            "base": threading.Lock(),
        }
        self._model_configs = {
            "custom_voice": {
                "model_path": settings.qwen_tts_custom_voice_model,
                "description": "CustomVoice model for preset speakers"
            },
            "voice_design": {
                "model_path": settings.qwen_tts_voice_design_model,
                "description": "VoiceDesign model for voice design"
            },
            "base": {
                "model_path": settings.qwen_tts_base_model,
                "description": "Base model for voice cloning"
            },
        }
    
    def _load_model(self, model_type: str) -> Qwen3TTSModel:
        """
        Load a TTS model
        
        Args:
            model_type: Type of model to load (custom_voice, voice_design, base)
            
        Returns:
            Loaded model instance
        """
        config = self._model_configs[model_type]
        model_path = config["model_path"]
        
        logger.info(f"Loading {config['description']} from {model_path}")
        
        # Build model loading kwargs
        load_kwargs = {
            "device_map": settings.cuda_device,
            "dtype": settings.get_torch_dtype(),
        }
        
        # Add flash attention if enabled
        if settings.use_flash_attention and settings.cuda_device != "cpu":
            load_kwargs["attn_implementation"] = "flash_attention_2"
        
        try:
            model = Qwen3TTSModel.from_pretrained(model_path, **load_kwargs)
            logger.info(f"Successfully loaded {config['description']}")
            return model
        except Exception as e:
            logger.error(f"Failed to load {config['description']}: {e}")
            raise
    
    def get_model(self, model_type: str) -> Qwen3TTSModel:
        """
        Get a TTS model (loads if not already cached)
        
        Args:
            model_type: Type of model (custom_voice, voice_design, base)
            
        Returns:
            The requested model instance
            
        Raises:
            ValueError: If model_type is invalid
            RuntimeError: If model loading fails
        """
        if model_type not in self._models:
            raise ValueError(f"Invalid model type: {model_type}")
        
        # Check if model is already loaded
        if self._models[model_type] is not None:
            return self._models[model_type]
        
        # Load model with thread-safe lock
        with self._locks[model_type]:
            # Double-check after acquiring lock
            if self._models[model_type] is not None:
                return self._models[model_type]
            
            # Load model
            self._models[model_type] = self._load_model(model_type)
            return self._models[model_type]
    
    def get_custom_voice_model(self) -> Qwen3TTSModel:
        """Get CustomVoice model"""
        return self.get_model("custom_voice")
    
    def get_voice_design_model(self) -> Qwen3TTSModel:
        """Get VoiceDesign model"""
        return self.get_model("voice_design")
    
    def get_base_model(self) -> Qwen3TTSModel:
        """Get Base model"""
        return self.get_model("base")
    
    def is_loaded(self, model_type: str) -> bool:
        """Check if a model is loaded"""
        return self._models.get(model_type) is not None
    
    def preload_all_models(self):
        """Preload all models (useful for startup)"""
        logger.info("Preloading all models...")
        for model_type in self._models.keys():
            try:
                self.get_model(model_type)
            except Exception as e:
                logger.error(f"Failed to preload {model_type} model: {e}")
        logger.info("Model preloading complete")
    
    def unload_model(self, model_type: str):
        """
        Unload a model to free memory
        
        Args:
            model_type: Type of model to unload
        """
        if model_type in self._models and self._models[model_type] is not None:
            with self._locks[model_type]:
                logger.info(f"Unloading {model_type} model")
                self._models[model_type] = None
                
                # Trigger garbage collection
                import gc
                import torch
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()


# Global model manager instance
model_manager = ModelManager()


# Voice clone prompt storage (in-memory for now)
# In production, consider using Redis or similar
_voice_clone_prompts: Dict[str, Dict[str, Any]] = {}
_prompts_lock = threading.Lock()


def store_voice_clone_prompt(prompt_id: str, prompt_data: Dict[str, Any]):
    """Store a voice clone prompt"""
    with _prompts_lock:
        _voice_clone_prompts[prompt_id] = prompt_data


def get_voice_clone_prompt(prompt_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a voice clone prompt"""
    with _prompts_lock:
        return _voice_clone_prompts.get(prompt_id)


def delete_voice_clone_prompt(prompt_id: str):
    """Delete a voice clone prompt"""
    with _prompts_lock:
        if prompt_id in _voice_clone_prompts:
            del _voice_clone_prompts[prompt_id]
