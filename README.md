
# 🎙️ VAANI - Voice Assistant for Android

A fully functional, customizable voice assistant for Android. Control your phone completely hands-free with your own wake word!

## 🎯 What It Does

**Like "Hey Google" or "Alexa" - but YOUR way:**
- 🎤 **Custom Wake Word**: Choose any name (Vaani, Jarvis, Assistant, or even your own name!)
- 📱 **Hands-Free Control**: Open apps, make calls, send messages - all by voice
- 🚀 **Fully Functional**: Working implementation ready to use
- 🔒 **Privacy First**: All processing on-device, no cloud required
- ⚡ **Fast Response**: < 2 second response time

**Example Usage:**
```
You: "Vaani"
Phone: *vibrates* "Yes?"
You: "Open WhatsApp"
Phone: *WhatsApp opens* ✓
```

## ✨ Key Features

### 🎙️ **Customizable Wake Word**
Choose ANY wake word you like:
- "Vaani" - Default
- "Hey Assistant"
- "Jarvis" - Like Iron Man
- "Computer" - Star Trek style
- Your own name or any 2+ character phrase

### 📱 **Complete Phone Control**
- ✅ Open any installed app
- ✅ Make phone calls
- ✅ Send messages
- ✅ Navigate (back, home, scroll)
- ✅ System control (volume, brightness)
- ✅ Get information (time, weather)

### 🔧 **Advanced Technology**
- Wake word detection with Vosk (offline)
- Continuous background listening
- Intent classification and entity extraction
- Action execution via Accessibility Service
- Text-to-Speech feedback
- Visual feedback with overlay

### 🔒 **Privacy & Security**
- **100% On-Device Processing** - No cloud uploads
- **No Data Collection** - Your voice stays on your phone
- **Open Source** - See exactly what it does
- **You Control It** - Disable anytime

## 🚀 Quick Start (5 Minutes)

### 1. Build & Install

```bash
cd android/vaani_phone_app

# Windows
quick_build_and_install.bat

# Linux/Mac
./gradlew clean assembleDebug installDebug
```

### 2. Setup on Phone

1. **Open Vaani app**
2. **Grant all permissions** (microphone, phone, SMS, etc.)
3. **Enter your wake word** (e.g., "Vaani")
4. **Click "Save"**
5. **Toggle service ON**

### 3. Test It!

```
Say: "[Your Wake Word]"
Wait for: Phone vibrates + "Yes?"
Say: "Open WhatsApp"
Result: WhatsApp opens! 🎉
```

## 📖 Complete Documentation

### For Users
- 📘 **[Quick Start Guide](android/vaani_phone_app/QUICKSTART.md)** - Get started in 5 minutes
- 📗 **[User Guide](android/vaani_phone_app/USER_GUIDE.md)** - All commands and features
- 📙 **[Setup Guide](android/vaani_phone_app/SETUP_GUIDE.md)** - Detailed installation

### For Developers
- 🏗️ Architecture details below
- 💻 Source code: `android/vaani_phone_app/app/src/main/java/com/vaani/phone/`
- 🐍 Python backend: `pipeline/android_bridge/vaani_backend_server.py`

## Project Structure

```
vaani_voice_app/
├── app/src/main/
│   ├── java/com/vaani/voice/MainActivity.kt
│   ├── res/layout/activity_main.xml
│   └── AndroidManifest.xml
├── build.gradle
└── settings.gradle
```

## How It Works

Speech Recognition → Intent Match → Execute Action

## Commands

- "Open WhatsApp"
- "Open Chrome"
- "Open Gmail"
- "Open YouTube"
- "Go home"

## Built With

- Kotlin
- Android SDK
- SpeechRecognizer API
- TextToSpeech API

## License

MIT

**Or with Python:**
```bash
python run_vaani_mobile.py --platform android --mode adb
```

This enables:
- ✅ Wake word activation ("Hey VAANI")
- ✅ Complete hands-free phone control
- ✅ Open apps, make calls, send messages by voice
- ✅ Read screen and notifications aloud
- ✅ Tap, swipe, scroll by voice commands
- ✅ Emergency SOS without touching phone
- ✅ Designed for elderly and disabled users

**See [Mobile Accessibility Guide](docs/MOBILE_ACCESSIBILITY_GUIDE.md) for full details.**

**No text input required - just speak naturally!**

## 🏗️ Architecture

VAANI consists of seven core components:

```
User Speech → VAD → ASR → NLU → DST → DM → NLG → TTS → Audio Response
```

### Components

1. **VAD (Voice Activity Detection)**: Detects when the user is speaking
   - Technology: Silero VAD
   
2. **ASR (Automatic Speech Recognition)**: Converts speech to text
   - Phase 1: Google Speech API
   - Phase 2: Fine-tuned Whisper model
   
3. **NLU (Natural Language Understanding)**: Extracts intent and entities
   - Intent classification
   - Named entity recognition
   - Custom trained models
   
4. **DST (Dialogue State Tracking)**: Maintains conversation context
   - Tracks conversation history
   - Manages multi-turn dialogues
   
5. **DM (Dialogue Manager)**: Decides what action to take
   - Rule-based and ML-based decision making
   - Action execution
   
6. **NLG (Natural Language Generation)**: Generates text responses
   - Template-based responses
   - Dynamic response generation
   
7. **TTS (Text-to-Speech)**: Converts text to speech
   - Android native TTS
   - Custom voice options

## 🎯 Supported Intents

VAANI currently supports 10 core intents:

