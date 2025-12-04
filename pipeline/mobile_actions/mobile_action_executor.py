"""
Mobile Action Executor for VAANI Accessibility Assistant

Routes accessibility intents to appropriate Android/iOS actions.
"""

import logging
from typing import Dict, Any, Optional
from .android_bridge import AndroidBridge, ANDROID_APP_PACKAGES

logger = logging.getLogger(__name__)


class MobileActionExecutor:
    """Execute mobile accessibility actions"""
    
    def __init__(self, platform='android', mode='adb'):
        """
        Initialize mobile action executor.
        
        Args:
            platform: 'android' or 'ios'
            mode: Connection mode for bridge
        """
        self.platform = platform
        self.action_history = []
        
        if platform == 'android':
            self.bridge = AndroidBridge(mode=mode)
            logger.info("Mobile action executor initialized for Android")
        else:
            self.bridge = None
            logger.warning("iOS not yet supported")
    
    def execute(self, intent: str, entities: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute mobile action based on intent and entities.
        
        Args:
            intent: Action intent (e.g., 'OPEN_APP', 'TAP_UI_ELEMENT')
            entities: Extracted entities
            context: Additional context
            
        Returns:
            Result dictionary with status and message
        """
        if not self.bridge:
            return {"status": "error", "message": f"{self.platform} not supported yet"}
        
        # Route to appropriate handler
        handler = self._get_handler(intent)
        if not handler:
            return {"status": "error", "message": f"No handler for intent: {intent}"}
        
        try:
            result = handler(entities, context or {})
            
            # Log action
            self.action_history.append({
                "intent": intent,
                "entities": entities,
                "result": result
            })
            
            # Keep only last 100 actions
            if len(self.action_history) > 100:
                self.action_history = self.action_history[-100:]
            
            return result
        
        except Exception as e:
            logger.error(f"Action execution failed: {e}", exc_info=True)
            return {"status": "error", "message": f"Execution failed: {str(e)}"}
    
    def _get_handler(self, intent: str):
        """Get handler function for intent"""
        handlers = {
            'OPEN_APP': self._open_app,
            'CLOSE_APP': self._close_app,
            'CALL_CONTACT': self._call_contact,
            'SEND_MESSAGE': self._send_message,
            'TYPE_TEXT': self._type_text,
            'DICTATE_PARAGRAPH': self._type_text,
            'TAP_UI_ELEMENT': self._tap_element,
            'SWIPE_GESTURE': self._swipe,
            'SCROLL_PAGE': self._scroll,
            'READ_SCREEN': self._read_screen,
            'READ_NOTIFICATIONS': self._read_notifications,
            'PLAY_MUSIC': self._play_music,
            'TAKE_PHOTO': self._take_photo,
            'RECORD_VIDEO': self._record_video,
            'SYSTEM_VOLUME': self._set_volume,
            'VOLUME_UP': lambda e, c: self._adjust_volume('up', e, c),
            'VOLUME_DOWN': lambda e, c: self._adjust_volume('down', e, c),
            'SYSTEM_BRIGHTNESS': self._set_brightness,
            'BRIGHTNESS_UP': lambda e, c: self._adjust_brightness('up', e, c),
            'BRIGHTNESS_DOWN': lambda e, c: self._adjust_brightness('down', e, c),
            'GO_BACK': lambda e, c: self.bridge.go_back(),
            'GO_HOME': lambda e, c: self.bridge.go_home(),
            'EMERGENCY_SOS': lambda e, c: self.bridge.emergency_sos(),
        }
        return handlers.get(intent)
    
    def _open_app(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Open mobile app"""
        app_name = entities.get('app', '').lower()
        
        if not app_name:
            return {"status": "error", "message": "No app specified"}
        
        # Get package name
        package = ANDROID_APP_PACKAGES.get(app_name)
        if not package:
            # Try direct package name
            package = app_name
        
        return self.bridge.open_app(package)
    
    def _close_app(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Close current app"""
        # Go home to close app
        return self.bridge.go_home()
    
    def _call_contact(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Make phone call"""
        contact = entities.get('contact', entities.get('person', ''))
        phone = entities.get('phone_number', '')
        
        if not phone and not contact:
            return {"status": "error", "message": "No contact or phone number specified"}
        
        # TODO: Resolve contact name to phone number from contacts
        # For now, use phone number directly
        if phone:
            return self.bridge.call_contact(phone)
        else:
            return {"status": "error", "message": f"Cannot resolve contact: {contact}"}
    
    def _send_message(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Send SMS message"""
        contact = entities.get('contact', entities.get('person', ''))
        message = entities.get('message', entities.get('text', ''))
        phone = entities.get('phone_number', '')
        
        if not message:
            return {"status": "error", "message": "No message text specified"}
        
        if not phone and not contact:
            return {"status": "error", "message": "No recipient specified"}
        
        # TODO: Resolve contact to phone number
        if phone:
            return self.bridge.send_sms(phone, message)
        else:
            return {"status": "error", "message": f"Cannot resolve contact: {contact}"}

    def _type_text(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Type text via keyboard"""
        text = entities.get('text', entities.get('message', ''))

        if not text:
            return {"status": "error", "message": "No text to type"}

        return self.bridge.type_text(text)

    def _tap_element(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Tap UI element"""
        x = entities.get('x', 540)  # Default center
        y = entities.get('y', 1200)

        # TODO: Use OCR/UI analysis to find element by name
        element = entities.get('element', '')
        if element:
            # For now, tap center
            logger.warning(f"Element detection not implemented, tapping center for: {element}")

        return self.bridge.tap(x, y)

    def _swipe(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Perform swipe gesture"""
        direction = entities.get('direction', 'left')

        # Default swipe coordinates (center of screen)
        if direction == 'left':
            return self.bridge.swipe(800, 1200, 200, 1200)
        elif direction == 'right':
            return self.bridge.swipe(200, 1200, 800, 1200)
        elif direction == 'up':
            return self.bridge.swipe(540, 1500, 540, 500)
        elif direction == 'down':
            return self.bridge.swipe(540, 500, 540, 1500)
        else:
            return {"status": "error", "message": f"Unknown direction: {direction}"}

    def _scroll(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Scroll page"""
        direction = entities.get('direction', 'down')
        return self.bridge.scroll(direction)

    def _read_screen(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Read screen content"""
        return self.bridge.read_screen()

    def _read_notifications(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Read notifications"""
        return self.bridge.read_notifications()

    def _play_music(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Play music"""
        # Open music app
        return self.bridge.open_app(ANDROID_APP_PACKAGES.get('spotify', 'com.spotify.music'))

    def _take_photo(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Take photo"""
        return self.bridge.take_photo()

    def _record_video(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Record video"""
        # Open camera in video mode
        self.bridge.open_app(ANDROID_APP_PACKAGES.get('camera', 'com.android.camera2'))
        return {"status": "success", "message": "Camera opened in video mode"}

    def _set_volume(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Set system volume"""
        level = entities.get('value', entities.get('level', 10))
        try:
            level = int(level)
        except:
            level = 10

        return self.bridge.set_volume(level)

    def _adjust_volume(self, direction: str, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Adjust volume up/down"""
        # Get current volume and adjust
        current = 10  # TODO: Get actual current volume
        if direction == 'up':
            new_level = min(15, current + 2)
        else:
            new_level = max(0, current - 2)

        return self.bridge.set_volume(new_level)

    def _set_brightness(self, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Set screen brightness"""
        level = entities.get('value', entities.get('level', 128))
        try:
            level = int(level)
        except:
            level = 128

        return self.bridge.set_brightness(level)

    def _adjust_brightness(self, direction: str, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Adjust brightness up/down"""
        current = 128  # TODO: Get actual current brightness
        if direction == 'up':
            new_level = min(255, current + 50)
        else:
            new_level = max(0, current - 50)

        return self.bridge.set_brightness(new_level)


