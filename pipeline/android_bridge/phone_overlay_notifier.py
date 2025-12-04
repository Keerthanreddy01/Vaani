"""
Phone Overlay Notifier
Sends status updates to Android overlay via socket connection
"""

import socket
import logging
import subprocess
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)


class OverlayState(Enum):
    """Overlay status states"""
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    SPEAKING = "SPEAKING"
    ACTION_OK = "ACTION_OK"
    ACTION_FAILED = "ACTION_FAILED"
    IDLE = "IDLE"


class PhoneOverlayNotifier:
    """Sends status updates to phone overlay"""
    
    def __init__(self, device_id: str, adb_path: str = 'adb', port: int = 8766):
        self.device_id = device_id
        self.adb_path = adb_path
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to phone overlay service"""
        try:
            # Forward port from PC to phone
            result = subprocess.run(
                [self.adb_path, '-s', self.device_id, 'forward', f'tcp:{self.port}', f'tcp:{self.port}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to forward port: {result.stderr}")
                return False
            
            # Connect to forwarded port
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(2)
            self.socket.connect(('localhost', self.port))
            self.connected = True
            logger.info(f"✅ Connected to phone overlay on port {self.port}")
            return True
            
        except Exception as e:
            logger.warning(f"Could not connect to overlay: {e}")
            self.connected = False
            return False
    
    def send_state(self, state: OverlayState) -> bool:
        """Send state update to overlay"""
        if not self.connected:
            # Try to reconnect
            if not self.connect():
                return False
        
        try:
            message = f"{state.value}\n"
            self.socket.sendall(message.encode('utf-8'))
            return True
        except Exception as e:
            logger.warning(f"Failed to send overlay state: {e}")
            self.connected = False
            return False
    
    def listening(self):
        """Set overlay to listening state"""
        self.send_state(OverlayState.LISTENING)
    
    def processing(self):
        """Set overlay to processing state"""
        self.send_state(OverlayState.PROCESSING)
    
    def speaking(self):
        """Set overlay to speaking state"""
        self.send_state(OverlayState.SPEAKING)
    
    def action_ok(self):
        """Set overlay to action success state"""
        self.send_state(OverlayState.ACTION_OK)
    
    def action_failed(self):
        """Set overlay to action failed state"""
        self.send_state(OverlayState.ACTION_FAILED)
    
    def idle(self):
        """Set overlay to idle state"""
        self.send_state(OverlayState.IDLE)
    
    def disconnect(self):
        """Disconnect from overlay"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        logger.info("Disconnected from phone overlay")

