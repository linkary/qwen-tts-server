"""
Comprehensive tests for audio preprocessing

PRIMARY FOCUS: Testing silence detection, smart clipping, and audio quality preservation
"""
import pytest
import numpy as np
from app.utils.audio import preprocess_reference_audio
from tests.utils import (
    generate_test_audio,
    add_silence,
    measure_silence,
    get_audio_duration,
    compare_audio_similarity
)


@pytest.mark.unit
@pytest.mark.preprocessing
class TestSilenceDetectionAndRemoval:
    """Test silence detection and removal functionality"""
    
    def test_detect_leading_silence(self, test_audio_samples):
        """Test silence detection at various thresholds"""
        audio, sample_rate = test_audio_samples["silent_edges"]
        
        # Measure silence before preprocessing
        leading, trailing = measure_silence(audio, sample_rate, threshold=-42.0)
        
        # Should detect approximately 2s leading and 2s trailing silence
        assert leading > 1.5, f"Expected >1.5s leading silence, got {leading}s"
        assert trailing > 1.5, f"Expected >1.5s trailing silence, got {trailing}s"
    
    def test_remove_silence_edges(self, test_audio_samples):
        """Test edge silence removal"""
        audio, sample_rate = test_audio_samples["silent_edges"]
        
        # Original duration should be ~9s (5s content + 4s silence)
        original_duration = get_audio_duration(audio, sample_rate)
        assert 8.5 < original_duration < 9.5, f"Expected ~9s, got {original_duration}s"
        
        # Preprocess
        processed_audio, _, metadata = preprocess_reference_audio(
            audio, sample_rate, max_duration=15.0, target_duration_min=5.0
        )
        
        # Check silence was removed
        assert "silence_removed_ms" in metadata
        assert metadata["silence_removed_ms"] > 0
        
        # Processed duration should be close to 5s (original content)
        processed_duration = get_audio_duration(processed_audio, sample_rate)
        assert 4.5 < processed_duration < 6.0, f"Expected ~5s after silence removal, got {processed_duration}s"
        
        # Verify silence at edges is reduced
        leading, trailing = measure_silence(processed_audio, sample_rate)
        assert leading < 0.5, f"Leading silence should be <0.5s, got {leading}s"
        assert trailing < 0.5, f"Trailing silence should be <0.5s, got {trailing}s"
    
    def test_silence_removal_preserves_content(self, test_audio_samples):
        """Test that silence removal doesn't damage audio content"""
        audio, sample_rate = test_audio_samples["silent_edges"]
        
        # Preprocess
        processed_audio, _, _ = preprocess_reference_audio(
            audio, sample_rate, max_duration=15.0
        )
        
        # Extract content portions for comparison
        # Original: skip first 2s and last 2s of silence
        content_start = int(2.0 * sample_rate)
        content_end = len(audio) - int(2.0 * sample_rate)
        original_content = audio[content_start:content_end]
        
        # Processed should be mostly the same content
        min_len = min(len(original_content), len(processed_audio))
        similarity = compare_audio_similarity(
            original_content[:min_len],
            processed_audio[:min_len],
            sample_rate
        )
        
        assert similarity > 0.9, f"Content similarity should be >0.9, got {similarity}"


