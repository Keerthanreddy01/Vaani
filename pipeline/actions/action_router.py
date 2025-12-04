import logging
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

class ActionRouter:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.action_map = {}
        self._register_actions()
    
    def _register_actions(self):
        try:
            from pipeline.actions.modules.open_app_action import open_app
            from pipeline.actions.modules.open_website_action import open_website
            from pipeline.actions.modules.play_media_action import play_media
            from pipeline.actions.modules.volume_control_action import change_volume
            from pipeline.actions.modules.brightness_control_action import change_brightness
            from pipeline.actions.modules.open_file_action import open_file
            from pipeline.actions.modules.system_command_action import execute_system_command
            
            self.action_map = {
                "OPEN_APP": open_app,
                "OPEN_WEBSITE": open_website,
                "PLAY_MUSIC": play_media,
                "PLAY_MEDIA": play_media,
                "VOLUME_UP": lambda e, c: change_volume("up", e, c),
                "VOLUME_DOWN": lambda e, c: change_volume("down", e, c),
                "VOLUME_SET": lambda e, c: change_volume("set", e, c),
                "BRIGHTNESS_UP": lambda e, c: change_brightness("up", e, c),
                "BRIGHTNESS_DOWN": lambda e, c: change_brightness("down", e, c),
                "BRIGHTNESS_SET": lambda e, c: change_brightness("set", e, c),
                "OPEN_FILE": open_file,
                "OPEN_FOLDER": open_file,
                "SYSTEM_SHUTDOWN": lambda e, c: execute_system_command("shutdown", e, c),
                "SYSTEM_RESTART": lambda e, c: execute_system_command("restart", e, c),
                "SYSTEM_LOCK": lambda e, c: execute_system_command("lock", e, c),
                "SYSTEM_SLEEP": lambda e, c: execute_system_command("sleep", e, c),
                "CALL_PERSON": self._handle_call,
            }
            
            logger.info(f"Registered {len(self.action_map)} actions")
        
        except ImportError as e:
            logger.error(f"Failed to import action modules: {e}")
    
    def _handle_call(self, entities: Dict, context: Dict) -> Dict:
        person = entities.get('person', '')
        if not person:
            return {
                "status": "error",
                "message": "No person specified for call",
                "data": {}
            }
        
        from pipeline.actions.modules.open_app_action import open_app
        return open_app({"app": "whatsapp"}, context)
    
    def route(self, intent: str, entities: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        context = context or {}
        
        if intent not in self.action_map:
            logger.warning(f"No action registered for intent: {intent}")
            return {
                "status": "error",
                "message": f"No action available for intent: {intent}",
                "data": {"intent": intent}
            }
        
        try:
            action_func = self.action_map[intent]
            result = action_func(entities, context)
            
            logger.info(f"Action {intent} executed: {result['status']}")
            return result
        
        except Exception as e:
            logger.error(f"Action routing failed for {intent}: {e}")
            return {
                "status": "error",
                "message": f"Action failed: {str(e)}",
                "data": {"error": str(e), "intent": intent}
            }
    
    def list_actions(self) -> list:
        return list(self.action_map.keys())
    
    def has_action(self, intent: str) -> bool:
        return intent in self.action_map

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    router = ActionRouter()
    print(f"Available actions: {router.list_actions()}")

