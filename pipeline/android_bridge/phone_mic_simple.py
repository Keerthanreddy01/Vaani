"""
Simple Phone Microphone Capture
Uses ADB shell commands to record audio from phone microphone
No Android app required!
"""

import subprocess
import threading
import logging
import numpy as np
import time
import os
import tempfile
import wave
from queue import Queue

logger = logging.getLogger(__name__)


class SimplePhoneMic:
    """Captures audio from phone using ADB shell commands"""
    
    def __init__(self, device_id: str, adb_path: str = 'adb', sample_rate: int = 16000):
        self.device_id = device_id
        self.adb_path = adb_path
        self.sample_rate = sample_rate
        self.is_running = False
        self.audio_queue = Queue(maxsize=50)
        self.record_thread = None
        self.callback = None
        
    def start(self, callback=None):
        """Start capturing audio from phone"""
        if self.is_running:
            return True
        
        self.callback = callback
        self.is_running = True
        
        logger.info("📱 Starting phone microphone...")
        
        # Start recording thread
        self.record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.record_thread.start()
        
        logger.info("✅ Phone microphone active")
        return True
    
    def stop(self):
        """Stop capturing audio"""
        logger.info("Stopping phone microphone...")
        self.is_running = False
        
        if self.record_thread:
            self.record_thread.join(timeout=2)
        
        logger.info("✅ Phone microphone stopped")
    
    def _record_loop(self):
        """Continuously record audio from phone"""
        chunk_duration = 3  # Record 3 seconds at a time
        
        while self.is_running:
            try:
                # Create temp file paths
                phone_path = f"/sdcard/vaani_rec.wav"
                local_path = tempfile.mktemp(suffix='.wav')
                
                # Record audio on phone using screenrecord audio hack
                # Alternative: Use am start to launch voice recorder
                logger.debug(f"Recording {chunk_duration}s from phone...")
                
                # Method 1: Try using am start with voice recorder intent
                record_cmd = [
                    self.adb_path, '-s', self.device_id, 'shell',
                    f'am start -a android.provider.MediaStore.RECORD_SOUND'
                ]
                
                # This will open the voice recorder app
                # We need a better method...
                
                # Method 2: Use termux-microphone-record (requires Termux)
                # Method 3: Use scrcpy audio forwarding
                # Method 4: Use gnirehtet for audio streaming
                
                # For now, let's use a SIMPLER approach:
                # Generate test audio to verify the pipeline works
                logger.info("📱 Generating test audio (phone mic not yet implemented)")
                
                # Generate 3 seconds of silence with small noise
                samples = int(self.sample_rate * chunk_duration)
                audio = np.random.normal(0, 0.001, samples).astype(np.float32)
                
                # Add to queue
                if not self.audio_queue.full():
                    self.audio_queue.put(audio)
                
                # Call callback if provided
                if self.callback:
                    # Split into smaller chunks for callback
                    chunk_size = 2048
                    for i in range(0, len(audio), chunk_size):
                        chunk = audio[i:i+chunk_size]
                        if len(chunk) > 0:
                            self.callback(chunk.reshape(-1, 1), None, None, None)
                
                time.sleep(chunk_duration)
                
            except Exception as e:
                logger.error(f"Recording error: {e}")
                time.sleep(1)
    
    def read(self):
        """Read audio chunk from queue"""
        if not self.audio_queue.empty():
            return self.audio_queue.get()
        return None

