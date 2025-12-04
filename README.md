# 🎙️ VAANI - Voice-Activated AI Natural Interface

> **A beautiful, simple voice assistant that runs natively on your Android phone. Just speak commands like "Open WhatsApp" and watch them execute!**

---

## 🌟 Features

✨ **100% Phone-Based**
- Everything runs ON your phone (not laptop)
- Uses your phone's microphone
- No PC involvement after installation

🎤 **Voice Commands**
- "Open WhatsApp" → WhatsApp opens
- "Open Chrome" → Chrome opens  
- "Go home" → Home screen appears
- Natural speech recognition

⚡ **Simple & Fast**
- No complex setup
- One-tap to activate
- Instant response

🎯 **Real Voice Assistant**
- Like Google Assistant or Siri
- But yours, customizable
- Open source

---

## 📱 Architecture

```
┌─────────────────────────────────────┐
│      YOUR VIVO ANDROID PHONE        │
├─────────────────────────────────────┤
│                                     │
│  🎤 Microphone (AudioRecord)        │
│         ↓                           │
│  🧠 Speech Recognition (Android)    │
│         ↓                           │
│  📝 Intent Classification (NLU)     │
│         ↓                           │
│  ⚡ Action Execution (on phone)     │
│         ↓                           │
│  ✅ App Opens / Command Executes    │
│                                     │
└─────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Android Studio (to build)
- Android phone (API 24+)
- USB cable for ADB

### Installation

**Step 1: Clone & Open**
```bash
git clone https://github.com/Keerthanreddy01/Vaani.git
cd Vaani/vaani_voice_app
```

**Step 2: Build in Android Studio**
1. Open Android Studio
2. File → Open → select `vaani_voice_app` folder
3. Wait for Gradle sync
4. Click Build → Build APK

**Step 3: Install on Phone**
```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

**Step 4: Launch & Test**
1. Open VAANI app on your phone
2. Grant microphone permission
3. Tap the big green button
4. **SPEAK**: "Open WhatsApp"
5. Watch it open! 🎉

---

## 🎯 Supported Commands

| Command | Action |
|---------|--------|
| "Open WhatsApp" | Opens WhatsApp |
| "Open Chrome" | Opens Chrome browser |
| "Open Gmail" | Opens Gmail |
| "Open YouTube" | Opens YouTube |
| "Go home" | Returns to home screen |

*More commands can be easily added in `MainActivity.kt`*

---

## 📁 Project Structure

```
vaani_voice_app/
├── app/
│   ├── src/main/
│   │   ├── java/com/vaani/voice/
│   │   │   └── MainActivity.kt          ← All logic here
│   │   ├── res/layout/
│   │   │   └── activity_main.xml        ← UI layout
│   │   └── AndroidManifest.xml          ← Permissions
│   └── build.gradle                     ← Dependencies
├── build.gradle                         ← Project config
└── settings.gradle
```

---

## 🔧 How It Works

### MainActivity.kt
The entire app is in one simple file:

1. **SpeechRecognizer Setup**
   - Configures Android's built-in speech recognition
   - Sets language to English
   
2. **Voice Listening**
   - Captures what you say
   - Converts speech to text

3. **Intent Matching**
   - Checks if text contains "whatsapp", "chrome", etc.
   - Executes the corresponding action

4. **App Launching**
   - Uses Android Intent system
   - Safely opens requested apps

5. **Text-to-Speech**
   - Speaks back confirmation
   - "Opening WhatsApp" feedback

---

## 🎨 UI

```
┌──────────────────────┐
│   🎙️ VAANI          │
│                      │
│ Tap button and       │
│ say your command     │
│                      │
│    ┌──────────┐      │
│    │    🎤    │      │
│    │  TAP TO  │      │
│    │  SPEAK   │      │
│    └──────────┘      │
│                      │
│ Try saying:          │
│ • Open WhatsApp      │
│ • Open Chrome        │
│ • Go home            │
└──────────────────────┘
```

---

## 🔐 Permissions

The app requests only essential permissions:
- `RECORD_AUDIO` - Listen to your voice
- `INTERNET` - For speech recognition

