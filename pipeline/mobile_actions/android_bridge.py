"""
Android Bridge for VAANI Accessibility Assistant

Provides interface to Android Accessibility Service via:
- ADB commands (for development/testing)
- WebSocket (for production app)
- HTTP API (fallback)
"""

import subprocess
import logging
import json
import socket
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)


class AndroidBridge:
    """Bridge to Android device for accessibility actions"""
    
    def __init__(self, mode='adb', host='localhost', port=8765):
        """
        Initialize Android bridge.
        
        Args:
            mode: 'adb', 'websocket', or 'http'
            host: Host for websocket/http connection
            port: Port for websocket/http connection
        """
        self.mode = mode
        self.host = host
        self.port = port
        self.connected = False
        
        if mode == 'adb':
            self._check_adb()
        
        logger.info(f"AndroidBridge initialized in {mode} mode")
    
    def _check_adb(self):
        """Check if ADB is available"""
        try:
            result = subprocess.run(['adb', 'devices'], 
                                  capture_output=True, text=True, timeout=5)
            if 'device' in result.stdout:
                self.connected = True
                logger.info("ADB connected to device")
            else:
                logger.warning("No ADB devices found")
        except Exception as e:
            logger.error(f"ADB not available: {e}")
    
    def _adb_shell(self, command: str) -> str:
        """Execute ADB shell command"""
        try:
            result = subprocess.run(
                ['adb', 'shell', command],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"ADB command failed: {e}")
            return ""
    
    def tap(self, x: int, y: int) -> Dict[str, Any]:
        """Tap at screen coordinates"""
        if self.mode == 'adb':
            self._adb_shell(f'input tap {x} {y}')
            return {"status": "success", "message": f"Tapped at ({x}, {y})"}
        return {"status": "error", "message": "Not implemented for this mode"}
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> Dict[str, Any]:
        """Swipe from (x1,y1) to (x2,y2)"""
        if self.mode == 'adb':
            self._adb_shell(f'input swipe {x1} {y1} {x2} {y2} {duration}')
            return {"status": "success", "message": f"Swiped from ({x1},{y1}) to ({x2},{y2})"}
        return {"status": "error", "message": "Not implemented for this mode"}
    
    def open_app(self, package_name: str) -> Dict[str, Any]:
        """Open app by package name"""
        if self.mode == 'adb':
            # Get launch activity
            activity = self._adb_shell(f'cmd package resolve-activity --brief {package_name} | tail -n 1')
            if activity:
                self._adb_shell(f'am start -n {activity}')
                return {"status": "success", "message": f"Opened {package_name}"}
            else:
                # Fallback: monkey launch
                self._adb_shell(f'monkey -p {package_name} -c android.intent.category.LAUNCHER 1')
                return {"status": "success", "message": f"Launched {package_name}"}
        return {"status": "error", "message": "Not implemented for this mode"}
    
    def go_back(self) -> Dict[str, Any]:
        """Press back button"""
        if self.mode == 'adb':
            self._adb_shell('input keyevent KEYCODE_BACK')
            return {"status": "success", "message": "Pressed back"}
        return {"status": "error", "message": "Not implemented"}
    
    def go_home(self) -> Dict[str, Any]:
        """Press home button"""
        if self.mode == 'adb':
            self._adb_shell('input keyevent KEYCODE_HOME')
            return {"status": "success", "message": "Pressed home"}
        return {"status": "error", "message": "Not implemented"}
    
    def scroll(self, direction: str = 'down') -> Dict[str, Any]:
        """Scroll in direction"""
        if self.mode == 'adb':
            # Get screen size
            size = self._adb_shell('wm size')
            # Parse: Physical size: 1080x2400
            if 'x' in size:
                width, height = map(int, size.split(':')[-1].strip().split('x'))
                cx, cy = width // 2, height // 2
                
                if direction == 'down':
                    self.swipe(cx, cy + 200, cx, cy - 200)
                elif direction == 'up':
                    self.swipe(cx, cy - 200, cx, cy + 200)
                elif direction == 'left':
                    self.swipe(cx + 200, cy, cx - 200, cy)
                elif direction == 'right':
                    self.swipe(cx - 200, cy, cx + 200, cy)
                
                return {"status": "success", "message": f"Scrolled {direction}"}
        return {"status": "error", "message": "Not implemented"}

    def type_text(self, text: str) -> Dict[str, Any]:
        """Type text using keyboard"""
        if self.mode == 'adb':
            # Escape special characters
            text = text.replace(' ', '%s').replace('&', '\\&')
            self._adb_shell(f'input text "{text}"')
            return {"status": "success", "message": f"Typed: {text}"}
        return {"status": "error", "message": "Not implemented"}

    def call_contact(self, phone_number: str) -> Dict[str, Any]:
        """Make phone call"""
        if self.mode == 'adb':
            self._adb_shell(f'am start -a android.intent.action.CALL -d tel:{phone_number}')
            return {"status": "success", "message": f"Calling {phone_number}"}
        return {"status": "error", "message": "Not implemented"}

    def send_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send SMS message"""
        if self.mode == 'adb':
            message = message.replace(' ', '%s')
            self._adb_shell(f'am start -a android.intent.action.SENDTO -d sms:{phone_number} --es sms_body "{message}"')
            # Auto-send (requires accessibility service)
            self._adb_shell('input keyevent KEYCODE_ENTER')
            return {"status": "success", "message": f"Sent SMS to {phone_number}"}
        return {"status": "error", "message": "Not implemented"}

    def read_screen(self) -> Dict[str, Any]:
        """Read screen content using UI dump"""
        if self.mode == 'adb':
            # Dump UI hierarchy
            self._adb_shell('uiautomator dump /sdcard/window_dump.xml')
            xml = self._adb_shell('cat /sdcard/window_dump.xml')

            # Extract text from XML (simple parsing)
            import re
            texts = re.findall(r'text="([^"]+)"', xml)
            texts = [t for t in texts if t.strip() and t != 'null']

            if texts:
                screen_text = ' '.join(texts[:20])  # First 20 text elements
                return {"status": "success", "message": "Screen read", "data": {"text": screen_text}}
            else:
                return {"status": "success", "message": "No text on screen", "data": {"text": ""}}
        return {"status": "error", "message": "Not implemented"}

    def read_notifications(self) -> Dict[str, Any]:
        """Read recent notifications"""
        if self.mode == 'adb':
            # Open notification shade
            self._adb_shell('cmd statusbar expand-notifications')
            # Wait and read
            import time
            time.sleep(0.5)
            result = self.read_screen()
            # Close notification shade
            self._adb_shell('cmd statusbar collapse')
            return result
        return {"status": "error", "message": "Not implemented"}

    def emergency_sos(self) -> Dict[str, Any]:
        """Trigger emergency SOS"""
        if self.mode == 'adb':
            # Call emergency number (varies by country)
            self.call_contact('911')  # US emergency number
            return {"status": "success", "message": "Emergency SOS triggered"}
        return {"status": "error", "message": "Not implemented"}

    def set_volume(self, level: int) -> Dict[str, Any]:
        """Set system volume (0-15)"""
        if self.mode == 'adb':
            level = max(0, min(15, level))
            self._adb_shell(f'media volume --stream 3 --set {level}')
            return {"status": "success", "message": f"Volume set to {level}"}
        return {"status": "error", "message": "Not implemented"}

    def set_brightness(self, level: int) -> Dict[str, Any]:
        """Set screen brightness (0-255)"""
        if self.mode == 'adb':
            level = max(0, min(255, level))
            self._adb_shell(f'settings put system screen_brightness {level}')
            return {"status": "success", "message": f"Brightness set to {level}"}
        return {"status": "error", "message": "Not implemented"}

    def take_photo(self) -> Dict[str, Any]:
        """Take photo with camera"""
        if self.mode == 'adb':
            self._adb_shell('am start -a android.media.action.IMAGE_CAPTURE')
            # Wait and press shutter (center tap)
            import time
            time.sleep(2)
            self.tap(540, 1800)  # Approximate shutter button location
            return {"status": "success", "message": "Photo taken"}
        return {"status": "error", "message": "Not implemented"}


# App package name mappings
ANDROID_APP_PACKAGES = {
    'whatsapp': 'com.whatsapp',
    'chrome': 'com.android.chrome',
    'gmail': 'com.google.android.gm',
    'maps': 'com.google.android.apps.maps',
    'youtube': 'com.google.android.youtube',
    'spotify': 'com.spotify.music',
    'facebook': 'com.facebook.katana',
    'instagram': 'com.instagram.android',
    'twitter': 'com.twitter.android',
    'messenger': 'com.facebook.orca',
    'phone': 'com.android.dialer',
    'contacts': 'com.android.contacts',
    'messages': 'com.google.android.apps.messaging',
    'camera': 'com.android.camera2',
    'gallery': 'com.google.android.apps.photos',
    'settings': 'com.android.settings',
    'calculator': 'com.android.calculator2',
    'calendar': 'com.google.android.calendar',
    'clock': 'com.google.android.deskclock',
    'notes': 'com.google.android.keep',
}


