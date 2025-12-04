"""
Whisper evaluation dashboard.

Interactive console UI for evaluating Whisper ASR performance.
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import whisper
except ImportError:
    whisper = None

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pipeline.asr.asr_evaluate import calculate_wer, calculate_cer
from utils.logger import get_logger
from utils.helpers import load_json

logger = get_logger(__name__)


class WhisperDashboard:
    """Whisper evaluation dashboard."""
    
    def __init__(self, model_path="base"):
        """
        Initialize dashboard.
        
        Args:
            model_path: Path to Whisper model or model name
        """
        if whisper is None:
            raise ImportError("openai-whisper is required. Install with: pip install openai-whisper")
        
        logger.info(f"Loading Whisper model: {model_path}")
        self.model = whisper.load_model(model_path)
        logger.info("Model loaded successfully")
    
    def transcribe(self, audio_path):
        """
        Transcribe audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcription text
        """
        result = self.model.transcribe(str(audio_path), language="en")
        return result["text"].strip()
    
    def evaluate_dataset(self, test_manifest, ground_truth_file=None):
        """
        Evaluate on test dataset.
        
        Args:
            test_manifest: Path to test manifest JSONL
            ground_truth_file: Optional ground truth annotations
            
        Returns:
            Evaluation results
        """
        # Load test data
        test_data = []
        with open(test_manifest, 'r', encoding='utf-8') as f:
            for line in f:
                test_data.append(json.loads(line))
        
        logger.info(f"Evaluating on {len(test_data)} samples")
        
        results = []
        total_wer = 0.0
        total_cer = 0.0
        
        for i, item in enumerate(test_data):
            audio_path = item["audio_filepath"]
            reference = item["text"]
            
            # Transcribe
            try:
                hypothesis = self.transcribe(audio_path)
                
                # Calculate metrics
                wer = calculate_wer(reference, hypothesis)
                cer = calculate_cer(reference, hypothesis)
                
                total_wer += wer
                total_cer += cer
                
                result = {
                    "audio_file": audio_path,
                    "reference": reference,
                    "hypothesis": hypothesis,
                    "wer": wer,
                    "cer": cer
                }
                
                results.append(result)
                
                # Progress
                if (i + 1) % 10 == 0:
                    print(f"Processed {i + 1}/{len(test_data)} samples...")
            
            except Exception as e:
                logger.error(f"Error processing {audio_path}: {e}")
                continue
        
        # Calculate averages
        avg_wer = total_wer / len(results) if results else 0.0
        avg_cer = total_cer / len(results) if results else 0.0
        
        # Find best and worst
        results_sorted_wer = sorted(results, key=lambda x: x["wer"])
        best_samples = results_sorted_wer[:5]
        worst_samples = results_sorted_wer[-5:]
        
        evaluation = {
            "total_samples": len(results),
            "avg_wer": avg_wer,
            "avg_cer": avg_cer,
            "best_samples": best_samples,
            "worst_samples": worst_samples,
            "all_results": results
        }
        
        return evaluation
    
    def display_results(self, evaluation):
        """Display evaluation results."""
        print("\n" + "=" * 70)
        print("📊 Whisper Evaluation Results")
        print("=" * 70)
        print(f"Total samples: {evaluation['total_samples']}")
        print(f"Average WER: {evaluation['avg_wer']:.2%}")
        print(f"Average CER: {evaluation['avg_cer']:.2%}")
        
        print("\n" + "-" * 70)
        print("✅ Best 5 Samples (Lowest WER)")
        print("-" * 70)
        for i, sample in enumerate(evaluation['best_samples'], 1):
            print(f"\n{i}. WER: {sample['wer']:.2%}, CER: {sample['cer']:.2%}")
            print(f"   REF: {sample['reference']}")
            print(f"   HYP: {sample['hypothesis']}")
        
        print("\n" + "-" * 70)
        print("❌ Worst 5 Samples (Highest WER)")
        print("-" * 70)
        for i, sample in enumerate(evaluation['worst_samples'], 1):
            print(f"\n{i}. WER: {sample['wer']:.2%}, CER: {sample['cer']:.2%}")
            print(f"   REF: {sample['reference']}")
            print(f"   HYP: {sample['hypothesis']}")
        
        print("\n" + "=" * 70)


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Whisper Evaluation Dashboard")
    parser.add_argument("--model", type=str, default="base",
                       help="Whisper model name or path")
    parser.add_argument("--test-manifest", type=str, required=True,
                       help="Path to test manifest JSONL")
    parser.add_argument("--output", type=str,
                       help="Output JSON file for results")
    
    args = parser.parse_args()
    
    dashboard = WhisperDashboard(model_path=args.model)
    
    evaluation = dashboard.evaluate_dataset(args.test_manifest)
    
    dashboard.display_results(evaluation)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(evaluation, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to: {args.output}")


if __name__ == "__main__":
    main()

