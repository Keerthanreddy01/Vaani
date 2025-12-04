# VAANI Phone App - Full Native Implementation

Complete voice assistant that runs 100% on your Android phone.

## Features

✅ **100% Phone-Native**
- Microphone input from phone
- On-device speech recognition (Vosk)
- On-device intent classification
- On-device text-to-speech
- All processing happens on phone
- NO laptop required

✅ **Full Voice Control**
- Open apps
- Make calls
- Send messages
- Navigate UI
- Read screen
- Control system settings

✅ **Offline Capable**
- Works without internet (after initial model download)
- Fast processing on device
- Privacy-friendly (no data sent to cloud)

## Installation

### Quick Install
```bash
cd android/vaani_phone_app
gradlew.bat assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

### Manual Build
1. Open project in Android Studio
2. Build -> Build APK
3. Install APK on phone

## Permissions Required

The app will request these permissions:
- 🎤 **Microphone** - To hear your voice commands
- 📱 **Accessibility Service** - To control phone (open apps, tap, etc.)
- 📞 **Phone** - To make calls
- 💬 **SMS** - To send messages
- 📧 **Contacts** - To find contacts by name

## First Time Setup

1. **Install the app**
2. **Grant all permissions**
3. **Enable Accessibility Service**:
   - Settings -> Accessibility -> VAANI -> Enable
4. **Download speech model** (first launch only):
   - App will download ~40MB Vosk model
   - Wait for "Ready" message
5. **Start using!**

## Usage

1. Open VAANI app
2. Tap "Start Listening"
3. Say your command
4. Watch it execute!

## Example Commands

### Apps
- "Open WhatsApp"
- "Open Chrome"
- "Open Camera"

### Communication
- "Call John"
- "Call 1234567890"
- "Send message to John saying hello"

### Navigation
- "Go back"
- "Go home"
- "Scroll down"
- "Swipe left"

### Information
- "Read the screen"
- "What's on the screen?"

### System
- "Volume up"
- "Brightness down"

## Architecture

```
┌─────────────────────────────────────┐
│         VAANI Phone App             │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────┐    ┌──────────┐      │
│  │ Record   │───>│   Vosk   │      │
│  │ Audio    │    │   ASR    │      │
│  └──────────┘    └──────────┘      │
│       │               │             │
│       v               v             │
│  ┌──────────────────────────┐      │
│  │   Intent Classifier      │      │
│  │   (Rule-based + ML)      │      │
│  └──────────────────────────┘      │
│               │                     │
│               v                     │
│  ┌──────────────────────────┐      │
│  │   Action Executor        │      │
│  │   (Accessibility API)    │      │
│  └──────────────────────────┘      │
│               │                     │
│               v                     │
│  ┌──────────────────────────┐      │
│  │   Android TTS            │      │
│  └──────────────────────────┘      │
│                                     │
└─────────────────────────────────────┘
```

## Components

### 1. VaaniMainActivity
- Main UI
- Start/stop button
- Status display
- Permission handling

### 2. VaaniAccessibilityService
- Phone control via Accessibility API
- Tap, swipe, scroll
- Open apps
- Read screen text

### 3. VaaniVoiceService
- Microphone recording
- Vosk ASR integration
- Continuous listening
- Background service

### 4. VaaniIntentClassifier
- Parse voice commands
- Extract intents
- Extract entities (app names, phone numbers, etc.)
- Rule-based + simple ML

### 5. VaaniActionExecutor
- Route intents to actions
- Execute via Accessibility Service
- Handle responses
- TTS feedback

## Technical Details

### Speech Recognition
- **Engine**: Vosk (offline)
- **Model**: vosk-model-small-en-us-0.15 (~40MB)
- **Sample Rate**: 16kHz
- **Format**: PCM 16-bit mono

### Intent Classification
- **Method**: Keyword matching + simple patterns
- **Intents**: ~25 intents supported
- **Entities**: App names, phone numbers, directions, etc.

### Text-to-Speech
- **Engine**: Android TTS
- **Language**: English (US)
- **Fallback**: System default

### Accessibility Service
- **API Level**: 21+ (Android 5.0+)
- **Capabilities**: Full UI control
- **Permissions**: BIND_ACCESSIBILITY_SERVICE

## File Structure

```
android/vaani_phone_app/
├── app/
│   ├── build.gradle
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── java/com/vaani/phone/
│       │   ├── MainActivity.kt
│       │   ├── VaaniAccessibilityService.kt
│       │   ├── VaaniVoiceService.kt
│       │   ├── VaaniIntentClassifier.kt
│       │   ├── VaaniActionExecutor.kt
│       │   └── VoskManager.kt
│       └── res/
│           ├── layout/
│           │   └── activity_main.xml
│           └── xml/
│               └── accessibility_service_config.xml
├── build.gradle
└── settings.gradle
```

## Troubleshooting

### App crashes on start
- Check Android version (requires 5.0+)
- Grant all permissions
- Check logcat: `adb logcat | grep VAANI`

### Speech not recognized
- Speak clearly
- Check microphone permission
- Wait for "Listening..." status
- Try simple commands first

### Actions don't execute
- Enable Accessibility Service
- Grant all required permissions
- Check if target app is installed

### TTS not working
- Install a TTS engine (Google TTS recommended)
- Set default TTS in Android settings

## Development

### Building from Source
```bash
cd android/vaani_phone_app
gradlew.bat assembleDebug
```

### Installing Dev Build
```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

### Viewing Logs
```bash
adb logcat | grep VAANI
```

## License

Part of the VAANI project.
