# 🎙️ Vaani Voice Assistant - User Guide

## Welcome to Vaani!

Your phone is now a fully functional voice assistant that responds to your voice commands 24/7. This guide will help you get started and make the most of your new assistant.

## 🚀 Quick Start (5 Minutes)

### 1. First Launch

When you open Vaani for the first time:
- You'll see a clean, modern interface
- The service will be **OFF** by default
- You'll need to grant permissions

### 2. Set Your Wake Word

**What is a wake word?**
Think of it like "Hey Google" or "Alexa" - it's the word that activates your assistant.

**Steps:**
1. Find the "Wake Word" section
2. Type any name you like (examples below)
3. Click **"Save"**

**Wake Word Ideas:**
- `Vaani` - Original name
- `Assistant` - Professional
- `Jarvis` - Iron Man style
- `Computer` - Star Trek style
- `Hey Phone` - Simple and clear
- Your own name
- Anything 2+ characters

### 3. Grant Permissions

Click **"Check Permissions"** and follow the prompts:

✅ **Microphone** - So Vaani can hear you
✅ **Phone** - To make calls for you
✅ **SMS** - To send messages
✅ **Contacts** - To find your contacts
✅ **Display over apps** - For visual feedback
✅ **Accessibility** - To control other apps

**Why so many permissions?**
Vaani needs to control your phone to execute commands. These permissions enable features like opening apps, making calls, and navigating your phone.

### 4. Enable the Service

Toggle the **Service Switch** to **ON**

You should see:
- Green status text: "✓ Listening for [your wake word]"
- A notification: "Vaani is listening"

### 5. Test It!

**Say:** "[Your wake word]"
**Wait for:** Vibration + "Yes?"
**Then say:** "Open WhatsApp"
**Watch:** WhatsApp opens automatically! 🎉

## 📱 How to Use Vaani

### Basic Pattern

All commands follow this simple pattern:

```
[WAKE WORD] + [COMMAND]
```

**Examples:**
```
"Vaani, open WhatsApp"
"Vaani, call Mom"
"Vaani, what time is it"
```

### Visual Feedback

When Vaani hears you:
1. **Phone vibrates** (haptic feedback)
2. **"Yes?"** spoken response
3. **Listening indicator** appears
4. **Command text** shows what it heard
5. **Action confirmation** after execution

## 🎯 Complete Command List

### 📱 Opening Apps

**Pattern:** "[Wake word], open [app name]"

```
"Vaani, open WhatsApp"
"Vaani, launch YouTube"
"Vaani, start Chrome"
"Vaani, open Camera"
```

**Supported Apps:**
- WhatsApp
- YouTube
- Chrome
- Gmail
- Maps
- Instagram
- Facebook
- Spotify
- Camera
- Settings
- Calculator
- Calendar
- Messages
- Phone
- Contacts
- Any installed app!

### 📞 Phone Calls

**Pattern:** "[Wake word], call [contact/number]"

```
"Vaani, call Mom"
"Vaani, call John Smith"
"Vaani, call 555-1234"
```

### 💬 Messaging

**Pattern:** "[Wake word], send message to [contact]"

```
"Vaani, send message to Sarah"
"Vaani, text Mike"
```

*Note: This opens the messaging app with the contact pre-selected. You can then dictate or type your message.*

### 🧭 Navigation

```
"Vaani, go back"        → Press back button
"Vaani, go home"        → Go to home screen
"Vaani, scroll down"    → Scroll page down
"Vaani, scroll up"      → Scroll page up
```

### ⏰ Information

```
"Vaani, what time is it?"
"Vaani, what's the date?"
"Vaani, what's the weather?"
```

### 🎵 Media Control

```
"Vaani, volume up"
"Vaani, volume down"
"Vaani, take a photo"
"Vaani, play music"
```

### 🔧 System Control

```
"Vaani, brightness up"
"Vaani, brightness down"
"Vaani, open settings"
```

### 🆘 Emergency

```
"Vaani, emergency!"
"Vaani, call 911!"
```

*This is the HIGHEST priority command and will execute immediately.*

## 💡 Pro Tips

### 1. **Speak Clearly**
- Use a normal speaking voice
- Don't whisper or shout
- Pause briefly after the wake word

### 2. **Avoid Background Noise**
- Works best in quiet environments
- Reduce TV/music volume when giving commands
- Move away from noisy areas

### 3. **Use Natural Language**
You can vary how you say things:
- "Open WhatsApp" ✓
- "Launch WhatsApp" ✓
- "Start WhatsApp" ✓
- "Go to WhatsApp" ✓

### 4. **Battery Optimization**
For 24/7 listening, disable battery optimization:
1. Settings → Apps → Vaani
2. Battery → Unrestricted
3. This prevents the service from stopping

