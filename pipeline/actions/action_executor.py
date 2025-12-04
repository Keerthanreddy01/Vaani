import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ActionExecutor:
    def __init__(self, config=None):
        self.config = config or {}
        self.safe_mode = self.config.get('safe_mode', True)
        self.action_history = []
        
        try:
            from pipeline.actions.action_router import ActionRouter
            self.router = ActionRouter(config=self.config)
            logger.info("ActionExecutor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ActionRouter: {e}")
            self.router = None
    
    def execute_action(self, intent: str, entities: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        if not self.router:
            return {
                "status": "error",
                "message": "Action router not available",
                "data": {}
            }
        
        try:
            logger.info(f"Executing action for intent: {intent}")
            logger.debug(f"Entities: {entities}")
            
            result = self.router.route(intent, entities, context)
            
            self.action_history.append({
                "intent": intent,
                "entities": entities,
                "result": result
            })
            
            if len(self.action_history) > 100:
                self.action_history = self.action_history[-100:]
            
            return result
        
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to execute action: {str(e)}",
                "data": {"error": str(e)}
            }
    
    def get_history(self, limit: int = 10) -> list:
        return self.action_history[-limit:]
    
    def clear_history(self):
        self.action_history = []
        logger.info("Action history cleared")

def execute_action_from_dm(dm_output: Dict[str, Any], config: Optional[Dict] = None) -> Dict[str, Any]:
    if not dm_output.get('should_act', False):
        return {
            "status": "skipped",
            "message": "No action required",
            "data": {}
        }
    
    executor = ActionExecutor(config=config)
    
    intent = dm_output.get('action', '')
    entities = dm_output.get('entities', {})
    context = dm_output.get('context', {})
    
    return executor.execute_action(intent, entities, context)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    executor = ActionExecutor()
    
    test_cases = [
        {
            "intent": "OPEN_APP",
            "entities": {"app": "notepad"},
            "context": {}
        },
        {
            "intent": "OPEN_WEBSITE",
            "entities": {"url": "https://google.com"},
            "context": {}
        }
    ]
    
    for test in test_cases:
        print(f"\nTesting: {test['intent']}")
        result = executor.execute_action(test['intent'], test['entities'], test['context'])
        print(f"Result: {result}")

