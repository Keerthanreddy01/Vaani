import sounddevice as sd
import numpy as np
import wave
import tempfile
import threading
from pathlib import Path

try:
    import torch
    import torchaudio
    vad_model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False)
    get_speech_timestamps = utils[0]
    HAS_VAD = True
except:
    HAS_VAD = False

SAMPLE_RATE = 16000
CHANNELS = 1

class MicrophoneEngine:
    def __init__(self):
        self.is_recording = False
        self.stream = None
        self.audio_buffer = []
        
    def record_once(self, duration=5):
        audio_data = sd.rec(int(duration * SAMPLE_RATE), 
                           samplerate=SAMPLE_RATE, 
                           channels=CHANNELS, 
                           dtype='float32')
        sd.wait()
        return audio_data.flatten()
    
    def detect_speech_vad(self, audio_data):
        if not HAS_VAD:
            return True
        
        try:
            audio_int16 = (audio_data * 32767).astype(np.int16)
            audio_tensor = torch.from_numpy(audio_int16).float() / 32768.0
            
            speech_timestamps = get_speech_timestamps(
                audio_tensor, 
                vad_model,
                sampling_rate=SAMPLE_RATE,
                threshold=0.5
            )
            
            return len(speech_timestamps) > 0
        except:
            return True
    
    def record_with_vad(self, duration=5):
        audio_data = self.record_once(duration)
        has_speech = self.detect_speech_vad(audio_data)
        return audio_data, has_speech
    
    def save_audio(self, audio_data, output_path):
        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
    
    def save_to_temp(self, audio_data):
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_path = temp_file.name
        temp_file.close()
        self.save_audio(audio_data, temp_path)
        return temp_path
    
    def start_continuous_listener(self, callback, duration=5):
        self.is_recording = True
        
        def listen_loop():
            while self.is_recording:
                try:
                    audio_data, has_speech = self.record_with_vad(duration)
                    if has_speech:
                        callback(audio_data)
                except Exception as e:
                    print(f"Error in listener: {e}")
                    break
        
        thread = threading.Thread(target=listen_loop, daemon=True)
        thread.start()
        return thread
    
    def stop_listener(self):
        self.is_recording = False

def test_microphone():
    try:
        print("Testing microphone...")
        audio = sd.rec(int(2 * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32')
        sd.wait()
        print(f"Recorded {len(audio)} samples")
        return True
    except Exception as e:
        print(f"Microphone test failed: {e}")
        return False

if __name__ == "__main__":
    test_microphone()

