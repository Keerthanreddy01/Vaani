import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    HAS_PYCAW = True
except ImportError:
    HAS_PYCAW = False
    logger.warning("pycaw not available. Volume control disabled.")

def get_volume_interface():
    if not HAS_PYCAW:
        return None
    
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        return volume
    except Exception as e:
        logger.error(f"Failed to get volume interface: {e}")
        return None

def change_volume(action: str, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    if not HAS_PYCAW:
        return {
            "status": "error",
            "message": "Volume control not available. Install pycaw.",
            "data": {}
        }
    
    volume = get_volume_interface()
    if not volume:
        return {
            "status": "error",
            "message": "Failed to access volume control",
            "data": {}
        }
    
    try:
        current_volume = volume.GetMasterVolumeLevelScalar()
        
        if action == "up":
            new_volume = min(1.0, current_volume + 0.1)
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            message = f"Volume increased to {int(new_volume * 100)}%"
        
        elif action == "down":
            new_volume = max(0.0, current_volume - 0.1)
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            message = f"Volume decreased to {int(new_volume * 100)}%"
        
        elif action == "set":
            level = entities.get('level', 50)
            new_volume = max(0.0, min(1.0, level / 100.0))
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            message = f"Volume set to {int(new_volume * 100)}%"
        
        else:
            return {
                "status": "error",
                "message": f"Unknown volume action: {action}",
                "data": {}
            }
        
        logger.info(message)
        return {
            "status": "success",
            "message": message,
            "data": {"volume": int(new_volume * 100)}
        }
    
    except Exception as e:
        logger.error(f"Volume control failed: {e}")
        return {
            "status": "error",
            "message": f"Failed to change volume: {str(e)}",
            "data": {"error": str(e)}
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if HAS_PYCAW:
        result = change_volume("up", {}, {})
        print(f"Result: {result}")
    else:
        print("pycaw not available")

