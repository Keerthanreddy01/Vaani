"""
Wake Word Detector for VAANI

Detects "Hey VAANI" or custom wake words.
"""

import logging
import numpy as np
from typing import Optional, Callable

logger = logging.getLogger(__name__)

# Try to import wake word libraries
try:
    import openwakeword
    from openwakeword.model import Model
    HAS_OPENWAKEWORD = True
except ImportError:
    HAS_OPENWAKEWORD = False
    logger.warning("openWakeWord not available. Install with: pip install openwakeword")

try:
    import pvporcupine
    HAS_PORCUPINE = False  # Requires API key
except ImportError:
    HAS_PORCUPINE = False


class WakeWordDetector:
    """Detect wake word in audio stream"""
    
    def __init__(self, wake_word='hey_vaani', engine='openwakeword', threshold=0.5):
        """
        Initialize wake word detector.
        
        Args:
            wake_word: Wake word to detect
            engine: 'openwakeword', 'porcupine', or 'energy'
            threshold: Detection threshold
        """
        self.wake_word = wake_word
        self.engine = engine
        self.threshold = threshold
        self.model = None
        
        if engine == 'openwakeword' and HAS_OPENWAKEWORD:
            self._init_openwakeword()
        elif engine == 'porcupine' and HAS_PORCUPINE:
            self._init_porcupine()
        else:
            logger.warning(f"Using energy-based wake word detection (fallback)")
            self.engine = 'energy'
    
    def _init_openwakeword(self):
        """Initialize openWakeWord"""
        try:
            # Load pre-trained model
            self.model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
            logger.info("openWakeWord initialized")
        except Exception as e:
            logger.error(f"Failed to initialize openWakeWord: {e}")
            self.engine = 'energy'
    
    def _init_porcupine(self):
        """Initialize Porcupine"""
        # Requires API key
        logger.warning("Porcupine requires API key. Using fallback.")
        self.engine = 'energy'
    
    def detect(self, audio_chunk: np.ndarray) -> bool:
        """
        Detect wake word in audio chunk.
        
        Args:
            audio_chunk: Audio data (float32, 16kHz)
            
        Returns:
            True if wake word detected
        """
        if self.engine == 'openwakeword' and self.model:
            return self._detect_openwakeword(audio_chunk)
        elif self.engine == 'porcupine':
            return self._detect_porcupine(audio_chunk)
        else:
            return self._detect_energy(audio_chunk)
    
    def _detect_openwakeword(self, audio_chunk: np.ndarray) -> bool:
        """Detect using openWakeWord"""
        try:
            # Convert to int16
            if audio_chunk.dtype == np.float32:
                audio_chunk = (audio_chunk * 32767).astype(np.int16)
            
            # Get prediction
            prediction = self.model.predict(audio_chunk)
            
            # Check if any wake word detected
            for key, score in prediction.items():
                if score > self.threshold:
                    logger.info(f"Wake word detected: {key} (score: {score:.2f})")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"openWakeWord detection failed: {e}")
            return False
    
    def _detect_porcupine(self, audio_chunk: np.ndarray) -> bool:
        """Detect using Porcupine"""
        # Not implemented
        return False
    
    def _detect_energy(self, audio_chunk: np.ndarray) -> bool:
        """Simple energy-based detection (fallback)"""
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        
        # Detect if energy exceeds threshold
        if rms > 0.05:  # Adjust threshold as needed
            logger.debug(f"Energy spike detected: {rms:.4f}")
            return True
        
        return False
    
    def reset(self):
        """Reset detector state"""
        if self.model and hasattr(self.model, 'reset'):
            self.model.reset()


class StreamingWakeWordDetector:
    """Streaming wake word detector with callback"""
    
    def __init__(self, callback: Optional[Callable] = None, **kwargs):
        """
        Initialize streaming detector.
        
        Args:
            callback: Function to call when wake word detected
            **kwargs: Arguments for WakeWordDetector
        """
        self.detector = WakeWordDetector(**kwargs)
        self.callback = callback
        self.is_active = False
    
    def process_chunk(self, audio_chunk: np.ndarray):
        """Process audio chunk"""
        if not self.is_active:
            return
        
        detected = self.detector.detect(audio_chunk)
        
        if detected and self.callback:
            self.callback('wake_word_detected', None)
    
    def start(self):
        """Start detection"""
        self.is_active = True
        logger.info("Wake word detection started")
    
    def stop(self):
        """Stop detection"""
        self.is_active = False
        logger.info("Wake word detection stopped")

