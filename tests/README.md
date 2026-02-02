# Qwen3-TTS Server Test Suite

Comprehensive test suite for Qwen3-TTS API Server v1.1.0, with focus on audio preprocessing, voice caching, and performance monitoring.

## Test Organization

```
tests/
├── conftest.py                         # Shared fixtures and configuration
├── utils.py                            # Test utilities and helpers
├── fixtures/
│   ├── audio/                          # Test audio files
│   └── generate_fixtures.py           # Fixture generation script
├── unit/                               # Unit tests (fast, no external dependencies)
│   ├── test_audio_preprocessing.py    # ⭐ PRIMARY: Audio preprocessing tests
│   ├── test_audio_validation.py       # Audio validation tests
│   ├── test_caching.py                # Voice prompt caching tests
│   └── test_metrics.py                # Performance metrics tests
├── integration/                        # Integration tests (API endpoints)
│   ├── test_preprocessing_integration.py
│   ├── test_base_api.py
│   ├── test_custom_voice_api.py
│   └── test_voice_design_api.py
└── e2e/                                # End-to-end tests (complete workflows)
    ├── test_complete_workflows.py
    └── test_performance.py
```

## Prerequisites

### 1. Install Test Dependencies

```bash
conda activate qwen-tts
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

### 2. Generate Test Fixtures

Generate synthetic audio files for testing:

```bash
python -m tests.fixtures.generate_fixtures
```

This creates test audio files in `tests/fixtures/audio/`:
- `short_clean.wav` - 3s clean audio
- `long_speech.wav` - 30s continuous speech
- `silent_edges.wav` - Audio with leading/trailing silence
- `with_pauses.wav` - Audio with natural pauses
- `stereo.wav` - Stereo audio for conversion tests
- `noisy.wav` - Noisy audio
- `silent.wav` - Completely silent audio
- And more...

### 3. Configure Test Environment

The test suite uses `test-api-key` by default. Make sure your `.env` includes:

```bash
API_KEYS=test-api-key
```

Or the tests will use environment variables set in `conftest.py`.

## Running Tests

### All Tests

```bash
conda activate qwen-tts
pytest tests/
```

### By Category

```bash
# Unit tests only (fast)
pytest tests/unit/

# Integration tests (slower)
pytest tests/integration/

# End-to-end tests (slowest)
pytest tests/e2e/

# Audio preprocessing tests specifically
pytest -m preprocessing tests/
```

### By Speed

```bash
# Fast tests only (skip slow tests)
pytest -m "not slow" tests/

# Slow tests only
pytest -m slow tests/
```

### With Coverage

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html tests/

# View report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### Specific Test File

```bash
pytest tests/unit/test_audio_preprocessing.py -v
```

### Specific Test Function

```bash
pytest tests/unit/test_audio_preprocessing.py::TestSilenceDetectionAndRemoval::test_remove_silence_edges -v
```

## Test Categories

### Unit Tests (Fast)

**Purpose**: Test individual components in isolation

**Characteristics**:
- No external dependencies
- Use mocks for TTS models
- Run in seconds
- High coverage of edge cases

**Coverage**:
- Audio preprocessing (silence detection, clipping, quality)
- Audio validation (size, format, duration)
- Voice caching (LRU, TTL, thread-safety)
- Performance metrics (RTF, tracking, logging)

### Integration Tests (Moderate)

**Purpose**: Test API endpoints with mocked models

**Characteristics**:
- Test API contracts
- Use FastAPI TestClient
- Mock TTS models to avoid GPU dependency
- Test authentication and error handling

**Coverage**:
- All API endpoints
- Request/response validation
- Cache statistics endpoints
- Speed control parameter
- Performance headers

### End-to-End Tests (Slow)

**Purpose**: Test complete workflows

**Characteristics**:
- Full request-response cycles
- May load actual models (marked with `@pytest.mark.requires_model`)
- Measure real performance
- Test production scenarios

**Coverage**:
- Complete voice cloning workflow
- Cache performance improvement
- Multi-step workflows
- Error recovery

## Test Markers

Use pytest markers to filter tests:

```bash
# Unit tests only
pytest -m unit tests/

# Skip slow tests
pytest -m "not slow" tests/

