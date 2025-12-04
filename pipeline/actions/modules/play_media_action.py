import os
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

def play_media(entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    file_path = entities.get('file', '')
    song_name = entities.get('song', '')
    
    if not file_path and not song_name:
        file_path = entities.get('TASK', '')
    
    if song_name and not file_path:
        return {
            "status": "error",
            "message": f"Cannot find song: {song_name}",
            "data": {"song": song_name}
        }
    
    if not file_path:
        return {
            "status": "error",
            "message": "No media file specified",
            "data": {}
        }
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        return {
            "status": "error",
            "message": f"File not found: {file_path}",
            "data": {"file": str(file_path)}
        }
    
    try:
        os.startfile(str(file_path))
        logger.info(f"Playing media: {file_path}")
        
        return {
            "status": "success",
            "message": f"Playing {file_path.name}",
            "data": {"file": str(file_path)}
        }
    
    except Exception as e:
        logger.error(f"Failed to play media {file_path}: {e}")
        return {
            "status": "error",
            "message": f"Failed to play media: {str(e)}",
            "data": {"file": str(file_path), "error": str(e)}
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    result = play_media({"file": "C:\\Windows\\Media\\Alarm01.wav"}, {})
    print(f"Result: {result}")

