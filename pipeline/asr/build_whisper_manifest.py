"""
Build Whisper training manifest files.

Creates train/val/test JSONL files for Whisper fine-tuning.
"""

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict

try:
    import librosa
except ImportError:
    librosa = None

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.logger import get_logger
from utils.helpers import ensure_dir, load_json

logger = get_logger(__name__)


class WhisperManifestBuilder:
    """Build Whisper training manifests."""
    
    def __init__(self, output_dir="data/whisper_dataset"):
        """
        Initialize manifest builder.
        
        Args:
            output_dir: Output directory for manifest files
        """
        if librosa is None:
            raise ImportError("librosa is required. Install with: pip install librosa")
        
        self.output_dir = Path(output_dir)
        ensure_dir(self.output_dir)
        logger.info(f"WhisperManifestBuilder initialized: {output_dir}")
    
    def get_audio_duration(self, audio_path):
        """
        Get audio duration.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds
        """
        try:
            duration = librosa.get_duration(path=str(audio_path))
            return round(duration, 2)
        except Exception as e:
            logger.warning(f"Could not get duration for {audio_path}: {e}")
            return 0.0
    
    def build_from_annotations(self, annotations_file, audio_dir, 
                              train_ratio=0.8, val_ratio=0.1, test_ratio=0.1):
        """
        Build manifests from annotation file.
        
        Args:
            annotations_file: Path to annotations JSON
            audio_dir: Directory containing audio files
            train_ratio: Training set ratio
            val_ratio: Validation set ratio
            test_ratio: Test set ratio
            
        Returns:
            Dictionary with manifest statistics
        """
        # Load annotations
        annotations = load_json(annotations_file)
        logger.info(f"Loaded {len(annotations)} annotations")
        
        audio_dir = Path(audio_dir)
        
        # Prepare manifest entries
        manifest_entries = []
        
        for ann in annotations:
            audio_file = ann.get("audio_file", "")
            transcription = ann.get("transcription", "")
            
            if not audio_file or not transcription:
                continue
            
            # Find audio file
            audio_path = Path(audio_file)
            if not audio_path.exists():
                # Try in audio_dir
                audio_path = audio_dir / audio_path.name
            
            if not audio_path.exists():
                logger.warning(f"Audio file not found: {audio_file}")
                continue
            
            # Get duration
            duration = self.get_audio_duration(audio_path)
            
            if duration == 0.0:
                continue
            
            # Create manifest entry
            entry = {
                "audio_filepath": str(audio_path.absolute()),
                "text": transcription,
                "duration": duration
            }
            
            manifest_entries.append(entry)
        
        logger.info(f"Created {len(manifest_entries)} manifest entries")
        
        # Split into train/val/test
        total = len(manifest_entries)
        train_size = int(total * train_ratio)
        val_size = int(total * val_ratio)
        
        train_entries = manifest_entries[:train_size]
        val_entries = manifest_entries[train_size:train_size + val_size]
        test_entries = manifest_entries[train_size + val_size:]
        
        # Save manifests
        train_file = self.output_dir / "train.jsonl"
        val_file = self.output_dir / "val.jsonl"
        test_file = self.output_dir / "test.jsonl"
        
        self._save_jsonl(train_entries, train_file)
        self._save_jsonl(val_entries, val_file)
        self._save_jsonl(test_entries, test_file)
        
        stats = {
            "total": total,
            "train": len(train_entries),
            "val": len(val_entries),
            "test": len(test_entries),
            "train_file": str(train_file),
            "val_file": str(val_file),
            "test_file": str(test_file)
        }
        
        logger.info(f"Manifests created: train={len(train_entries)}, "
                   f"val={len(val_entries)}, test={len(test_entries)}")
        
        return stats
    
    def _save_jsonl(self, entries, output_file):
        """Save entries to JSONL file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        logger.info(f"Saved {len(entries)} entries to {output_file}")


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Build Whisper training manifests")
    parser.add_argument("--annotations", type=str, required=True,
                       help="Path to annotations JSON file")
    parser.add_argument("--audio-dir", type=str, required=True,
                       help="Directory containing audio files")
    parser.add_argument("--output-dir", type=str, default="data/whisper_dataset",
                       help="Output directory for manifests")
    parser.add_argument("--train-ratio", type=float, default=0.8,
                       help="Training set ratio")
    parser.add_argument("--val-ratio", type=float, default=0.1,
                       help="Validation set ratio")
    parser.add_argument("--test-ratio", type=float, default=0.1,
                       help="Test set ratio")
    
    args = parser.parse_args()
    
    builder = WhisperManifestBuilder(output_dir=args.output_dir)
    
    stats = builder.build_from_annotations(
        annotations_file=args.annotations,
        audio_dir=args.audio_dir,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio
    )
    
    print("\n" + "=" * 70)
    print("📊 Whisper Manifest Statistics")
    print("=" * 70)
    print(f"Total samples: {stats['total']}")
    print(f"Training: {stats['train']}")
    print(f"Validation: {stats['val']}")
    print(f"Test: {stats['test']}")
    print(f"\nFiles created:")
    print(f"  - {stats['train_file']}")
    print(f"  - {stats['val_file']}")
    print(f"  - {stats['test_file']}")
    print("=" * 70)


if __name__ == "__main__":
    main()

