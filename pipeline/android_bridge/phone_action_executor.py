"""
Phone Action Executor
Routes VAANI intents to phone actions via ADB
"""

import logging
from typing import Dict, Any, Optional
from .adb_connection import ADBConnection
from .adb_actions import ADBActions
from .adb_audio_forward import ADBAudio

logger = logging.getLogger(__name__)


class PhoneActionExecutor:
    """Execute VAANI actions on Android phone"""
    
    def __init__(self):
        """Initialize phone action executor"""
        self.connection = ADBConnection()
        self.actions: Optional[ADBActions] = None
        self.audio: Optional[ADBAudio] = None
        self.connected = False
        
    def connect(self, device_id: Optional[str] = None) -> bool:
        """
        Connect to Android device.

        Args:
            device_id: Specific device ID or None for auto-detect

        Returns:
            True if connected successfully
        """
        if self.connection.connect(device_id):
            self.actions = ADBActions(self.connection.device_id, self.connection.adb_path)
            self.audio = ADBAudio(self.connection.device_id, self.connection.adb_path)
            self.connected = True
            logger.info("✅ Phone action executor ready")
            return True
        return False
    
    def execute(self, intent: str, entities: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute action based on intent.
        
        Args:
            intent: NLU intent
            entities: Extracted entities
            context: Optional context
            
        Returns:
            Result dictionary
        """
        if not self.connected or not self.actions:
            return {"status": "error", "message": "Phone not connected"}
        
        logger.info(f"🎯 Executing on phone: {intent}")
        
        # Route intent to action
        handler = self._get_handler(intent)
        
        if handler:
            try:
                result = handler(entities, context or {})
                logger.info(f"✅ Action result: {result.get('status')}")
                return result
            except Exception as e:
                logger.error(f"❌ Action failed: {e}", exc_info=True)
                return {"status": "error", "message": str(e)}
        else:
            logger.warning(f"⚠️ No handler for intent: {intent}")
            return {"status": "error", "message": f"No handler for intent: {intent}"}
    
    def _get_handler(self, intent: str):
        """Get handler function for intent"""
        handlers = {
            # App control
            'OPEN_APP': self._open_app,
            'CLOSE_APP': self._close_app,
            
            # Communication
            'CALL_CONTACT': self._call_contact,
            'SEND_MESSAGE': self._send_message,
            
            # Text input
            'TYPE_TEXT': self._type_text,
            'DICTATE_PARAGRAPH': self._type_text,
            
            # Gestures
            'TAP_UI_ELEMENT': self._tap_element,
            'SWIPE_GESTURE': self._swipe,
            'SCROLL_PAGE': self._scroll,
            
            # Screen reading
            'READ_SCREEN': self._read_screen,
            'READ_NOTIFICATIONS': self._read_notifications,
            
            # Media
            'PLAY_MUSIC': self._play_music,
            'TAKE_PHOTO': self._take_photo,
            
            # System control
            'SYSTEM_VOLUME': self._set_volume,
            'VOLUME_UP': self._volume_up,
            'VOLUME_DOWN': self._volume_down,
            'BRIGHTNESS_UP': self._brightness_up,
            'BRIGHTNESS_DOWN': self._brightness_down,
            
            # Navigation
            'GO_BACK': lambda e, c: self.actions.press_back(),
            'GO_HOME': lambda e, c: self.actions.press_home(),
            
            # Emergency
            'EMERGENCY_SOS': self._emergency_sos,
        }
        
        return handlers.get(intent)
    
    def _open_app(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Open app on phone"""
        app = entities.get('app', entities.get('application', ''))
        if not app:
            return {"status": "error", "message": "No app specified"}
        
        logger.info(f"📱 Opening app: {app}")
        return self.actions.open_app(app)
    
    def _close_app(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Close current app"""
        return self.actions.press_home()
    
    def _call_contact(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Make phone call"""
        phone = entities.get('phone_number', entities.get('contact', ''))
        if not phone:
            return {"status": "error", "message": "No phone number specified"}
        
        logger.info(f"📞 Calling: {phone}")
        return self.actions.call_number(phone)
    
    def _send_message(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Send SMS"""
        phone = entities.get('phone_number', entities.get('contact', ''))
        message = entities.get('message', entities.get('text', ''))

        if not phone or not message:
            return {"status": "error", "message": "Missing phone number or message"}

        logger.info(f"💬 Sending SMS to {phone}: {message}")
        return self.actions.send_sms(phone, message)

    def _type_text(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Type text on phone"""
        text = entities.get('text', entities.get('message', ''))
        if not text:
            return {"status": "error", "message": "No text specified"}

        logger.info(f"⌨️ Typing: {text}")
        return self.actions.type_text(text)

    def _tap_element(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Tap UI element"""
        x = entities.get('x', 540)
        y = entities.get('y', 1200)

        element = entities.get('element', '')
        if element:
            logger.info(f"👆 Tapping element: {element}")
            # For now, tap center - full implementation would use OCR
            logger.warning("Element detection not implemented, tapping center")

        return self.actions.tap(x, y)

    def _swipe(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Perform swipe gesture"""
        direction = entities.get('direction', 'down').lower()

        width, height = self.actions.get_screen_size()
        cx, cy = width // 2, height // 2

        if direction == 'down':
            return self.actions.swipe(cx, cy + 300, cx, cy - 300)
        elif direction == 'up':
            return self.actions.swipe(cx, cy - 300, cx, cy + 300)
        elif direction == 'left':
            return self.actions.swipe(cx + 300, cy, cx - 300, cy)
        elif direction == 'right':
            return self.actions.swipe(cx - 300, cy, cx + 300, cy)
        else:
            return {"status": "error", "message": f"Unknown direction: {direction}"}

    def _scroll(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Scroll page"""
        direction = entities.get('direction', 'down').lower()

        if direction == 'down':
            return self.actions.scroll_down()
        elif direction == 'up':
            return self.actions.scroll_up()
        else:
            return {"status": "error", "message": f"Unknown direction: {direction}"}

    def _read_screen(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Read screen text"""
        logger.info("📖 Reading screen")
        result = self.actions.read_screen_text()

        # Speak the text
        if result.get('status') == 'success' and result.get('data', {}).get('text'):
            text = result['data']['text']
            logger.info(f"📄 Screen text: {text[:100]}...")

        return result

    def _read_notifications(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Read notifications"""
        logger.info("🔔 Reading notifications")

        # Open notification shade
        self.actions.open_notification_shade()

        # Read screen text
        import time
        time.sleep(1)
        result = self.actions.read_screen_text()

        # Close notification shade
        self.actions.close_notification_shade()

        return result

    def _play_music(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Play music"""
        song = entities.get('song', entities.get('music', ''))

        # Open music app (Spotify by default)
        result = self.actions.open_app('spotify')

        if song:
            logger.info(f"🎵 Playing: {song}")
            # Would need to search and play - simplified for now

        return result

    def _take_photo(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Take photo"""
        logger.info("📸 Taking photo")

        # Open camera
        result = self.actions.open_app('camera')

        # Wait and tap shutter button (usually center bottom)
        import time
        time.sleep(2)

        width, height = self.actions.get_screen_size()
        self.actions.tap(width // 2, height - 200)

        return result

    def _set_volume(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Set volume level"""
        level = entities.get('level', 10)
        return self.actions.set_volume(level)

    def _volume_up(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Increase volume"""
        logger.info("🔊 Volume up")
        # Get current volume and increase
        return self.actions.set_volume(12)  # Simplified

    def _volume_down(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Decrease volume"""
        logger.info("🔉 Volume down")
        return self.actions.set_volume(5)  # Simplified

    def _brightness_up(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Increase brightness"""
        logger.info("💡 Brightness up")
        return self.actions.set_brightness(200)

    def _brightness_down(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Decrease brightness"""
        logger.info("🌙 Brightness down")
        return self.actions.set_brightness(50)

    def _emergency_sos(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Emergency SOS"""
        logger.info("🚨 EMERGENCY SOS")

        # Call emergency number (911 in US, 112 in India)
        emergency_number = entities.get('emergency_number', '112')

        return self.actions.call_number(emergency_number)

    def speak_on_phone(self, text: str) -> bool:
        """
        Speak text on phone speaker.

        Args:
            text: Text to speak

        Returns:
            True if successful
        """
        if self.audio:
            return self.audio.speak_on_phone(text)
        return False

    def disconnect(self):
        """Disconnect from phone"""
        if self.connection:
            self.connection.disconnect()
        self.connected = False

