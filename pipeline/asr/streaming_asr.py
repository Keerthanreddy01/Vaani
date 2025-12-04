import sys
import time
import logging
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import sounddevice as sd
    import numpy as np
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False
    logger.warning("sounddevice not available")

try:
    from pipeline.vad.vad_silero import StreamingVAD
    HAS_VAD = True
except ImportError:
    HAS_VAD = False
    logger.warning("VAD not available")

try:
    from pipeline.asr.asr_whisper import WhisperASR
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False
    logger.warning("Whisper not available")

class StreamingASR:
    def __init__(self,
                 sample_rate=16000,
                 chunk_duration=0.5,
                 vad_enabled=True,
                 whisper_model="base",
                 callback=None):

        if not HAS_AUDIO:
            raise ImportError("sounddevice required")

        self.sample_rate = sample_rate
        self.chunk_size = 512 if sample_rate == 16000 else 256
        self.vad_enabled = vad_enabled
        self.callback = callback

        self.is_running = False
        self.stream = None

        # For non-VAD mode: collect audio chunks and process periodically
        self.audio_buffer = []
        self.buffer_duration = 3.0  # Process every 3 seconds
        self.last_process_time = 0

        logger.info(f"Initializing StreamingASR: sample_rate={sample_rate}, chunk_size={self.chunk_size}")

        if vad_enabled and HAS_VAD:
            self.vad = StreamingVAD(threshold=0.6, sample_rate=sample_rate, chunk_size=self.chunk_size)
            logger.info("VAD enabled with threshold=0.6")
        else:
            self.vad = None
            logger.info("VAD disabled")

        if HAS_WHISPER:
            self.asr = WhisperASR(model_name=whisper_model)
            logger.info(f"Whisper ASR loaded: {whisper_model}")
        else:
            self.asr = None
            logger.warning("Whisper not available")
    
    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            if 'overflow' in str(status).lower():
                logger.warning("⚠ Audio buffer overflow - skipping frame")
                return
            else:
                logger.warning(f"Audio status: {status}")

        try:
            audio_chunk = indata[:, 0].copy()

            if self.vad:
                state, complete_audio = self.vad.process_chunk(audio_chunk)

                if state == 'ended' and complete_audio is not None:
                    threading.Thread(
                        target=self._process_audio,
                        args=(complete_audio,),
                        daemon=True
                    ).start()
            else:
                # No VAD: collect chunks and process periodically
                import time
                self.audio_buffer.append(audio_chunk)

                current_time = time.time()
                buffer_duration = len(self.audio_buffer) * len(audio_chunk) / self.sample_rate

                # Process every 3 seconds of audio
                if buffer_duration >= self.buffer_duration:
                    # Concatenate all chunks
                    complete_audio = np.concatenate(self.audio_buffer)
                    self.audio_buffer = []

                    # Check if there's actual audio (not silence)
                    audio_level = np.abs(complete_audio).mean()
                    if audio_level > 0.01:  # Threshold for silence detection
                        logger.info(f"🎤 Audio detected (level: {audio_level:.4f}), processing...")
                        threading.Thread(
                            target=self._process_audio,
                            args=(complete_audio,),
                            daemon=True
                        ).start()
                    else:
                        logger.debug(f"Silence detected (level: {audio_level:.4f}), skipping")

                if self.callback:
                    self.callback('chunk', audio_chunk)
        except Exception as e:
            logger.error(f"Audio callback error: {e}")
    
    def _process_audio(self, audio_data):
        if self.callback:
            self.callback('processing', None)

        speech_duration = len(audio_data) / self.sample_rate
        logger.info(f"Processing speech: {speech_duration:.2f}s duration, {len(audio_data)} samples")

        if self.asr:
            result = self.asr.transcribe_audio(audio_data, sample_rate=self.sample_rate)

            if result['success'] and result['text']:
                # Ignore very short transcriptions (likely noise)
                if len(result['text'].strip()) < 2:
                    logger.info("Ignoring very short transcription (noise)")
                    return

                if self.callback:
                    self.callback('result', result)
                logger.info(f"✓ Transcription: '{result['text']}'")
            else:
                logger.warning("Transcription failed or empty")
        else:
            logger.warning("No ASR engine available")
    
    def start(self):
        if self.is_running:
            logger.warning("Already running")
            return
        
        logger.info("Starting streaming ASR...")
        self.is_running = True
        
        try:
            # Use larger blocksize to prevent overflow
            blocksize = 2048 if self.sample_rate == 16000 else 1024

            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32',
                blocksize=blocksize,
                callback=self._audio_callback,
                latency='low'  # Reduce latency
            )
            self.stream.start()
            logger.info(f"Streaming ASR started (blocksize={blocksize}, samplerate={self.sample_rate})")

            if self.callback:
                self.callback('started', None)
        
        except Exception as e:
            logger.error(f"Failed to start stream: {e}")
            self.is_running = False
            raise
    
    def stop(self):
        if not self.is_running:
            return
        
        logger.info("Stopping streaming ASR...")
        self.is_running = False
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        logger.info("Streaming ASR stopped")
        
        if self.callback:
            self.callback('stopped', None)
    
    def is_active(self):
        return self.is_running

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    def callback(event, data):
        if event == 'started':
            print("🎙️  Listening...")
        elif event == 'processing':
            print("🔵 Processing...")
        elif event == 'result':
            print(f"📝 Result: {data['text']}")
        elif event == 'stopped':
            print("🛑 Stopped")
    
    if HAS_AUDIO:
        print("Starting streaming ASR demo (press Ctrl+C to stop)...")
        asr = StreamingASR(callback=callback)
        asr.start()
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping...")
            asr.stop()
    else:
        print("❌ sounddevice not available")