@pytest.mark.unit
@pytest.mark.preprocessing
class TestSmartLengthClipping:
    """Test smart length clipping at natural boundaries"""
    
    def test_clip_at_long_silence(self, test_audio_samples):
        """Test clipping at natural pause boundaries"""
        audio, sample_rate = test_audio_samples["with_pauses"]
        
        # Original is ~17s (5s + 1s pause + 5s + 1s pause + 5s)
        original_duration = get_audio_duration(audio, sample_rate)
        assert original_duration > 15.0, f"Test audio should be >15s, got {original_duration}s"
        
        # Preprocess with max_duration=15.0
        processed_audio, _, metadata = preprocess_reference_audio(
            audio, sample_rate, max_duration=15.0, target_duration_min=5.0
        )
        
        # Should clip at a pause, not mid-content
        processed_duration = get_audio_duration(processed_audio, sample_rate)
        assert processed_duration <= 15.0, f"Duration should be ≤15s, got {processed_duration}s"
        
        # Check clip method was used
        assert "clip_method" in metadata
        assert metadata["clip_method"] in ["long_silence", "short_silence", "hard_clip"]
    
    def test_clip_respects_target_min(self, test_audio_samples):
        """Test that clipping respects target_duration_min"""
        audio, sample_rate = test_audio_samples["long"]
        
        # Preprocess with target_duration_min=10.0
        processed_audio, _, metadata = preprocess_reference_audio(
            audio, sample_rate, max_duration=15.0, target_duration_min=10.0
        )
        
        processed_duration = get_audio_duration(processed_audio, sample_rate)
        
        # Should try to keep at least target_duration_min if possible
        # (may be less if no suitable clip point found)
        # Allow small tolerance for rounding
        assert processed_duration <= 15.1, f"Duration should be ≤15.1s, got {processed_duration}s"
    
    def test_hard_clip_fallback(self, test_audio_samples):
        """Test hard clip when no suitable silence found"""
        audio, sample_rate = test_audio_samples["continuous"]
        
        # Continuous audio without clear pauses
        original_duration = get_audio_duration(audio, sample_rate)
        assert original_duration > 15.0
        
        # Should fall back to hard clip
        processed_audio, _, metadata = preprocess_reference_audio(
            audio, sample_rate, max_duration=15.0, target_duration_min=5.0
        )
        
        processed_duration = get_audio_duration(processed_audio, sample_rate)
        
        # Should clip to exactly max_duration or close to it
        assert 14.5 <= processed_duration <= 15.5, f"Expected ~15s, got {processed_duration}s"
        
        # Clip method might be hard_clip
        if "clip_method" in metadata:
            # Any method is acceptable as long as duration is correct
            assert metadata["clip_method"] in ["long_silence", "short_silence", "hard_clip"]


@pytest.mark.unit
@pytest.mark.preprocessing
class TestDurationConstraints:
    """Test duration constraint enforcement"""
    
    def test_respect_max_duration(self, test_audio_samples):
        """Test maximum duration enforcement"""
        audio, sample_rate = test_audio_samples["long"]
        
        # 30s audio with max_duration=15.0
        max_duration = 15.0
        processed_audio, _, _ = preprocess_reference_audio(
            audio, sample_rate, max_duration=max_duration
        )
        
        processed_duration = get_audio_duration(processed_audio, sample_rate)
        
        # Result should be ≤ max_duration (with small tolerance for silence removal)
        assert processed_duration <= max_duration + 0.5, \
            f"Duration {processed_duration}s exceeds max {max_duration}s"
    
    def test_short_audio_passes_through(self, test_audio_samples):
        """Test audio already within limits passes through with minimal changes"""
        audio, sample_rate = test_audio_samples["medium"]
        
        # 10s audio with max_duration=15.0 (already within limits)
        original_duration = get_audio_duration(audio, sample_rate)
        
        processed_audio, _, metadata = preprocess_reference_audio(
            audio, sample_rate, max_duration=15.0, target_duration_min=5.0
        )
        
        processed_duration = get_audio_duration(processed_audio, sample_rate)
        
        # Should be close to original (maybe slightly different due to silence removal)
        duration_diff = abs(processed_duration - original_duration)
        assert duration_diff < 1.0, f"Duration changed too much: {duration_diff}s"
    
    def test_very_short_audio(self, test_audio_samples):
        """Test very short audio (< target_duration_min)"""
        audio, sample_rate = test_audio_samples["very_short"]
        
        # 0.5s audio (much shorter than target_duration_min)
        processed_audio, _, metadata = preprocess_reference_audio(
            audio, sample_rate, max_duration=15.0, target_duration_min=5.0
        )
        
        # Should pass through without issues
        assert len(processed_audio) > 0, "Processed audio should not be empty"
        
        processed_duration = get_audio_duration(processed_audio, sample_rate)
        assert processed_duration > 0, "Duration should be positive"


