"""
Tests for performance metrics functionality
"""
import pytest
import time
from app.utils.metrics import PerformanceTracker, track_time


@pytest.mark.unit
class TestRTFCalculation:
    """Test Real-Time Factor calculation"""
    
    def test_rtf_calculation_basic(self):
        """Test basic RTF calculation"""
        tracker = PerformanceTracker()
        tracker.start()
        
        # Simulate 1s generation time for 2s audio
        time.sleep(0.1)  # Small delay to simulate processing
        tracker.mark_generation()
        tracker.set_audio_duration(2.0)
        
        rtf = tracker.get_rtf()
        
        assert rtf is not None
        assert rtf > 0, "RTF should be positive"
        # RTF should be less than 1.0 for this test (fast generation)
        assert rtf < 1.0, f"RTF should be <1.0 for fast generation, got {rtf}"
    
    def test_rtf_with_zero_duration(self):
        """Test RTF calculation with zero audio duration"""
        tracker = PerformanceTracker()
        tracker.start()
        tracker.mark_generation()
        tracker.set_audio_duration(0.0)
        
        rtf = tracker.get_rtf()
        
        # Should handle gracefully
        assert rtf is None or rtf == 0
    
    def test_rtf_without_generation_time(self):
        """Test RTF calculation without generation time"""
        tracker = PerformanceTracker()
        tracker.set_audio_duration(2.0)
        
        rtf = tracker.get_rtf()
        
        assert rtf is None, "RTF should be None without generation time"


@pytest.mark.unit
class TestPerformanceHeaders:
    """Test header generation"""
    
    def test_headers_with_full_metrics(self):
        """Test header generation with all metrics"""
        tracker = PerformanceTracker()
        tracker.start()
        time.sleep(0.05)
        tracker.mark_generation()
        tracker.set_audio_duration(1.0)
        tracker.set_cache_status("hit")
        tracker.mark_preprocessing(0.1)
        
        headers = tracker.get_headers()
        
        # Check all expected headers
        assert "X-Generation-Time" in headers
        assert "X-Audio-Duration" in headers
        assert "X-RTF" in headers
        assert "X-Cache-Status" in headers
        assert "X-Preprocessing-Time" in headers
        
        # Check header values are strings
        assert isinstance(headers["X-Generation-Time"], str)
        assert isinstance(headers["X-RTF"], str)
        assert headers["X-Cache-Status"] == "hit"
    
    def test_headers_with_partial_metrics(self):
        """Test header generation with partial metrics"""
        tracker = PerformanceTracker()
        tracker.start()
        tracker.mark_generation()
        tracker.set_cache_status("miss")
        
        headers = tracker.get_headers()
        
        # Should have generation time and cache status
        assert "X-Generation-Time" in headers
        assert "X-Cache-Status" in headers
        assert headers["X-Cache-Status"] == "miss"
    
    def test_headers_cache_status_default(self):
        """Test default cache status in headers"""
        tracker = PerformanceTracker()
        
        headers = tracker.get_headers()
        
        # Default cache status should be "miss"
        assert headers["X-Cache-Status"] == "miss"


@pytest.mark.unit
class TestMetricsLogging:
    """Test performance logging"""
    
    def test_log_metrics_with_rtf(self, caplog):
        """Test logging with RTF"""
        tracker = PerformanceTracker()
        tracker.start()
        time.sleep(0.05)
        tracker.mark_generation()
        tracker.set_audio_duration(1.0)
        tracker.set_cache_status("hit")
        
        with caplog.at_level("INFO"):
            tracker.log_metrics()
        
        # Check log message
        assert len(caplog.records) > 0
        log_message = caplog.records[0].message
        
        # Should contain key information
        assert "Generation completed" in log_message
        assert "RTF:" in log_message
        assert "[cache: hit]" in log_message
    
    def test_log_metrics_without_rtf(self, caplog):
        """Test logging without RTF"""
        tracker = PerformanceTracker()
        tracker.start()
        time.sleep(0.05)
        tracker.mark_generation()
        tracker.set_cache_status("miss")
        
        with caplog.at_level("INFO"):
            tracker.log_metrics()
        
        assert len(caplog.records) > 0
        log_message = caplog.records[0].message
        
        # Should still log generation time
        assert "Generation completed" in log_message
        assert "[cache: miss]" in log_message
    
    def test_log_metrics_with_preprocessing(self, caplog):
        """Test logging with preprocessing time"""
        tracker = PerformanceTracker()
        tracker.start()
        time.sleep(0.05)
        tracker.mark_generation()
        tracker.mark_preprocessing(0.15)
        
        with caplog.at_level("INFO"):
            tracker.log_metrics()
        
        log_message = caplog.records[0].message
        
        # Should include preprocessing time
        assert "[preprocessing:" in log_message


