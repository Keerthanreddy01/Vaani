#!/usr/bin/env python3
"""
VAANI Intent Classification Model
Train and evaluate intent classifier using TF-IDF + SVM baseline.

Usage:
    python pipeline/nlu/intent_classifier.py --train
    python pipeline/nlu/intent_classifier.py --predict "What time is it"
"""

import csv
import pickle
import argparse
import json
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns


class IntentClassifier:
    """Intent classification model."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            lowercase=True,
            stop_words='english'
        )
        self.classifier = SVC(
            kernel='linear',
            C=1.0,
            probability=True,
            random_state=42
        )
        self.label_encoder = {}
        self.label_decoder = {}
    
    def prepare_data(self, texts, intents):
        """Prepare data for training."""
        # Encode labels
        unique_intents = sorted(set(intents))
        self.label_encoder = {intent: idx for idx, intent in enumerate(unique_intents)}
        self.label_decoder = {idx: intent for intent, idx in self.label_encoder.items()}
        
        # Encode labels
        y = np.array([self.label_encoder[intent] for intent in intents])
        
        # Vectorize texts
        X = self.vectorizer.fit_transform(texts)
        
        return X, y
    
    def train(self, texts, intents, test_size=0.2):
        """Train the intent classifier."""
        print("🎯 Training Intent Classifier\n")
        
        # Prepare data
        X, y = self.prepare_data(texts, intents)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"Training samples: {X_train.shape[0]}")
        print(f"Test samples: {X_test.shape[0]}")
        print(f"Number of intents: {len(self.label_encoder)}")
        print(f"Feature dimensions: {X_train.shape[1]}\n")
        
        # Train classifier
        print("Training SVM classifier...")
        self.classifier.fit(X_train, y_train)
        print("✅ Training complete\n")
        
        # Evaluate
        y_pred = self.classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"📊 Test Accuracy: {accuracy:.2%}\n")
        
        # Classification report
        intent_names = [self.label_decoder[i] for i in range(len(self.label_decoder))]
        report = classification_report(y_test, y_pred, target_names=intent_names)
        print("Classification Report:")
        print(report)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        return {
            'accuracy': accuracy,
            'confusion_matrix': cm,
            'intent_names': intent_names,
            'X_test': X_test,
            'y_test': y_test,
            'y_pred': y_pred
        }
    
    def predict(self, text):
        """Predict intent for a single text."""
        X = self.vectorizer.transform([text])
        y_pred = self.classifier.predict(X)[0]
        y_proba = self.classifier.predict_proba(X)[0]
        
        intent = self.label_decoder[y_pred]
        confidence = y_proba[y_pred]
        
        # Get top 3 predictions
        top_indices = np.argsort(y_proba)[-3:][::-1]
        top_predictions = [
            {
                'intent': self.label_decoder[idx],
                'confidence': float(y_proba[idx])
            }
            for idx in top_indices
        ]
        
        return {
            'intent': intent,
            'confidence': float(confidence),
            'top_predictions': top_predictions
        }
    
    def save(self, filepath):
        """Save model to file."""
        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'label_encoder': self.label_encoder,
            'label_decoder': self.label_decoder
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"💾 Model saved to: {filepath}")
    
    def load(self, filepath):
        """Load model from file."""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        self.vectorizer = model_data['vectorizer']
        self.classifier = model_data['classifier']
        self.label_encoder = model_data['label_encoder']
        self.label_decoder = model_data['label_decoder']
        print(f"📂 Model loaded from: {filepath}")


def load_data_from_csv(filepath):
    """Load training data from CSV."""
    texts = []
    intents = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            texts.append(row['text'])
            intents.append(row['intent'])
    
    return texts, intents


def plot_confusion_matrix(cm, intent_names, output_file):
    """Plot and save confusion matrix."""
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
    print(f"📊 Confusion matrix saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="VAANI Intent Classifier")
    parser.add_argument("--train", action="store_true", help="Train the model")
    parser.add_argument("--predict", help="Predict intent for text")
    parser.add_argument("--data", default="data/queries/queries_day1.csv",
                        help="Training data CSV")
    parser.add_argument("--model", default="models/nlu/intent_classifier.pkl",
                        help="Model file path")
    parser.add_argument("--test-size", type=float, default=0.2,
                        help="Test set size")
    
    args = parser.parse_args()
    
    classifier = IntentClassifier()
    
    if args.train:
        # Load data
        print(f"📂 Loading data from: {args.data}\n")
        texts, intents = load_data_from_csv(args.data)
        
        # Train model
        results = classifier.train(texts, intents, args.test_size)
        
        # Save model
        Path(args.model).parent.mkdir(parents=True, exist_ok=True)
        classifier.save(args.model)
        
        # Plot confusion matrix
        cm_file = Path(args.model).parent / "confusion_matrix.png"
        plot_confusion_matrix(results['confusion_matrix'], results['intent_names'], cm_file)
    
    elif args.predict:
        # Load model
        if not Path(args.model).exists():
            print(f"❌ Model not found: {args.model}")
            print("   Train the model first with --train")
            return
        
        classifier.load(args.model)
        
        # Predict
        result = classifier.predict(args.predict)
        print(f"\n📝 Text: {args.predict}")
        print(f"🎯 Intent: {result['intent']}")
        print(f"📊 Confidence: {result['confidence']:.2%}")
        print(f"\n🔝 Top 3 Predictions:")
        for pred in result['top_predictions']:
            print(f"   {pred['intent']}: {pred['confidence']:.2%}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

