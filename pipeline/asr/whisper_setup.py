#!/usr/bin/env python3
"""
VAANI Whisper Setup
Setup and verify Whisper installation for fine-tuning.

Usage:
    python pipeline/asr/whisper_setup.py --check
    python pipeline/asr/whisper_setup.py --test-inference
"""

import argparse
import sys
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking Whisper dependencies...\n")
    
    dependencies = {
        "torch": "PyTorch",
        "whisper": "OpenAI Whisper",
        "transformers": "Hugging Face Transformers",
        "datasets": "Hugging Face Datasets",
        "librosa": "Audio processing",
        "soundfile": "Audio I/O",
    }
    
    missing = []
    installed = []
    
    for module, name in dependencies.items():
        try:
            __import__(module)
            installed.append(f"✅ {name} ({module})")
        except ImportError:
            missing.append(f"❌ {name} ({module})")
    
    # Print results
    if installed:
        print("Installed:")
        for item in installed:
            print(f"  {item}")
    
    if missing:
        print("\nMissing:")
        for item in missing:
            print(f"  {item}")
        
        print("\n📦 Install missing packages:")
        print("   pip install openai-whisper torch transformers datasets librosa soundfile")
        return False
    
    print("\n✅ All dependencies installed!")
    return True


def test_whisper_inference(audio_path=None):
    """Test Whisper inference on a sample audio file."""
    try:
        import whisper
        import torch
    except ImportError:
        print("❌ Whisper not installed. Run with --check first.")
        return False
    
    print("\n🎙️  Testing Whisper Inference...\n")
    
    # Check CUDA availability
    if torch.cuda.is_available():
        print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
        device = "cuda"
    else:
        print("⚠️  CUDA not available. Using CPU (slower)")
        device = "cpu"
    
    # Load model
    print("\n📥 Loading Whisper base model...")
    model = whisper.load_model("base", device=device)
    print("✅ Model loaded successfully")
    
    # Test inference
    if audio_path and Path(audio_path).exists():
        print(f"\n🔊 Transcribing: {audio_path}")
        result = model.transcribe(audio_path)
        print(f"\n📝 Transcription: {result['text']}")
        print(f"🌍 Detected language: {result['language']}")
    else:
        print("\n⚠️  No audio file provided. Skipping inference test.")
        print("   Use: --test-inference --audio <path>")
    
    return True


def check_gpu_memory():
    """Check GPU memory availability."""
    try:
        import torch
        if torch.cuda.is_available():
            print("\n💾 GPU Memory Info:")
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                total_memory = props.total_memory / 1024**3  # Convert to GB
                print(f"   GPU {i}: {props.name}")
                print(f"   Total Memory: {total_memory:.2f} GB")
                
                # Check available memory
                allocated = torch.cuda.memory_allocated(i) / 1024**3
                reserved = torch.cuda.memory_reserved(i) / 1024**3
                print(f"   Allocated: {allocated:.2f} GB")
                print(f"   Reserved: {reserved:.2f} GB")
        else:
            print("\n⚠️  No GPU available")
    except Exception as e:
        print(f"\n❌ Error checking GPU: {e}")


def print_setup_guide():
    """Print setup guide for Whisper fine-tuning."""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         🎙️  WHISPER FINE-TUNING SETUP GUIDE  🎙️         ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

📋 Prerequisites:
   1. Python 3.8+
   2. CUDA-capable GPU (recommended for training)
   3. At least 8GB GPU memory for base model
   4. 16GB+ GPU memory for larger models

📦 Installation:
   pip install openai-whisper
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   pip install transformers datasets
   pip install librosa soundfile

📁 Data Preparation:
   1. Prepare audio files (16kHz, mono, WAV format)
   2. Create annotations JSON with transcriptions
   3. Split into train/val/test sets
   4. Run: python pipeline/asr/prepare_dataset.py

🏋️  Training:
   1. Configure training parameters in whisper_config.json
   2. Run fine-tuning script (coming in Week 5-6)
   3. Monitor training metrics
   4. Evaluate on test set

📊 Recommended Model Sizes:
   - tiny: 39M params, ~1GB VRAM, fastest
   - base: 74M params, ~1GB VRAM, good balance
   - small: 244M params, ~2GB VRAM, better accuracy
   - medium: 769M params, ~5GB VRAM, high accuracy
   - large: 1550M params, ~10GB VRAM, best accuracy

🎯 For VAANI:
   - Start with 'base' model for fine-tuning
   - Use Indian English (en-IN) data
   - Target: 500-1000 annotated samples minimum
   - Expected training time: 2-4 hours on GPU

📚 Next Steps:
   1. Run: python pipeline/asr/whisper_setup.py --check
   2. Run: python pipeline/asr/prepare_dataset.py
   3. Review: pipeline/asr/whisper_config.json
   4. Wait for Week 5-6 for fine-tuning scripts
    """)


def main():
    parser = argparse.ArgumentParser(description="VAANI Whisper Setup")
    parser.add_argument("--check", action="store_true",
                        help="Check dependencies")
    parser.add_argument("--test-inference", action="store_true",
                        help="Test Whisper inference")
    parser.add_argument("--audio", help="Audio file for inference test")
    parser.add_argument("--gpu-info", action="store_true",
                        help="Show GPU information")
    parser.add_argument("--guide", action="store_true",
                        help="Show setup guide")
    
    args = parser.parse_args()
    
    if args.guide:
        print_setup_guide()
    
    elif args.check:
        check_dependencies()
        check_gpu_memory()
    
    elif args.test_inference:
        if check_dependencies():
            test_whisper_inference(args.audio)
    
    elif args.gpu_info:
        check_gpu_memory()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

