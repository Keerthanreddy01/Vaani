# VAANI Overlay - Visual Feedback System

A floating overlay that shows VAANI's status on your Android phone screen.

## Features

- **Floating Status Indicator**: Small colored dot that appears on top of all apps
- **Real-time Status Updates**: Changes color based on VAANI's current state
- **Non-intrusive**: Doesn't block touches, auto-hides when idle
- **Always Visible**: Works even when phone is locked or other apps are open

## Status Colors

- 🔵 **Blue (Pulsing)** = Listening to your voice
- 🟡 **Yellow (Pulsing)** = Processing your command
- 🟣 **Purple** = Speaking response
- 🟢 **Green** = Action executed successfully
- 🔴 **Red** = Error occurred
- ⚫ **Hidden** = Idle (auto-hides after 5 seconds)

## Building the APK

### Option 1: Using Android Studio (Recommended)

1. Install Android Studio
2. Open project: `android/vaani_overlay`
3. Wait for Gradle sync to complete
4. Build -> Build Bundle(s) / APK(s) -> Build APK(s)
5. APK will be at: `app/build/outputs/apk/debug/app-debug.apk`

### Option 2: Using Command Line

```bash
cd android/vaani_overlay
gradlew.bat assembleDebug
```

## Installing on Phone

### Automatic Installation

Run from project root:
```bash
deploy_overlay_to_phone.bat
```

### Manual Installation

```bash
adb install -r android/vaani_overlay/app/build/outputs/apk/debug/app-debug.apk
```

## Granting Permissions

1. Open the VAANI Overlay app on your phone
2. Tap "Start Overlay Service"
3. You'll be prompted to grant "Display over other apps" permission
4. Enable the permission
5. Return to the app and tap "Start Overlay Service" again
6. You should see a small blue dot appear on your screen

## Using with VAANI

Once the overlay is running:

1. Run VAANI in phone mode:
   ```bash
   python run_vaani_phone.py
   ```

2. The overlay will automatically connect and show status updates

3. Speak commands and watch the dot change colors!

## Troubleshooting

### Overlay doesn't appear
- Make sure you granted "Display over other apps" permission
- Check if the service is running: Settings -> Apps -> VAANI Overlay -> Force Stop, then restart

### Colors don't change
- Check if port 8766 is forwarded: `adb forward tcp:8766 tcp:8766`
- Restart the overlay service
- Check VAANI logs for connection errors

### App crashes
- Check Android version (requires Android 5.0+)
- Check logcat: `adb logcat | grep VAANI`

## Technical Details

- **Communication**: Socket connection on port 8766
- **Port Forwarding**: ADB forwards localhost:8766 to phone
- **Protocol**: Simple text commands (LISTENING, PROCESSING, etc.)
- **Overlay Type**: TYPE_APPLICATION_OVERLAY (Android 8.0+) or TYPE_PHONE (older)
- **Permissions**: SYSTEM_ALERT_WINDOW, INTERNET

## Architecture

```
Python (Laptop)                    Android (Phone)
┌─────────────────┐               ┌──────────────────┐
│ run_vaani_phone │               │ VaaniOverlayService│
│                 │               │                  │
│ PhoneOverlay    │──Socket───────│ ServerSocket     │
│ Notifier        │  Port 8766    │ (Port 8766)      │
│                 │               │                  │
│ send("LISTENING")│──────────────>│ showStatus(BLUE) │
│ send("PROCESSING")│─────────────>│ showStatus(YELLOW)│
│ send("ACTION_OK")│──────────────>│ showStatus(GREEN)│
└─────────────────┘               └──────────────────┘
```

## Files

- `VaaniOverlayService.kt` - Main service that manages the overlay
- `MainActivity.kt` - UI for starting/stopping the service
- `VaaniBroadcastReceiver.kt` - Handles boot and start intents
- `overlay_bubble.xml` - Layout for the floating dot
- `circle.xml` - Drawable for the dot shape

## License

Part of the VAANI project.

