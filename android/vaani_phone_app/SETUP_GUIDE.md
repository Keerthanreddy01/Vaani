# Vaani Voice Assistant - Complete Setup Guide

## 🎯 What You're Building

A fully functional voice assistant that:
- **Listens continuously** for your custom wake word (like "Hey Google" or "Alexa")
- **Responds to commands** like "open WhatsApp", "call Mom", "what time is it"
- **Works hands-free** - no need to touch your phone
- **Customizable** - choose any wake word you want

## 📋 Prerequisites

### Required Software
1. **Android Studio** (Latest version)
   - Download: https://developer.android.com/studio
   
2. **Android Phone** (Physical device recommended)
   - Android 5.0+ (API 21+)
   - Microphone enabled
   - USB Debugging enabled

3. **Python 3.8+** (For backend server - optional but recommended)
   - Download: https://www.python.org/downloads/

## 🚀 Step-by-Step Setup

### Step 1: Clone and Open Project

```bash
# Navigate to the project
cd Vaani/android/vaani_phone_app

# Open in Android Studio
# File → Open → Select vaani_phone_app folder
```

### Step 2: Update MainActivity in AndroidManifest

Change the launcher activity to use the new UI:

```xml
<!-- In AndroidManifest.xml, replace OnboardingActivity with MainActivityNew -->
<activity
    android:name=".MainActivityNew"
    android:exported="true"
    android:screenOrientation="portrait">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>
```

### Step 3: Build and Install

1. **Connect your Android phone**
   ```bash
   # Enable USB Debugging on your phone
   # Settings → About Phone → Tap "Build Number" 7 times
   # Settings → Developer Options → Enable "USB Debugging"
   ```

2. **Build in Android Studio**
   - Click the **green play button** or press `Shift+F10`
   - Select your connected device
   - Wait for the build to complete

3. **Install on Phone**
   ```bash
   # Or use command line
   ./gradlew installDebug
   
   # Windows
   gradlew.bat installDebug
   ```

### Step 4: Grant Permissions

When the app launches, you'll need to grant several permissions:

1. **Microphone** - Required to hear your voice
2. **Phone** - To make calls
3. **SMS** - To send messages
4. **Contacts** - To find contacts
5. **Display over other apps** - For visual feedback
6. **Accessibility Service** - To control other apps

**Important**: Follow the prompts in the app to grant all permissions.

### Step 5: Configure Your Wake Word

1. **Open the app**
2. **Enter your custom wake word** (e.g., "Vaani", "Assistant", "Hey Phone")
3. **Click "Save"**
4. **Enable the service** using the toggle switch

### Step 6: Test It!

1. **Say your wake word**: "Vaani" (or whatever you chose)
2. **Listen for the response**: Phone will vibrate and say "Yes?"
3. **Give a command**: "Open WhatsApp"
4. **Watch it work!** 🎉

## 📱 Supported Commands

### App Control
- "Open [app name]" - Opens any installed app
- "Open WhatsApp" / "Open YouTube" / "Open Chrome"
- "Go back" - Press back button
- "Go home" - Go to home screen

### Phone Actions
- "Call [contact name]" - Make a phone call
- "Call [phone number]"
- "Send message to [contact]"

### System Control
- "What time is it?"
- "Scroll up" / "Scroll down"
- "Volume up" / "Volume down"
- "Take a photo"

### App Package Names
Common apps you can open:

| App | Package Name | Command Example |
|-----|--------------|-----------------|
| WhatsApp | com.whatsapp | "Open WhatsApp" |
| YouTube | com.google.android.youtube | "Open YouTube" |
| Chrome | com.android.chrome | "Open Chrome" |
| Gmail | com.google.android.gm | "Open Gmail" |
| Maps | com.google.android.apps.maps | "Open Maps" |
| Camera | com.android.camera | "Open Camera" |
| Phone | com.android.dialer | "Open Phone" |
| Messages | com.google.android.apps.messaging | "Open Messages" |

## 🔧 Troubleshooting

### Wake Word Not Detected

**Problem**: Service runs but doesn't hear wake word

**Solutions**:
1. Check microphone permission granted
2. Speak clearly and loudly
3. Try a longer wake word (2+ syllables)
4. Check device volume and microphone

### Speech Model Download Fails

