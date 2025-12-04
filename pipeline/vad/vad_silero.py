import logging
import numpy as np

logger = logging.getLogger(__name__)

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    logger.warning("PyTorch not available. Install with: pip install torch")

class SileroVAD:
    def __init__(self, threshold=0.5, sample_rate=16000):
        if not HAS_TORCH:
            raise ImportError("PyTorch required for Silero VAD")
        
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.model = None
        self.utils = None
        self._load_model()
    
    def _load_model(self):
        try:
            logger.info("Loading Silero VAD model...")
            self.model, self.utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False,
                trust_repo=True
            )
            self.get_speech_timestamps = self.utils[0]
            logger.info("Silero VAD model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Silero VAD: {e}")
            logger.warning("Falling back to simple energy-based VAD")
            self.model = None
            self.utils = None
    
    def is_speech(self, audio_chunk):
        if not self.model:
            if isinstance(audio_chunk, torch.Tensor):
                audio_chunk = audio_chunk.numpy()
            energy = np.sqrt(np.mean(audio_chunk ** 2))
            return energy > 0.01

        try:
            if isinstance(audio_chunk, np.ndarray):
                audio_chunk = torch.from_numpy(audio_chunk).float()

            if audio_chunk.dim() > 1:
                audio_chunk = audio_chunk.squeeze()

            if audio_chunk.abs().max() > 1.0:
                audio_chunk = audio_chunk / 32768.0

            with torch.no_grad():
                speech_prob = self.model(audio_chunk, self.sample_rate).item()

            return speech_prob > self.threshold

        except Exception as e:
            logger.error(f"VAD error: {e}")
            if isinstance(audio_chunk, torch.Tensor):
                audio_chunk = audio_chunk.numpy()
            energy = np.sqrt(np.mean(audio_chunk ** 2))
            return energy > 0.01
    
    def detect_speech_segments(self, audio_data):
        if not self.model:
            return [(0, len(audio_data))]
        
        try:
            if isinstance(audio_data, np.ndarray):
                audio_tensor = torch.from_numpy(audio_data).float()
            else:
                audio_tensor = audio_data
            
            if audio_tensor.dim() > 1:
                audio_tensor = audio_tensor.squeeze()
            
            if audio_tensor.abs().max() > 1.0:
                audio_tensor = audio_tensor / 32768.0
            
            speech_timestamps = self.get_speech_timestamps(
                audio_tensor,
                self.model,
                threshold=self.threshold,
                sampling_rate=self.sample_rate,
                min_speech_duration_ms=250,
                min_silence_duration_ms=100
            )
            
            segments = [(ts['start'], ts['end']) for ts in speech_timestamps]
            return segments
        
        except Exception as e:
            logger.error(f"Speech detection error: {e}")
            return [(0, len(audio_data))]
    
    def has_speech(self, audio_data):
        segments = self.detect_speech_segments(audio_data)
        return len(segments) > 0

class StreamingVAD:
    def __init__(self, threshold=0.6, sample_rate=16000, chunk_size=512):
        self.vad = SileroVAD(threshold=threshold, sample_rate=sample_rate)
        self.chunk_size = chunk_size
        self.is_speaking = False
        self.speech_buffer = []
        self.silence_chunks = 0
        self.max_silence_chunks = 13  # ~0.4s of silence (13 * 32ms)
        self.min_speech_chunks = 22  # ~0.7s minimum speech (22 * 32ms)
        self.speech_chunks_count = 0

    def process_chunk(self, audio_chunk):
        is_speech = self.vad.is_speech(audio_chunk)

        if is_speech:
            if not self.is_speaking:
                logger.info("VAD: speech started")
                self.is_speaking = True
                self.speech_chunks_count = 0

            self.speech_buffer.append(audio_chunk)
            self.speech_chunks_count += 1
            self.silence_chunks = 0
            return 'speaking', None

        else:
            if self.is_speaking:
                self.silence_chunks += 1
                self.speech_buffer.append(audio_chunk)

                if self.silence_chunks >= self.max_silence_chunks:
                    # Check if we have enough speech
                    if self.speech_chunks_count < self.min_speech_chunks:
                        logger.info("VAD: ignoring noise (too short)")
                        self.is_speaking = False
                        self.speech_buffer = []
                        self.silence_chunks = 0
                        self.speech_chunks_count = 0
                        return 'silence', None

                    logger.info(f"VAD: speech ended ({len(self.speech_buffer)} chunks, {len(self.speech_buffer)*0.032:.2f}s)")
                    self.is_speaking = False

                    if isinstance(self.speech_buffer[0], np.ndarray):
                        complete_audio = np.concatenate(self.speech_buffer)
                    else:
                        complete_audio = torch.cat(self.speech_buffer)

                    self.speech_buffer = []
                    self.silence_chunks = 0
                    self.speech_chunks_count = 0
                    return 'ended', complete_audio

                return 'speaking', None

            return 'silence', None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if HAS_TORCH:
        print("✅ PyTorch is available")
        try:
            vad = SileroVAD()
            print("✅ Silero VAD loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load Silero VAD: {e}")
    else:
        print("❌ PyTorch not available")

