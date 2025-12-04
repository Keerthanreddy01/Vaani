"""
Real-time audio recording module for VAANI data collection.

Records audio via microphone, saves in WAV format (16kHz mono).
"""

import argparse
import sys
import wave
from datetime import datetime
from pathlib import Path

try:
    import pyaudio
except ImportError:
    pyaudio = None

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.logger import get_logger
from utils.helpers import ensure_dir

logger = get_logger(__name__)


class AudioRecorder:
    """Records audio from microphone."""
    
    def __init__(self, sample_rate=16000, channels=1, chunk_size=1024):
        """
        Initialize audio recorder.
        
        Args:
            sample_rate: Sample rate in Hz (default: 16000)
            channels: Number of channels (default: 1 for mono)
            chunk_size: Audio chunk size (default: 1024)
        """
        if pyaudio is None:
            raise ImportError("pyaudio is required for recording. Install with: pip install pyaudio")
        
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = pyaudio.paInt16
        self.audio = pyaudio.PyAudio()
        
        logger.info(f"AudioRecorder initialized: {sample_rate}Hz, {channels} channel(s)")
    
    def record(self, duration_seconds, output_path, prompt=None):
        """
        Record audio for specified duration.
        
        Args:
            duration_seconds: Recording duration in seconds
            output_path: Path to save WAV file
            prompt: Optional text prompt to display
            
        Returns:
            Path to saved audio file
        """
        if prompt:
            print(f"\n📝 Prompt: {prompt}")
        
        print(f"🎤 Recording for {duration_seconds} seconds...")
        print("   Press Ctrl+C to stop early")
        
        try:
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            frames = []
            num_chunks = int(self.sample_rate / self.chunk_size * duration_seconds)
            
            for i in range(num_chunks):
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                # Progress indicator
                if (i + 1) % 10 == 0:
                    progress = (i + 1) / num_chunks * 100
                    print(f"   Progress: {progress:.0f}%", end='\r')
            
            print("\n✅ Recording complete!")
            
            stream.stop_stream()
            stream.close()
            
            # Save to WAV file
            ensure_dir(Path(output_path).parent)
            
            with wave.open(str(output_path), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))
            
            logger.info(f"Audio saved to: {output_path}")
            return output_path
            
        except KeyboardInterrupt:
            print("\n⚠️ Recording stopped by user")
            stream.stop_stream()
            stream.close()
            return None
        except Exception as e:
            logger.error(f"Recording error: {e}")
            raise
    
    def close(self):
        """Close audio interface."""
        self.audio.terminate()
        logger.info("AudioRecorder closed")


def generate_filename(prefix="audio", extension="wav"):
    """
    Generate timestamped filename.
    
    Args:
        prefix: Filename prefix
        extension: File extension
        
    Returns:
        Filename string
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Record audio for VAANI")
    parser.add_argument("--duration", type=int, default=5, help="Recording duration in seconds")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--output-dir", type=str, default="data/audio_raw/recordings",
                       help="Output directory")
    parser.add_argument("--prompt", type=str, help="Text prompt to display")
    parser.add_argument("--sample-rate", type=int, default=16000, help="Sample rate in Hz")
    
    args = parser.parse_args()
    
    # Generate output path
    if args.output:
        output_path = args.output
    else:
        filename = generate_filename()
        output_path = Path(args.output_dir) / filename
    
    # Record audio
    recorder = AudioRecorder(sample_rate=args.sample_rate)
    
    try:
        result = recorder.record(args.duration, output_path, args.prompt)
        if result:
            print(f"\n💾 Saved: {result}")
    finally:
        recorder.close()


if __name__ == "__main__":
    main()