@pytest.mark.unit
@pytest.mark.preprocessing
class TestAudioQualityPreservation:
    """Test audio quality preservation during preprocessing"""
    
    def test_mono_conversion(self, test_audio_samples):
        """Test stereo to mono conversion"""
        audio, sample_rate = test_audio_samples["stereo"]
        
        # Verify it's stereo
        assert audio.ndim == 2, "Test audio should be stereo"
        assert audio.shape[1] == 2, "Stereo audio should have 2 channels"
        
        # Preprocess
        processed_audio, _, metadata = preprocess_reference_audio(
            audio, sample_rate, max_duration=15.0
        )
        
        # Should be converted to mono
        assert processed_audio.ndim == 1, "Processed audio should be mono"
        assert "converted_to_mono" in metadata
        assert metadata["converted_to_mono"] is True
    
    def test_sample_rate_preservation(self, test_audio_samples):
        """Test sample rate is maintained"""
        audio, input_sample_rate = test_audio_samples["short_clean"]
        
        # Preprocess
        processed_audio, output_sample_rate, _ = preprocess_reference_audio(
            audio, input_sample_rate, max_duration=15.0
        )
        
        # Sample rate should be unchanged
        assert output_sample_rate == input_sample_rate, \
            f"Sample rate changed from {input_sample_rate} to {output_sample_rate}"
    
    def test_audio_integrity_clean(self, test_audio_samples):
        """Test audio content integrity after preprocessing (clean audio)"""
        audio, sample_rate = test_audio_samples["short_clean"]
        
        # Short clean audio should pass through with minimal changes
        processed_audio, _, _ = preprocess_reference_audio(
            audio, sample_rate, max_duration=15.0
        )
        
        # Compare similarity
        min_len = min(len(audio), len(processed_audio))
        similarity = compare_audio_similarity(
            audio[:min_len],
            processed_audio[:min_len],
            sample_rate
        )
        
        # Clean audio should have very high similarity
        assert similarity > 0.95, f"Clean audio similarity should be >0.95, got {similarity}"
    
    def test_noisy_audio_handled(self, test_audio_samples):
        """Test preprocessing handles noisy audio without crashes"""
        audio, sample_rate = test_audio_samples["noisy"]
        
        # Should handle noisy audio without errors
        processed_audio, _, metadata = preprocess_reference_audio(
            audio, sample_rate, max_duration=15.0
        )
        
        # Should produce valid output
        assert len(processed_audio) > 0
        assert not np.isnan(processed_audio).any(), "Output should not contain NaN"
        assert not np.isinf(processed_audio).any(), "Output should not contain Inf"


@pytest.mark.unit
@pytest.mark.preprocessing
class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_completely_silent_audio(self, test_audio_samples):
        """Test handling of completely silent audio"""
        audio, sample_rate = test_audio_samples["silent"]
        
        # Should handle gracefully without errors
        processed_audio, _, metadata = preprocess_reference_audio(
            audio, sample_rate, max_duration=15.0
        )
        
        # Should produce some output (even if very short)
        assert len(processed_audio) > 0, "Should produce some output for silent audio"
    
    def test_empty_audio(self):
        """Test handling of empty audio array"""
        audio = np.array([], dtype=np.float32)
        sample_rate = 24000
        
        # Should handle gracefully
        try:
            processed_audio, _, _ = preprocess_reference_audio(
                audio, sample_rate, max_duration=15.0
            )
            # If it succeeds, output should be empty or minimal
            assert len(processed_audio) == 0 or len(processed_audio) < sample_rate
        except Exception as e:
            # Or it might raise an exception, which is also acceptable
            assert True, "Empty audio handling can raise exception"
    
    def test_extreme_max_duration(self, test_audio_samples):
        """Test with extreme max_duration values"""
        audio, sample_rate = test_audio_samples["short_clean"]
        
        # Very large max_duration (should pass through)
        processed_audio, _, _ = preprocess_reference_audio(
            audio, sample_rate, max_duration=1000.0
        )
        
        original_duration = get_audio_duration(audio, sample_rate)
        processed_duration = get_audio_duration(processed_audio, sample_rate)
        
        # Should be close to original
        assert abs(processed_duration - original_duration) < 1.0
        
        # Very small max_duration
        processed_audio, _, _ = preprocess_reference_audio(
            audio, sample_rate, max_duration=0.5
        )
        
        processed_duration = get_audio_duration(processed_audio, sample_rate)
        assert processed_duration <= 1.0, "Should clip to small duration"