| Intent | Description | Example |
|--------|-------------|---------|
| GREETING | Greet the assistant | "Hello VAANI" |
| QUERY_TIME | Ask for current time | "What time is it?" |
| QUERY_WEATHER | Get weather information | "What's the weather in Delhi?" |
| OPEN_APP | Launch applications | "Open YouTube" |
| CALL_PERSON | Make phone calls | "Call Mom" |
| GENERAL_KNOWLEDGE | Ask factual questions | "Who is Einstein?" |
| ALARM_SET | Set alarms | "Set alarm for 6 AM" |
| REMINDER_SET | Create reminders | "Remind me to buy milk" |
| JOKE | Request entertainment | "Tell me a joke" |
| CASUAL_CHAT | General conversation | "How are you?" |

## 📁 Project Structure

```
vaani/
├── data/                    # All datasets
│   ├── audio_raw/          # Raw audio files
│   ├── transcripts/        # Transcriptions
│   ├── queries/            # Text queries
│   └── annotations/        # Labeled data
├── models/                 # Trained models
│   ├── asr/               # ASR models
│   ├── nlu/               # NLU models
│   ├── dst/               # DST models
│   └── dm/                # DM models
├── pipeline/              # Core pipeline code
│   ├── asr/              # ASR implementation
│   ├── nlu/              # NLU implementation
│   ├── dst/              # DST implementation
│   ├── dm/               # DM implementation
│   ├── nlg/              # NLG implementation
│   ├── tts/              # TTS implementation
│   └── vad/              # VAD implementation
├── app/                   # Application code
│   └── android/          # Android app
├── notebooks/            # Jupyter notebooks
├── docs/                 # Documentation
├── tests/                # Unit tests
└── logs/                 # Application logs
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/vaani.git
cd vaani
```

### 2. Set Up Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Auto-repair audio environment
python scripts/fix_audio_env.py

# Test microphone
python scripts/test_microphone.py
```

### 3. Generate Initial Dataset

```bash
# Create project structure
python setup_structure.py

# Generate 1,000 sample queries
python generate_queries.py

# Generate synthetic audio (optional)
python generate_audio.py --engine gtts --limit 10
```

### 4. Train NLU Models

```bash
# Train intent classifier
python pipeline/nlu/train_intents.py --data data/queries/queries_day1.csv

# Train entity extractor (requires annotations)
python pipeline/nlu/train_entities.py --annotations data/annotations/sample_annotations.json
```

### 5. Run the CLI Demo

```bash
# Advanced streaming demo with Whisper + VAD
python cli/vaani_demo.py

# Or use the basic voice CLI
python cli/vaani_voice_cli.py

# Commands in demo:
#   start   - Start streaming mode with real-time ASR
#   stop    - Stop streaming
#   whisper - Toggle Whisper ASR
#   vad     - Toggle Voice Activity Detection
#   status  - Show system status
#   exit    - Exit
```

### 6. Explore the Data

```bash
# View generated queries
head data/queries/queries_day1.csv

# Check audio files (if generated)
ls data/audio_raw/day1/
```

## 🎮 Advanced Demo (NEW!)

Experience the complete VAANI pipeline with our advanced demo system!

### Interactive CLI v2

Run the enhanced interactive CLI with full pipeline visualization:

```bash
python cli/vaani_cli_v2.py
```

**Features:**
- 🎤 **Voice Input**: Record from microphone with `talk` command
- 📁 **Audio Files**: Process WAV files with `audio <filepath>`
- 💬 **Text Input**: Process text with `text "<message>"`
- 📊 **State Tracking**: View dialogue state with `state`
- 📜 **History**: See conversation history with `history`
- 🔄 **Reset**: Clear state with `reset`

**Example Session:**
```
VAANI> text "hello VAANI"
💬 Response: Hello! How can I help you today?

VAANI> text "what's the weather in Delhi"
💬 Response: I'll check the weather in Delhi for you.

VAANI> state
Current Dialogue State:
  Turn Count: 2
  Active Intent: QUERY_WEATHER
  Stored Entities: 1
    - LOCATION: Delhi
```

### Advanced Pipeline Script

Process inputs with detailed stage-by-stage output:

```bash
# Process text
python pipeline/run_pipeline_advanced.py --text "what time is it"

# Process audio file
python pipeline/run_pipeline_advanced.py --audio samples/weather_delhi.wav

# Record from microphone
python pipeline/run_pipeline_advanced.py --microphone --duration 5

# Enable TTS output
python pipeline/run_pipeline_advanced.py --text "hello" --speak
```

**Pipeline Stages Shown:**
1. 🔊 **VAD** - Voice Activity Detection
2. 📝 **ASR** - Speech Recognition (Whisper → Google → Simulated)
3. 🧠 **NLU** - Intent & Entity Extraction
4. 💾 **DST** - Dialogue State Update
5. 🎯 **DM** - Action Decision
6. 💬 **NLG** - Response Generation

**With colored output and timing for each stage!**

### Sample Audio Files

Generate sample audio files for testing:

```bash
# Install TTS dependencies
pip install gtts pydub

# Generate samples
python generate_sample_audio.py
```

This creates 8 sample WAV files in `samples/` directory covering all major intents.

### Complete Demo Guide

For detailed instructions, examples, and troubleshooting:

📖 **[Read the Complete Demo Guide](docs/DEMO_GUIDE.md)**

Includes:
- Prerequisites and setup
- Usage examples with expected output
- CLI commands reference
- Pipeline stages explained
- Troubleshooting guide
- Advanced features

## 🛠️ Technology Stack

- **Language**: Python 3.8+
- **ML Frameworks**: PyTorch, Transformers, scikit-learn
- **ASR**: Google Speech API, OpenAI Whisper
- **NLP**: NLTK, spaCy
- **Audio Processing**: librosa, soundfile, pydub
- **TTS**: gTTS, pyttsx3, Coqui TTS
- **Mobile**: Android (Java/Kotlin)
- **Tools**: Jupyter, pytest, black, flake8

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

