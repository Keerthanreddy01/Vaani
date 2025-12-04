"""
Expanded entity extractor training script.

Trains spaCy NER model on annotated data.
"""

import argparse
import random
import sys
from pathlib import Path

try:
    import spacy
    from spacy.training import Example
    from spacy.util import minibatch, compounding
except ImportError:
    spacy = None

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.logger import get_logger
from utils.helpers import load_json, ensure_dir

logger = get_logger(__name__)


class EntityTrainer:
    """Train spaCy NER model."""
    
    def __init__(self, base_model="en_core_web_sm", output_dir="models/nlu/entity_extractor"):
        """
        Initialize entity trainer.
        
        Args:
            base_model: Base spaCy model
            output_dir: Output directory for trained model
        """
        if spacy is None:
            raise ImportError("spaCy is required. Install with: pip install spacy")
        
        self.base_model = base_model
        self.output_dir = Path(output_dir)
        ensure_dir(self.output_dir)
        
        logger.info(f"EntityTrainer initialized with base model: {base_model}")
    
    def load_training_data(self, annotations_file):
        """
        Load training data from annotations.
        
        Args:
            annotations_file: Path to annotations JSON
            
        Returns:
            List of training examples in spaCy format
        """
        annotations = load_json(annotations_file)
        
        training_data = []
        
        for ann in annotations:
            text = ann.get("transcription", "")
            entities = ann.get("entities", [])
            
            if not text or not entities:
                continue
            
            # Convert to spaCy format
            ent_list = []
            for ent in entities:
                start = ent.get("start", 0)
                end = ent.get("end", 0)
                label = ent.get("type", ent.get("label", ""))
                
                if start < end and label:
                    ent_list.append((start, end, label))
            
            if ent_list:
                training_data.append((text, {"entities": ent_list}))
        
        logger.info(f"Loaded {len(training_data)} training examples")
        return training_data
    
    def train(self, training_data, n_iter=30, dropout=0.5):
        """
        Train NER model.
        
        Args:
            training_data: Training data in spaCy format
            n_iter: Number of training iterations
            dropout: Dropout rate
            
        Returns:
            Trained model
        """
        # Load base model
        try:
            nlp = spacy.load(self.base_model)
            logger.info(f"Loaded base model: {self.base_model}")
        except:
            logger.warning(f"Could not load {self.base_model}, creating blank model")
            nlp = spacy.blank("en")
        
        # Get or create NER component
        if "ner" not in nlp.pipe_names:
            ner = nlp.add_pipe("ner")
        else:
            ner = nlp.get_pipe("ner")
        
        # Add entity labels
        for _, annotations in training_data:
            for ent in annotations.get("entities"):
                ner.add_label(ent[2])
        
        # Disable other pipes during training
        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
        
        with nlp.disable_pipes(*other_pipes):
            # Initialize optimizer
            optimizer = nlp.begin_training()
            
            logger.info(f"Starting training for {n_iter} iterations...")
            
            for iteration in range(n_iter):
                random.shuffle(training_data)
                losses = {}
                
                # Batch training
                batches = minibatch(training_data, size=compounding(4.0, 32.0, 1.001))
                
                for batch in batches:
                    examples = []
                    for text, annotations in batch:
                        doc = nlp.make_doc(text)
                        example = Example.from_dict(doc, annotations)
                        examples.append(example)
                    
                    nlp.update(examples, drop=dropout, losses=losses, sgd=optimizer)
                
                if (iteration + 1) % 5 == 0:
                    logger.info(f"Iteration {iteration + 1}/{n_iter}, Loss: {losses.get('ner', 0):.4f}")
        
        logger.info("Training complete!")
        return nlp
    
    def evaluate(self, nlp, test_data):
        """
        Evaluate NER model.
        
        Args:
            nlp: Trained spaCy model
            test_data: Test data
            
        Returns:
            Evaluation metrics
        """
        from spacy.scorer import Scorer
        
        examples = []
        for text, annotations in test_data:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            examples.append(example)
        
        scorer = Scorer()
        scores = scorer.score(examples)
        
        logger.info(f"Evaluation - Precision: {scores['ents_p']:.4f}, "
                   f"Recall: {scores['ents_r']:.4f}, F1: {scores['ents_f']:.4f}")
        
        return scores
    
    def save_model(self, nlp):
        """Save trained model."""
        nlp.to_disk(self.output_dir)
        logger.info(f"Model saved to {self.output_dir}")


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Train entity extractor")
    parser.add_argument("--annotations", type=str, required=True,
                       help="Path to annotations JSON file")
    parser.add_argument("--base-model", type=str, default="en_core_web_sm",
                       help="Base spaCy model")
    parser.add_argument("--output-dir", type=str, default="models/nlu/entity_extractor",
                       help="Output directory")
    parser.add_argument("--iterations", type=int, default=30,
                       help="Number of training iterations")
    parser.add_argument("--dropout", type=float, default=0.5,
                       help="Dropout rate")
    parser.add_argument("--test-split", type=float, default=0.2,
                       help="Test set ratio")
    
    args = parser.parse_args()
    
    trainer = EntityTrainer(
        base_model=args.base_model,
        output_dir=args.output_dir
    )
    
    # Load data
    training_data = trainer.load_training_data(args.annotations)
    
    # Split train/test
    split_idx = int(len(training_data) * (1 - args.test_split))
    train_data = training_data[:split_idx]
    test_data = training_data[split_idx:]
    
    logger.info(f"Train: {len(train_data)}, Test: {len(test_data)}")
    
    # Train
    nlp = trainer.train(train_data, n_iter=args.iterations, dropout=args.dropout)
    
    # Evaluate
    if test_data:
        scores = trainer.evaluate(nlp, test_data)
    
    # Save
    trainer.save_model(nlp)
    
    print("\n" + "=" * 70)
    print("✅ Training Complete!")
    print("=" * 70)
    print(f"Model saved to: {args.output_dir}")
    if test_data:
        print(f"Test F1 Score: {scores['ents_f']:.4f}")
    print("=" * 70)


if __name__ == "__main__":
    main()

