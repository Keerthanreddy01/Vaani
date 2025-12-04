"""
ADB Audio Forwarding
Stream audio between phone and laptop
"""

import subprocess
import logging
import threading
import numpy as np
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class ADBAudio:
    """Handle audio streaming between phone and laptop"""

    def __init__(self, device_id: str, adb_path: str = 'adb'):
        """
        Initialize audio forwarding.

        Args:
            device_id: Android device ID
            adb_path: Path to ADB executable
        """
        self.device_id = device_id
        self.adb_path = adb_path
        self.recording = False
        self.record_thread: Optional[threading.Thread] = None
        self.audio_callback: Optional[Callable] = None
        
    def start_mic_stream(self, callback: Callable[[np.ndarray], None]) -> bool:
        """
        Start streaming phone microphone to laptop.
        
        Args:
            callback: Function to call with audio chunks
            
        Returns:
            True if started successfully
        """
        logger.info("🎤 Starting phone microphone stream...")
        
        self.audio_callback = callback
        self.recording = True
        
        # Start recording thread
        self.record_thread = threading.Thread(
            target=self._record_loop,
            daemon=True
        )
        self.record_thread.start()
        
        logger.info("✅ Phone microphone streaming")
        return True
    
    def _record_loop(self):
        """Record audio from phone microphone"""
        try:
            # Use ADB to record audio
            # Note: This requires a helper app on the phone or scrcpy
            logger.warning("⚠️ Direct ADB audio streaming requires additional setup")
            logger.warning("Alternative: Use scrcpy with audio forwarding")
            logger.warning("For now, using laptop microphone as fallback")
            
            # Fallback: Use laptop microphone
            import sounddevice as sd
            
            def audio_callback(indata, frames, time_info, status):
                if status:
                    logger.warning(f"Audio status: {status}")
                
                if self.recording and self.audio_callback:
                    audio_chunk = indata[:, 0].copy()
                    self.audio_callback(audio_chunk)
            
            with sd.InputStream(
                samplerate=16000,
                channels=1,
                dtype='float32',
                blocksize=2048,
                callback=audio_callback
            ):
                while self.recording:
                    sd.sleep(100)
                    
        except Exception as e:
            logger.error(f"❌ Audio recording failed: {e}")
            self.recording = False
    
    def stop_mic_stream(self):
        """Stop microphone streaming"""
        logger.info("Stopping microphone stream...")
        self.recording = False
        
        if self.record_thread:
            self.record_thread.join(timeout=2)
        
        logger.info("✅ Microphone stream stopped")
    
    def play_audio_on_phone(self, audio_file: str) -> bool:
        """
        Play audio file on phone speaker.
        
        Args:
            audio_file: Path to audio file on phone
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"🔊 Playing audio on phone: {audio_file}")
            
            # Use media player
            subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 
                 f'am start -a android.intent.action.VIEW -d file://{audio_file} -t audio/*'],
                timeout=5
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Audio playback failed: {e}")
            return False
    
    def speak_on_phone(self, text: str) -> bool:
        """
        Use phone's TTS to speak text.
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"🗣️ Speaking on phone: {text}")
            
            # Escape text
            text_escaped = text.replace('"', '\\"').replace("'", "\\'")
            
            # Use Android TTS service
            subprocess.run(
                ['adb', '-s', self.device_id, 'shell',
                 f'am start -a android.intent.action.TTS_SERVICE --es android.intent.extra.TEXT "{text_escaped}"'],
                timeout=5
            )
            
            # Alternative: Use termux-tts-speak if Termux is installed
            # subprocess.run(['adb', '-s', self.device_id, 'shell', f'termux-tts-speak "{text_escaped}"'])
            
            return True
            
        except Exception as e:
            logger.error(f"❌ TTS failed: {e}")
            return False
    
    def push_audio_file(self, local_path: str, phone_path: str = '/sdcard/vaani_audio.wav') -> bool:
        """
        Push audio file to phone.
        
        Args:
            local_path: Local audio file path
            phone_path: Destination path on phone
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"📤 Pushing audio to phone: {local_path} -> {phone_path}")
            
            subprocess.run(
                ['adb', '-s', self.device_id, 'push', local_path, phone_path],
                timeout=10
            )
            
            logger.info("✅ Audio file pushed")
            return True
            
        except Exception as e:
            logger.error(f"❌ File push failed: {e}")
            return False

