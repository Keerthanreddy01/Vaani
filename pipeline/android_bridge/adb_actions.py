"""
ADB Actions - Direct phone control via ADB commands
"""

import subprocess
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


# Android app package names
APP_PACKAGES = {
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


class ADBActions:
    """Execute actions on Android device via ADB"""

    def __init__(self, device_id: str, adb_path: str = 'adb'):
        """
        Initialize ADB actions.

        Args:
            device_id: Android device ID from ADB
            adb_path: Path to ADB executable
        """
        self.device_id = device_id
        self.adb_path = adb_path

    def _shell(self, command: str) -> str:
        """Execute ADB shell command"""
        try:
            result = subprocess.run(
                [self.adb_path, '-s', self.device_id, 'shell', command],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Shell command failed: {command} - {e}")
            return ""
    
    def open_app(self, app_name: str) -> Dict[str, Any]:
        """
        Open app by name or package.
        
        Args:
            app_name: App name (e.g., 'whatsapp') or package name
            
        Returns:
            Result dictionary
        """
        # Get package name
        package = APP_PACKAGES.get(app_name.lower(), app_name)
        
        logger.info(f"📱 Opening app: {app_name} ({package})")
        
        try:
            # Method 1: Monkey launch (most reliable)
            output = self._shell(f'monkey -p {package} -c android.intent.category.LAUNCHER 1')
            
            if 'Events injected' in output or 'monkey' in output.lower():
                logger.info(f"✅ Opened {app_name}")
                return {"status": "success", "message": f"Opened {app_name}"}
            
            # Method 2: Activity manager
            self._shell(f'am start -n {package}')
            time.sleep(0.5)
            
            return {"status": "success", "message": f"Opened {app_name}"}
            
        except Exception as e:
            logger.error(f"❌ Failed to open {app_name}: {e}")
            return {"status": "error", "message": str(e)}
    
    def tap(self, x: int, y: int) -> Dict[str, Any]:
        """
        Tap at screen coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Result dictionary
        """
        logger.info(f"👆 Tapping at ({x}, {y})")
        
        try:
            self._shell(f'input tap {x} {y}')
            return {"status": "success", "message": f"Tapped at ({x}, {y})"}
        except Exception as e:
            logger.error(f"❌ Tap failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> Dict[str, Any]:
        """
        Swipe from (x1,y1) to (x2,y2).
        
        Args:
            x1, y1: Start coordinates
            x2, y2: End coordinates
            duration: Swipe duration in ms
            
        Returns:
            Result dictionary
        """
        logger.info(f"👉 Swiping from ({x1},{y1}) to ({x2},{y2})")
        
        try:
            self._shell(f'input swipe {x1} {y1} {x2} {y2} {duration}')
            return {"status": "success", "message": "Swiped"}
        except Exception as e:
            logger.error(f"❌ Swipe failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def type_text(self, text: str) -> Dict[str, Any]:
        """
        Type text using keyboard.
        
        Args:
            text: Text to type
            
        Returns:
            Result dictionary
        """
        logger.info(f"⌨️ Typing: {text}")
        
        try:
            # Escape special characters
            text = text.replace(' ', '%s')
            text = text.replace('&', '\\&')
            text = text.replace('(', '\\(')
            text = text.replace(')', '\\)')
            
            self._shell(f'input text "{text}"')
            return {"status": "success", "message": f"Typed: {text}"}
        except Exception as e:
            logger.error(f"❌ Type failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def press_back(self) -> Dict[str, Any]:
        """Press back button"""
        logger.info("⬅️ Pressing back")
        try:
            self._shell('input keyevent 4')
            return {"status": "success", "message": "Back pressed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def press_home(self) -> Dict[str, Any]:
        """Press home button"""
        logger.info("🏠 Pressing home")
        try:
            self._shell('input keyevent 3')
            return {"status": "success", "message": "Home pressed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def press_enter(self) -> Dict[str, Any]:
        """Press enter key"""
        try:
            self._shell('input keyevent 66')
            return {"status": "success", "message": "Enter pressed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def scroll_down(self) -> Dict[str, Any]:
        """Scroll down"""
        logger.info("📜 Scrolling down")
        # Get screen size
        size = self._shell('wm size')
        if 'x' in size:
            try:
                width, height = map(int, size.split(':')[-1].strip().split('x'))
                cx, cy = width // 2, height // 2
                return self.swipe(cx, cy + 300, cx, cy - 300, 300)
            except:
                pass
        # Fallback
        return self.swipe(540, 1500, 540, 500, 300)

    def scroll_up(self) -> Dict[str, Any]:
        """Scroll up"""
        logger.info("📜 Scrolling up")
        size = self._shell('wm size')
        if 'x' in size:
            try:
                width, height = map(int, size.split(':')[-1].strip().split('x'))
                cx, cy = width // 2, height // 2
                return self.swipe(cx, cy - 300, cx, cy + 300, 300)
            except:
                pass
        return self.swipe(540, 500, 540, 1500, 300)

    def call_number(self, phone_number: str) -> Dict[str, Any]:
        """Make phone call"""
        logger.info(f"📞 Calling {phone_number}")
        try:
            self._shell(f'am start -a android.intent.action.CALL -d tel:{phone_number}')
            return {"status": "success", "message": f"Calling {phone_number}"}
        except Exception as e:
            logger.error(f"❌ Call failed: {e}")
            return {"status": "error", "message": str(e)}

    def send_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send SMS"""
        logger.info(f"💬 Sending SMS to {phone_number}")
        try:
            # Open messaging app with number and message
            message_escaped = message.replace(' ', '%s')
            self._shell(f'am start -a android.intent.action.SENDTO -d sms:{phone_number} --es sms_body "{message_escaped}"')
            time.sleep(1)
            # Press send button (usually at bottom right)
            size = self._shell('wm size')
            if 'x' in size:
                width, height = map(int, size.split(':')[-1].strip().split('x'))
                self.tap(width - 100, height - 100)
            return {"status": "success", "message": "SMS sent"}
        except Exception as e:
            logger.error(f"❌ SMS failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_screen_size(self) -> tuple:
        """Get screen dimensions"""
        try:
            size = self._shell('wm size')
            if 'x' in size:
                width, height = map(int, size.split(':')[-1].strip().split('x'))
                return (width, height)
        except:
            pass
        return (1080, 2400)  # Default

    def take_screenshot(self, save_path: str = '/sdcard/screenshot.png') -> Dict[str, Any]:
        """Take screenshot"""
        logger.info("📸 Taking screenshot")
        try:
            self._shell(f'screencap -p {save_path}')
            return {"status": "success", "message": "Screenshot taken", "path": save_path}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_current_app(self) -> str:
        """Get current foreground app package"""
        try:
            output = self._shell('dumpsys window | grep mCurrentFocus')
            if output:
                # Extract package name
                parts = output.split()
                for part in parts:
                    if '/' in part:
                        package = part.split('/')[0]
                        return package
        except:
            pass
        return ""

    def set_volume(self, level: int) -> Dict[str, Any]:
        """Set media volume (0-15)"""
        logger.info(f"🔊 Setting volume to {level}")
        try:
            level = max(0, min(15, level))
            self._shell(f'media volume --stream 3 --set {level}')
            return {"status": "success", "message": f"Volume set to {level}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def set_brightness(self, level: int) -> Dict[str, Any]:
        """Set screen brightness (0-255)"""
        logger.info(f"💡 Setting brightness to {level}")
        try:
            level = max(0, min(255, level))
            self._shell(f'settings put system screen_brightness {level}')
            return {"status": "success", "message": f"Brightness set to {level}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def read_screen_text(self) -> Dict[str, Any]:
        """Read screen text using UI dump"""
        logger.info("📖 Reading screen text")
        try:
            # Dump UI hierarchy
            self._shell('uiautomator dump /sdcard/window_dump.xml')
            xml = self._shell('cat /sdcard/window_dump.xml')

            # Extract text from XML
            import re
            texts = re.findall(r'text="([^"]+)"', xml)
            texts = [t for t in texts if t.strip() and t != 'null' and len(t) > 0]

            if texts:
                screen_text = ' '.join(texts[:30])  # First 30 text elements
                logger.info(f"📄 Screen text: {screen_text[:100]}...")
                return {
                    "status": "success",
                    "message": "Screen read",
                    "data": {"text": screen_text, "elements": texts}
                }
            else:
                return {
                    "status": "success",
                    "message": "No text on screen",
                    "data": {"text": "", "elements": []}
                }
        except Exception as e:
            logger.error(f"❌ Screen read failed: {e}")
            return {"status": "error", "message": str(e)}

    def open_notification_shade(self) -> Dict[str, Any]:
        """Open notification shade"""
        logger.info("🔔 Opening notifications")
        try:
            self._shell('cmd statusbar expand-notifications')
            return {"status": "success", "message": "Notifications opened"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def close_notification_shade(self) -> Dict[str, Any]:
        """Close notification shade"""
        try:
            self._shell('cmd statusbar collapse')
            return {"status": "success", "message": "Notifications closed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

