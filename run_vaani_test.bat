@echo off
echo ========================================
echo VAANI - Voice Command Tester
echo ========================================
echo.
echo Your Vivo phone is connected!
echo Testing voice-activated commands...
echo.

:menu
cls
echo ========================================
echo VAANI VOICE COMMAND SIMULATOR
echo ========================================
echo.
echo This simulates what the app will do when you speak:
echo.
echo 1. Test "Open WhatsApp"
echo 2. Test "Open Chrome"
echo 3. Test "Open Gmail"
echo 4. Test "Open YouTube"
echo 5. Test "Go Home"
echo 6. Exit
echo.
set /p choice="Enter command number (1-6): "

if "%choice%"=="1" (
    echo.
    echo 🎤 You said: "Open WhatsApp"
    echo ✅ Opening WhatsApp on your phone...
    C:\Users\keert\AppData\Local\Android\Sdk\platform-tools\adb.exe shell am start -n com.whatsapp/.HomeActivity
    timeout /t 2 > nul
    goto menu
)

if "%choice%"=="2" (
    echo.
    echo 🎤 You said: "Open Chrome"
    echo ✅ Opening Chrome on your phone...
    C:\Users\keert\AppData\Local\Android\Sdk\platform-tools\adb.exe shell am start -n com.android.chrome/com.google.android.apps.chrome.Main
    timeout /t 2 > nul
    goto menu
)

if "%choice%"=="3" (
    echo.
    echo 🎤 You said: "Open Gmail"
    echo ✅ Opening Gmail on your phone...
    C:\Users\keert\AppData\Local\Android\Sdk\platform-tools\adb.exe shell am start -n com.google.android.gm/.ConversationListActivityGmail
    timeout /t 2 > nul
    goto menu
)

if "%choice%"=="4" (
    echo.
    echo 🎤 You said: "Open YouTube"
    echo ✅ Opening YouTube on your phone...
    C:\Users\keert\AppData\Local\Android\Sdk\platform-tools\adb.exe shell am start -n com.google.android.youtube/.HomeActivity
    timeout /t 2 > nul
    goto menu
)

if "%choice%"=="5" (
    echo.
    echo 🎤 You said: "Go Home"
    echo ✅ Going to home screen...
    C:\Users\keert\AppData\Local\Android\Sdk\platform-tools\adb.exe shell input keyevent KEYCODE_HOME
    timeout /t 2 > nul
    goto menu
)

if "%choice%"=="6" (
    echo.
    echo Exiting...
    exit /b 0
)

echo Invalid choice!
timeout /t 1 > nul
goto menu