Both requested at runtime for transparency.

---

## 📝 Adding New Commands

Want to add more commands? Edit `MainActivity.kt`:

```kotlin
private fun executeCommand(command: String) {
    val cmd = command.lowercase()
    
    val result = when {
        cmd.contains("whatsapp") -> {
            openApp("com.whatsapp")
            "Opening WhatsApp"
        }
        cmd.contains("new app") -> {      // ← Add here
            openApp("com.package.name")
            "Opening new app"
        }
        // ... more commands
    }
}
```

Then rebuild and reinstall.

---

## 🐛 Troubleshooting

**App won't start?**
- Check Android 24+ compatibility
- Grant microphone permission

**No voice response?**
- Ensure microphone permission is granted
- Check phone speaker volume
- Restart app

**Command not recognized?**
- Speak clearly
- Try different wording
- Check if app is installed on phone

**Build fails?**
- Sync Gradle in Android Studio
- Update Android SDK
- Check Java version (11+)

---

## 📊 Technical Details

**Built with:**
- Kotlin + Android SDK
- Android SpeechRecognizer API
- Android TextToSpeech API
- Material Design UI

**Tested on:**
- Vivo V2050 (Android 13)
- Minimum SDK: API 24 (Android 7.0)
- Target SDK: API 33 (Android 13)

---

## 🎓 Learning Resources

This project teaches:
- ✅ Android app development
- ✅ Voice recognition integration
- ✅ Intent-based app launching
- ✅ Permission handling
- ✅ Service architecture

Perfect for learning Android voice features!

---

## 🚀 Future Enhancements

- [ ] Always-on wake word detection
- [ ] More sophisticated NLU
- [ ] Custom command profiles
- [ ] Multi-language support
- [ ] Gesture-based actions
- [ ] Cloud integration (optional)

---

## 📄 License

MIT License - Feel free to use, modify, and distribute!

---

## 👨‍💻 Author

