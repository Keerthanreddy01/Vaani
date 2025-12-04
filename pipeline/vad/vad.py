"""
Voice Activity Detection using Silero VAD.

Detects speech segments in audio and slices long audio into utterances.
"""

import argparse
import sys
from pathlib import Path

try:
    import torch
    import torchaudio
    import numpy as np
except ImportError:
    torch = None
    torchaudio = None
    np = None

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.logger import get_logger
from utils.helpers import ensure_dir

logger = get_logger(__name__)


class VoiceActivityDetector:
    """Voice Activity Detection using Silero VAD."""
    
    def __init__(self, threshold=0.5, min_speech_duration_ms=250, 
                 min_silence_duration_ms=100, sample_rate=16000):
        """
        Initialize VAD.
        
        Args:
            threshold: Speech probability threshold (0-1)
            min_speech_duration_ms: Minimum speech duration in ms
            min_silence_duration_ms: Minimum silence duration in ms
            sample_rate: Audio sample rate
        """
        if torch is None or torchaudio is None:
            raise ImportError("torch and torchaudio are required. "
                            "Install with: pip install torch torchaudio")
        
        self.threshold = threshold
        self.min_speech_duration_ms = min_speech_duration_ms
        self.min_silence_duration_ms = min_silence_duration_ms
        self.sample_rate = sample_rate
        
        # Load Silero VAD model
        logger.info("Loading Silero VAD model...")
        try:
            self.model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            self.get_speech_timestamps = utils[0]
            logger.info("Silero VAD model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Silero VAD: {e}")
            raise
    
    def detect_speech(self, audio_path):
        """
        Detect speech segments in audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            List of speech segments with start/end timestamps
        """
        # Load audio
        wav, sr = torchaudio.load(audio_path)
        
        # Resample if needed
        if sr != self.sample_rate:
            resampler = torchaudio.transforms.Resample(sr, self.sample_rate)
            wav = resampler(wav)
        
        # Convert to mono if stereo
        if wav.shape[0] > 1:
            wav = torch.mean(wav, dim=0, keepdim=True)
        
        # Get speech timestamps
        speech_timestamps = self.get_speech_timestamps(
            wav[0],
            self.model,
            threshold=self.threshold,
            sampling_rate=self.sample_rate,
            min_speech_duration_ms=self.min_speech_duration_ms,
            min_silence_duration_ms=self.min_silence_duration_ms
        )
        
        # Convert to seconds
        segments = []
        for ts in speech_timestamps:
            start_sec = ts['start'] / self.sample_rate
            end_sec = ts['end'] / self.sample_rate
            segments.append({
                "start": start_sec,
                "end": end_sec,
                "duration": end_sec - start_sec
            })
        
        logger.info(f"Detected {len(segments)} speech segments in {audio_path}")
        return segments
    
    def slice_audio(self, audio_path, output_dir, segments=None):
        """
        Slice audio into speech segments.
        
        Args:
            audio_path: Path to input audio
            output_dir: Output directory for sliced audio
            segments: Optional pre-computed segments (if None, will detect)
            
        Returns:
            List of output file paths
        """
        if segments is None:
            segments = self.detect_speech(audio_path)
        
        if not segments:
            logger.warning(f"No speech segments found in {audio_path}")
            return []
        
        # Load audio
        wav, sr = torchaudio.load(audio_path)
        
        # Resample if needed
        if sr != self.sample_rate:
            resampler = torchaudio.transforms.Resample(sr, self.sample_rate)
            wav = resampler(wav)
        
        # Create output directory
        output_dir = Path(output_dir)
        ensure_dir(output_dir)
        
        # Slice and save
        output_files = []
        audio_name = Path(audio_path).stem
        
        for i, segment in enumerate(segments):
            start_sample = int(segment["start"] * self.sample_rate)
            end_sample = int(segment["end"] * self.sample_rate)
            
            # Extract segment
            segment_wav = wav[:, start_sample:end_sample]
            
            # Save
            output_file = output_dir / f"{audio_name}_segment_{i:03d}.wav"
            torchaudio.save(str(output_file), segment_wav, self.sample_rate)
            
            output_files.append(str(output_file))
            logger.debug(f"Saved segment {i}: {output_file}")
        
        logger.info(f"Sliced audio into {len(output_files)} segments")
        return output_files


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Voice Activity Detection")
    parser.add_argument("--audio", type=str, required=True,
                       help="Path to audio file")
    parser.add_argument("--output-dir", type=str,
                       help="Output directory for sliced audio")
    parser.add_argument("--threshold", type=float, default=0.5,
                       help="Speech probability threshold")
    parser.add_argument("--min-speech-ms", type=int, default=250,
                       help="Minimum speech duration in ms")
    parser.add_argument("--min-silence-ms", type=int, default=100,
                       help="Minimum silence duration in ms")
    parser.add_argument("--sample-rate", type=int, default=16000,
                       help="Audio sample rate")
    
    args = parser.parse_args()
    
    vad = VoiceActivityDetector(
        threshold=args.threshold,
        min_speech_duration_ms=args.min_speech_ms,
        min_silence_duration_ms=args.min_silence_ms,
        sample_rate=args.sample_rate
    )
    
    # Detect speech
    segments = vad.detect_speech(args.audio)
    
    print("\n" + "=" * 70)
    print("🎤 Voice Activity Detection Results")
    print("=" * 70)
    print(f"Audio file: {args.audio}")
    print(f"Speech segments: {len(segments)}")
    print()
    
    for i, seg in enumerate(segments, 1):
        print(f"Segment {i}: {seg['start']:.2f}s - {seg['end']:.2f}s (duration: {seg['duration']:.2f}s)")
    
    # Slice if output directory provided
    if args.output_dir:
        output_files = vad.slice_audio(args.audio, args.output_dir, segments)
        print(f"\n✅ Sliced audio saved to: {args.output_dir}")
        print(f"   {len(output_files)} files created")
    
    print("=" * 70)


if __name__ == "__main__":
    main()

