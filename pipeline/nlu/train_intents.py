
"""
Expanded intent classifier training script.

Trains multiple models and selects the best one for a specific language.
"""

import argparse
import sys
from pathlib import Path
import pickle

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import LinearSVC
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import classification_report, confusion_matrix
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError:
    pass

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.logger import get_logger
from utils.helpers import load_csv, ensure_dir

logger = get_logger(__name__)


class IntentTrainer:
    """Train and compare multiple intent classifiers for a given language."""

    def __init__(self, output_dir="models/nlu"):
        self.output_dir = Path(output_dir)
        ensure_dir(self.output_dir)
        self.models = {
            "tfidf_svm": {
                "vectorizer": TfidfVectorizer(max_features=1000, ngram_range=(1, 2)),
                "classifier": LinearSVC(random_state=42, max_iter=2000)
            },
            "tfidf_logreg": {
                "vectorizer": TfidfVectorizer(max_features=1000, ngram_range=(1, 2)),
                "classifier": LogisticRegression(random_state=42, max_iter=1000)
            },
            "tfidf_rf": {
                "vectorizer": TfidfVectorizer(max_features=1000, ngram_range=(1, 2)),
                "classifier": RandomForestClassifier(n_estimators=100, random_state=42)
            }
        }
        logger.info(f"IntentTrainer initialized with {len(self.models)} models")

    def load_data(self, data_file):
        data = load_csv(data_file)
        texts, labels = [], []
        for row in data:
            text, intent = row.get('query', row.get('text', '')), row.get('intent', '')
            if text and intent:
                texts.append(text)
                labels.append(intent)
        logger.info(f"Loaded {len(texts)} samples from {data_file}")
        return texts, labels

    def train_and_evaluate(self, texts, labels, test_size=0.2):
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=test_size, random_state=42, stratify=labels
        )
        logger.info(f"Training set: {len(X_train)}, Test set: {len(X_test)}")
        results = {}
        for model_name, components in self.models.items():
            logger.info(f"\nTraining {model_name}...")
            vectorizer, classifier = components["vectorizer"], components["classifier"]
            X_train_vec = vectorizer.fit_transform(X_train)
            X_test_vec = vectorizer.transform(X_test)
            classifier.fit(X_train_vec, y_train)
            test_score = classifier.score(X_test_vec, y_test)
            cv_scores = cross_val_score(classifier, X_train_vec, y_train, cv=5)
            results[model_name] = {
                "test_accuracy": test_score, "cv_mean": cv_scores.mean(),
                "vectorizer": vectorizer, "classifier": classifier
            }
            logger.info(f"{model_name} - Test Accuracy: {test_score:.4f}, CV: {cv_scores.mean():.4f}")
        return results

    def select_best_model(self, results):
        best_model = max(results.items(), key=lambda x: x[1]["test_accuracy"])
        logger.info(f"Best model: {best_model[0]} with accuracy {best_model[1]['test_accuracy']:.4f}")
        return best_model[0]

    def save_model(self, model_name, results, language):
        model_data = results[model_name]
        model_file = self.output_dir / f"intent_classifier_{language}.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump({
                "vectorizer": model_data["vectorizer"],
                "classifier": model_data["classifier"],
                "model_name": model_name
            }, f)
        logger.info(f"Best model ({model_name}) saved to {model_file}")
        return model_file

def main():
    parser = argparse.ArgumentParser(description="Train intent classifiers for a specific language.")
    parser.add_argument("--data", type=str, required=True, help="Path to language-specific training data CSV")
    parser.add_argument("--language", type=str, required=True, help="Language code (e.g., 'en', 'hi')")
    parser.add_argument("--output-dir", type=str, default="models/nlu", help="Output directory for models")
    args = parser.parse_args()

    trainer = IntentTrainer(output_dir=args.output_dir)
    texts, labels = trainer.load_data(args.data)
    results = trainer.train_and_evaluate(texts, labels)
    best_model = trainer.select_best_model(results)
    model_file = trainer.save_model(best_model, results, args.language)

    print(f"\n{'='*70}\n✅ {args.language.upper()} Training Complete!\n{'='*70}")
    print(f"Best model: {best_model}")
    print(f"Test accuracy: {results[best_model]['test_accuracy']:.4f}")
    print(f"Model saved to: {model_file}")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