### 5. **Custom Apps**
To open apps not in the default list:
- Find the app's package name
- Say: "[Wake word], open [package name]"

## 🔧 Troubleshooting

### Wake Word Not Detected

**Symptom:** Service is on but nothing happens when you say wake word

**Solutions:**
1. ✅ Check microphone permission granted
2. ✅ Speak louder and clearer
3. ✅ Try a different wake word (longer is better)
4. ✅ Check notification is showing
5. ✅ Restart the service (toggle off/on)
6. ✅ Restart the app

### Commands Don't Execute

**Symptom:** Wake word works but commands fail

**Solutions:**
1. ✅ Enable Accessibility Service
   - Settings → Accessibility → Vaani → Enable
2. ✅ Check app is installed
3. ✅ Grant required permissions
4. ✅ Try simpler commands first

### Service Stops Working

**Symptom:** Works for a while then stops

**Solutions:**
1. ✅ Disable battery optimization (see Pro Tips)
2. ✅ Enable auto-start (varies by manufacturer)
3. ✅ Lock app in recent apps (prevent accidental closure)
4. ✅ Check notification still showing

### Poor Recognition

**Symptom:** Often misunderstands commands

**Solutions:**
1. ✅ Speak at normal pace (not too fast)
2. ✅ Reduce background noise
3. ✅ Wait for "Yes?" before giving command
4. ✅ Use simpler, direct commands
5. ✅ Ensure speech model fully downloaded

### Battery Drain

**Symptom:** Battery depletes faster

**Why:** Continuous microphone listening uses power

**Solutions:**
1. Toggle service off when not needed
2. Use only when actively needed
3. Modern phones handle this well - usually minimal impact

## 🎓 Advanced Features

### Backend Server (Optional)

For advanced NLU and context-aware responses:

1. **Start Python backend:**
   ```bash
   cd Vaani
   python pipeline/android_bridge/vaani_backend_server.py
   ```

2. **Configure Android app to use server**
   - Settings → Backend Server
   - Enter: `http://[your-computer-ip]:8080`

**Benefits:**
- Better intent understanding
- Context-aware conversations
- Multi-turn dialogues
- Custom trained models

### Custom Commands

Add your own commands by modifying:
- `VaaniIntentClassifier.kt` - Add new intents
- `VaaniActionExecutor.kt` - Add new actions

### Multiple Languages

Vaani supports multilingual commands:
- English: "Open WhatsApp"
- Hindi: "WhatsApp खोलो"
- Telugu: "WhatsApp తెరువు"

## 📊 Understanding the Interface

### Main Screen

**Wake Word Section:**
- Input field to customize your wake word
- Shows current active wake word
- Save button to apply changes
- Test button for guidance

**Service Status:**
- Toggle switch to enable/disable
- Status text shows current state
- Green = Running, Red = Stopped

**Quick Actions:**
- Check Permissions - Review and grant needed permissions
- How to Use - Opens this guide

**Example Commands:**
- Reference list of common commands

### Notifications

**While Running:**
- Persistent notification shows Vaani is listening
- Shows current status
- Tap to open app

**During Command:**
- Status updates to "Processing..."
- Shows recognized command

## 🔒 Privacy & Security

**Your voice data:**
- Processed **locally** on your device
- NOT sent to any servers (unless you enable backend)
- NOT stored permanently
- NOT shared with anyone

**Permissions:**
- Used ONLY for stated features
- Can revoke anytime in Settings
- App cannot access other data

**Wake Word:**
- Stored locally in app preferences
- Only you know it
- Change anytime

## 🆘 Need Help?

### Common Issues
- See Troubleshooting section above

### Reset Everything
1. Stop the service
2. Clear app data (Settings → Apps → Vaani → Clear Data)
3. Relaunch and setup again

### Still Stuck?
- Check the GitHub issues
- Create a new issue with details
- Include Android version, device model, error logs

## 🎉 Success Checklist

Before calling Vaani "working", verify:

- [ ] App installs without errors
- [ ] All permissions granted
- [ ] Wake word saved
- [ ] Service shows as running
- [ ] Wake word triggers response ("Yes?")
- [ ] At least one command works (e.g., "go home")
- [ ] Apps can be opened by voice
- [ ] Service survives screen lock
- [ ] Notification persists

## 🚀 You're All Set!

Congratulations! You now have a fully functional voice assistant on your phone.

**Quick reminder:**
1. Say your wake word
2. Wait for "Yes?"
3. Give your command
4. Watch it execute!

Enjoy hands-free control of your phone! 🎙️📱

---

**Version:** 1.0.0
**Last Updated:** December 2025
**Questions?** Check the troubleshooting section or visit our GitHub
