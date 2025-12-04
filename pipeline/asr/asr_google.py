#!/usr/bin/env python3
"""
VAANI Google Cloud Speech-to-Text Integration
Baseline ASR pipeline using Google Cloud Speech API.

Usage:
    python pipeline/asr/asr_google.py --audio data/audio_raw/day1/audio_0001.wav
    python pipeline/asr/asr_google.py --batch --input-dir data/audio_raw/day1
"""

import os
import argparse
import csv
from pathlib import Path
import json

# Try to import Google Cloud Speech
try:
    from google.cloud import speech
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠️  Google Cloud Speech not installed.")
    print("   Install with: pip install google-cloud-speech")

# Fallback to speech_recognition
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False


def transcribe_audio_google_cloud(audio_path, language_code="en-IN"):
    """
    Transcribe audio using Google Cloud Speech API.
    
    Args:
        audio_path: Path to audio file
        language_code: Language code (default: en-IN for Indian English)
    
    Returns:
        dict: Transcription result with text and confidence
    """
    if not GOOGLE_AVAILABLE:
        raise ImportError("Google Cloud Speech not available")
    
    client = speech.SpeechClient()
    
    # Load audio file
    with open(audio_path, 'rb') as audio_file:
        content = audio_file.read()
    
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language_code,
        enable_automatic_punctuation=True,
    )
    
    # Perform transcription
    response = client.recognize(config=config, audio=audio)
    
    # Extract results
    if response.results:
        result = response.results[0]
        alternative = result.alternatives[0]
        return {
            "text": alternative.transcript,
            "confidence": alternative.confidence,
            "success": True
        }
    else:
        return {
            "text": "",
            "confidence": 0.0,
            "success": False,
            "error": "No transcription results"
        }


def transcribe_audio_speech_recognition(audio_path, language="en-IN"):
    """
    Transcribe audio using SpeechRecognition library (fallback).
    
    Args:
        audio_path: Path to audio file
        language: Language code
    
    Returns:
        dict: Transcription result
    """
    if not SR_AVAILABLE:
        raise ImportError("SpeechRecognition not available")
    
    recognizer = sr.Recognizer()
    
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        
        # Use Google Speech Recognition (free tier)
        text = recognizer.recognize_google(audio, language=language)
        
        return {
            "text": text,
            "confidence": 1.0,  # Not provided by this API
            "success": True
        }
    
    except sr.UnknownValueError:
        return {
            "text": "",
            "confidence": 0.0,
            "success": False,
            "error": "Could not understand audio"
        }
    except sr.RequestError as e:
        return {
            "text": "",
            "confidence": 0.0,
            "success": False,
            "error": f"API error: {e}"
        }


def transcribe_audio(audio_path, method="auto", language="en-IN"):
    """
    Transcribe audio file using available method.
    
    Args:
        audio_path: Path to audio file
        method: "google_cloud", "speech_recognition", or "auto"
        language: Language code
    
    Returns:
        dict: Transcription result
    """
    if method == "auto":
        if GOOGLE_AVAILABLE:
            method = "google_cloud"
        elif SR_AVAILABLE:
            method = "speech_recognition"
        else:
            return {
                "text": "",
                "confidence": 0.0,
                "success": False,
                "error": "No ASR library available"
            }
    
    try:
        if method == "google_cloud":
            return transcribe_audio_google_cloud(audio_path, language)
        elif method == "speech_recognition":
            return transcribe_audio_speech_recognition(audio_path, language)
        else:
            return {
                "text": "",
                "confidence": 0.0,
                "success": False,
                "error": f"Unknown method: {method}"
            }
    except Exception as e:
        return {
            "text": "",
            "confidence": 0.0,
            "success": False,
            "error": str(e)
        }


def batch_transcribe(input_dir, output_csv, method="auto", language="en-IN"):
    """
    Batch transcribe all audio files in a directory.
    
    Args:
        input_dir: Directory containing audio files
        output_csv: Output CSV file path
        method: ASR method to use
        language: Language code
    """
    audio_files = sorted(Path(input_dir).glob("*.wav"))
    
    print(f"🎙️  Found {len(audio_files)} audio files")
    print(f"🔧 Using method: {method}")
    print(f"🌍 Language: {language}\n")
    
    results = []
    
    for i, audio_path in enumerate(audio_files, 1):
        print(f"[{i}/{len(audio_files)}] Processing: {audio_path.name}")
        
        result = transcribe_audio(str(audio_path), method, language)
        
        results.append({
            "audio_file": audio_path.name,
            "transcription": result["text"],
            "confidence": result["confidence"],
            "success": result["success"],
            "error": result.get("error", "")
        })
        
        if result["success"]:
            print(f"   ✅ {result['text'][:50]}...")
        else:
            print(f"   ❌ {result.get('error', 'Failed')}")
    
    # Save results
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["audio_file", "transcription", "confidence", "success", "error"])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✅ Results saved to: {output_csv}")
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    print(f"\n📊 Summary:")
    print(f"   Total: {len(results)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {len(results) - successful}")


def main():
    parser = argparse.ArgumentParser(description="VAANI Google ASR Pipeline")
    parser.add_argument("--audio", help="Single audio file to transcribe")
    parser.add_argument("--batch", action="store_true", help="Batch process directory")
    parser.add_argument("--input-dir", default="data/audio_raw/day1",
                        help="Input directory for batch processing")
    parser.add_argument("--output", default="data/transcripts/asr_results.csv",
                        help="Output CSV file")
    parser.add_argument("--method", choices=["auto", "google_cloud", "speech_recognition"],
                        default="auto", help="ASR method to use")
    parser.add_argument("--language", default="en-IN",
                        help="Language code (default: en-IN)")
    
    args = parser.parse_args()
    
    if args.audio:
        # Single file transcription
        result = transcribe_audio(args.audio, args.method, args.language)
        print(json.dumps(result, indent=2))
    
    elif args.batch:
        # Batch transcription
        batch_transcribe(args.input_dir, args.output, args.method, args.language)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

