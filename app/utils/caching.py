"""
Voice prompt caching utilities
"""
import hashlib
import logging
import threading
import time
from collections import OrderedDict
from typing import Optional, Dict, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class VoicePromptCache:
    """
    Thread-safe LRU cache for voice clone prompts
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """
        Initialize cache
        
        Args:
            max_size: Maximum number of prompts to cache
            ttl_seconds: Time-to-live for cached prompts in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
    
    def _generate_cache_key(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        ref_text: Optional[str],
        x_vector_only_mode: bool
    ) -> str:
        """
        Generate a unique cache key based on audio content and parameters
        
        Args:
            audio_data: Reference audio data
            sample_rate: Sample rate
            ref_text: Reference text transcript
            x_vector_only_mode: Whether using x-vector only mode
            
        Returns:
            Hash-based cache key
        """
        # Create hash from audio data (first 1000 samples to be efficient)
        audio_sample = audio_data[:min(1000, len(audio_data))].tobytes()
        audio_hash = hashlib.sha256(audio_sample).hexdigest()[:16]
        
        # Include ref_text and mode in the key
        text_part = ref_text if ref_text else "no_text"
        mode_part = "xvec" if x_vector_only_mode else "full"
        
        # Combine into cache key
        cache_key = f"{audio_hash}_{text_part[:32]}_{mode_part}_{sample_rate}"
        return hashlib.md5(cache_key.encode()).hexdigest()
    
    def get(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        ref_text: Optional[str],
        x_vector_only_mode: bool
    ) -> Optional[Any]:
        """
        Get cached voice prompt if available
        
        Args:
            audio_data: Reference audio data
            sample_rate: Sample rate
            ref_text: Reference text transcript
            x_vector_only_mode: Whether using x-vector only mode
            
        Returns:
            Cached prompt items or None if not found/expired
        """
        cache_key = self._generate_cache_key(
            audio_data, sample_rate, ref_text, x_vector_only_mode
        )
        
        with self._lock:
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                
                # Check if expired
                if time.time() - entry["timestamp"] > self.ttl_seconds:
                    logger.debug(f"Cache entry expired: {cache_key}")
                    del self._cache[cache_key]
                    self._misses += 1
                    return None
                
                # Move to end (most recently used)
                self._cache.move_to_end(cache_key)
                
                self._hits += 1
                logger.debug(f"Cache hit: {cache_key}")
                return entry["prompt_items"]
            else:
                self._misses += 1
                logger.debug(f"Cache miss: {cache_key}")
                return None
    
    def put(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        ref_text: Optional[str],
        x_vector_only_mode: bool,
        prompt_items: Any
    ) -> str:
        """
        Store voice prompt in cache
        
        Args:
            audio_data: Reference audio data
            sample_rate: Sample rate
            ref_text: Reference text transcript
            x_vector_only_mode: Whether using x-vector only mode
            prompt_items: Voice clone prompt to cache
            
        Returns:
            Cache key used for storage
        """
        cache_key = self._generate_cache_key(
            audio_data, sample_rate, ref_text, x_vector_only_mode
        )
        
        with self._lock:
            # Evict oldest if at capacity
            if len(self._cache) >= self.max_size and cache_key not in self._cache:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._evictions += 1
                logger.debug(f"Evicted cache entry: {oldest_key}")
            
            # Store new entry
            self._cache[cache_key] = {
                "prompt_items": prompt_items,
                "timestamp": time.time(),
                "ref_text": ref_text,
                "x_vector_only_mode": x_vector_only_mode,
            }
            
            # Move to end
            self._cache.move_to_end(cache_key)
            
            logger.debug(f"Cached voice prompt: {cache_key}")
            return cache_key
    
    def clear(self):
        """Clear all cached prompts"""
        with self._lock:
            self._cache.clear()
            logger.info("Voice prompt cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_rate_percent": round(hit_rate, 2),
                "total_requests": total_requests,
            }
    
    def reset_stats(self):
        """Reset cache statistics"""
        with self._lock:
            self._hits = 0
            self._misses = 0
            self._evictions = 0
            logger.info("Cache statistics reset")


# Global cache instance
_voice_cache: Optional[VoicePromptCache] = None
_cache_lock = threading.Lock()


def get_voice_cache() -> VoicePromptCache:
    """Get or create global voice cache instance"""
    global _voice_cache
    
    if _voice_cache is None:
        with _cache_lock:
            if _voice_cache is None:
                from app.config import settings
                _voice_cache = VoicePromptCache(
                    max_size=settings.voice_cache_max_size,
                    ttl_seconds=settings.voice_cache_ttl_seconds
                )
                logger.info(
                    f"Initialized voice cache: max_size={settings.voice_cache_max_size}, "
                    f"ttl={settings.voice_cache_ttl_seconds}s"
                )
    
    return _voice_cache
