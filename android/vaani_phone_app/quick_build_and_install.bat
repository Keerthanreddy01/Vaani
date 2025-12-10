@echo off
REM Vaani Voice Assistant - Quick Build and Deploy Script for Windows

echo ================================
echo Vaani Voice Assistant Builder
echo ================================
echo.

REM Check if we're in the right directory
if not exist "app\build.gradle" (
    echo ERROR: Must be run from vaani_phone_app directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Step 1: Checking for connected Android device...
adb devices

echo.
echo Step 2: Cleaning previous build...
call gradlew.bat clean

echo.
echo Step 3: Building debug APK...
call gradlew.bat assembleDebug

if errorlevel 1 (
    echo.
    echo BUILD FAILED!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo Step 4: Installing APK to device...
call gradlew.bat installDebug

if errorlevel 1 (
    echo.
    echo INSTALL FAILED!
    echo Make sure:
    echo  1. Your phone is connected via USB
    echo  2. USB Debugging is enabled
    echo  3. You've authorized this computer on your phone
    pause
    exit /b 1
)

echo.
echo Step 5: Launching app...
adb shell am start -n com.vaani.phone/.MainActivityNew

echo.
echo ================================
echo SUCCESS!
echo ================================
echo.
echo Vaani has been installed and launched on your device!
echo.
echo Next steps:
echo  1. Grant all requested permissions
echo  2. Set your custom wake word
echo  3. Enable the service toggle
echo  4. Say your wake word and give a command!
echo.
echo Example: "Vaani, open WhatsApp"
echo.
pause
