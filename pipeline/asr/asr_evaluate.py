#!/usr/bin/env python3
"""
VAANI ASR Evaluation
Compute Word Error Rate (WER) and Character Error Rate (CER) for ASR outputs.

Usage:
    python pipeline/asr/asr_evaluate.py --predictions data/transcripts/asr_results.csv --ground-truth data/annotations/annotations_day2.json
"""

import csv
import json
import argparse
from pathlib import Path
import re


def normalize_text(text):
    """Normalize text for comparison."""
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text


def calculate_wer(reference, hypothesis):
    """
    Calculate Word Error Rate (WER).
    
    WER = (S + D + I) / N
    where S = substitutions, D = deletions, I = insertions, N = words in reference
    """
    ref_words = normalize_text(reference).split()
    hyp_words = normalize_text(hypothesis).split()
    
    # Dynamic programming for edit distance
    d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    
    for i in range(len(ref_words) + 1):
        d[i][0] = i
    for j in range(len(hyp_words) + 1):
        d[0][j] = j
    
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i-1] == hyp_words[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                substitution = d[i-1][j-1] + 1
                insertion = d[i][j-1] + 1
                deletion = d[i-1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)
    
    wer = d[len(ref_words)][len(hyp_words)] / len(ref_words) if ref_words else 0
    return wer


def calculate_cer(reference, hypothesis):
    """
    Calculate Character Error Rate (CER).
    """
    ref_chars = list(normalize_text(reference).replace(' ', ''))
    hyp_chars = list(normalize_text(hypothesis).replace(' ', ''))
    
    # Dynamic programming for edit distance
    d = [[0] * (len(hyp_chars) + 1) for _ in range(len(ref_chars) + 1)]
    
    for i in range(len(ref_chars) + 1):
        d[i][0] = i
    for j in range(len(hyp_chars) + 1):
        d[0][j] = j
    
    for i in range(1, len(ref_chars) + 1):
        for j in range(1, len(hyp_chars) + 1):
            if ref_chars[i-1] == hyp_chars[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                substitution = d[i-1][j-1] + 1
                insertion = d[i][j-1] + 1
                deletion = d[i-1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)
    
    cer = d[len(ref_chars)][len(hyp_chars)] / len(ref_chars) if ref_chars else 0
    return cer


def load_ground_truth(filepath):
    """Load ground truth annotations."""
    with open(filepath, 'r', encoding='utf-8') as f:
        annotations = json.load(f)
    
    # Create mapping from audio_file to transcription
    ground_truth = {}
    for ann in annotations:
        audio_file = ann.get('audio_file', '')
        transcription = ann.get('transcription', '')
        ground_truth[audio_file] = transcription
    
    return ground_truth


def load_predictions(filepath):
    """Load ASR predictions."""
    predictions = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            audio_file = row['audio_file']
            transcription = row['transcription']
            predictions[audio_file] = transcription
    
    return predictions


def evaluate_asr(ground_truth, predictions, output_file=None):
    """
    Evaluate ASR performance.
    
    Args:
        ground_truth: Dict mapping audio_file to reference transcription
        predictions: Dict mapping audio_file to hypothesis transcription
        output_file: Optional file to save detailed results
    """
    results = []
    wer_scores = []
    cer_scores = []
    
    # Find common audio files
    common_files = set(ground_truth.keys()) & set(predictions.keys())
    
    if not common_files:
        print("❌ No common audio files found between ground truth and predictions")
        return
    
    print(f"📊 Evaluating {len(common_files)} audio files\n")
    
    for audio_file in sorted(common_files):
        reference = ground_truth[audio_file]
        hypothesis = predictions[audio_file]
        
        wer = calculate_wer(reference, hypothesis)
        cer = calculate_cer(reference, hypothesis)
        
        wer_scores.append(wer)
        cer_scores.append(cer)
        
        results.append({
            'audio_file': audio_file,
            'reference': reference,
            'hypothesis': hypothesis,
            'wer': wer,
            'cer': cer
        })
    
    # Calculate average metrics
    avg_wer = sum(wer_scores) / len(wer_scores) if wer_scores else 0
    avg_cer = sum(cer_scores) / len(cer_scores) if cer_scores else 0
    
    # Print report
    print(f"{'='*60}")
    print("📈 ASR EVALUATION RESULTS")
    print(f"{'='*60}\n")
    
    print(f"Total samples: {len(common_files)}")
    print(f"Average WER: {avg_wer:.2%}")
    print(f"Average CER: {avg_cer:.2%}")
    
    # Show best and worst examples
    results_sorted = sorted(results, key=lambda x: x['wer'])
    
    print(f"\n✅ Best 3 Examples (Lowest WER):")
    for r in results_sorted[:3]:
        print(f"\n   File: {r['audio_file']}")
        print(f"   REF: {r['reference']}")
        print(f"   HYP: {r['hypothesis']}")
        print(f"   WER: {r['wer']:.2%}, CER: {r['cer']:.2%}")
    
    print(f"\n❌ Worst 3 Examples (Highest WER):")
    for r in results_sorted[-3:]:
        print(f"\n   File: {r['audio_file']}")
        print(f"   REF: {r['reference']}")
        print(f"   HYP: {r['hypothesis']}")
        print(f"   WER: {r['wer']:.2%}, CER: {r['cer']:.2%}")
    
    # Save detailed results
    if output_file:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['audio_file', 'reference', 'hypothesis', 'wer', 'cer'])
            writer.writeheader()
            writer.writerows(results)
        print(f"\n💾 Detailed results saved to: {output_file}")
    
    return {
        'avg_wer': avg_wer,
        'avg_cer': avg_cer,
        'num_samples': len(common_files)
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate VAANI ASR performance")
    parser.add_argument("--predictions", required=True,
                        help="CSV file with ASR predictions")
    parser.add_argument("--ground-truth", required=True,
                        help="JSON file with ground truth annotations")
    parser.add_argument("--output", default="data/transcripts/asr_evaluation.csv",
                        help="Output file for detailed results")
    
    args = parser.parse_args()
    
    # Load data
    ground_truth = load_ground_truth(args.ground_truth)
    predictions = load_predictions(args.predictions)
    
    # Evaluate
    evaluate_asr(ground_truth, predictions, args.output)


if __name__ == "__main__":
    main()

