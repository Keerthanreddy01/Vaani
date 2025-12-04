"""
Advanced End-to-End VAANI Pipeline with Production Features.

Features:
- Multiple input modes: microphone, audio file, text
- ASR fallback chain: Whisper → Google → Simulated
- Colored console output for each stage
- Processing time tracking
- Comprehensive error handling
- Optional TTS output
"""

import argparse
import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Colored output
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Fallback: no colors
    class Fore:
        CYAN = YELLOW = GREEN = BLUE = MAGENTA = RED = WHITE = ""
    class Style:
        BRIGHT = RESET_ALL = ""

# Core imports
from pipeline.vad.vad import VoiceActivityDetector
from pipeline.nlu.predict import NLUPredictor
from pipeline.dst.state_manager import DialogueStateManager
from pipeline.dm.decision_manager import DecisionManager
from pipeline.nlg.generate_response import ResponseGenerator
from utils.logger import get_logger
from utils.helpers import ensure_dir
import yaml

logger = get_logger(__name__)


class AdvancedVAANIPipeline:
    """Advanced end-to-end VAANI pipeline with production features."""
    
    def __init__(self, config_path="config/app_config.yaml", 
                 intent_model_path=None, entity_model_path=None,
                 use_vad=True, enable_tts=False):
        """
        Initialize advanced pipeline.
        
        Args:
            config_path: Path to configuration file
            intent_model_path: Path to intent classifier (overrides config)
            entity_model_path: Path to entity extractor (overrides config)
            use_vad: Whether to use VAD for audio input
            enable_tts: Whether to speak responses
        """
        logger.info("Initializing Advanced VAANI Pipeline...")
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Override with provided paths
        if intent_model_path:
            self.intent_model_path = intent_model_path
        else:
            self.intent_model_path = self.config['models']['nlu']['intent_classifier']
        
        if entity_model_path:
            self.entity_model_path = entity_model_path
        else:
            self.entity_model_path = self.config['models']['nlu']['entity_extractor']
        
        self.use_vad = use_vad
        self.enable_tts = enable_tts
        
        # Initialize components
        self._init_components()
        
        # Load ASR fallback map
        self.asr_fallback_map = self._load_asr_fallback_map()
        
        logger.info("Advanced VAANI Pipeline ready!")
    
    def _load_config(self, config_path):
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load config: {e}. Using defaults.")
            return {
                'models': {
                    'nlu': {
                        'intent_classifier': 'models/nlu/intent_classifier_tfidf_svm.pkl',
                        'entity_extractor': 'models/nlu/entity_extractor'
                    }
                },
                'vad': {'threshold': 0.5},
                'audio': {'sample_rate': 16000}
            }
    
    def _init_components(self):
        """Initialize pipeline components."""
        # VAD
        if self.use_vad:
            try:
                self.vad = VoiceActivityDetector(
                    threshold=self.config.get('vad', {}).get('threshold', 0.5)
                )
                self._print_stage("✓ VAD initialized", Fore.GREEN)
            except Exception as e:
                logger.warning(f"VAD initialization failed: {e}")
                self.vad = None
                self._print_stage("⚠ VAD not available", Fore.YELLOW)
        else:
            self.vad = None
        
        # NLU
        try:
            self.nlu = NLUPredictor(self.intent_model_path, self.entity_model_path)
            self._print_stage("✓ NLU initialized", Fore.GREEN)
        except Exception as e:
            logger.error(f"NLU initialization failed: {e}")
            raise RuntimeError("NLU is required for pipeline operation")
        
        # DST
        self.state = DialogueStateManager()
        self._print_stage("✓ DST initialized", Fore.GREEN)
        
        # DM
        self.dm = DecisionManager()
        self._print_stage("✓ DM initialized", Fore.GREEN)
        
        # NLG
        self.nlg = ResponseGenerator()
        self._print_stage("✓ NLG initialized", Fore.GREEN)
        
        # TTS (optional)
        if self.enable_tts:
            try:
                import pyttsx3
                self.tts_engine = pyttsx3.init()
                self._print_stage("✓ TTS initialized", Fore.GREEN)
            except Exception as e:
                logger.warning(f"TTS initialization failed: {e}")
                self.tts_engine = None
                self._print_stage("⚠ TTS not available", Fore.YELLOW)
        else:
            self.tts_engine = None

    def _load_asr_fallback_map(self):
        """Load ASR fallback mapping from CSV."""
        fallback_map = {}
        csv_path = Path("samples/sample_asr_map.csv")

        if not csv_path.exists():
            logger.warning("ASR fallback map not found")
            return fallback_map

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    fallback_map[row['filename']] = row['transcription']
            logger.info(f"Loaded {len(fallback_map)} ASR fallback entries")
        except Exception as e:
            logger.error(f"Error loading ASR fallback map: {e}")

        return fallback_map

    def _print_stage(self, message, color=Fore.WHITE, bold=False):
        """Print colored stage message."""
        if COLORS_AVAILABLE:
            style = Style.BRIGHT if bold else ""
            print(f"{style}{color}{message}{Style.RESET_ALL}")
        else:
            print(message)

    def _print_separator(self, char="=", length=70):
        """Print separator line."""
        print(char * length)

    def _transcribe_audio(self, audio_path):
        """
        Transcribe audio using fallback chain: Whisper → Google → Simulated.

        Args:
            audio_path: Path to audio file

        Returns:
            tuple: (transcription, method_used)
        """
        audio_path = Path(audio_path)

        # Priority 1: Try Whisper
        whisper_model_path = Path(self.config['models']['asr']['whisper']) / "final"
        if whisper_model_path.exists():
            try:
                import whisper
                logger.info("Attempting Whisper ASR...")
                model = whisper.load_model("base")
                result = model.transcribe(str(audio_path))
                transcription = result['text'].strip()
                if transcription:
                    return transcription, "whisper"
            except Exception as e:
                logger.warning(f"Whisper ASR failed: {e}")

        # Priority 2: Try Google Cloud Speech
        try:
            from pipeline.asr.asr_google import transcribe_audio
            logger.info("Attempting Google Cloud Speech ASR...")
            transcription = transcribe_audio(str(audio_path))
            if transcription and transcription != "ASR failed":
                return transcription, "google"
        except Exception as e:
            logger.warning(f"Google ASR failed: {e}")

        # Priority 3: Simulated ASR using fallback map
        filename = audio_path.name
        if filename in self.asr_fallback_map:
            logger.info("Using simulated ASR from fallback map")
            return self.asr_fallback_map[filename], "simulated"

        # Last resort: return error
        logger.error("All ASR methods failed")
        return None, "failed"

    def _record_audio(self, duration=5):
        """
        Record audio from microphone.

        Args:
            duration: Recording duration in seconds

        Returns:
            Path to recorded audio file
        """
        try:
            from pipeline.data.record_audio import AudioRecorder

            # Create temporary directory
            temp_dir = Path("data/temp")
            ensure_dir(temp_dir)

            # Generate filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = temp_dir / f"recording_{timestamp}.wav"

            # Record
            recorder = AudioRecorder(
                sample_rate=self.config.get('audio', {}).get('sample_rate', 16000)
            )
            recorder.record(duration, output_path)

            return output_path
        except Exception as e:
            logger.error(f"Recording failed: {e}")
            return None

    def _speak_response(self, text):
        """Speak response using TTS."""
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                logger.warning(f"TTS failed: {e}")

    def process_text(self, text, verbose=True):
        """
        Process text input through NLU → DST → DM → NLG pipeline.

        Args:
            text: Input text
            verbose: Whether to print detailed output

        Returns:
            dict: Pipeline results with response
        """
        results = {'input_text': text, 'stages': {}}

        if verbose:
            self._print_separator()
            self._print_stage("🎯 VAANI ADVANCED PIPELINE", Fore.CYAN, bold=True)
            self._print_separator()
            self._print_stage(f"\n📝 Input: {text}", Fore.CYAN)

        try:
            # Stage 1: NLU
            start_time = time.time()
            nlu_result = self.nlu.predict_all(text)
            nlu_time = time.time() - start_time

            results['stages']['nlu'] = {
                'intent': nlu_result['intent'],
                'confidence': nlu_result['confidence'],
                'entities': nlu_result['entities'],
                'time': nlu_time
            }

            if verbose:
                self._print_stage(f"\n🧠 NLU Results ({nlu_time:.3f}s):", Fore.BLUE)
                self._print_stage(f"   Intent: {nlu_result['intent']}", Fore.BLUE)
                self._print_stage(f"   Confidence: {nlu_result['confidence']:.2%}", Fore.BLUE)
                if nlu_result['entities']:
                    self._print_stage(f"   Entities: {len(nlu_result['entities'])}", Fore.BLUE)
                    for ent in nlu_result['entities']:
                        self._print_stage(f"      - {ent['text']} ({ent['label']})", Fore.BLUE)
                else:
                    self._print_stage("   Entities: None", Fore.BLUE)

            # Stage 2: DST
            start_time = time.time()
            self.state.update_turn(
                user_input=text,
                intent=nlu_result['intent'],
                entities=nlu_result['entities']
            )
            dst_time = time.time() - start_time

            results['stages']['dst'] = {
                'turn_count': self.state.turn_count,
                'active_intent': self.state.active_intent,
                'entities': dict(self.state.entities),
                'time': dst_time
            }

            if verbose:
                self._print_stage(f"\n💾 DST State ({dst_time:.3f}s):", Fore.MAGENTA)
                self._print_stage(f"   Turn: {self.state.turn_count}", Fore.MAGENTA)
                self._print_stage(f"   Active Intent: {self.state.active_intent}", Fore.MAGENTA)
                if self.state.entities:
                    self._print_stage(f"   Stored Entities: {len(self.state.entities)}", Fore.MAGENTA)

            # Stage 3: DM
            start_time = time.time()
            action = self.dm.decide(nlu_result['intent'], self.state, nlu_result['entities'])
            dm_time = time.time() - start_time

            results['stages']['dm'] = {
                'action': action,
                'time': dm_time
            }

            if verbose:
                self._print_stage(f"\n🎯 DM Decision ({dm_time:.3f}s):", Fore.YELLOW)
                self._print_stage(f"   Action: {action.get('action', 'unknown')}", Fore.YELLOW)

            # Stage 4: NLG
            start_time = time.time()
            response = self.nlg.generate(action)
            nlg_time = time.time() - start_time

            results['stages']['nlg'] = {
                'response': response,
                'time': nlg_time
            }
            results['response'] = response

            if verbose:
                self._print_stage(f"\n💬 NLG Response ({nlg_time:.3f}s):", Fore.GREEN, bold=True)
                self._print_stage(f"   {response}", Fore.GREEN, bold=True)

                total_time = nlu_time + dst_time + dm_time + nlg_time
                self._print_stage(f"\n⏱️  Total Processing Time: {total_time:.3f}s", Fore.WHITE)
                self._print_separator()

            # TTS output
            if self.enable_tts:
                self._speak_response(response)

            return results

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            if verbose:
                self._print_stage(f"\n❌ Error: {e}", Fore.RED)
                self._print_separator()
            return {'error': str(e), 'response': "I'm sorry, I encountered an error processing your request."}

    def process_audio(self, audio_path, verbose=True):
        """
        Process audio input through VAD → ASR → NLU → DST → DM → NLG pipeline.

        Args:
            audio_path: Path to audio file
            verbose: Whether to print detailed output

        Returns:
            dict: Pipeline results with response
        """
        results = {'input_audio': str(audio_path), 'stages': {}}

        if verbose:
            self._print_separator()
            self._print_stage("🎯 VAANI ADVANCED PIPELINE", Fore.CYAN, bold=True)
            self._print_separator()
            self._print_stage(f"\n🎤 Audio Input: {audio_path}", Fore.CYAN)

        try:
            # Stage 0: VAD (optional)
            if self.vad:
                start_time = time.time()
                segments = self.vad.detect_speech(str(audio_path))
                vad_time = time.time() - start_time

                results['stages']['vad'] = {
                    'segments': segments,
                    'time': vad_time
                }

                if verbose:
                    self._print_stage(f"\n🔊 VAD Results ({vad_time:.3f}s):", Fore.YELLOW)
                    self._print_stage(f"   Speech segments detected: {len(segments)}", Fore.YELLOW)
                    for i, seg in enumerate(segments, 1):
                        self._print_stage(f"      Segment {i}: {seg['start']:.2f}s - {seg['end']:.2f}s ({seg['duration']:.2f}s)", Fore.YELLOW)

            # Stage 1: ASR
            start_time = time.time()
            transcription, asr_method = self._transcribe_audio(audio_path)
            asr_time = time.time() - start_time

            if not transcription:
                error_msg = "ASR failed - could not transcribe audio"
                logger.error(error_msg)
                if verbose:
                    self._print_stage(f"\n❌ {error_msg}", Fore.RED)
                    self._print_separator()
                return {'error': error_msg, 'response': "I'm sorry, I couldn't understand the audio."}

            results['stages']['asr'] = {
                'transcription': transcription,
                'method': asr_method,
                'time': asr_time
            }

            if verbose:
                self._print_stage(f"\n📝 ASR Transcription ({asr_time:.3f}s):", Fore.GREEN)
                self._print_stage(f"   Method: {asr_method}", Fore.GREEN)
                self._print_stage(f"   Text: \"{transcription}\"", Fore.GREEN)

            # Continue with text processing
            text_results = self.process_text(transcription, verbose=False)

            # Merge results
            results['stages'].update(text_results.get('stages', {}))
            results['response'] = text_results.get('response', '')

            if verbose:
                # Print NLU, DST, DM, NLG results
                if 'nlu' in results['stages']:
                    nlu = results['stages']['nlu']
                    self._print_stage(f"\n🧠 NLU Results ({nlu['time']:.3f}s):", Fore.BLUE)
                    self._print_stage(f"   Intent: {nlu['intent']}", Fore.BLUE)
                    self._print_stage(f"   Confidence: {nlu['confidence']:.2%}", Fore.BLUE)
                    if nlu['entities']:
                        self._print_stage(f"   Entities: {len(nlu['entities'])}", Fore.BLUE)
                        for ent in nlu['entities']:
                            self._print_stage(f"      - {ent['text']} ({ent['label']})", Fore.BLUE)

                if 'dst' in results['stages']:
                    dst = results['stages']['dst']
                    self._print_stage(f"\n💾 DST State ({dst['time']:.3f}s):", Fore.MAGENTA)
                    self._print_stage(f"   Turn: {dst['turn_count']}", Fore.MAGENTA)
                    self._print_stage(f"   Active Intent: {dst['active_intent']}", Fore.MAGENTA)

                if 'dm' in results['stages']:
                    dm = results['stages']['dm']
                    self._print_stage(f"\n🎯 DM Decision ({dm['time']:.3f}s):", Fore.YELLOW)
                    self._print_stage(f"   Action: {dm['action'].get('action', 'unknown')}", Fore.YELLOW)

                if 'nlg' in results['stages']:
                    nlg = results['stages']['nlg']
                    self._print_stage(f"\n💬 NLG Response ({nlg['time']:.3f}s):", Fore.GREEN, bold=True)
                    self._print_stage(f"   {nlg['response']}", Fore.GREEN, bold=True)

                # Total time
                total_time = sum(stage.get('time', 0) for stage in results['stages'].values())
                self._print_stage(f"\n⏱️  Total Processing Time: {total_time:.3f}s", Fore.WHITE)
                self._print_separator()

            # TTS output
            if self.enable_tts:
                self._speak_response(results['response'])

            return results

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            if verbose:
                self._print_stage(f"\n❌ Error: {e}", Fore.RED)
                self._print_separator()
            return {'error': str(e), 'response': "I'm sorry, I encountered an error processing your request."}

    def process_microphone(self, duration=5, verbose=True):
        """
        Record from microphone and process through full pipeline.

        Args:
            duration: Recording duration in seconds
            verbose: Whether to print detailed output

        Returns:
            dict: Pipeline results with response
        """
        if verbose:
            self._print_stage("\n🎤 Recording from microphone...", Fore.CYAN)
            self._print_stage(f"   Duration: {duration} seconds", Fore.CYAN)
            self._print_stage("   Press Ctrl+C to stop early\n", Fore.CYAN)

        audio_path = self._record_audio(duration)

        if not audio_path:
            error_msg = "Recording failed"
            if verbose:
                self._print_stage(f"\n❌ {error_msg}", Fore.RED)
            return {'error': error_msg, 'response': "I'm sorry, I couldn't record audio."}

        return self.process_audio(audio_path, verbose=verbose)

    def reset_state(self):
        """Reset dialogue state."""
        self.state.reset()
        logger.info("Dialogue state reset")


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Advanced VAANI Pipeline - Production-Ready End-to-End Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process text
  python pipeline/run_pipeline_advanced.py --text "what time is it"

  # Process audio file
  python pipeline/run_pipeline_advanced.py --audio samples/weather_delhi.wav

  # Record from microphone
  python pipeline/run_pipeline_advanced.py --microphone --duration 5

  # Enable TTS output
  python pipeline/run_pipeline_advanced.py --text "hello" --speak
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--text", type=str, help="Text input to process")
    input_group.add_argument("--audio", type=str, help="Audio file path to process")
    input_group.add_argument("--microphone", action="store_true", help="Record from microphone")

    # Model options
    parser.add_argument("--intent-model", type=str,
                       default="models/nlu/intent_classifier_tfidf_svm.pkl",
                       help="Path to intent classifier")
    parser.add_argument("--entity-model", type=str,
                       default="models/nlu/entity_extractor",
                       help="Path to entity extractor")

    # Pipeline options
    parser.add_argument("--no-vad", action="store_true", help="Disable VAD")
    parser.add_argument("--speak", action="store_true", help="Enable TTS output")
    parser.add_argument("--duration", type=int, default=5, help="Recording duration (seconds)")
    parser.add_argument("--config", type=str, default="config/app_config.yaml",
                       help="Path to config file")

    args = parser.parse_args()

    try:
        # Initialize pipeline
        pipeline = AdvancedVAANIPipeline(
            config_path=args.config,
            intent_model_path=args.intent_model,
            entity_model_path=args.entity_model,
            use_vad=not args.no_vad,
            enable_tts=args.speak
        )

        # Process input
        if args.text:
            results = pipeline.process_text(args.text)
        elif args.audio:
            results = pipeline.process_audio(args.audio)
        elif args.microphone:
            results = pipeline.process_microphone(duration=args.duration)

        # Exit with appropriate code
        sys.exit(0 if 'response' in results else 1)

    except Exception as e:
        print(f"\n{Fore.RED}❌ Fatal Error: {e}{Style.RESET_ALL}")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

