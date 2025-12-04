@echo off
echo ========================================
echo Building VAANI Voice App
echo ========================================
echo.

cd vaani_voice_app

echo Checking Android SDK...
if not exist "%ANDROID_HOME%\build-tools" (
    if exist "C:\Users\keert\AppData\Local\Android\Sdk" (
        set ANDROID_HOME=C:\Users\keert\AppData\Local\Android\Sdk
    ) else (
        echo ERROR: Android SDK not found
        echo Please install Android Studio first
        pause
        exit /b 1
    )
)

echo.
echo Compiling Kotlin files...
"%ANDROID_HOME%\build-tools\33.0.0\aapt2" compile -o compiled\ app\src\main\res\layout\activity_main.xml

echo.
echo Building APK...
echo This requires Android Studio. Opening project...
start "" "C:\Program Files\Android\Android Studio\bin\studio64.exe" "%CD%"

echo.
echo ========================================
echo Please wait for Android Studio to open
echo Then click: Build → Build APK
echo ========================================
pause
