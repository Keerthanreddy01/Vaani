"""
Batch audio collection script for VAANI.

Shows user queries one by one, records audio, saves with metadata.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pipeline.data.record_audio import AudioRecorder, generate_filename
from utils.logger import get_logger
from utils.helpers import load_csv, save_json, ensure_dir

logger = get_logger(__name__)


class BatchCollector:
    """Batch audio collection manager."""
    
    def __init__(self, queries_file, output_dir, speaker_id, sample_rate=16000):
        """
        Initialize batch collector.
        
        Args:
            queries_file: Path to CSV file with queries
            output_dir: Directory to save recordings
            speaker_id: Unique speaker identifier
            sample_rate: Audio sample rate
        """
        self.queries_file = queries_file
        self.output_dir = Path(output_dir)
        self.speaker_id = speaker_id
        self.sample_rate = sample_rate
        
        # Load queries
        self.queries = load_csv(queries_file)
        logger.info(f"Loaded {len(self.queries)} queries from {queries_file}")
        
        # Create output directory
        ensure_dir(self.output_dir)
        
        # Initialize recorder
        self.recorder = AudioRecorder(sample_rate=sample_rate)
        
        # Metadata storage
        self.metadata = []
        self.metadata_file = self.output_dir / "collection_metadata.json"
    
    def collect(self, start_index=0, num_samples=None, duration=5):
        """
        Collect audio samples.
        
        Args:
            start_index: Starting query index
            num_samples: Number of samples to collect (None = all)
            duration: Recording duration per sample
        """
        if num_samples is None:
            end_index = len(self.queries)
        else:
            end_index = min(start_index + num_samples, len(self.queries))
        
        print("\n" + "=" * 70)
        print("🎙️ VAANI Batch Audio Collection")
        print("=" * 70)
        print(f"Speaker ID: {self.speaker_id}")
        print(f"Samples to collect: {end_index - start_index}")
        print(f"Recording duration: {duration} seconds")
        print(f"Output directory: {self.output_dir}")
        print("=" * 70)
        print("\nInstructions:")
        print("  1. Read the prompt aloud naturally")
        print("  2. Recording starts automatically")
        print("  3. Press Enter to continue or 's' to skip")
        print("  4. Press 'q' to quit")
        print("=" * 70)
        
        collected = 0
        skipped = 0
        
        try:
            for i in range(start_index, end_index):
                query_data = self.queries[i]
                query_text = query_data.get('query', query_data.get('text', ''))
                query_id = query_data.get('id', f"Q{i:04d}")
                intent = query_data.get('intent', 'UNKNOWN')
                
                print(f"\n\n{'='*70}")
                print(f"Sample {i - start_index + 1}/{end_index - start_index}")
                print(f"Query ID: {query_id}")
                print(f"Intent: {intent}")
                print(f"{'='*70}")
                
                # Show prompt
                print(f"\n📝 Please say:")
                print(f"   \"{query_text}\"")
                print()
                
                # Wait for user
                user_input = input("Press Enter to record (or 's' to skip, 'q' to quit): ").strip().lower()
                
                if user_input == 'q':
                    print("\n⚠️ Collection stopped by user")
                    break
                elif user_input == 's':
                    print("⏭️ Skipped")
                    skipped += 1
                    continue
                
                # Generate filename
                filename = f"{self.speaker_id}_{query_id}_{generate_filename()}"
                output_path = self.output_dir / filename
                
                # Record
                result = self.recorder.record(duration, output_path, prompt=None)
                
                if result:
                    # Save metadata
                    metadata_entry = {
                        "audio_file": str(output_path),
                        "query_id": query_id,
                        "query_text": query_text,
                        "intent": intent,
                        "speaker_id": self.speaker_id,
                        "duration": duration,
                        "sample_rate": self.sample_rate,
                        "timestamp": datetime.now().isoformat(),
                        "index": i
                    }
                    self.metadata.append(metadata_entry)
                    collected += 1
                    
                    # Save metadata incrementally
                    save_json(self.metadata, self.metadata_file)
                    
                    print(f"✅ Saved: {filename}")
                else:
                    skipped += 1
        
        except KeyboardInterrupt:
            print("\n\n⚠️ Collection interrupted by user")
        
        finally:
            self.recorder.close()
            
            # Final summary
            print("\n" + "=" * 70)
            print("📊 Collection Summary")
            print("=" * 70)
            print(f"Collected: {collected}")
            print(f"Skipped: {skipped}")
            print(f"Total: {collected + skipped}")
            print(f"Metadata saved: {self.metadata_file}")
            print("=" * 70)
            
            logger.info(f"Collection complete: {collected} samples collected, {skipped} skipped")


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Batch audio collection for VAANI")
    parser.add_argument("--queries", type=str, default="data/queries/queries_day1.csv",
                       help="Path to queries CSV file")
    parser.add_argument("--output-dir", type=str, default="data/audio_raw/batch_collection",
                       help="Output directory for recordings")
    parser.add_argument("--speaker-id", type=str, required=True,
                       help="Unique speaker identifier (e.g., SPK001)")
    parser.add_argument("--start", type=int, default=0,
                       help="Starting query index")
    parser.add_argument("--num-samples", type=int, default=None,
                       help="Number of samples to collect (default: all)")
    parser.add_argument("--duration", type=int, default=5,
                       help="Recording duration per sample in seconds")
    parser.add_argument("--sample-rate", type=int, default=16000,
                       help="Audio sample rate in Hz")
    
    args = parser.parse_args()
    
    # Create collector
    collector = BatchCollector(
        queries_file=args.queries,
        output_dir=args.output_dir,
        speaker_id=args.speaker_id,
        sample_rate=args.sample_rate
    )
    
    # Start collection
    collector.collect(
        start_index=args.start,
        num_samples=args.num_samples,
        duration=args.duration
    )


if __name__ == "__main__":
    main()

