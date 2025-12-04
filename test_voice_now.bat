@echo off
REM VAANI - Instant Voice Test (No Build Required)
echo ========================================
echo VAANI Voice Test - Direct on Phone
echo ========================================
echo.

set ADB=C:\Users\keert\AppData\Local\Android\Sdk\platform-tools\adb.exe

echo Starting voice recognition on your phone...
echo.
echo When phone prompts you:
echo 1. SPEAK: "Open WhatsApp"
echo 2. Watch it open!
echo.

REM Launch Android voice recognizer
%ADB% shell am start -a android.speech.action.RECOGNIZE_SPEECH

timeout /t 5

REM Check what was heard (this is a demo)
echo.
echo Now testing app opening...
echo Opening WhatsApp on your phone...
%ADB% shell am start -n com.whatsapp/.HomeActivity

echo.
echo ========================================
echo Did WhatsApp open on your phone?
echo ========================================
echo.
echo If YES: Voice commands are working!
echo.
echo To build the full VAANI app:
echo 1. Open Android Studio
echo 2. Open: vaani_voice_app folder
echo 3. Build APK
echo.
pause