# Preprocessing tests specifically
pytest -m preprocessing tests/

# Tests that require actual models
pytest -m requires_model tests/
```

## Expected Test Results

### Fast Test Run (unit tests only)

```bash
$ pytest tests/unit/ -v

tests/unit/test_audio_preprocessing.py::TestSilenceDetectionAndRemoval::test_detect_leading_silence PASSED
tests/unit/test_audio_preprocessing.py::TestSilenceDetectionAndRemoval::test_remove_silence_edges PASSED
tests/unit/test_audio_preprocessing.py::TestSilenceDetectionAndRemoval::test_silence_removal_preserves_content PASSED
tests/unit/test_audio_preprocessing.py::TestSmartLengthClipping::test_clip_at_long_silence PASSED
tests/unit/test_audio_preprocessing.py::TestSmartLengthClipping::test_clip_respects_target_min PASSED
tests/unit/test_audio_preprocessing.py::TestSmartLengthClipping::test_hard_clip_fallback PASSED
tests/unit/test_audio_preprocessing.py::TestDurationConstraints::test_respect_max_duration PASSED
tests/unit/test_audio_preprocessing.py::TestDurationConstraints::test_short_audio_passes_through PASSED
tests/unit/test_audio_preprocessing.py::TestAudioQualityPreservation::test_mono_conversion PASSED
tests/unit/test_audio_preprocessing.py::TestAudioQualityPreservation::test_sample_rate_preservation PASSED
tests/unit/test_audio_preprocessing.py::TestAudioQualityPreservation::test_audio_integrity_clean PASSED
tests/unit/test_audio_preprocessing.py::TestEdgeCases::test_completely_silent_audio PASSED
tests/unit/test_audio_preprocessing.py::TestMetadataAccuracy::test_metadata_has_required_fields PASSED
...

====== 85 passed in 15.32s ======
```

### Full Test Run

```bash
$ pytest tests/ --cov=app --cov-report=term

====== test session starts ======
...
tests/unit/ ..................... [ 45% ]
tests/integration/ .............. [ 75% ]
tests/e2e/ ................      [100% ]

---------- coverage: platform darwin, python 3.10.x -----------
Name                              Stmts   Miss  Cover
-----------------------------------------------------
app/__init__.py                       1      0   100%
app/auth.py                          15      2    87%
app/config.py                        30      0   100%
app/main.py                          25      3    88%
app/routers/base.py                  95      8    92%
app/routers/custom_voice.py          70      5    93%
app/routers/voice_design.py          55      4    93%
app/utils/audio.py                   85      7    92%
app/utils/caching.py                 65      3    95%
app/utils/metrics.py                 45      2    96%
app/utils/streaming.py               20      1    95%
-----------------------------------------------------
TOTAL                               506     35    93%

====== 120 passed, 5 skipped in 45.67s ======
```

## Troubleshooting

### Tests Fail to Import Modules

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**: Run tests from project root:
```bash
cd /Users/linkary/Codes/Labs/qwen-tts-server
conda activate qwen-tts
pytest tests/
```

### pydub Not Available

**Problem**: `ImportError: No module named 'pydub'`

**Solution**: Install audio dependencies:
```bash
pip install pydub librosa
```

Also install system dependencies:
- macOS: `brew install ffmpeg`
- Ubuntu: `sudo apt-get install ffmpeg`

### python-magic Issues

**Problem**: `ImportError: failed to find libmagic`

**Solution**: Install libmagic:
- macOS: `brew install libmagic`
- Ubuntu: `sudo apt-get install libmagic1`

Or skip tests that require python-magic:
```bash
pytest tests/ --ignore=tests/unit/test_audio_validation.py
```

### Slow Tests Take Too Long

**Solution**: Skip slow tests:
```bash
pytest -m "not slow" tests/
```

Or run only unit tests:
```bash
pytest tests/unit/
```

### Server Not Running

**Problem**: Integration/E2E tests fail with connection errors

**Solution**: Start the server first:
```bash
# In one terminal
conda activate qwen-tts
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# In another terminal
conda activate qwen-tts
pytest tests/integration/
```

Or use mocked tests only:
```bash
pytest tests/unit/ tests/integration/ -m "not requires_model"
```

## Writing New Tests

### Test Structure Template

```python
"""
Description of test module
"""
import pytest
from app.utils.something import function_to_test


