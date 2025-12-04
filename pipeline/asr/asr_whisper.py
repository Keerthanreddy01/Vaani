import os
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import whisper
    import torch
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False
    logger.warning("Whisper not available. Install with: pip install openai-whisper")

class WhisperASR:
    def __init__(self, model_name="base", device=None):
        if not HAS_WHISPER:
            raise ImportError("Whisper not installed")
        
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self._load_model()
    
    def _load_model(self):
        logger.info(f"Loading Whisper model: {self.model_name} on {self.device}")
        start_time = time.time()
        self.model = whisper.load_model(self.model_name, device=self.device)
        load_time = time.time() - start_time
        logger.info(f"Whisper model loaded in {load_time:.2f}s")
    
    def transcribe_file(self, audio_path, language=None):
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        start_time = time.time()
        
        try:
            result = self.model.transcribe(
                str(audio_path),
                language=language,
                fp16=(self.device == "cuda")
            )
            
            latency = time.time() - start_time
            
            return {
                'text': result['text'].strip(),
                'language': result.get('language', 'unknown'),
                'confidence': 1.0,
                'latency': latency,
                'success': True,
                'method': 'whisper'
            }
        
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return {
                'text': '',
                'confidence': 0.0,
                'latency': 0.0,
                'success': False,
                'error': str(e),
                'method': 'whisper'
            }
    
    def transcribe_audio(self, audio_data, sample_rate=16000, language=None):
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        start_time = time.time()
        
        try:
            import numpy as np
            
            if isinstance(audio_data, list):
                audio_data = np.array(audio_data, dtype=np.float32)
            
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            if len(audio_data.shape) > 1:
                audio_data = audio_data.flatten()
            
            if sample_rate != 16000:
                from scipy import signal
                audio_data = signal.resample(audio_data, int(len(audio_data) * 16000 / sample_rate))

            logger.info(f"Transcribing audio: {len(audio_data)/16000:.2f}s duration")

            # Transcribe with improved settings for accuracy
            result = self.model.transcribe(
                audio_data,
                language=language or "en",
                fp16=False,  # Disable fp16 for better accuracy
                temperature=0,  # Deterministic output
                no_speech_threshold=0.05,  # Lower threshold
                condition_on_previous_text=False,  # Don't use context
                compression_ratio_threshold=2.4,
                logprob_threshold=-1.0
            )

            latency = time.time() - start_time
            text = result['text'].strip()

            logger.info(f"Whisper transcription: '{text}' (latency: {latency:.2f}s)")

            return {
                'text': text,
                'language': result.get('language', 'en'),
                'confidence': 1.0,
                'latency': latency,
                'success': True,
                'method': 'whisper'
            }
        
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return {
                'text': '',
                'confidence': 0.0,
                'latency': 0.0,
                'success': False,
                'error': str(e),
                'method': 'whisper'
            }

def transcribe_with_whisper(audio_path, model_name="base", language=None):
    try:
        asr = WhisperASR(model_name=model_name)
        result = asr.transcribe_file(audio_path, language=language)
        
        if result['success']:
            logger.info(f"Whisper transcription: '{result['text']}' (latency: {result['latency']:.2f}s)")
            return result['text']
        else:
            logger.error(f"Whisper failed: {result.get('error', 'Unknown error')}")
            return None
    
    except Exception as e:
        logger.error(f"Whisper transcription error: {e}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if HAS_WHISPER:
        print("✅ Whisper is available")
        print(f"   Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    else:
        print("❌ Whisper not available")
        print("   Install with: pip install openai-whisper")

