"""
Prepare audio files for ASR training/inference.

Converts raw audio to processed format with validation.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pipeline.data.clean_audio import AudioCleaner
from utils.logger import get_logger
from utils.helpers import ensure_dir, save_json

logger = get_logger(__name__)


class ASRDataPreparator:
    """Prepare audio data for ASR."""
    
    def __init__(self, target_sr=16000, min_duration=0.5, max_duration=30.0):
        """
        Initialize ASR data preparator.
        
        Args:
            target_sr: Target sample rate
            min_duration: Minimum audio duration in seconds
            max_duration: Maximum audio duration in seconds
        """
        self.cleaner = AudioCleaner(target_sr=target_sr)
        self.min_duration = min_duration
        self.max_duration = max_duration
        logger.info(f"ASRDataPreparator initialized: {target_sr}Hz, "
                   f"duration range: {min_duration}-{max_duration}s")
    
    def validate_audio(self, audio_path):
        """
        Validate audio file for ASR.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Tuple of (is_valid, quality_metrics)
        """
        try:
            audio, sr = self.cleaner.load_audio(audio_path)
            quality = self.cleaner.check_quality(audio, sr)
            
            # Additional ASR-specific checks
            is_valid = (
                quality["is_valid"] and
                self.min_duration <= quality["duration"] <= self.max_duration
            )
            
            return is_valid, quality
        
        except Exception as e:
            logger.error(f"Validation error for {audio_path}: {e}")
            return False, {"error": str(e)}
    
    def prepare_batch(self, input_dir, output_dir, metadata_file=None):
        """
        Prepare batch of audio files.
        
        Args:
            input_dir: Input directory with raw audio
            output_dir: Output directory for processed audio
            metadata_file: Optional metadata JSON file
            
        Returns:
            Dictionary with preparation statistics
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        ensure_dir(output_dir)
        
        # Find audio files
        audio_files = list(input_dir.glob("*.wav")) + list(input_dir.glob("*.mp3"))
        logger.info(f"Found {len(audio_files)} audio files in {input_dir}")
        
        # Load metadata if provided
        metadata = {}
        if metadata_file and Path(metadata_file).exists():
            with open(metadata_file) as f:
                metadata_list = json.load(f)
                metadata = {Path(item["audio_file"]).name: item for item in metadata_list}
        
        # Process files
        results = []
        valid_count = 0
        invalid_count = 0
        
        for audio_file in audio_files:
            output_file = output_dir / audio_file.name
            
            try:
                # Clean audio
                quality = self.cleaner.clean(audio_file, output_file)
                
                # Validate
                is_valid = (
                    quality["is_valid"] and
                    self.min_duration <= quality["duration"] <= self.max_duration
                )
                
                # Prepare result entry
                result = {
                    "input_file": str(audio_file),
                    "output_file": str(output_file),
                    "is_valid": is_valid,
                    "quality": quality
                }
                
                # Add metadata if available
                if audio_file.name in metadata:
                    result.update(metadata[audio_file.name])
                
                results.append(result)
                
                if is_valid:
                    valid_count += 1
                    logger.info(f"✅ Processed: {audio_file.name}")
                else:
                    invalid_count += 1
                    logger.warning(f"⚠️ Invalid: {audio_file.name} - {quality}")
            
            except Exception as e:
                logger.error(f"❌ Error processing {audio_file.name}: {e}")
                invalid_count += 1
                results.append({
                    "input_file": str(audio_file),
                    "is_valid": False,
                    "error": str(e)
                })
        
        # Save results
        results_file = output_dir / "preparation_results.json"
        save_json(results, results_file)
        
        stats = {
            "total": len(audio_files),
            "valid": valid_count,
            "invalid": invalid_count,
            "results_file": str(results_file)
        }
        
        logger.info(f"Preparation complete: {valid_count}/{len(audio_files)} valid")
        return stats


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Prepare audio for ASR")
    parser.add_argument("--input-dir", type=str, required=True,
                       help="Input directory with raw audio")
    parser.add_argument("--output-dir", type=str, required=True,
                       help="Output directory for processed audio")
    parser.add_argument("--metadata", type=str,
                       help="Optional metadata JSON file")
    parser.add_argument("--sample-rate", type=int, default=16000,
                       help="Target sample rate")
    parser.add_argument("--min-duration", type=float, default=0.5,
                       help="Minimum duration in seconds")
    parser.add_argument("--max-duration", type=float, default=30.0,
                       help="Maximum duration in seconds")
    
    args = parser.parse_args()
    
    preparator = ASRDataPreparator(
        target_sr=args.sample_rate,
        min_duration=args.min_duration,
        max_duration=args.max_duration
    )
    
    stats = preparator.prepare_batch(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        metadata_file=args.metadata
    )
    
    print("\n" + "=" * 70)
    print("📊 Preparation Summary")
    print("=" * 70)
    print(f"Total files: {stats['total']}")
    print(f"Valid: {stats['valid']}")
    print(f"Invalid: {stats['invalid']}")
    print(f"Results saved: {stats['results_file']}")
    print("=" * 70)


if __name__ == "__main__":
    main()