**Keerthan Reddy**
- GitHub: [@Keerthanreddy01](https://github.com/Keerthanreddy01)
- Project: VAANI Voice Assistant

---

## 💬 Support

Having issues? 
1. Check Troubleshooting section above
2. Review `MainActivity.kt` comments
3. Check Android Studio build output
4. Verify permissions on phone

---

## 🎉 Demo

```
YOU: "Hey, open WhatsApp"
     ↓
VAANI: "🎤 Listening..."
     ↓
VAANI: "✅ Opening WhatsApp"
     ↓
RESULT: WhatsApp opens on your phone!
```

That's it! Simple, clean, and it works.

---

**Made with ❤️ for Android developers**

*Last Updated: December 2025*

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

## 📚 Documentation

### Getting Started
- **[Quick Start Guide](docs/QUICKSTART.md)**: 5-minute quick start
- **[Demo Guide](docs/DEMO_GUIDE.md)**: 🆕 Complete guide for running the advanced demo
- **[Day 1 Setup Guide](docs/day1_setup.md)**: Complete guide for Day 1 setup

### Development Guides
- **[Days 2-4 Documentation](docs/day2_to_day4.md)**: Comprehensive guide for Days 2-4 (ASR, NLU, Dialogue)
- **[Days 5-8 Documentation](docs/day5_to_day8.md)**: Complete guide for Days 5-8 (Data Collection, Whisper, VAD, Pipeline)

### Data & Annotations
- **[Annotation Guidelines](data/annotations/annotation_guidelines.md)**: How to annotate data
- **[Entity Definitions](data/nlu/entities.json)**: Entity types and examples

### Reference (Coming Soon)
- **[Architecture Deep Dive](docs/architecture.md)**: Detailed architecture documentation
- **[API Reference](docs/api_reference.md)**: API documentation

## 🗓️ Development Roadmap

### Month 1: Foundation (Weeks 1-4)
- ✅ **Week 1 (Days 1-4)**: Project setup, data generation, annotation tools, baseline ASR, NLU models, dialogue system
- ✅ **Week 2 (Days 5-8)**: Real data collection tools, Whisper fine-tuning prep, expanded NLU training, VAD integration, end-to-end pipeline, CLI demo
- ⏳ **Week 3**: Large-scale data collection and annotation (500+ samples)
- ⏳ **Week 4**: Model training on full dataset, optimization

### Month 2: Core Development (Weeks 5-8)
- ⏳ **Week 5**: Whisper ASR fine-tuning on collected data
- ⏳ **Week 6**: Whisper evaluation and optimization
- ⏳ **Week 7**: NLU enhancement and advanced features
- ⏳ **Week 8**: Dialogue system improvements and context handling

### Month 3: Integration & Deployment (Weeks 9-12)
- ⏳ **Week 9**: End-to-end integration and comprehensive testing
- ⏳ **Week 10**: Android app development
- ⏳ **Week 11**: Testing, optimization, bug fixes
- ⏳ **Week 12**: Final deployment and documentation

## 🛠️ Technology Stack

- **Language**: Python 3.8+
- **ML Frameworks**: PyTorch, Transformers, scikit-learn
- **ASR**: Google Speech API, OpenAI Whisper
- **NLP**: NLTK, spaCy
- **Audio Processing**: librosa, soundfile, pydub
- **TTS**: gTTS, pyttsx3, Coqui TTS
- **Mobile**: Android (Java/Kotlin)
- **Tools**: Jupyter, pytest, black, flake8

## 📊 Current Status

**Days 1-8 Complete** ✅ (~20% Progress)

### Completed Components:

**Days 1-2: Foundation & Data Tools**
- ✅ Project structure created
- ✅ 1,000 sample queries generated
- ✅ Audio generation scripts
- ✅ Interactive annotation tool
- ✅ Annotation validator
- ✅ Progress tracker

**Days 2-3: ASR Pipeline**
- ✅ Google Cloud STT integration
- ✅ ASR evaluation (WER/CER)
- ✅ Whisper setup and dataset preparation
- ✅ Whisper configuration

**Day 3: NLU Models**
- ✅ Intent classifier (TF-IDF + SVM)
- ✅ Entity extractor (spaCy NER)
- ✅ NLU evaluation system
- ✅ Entity definitions

**Day 4: Dialogue System**
- ✅ Dialogue State Tracker
- ✅ Decision Manager (rule-based)
- ✅ NLG templates and generator

**Day 5: Real Data Collection**
- ✅ Real-time audio recording module
- ✅ Batch audio collection tool
- ✅ Audio cleaning and preprocessing
- ✅ ASR data preparation pipeline

**Day 6: Whisper Fine-Tuning Prep**
- ✅ Whisper manifest builder (JSONL format)
- ✅ Whisper training script (HuggingFace)
- ✅ Whisper evaluation dashboard

**Day 7: Expanded NLU Training**
- ✅ Multi-model intent classifier training
- ✅ spaCy NER training pipeline
- ✅ Unified NLU prediction API

**Day 8: End-to-End Integration**
- ✅ Voice Activity Detection (Silero VAD)
- ✅ Complete end-to-end pipeline
- ✅ Interactive CLI voice assistant

**Testing & Documentation**
- ✅ 76+ unit tests across all components
- ✅ Comprehensive documentation (Days 1-8)
- ✅ Logging utility
- ✅ Helper functions
- ✅ App configuration (YAML)

**Next Steps (Week 3)**:
- Collect 500-1000 real audio samples
- Fine-tune Whisper on collected data
- Optimize NLU models on full dataset
- Android app development begins

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Project Lead**: [Your Name]
- **Contributors**: [List contributors]

## 🙏 Acknowledgments

- OpenAI Whisper for ASR capabilities
- Hugging Face for transformer models
- Coqui TTS for speech synthesis
- The open-source community

## 📞 Contact

For questions, suggestions, or collaboration:
- **Email**: your.email@example.com
- **GitHub Issues**: [Create an issue](https://github.com/yourusername/vaani/issues)

---

**Built with ❤️ for the voice AI community**

*VAANI - Making voice interaction accessible to everyone*

