#!/usr/bin/env python3
"""
VAANI Whisper Dataset Preparation
Prepare audio dataset for Whisper fine-tuning.

Usage:
    python pipeline/asr/prepare_dataset.py
    python pipeline/asr/prepare_dataset.py --split 0.8 0.1 0.1
"""

import json
import argparse
import random
from pathlib import Path
import shutil

def load_annotations(filepath):
    """Load annotations from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def prepare_whisper_manifest(annotations, audio_dir, output_file):
    """
    Prepare manifest file for Whisper training.
    
    Format: JSON Lines with {audio_path, text}
    """
    manifest = []
    
    for ann in annotations:
        audio_file = ann.get('audio_file', '')
        transcription = ann.get('transcription', '')
        audio_path = Path(audio_dir) / audio_file
        
        if audio_path.exists():
            manifest.append({
                "audio": str(audio_path),
                "text": transcription,
                "id": ann.get('id', ''),
                "duration": ann.get('metadata', {}).get('duration_seconds', 0.0)
            })
    
    # Save as JSON Lines
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in manifest:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    return len(manifest)


def split_dataset(annotations, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, seed=42):
    """
    Split dataset into train/val/test sets.
    
    Args:
        annotations: List of annotations
        train_ratio: Proportion for training
        val_ratio: Proportion for validation
        test_ratio: Proportion for testing
        seed: Random seed for reproducibility
    
    Returns:
        tuple: (train, val, test) annotation lists
    """
    random.seed(seed)
    
    # Shuffle annotations
    shuffled = annotations.copy()
    random.shuffle(shuffled)
    
    total = len(shuffled)
    train_size = int(total * train_ratio)
    val_size = int(total * val_ratio)
    
    train = shuffled[:train_size]
    val = shuffled[train_size:train_size + val_size]
    test = shuffled[train_size + val_size:]
    
    return train, val, test


def main():
    parser = argparse.ArgumentParser(description="Prepare dataset for Whisper fine-tuning")
    parser.add_argument("--annotations", default="data/annotations/annotations_day2.json",
                        help="Input annotations JSON")
    parser.add_argument("--audio-dir", default="data/audio_raw/day1",
                        help="Directory containing audio files")
    parser.add_argument("--output-dir", default="data/whisper_dataset",
                        help="Output directory for prepared dataset")
    parser.add_argument("--split", nargs=3, type=float, default=[0.8, 0.1, 0.1],
                        metavar=('TRAIN', 'VAL', 'TEST'),
                        help="Train/val/test split ratios")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")
    
    args = parser.parse_args()
    
    print("🎙️  Preparing Whisper Dataset\n")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load annotations
    print(f"📂 Loading annotations from: {args.annotations}")
    annotations = load_annotations(args.annotations)
    print(f"   Total annotations: {len(annotations)}")
    
    # Split dataset
    train_ratio, val_ratio, test_ratio = args.split
    print(f"\n📊 Splitting dataset: {train_ratio:.0%} train, {val_ratio:.0%} val, {test_ratio:.0%} test")
    
    train, val, test = split_dataset(annotations, train_ratio, val_ratio, test_ratio, args.seed)
    
    print(f"   Train: {len(train)} samples")
    print(f"   Val: {len(val)} samples")
    print(f"   Test: {len(test)} samples")
    
    # Prepare manifests
    print(f"\n📝 Creating manifest files...")
    
    train_count = prepare_whisper_manifest(train, args.audio_dir, output_dir / "train.jsonl")
    val_count = prepare_whisper_manifest(val, args.audio_dir, output_dir / "val.jsonl")
    test_count = prepare_whisper_manifest(test, args.audio_dir, output_dir / "test.jsonl")
    
    print(f"   ✅ Train manifest: {train_count} samples")
    print(f"   ✅ Val manifest: {val_count} samples")
    print(f"   ✅ Test manifest: {test_count} samples")
    
    # Save split info
    split_info = {
        "total_samples": len(annotations),
        "train_samples": len(train),
        "val_samples": len(val),
        "test_samples": len(test),
        "train_ratio": train_ratio,
        "val_ratio": val_ratio,
        "test_ratio": test_ratio,
        "seed": args.seed,
        "audio_dir": args.audio_dir
    }
    
    with open(output_dir / "split_info.json", 'w', encoding='utf-8') as f:
        json.dump(split_info, f, indent=2)
    
    print(f"\n✅ Dataset preparation complete!")
    print(f"📁 Output directory: {output_dir}")
    print(f"\n📋 Files created:")
    print(f"   - train.jsonl ({train_count} samples)")
    print(f"   - val.jsonl ({val_count} samples)")
    print(f"   - test.jsonl ({test_count} samples)")
    print(f"   - split_info.json")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Review the manifest files")
    print(f"   2. Configure training in whisper_config.json")
    print(f"   3. Wait for Week 5-6 for fine-tuning scripts")


if __name__ == "__main__":
    main()

