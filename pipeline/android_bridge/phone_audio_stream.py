"""
Phone Audio Stream
Receives audio from Android phone microphone via socket connection
Requires VAANI Mic Service app running on phone
"""

import subprocess
import threading
import logging
import numpy as np
import time
import socket
import struct
from queue import Queue

logger = logging.getLogger(__name__)


class PhoneAudioStream:
    """Receives audio stream from phone microphone via socket"""

    def __init__(self, device_id: str, adb_path: str = 'adb', sample_rate: int = 16000, port: int = 8888):
        self.device_id = device_id
        self.adb_path = adb_path
        self.sample_rate = sample_rate
        self.port = port
        self.is_running = False
        self.audio_queue = Queue(maxsize=100)
        self.receive_thread = None
        self.socket = None
        self.callback = None
        
    def start(self, callback=None):
        """Start receiving audio from phone microphone"""
        if self.is_running:
            return

        self.callback = callback

        logger.info("📱 Connecting to phone microphone...")

        # Forward port from phone to laptop
        try:
            subprocess.run(
                [self.adb_path, '-s', self.device_id, 'forward', f'tcp:{self.port}', f'tcp:{self.port}'],
                capture_output=True,
                timeout=5
            )
            logger.info(f"✅ Port forwarding: localhost:{self.port}")
        except Exception as e:
            logger.error(f"Port forwarding failed: {e}")
            return False

        self.is_running = True

        # Start receive thread
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()

        logger.info("✅ Phone microphone active")
        return True
    
    def stop(self):
        """Stop receiving audio"""
        logger.info("Stopping phone microphone...")
        self.is_running = False

        if self.socket:
            try:
                self.socket.close()
            except:
                pass

        if self.receive_thread:
            self.receive_thread.join(timeout=2)

        logger.info("✅ Phone microphone stopped")
    
    def _receive_loop(self):
        """Receive audio stream from phone"""
        try:
            # Connect to phone
            logger.info(f"Connecting to phone on port {self.port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect(('localhost', self.port))
            logger.info("✅ Connected to phone microphone")

            # Receive audio data
            chunk_size = 2048  # bytes
            while self.is_running:
                try:
                    data = self.socket.recv(chunk_size)
                    if not data:
                        logger.warning("Connection closed by phone")
                        break

                    # Convert bytes to float32 audio
                    audio_int16 = np.frombuffer(data, dtype=np.int16)
                    audio_float32 = audio_int16.astype(np.float32) / 32768.0

                    # Add to queue
                    if not self.audio_queue.full():
                        self.audio_queue.put(audio_float32)

                    # Call callback if provided
                    if self.callback:
                        self.callback(audio_float32, None, None, None)

                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"Receive error: {e}")
                    break

        except Exception as e:
            logger.error(f"Connection error: {e}")
            logger.error("Make sure VAANI Mic Service app is running on phone!")
        finally:
            self.is_running = False
            if self.socket:
                self.socket.close()
    
    def read(self):
        """Read audio chunk from queue"""
        if not self.audio_queue.empty():
            return self.audio_queue.get()
        return None

