#!/usr/bin/env python3
"""
VAANI NLU Evaluation
Comprehensive evaluation of intent classification and entity extraction.

Usage:
    python pipeline/nlu/nlu_evaluate.py
"""

import csv
import json
import argparse
import pickle
from pathlib import Path
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import spacy


def load_intent_model(model_path):
    """Load intent classification model."""
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
    return model_data


def load_entity_model(model_path):
    """Load entity extraction model."""
    return spacy.load(model_path)


def evaluate_intent_classification(model_data, test_texts, test_intents):
    """Evaluate intent classification."""
    print("🎯 Evaluating Intent Classification\n")
    
    vectorizer = model_data['vectorizer']
    classifier = model_data['classifier']
    label_decoder = model_data['label_decoder']
    label_encoder = model_data['label_encoder']
    
    # Vectorize test texts
    X_test = vectorizer.transform(test_texts)
    
    # Encode test intents
    y_test = np.array([label_encoder[intent] for intent in test_intents])
    
    # Predict
    y_pred = classifier.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    
    # Get intent names
    intent_names = [label_decoder[i] for i in range(len(label_decoder))]
    
    # Classification report
    report = classification_report(y_test, y_pred, target_names=intent_names, output_dict=True)
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    
    print(f"Accuracy: {accuracy:.2%}\n")
    print("Per-Intent Metrics:")
    for intent in intent_names:
        metrics = report[intent]
        print(f"  {intent}:")
        print(f"    Precision: {metrics['precision']:.2%}")
        print(f"    Recall: {metrics['recall']:.2%}")
        print(f"    F1-Score: {metrics['f1-score']:.2%}")
    
    return {
        'accuracy': accuracy,
        'report': report,
        'confusion_matrix': cm,
        'intent_names': intent_names
    }


def evaluate_entity_extraction(nlp, test_data):
    """Evaluate entity extraction."""
    print("\n🏷️  Evaluating Entity Extraction\n")
    
    total_entities = 0
    correct_entities = 0
    predicted_entities = 0
    
    entity_stats = {}
    
    for text, annotations in test_data:
        # Get ground truth entities
        true_entities = set()
        for start, end, label in annotations.get("entities", []):
            true_entities.add((start, end, label))
            entity_stats.setdefault(label, {'true': 0, 'pred': 0, 'correct': 0})
            entity_stats[label]['true'] += 1
        
        # Get predicted entities
        doc = nlp(text)
        pred_entities = set()
        for ent in doc.ents:
            pred_entities.add((ent.start_char, ent.end_char, ent.label_))
            entity_stats.setdefault(ent.label_, {'true': 0, 'pred': 0, 'correct': 0})
            entity_stats[ent.label_]['pred'] += 1
        
        # Calculate matches
        matches = true_entities & pred_entities
        for match in matches:
            entity_stats[match[2]]['correct'] += 1
        
        total_entities += len(true_entities)
        predicted_entities += len(pred_entities)
        correct_entities += len(matches)
    
    # Overall metrics
    precision = correct_entities / predicted_entities if predicted_entities > 0 else 0
    recall = correct_entities / total_entities if total_entities > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"Overall Metrics:")
    print(f"  Precision: {precision:.2%}")
    print(f"  Recall: {recall:.2%}")
    print(f"  F1-Score: {f1:.2%}")
    
    # Per-entity metrics
    print(f"\nPer-Entity Metrics:")
    for entity_type, stats in sorted(entity_stats.items()):
        ent_precision = stats['correct'] / stats['pred'] if stats['pred'] > 0 else 0
        ent_recall = stats['correct'] / stats['true'] if stats['true'] > 0 else 0
        ent_f1 = 2 * ent_precision * ent_recall / (ent_precision + ent_recall) if (ent_precision + ent_recall) > 0 else 0
        
        print(f"  {entity_type}:")
        print(f"    Precision: {ent_precision:.2%}")
        print(f"    Recall: {ent_recall:.2%}")
        print(f"    F1-Score: {ent_f1:.2%}")
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'entity_stats': entity_stats
    }


def plot_confusion_matrix(cm, intent_names, output_file):
    """Plot confusion matrix."""
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=intent_names, yticklabels=intent_names)
    plt.title('Intent Classification Confusion Matrix')
    plt.ylabel('True Intent')
    plt.xlabel('Predicted Intent')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n📊 Confusion matrix saved to: {output_file}")


def save_metrics(intent_results, entity_results, output_file):
    """Save evaluation metrics to JSON."""
    metrics = {
        'intent_classification': {
            'accuracy': intent_results['accuracy'],
            'per_intent': {
                intent: {
                    'precision': intent_results['report'][intent]['precision'],
                    'recall': intent_results['report'][intent]['recall'],
                    'f1_score': intent_results['report'][intent]['f1-score']
                }
                for intent in intent_results['intent_names']
            }
        },
        'entity_extraction': {
            'overall': {
                'precision': entity_results['precision'],
                'recall': entity_results['recall'],
                'f1_score': entity_results['f1']
            },
            'per_entity': entity_results['entity_stats']
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"💾 Metrics saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate VAANI NLU models")
    parser.add_argument("--intent-model", default="models/nlu/intent_classifier.pkl",
                        help="Intent classification model")
    parser.add_argument("--entity-model", default="models/nlu/entity_extractor",
                        help="Entity extraction model")
    parser.add_argument("--test-data", default="data/queries/queries_day1.csv",
                        help="Test data CSV")
    parser.add_argument("--annotations", default="data/annotations/annotations_day2.json",
                        help="Annotations for entity evaluation")
    parser.add_argument("--output-dir", default="models/nlu",
                        help="Output directory for results")
    
    args = parser.parse_args()
    
    print("="*60)
    print("📊 VAANI NLU EVALUATION")
    print("="*60 + "\n")
    
    # Load test data for intent classification
    test_texts = []
    test_intents = []
    with open(args.test_data, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_texts.append(row['text'])
            test_intents.append(row['intent'])
    
    # Evaluate intent classification
    intent_model = load_intent_model(args.intent_model)
    intent_results = evaluate_intent_classification(intent_model, test_texts, test_intents)
    
    # Plot confusion matrix
    cm_file = Path(args.output_dir) / "nlu_confusion_matrix.png"
    plot_confusion_matrix(intent_results['confusion_matrix'], intent_results['intent_names'], cm_file)
    
    # Evaluate entity extraction (if annotations available)
    if Path(args.annotations).exists() and Path(args.entity_model).exists():
        entity_nlp = load_entity_model(args.entity_model)
        
        # Load annotations
        with open(args.annotations, 'r', encoding='utf-8') as f:
            annotations = json.load(f)
        
        # Prepare test data
        test_data = []
        for ann in annotations:
            text = ann.get('transcription', '')
            entities = [(e['start'], e['end'], e['type']) for e in ann.get('entities', [])]
            test_data.append((text, {"entities": entities}))
        
        entity_results = evaluate_entity_extraction(entity_nlp, test_data)
        
        # Save metrics
        metrics_file = Path(args.output_dir) / "nlu_metrics.json"
        save_metrics(intent_results, entity_results, metrics_file)
    
    print("\n✅ Evaluation complete!")


if __name__ == "__main__":
    main()

