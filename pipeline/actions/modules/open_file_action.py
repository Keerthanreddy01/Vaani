import os
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

def open_file(entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    file_path = entities.get('file', '')
    folder_path = entities.get('folder', '')
    
    path = file_path or folder_path
    
    if not path:
        path = entities.get('LOCATION', '')
    
    if not path:
        return {
            "status": "error",
            "message": "No file or folder specified",
            "data": {}
        }
    
    path = Path(path)
    
    if not path.exists():
        return {
            "status": "error",
            "message": f"Path not found: {path}",
            "data": {"path": str(path)}
        }
    
    try:
        os.startfile(str(path))
        logger.info(f"Opened: {path}")
        
        item_type = "folder" if path.is_dir() else "file"
        
        return {
            "status": "success",
            "message": f"Opening {item_type}: {path.name}",
            "data": {"path": str(path), "type": item_type}
        }
    
    except Exception as e:
        logger.error(f"Failed to open {path}: {e}")
        return {
            "status": "error",
            "message": f"Failed to open: {str(e)}",
            "data": {"path": str(path), "error": str(e)}
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    result = open_file({"folder": "C:\\Users"}, {})
    print(f"Result: {result}")

