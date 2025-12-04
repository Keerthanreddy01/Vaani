
"""
Unified NLU prediction module.

Combines intent classification and entity extraction.
"""

import argparse
import pickle
import sys
from pathlib import Path

try:
    import spacy
except ImportError:
    spacy = None

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.logger import get_logger

logger = get_logger(__name__)


class NLUPredictor:
    """Unified NLU predictor for intent and entities."""

    def __init__(self, model_dir, language='en'):
        """
        Initialize NLU predictor.

        Args:
            model_dir: Directory containing NLU models.
            language: Language code for the models to load.
        """
        self.model_dir = Path(model_dir)
        self.language = language

        intent_model_path = self.model_dir / f"intent_classifier_{self.language}.pkl"
        entity_model_path = self.model_dir / f"entity_extractor_{self.language}"

        # Load intent classifier
        logger.info(f"Loading intent classifier from {intent_model_path}")
        with open(intent_model_path, 'rb') as f:
            intent_data = pickle.load(f)
            self.intent_vectorizer = intent_data["vectorizer"]
            self.intent_classifier = intent_data["classifier"]

        # Load entity extractor (optional)
        self.entity_nlp = None
        if entity_model_path.exists():
            try:
                if spacy is None:
                    logger.warning("spaCy not available. Entity extraction disabled.")
                else:
                    logger.info(f"Loading entity extractor from {entity_model_path}")
                    self.entity_nlp = spacy.load(entity_model_path)
            except Exception as e:
                logger.warning(f"Could not load entity model: {e}. Entity extraction disabled.")

        logger.info("NLU Predictor initialized successfully")

    def predict_intent(self, text):
        text_vec = self.intent_vectorizer.transform([text])
        intent = self.intent_classifier.predict(text_vec)[0]
        confidence = 1.0  # Default confidence
        if hasattr(self.intent_classifier, "predict_proba"):
            probs = self.intent_classifier.predict_proba(text_vec)[0]
            confidence = float(max(probs))
        return {"intent": intent, "confidence": confidence}

    def predict_entities(self, text):
        if not self.entity_nlp:
            return []
        doc = self.entity_nlp(text)
        return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    def predict_all(self, text):
        intent_result = self.predict_intent(text)
        entities_list = self.predict_entities(text)

        entity_dict = {}
        for ent in entities_list:
            entity_dict[ent['label'].lower()] = ent['text']

        return {
            "text": text,
            "intent": intent_result["intent"],
            "confidence": intent_result["confidence"],
            "entities": entity_dict
        }

def main():
    parser = argparse.ArgumentParser(description="NLU Prediction")
    parser.add_argument("--text", type=str, help="Text to analyze")
    parser.add_argument("--model-dir", type=str, default="models/nlu", help="Directory of NLU models")
    parser.add_argument("--language", type=str, default="en", help="Language of the model to use")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    args = parser.parse_args()

    predictor = NLUPredictor(model_dir=args.model_dir, language=args.language)

    if args.interactive:
        print("\nInteractive NLU mode. Type 'quit' to exit.")
        while True:
            text = input("\n> ").strip()
            if text.lower() in ['quit', 'exit']:
                break
            if not text:
                continue
            result = predictor.predict_all(text)
            print(result)
    elif args.text:
        result = predictor.predict_all(args.text)
        print(result)
    else:
        print("Please provide --text or use --interactive mode.")

if __name__ == "__main__":
    main()
