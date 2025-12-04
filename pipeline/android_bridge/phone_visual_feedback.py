"""
Phone Visual Feedback System
Shows persistent visual status on phone screen using ADB
"""

import subprocess
import logging
import threading
import time

logger = logging.getLogger(__name__)


class PhoneVisualFeedback:
    """Shows persistent visual feedback on phone screen"""
    
    def __init__(self, device_id: str, adb_path: str = 'adb'):
        self.device_id = device_id
        self.adb_path = adb_path
        self.current_state = "IDLE"
        self.running = False
        self.update_thread = None
        
    def _shell(self, command: str) -> str:
        """Execute ADB shell command"""
        try:
            result = subprocess.run(
                [self.adb_path, '-s', self.device_id, 'shell', command],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except Exception as e:
            logger.debug(f"Shell command failed: {e}")
            return ""
    
    def _show_persistent_notification(self, title: str, message: str, icon: str):
        """Show persistent notification on phone"""
        try:
            # Wake screen
            self._shell('input keyevent KEYCODE_WAKEUP')
            
            # Post notification using cmd notification
            cmd = f'cmd notification post -t "{title}" vaani_status "{icon} {message}"'
            self._shell(cmd)
            
            # Also show as toast for immediate feedback
            # Note: This requires a helper app, so we'll use logcat instead
            self._shell(f'log -t VAANI "{icon} {title}: {message}"')
            
            logger.info(f"📱 {icon} {title}: {message}")
            
        except Exception as e:
            logger.debug(f"Could not show notification: {e}")
    
    def _update_loop(self):
        """Continuously update visual feedback - DISABLED to prevent spam"""
        # This loop is disabled - notifications are only sent when state changes
        pass
    
    def start(self):
        """Start visual feedback system"""
        if not self.running:
            self.running = True
            # No update thread needed - notifications sent on state change only
            logger.info("✅ Visual feedback system started")
    
    def stop(self):
        """Stop visual feedback system"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=3)
        # Clear notification
        try:
            self._shell('cmd notification cancel vaani_status')
        except:
            pass
        logger.info("✅ Visual feedback system stopped")
    
    def listening(self):
        """Show listening state"""
        if self.current_state != "LISTENING":  # Only update if state changed
            self.current_state = "LISTENING"
            self._show_persistent_notification("VAANI LISTENING", "Speak now...", "🔵")
    
    def processing(self):
        """Show processing state"""
        self.current_state = "PROCESSING"
        self._show_persistent_notification("VAANI PROCESSING", "Understanding...", "🟡")
    
    def speaking(self):
        """Show speaking state"""
        self.current_state = "SPEAKING"
        self._show_persistent_notification("VAANI SPEAKING", "Responding...", "🟣")
    
    def action_ok(self, action: str = ""):
        """Show success state"""
        self.current_state = "SUCCESS"
        msg = f"Executed: {action}" if action else "Success!"
        self._show_persistent_notification("VAANI SUCCESS", msg, "🟢")
    
    def action_failed(self, error: str = ""):
        """Show error state"""
        self.current_state = "ERROR"
        msg = f"Error: {error}" if error else "Failed"
        self._show_persistent_notification("VAANI ERROR", msg, "🔴")
    
    def idle(self):
        """Show idle state"""
        self.current_state = "IDLE"
        try:
            self._shell('cmd notification cancel vaani_status')
        except:
            pass

