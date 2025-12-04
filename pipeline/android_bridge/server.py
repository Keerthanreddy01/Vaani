"""
Android Bridge Server
WebSocket/HTTP server for phone ↔ laptop communication
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, Callable
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

logger = logging.getLogger(__name__)


class AndroidBridgeHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Android bridge"""
    
    # Class variable to store message handler
    message_handler: Optional[Callable] = None
    
    def do_POST(self):
        """Handle POST requests from phone"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            
            # Parse JSON
            data = json.loads(body.decode('utf-8'))
            
            logger.info(f"📱 Received from phone: {data.get('type', 'unknown')}")
            
            # Process message
            response = {"status": "success"}
            
            if self.message_handler:
                response = self.message_handler(data)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"❌ Request handling failed: {e}")
            self.send_response(500)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


class AndroidBridgeServer:
    """Server for phone ↔ laptop communication"""
    
    def __init__(self, port: int = 8765):
        """
        Initialize server.
        
        Args:
            port: Server port
        """
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.running = False
        self.message_handler: Optional[Callable] = None
        
    def set_message_handler(self, handler: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """
        Set handler for messages from phone.
        
        Args:
            handler: Function to process messages
        """
        self.message_handler = handler
        AndroidBridgeHandler.message_handler = handler
    
    def start(self) -> bool:
        """
        Start server.
        
        Returns:
            True if started successfully
        """
        try:
            logger.info(f"🌐 Starting Android Bridge Server on port {self.port}...")
            
            # Create server
            self.server = HTTPServer(('localhost', self.port), AndroidBridgeHandler)
            
            # Start server thread
            self.running = True
            self.server_thread = threading.Thread(
                target=self._run_server,
                daemon=True
            )
            self.server_thread.start()
            
            logger.info(f"✅ Server running on http://localhost:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Server start failed: {e}")
            return False
    
    def _run_server(self):
        """Run server loop"""
        try:
            while self.running:
                self.server.handle_request()
        except Exception as e:
            logger.error(f"Server error: {e}")
    
    def stop(self):
        """Stop server"""
        logger.info("Stopping server...")
        self.running = False
        
        if self.server:
            self.server.shutdown()
            self.server = None
        
        if self.server_thread:
            self.server_thread.join(timeout=2)
        
        logger.info("✅ Server stopped")
    
    def send_to_phone(self, message: Dict[str, Any]) -> bool:
        """
        Send message to phone.
        
        Note: This requires the phone app to poll or use WebSocket.
        For now, we use direct ADB commands instead.
        
        Args:
            message: Message to send
            
        Returns:
            True if sent successfully
        """
        logger.info(f"📤 Sending to phone: {message.get('type', 'unknown')}")
        
        # For now, messages are sent via ADB actions directly
        # In a full implementation, this would use WebSocket or push notifications
        
        return True


class PhoneMessageQueue:
    """Queue for messages between phone and laptop"""
    
    def __init__(self):
        self.screen_text_queue = []
        self.action_queue = []
        self.lock = threading.Lock()
    
    def add_screen_text(self, text: str):
        """Add screen text from phone"""
        with self.lock:
            self.screen_text_queue.append(text)
            logger.info(f"📄 Screen text queued: {text[:50]}...")
    
    def get_screen_text(self) -> Optional[str]:
        """Get latest screen text"""
        with self.lock:
            if self.screen_text_queue:
                return self.screen_text_queue.pop(0)
        return None
    
    def add_action(self, action: Dict[str, Any]):
        """Add action to execute on phone"""
        with self.lock:
            self.action_queue.append(action)
            logger.info(f"🎯 Action queued: {action.get('type', 'unknown')}")
    
    def get_action(self) -> Optional[Dict[str, Any]]:
        """Get next action to execute"""
        with self.lock:
            if self.action_queue:
                return self.action_queue.pop(0)
        return None

