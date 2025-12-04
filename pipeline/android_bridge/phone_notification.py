"""
Phone Notification System
Shows VAANI status on phone screen using ADB (no app install needed)
"""

import subprocess
import logging
from typing import Optional
import threading
import time

logger = logging.getLogger(__name__)


class PhoneNotification:
    """Shows status on phone screen via ADB"""

    def __init__(self, device_id: str, adb_path: str = 'adb'):
        self.device_id = device_id
        self.adb_path = adb_path
        self.current_status = None
        self.status_thread = None
        self.running = False

    def _show_on_screen(self, message: str, duration: int = 2):
        """Show message on phone screen using input text"""
        try:
            # Method 1: Use input keyevent to wake screen
            subprocess.run(
                [self.adb_path, '-s', self.device_id, 'shell', 'input', 'keyevent', 'KEYCODE_WAKEUP'],
                capture_output=True, timeout=2
            )

            # Method 2: Show via service call (status bar notification)
            # This creates a persistent notification
            cmd = [
                self.adb_path, '-s', self.device_id, 'shell',
                'cmd', 'notification', 'post',
                '-t', 'VAANI Status',
                'vaani_status',
                message
            ]
            subprocess.run(cmd, capture_output=True, timeout=2)

            # Method 3: Log to logcat with tag
            log_cmd = [
                self.adb_path, '-s', self.device_id, 'shell',
                'log', '-t', 'VAANI_STATUS', message
            ]
            subprocess.run(log_cmd, capture_output=True, timeout=2)

            logger.info(f"📱 Phone: {message}")

        except Exception as e:
            logger.debug(f"Could not show on screen: {e}")

    def listening(self):
        """Show listening status"""
        self._show_on_screen("🔵 VAANI: LISTENING - Speak now...")
        self.current_status = "LISTENING"

    def processing(self):
        """Show processing status"""
        self._show_on_screen("🟡 VAANI: PROCESSING - Understanding your command...")
        self.current_status = "PROCESSING"

    def speaking(self):
        """Show speaking status"""
        self._show_on_screen("🟣 VAANI: SPEAKING - Responding...")
        self.current_status = "SPEAKING"

    def action_ok(self, action: str = ""):
        """Show action success"""
        msg = f"🟢 VAANI: SUCCESS - {action}" if action else "🟢 VAANI: SUCCESS"
        self._show_on_screen(msg)
        self.current_status = "SUCCESS"

    def action_failed(self, error: str = ""):
        """Show action failed"""
        msg = f"🔴 VAANI: ERROR - {error}" if error else "🔴 VAANI: ERROR"
        self._show_on_screen(msg)
        self.current_status = "ERROR"

    def idle(self):
        """Show idle status"""
        self._show_on_screen("⚫ VAANI: IDLE - Ready")
        self.current_status = "IDLE"

    def disconnect(self):
        """Cleanup"""
        self.running = False
        if self.status_thread:
            self.status_thread.join(timeout=1)