**Problem**: "Downloading speech model..." stuck

**Solutions**:
1. Ensure internet connection
2. Wait 2-3 minutes for download
3. Restart the app
4. Manually download model:
   ```bash
   # Download from: https://alphacephei.com/vosk/models
   # Model: vosk-model-small-en-us-0.15
   # Place in: /sdcard/Android/data/com.vaani.phone/files/models/
   ```

### App Commands Don't Work

**Problem**: Wake word detected but commands fail

**Solutions**:
1. **Enable Accessibility Service**
   - Settings → Accessibility → Vaani Voice Assistant → Enable
2. Check app is installed
3. Use exact package name for apps

### Service Stops After Phone Sleep

**Problem**: Service stops working after screen off

**Solutions**:
1. **Disable Battery Optimization**
   - Settings → Apps → Vaani → Battery → Unrestricted
2. **Enable Autostart** (varies by manufacturer)
   - Settings → Apps → Vaani → Autostart → Enable

## 🏗️ Architecture Overview

```
User Says Wake Word
        ↓
WakeWordDetector (Continuous Listening)
        ↓
Wake Word Matched
        ↓
VaaniService Activates
        ↓
Listen for Command (10 seconds)
        ↓
Speech Recognition (Vosk)
        ↓
Command Text
        ↓
IntentClassifier (Parse Intent)
        ↓
ActionExecutor (Execute Action)
        ↓
Feedback (TTS + Vibration)
```

## 🔨 Building from Source

### Full Build

```bash
cd Vaani/android/vaani_phone_app

# Clean build
./gradlew clean

# Build debug APK
./gradlew assembleDebug

# Install to device
./gradlew installDebug

# Build + Install + Run
./gradlew installDebug
adb shell am start -n com.vaani.phone/.MainActivityNew
```

### Generate Signed APK

```bash
# Create keystore (first time only)
keytool -genkey -v -keystore vaani.keystore -alias vaani -keyalg RSA -keysize 2048 -validity 10000

# Build signed release
./gradlew assembleRelease

# APK location
# app/build/outputs/apk/release/app-release.apk
```

## 🐍 Python Backend (Optional)

For advanced features, run the Python backend:

```bash
cd Vaani/

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run backend server
python pipeline/android_bridge/server.py
```

The backend enables:
- Advanced NLU (Natural Language Understanding)
- Custom intent training
- Multi-turn dialogue
- Context-aware responses

## 📊 Testing Checklist

- [ ] App installs successfully
- [ ] All permissions granted
- [ ] Wake word can be customized
- [ ] Service starts and shows notification
- [ ] Wake word detection works
- [ ] Phone vibrates and responds
- [ ] Commands are recognized
- [ ] Apps open correctly
- [ ] Phone calls work
- [ ] Back/home gestures work
- [ ] Service survives phone sleep
- [ ] Service restarts after reboot

## 🎓 Development Tips

### Adding New Commands

1. **Add intent to `VaaniIntentClassifier.kt`**
2. **Add action to `VaaniActionExecutor.kt`**
3. **Test with voice command**

### Improving Wake Word Detection

- Use 2-3 syllable words
- Avoid common words (reduces false positives)
- Train custom wake word model (advanced)

### Debugging

```bash
# View Android logs
adb logcat | grep -i vaani

# Check service status
adb shell dumpsys activity services | grep -i vaani

# Test speech recognition
adb shell am start -n com.vaani.phone/.MainActivityNew
```

## 📚 Additional Resources

- **Vosk Speech Recognition**: https://alphacephei.com/vosk/
- **Android Accessibility**: https://developer.android.com/guide/topics/ui/accessibility
- **Android Speech API**: https://developer.android.com/reference/android/speech/package-summary

## 🤝 Support

**Issues?** Check the troubleshooting section above or create an issue on GitHub.

**Want to customize?** All source code is in `app/src/main/java/com/vaani/phone/`

## 🎉 You're Ready!

Your phone is now a fully functional voice assistant. Say your wake word and start commanding your phone with your voice!

**Example Session:**
```
You: "Vaani"
Phone: *vibrates* "Yes?"
You: "Open WhatsApp"
Phone: "Opening app" *WhatsApp opens*
```

Enjoy your personal voice assistant! 🎙️
