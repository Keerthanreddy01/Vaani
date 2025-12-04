#!/usr/bin/env python3
"""
VAANI Annotation Validator
Validates annotation files for completeness, consistency, and format.

Usage:
    python pipeline/annotation/validate_annotations.py
    python pipeline/annotation/validate_annotations.py --input data/annotations/annotations_day2.json
"""

import json
import argparse
from pathlib import Path
from collections import Counter

# Valid intents
VALID_INTENTS = [
    "GREETING", "QUERY_TIME", "QUERY_WEATHER", "OPEN_APP",
    "CALL_PERSON", "GENERAL_KNOWLEDGE", "ALARM_SET", "REMINDER_SET",
    "JOKE", "CASUAL_CHAT"
]

# Valid entity types
VALID_ENTITY_TYPES = ["TIME", "LOCATION", "PERSON", "APP", "DATE", "TASK"]

# Required fields
REQUIRED_FIELDS = ["id", "audio_file", "transcription", "intent", "entities", "metadata"]
REQUIRED_METADATA = ["annotator", "annotation_date", "quality_score"]


class AnnotationValidator:
    """Validates annotation data."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {
            "total": 0,
            "valid": 0,
            "errors": 0,
            "warnings": 0
        }
    
    def validate_structure(self, annotation, idx):
        """Validate annotation structure."""
        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in annotation:
                self.errors.append(f"Annotation {idx}: Missing required field '{field}'")
                return False
        
        # Check metadata
        if "metadata" in annotation:
            for field in REQUIRED_METADATA:
                if field not in annotation["metadata"]:
                    self.warnings.append(f"Annotation {idx}: Missing metadata field '{field}'")
        
        return True
    
    def validate_intent(self, annotation, idx):
        """Validate intent classification."""
        intent = annotation.get("intent", "")
        if intent not in VALID_INTENTS:
            self.errors.append(f"Annotation {idx} ({annotation.get('id')}): Invalid intent '{intent}'")
            return False
        return True
    
    def validate_entities(self, annotation, idx):
        """Validate entity extraction."""
        entities = annotation.get("entities", [])
        transcription = annotation.get("transcription", "")
        
        for i, entity in enumerate(entities):
            # Check required entity fields
            if "type" not in entity:
                self.errors.append(f"Annotation {idx}: Entity {i} missing 'type'")
                continue
            
            if "value" not in entity:
                self.errors.append(f"Annotation {idx}: Entity {i} missing 'value'")
                continue
            
            # Validate entity type
            if entity["type"] not in VALID_ENTITY_TYPES:
                self.warnings.append(
                    f"Annotation {idx}: Unknown entity type '{entity['type']}'"
                )
            
            # Validate entity positions
            if "start" in entity and "end" in entity:
                start = entity["start"]
                end = entity["end"]
                
                if start < 0 or end > len(transcription):
                    self.errors.append(
                        f"Annotation {idx}: Entity position out of bounds ({start}, {end})"
                    )
                
                # Check if entity value matches transcription
                if 0 <= start < end <= len(transcription):
                    extracted = transcription[start:end]
                    if extracted != entity["value"]:
                        self.warnings.append(
                            f"Annotation {idx}: Entity value mismatch. "
                            f"Expected '{entity['value']}', got '{extracted}'"
                        )
        
        return True
    
    def validate_quality(self, annotation, idx):
        """Validate quality score."""
        if "metadata" in annotation and "quality_score" in annotation["metadata"]:
            score = annotation["metadata"]["quality_score"]
            if not isinstance(score, int) or score < 1 or score > 5:
                self.warnings.append(
                    f"Annotation {idx}: Quality score should be 1-5, got {score}"
                )
        return True
    
    def validate_file(self, filepath):
        """Validate entire annotation file."""
        print(f"🔍 Validating: {filepath}\n")
        
        # Load annotations
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                annotations = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON format: {e}")
            return False
        except FileNotFoundError:
            self.errors.append(f"File not found: {filepath}")
            return False
        
        if not isinstance(annotations, list):
            self.errors.append("Annotations should be a list")
            return False
        
        self.stats["total"] = len(annotations)
        
        # Validate each annotation
        for idx, annotation in enumerate(annotations):
            valid = True
            
            if not self.validate_structure(annotation, idx):
                valid = False
            
            if valid:
                self.validate_intent(annotation, idx)
                self.validate_entities(annotation, idx)
                self.validate_quality(annotation, idx)
            
            if valid and not any(f"Annotation {idx}" in e for e in self.errors):
                self.stats["valid"] += 1
        
        self.stats["errors"] = len(self.errors)
        self.stats["warnings"] = len(self.warnings)
        
        return len(self.errors) == 0
    
    def print_report(self):
        """Print validation report."""
        print(f"\n{'='*60}")
        print("📊 VALIDATION REPORT")
        print(f"{'='*60}\n")
        
        print(f"Total annotations: {self.stats['total']}")
        print(f"Valid annotations: {self.stats['valid']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Warnings: {self.stats['warnings']}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors[:10]:  # Show first 10
                print(f"   • {error}")
            if len(self.errors) > 10:
                print(f"   ... and {len(self.errors) - 10} more")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"   • {warning}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more")
        
        if not self.errors and not self.warnings:
            print("\n✅ All annotations are valid!")
        elif not self.errors:
            print("\n✅ No errors found (warnings can be ignored)")
        else:
            print("\n❌ Validation failed. Please fix errors.")


def main():
    parser = argparse.ArgumentParser(description="Validate VAANI annotations")
    parser.add_argument("--input", default="data/annotations/annotations_day2.json",
                        help="Input annotation file")
    
    args = parser.parse_args()
    
    validator = AnnotationValidator()
    validator.validate_file(args.input)
    validator.print_report()
    
    # Exit with error code if validation failed
    if validator.stats["errors"] > 0:
        exit(1)


if __name__ == "__main__":
    main()

