#!/usr/bin/env python3
"""
Example script showing all three TTS model types
"""
import requests
import base64
import sys

API_KEY = "your-api-key-1"
BASE_URL = "http://localhost:8000"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def example_custom_voice():
    """Example: CustomVoice with preset speakers"""
    print("\n" + "="*60)
    print("Example 1: CustomVoice (Preset Speakers)")
    print("="*60)
    
    # Get list of available speakers
    response = requests.get(f"{BASE_URL}/api/v1/custom-voice/speakers", headers=headers)
    speakers = response.json()["speakers"]
    print(f"\nAvailable speakers: {len(speakers)}")
    for speaker in speakers[:3]:  # Show first 3
        print(f"  - {speaker['name']}: {speaker['description']}")
    
    # Generate with custom voice
    print("\nGenerating speech with Ryan (English male voice)...")
    response = requests.post(
        f"{BASE_URL}/api/v1/custom-voice/generate",
        headers=headers,
        json={
            "text": "Welcome to Qwen3-TTS! I'm Ryan, and I'm excited to help you with text-to-speech.",
            "language": "English",
            "speaker": "Ryan",
            "instruct": "Speak enthusiastically and clearly",
            "response_format": "wav"
        }
    )
    
    if response.status_code == 200:
        with open("example_custom_voice.wav", "wb") as f:
            f.write(response.content)
        print("✓ Saved to: example_custom_voice.wav")
    else:
        print(f"✗ Error: {response.status_code}")


def example_voice_design():
    """Example: VoiceDesign with natural language description"""
    print("\n" + "="*60)
    print("Example 2: VoiceDesign (Custom Voice Description)")
    print("="*60)
    
    print("\nDesigning a custom voice with natural language...")
    print("Description: Young professional female, confident and articulate")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/voice-design/generate",
        headers=headers,
        json={
            "text": "Voice design allows you to create any voice you can imagine using natural language descriptions.",
            "language": "English",
            "instruct": "Young professional female voice, 25-30 years old, confident and articulate with a slight smile in her voice, speaking at a moderate pace",
            "response_format": "wav"
        }
    )
    
    if response.status_code == 200:
        with open("example_voice_design.wav", "wb") as f:
            f.write(response.content)
        print("✓ Saved to: example_voice_design.wav")
    else:
        print(f"✗ Error: {response.status_code}")


def example_voice_clone():
    """Example: Voice cloning from reference audio"""
    print("\n" + "="*60)
    print("Example 3: Voice Cloning (Using Reference Audio)")
    print("="*60)
    
    print("\nNote: This example requires a reference audio file.")
    print("For demonstration, we'll use a public URL.")
    print("In practice, you can use your own audio files.\n")
    
    # Using a public reference audio (you should replace with your own)
    ref_audio_url = "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3-TTS-Repo/clone.wav"
    ref_text = "Okay. Yeah. I resent you. I love you. I respect you. But you know what? You blew it! And thanks to you."
    
    print("Cloning voice from reference audio...")
    response = requests.post(
        f"{BASE_URL}/api/v1/base/clone",
        headers=headers,
        json={
            "text": "This is a demonstration of voice cloning technology, where I can speak with the characteristics of the reference voice.",
            "language": "English",
            "ref_audio_url": ref_audio_url,
            "ref_text": ref_text,
            "x_vector_only_mode": False,
            "response_format": "wav"
        }
    )
    
    if response.status_code == 200:
        with open("example_voice_clone.wav", "wb") as f:
            f.write(response.content)
        print("✓ Saved to: example_voice_clone.wav")
    else:
        print(f"✗ Error: {response.status_code}")
    
    # Also demonstrate the reusable prompt feature
    print("\nCreating a reusable voice clone prompt...")
    response = requests.post(
        f"{BASE_URL}/api/v1/base/create-prompt",
        headers=headers,
        json={
            "ref_audio_url": ref_audio_url,
            "ref_text": ref_text,
            "x_vector_only_mode": False
        }
    )
    
    if response.status_code == 200:
        prompt_data = response.json()
        prompt_id = prompt_data["prompt_id"]
        print(f"✓ Created prompt: {prompt_id}")
        
        # Use the prompt
        print("Using the saved prompt for new generation...")
        response = requests.post(
            f"{BASE_URL}/api/v1/base/generate-with-prompt",
            headers=headers,
            json={
                "text": "Now I can reuse this voice profile for multiple generations without re-processing the reference audio.",
                "language": "English",
                "prompt_id": prompt_id,
                "response_format": "wav"
            }
        )
        
        if response.status_code == 200:
            with open("example_voice_clone_prompt.wav", "wb") as f:
                f.write(response.content)
            print("✓ Saved to: example_voice_clone_prompt.wav")


def main():
    print("\n" + "="*60)
    print("Qwen3-TTS API Server - Complete Examples")
    print("="*60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:10]}...")
    
    # Check server
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("\n✗ Server is not responding correctly")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print(f"\n✗ Could not connect to {BASE_URL}")
        print("Please make sure the server is running!")
        sys.exit(1)
    
    print("✓ Server is running\n")
    
    try:
        example_custom_voice()
        example_voice_design()
        example_voice_clone()
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)
        print("\nGenerated files:")
        print("  - example_custom_voice.wav")
        print("  - example_voice_design.wav")
        print("  - example_voice_clone.wav")
        print("  - example_voice_clone_prompt.wav")
        print("\nYou can play these files to hear the results!")
        
    except Exception as e:
        print(f"\n✗ Error during examples: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
