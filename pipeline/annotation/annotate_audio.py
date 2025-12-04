#!/usr/bin/env python3
"""
VAANI Audio Annotation Tool
Interactive tool for annotating audio files with transcriptions, intents, and entities.

Usage:
    python pipeline/annotation/annotate_audio.py
    python pipeline/annotation/annotate_audio.py --start-from 100
"""

import csv
import json
import os
import argparse
from pathlib import Path
from datetime import datetime
import sys

# Try to import audio playback library
try:
    import pygame
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️  pygame not installed. Audio playback disabled.")
    print("   Install with: pip install pygame")

# Intent categories
INTENTS = [
    "GREETING", "QUERY_TIME", "QUERY_WEATHER", "OPEN_APP",
    "CALL_PERSON", "GENERAL_KNOWLEDGE", "ALARM_SET", "REMINDER_SET",
    "JOKE", "CASUAL_CHAT"
]

# Entity types
ENTITY_TYPES = ["TIME", "LOCATION", "PERSON", "APP", "DATE", "TASK"]


def play_audio(audio_path):
    """Play audio file using pygame."""
    if not AUDIO_AVAILABLE:
        print(f"   [Audio playback disabled: {audio_path}]")
        return
    
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"   ⚠️  Could not play audio: {e}")


def get_user_input(prompt, options=None):
    """Get user input with optional validation."""
    while True:
        if options:
            print(f"\n{prompt}")
            for i, opt in enumerate(options, 1):
                print(f"  {i}. {opt}")
            choice = input("Enter number: ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
                print("❌ Invalid choice. Try again.")
            except ValueError:
                print("❌ Please enter a number.")
        else:
            response = input(f"{prompt}: ").strip()
            if response:
                return response
            print("❌ Input cannot be empty.")


def extract_entities(transcription):
    """Interactive entity extraction."""
    entities = []
    print("\n📝 Entity Extraction")
    print(f"   Text: {transcription}")
    
    while True:
        add_entity = input("\n   Add entity? (y/n): ").strip().lower()
        if add_entity != 'y':
            break
        
        entity_type = get_user_input("   Select entity type", ENTITY_TYPES)
        entity_value = get_user_input("   Enter entity value (text from transcription)")
        
        # Find position in text
        start = transcription.find(entity_value)
        if start == -1:
            print(f"   ⚠️  '{entity_value}' not found in transcription. Adding anyway.")
            start = 0
            end = len(entity_value)
        else:
            end = start + len(entity_value)
        
        entities.append({
            "type": entity_type,
            "value": entity_value,
            "start": start,
            "end": end
        })
        print(f"   ✅ Added: {entity_type} = '{entity_value}'")
    
    return entities


def annotate_audio_file(query_id, query_text, audio_path, annotator_name):
    """Annotate a single audio file."""
    print(f"\n{'='*60}")
    print(f"📝 Annotating: {query_id}")
    print(f"{'='*60}")
    print(f"Expected text: {query_text}")
    
    # Play audio
    if os.path.exists(audio_path):
        print(f"\n🔊 Playing audio: {audio_path}")
        play_audio(audio_path)
    else:
        print(f"\n⚠️  Audio file not found: {audio_path}")
    
    # Get transcription
    print("\n1️⃣  TRANSCRIPTION")
    use_expected = input(f"   Use expected text? (y/n): ").strip().lower()
    if use_expected == 'y':
        transcription = query_text
    else:
        transcription = get_user_input("   Enter transcription")
    
    # Get intent
    print("\n2️⃣  INTENT CLASSIFICATION")
    intent = get_user_input("   Select intent", INTENTS)
    
    # Get entities
    print("\n3️⃣  ENTITY EXTRACTION")
    entities = extract_entities(transcription)
    
    # Quality score
    print("\n4️⃣  QUALITY ASSESSMENT")
    quality_score = int(get_user_input("   Quality score (1-5)"))
    
    # Notes
    notes = input("\n5️⃣  Notes (optional): ").strip()
    
    # Create annotation
    annotation = {
        "id": query_id,
        "audio_file": os.path.basename(audio_path),
        "transcription": transcription,
        "intent": intent,
        "entities": entities,
        "metadata": {
            "duration_seconds": 0.0,  # TODO: Calculate from audio
            "sample_rate": 16000,
            "annotator": annotator_name,
            "annotation_date": datetime.now().strftime("%Y-%m-%d"),
            "quality_score": quality_score,
            "notes": notes
        }
    }
    
    return annotation


def main():
    parser = argparse.ArgumentParser(description="VAANI Audio Annotation Tool")
    parser.add_argument("--queries", default="data/queries/queries_day1.csv",
                        help="Path to queries CSV")
    parser.add_argument("--audio-dir", default="data/audio_raw/day1",
                        help="Directory containing audio files")
    parser.add_argument("--output", default="data/annotations/annotations_day2.json",
                        help="Output JSON file")
    parser.add_argument("--start-from", type=int, default=0,
                        help="Start from query index")
    parser.add_argument("--annotator", default="annotator_01",
                        help="Annotator name/ID")
    
    args = parser.parse_args()
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║           🎙️  VAANI ANNOTATION TOOL  🎙️                 ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Load existing annotations if any
    annotations = []
    if os.path.exists(args.output):
        with open(args.output, 'r', encoding='utf-8') as f:
            annotations = json.load(f)
        print(f"📂 Loaded {len(annotations)} existing annotations")
    
    # Load queries
    queries = []
    with open(args.queries, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        queries = list(reader)
    
    print(f"📊 Total queries: {len(queries)}")
    print(f"🎯 Starting from index: {args.start_from}")
    
    # Annotate
    for i, query in enumerate(queries[args.start_from:], start=args.start_from):
        query_id = query['id']
        query_text = query['text']
        audio_filename = f"audio_{query_id[1:]}.wav"
        audio_path = os.path.join(args.audio_dir, audio_filename)
        
        try:
            annotation = annotate_audio_file(query_id, query_text, audio_path, args.annotator)
            annotations.append(annotation)
            
            # Save after each annotation
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(annotations, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Saved annotation {i+1}/{len(queries)}")
            
            # Continue?
            if i < len(queries) - 1:
                cont = input("\n   Continue to next? (y/n/q to quit): ").strip().lower()
                if cont == 'q':
                    break
                elif cont != 'y':
                    print(f"\n💾 Progress saved. Resume with: --start-from {i+1}")
                    break
        
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Interrupted. Progress saved. Resume with: --start-from {i}")
            break
    
    print(f"\n✅ Annotation complete! Total annotations: {len(annotations)}")
    print(f"📁 Saved to: {args.output}")


if __name__ == "__main__":
    main()

