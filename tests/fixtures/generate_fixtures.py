"""
Generate test audio fixtures

Run this script to generate test audio files:
    python -m tests.fixtures.generate_fixtures
"""
import os
import sys
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.utils import (
    generate_test_audio,
    add_silence,
    create_stereo_audio,
    save_test_audio
)

FIXTURES_DIR = os.path.dirname(__file__)
AUDIO_DIR = os.path.join(FIXTURES_DIR, 'audio')


def generate_all_fixtures():
    """Generate all test audio fixtures"""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    
    print("Generating test audio fixtures...")
    
    # 1. Short clean audio (3s)
    print("  - short_clean.wav")
    audio = generate_test_audio(duration=3.0, frequency=440.0)
    save_test_audio(audio, 24000, os.path.join(AUDIO_DIR, 'short_clean.wav'))
    
    # 2. Long speech (30s continuous)
    print("  - long_speech.wav")
    # Mix multiple frequencies to simulate speech
    audio = np.zeros(30 * 24000, dtype=np.float32)
    for freq in [200, 400, 600, 800]:
        audio += generate_test_audio(duration=30.0, frequency=freq) * 0.25
    save_test_audio(audio, 24000, os.path.join(AUDIO_DIR, 'long_speech.wav'))
    
    # 3. Audio with silent edges (5s content + 2s leading + 1s trailing silence)
    print("  - silent_edges.wav")
    audio = generate_test_audio(duration=5.0, frequency=440.0)
    audio = add_silence(audio, 24000, 2.0, position='start')
    audio = add_silence(audio, 24000, 1.0, position='end')
    save_test_audio(audio, 24000, os.path.join(AUDIO_DIR, 'silent_edges.wav'))
    
    # 4. Audio with natural pauses (15s with pauses at 5s and 10s)
    print("  - with_pauses.wav")
    audio1 = generate_test_audio(duration=5.0, frequency=440.0)
    silence = np.zeros(int(1.0 * 24000), dtype=np.float32)
    audio2 = generate_test_audio(duration=5.0, frequency=550.0)
    audio3 = generate_test_audio(duration=4.0, frequency=660.0)
    audio = np.concatenate([audio1, silence, audio2, silence, audio3])
    save_test_audio(audio, 24000, os.path.join(AUDIO_DIR, 'with_pauses.wav'))
    
    # 5. Stereo audio
    print("  - stereo.wav")
    audio = generate_test_audio(duration=3.0, frequency=440.0)
    audio_stereo = create_stereo_audio(audio, channel_diff=0.1)
    save_test_audio(audio_stereo, 24000, os.path.join(AUDIO_DIR, 'stereo.wav'))
    
    # 6. Noisy audio
    print("  - noisy.wav")
    audio = generate_test_audio(duration=3.0, frequency=440.0, add_noise=True, noise_level=0.05)
    save_test_audio(audio, 24000, os.path.join(AUDIO_DIR, 'noisy.wav'))
    
    # 7. Completely silent audio
    print("  - silent.wav")
    audio = np.zeros(3 * 24000, dtype=np.float32)
    save_test_audio(audio, 24000, os.path.join(AUDIO_DIR, 'silent.wav'))
    
    # 8. Very short audio (0.5s)
    print("  - very_short.wav")
    audio = generate_test_audio(duration=0.5, frequency=440.0)
    save_test_audio(audio, 24000, os.path.join(AUDIO_DIR, 'very_short.wav'))
    
    # 9. Continuous speech without clear pauses (20s)
    print("  - continuous_speech.wav")
    audio = np.zeros(20 * 24000, dtype=np.float32)
    # Randomly varying frequencies to simulate continuous speech
    np.random.seed(42)
    for i in range(100):
        freq = 200 + np.random.random() * 600
        start = int(i * 0.2 * 24000)
        end = int((i * 0.2 + 0.2) * 24000)
        if end > len(audio):
            break
        segment = generate_test_audio(duration=0.2, frequency=freq)
        audio[start:end] = segment
    save_test_audio(audio, 24000, os.path.join(AUDIO_DIR, 'continuous_speech.wav'))
    
    # 10. Medium audio (10s) - within target range
    print("  - medium_clean.wav")
    audio = generate_test_audio(duration=10.0, frequency=440.0)
    save_test_audio(audio, 24000, os.path.join(AUDIO_DIR, 'medium_clean.wav'))
    
    print("\nFixtures generated successfully in:", AUDIO_DIR)
    print("Total files:", len(os.listdir(AUDIO_DIR)))


if __name__ == "__main__":
    generate_all_fixtures()
