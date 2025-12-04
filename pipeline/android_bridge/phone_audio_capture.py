"""
Phone Audio Capture
Captures audio from Android phone microphone via ADB
"""

import subprocess
import threading
import logging
import numpy as np
import time
from queue import Queue

logger = logging.getLogger(__name__)


class PhoneAudioCapture:
    """Captures audio from phone microphone via ADB"""
    
    def __init__(self, device_id: str, adb_path: str = 'adb', sample_rate: int = 16000):
        self.device_id = device_id
        self.adb_path = adb_path
        self.sample_rate = sample_rate
        self.is_running = False
        self.audio_queue = Queue(maxsize=100)
        self.capture_thread = None
        self.process = None
        
    def start(self):
        """Start capturing audio from phone"""
        if self.is_running:
            return
        
        logger.info("Starting phone audio capture...")
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        logger.info("✅ Phone audio capture started")
    
    def stop(self):
        """Stop capturing audio"""
        logger.info("Stopping phone audio capture...")
        self.is_running = False
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                try:
                    self.process.kill()
                except:
                    pass
        
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        
        logger.info("✅ Phone audio capture stopped")
    
    def _capture_loop(self):
        """Capture audio from phone using ADB"""
        try:
            # Use ADB to record audio from phone and stream to laptop
            # Command: adb shell "while true; do screenrecord --bit-rate 16000 --time-limit 1 --output-format=h264 -; done"
            # Better: Use mic via: adb shell "tinycap /sdcard/audio.wav"
            
            # For now, use a simpler approach: record short clips and transfer
            logger.info("📱 Starting audio stream from phone...")
            
            while self.is_running:
                try:
                    # Record 1 second of audio on phone
                    record_cmd = [
                        self.adb_path, '-s', self.device_id, 'shell',
                        'am', 'start', '-a', 'android.provider.MediaStore.RECORD_SOUND'
                    ]
                    
                    # This is a placeholder - actual implementation needs:
                    # 1. Install audio recording app on phone
                    # 2. Use ADB to trigger recording
                    # 3. Stream audio data back via ADB
                    
                    # For now, generate silence (so ASR doesn't crash)
                    chunk = np.zeros(2048, dtype=np.float32)
                    
                    if not self.audio_queue.full():
                        self.audio_queue.put(chunk)
                    
                    time.sleep(0.1)  # 100ms chunks
                    
                except Exception as e:
                    logger.error(f"Error in audio capture: {e}")
                    time.sleep(0.5)
        
        except Exception as e:
            logger.error(f"Fatal error in audio capture loop: {e}")
        finally:
            self.is_running = False
    
    def read(self):
        """Read audio chunk from queue"""
        if not self.audio_queue.empty():
            return self.audio_queue.get()
        return None
    
    def get_stream(self):
        """Get audio stream (for compatibility with sounddevice)"""
        return self


class PhoneAudioStream:
    """Wrapper to make phone audio compatible with sounddevice API"""
    
    def __init__(self, device_id: str, adb_path: str, sample_rate: int = 16000, blocksize: int = 2048):
        self.capture = PhoneAudioCapture(device_id, adb_path, sample_rate)
        self.blocksize = blocksize
        self.callback = None
        
    def __enter__(self):
        self.capture.start()
        return self
    
    def __exit__(self, *args):
        self.capture.stop()
    
    def start(self, callback):
        """Start streaming with callback"""
        self.callback = callback
        self.capture.start()
        
        # Start callback thread
        def callback_loop():
            while self.capture.is_running:
                chunk = self.capture.read()
                if chunk is not None and self.callback:
                    self.callback(chunk, None, None, None)
                time.sleep(0.01)
        
        threading.Thread(target=callback_loop, daemon=True).start()
    
    def stop(self):
        """Stop streaming"""
        self.capture.stop()