@pytest.mark.unit  # or integration, e2e
class TestFeatureName:
    """Test specific feature"""
    
    def test_specific_behavior(self, fixture_name):
        """Test description"""
        # Arrange
        input_data = ...
        
        # Act
        result = function_to_test(input_data)
        
        # Assert
        assert result == expected_value
```

### Using Fixtures

Available fixtures from `conftest.py`:
- `test_audio_samples` - Pre-generated audio samples
- `temp_audio_file` - Temporary audio file
- `api_client` - FastAPI test client
- `mock_tts_model` - Mock TTS model
- `base64_test_audio` - Base64 encoded test audio

### Adding Test Markers

```python
@pytest.mark.unit           # Unit test
@pytest.mark.integration    # Integration test
@pytest.mark.e2e            # End-to-end test
@pytest.mark.slow           # Slow test
@pytest.mark.preprocessing  # Preprocessing-related
@pytest.mark.requires_model # Requires actual model loaded
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install torch --index-url https://download.pytorch.org/whl/cpu
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          pytest tests/ --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Performance Benchmarks

Expected test execution times:

| Test Category | Count | Time | Per Test |
|--------------|-------|------|----------|
| Unit tests | 85 | ~15s | ~175ms |
| Integration tests | 25 | ~20s | ~800ms |
| E2E tests | 10 | ~15s | ~1.5s |
| **Total** | **120** | **~50s** | **~417ms** |

## Coverage Goals

- Overall: ≥85%
- Audio preprocessing: ≥95%
- Caching: ≥90%
- API endpoints: ≥85%
- Utilities: ≥90%

## Best Practices

1. **Keep tests fast**: Mock heavy operations (model inference, file I/O)
2. **Test one thing**: Each test should verify one specific behavior
3. **Clear names**: Test names should describe what they test
4. **Arrange-Act-Assert**: Follow AAA pattern
5. **No test interdependence**: Tests should run independently
6. **Use fixtures**: Reuse common setup code
7. **Mark appropriately**: Use markers for filtering
8. **Document expectations**: Add docstrings explaining test purpose

## Continuous Improvement

### Adding Tests for New Features

When adding new features:

1. Write unit tests first (TDD)
2. Add integration tests for API contracts
3. Add E2E tests for workflows
4. Update this documentation
5. Verify coverage doesn't decrease

### Maintaining Test Quality

- Run tests before committing: `pytest tests/unit/`
- Check coverage periodically: `pytest --cov=app tests/`
- Keep tests updated with code changes
- Remove obsolete tests
- Add tests for bug fixes

## Support

For test-related issues:
1. Check this README first
2. Review test output carefully
3. Run with `-vv` for verbose output: `pytest -vv tests/`
4. Use `--pdb` to debug failures: `pytest --pdb tests/`
5. Check GitHub issues

## Quick Reference

```bash
# Most common commands

# Fast development loop (unit tests only)
pytest tests/unit/ -v

# Test specific feature
pytest -m preprocessing tests/

# Test with coverage
pytest --cov=app --cov-report=html tests/

# Test one file
pytest tests/unit/test_audio_preprocessing.py -v

# Test with debugging on failure
pytest --pdb tests/

# Skip slow tests
pytest -m "not slow" tests/

# Show print statements
pytest -s tests/

# Stop on first failure
pytest -x tests/
```

## Test Statistics

Current test suite metrics (as of v1.1.0):

- **Total tests**: 120+
- **Unit tests**: 85 (focus on preprocessing, validation, caching, metrics)
- **Integration tests**: 25 (API endpoints with mocks)
- **E2E tests**: 10 (complete workflows)
- **Coverage**: ~90% of app code
- **Execution time**: ~50s (full suite), ~15s (unit only)
- **Audio preprocessing coverage**: 95%+

## Contributing

When contributing tests:

1. Follow existing patterns in test files
2. Add appropriate markers
3. Include docstrings
4. Keep tests deterministic (no random failures)
5. Update this README if adding new test categories
6. Ensure tests pass before submitting PR

---

**Last Updated**: 2026-01-30 (v1.1.0)
