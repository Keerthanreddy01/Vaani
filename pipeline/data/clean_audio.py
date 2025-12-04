"""
Audio cleaning and preprocessing module for VAANI.

Performs normalization, noise reduction, silence trimming, and quality checks.
"""

import argparse
import sys
from pathlib import Path

try:
    import librosa
    import soundfile as sf
    import numpy as np
except ImportError:
    librosa = None
    sf = None
    np = None

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.logger import get_logger
from utils.helpers import ensure_dir

logger = get_logger(__name__)


class AudioCleaner:
    """Audio cleaning and preprocessing."""
    
    def __init__(self, target_sr=16000):
        """
        Initialize audio cleaner.
        
        Args:
            target_sr: Target sample rate
        """
        if librosa is None or sf is None or np is None:
            raise ImportError("librosa, soundfile, and numpy are required. "
                            "Install with: pip install librosa soundfile numpy")
        
        self.target_sr = target_sr
        logger.info(f"AudioCleaner initialized with target sample rate: {target_sr}Hz")
    
    def load_audio(self, audio_path):
        """
        Load audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        audio, sr = librosa.load(audio_path, sr=self.target_sr, mono=True)
        logger.debug(f"Loaded audio: {audio_path}, duration: {len(audio)/sr:.2f}s")
        return audio, sr
    
    def normalize(self, audio):
        """
        Normalize audio amplitude.
        
        Args:
            audio: Audio data array
            
        Returns:
            Normalized audio
        """
        # Peak normalization
        max_val = np.abs(audio).max()
        if max_val > 0:
            audio = audio / max_val * 0.95  # Leave some headroom
        return audio
    
    def reduce_noise(self, audio, sr):
        """
        Simple noise reduction using spectral gating.
        
        Args:
            audio: Audio data array
            sr: Sample rate
            
        Returns:
            Noise-reduced audio
        """
        # Simple approach: high-pass filter to remove low-frequency noise
        audio_filtered = librosa.effects.preemphasis(audio)
        return audio_filtered
    
    def trim_silence(self, audio, sr, top_db=20):
        """
        Trim silence from beginning and end.
        
        Args:
            audio: Audio data array
            sr: Sample rate
            top_db: Threshold in dB below reference
            
        Returns:
            Trimmed audio
        """
        audio_trimmed, _ = librosa.effects.trim(audio, top_db=top_db)
        
        original_duration = len(audio) / sr
        trimmed_duration = len(audio_trimmed) / sr
        logger.debug(f"Trimmed: {original_duration:.2f}s -> {trimmed_duration:.2f}s")
        
        return audio_trimmed
    
    def check_quality(self, audio, sr):
        """
        Check audio quality.
        
        Args:
            audio: Audio data array
            sr: Sample rate
            
        Returns:
            Dictionary with quality metrics
        """
        duration = len(audio) / sr
        rms = np.sqrt(np.mean(audio**2))
        peak = np.abs(audio).max()
        
        # Check for clipping
        clipping_ratio = np.sum(np.abs(audio) > 0.99) / len(audio)
        
        # Check for silence
        silence_ratio = np.sum(np.abs(audio) < 0.01) / len(audio)
        
        quality = {
            "duration": duration,
            "rms": float(rms),
            "peak": float(peak),
            "clipping_ratio": float(clipping_ratio),
            "silence_ratio": float(silence_ratio),
            "is_valid": clipping_ratio < 0.01 and silence_ratio < 0.8 and duration > 0.5
        }
        
        return quality
    
    def clean(self, audio_path, output_path=None, normalize=True, 
              reduce_noise=True, trim_silence=True):
        """
        Clean audio file.
        
        Args:
            audio_path: Input audio path
            output_path: Output audio path (None = overwrite)
            normalize: Whether to normalize
            reduce_noise: Whether to reduce noise
            trim_silence: Whether to trim silence
            
        Returns:
            Dictionary with quality metrics
        """
        # Load audio
        audio, sr = self.load_audio(audio_path)
        
        # Apply cleaning steps
        if trim_silence:
            audio = self.trim_silence(audio, sr)
        
        if reduce_noise:
            audio = self.reduce_noise(audio, sr)
        
        if normalize:
            audio = self.normalize(audio)
        
        # Check quality
        quality = self.check_quality(audio, sr)
        
        # Save cleaned audio
        if output_path is None:
            output_path = audio_path
        else:
            ensure_dir(Path(output_path).parent)
        
        sf.write(output_path, audio, sr)
        logger.info(f"Cleaned audio saved: {output_path}")
        
        return quality


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Clean audio files for VAANI")
    parser.add_argument("--input", type=str, required=True, help="Input audio file or directory")
    parser.add_argument("--output", type=str, help="Output file or directory")
    parser.add_argument("--sample-rate", type=int, default=16000, help="Target sample rate")
    parser.add_argument("--no-normalize", action="store_true", help="Skip normalization")
    parser.add_argument("--no-noise-reduction", action="store_true", help="Skip noise reduction")
    parser.add_argument("--no-trim", action="store_true", help="Skip silence trimming")
    
    args = parser.parse_args()
    
    cleaner = AudioCleaner(target_sr=args.sample_rate)
    
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Single file
        output_path = args.output if args.output else None
        quality = cleaner.clean(
            input_path,
            output_path,
            normalize=not args.no_normalize,
            reduce_noise=not args.no_noise_reduction,
            trim_silence=not args.no_trim
        )
        print(f"\n✅ Cleaned: {input_path}")
        print(f"Quality metrics: {quality}")
    
    elif input_path.is_dir():
        # Directory
        audio_files = list(input_path.glob("*.wav")) + list(input_path.glob("*.mp3"))
        print(f"\nFound {len(audio_files)} audio files")
        
        output_dir = Path(args.output) if args.output else input_path / "cleaned"
        ensure_dir(output_dir)
        
        for audio_file in audio_files:
            output_file = output_dir / audio_file.name
            try:
                quality = cleaner.clean(
                    audio_file,
                    output_file,
                    normalize=not args.no_normalize,
                    reduce_noise=not args.no_noise_reduction,
                    trim_silence=not args.no_trim
                )
                status = "✅" if quality["is_valid"] else "⚠️"
                print(f"{status} {audio_file.name}: {quality['duration']:.2f}s")
            except Exception as e:
                print(f"❌ {audio_file.name}: {e}")
    
    else:
        print(f"❌ Invalid input path: {input_path}")


if __name__ == "__main__":
    main()

