#!/usr/bin/env python3
"""
VAANI Annotation Progress Tracker
Tracks annotation progress and generates status reports.

Usage:
    python pipeline/annotation/track_progress.py
    python pipeline/annotation/track_progress.py --update
"""

import csv
import json
import argparse
from pathlib import Path
from collections import Counter

def load_annotations(filepath):
    """Load annotations from JSON file."""
    if not Path(filepath).exists():
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_queries(filepath):
    """Load queries from CSV file."""
    queries = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        queries = list(reader)
    return queries

def generate_status_csv(queries, annotations, output_file):
    """Generate annotation status CSV."""
    annotated_ids = {ann['id'] for ann in annotations}
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['audio_id', 'query_text', 'status', 'annotator', 'date'])
        writer.writeheader()
        
        for query in queries:
            query_id = query['id']
            status = 'done' if query_id in annotated_ids else 'pending'
            
            # Find annotation details
            annotator = ''
            date = ''
            if status == 'done':
                ann = next((a for a in annotations if a['id'] == query_id), None)
                if ann and 'metadata' in ann:
                    annotator = ann['metadata'].get('annotator', '')
                    date = ann['metadata'].get('annotation_date', '')
            
            writer.writerow({
                'audio_id': query_id,
                'query_text': query['text'],
                'status': status,
                'annotator': annotator,
                'date': date
            })

def print_progress_report(queries, annotations):
    """Print detailed progress report."""
    total = len(queries)
    annotated = len(annotations)
    pending = total - annotated
    progress = (annotated / total * 100) if total > 0 else 0
    
    print(f"\n{'='*60}")
    print("📊 ANNOTATION PROGRESS REPORT")
    print(f"{'='*60}\n")
    
    print(f"Total queries: {total}")
    print(f"Annotated: {annotated} ({progress:.1f}%)")
    print(f"Pending: {pending}")
    
    # Progress bar
    bar_length = 40
    filled = int(bar_length * annotated / total) if total > 0 else 0
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"\n[{bar}] {progress:.1f}%")
    
    # Intent distribution
    if annotations:
        print(f"\n📈 Intent Distribution:")
        intent_counts = Counter(ann['intent'] for ann in annotations)
        for intent, count in intent_counts.most_common():
            print(f"   {intent}: {count}")
    
    # Annotator statistics
    if annotations:
        print(f"\n👥 Annotator Statistics:")
        annotator_counts = Counter(
            ann['metadata'].get('annotator', 'unknown') 
            for ann in annotations if 'metadata' in ann
        )
        for annotator, count in annotator_counts.most_common():
            print(f"   {annotator}: {count} annotations")
    
    # Quality scores
    if annotations:
        quality_scores = [
            ann['metadata'].get('quality_score', 0)
            for ann in annotations if 'metadata' in ann
        ]
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            print(f"\n⭐ Average Quality Score: {avg_quality:.2f}/5.0")

def main():
    parser = argparse.ArgumentParser(description="Track VAANI annotation progress")
    parser.add_argument("--queries", default="data/queries/queries_day1.csv",
                        help="Path to queries CSV")
    parser.add_argument("--annotations", default="data/annotations/annotations_day2.json",
                        help="Path to annotations JSON")
    parser.add_argument("--output", default="data/annotations/annotation_status.csv",
                        help="Output status CSV")
    parser.add_argument("--update", action="store_true",
                        help="Update status CSV file")
    
    args = parser.parse_args()
    
    # Load data
    queries = load_queries(args.queries)
    annotations = load_annotations(args.annotations)
    
    # Print report
    print_progress_report(queries, annotations)
    
    # Update status CSV if requested
    if args.update:
        generate_status_csv(queries, annotations, args.output)
        print(f"\n✅ Status CSV updated: {args.output}")

if __name__ == "__main__":
    main()

