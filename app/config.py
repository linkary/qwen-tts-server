"""
Configuration management using Pydantic Settings
"""
import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Model Configuration
    qwen_tts_custom_voice_model: str = Field(
        default="Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
        description="Path or HuggingFace ID for CustomVoice model"
    )
    qwen_tts_voice_design_model: str = Field(
        default="Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
        description="Path or HuggingFace ID for VoiceDesign model"
    )
    qwen_tts_base_model: str = Field(
        default="Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        description="Path or HuggingFace ID for Base model"
    )
    qwen_tts_tokenizer: str = Field(
        default="Qwen/Qwen3-TTS-Tokenizer-12Hz",
        description="Path or HuggingFace ID for Tokenizer"
    )
    
    # Device Configuration
    cuda_device: str = Field(default="cuda:0", description="CUDA device to use")
    model_dtype: str = Field(default="bfloat16", description="Model dtype (float16, bfloat16, float32)")
    use_flash_attention: bool = Field(default=True, description="Use Flash Attention 2")
    
    # API Configuration
    api_keys: str = Field(
        default="",
        description="Comma-separated list of API keys for authentication"
    )
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # Model Caching
    hf_home: Optional[str] = Field(default=None, description="HuggingFace cache directory")
    model_cache_dir: Optional[str] = Field(default=None, description="Model cache directory")
    
    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    
    # Model Loading
    preload_models: bool = Field(
        default=False,
        description="Preload all models on startup (requires more GPU memory)"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_api_keys_list(self) -> List[str]:
        """Parse API keys from comma-separated string"""
        if not self.api_keys:
            return []
        return [key.strip() for key in self.api_keys.split(",") if key.strip()]
    
    def get_torch_dtype(self):
        """Convert dtype string to torch dtype"""
        import torch
        dtype_map = {
            "float16": torch.float16,
            "bfloat16": torch.bfloat16,
            "float32": torch.float32,
        }
        return dtype_map.get(self.model_dtype.lower(), torch.bfloat16)


# Global settings instance
settings = Settings()

# Set HuggingFace cache directory if specified
if settings.hf_home:
    os.environ["HF_HOME"] = settings.hf_home
if settings.model_cache_dir:
    os.environ["TRANSFORMERS_CACHE"] = settings.model_cache_dir