@pytest.mark.unit
class TestPerformanceTracker:
    """Test PerformanceTracker state management"""
    
    def test_tracker_initialization(self):
        """Test tracker is initialized correctly"""
        tracker = PerformanceTracker()
        
        assert tracker.start_time is None
        assert tracker.generation_time is None
        assert tracker.preprocessing_time is None
        assert tracker.cache_status == "miss"
        assert tracker.audio_duration is None
    
    def test_start_sets_time(self):
        """Test start() sets start time"""
        tracker = PerformanceTracker()
        
        before = time.time()
        tracker.start()
        after = time.time()
        
        assert tracker.start_time is not None
        assert before <= tracker.start_time <= after
    
    def test_mark_generation_calculates_time(self):
        """Test mark_generation() calculates elapsed time"""
        tracker = PerformanceTracker()
        tracker.start()
        
        time.sleep(0.05)
        tracker.mark_generation()
        
        assert tracker.generation_time is not None
        assert tracker.generation_time >= 0.05, f"Generation time should be ≥0.05s, got {tracker.generation_time}s"
    
    def test_set_audio_duration(self):
        """Test setting audio duration"""
        tracker = PerformanceTracker()
        tracker.set_audio_duration(3.5)
        
        assert tracker.audio_duration == 3.5
    
    def test_set_cache_status(self):
        """Test setting cache status"""
        tracker = PerformanceTracker()
        tracker.set_cache_status("hit")
        
        assert tracker.cache_status == "hit"
    
    def test_mark_preprocessing(self):
        """Test marking preprocessing time"""
        tracker = PerformanceTracker()
        tracker.mark_preprocessing(0.25)
        
        assert tracker.preprocessing_time == 0.25


@pytest.mark.unit
class TestGetMetrics:
    """Test get_metrics() method"""
    
    def test_get_metrics_complete(self):
        """Test get_metrics with all data"""
        tracker = PerformanceTracker()
        tracker.start()
        time.sleep(0.05)
        tracker.mark_generation()
        tracker.set_audio_duration(1.0)
        tracker.set_cache_status("hit")
        tracker.mark_preprocessing(0.1)
        
        metrics = tracker.get_metrics()
        
        assert "generation_time" in metrics
        assert "audio_duration" in metrics
        assert "rtf" in metrics
        assert "cache_status" in metrics
        assert "preprocessing_time" in metrics
        
        assert metrics["generation_time"] is not None
        assert metrics["audio_duration"] == 1.0
        assert metrics["rtf"] is not None
        assert metrics["cache_status"] == "hit"
        assert metrics["preprocessing_time"] == 0.1
    
    def test_get_metrics_partial(self):
        """Test get_metrics with partial data"""
        tracker = PerformanceTracker()
        tracker.start()
        tracker.mark_generation()
        
        metrics = tracker.get_metrics()
        
        assert metrics["generation_time"] is not None
        assert metrics["audio_duration"] is None
        assert metrics["rtf"] is None


@pytest.mark.unit
class TestTrackTime:
    """Test track_time context manager"""
    
    def test_track_time_basic(self):
        """Test basic time tracking"""
        with track_time("test") as timer:
            time.sleep(0.05)
        
        assert "duration" in timer
        assert timer["duration"] >= 0.05, f"Duration should be ≥0.05s, got {timer['duration']}s"
    
    def test_track_time_with_exception(self):
        """Test time tracking with exception"""
        try:
            with track_time("test") as timer:
                time.sleep(0.05)
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Timer should still have duration even with exception
        assert "duration" in timer
        assert timer["duration"] >= 0.05
    
    def test_track_time_zero_duration(self):
        """Test time tracking with zero duration"""
        with track_time("test") as timer:
            pass
        
        assert "duration" in timer
        assert timer["duration"] >= 0, "Duration should be non-negative"
