"""
Tests for audio validation functionality
"""
import pytest
import numpy as np
import io
import soundfile as sf
from app.utils.audio import validate_audio_file, AudioValidationError
from tests.utils import generate_test_audio, save_test_audio


@pytest.mark.unit
class TestFileSizeValidation:
    """Test file size limit validation"""
    
    def test_validate_file_size_under_limit(self, test_audio_samples):
        """Test file under size limit passes validation"""
        audio, sample_rate = test_audio_samples["short_clean"]
        
        # Create audio file bytes
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        file_content = buffer.read()
        
        # Should pass with default 5MB limit
        audio_data, sr, metadata = validate_audio_file(
            file_content, "test.wav", max_size_mb=5.0
        )
        
        assert len(audio_data) > 0
        assert sr == sample_rate
        assert "size_mb" in metadata
        assert metadata["size_mb"] < 5.0
    
    def test_validate_file_size_exceeds_limit(self, test_audio_samples):
        """Test file exceeding size limit fails validation"""
        audio, sample_rate = test_audio_samples["long"]
        
        # Create audio file bytes
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        file_content = buffer.read()
        
        # Set very small limit
        with pytest.raises(AudioValidationError) as exc_info:
            validate_audio_file(
                file_content, "test.wav", max_size_mb=0.1
            )
        
        assert "exceeds maximum allowed size" in str(exc_info.value)


@pytest.mark.unit
class TestFormatValidation:
    """Test file format validation"""
    
    @pytest.mark.parametrize("extension", ["wav", "mp3", "flac", "ogg"])
    def test_allowed_formats(self, test_audio_samples, extension):
        """Test allowed file formats pass validation"""
        audio, sample_rate = test_audio_samples["short_clean"]
        
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        file_content = buffer.read()
        
        # Should pass for allowed formats
        audio_data, sr, metadata = validate_audio_file(
            file_content, f"test.{extension}", allowed_formats={extension, 'wav'}
        )
        
        assert len(audio_data) > 0
    
    def test_disallowed_format(self, test_audio_samples):
        """Test disallowed file format fails validation"""
        audio, sample_rate = test_audio_samples["short_clean"]
        
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        file_content = buffer.read()
        
        # Use fake extension
        with pytest.raises(AudioValidationError) as exc_info:
            validate_audio_file(
                file_content, "test.xyz", allowed_formats={'wav', 'mp3'}
            )
        
        assert "not allowed" in str(exc_info.value)


@pytest.mark.unit
class TestDurationValidation:
    """Test audio duration validation"""
    
    def test_duration_within_limit(self, test_audio_samples):
        """Test audio within duration limit passes"""
        audio, sample_rate = test_audio_samples["short_clean"]
        
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        file_content = buffer.read()
        
        # 3s audio with 60s limit should pass
        audio_data, sr, metadata = validate_audio_file(
            file_content, "test.wav", max_duration=60.0
        )
        
        assert len(audio_data) > 0
        assert "duration" in metadata
        assert metadata["duration"] < 60.0
    
    def test_duration_exceeds_limit(self, test_audio_samples):
        """Test audio exceeding duration limit fails"""
        audio, sample_rate = test_audio_samples["long"]
        
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        file_content = buffer.read()
        
        # 30s audio with 10s limit should fail
        with pytest.raises(AudioValidationError) as exc_info:
            validate_audio_file(
                file_content, "test.wav", max_duration=10.0
            )
        
        assert "exceeds maximum allowed duration" in str(exc_info.value)


@pytest.mark.unit
class TestAudioContentValidation:
    """Test audio content can be read"""
    
    def test_valid_audio_content(self, test_audio_samples):
        """Test valid audio file can be read"""
        audio, sample_rate = test_audio_samples["short_clean"]
        
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        file_content = buffer.read()
        
        audio_data, sr, metadata = validate_audio_file(
            file_content, "test.wav"
        )
        
        assert len(audio_data) > 0
        assert sr > 0
        assert "channels" in metadata
    
    def test_invalid_audio_content(self):
        """Test invalid audio content fails validation"""
        # Random bytes that are not audio
        file_content = b"This is not an audio file"
        
        with pytest.raises(AudioValidationError) as exc_info:
            validate_audio_file(file_content, "test.wav")
        
        assert "Failed to read audio file" in str(exc_info.value)


@pytest.mark.unit
class TestMetadataGeneration:
    """Test validation generates correct metadata"""
    
    def test_metadata_completeness(self, test_audio_samples):
        """Test metadata contains all expected fields"""
        audio, sample_rate = test_audio_samples["short_clean"]
        
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        file_content = buffer.read()
        
        _, _, metadata = validate_audio_file(file_content, "test.wav")
        
        # Check all expected fields
        assert "size_mb" in metadata
        assert "duration" in metadata
        assert "sample_rate" in metadata
        assert "channels" in metadata
        assert "format" in metadata
        
        # Check values are reasonable
        assert metadata["size_mb"] > 0
        assert metadata["duration"] > 0
        assert metadata["sample_rate"] == sample_rate
        assert metadata["format"] == "wav"
    
    def test_stereo_audio_metadata(self, test_audio_samples):
        """Test stereo audio metadata"""
        audio, sample_rate = test_audio_samples["stereo"]
        
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        file_content = buffer.read()
        
        _, _, metadata = validate_audio_file(file_content, "test.wav")
        
        # Stereo should have 2 channels
        assert metadata["channels"] == 2


@pytest.mark.unit
class TestErrorMessages:
    """Test validation error messages are descriptive"""
    
    def test_size_error_message(self, test_audio_samples):
        """Test file size error message is clear"""
        audio, sample_rate = test_audio_samples["short_clean"]
        
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        file_content = buffer.read()
        
        try:
            validate_audio_file(file_content, "test.wav", max_size_mb=0.001)
            assert False, "Should have raised error"
        except AudioValidationError as e:
            error_msg = str(e)
            # Should mention size and limit
            assert "size" in error_msg.lower()
            assert "exceeds" in error_msg.lower()
    
    def test_duration_error_message(self, test_audio_samples):
        """Test duration error message is clear"""
        audio, sample_rate = test_audio_samples["medium"]
        
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        file_content = buffer.read()
        
        try:
            validate_audio_file(file_content, "test.wav", max_duration=1.0)
            assert False, "Should have raised error"
        except AudioValidationError as e:
            error_msg = str(e)
            # Should mention duration and limit
            assert "duration" in error_msg.lower()
            assert "exceeds" in error_msg.lower()
    
    def test_format_error_message(self):
        """Test format error message is clear"""
        try:
            validate_audio_file(b"fake data", "test.xyz", allowed_formats={'wav'})
            assert False, "Should have raised error"
        except AudioValidationError as e:
            error_msg = str(e)
            # Should mention format and allowed formats
            assert "not allowed" in error_msg.lower()
