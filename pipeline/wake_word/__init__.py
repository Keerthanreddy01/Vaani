"""
Wake Word Detection Module for VAANI

Supports:
- openWakeWord (open source)
- Porcupine (Picovoice)
- Simple energy-based detection (fallback)
"""

from .wake_word_detector import WakeWordDetector

__all__ = ['WakeWordDetector']

