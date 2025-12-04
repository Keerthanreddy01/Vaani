# COMPLETE PROMPT FOR ANDROID STUDIO AGENT

Copy and paste this entire prompt to an AI agent in Android Studio:

---

I need you to complete and fix the VAANI voice assistant Android app so it runs properly on my Vivo V2050 phone (Android 13).

## PROJECT LOCATION
`C:\Users\keert\Desktop\Vaani\android\vaani_app`

## WHAT I HAVE
The project structure is already created with these files:
- `app/src/main/AndroidManifest.xml`
- `app/src/main/java/com/vaani/assistant/VaaniVoiceService.kt`
- `app/src/main/java/com/vaani/assistant/WakeWordDetector.kt`
- `app/src/main/java/com/vaani/assistant/ASREngine.kt`
- `app/src/main/java/com/vaani/assistant/NLUEngine.kt`
- `app/src/main/java/com/vaani/assistant/ActionExecutor.kt`
- `app/src/main/java/com/vaani/assistant/OverlayManager.kt`
- `app/src/main/java/com/vaani/assistant/MainActivity.kt`
- `app/src/main/res/layout/activity_main.xml`
- `app/build.gradle`
- `build.gradle`
- `settings.gradle`

## WHAT I NEED YOU TO DO

### 1. FIX ALL COMPILATION ERRORS
- Fix any missing imports
- Fix any syntax errors
- Add missing resource IDs in `activity_main.xml`
- Add missing `R.java` references
- Fix any Gradle sync issues

### 2. ADD MISSING RESOURCES
Create these if missing:
- `app/src/main/res/values/strings.xml`
- `app/src/main/res/values/colors.xml`
- `app/src/main/res/values/themes.xml`
- App icons in `res/mipmap/`

### 3. FIX THE ASR ENGINE
The `ASREngine.kt` currently has a mock implementation. Fix it to use one of:
- **Android SpeechRecognizer API** (preferred for simplicity)
- OR local speech recognition
- Make it actually transcribe the audio bytes passed to it

### 4. IMPROVE WAKE WORD DETECTION
The current `WakeWordDetector.kt` is too simple. Make it:
- More accurate in detecting "Hey Vaani"
- Use proper audio analysis
- Reduce false positives

### 5. ENSURE ALL COMPONENTS WORK
Make sure:
- `VaaniVoiceService` starts properly
- `AudioRecord` captures phone microphone
- Wake word detection triggers correctly
- ASR transcribes speech
- NLU classifies intents
- ActionExecutor executes commands
- OverlayManager shows feedback

### 6. ADD PROPER ERROR HANDLING
- Add try-catch blocks
- Handle permission denials gracefully
- Show user-friendly error messages

### 7. TEST THESE COMMANDS
Ensure the app can handle:
- "Hey Vaani, open WhatsApp"
- "Hey Vaani, open Chrome"
- "Hey Vaani, go home"
- "Hey Vaani, volume up"
- "Hey Vaani, brightness up"

### 8. BUILD AND TEST
After fixing everything:
1. Sync Gradle
2. Build APK: `Build → Build Bundle(s) / APK(s) → Build APK(s)`
3. Verify it compiles with no errors

## IMPORTANT REQUIREMENTS

### ✅ MUST USE PHONE MICROPHONE ONLY
```kotlin
// In VaaniVoiceService.kt
audioRecord = AudioRecord(
    MediaRecorder.AudioSource.VOICE_RECOGNITION,  // ← Phone mic
    SAMPLE_RATE,
    CHANNEL_CONFIG,
    AUDIO_FORMAT,
    bufferSize
)
```

### ✅ EVERYTHING RUNS ON PHONE
- NO laptop microphone
- NO PC audio streaming
- ALL processing on Android device
- Like Google Assistant architecture

### ✅ PROPER PERMISSIONS
Ensure AndroidManifest.xml has all needed permissions and they're requested at runtime in MainActivity.

### ✅ FOREGROUND SERVICE
Ensure VaaniVoiceService runs as a proper foreground service with notification.

## CRITICAL FIXES NEEDED

### Fix 1: ASREngine.kt
Replace the mock `transcribe()` method with actual Android SpeechRecognizer:

```kotlin
suspend fun transcribe(audioData: ByteArray): String = withContext(Dispatchers.Main) {
    suspendCancellableCoroutine { continuation ->
        val recognizer = SpeechRecognizer.createSpeechRecognizer(context)
        
        recognizer.setRecognitionListener(object : RecognitionListener {
            override fun onResults(results: Bundle?) {
                val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                val transcript = matches?.get(0) ?: ""
                continuation.resume(transcript)
            }
            
            override fun onError(error: Int) {
                continuation.resume("")
            }
            
            // Other required overrides...
        })
        
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-IN")
        }
        
        recognizer.startListening(intent)
    }
}
```

### Fix 2: Add Missing Resources
Create `app/src/main/res/values/strings.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">VAANI</string>
</resources>
```

### Fix 3: Fix activity_main.xml Resource IDs
Ensure all IDs referenced in MainActivity.kt exist in the XML.

## OUTPUT I EXPECT

After you complete this, I should be able to:
1. Open project in Android Studio
2. Click Build → Build APK
3. See "BUILD SUCCESSFUL"
4. Install on phone: `adb install -r app/build/outputs/apk/debug/app-debug.apk`
5. Open VAANI app on phone
6. Grant permissions
7. Tap "Start VAANI"
8. Say "Hey Vaani, open WhatsApp"
9. See WhatsApp open on phone

## VERIFY EVERYTHING WORKS

Make sure:
- ✅ No compilation errors
- ✅ All resources exist
- ✅ Gradle syncs successfully
- ✅ APK builds successfully
- ✅ App installs on Android 13
- ✅ Microphone captures audio from phone
- ✅ Service runs in foreground
- ✅ Wake word detection works
- ✅ Speech recognition works
- ✅ Actions execute on phone

## DEVICE INFO
- Device: Vivo V2050
- Android: 13
- Device ID: 96346669290005H

## FINAL CHECK

Before you're done, run through this checklist:
- [ ] Project syncs in Android Studio
- [ ] No red errors in code
- [ ] Build APK succeeds
- [ ] All permissions in manifest
- [ ] AudioRecord uses phone microphone
- [ ] Service starts and shows notification
- [ ] Wake word detector works
- [ ] ASR transcribes speech (not mock)
- [ ] Actions execute on phone
- [ ] Overlay shows on screen

---

Please fix all issues and make the app fully functional. Show me what you fixed and confirm when it's ready to build and test.
