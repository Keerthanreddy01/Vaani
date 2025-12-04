#!/bin/bash
# VAANI Phone App - Quick Build Script
# Just builds the APK without deploying

echo "========================================"
echo "VAANI PHONE APP - QUICK BUILD"
echo "========================================"
echo ""

echo "[1/2] Building APK..."
cd android/vaani_phone_app

if [ ! -f "gradlew" ]; then
    echo "[ERROR] gradlew not found!"
    exit 1
fi

chmod +x gradlew
./gradlew assembleDebug

if [ $? -ne 0 ]; then
    echo "[ERROR] Build failed!"
    exit 1
fi

echo "[OK] Build successful!"
echo ""

echo "[2/2] APK location:"
APK_PATH="app/build/outputs/apk/debug/app-debug.apk"

if [ -f "$APK_PATH" ]; then
    echo "[OK] APK ready at: $APK_PATH"
    echo ""
    echo "To install: adb install -r $APK_PATH"
else
    echo "[ERROR] APK not found!"
    exit 1
fi

cd ../..

echo ""
echo "========================================"
echo "BUILD COMPLETE!"
echo "========================================"