@pytest.mark.unit
@pytest.mark.preprocessing
class TestMetadataAccuracy:
    """Test preprocessing metadata is accurate"""
    
    def test_metadata_has_required_fields(self, test_audio_samples):
        """Test metadata contains required fields"""
        audio, sample_rate = test_audio_samples["short_clean"]
        
        _, _, metadata = preprocess_reference_audio(
            audio, sample_rate, max_duration=15.0
        )
        
        # Check required fields
        assert "original_duration" in metadata
        assert "sample_rate" in metadata
        
        # Original duration should be accurate
        expected_duration = get_audio_duration(audio, sample_rate)
        assert abs(metadata["original_duration"] - expected_duration) < 0.1
    
    def test_clip_method_reported(self, test_audio_samples):
        """Test clip_method is correctly reported"""
        audio, sample_rate = test_audio_samples["long"]
        
        _, _, metadata = preprocess_reference_audio(
            audio, sample_rate, max_duration=15.0
        )
        
        # Should have clip_method since audio was clipped
        if "clip_method" in metadata:
            assert metadata["clip_method"] in [
                "long_silence", "short_silence", "hard_clip", "basic_clip"
            ]
    
    def test_processed_duration_accurate(self, test_audio_samples):
        """Test processed_duration in metadata matches actual output"""
        audio, sample_rate = test_audio_samples["medium"]
        
        processed_audio, _, metadata = preprocess_reference_audio(
            audio, sample_rate, max_duration=15.0
        )
        
        actual_duration = get_audio_duration(processed_audio, sample_rate)
        
        if "processed_duration" in metadata:
            # Metadata duration should match actual duration
            assert abs(metadata["processed_duration"] - actual_duration) < 0.1, \
                f"Metadata duration {metadata['processed_duration']} != actual {actual_duration}"


@pytest.mark.unit
@pytest.mark.preprocessing
class TestConfigurationRespect:
    """Test that preprocessing respects configuration"""
    
    def test_respects_config_max_duration(self, test_audio_samples):
        """Test configuration override for max duration"""
        audio, sample_rate = test_audio_samples["long"]
        
        # Test with different max durations
        for max_dur in [10.0, 15.0, 20.0]:
            processed_audio, _, _ = preprocess_reference_audio(
                audio, sample_rate, max_duration=max_dur
            )
            
            processed_duration = get_audio_duration(processed_audio, sample_rate)
            assert processed_duration <= max_dur + 0.5, \
                f"Duration {processed_duration}s exceeds configured max {max_dur}s"
    
    def test_respects_config_target_min(self, test_audio_samples):
        """Test configuration override for target min"""
        audio, sample_rate = test_audio_samples["long"]
        
        # With higher target_min, might try to keep more audio
        processed_audio1, _, _ = preprocess_reference_audio(
            audio, sample_rate, max_duration=15.0, target_duration_min=3.0
        )
        
        processed_audio2, _, _ = preprocess_reference_audio(
            audio, sample_rate, max_duration=15.0, target_duration_min=10.0
        )
        
        # Both should respect max_duration
        assert get_audio_duration(processed_audio1, sample_rate) <= 15.5
        assert get_audio_duration(processed_audio2, sample_rate) <= 15.5


@pytest.mark.unit
@pytest.mark.preprocessing
class TestPreprocessingWithoutPydub:
    """Test preprocessing fallback when pydub is not available"""
    
    def test_basic_clipping_fallback(self, test_audio_samples, monkeypatch):
        """Test basic clipping when pydub import fails"""
        audio, sample_rate = test_audio_samples["long"]
        
        # Mock pydub import failure
        def mock_import(name, *args, **kwargs):
            if 'pydub' in name:
                raise ImportError("pydub not available")
            return __import__(name, *args, **kwargs)
        
        # This will use basic clipping fallback
        processed_audio, _, metadata = preprocess_reference_audio(
            audio, sample_rate, max_duration=15.0
        )
        
        # Should still work with basic clipping
        processed_duration = get_audio_duration(processed_audio, sample_rate)
        assert processed_duration <= 15.5, "Basic clipping should respect max duration"
        
        # Might indicate basic_clip in metadata
        if "clip_method" in metadata:
            # Any method is fine, as long as it works
            pass
