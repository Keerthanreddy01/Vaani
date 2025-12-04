import os
import subprocess
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

APP_PATHS = {
    "spotify": "C:\\Users\\keert\\AppData\\Roaming\\Spotify\\Spotify.exe",
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "whatsapp": "C:\\Users\\keert\\AppData\\Local\\Programs\\WhatsApp\\WhatsApp.exe",
    "notepad": "notepad.exe",
    "calc": "calc.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "explorer": "explorer.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
}

def open_app(entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    app_name = entities.get('app', '').lower()
    
    if not app_name:
        app_name = entities.get('APP', '').lower()
    
    if not app_name:
        return {
            "status": "error",
            "message": "No app specified",
            "data": {}
        }
    
    app_path = APP_PATHS.get(app_name)
    
    if not app_path:
        return {
            "status": "error",
            "message": f"App '{app_name}' not found in registry",
            "data": {"app": app_name, "available_apps": list(APP_PATHS.keys())}
        }
    
    try:
        if os.path.exists(app_path):
            os.startfile(app_path)
        else:
            subprocess.Popen(app_path, shell=True)
        
        logger.info(f"Opened app: {app_name}")
        return {
            "status": "success",
            "message": f"Opening {app_name}",
            "data": {"app": app_name, "path": app_path}
        }
    
    except FileNotFoundError:
        logger.error(f"App not found: {app_path}")
        return {
            "status": "error",
            "message": f"App '{app_name}' not found on system",
            "data": {"app": app_name, "path": app_path}
        }
    
    except Exception as e:
        logger.error(f"Failed to open app {app_name}: {e}")
        return {
            "status": "error",
            "message": f"Failed to open {app_name}: {str(e)}",
            "data": {"app": app_name, "error": str(e)}
        }

def list_apps() -> list:
    return list(APP_PATHS.keys())

def add_app(name: str, path: str):
    APP_PATHS[name.lower()] = path
    logger.info(f"Added app: {name} -> {path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Available apps:", list_apps())
    
    result = open_app({"app": "notepad"}, {})
    print(f"Result: {result}")

