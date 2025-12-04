"""
End-to-end VAANI pipeline.

Integrates VAD, ASR, NLU, DST, DM, and NLG.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.vad.vad import VoiceActivityDetector
from pipeline.nlu.predict import NLUPredictor
from pipeline.dst.state_manager import DialogueStateManager
from pipeline.dm.decision_manager import DecisionManager
from pipeline.nlg.generate_response import ResponseGenerator
from utils.logger import get_logger

logger = get_logger(__name__)


class VAANIPipeline:
    """End-to-end VAANI pipeline."""
    
    def __init__(self, intent_model_path, entity_model_path, use_vad=True):
        """
        Initialize pipeline.
        
        Args:
            intent_model_path: Path to intent classifier
            entity_model_path: Path to entity extractor
            use_vad: Whether to use VAD
        """
        logger.info("Initializing VAANI Pipeline...")
        
        # Initialize components
        if use_vad:
            self.vad = VoiceActivityDetector()
            logger.info("✓ VAD initialized")
        else:
            self.vad = None
        
        self.nlu = NLUPredictor(intent_model_path, entity_model_path)
        logger.info("✓ NLU initialized")
        
        self.state = DialogueStateManager()
        logger.info("✓ DST initialized")
        
        self.dm = DecisionManager()
        logger.info("✓ DM initialized")
        
        self.nlg = ResponseGenerator()
        logger.info("✓ NLG initialized")
        
        logger.info("VAANI Pipeline ready!")
    
    def process_text(self, text):
        """
        Process text input through the pipeline.
        
        Args:
            text: User input text
            
        Returns:
            Response text
        """
        logger.info(f"Processing: {text}")
        
        # NLU
        nlu_result = self.nlu.predict_all(text)
        intent = nlu_result["intent"]
        entities = nlu_result["entities"]
        
        logger.info(f"Intent: {intent}, Entities: {len(entities)}")
        
        # Update dialogue state
        self.state.update_turn(
            user_input=text,
            intent=intent,
            entities=entities,
            response=None  # Will be filled after generation
        )
        
        # Decision manager
        action = self.dm.decide(intent, self.state, entities)
        logger.info(f"Action: {action['action']}")
        
        # Generate response
        response = self.nlg.generate(action)
        
        # Update state with response
        last_turn = self.state.get_last_turn()
        if last_turn:
            last_turn['response'] = response
        
        logger.info(f"Response: {response}")
        
        return response
    
    def process_audio(self, audio_path, asr_method="google"):
        """
        Process audio input through the pipeline.
        
        Args:
            audio_path: Path to audio file
            asr_method: ASR method to use
            
        Returns:
            Response text
        """
        logger.info(f"Processing audio: {audio_path}")
        
        # VAD (if enabled)
        if self.vad:
            segments = self.vad.detect_speech(audio_path)
            logger.info(f"VAD detected {len(segments)} speech segments")
            # For now, process the whole file
            # In production, you'd process each segment
        
        # ASR
        # Note: This is a placeholder - you'd integrate actual ASR here
        if asr_method == "google":
            from pipeline.asr.asr_google import transcribe_audio
            transcription = transcribe_audio(audio_path)
        else:
            # Whisper or other ASR
            transcription = "ASR not implemented yet"
        
        logger.info(f"Transcription: {transcription}")
        
        # Process transcription through NLU pipeline
        return self.process_text(transcription)
    
    def reset(self):
        """Reset dialogue state."""
        self.state.reset()
        logger.info("Pipeline state reset")


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="VAANI End-to-End Pipeline")
    parser.add_argument("--text", type=str, help="Text input")
    parser.add_argument("--audio", type=str, help="Audio file input")
    parser.add_argument("--intent-model", type=str,
                       default="models/nlu/intent_classifier.pkl",
                       help="Path to intent classifier")
    parser.add_argument("--entity-model", type=str,
                       default="models/nlu/entity_extractor",
                       help="Path to entity extractor")
    parser.add_argument("--no-vad", action="store_true",
                       help="Disable VAD")
    parser.add_argument("--asr-method", type=str, default="google",
                       choices=["google", "whisper"],
                       help="ASR method")
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = VAANIPipeline(
        intent_model_path=args.intent_model,
        entity_model_path=args.entity_model,
        use_vad=not args.no_vad
    )
    
    # Process input
    if args.text:
        response = pipeline.process_text(args.text)
        print("\n" + "=" * 70)
        print("🤖 VAANI Response")
        print("=" * 70)
        print(f"User: {args.text}")
        print(f"VAANI: {response}")
        print("=" * 70)
    
    elif args.audio:
        response = pipeline.process_audio(args.audio, args.asr_method)
        print("\n" + "=" * 70)
        print("🤖 VAANI Response")
        print("=" * 70)
        print(f"Audio: {args.audio}")
        print(f"VAANI: {response}")
        print("=" * 70)
    
    else:
        print("Please provide --text or --audio input")


if __name__ == "__main__":
    main()

