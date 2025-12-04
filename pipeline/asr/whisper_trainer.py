"""
Whisper ASR model fine-tuning trainer.

Trains Whisper model on custom dataset for Indian English.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    import torch
    from transformers import WhisperProcessor, WhisperForConditionalGeneration
    from transformers import Seq2SeqTrainingArguments, Seq2SeqTrainer
    from datasets import Dataset, Audio
except ImportError:
    torch = None
    WhisperProcessor = None

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.logger import get_logger
from utils.helpers import ensure_dir, load_json

logger = get_logger(__name__)


class WhisperTrainer:
    """Whisper model trainer."""
    
    def __init__(self, model_name="openai/whisper-base", output_dir="models/asr/whisper_finetuned"):
        """
        Initialize Whisper trainer.
        
        Args:
            model_name: Pretrained model name
            output_dir: Output directory for checkpoints
        """
        if torch is None or WhisperProcessor is None:
            raise ImportError("transformers and torch are required. "
                            "Install with: pip install transformers torch")
        
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        ensure_dir(self.output_dir)
        
        # Load processor and model
        logger.info(f"Loading Whisper model: {model_name}")
        self.processor = WhisperProcessor.from_pretrained(model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_name)
        
        # Set language and task
        self.model.config.forced_decoder_ids = self.processor.get_decoder_prompt_ids(
            language="en", task="transcribe"
        )
        
        logger.info(f"WhisperTrainer initialized: {model_name}")
    
    def load_dataset(self, manifest_file):
        """
        Load dataset from JSONL manifest.
        
        Args:
            manifest_file: Path to JSONL manifest
            
        Returns:
            HuggingFace Dataset
        """
        # Read JSONL
        data = []
        with open(manifest_file, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line))
        
        # Create dataset
        dataset = Dataset.from_list(data)
        
        # Cast audio column
        dataset = dataset.cast_column("audio_filepath", Audio(sampling_rate=16000))
        dataset = dataset.rename_column("audio_filepath", "audio")
        
        logger.info(f"Loaded dataset: {len(dataset)} samples from {manifest_file}")
        return dataset
    
    def preprocess_function(self, examples):
        """Preprocess examples for training."""
        # Extract audio arrays
        audio = [x["array"] for x in examples["audio"]]
        
        # Process audio
        inputs = self.processor(
            audio, sampling_rate=16000, return_tensors="pt", padding=True
        )
        
        # Process text
        labels = self.processor.tokenizer(
            examples["text"], return_tensors="pt", padding=True
        )
        
        inputs["labels"] = labels["input_ids"]
        
        return inputs
    
    def train(self, train_manifest, val_manifest, epochs=3, batch_size=8, 
              learning_rate=1e-5, save_steps=500):
        """
        Train Whisper model.
        
        Args:
            train_manifest: Path to training manifest
            val_manifest: Path to validation manifest
            epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate
            save_steps: Save checkpoint every N steps
            
        Returns:
            Training results
        """
        # Load datasets
        train_dataset = self.load_dataset(train_manifest)
        val_dataset = self.load_dataset(val_manifest)
        
        # Preprocess
        logger.info("Preprocessing datasets...")
        train_dataset = train_dataset.map(
            self.preprocess_function, batched=True, remove_columns=train_dataset.column_names
        )
        val_dataset = val_dataset.map(
            self.preprocess_function, batched=True, remove_columns=val_dataset.column_names
        )
        
        # Training arguments
        training_args = Seq2SeqTrainingArguments(
            output_dir=str(self.output_dir),
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            num_train_epochs=epochs,
            save_steps=save_steps,
            eval_steps=save_steps,
            logging_steps=100,
            evaluation_strategy="steps",
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            fp16=torch.cuda.is_available(),
            report_to=["tensorboard"],
            push_to_hub=False,
        )
        
        # Create trainer
        trainer = Seq2SeqTrainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.processor.feature_extractor,
        )
        
        # Train
        logger.info("Starting training...")
        train_result = trainer.train()
        
        # Save final model
        final_model_dir = self.output_dir / "final"
        trainer.save_model(str(final_model_dir))
        self.processor.save_pretrained(str(final_model_dir))
        
        logger.info(f"Training complete! Model saved to {final_model_dir}")
        
        return train_result


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Train Whisper ASR model")
    parser.add_argument("--train-manifest", type=str, required=True,
                       help="Path to training manifest (JSONL)")
    parser.add_argument("--val-manifest", type=str, required=True,
                       help="Path to validation manifest (JSONL)")
    parser.add_argument("--model-name", type=str, default="openai/whisper-base",
                       help="Pretrained model name")
    parser.add_argument("--output-dir", type=str, default="models/asr/whisper_finetuned",
                       help="Output directory")
    parser.add_argument("--epochs", type=int, default=3,
                       help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=8,
                       help="Batch size")
    parser.add_argument("--learning-rate", type=float, default=1e-5,
                       help="Learning rate")
    parser.add_argument("--save-steps", type=int, default=500,
                       help="Save checkpoint every N steps")
    
    args = parser.parse_args()
    
    trainer = WhisperTrainer(
        model_name=args.model_name,
        output_dir=args.output_dir
    )
    
    result = trainer.train(
        train_manifest=args.train_manifest,
        val_manifest=args.val_manifest,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        save_steps=args.save_steps
    )
    
    print("\n" + "=" * 70)
    print("✅ Training Complete!")
    print("=" * 70)
    print(f"Final model saved to: {args.output_dir}/final")
    print("=" * 70)


if __name__ == "__main__":
    main()

