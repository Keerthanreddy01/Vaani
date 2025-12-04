#!/usr/bin/env python3
"""
VAANI Entity Extraction Model
Train and evaluate entity extractor using spaCy NER.

Usage:
    python pipeline/nlu/entity_extractor.py --train
    python pipeline/nlu/entity_extractor.py --predict "Set alarm for 7 AM tomorrow"
"""

import json
import argparse
import random
from pathlib import Path
import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding


class EntityExtractor:
    """Entity extraction model using spaCy NER."""
    
    def __init__(self, model_name="en_core_web_sm"):
        """Initialize entity extractor."""
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            print(f"⚠️  Model '{model_name}' not found. Creating blank model.")
            self.nlp = spacy.blank("en")
        
        # Add NER pipeline if not present
        if "ner" not in self.nlp.pipe_names:
            ner = self.nlp.add_pipe("ner")
        else:
            ner = self.nlp.get_pipe("ner")
        
        self.ner = ner
    
    def prepare_training_data(self, annotations):
        """
        Prepare training data from annotations.
        
        Format: [(text, {"entities": [(start, end, label)]}), ...]
        """
        training_data = []
        
        for ann in annotations:
            text = ann.get('transcription', '')
            entities = ann.get('entities', [])
            
            # Convert entities to spaCy format
            ent_list = []
            for ent in entities:
                start = ent.get('start', 0)
                end = ent.get('end', 0)
                label = ent.get('type', 'UNKNOWN')
                ent_list.append((start, end, label))
            
            if text:
                training_data.append((text, {"entities": ent_list}))
        
        return training_data
    
    def train(self, training_data, n_iter=30, drop=0.2):
        """Train the NER model."""
        print("🎯 Training Entity Extractor\n")
        
        # Add labels to NER
        for _, annotations in training_data:
            for ent in annotations.get("entities"):
                self.ner.add_label(ent[2])
        
        print(f"Training samples: {len(training_data)}")
        print(f"Entity labels: {list(self.ner.labels)}")
        print(f"Iterations: {n_iter}\n")
        
        # Get names of other pipes to disable during training
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "ner"]
        
        # Train only NER
        with self.nlp.disable_pipes(*other_pipes):
            optimizer = self.nlp.begin_training()
            
            for iteration in range(n_iter):
                random.shuffle(training_data)
                losses = {}
                
                # Batch training
                batches = minibatch(training_data, size=compounding(4.0, 32.0, 1.001))
                
                for batch in batches:
                    examples = []
                    for text, annotations in batch:
                        doc = self.nlp.make_doc(text)
                        example = Example.from_dict(doc, annotations)
                        examples.append(example)
                    
                    self.nlp.update(examples, drop=drop, losses=losses, sgd=optimizer)
                
                if (iteration + 1) % 5 == 0:
                    print(f"Iteration {iteration + 1}/{n_iter} - Loss: {losses.get('ner', 0):.4f}")
        
        print("\n✅ Training complete")
    
    def extract_entities(self, text):
        """Extract entities from text."""
        doc = self.nlp(text)
        
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })
        
        return entities
    
    def evaluate(self, test_data):
        """Evaluate the NER model."""
        print("\n📊 Evaluating Entity Extractor\n")
        
        total_entities = 0
        correct_entities = 0
        predicted_entities = 0
        
        for text, annotations in test_data:
            # Get ground truth entities
            true_entities = set()
            for start, end, label in annotations.get("entities", []):
                true_entities.add((start, end, label))
            
            # Get predicted entities
            doc = self.nlp(text)
            pred_entities = set()
            for ent in doc.ents:
                pred_entities.add((ent.start_char, ent.end_char, ent.label_))
            
            # Calculate metrics
            total_entities += len(true_entities)
            predicted_entities += len(pred_entities)
            correct_entities += len(true_entities & pred_entities)
        
        # Calculate precision, recall, F1
        precision = correct_entities / predicted_entities if predicted_entities > 0 else 0
        recall = correct_entities / total_entities if total_entities > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"Total entities: {total_entities}")
        print(f"Predicted entities: {predicted_entities}")
        print(f"Correct entities: {correct_entities}")
        print(f"\nPrecision: {precision:.2%}")
        print(f"Recall: {recall:.2%}")
        print(f"F1 Score: {f1:.2%}")
        
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    
    def save(self, output_dir):
        """Save model to directory."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        self.nlp.to_disk(output_path)
        print(f"💾 Model saved to: {output_path}")
    
    def load(self, model_dir):
        """Load model from directory."""
        self.nlp = spacy.load(model_dir)
        self.ner = self.nlp.get_pipe("ner")
        print(f"📂 Model loaded from: {model_dir}")


def load_annotations(filepath):
    """Load annotations from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="VAANI Entity Extractor")
    parser.add_argument("--train", action="store_true", help="Train the model")
    parser.add_argument("--predict", help="Extract entities from text")
    parser.add_argument("--annotations", default="data/annotations/annotations_day2.json",
                        help="Annotations JSON file")
    parser.add_argument("--model", default="models/nlu/entity_extractor",
                        help="Model directory")
    parser.add_argument("--iterations", type=int, default=30,
                        help="Training iterations")
    parser.add_argument("--test-split", type=float, default=0.2,
                        help="Test set proportion")
    
    args = parser.parse_args()
    
    extractor = EntityExtractor()
    
    if args.train:
        # Load annotations
        print(f"📂 Loading annotations from: {args.annotations}\n")
        annotations = load_annotations(args.annotations)
        
        # Prepare training data
        training_data = extractor.prepare_training_data(annotations)
        
        if not training_data:
            print("❌ No training data found. Please annotate data first.")
            return
        
        # Split train/test
        split_idx = int(len(training_data) * (1 - args.test_split))
        train_data = training_data[:split_idx]
        test_data = training_data[split_idx:]
        
        # Train
        extractor.train(train_data, n_iter=args.iterations)
        
        # Evaluate
        if test_data:
            extractor.evaluate(test_data)
        
        # Save
        extractor.save(args.model)
    
    elif args.predict:
        # Load model
        if not Path(args.model).exists():
            print(f"❌ Model not found: {args.model}")
            print("   Train the model first with --train")
            return
        
        extractor.load(args.model)
        
        # Extract entities
        entities = extractor.extract_entities(args.predict)
        
        print(f"\n📝 Text: {args.predict}")
        print(f"🏷️  Entities: {len(entities)}\n")
        
        for ent in entities:
            print(f"   {ent['label']}: '{ent['text']}' ({ent['start']}-{ent['end']})")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

