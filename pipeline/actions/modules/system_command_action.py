import os
import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

DANGEROUS_COMMANDS = ["shutdown", "restart"]

def execute_system_command(command: str, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    safe_mode = context.get('safe_mode', True)
    confirm = entities.get('confirm', False)
    
    if command in DANGEROUS_COMMANDS and safe_mode and not confirm:
        return {
            "status": "error",
            "message": f"Command '{command}' requires confirmation in safe mode",
            "data": {"command": command, "requires_confirmation": True}
        }
    
    try:
        if command == "shutdown":
            subprocess.Popen("shutdown /s /t 60", shell=True)
            message = "System will shutdown in 60 seconds"
        
        elif command == "restart":
            subprocess.Popen("shutdown /r /t 60", shell=True)
            message = "System will restart in 60 seconds"
        
        elif command == "lock":
            subprocess.Popen("rundll32.exe user32.dll,LockWorkStation", shell=True)
            message = "Locking system"
        
        elif command == "sleep":
            subprocess.Popen("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
            message = "Putting system to sleep"
        
        elif command == "cancel_shutdown":
            subprocess.Popen("shutdown /a", shell=True)
            message = "Shutdown cancelled"
        
        else:
            return {
                "status": "error",
                "message": f"Unknown system command: {command}",
                "data": {"command": command}
            }
        
        logger.info(f"Executed system command: {command}")
        return {
            "status": "success",
            "message": message,
            "data": {"command": command}
        }
    
    except Exception as e:
        logger.error(f"System command failed: {e}")
        return {
            "status": "error",
            "message": f"Failed to execute command: {str(e)}",
            "data": {"command": command, "error": str(e)}
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    result = execute_system_command("lock", {}, {"safe_mode": False})
    print(f"Result: {result}")

