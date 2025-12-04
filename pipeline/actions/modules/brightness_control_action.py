import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

try:
    import screen_brightness_control as sbc
    HAS_SBC = True
except ImportError:
    HAS_SBC = False
    logger.warning("screen_brightness_control not available. Brightness control disabled.")

def change_brightness(action: str, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    if not HAS_SBC:
        return {
            "status": "error",
            "message": "Brightness control not available. Install screen-brightness-control.",
            "data": {}
        }
    
    try:
        current_brightness = sbc.get_brightness()[0]
        
        if action == "up":
            new_brightness = min(100, current_brightness + 10)
            sbc.set_brightness(new_brightness)
            message = f"Brightness increased to {new_brightness}%"
        
        elif action == "down":
            new_brightness = max(0, current_brightness - 10)
            sbc.set_brightness(new_brightness)
            message = f"Brightness decreased to {new_brightness}%"
        
        elif action == "set":
            level = entities.get('level', 50)
            new_brightness = max(0, min(100, level))
            sbc.set_brightness(new_brightness)
            message = f"Brightness set to {new_brightness}%"
        
        else:
            return {
                "status": "error",
                "message": f"Unknown brightness action: {action}",
                "data": {}
            }
        
        logger.info(message)
        return {
            "status": "success",
            "message": message,
            "data": {"brightness": new_brightness}
        }
    
    except Exception as e:
        logger.error(f"Brightness control failed: {e}")
        return {
            "status": "error",
            "message": f"Failed to change brightness: {str(e)}",
            "data": {"error": str(e)}
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if HAS_SBC:
        result = change_brightness("up", {}, {})
        print(f"Result: {result}")
    else:
        print("screen_brightness_control not available")

