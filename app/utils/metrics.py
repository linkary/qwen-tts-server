"""
Performance metrics utilities
"""
import time
import logging
from typing import Dict, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """Track performance metrics for audio generation"""
    
    def __init__(self):
        self.start_time: Optional[float] = None
        self.generation_time: Optional[float] = None
        self.preprocessing_time: Optional[float] = None
        self.cache_status: str = "miss"
        self.audio_duration: Optional[float] = None
    
    def start(self):
        """Start timing"""
        self.start_time = time.time()
    
    def mark_preprocessing(self, duration: float):
        """Mark preprocessing time"""
        self.preprocessing_time = duration
    
    def mark_generation(self):
        """Mark generation complete"""
        if self.start_time is not None:
            self.generation_time = time.time() - self.start_time
    
    def set_audio_duration(self, duration: float):
        """Set audio duration in seconds"""
        self.audio_duration = duration
    
    def set_cache_status(self, status: str):
        """Set cache status (hit/miss)"""
        self.cache_status = status
    
    def get_rtf(self) -> Optional[float]:
        """
        Calculate Real-Time Factor
        
        Returns:
            RTF value (generation_time / audio_duration) or None
        """
        if self.generation_time is not None and self.audio_duration is not None and self.audio_duration > 0:
            return self.generation_time / self.audio_duration
        return None
    
    def log_metrics(self, logger_instance: logging.Logger = logger):
        """Log performance metrics"""
        if self.generation_time is None:
            return
        
        rtf = self.get_rtf()
        
        if rtf is not None:
            log_msg = (
                f"Generation completed in {self.generation_time:.2f}s "
                f"(audio: {self.audio_duration:.2f}s, RTF: {rtf:.2f}x) "
                f"[cache: {self.cache_status}]"
            )
        else:
            log_msg = f"Generation completed in {self.generation_time:.2f}s [cache: {self.cache_status}]"
        
        if self.preprocessing_time is not None:
            log_msg += f" [preprocessing: {self.preprocessing_time:.2f}s]"
        
        logger_instance.info(log_msg)
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get performance metrics as response headers
        
        Returns:
            Dictionary of header names to values
        """
        headers = {}
        
        if self.generation_time is not None:
            headers["X-Generation-Time"] = f"{self.generation_time:.3f}"
        
        if self.audio_duration is not None:
            headers["X-Audio-Duration"] = f"{self.audio_duration:.3f}"
        
        rtf = self.get_rtf()
        if rtf is not None:
            headers["X-RTF"] = f"{rtf:.3f}"
        
        headers["X-Cache-Status"] = self.cache_status
        
        if self.preprocessing_time is not None:
            headers["X-Preprocessing-Time"] = f"{self.preprocessing_time:.3f}"
        
        return headers
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics as dictionary
        
        Returns:
            Dictionary with all tracked metrics
        """
        return {
            "generation_time": self.generation_time,
            "audio_duration": self.audio_duration,
            "rtf": self.get_rtf(),
            "cache_status": self.cache_status,
            "preprocessing_time": self.preprocessing_time,
        }


@contextmanager
def track_time(name: str = "operation"):
    """
    Context manager for timing operations
    
    Usage:
        with track_time("preprocessing") as timer:
            # do work
            pass
        duration = timer['duration']
    """
    timer = {"duration": 0.0}
    start = time.time()
    try:
        yield timer
    finally:
        timer["duration"] = time.time() - start
        logger.debug(f"{name} took {timer['duration']:.3f}s")
