import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from pipeline.audio.mic_engine import MicrophoneEngine
    HAS_MIC = True
except ImportError:
    HAS_MIC = False
    MicrophoneEngine = None

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class Fore:
        CYAN = YELLOW = GREEN = BLUE = MAGENTA = RED = WHITE = ""
    class Style:
        BRIGHT = RESET_ALL = ""

try:
    import pyttsx3
    TTS_ENGINE = pyttsx3.init()
except:
    TTS_ENGINE = None

from pipeline.nlu.predict import NLUPredictor
from pipeline.dst.state_manager import DialogueStateManager
from pipeline.dm.decision_manager import DecisionManager
from pipeline.nlg.generate_response import ResponseGenerator
from utils.indicators import ListeningIndicator, ProcessingIndicator, RespondingIndicator

SAMPLE_RATE = 16000
VAD_THRESHOLD = 0.5
SILENCE_DURATION = 1.5

class LiveVoiceAssistant:
    def __init__(self, intent_model="models/nlu/intent_classifier_tfidf_svm.pkl",
                 entity_model="models/nlu/entity_extractor"):
        try:
            self.nlu = NLUPredictor(intent_model, entity_model)
        except:
            self.nlu = None
        self.state = DialogueStateManager()
        self.dm = DecisionManager()
        self.nlg = ResponseGenerator()

        if HAS_MIC:
            self.mic = MicrophoneEngine()
        else:
            self.mic = None
    
    def print_log(self, msg, color=Fore.WHITE):
        print(f"{color}{msg}{Style.RESET_ALL}")
    
    def speak(self, text):
        if TTS_ENGINE:
            try:
                responding = RespondingIndicator()
                responding.start()
                TTS_ENGINE.say(text)
                TTS_ENGINE.runAndWait()
                responding.stop()
            except:
                pass
    
    def transcribe_audio(self, audio_path):
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.AudioFile(str(audio_path)) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
                return text.strip(), "google_free"
        except ImportError:
            pass
        except Exception as e:
            pass

        try:
            import whisper
            model = whisper.load_model("base")
            result = model.transcribe(str(audio_path))
            return result['text'].strip(), "whisper"
        except:
            pass

        try:
            from pipeline.asr.asr_google import transcribe_audio
            text = transcribe_audio(str(audio_path))
            if text and text != "ASR failed":
                return text, "google_cloud"
        except:
            pass

        return None, "failed"
    
    def process_audio(self, audio_data):
        processing = ProcessingIndicator()
        processing.start()

        temp_path = self.mic.save_to_temp(audio_data)
        text, method = self.transcribe_audio(temp_path)
        Path(temp_path).unlink(missing_ok=True)

        if not text:
            processing.stop()
            self.print_log("❌ Could not transcribe audio", Fore.RED)
            return None

        if self.nlu:
            nlu_result = self.nlu.predict_all(text)
            self.state.update_turn(text, nlu_result['intent'], nlu_result['entities'])
            action = self.dm.decide(nlu_result['intent'], self.state, nlu_result['entities'])
            response = self.nlg.generate(action)
        else:
            response = f"I heard: {text}"

        processing.stop()

        self.print_log(f"📝 You said: {text}", Fore.GREEN)
        if self.nlu:
            self.print_log(f"🧠 Intent: {nlu_result['intent']} ({nlu_result['confidence']:.0%})", Fore.BLUE)
        self.print_log(f"💬 VAANI: {response}", Fore.GREEN + Style.BRIGHT)

        self.speak(response)

        return response
    
    def listen_once(self, duration=5):
        if not HAS_MIC:
            self.print_log("❌ Microphone not available. Install with: pip install sounddevice numpy", Fore.RED)
            self.print_log("💡 Testing with simulated input instead...", Fore.YELLOW)

            listening = ListeningIndicator()
            listening.start()
            time.sleep(2)
            listening.stop()

            test_text = "what time is it"

            processing = ProcessingIndicator()
            processing.start()

            if self.nlu:
                nlu_result = self.nlu.predict_all(test_text)
                self.state.update_turn(test_text, nlu_result['intent'], nlu_result['entities'])
                action = self.dm.decide(nlu_result['intent'], self.state, nlu_result['entities'])
                response = self.nlg.generate(action)
            else:
                response = f"I heard: {test_text}"

            processing.stop()

            self.print_log(f"📝 Simulated: {test_text}", Fore.GREEN)
            if self.nlu:
                self.print_log(f"🧠 Intent: {nlu_result['intent']} ({nlu_result['confidence']:.0%})", Fore.BLUE)
            self.print_log(f"💬 VAANI: {response}", Fore.GREEN + Style.BRIGHT)

            self.speak(response)
            return response

        listening = ListeningIndicator()
        listening.start()

        try:
            audio_data, has_speech = self.mic.record_with_vad(duration)
            listening.stop()

            if has_speech:
                self.print_log("🗣 Speech detected!", Fore.YELLOW)
                return self.process_audio(audio_data)
            else:
                self.print_log("⚠ No speech detected", Fore.YELLOW)
                return None
        except Exception as e:
            listening.stop()
            self.print_log(f"❌ Error: {e}", Fore.RED)
            return None

def main():
    assistant = LiveVoiceAssistant()
    assistant.print_log("\n🎙️ VAANI Live Voice Assistant Ready!", Fore.CYAN + Style.BRIGHT)
    assistant.listen_once()

if __name__ == "__main__":
    main()

