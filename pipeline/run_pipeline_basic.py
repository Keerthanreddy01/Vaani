"""
VAANI Basic Pipeline with Action Execution
Integrates ASR, NLU, DST, DM, NLG, and Action Executor.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.nlu.predict import NLUPredictor
from pipeline.dst.state_manager import DialogueStateManager
from pipeline.dm.decision_manager import DecisionManager
from pipeline.nlg.generate_response import ResponseGenerator
from pipeline.actions.action_executor import ActionExecutor
from utils.logger import get_logger

logger = get_logger(__name__)


class VAANIBasicPipeline:
    """Basic VAANI pipeline with action execution."""
    
    def __init__(self, intent_model_path=None, entity_model_path=None):
        """Initialize pipeline."""
        logger.info("Initializing VAANI Basic Pipeline...")
        
        try:
            self.nlu = NLUPredictor(intent_model_path, entity_model_path)
            logger.info("✓ NLU initialized")
        except Exception as e:
            logger.warning(f"NLU initialization failed: {e}")
            self.nlu = None
        
        self.state = DialogueStateManager()
        logger.info("✓ DST initialized")
        
        self.dm = DecisionManager()
        logger.info("✓ DM initialized")
        
        self.nlg = ResponseGenerator()
        logger.info("✓ NLG initialized")
        
        self.action_executor = ActionExecutor()
        logger.info("✓ Action Executor initialized")
        
        logger.info("VAANI Basic Pipeline ready!")
    
    def process_text(self, text):
        """
        Process text input through the pipeline.
        
        Args:
            text: User input text
            
        Returns:
            dict: Response with text and action result
        """
        logger.info(f"Processing: {text}")
        
        if not self.nlu:
            return {
                "response": f"I heard: {text}",
                "action_result": None
            }
        
        # NLU
        nlu_result = self.nlu.predict_all(text)
        intent = nlu_result["intent"]
        entities = nlu_result["entities"]
        confidence = nlu_result["confidence"]
        
        logger.info(f"Intent: {intent} ({confidence:.2%}), Entities: {len(entities)}")
        
        # Update dialogue state
        self.state.update_turn(
            user_input=text,
            intent=intent,
            entities=entities
        )
        
        # Decision Manager
        action = self.dm.decide(intent, self.state, entities)
        logger.info(f"DM decision: {action.get('action', 'respond')}")
        
        # Check if action should be executed
        action_result = None
        if isinstance(action, dict) and action.get('should_act', False):
            logger.info(f"⚡ Executing action: {action['action']}")
            print(f"\n⚡ Executing action: {action['action']}")
            
            action_result = self.action_executor.execute_action(
                action['action'],
                action['entities'],
                action.get('context', {})
            )
            
            logger.info(f"✓ Action result: {action_result['status']} - {action_result['message']}")
            print(f"✓ Action result: {action_result['status']} - {action_result['message']}")
            
            response = self.nlg.generate(action_result)
        else:
            response = self.nlg.generate(action)
        
        logger.info(f"Response: {response}")
        
        return {
            "response": response,
            "action_result": action_result,
            "intent": intent,
            "entities": entities,
            "confidence": confidence
        }


def main():
    parser = argparse.ArgumentParser(description="VAANI Basic Pipeline")
    parser.add_argument("--intent-model", type=str, default="models/nlu/intent_classifier_tfidf_svm.pkl")
    parser.add_argument("--entity-model", type=str, default="models/nlu/entity_extractor_spacy")
    args = parser.parse_args()
    
    pipeline = VAANIBasicPipeline(args.intent_model, args.entity_model)
    
    print("\n" + "="*70)
    print("           🎙️  VAANI - Basic Pipeline with Actions")
    print("="*70 + "\n")
    print("Type your command or 'exit' to quit.\n")
    
    while True:
        try:
            text = input("You: ").strip()
            
            if not text:
                continue
            
            if text.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
            
            result = pipeline.process_text(text)
            print(f"\nVAANI: {result['response']}\n")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Error: {e}")


if __name__ == "__main__":
    main()

