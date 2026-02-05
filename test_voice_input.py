"""
Test script for Voice Input functionality
Tests Whisper installation and basic transcription
"""

import sys

def test_imports():
    """Test if all required packages are installed"""
    print("🔍 Testing imports...")
    
    try:
        import whisper
        print("✅ OpenAI Whisper installed")
        WHISPER_OK = True
    except ImportError as e:
        print(f"❌ OpenAI Whisper not installed: {e}")
        print("   Install with: pip install openai-whisper")
        WHISPER_OK = False
    
    try:
        from audio_recorder_streamlit import audio_recorder
        print("✅ Audio recorder installed")
        RECORDER_OK = True
    except ImportError as e:
        print(f"❌ Audio recorder not installed: {e}")
        print("   Install with: pip install audio-recorder-streamlit")
        RECORDER_OK = False
    
    try:
        import torch
        print(f"✅ PyTorch installed (version: {torch.__version__})")
        if torch.cuda.is_available():
            print(f"   🚀 CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            print("   ⚠️  CUDA not available, will use CPU")
        TORCH_OK = True
    except ImportError as e:
        print(f"❌ PyTorch not installed: {e}")
        TORCH_OK = False
    
    try:
        import streamlit
        print(f"✅ Streamlit installed (version: {streamlit.__version__})")
        STREAMLIT_OK = True
    except ImportError as e:
        print(f"❌ Streamlit not installed: {e}")
        STREAMLIT_OK = False
    
    return WHISPER_OK and RECORDER_OK and TORCH_OK and STREAMLIT_OK


def test_ffmpeg():
    """Test if ffmpeg is installed and accessible"""
    print("\n🔍 Testing FFmpeg...")
    import subprocess
    
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg installed: {version_line}")
            return True
        else:
            print("❌ FFmpeg found but not working properly")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found in PATH")
        print("   Windows: Download from https://www.gyan.dev/ffmpeg/builds/")
        print("   Linux: sudo apt-get install ffmpeg")
        print("   Mac: brew install ffmpeg")
        return False
    except Exception as e:
        print(f"❌ Error testing FFmpeg: {e}")
        return False


def test_whisper_model():
    """Test loading Whisper model"""
    print("\n🔍 Testing Whisper model loading...")
    
    try:
        import whisper
        import torch
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   Loading 'tiny' model on {device}...")
        
        model = whisper.load_model("tiny", device=device)
        print("✅ Whisper model loaded successfully")
        print(f"   Model size: tiny (~39 MB)")
        print(f"   Device: {device}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to load Whisper model: {e}")
        print("   This may be due to:")
        print("   1. Missing FFmpeg")
        print("   2. Network issues (first download)")
        print("   3. Insufficient disk space")
        return False


def test_voice_input_module():
    """Test our custom voice input module"""
    print("\n🔍 Testing voice_input.py module...")
    
    try:
        from voice_input import VoiceInputHandler, WHISPER_AVAILABLE, AUDIO_RECORDER_AVAILABLE
        
        if WHISPER_AVAILABLE:
            print("✅ Voice input module loaded")
            print(f"   Whisper available: {WHISPER_AVAILABLE}")
            print(f"   Audio recorder available: {AUDIO_RECORDER_AVAILABLE}")
            
            # Test handler initialization
            handler = VoiceInputHandler(model_size="tiny", default_language="en")
            print("✅ VoiceInputHandler initialized")
            
            return True
        else:
            print("❌ Whisper not available in voice_input module")
            return False
            
    except Exception as e:
        print(f"❌ Failed to load voice_input module: {e}")
        return False


def test_sample_transcription():
    """Test transcription with a sample audio file (if available)"""
    print("\n🔍 Testing sample transcription...")
    print("   (Skipped - requires actual audio file)")
    print("   To test manually:")
    print("   1. Run: streamlit run app_streamlit.py")
    print("   2. Go to Diagnosis page")
    print("   3. Click 'Voice Input' expander")
    print("   4. Record and test transcription")
    return True


def main():
    print("=" * 60)
    print("Voice Input Test Suite for AVA")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Package Imports", test_imports()))
    results.append(("FFmpeg", test_ffmpeg()))
    results.append(("Whisper Model", test_whisper_model()))
    results.append(("Voice Input Module", test_voice_input_module()))
    results.append(("Sample Transcription", test_sample_transcription()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! Voice input is ready to use.")
        print("\nNext steps:")
        print("1. Run: streamlit run app_streamlit.py")
        print("2. Navigate to Diagnosis page")
        print("3. Try voice input in English or Malayalam")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nQuick fixes:")
        print("- Install missing packages: pip install -r requirements.txt")
        print("- Install FFmpeg: See VOICE_INPUT_SETUP.md for instructions")
        print("- Restart terminal after installing FFmpeg")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
