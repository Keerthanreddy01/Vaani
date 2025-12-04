
package com.vaani.service

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.speech.tts.TextToSpeech
import android.util.Log
import java.util.Locale

class TTSService : Service(), TextToSpeech.OnInitListener {

    private val TAG = "TTSService"
    private lateinit var tts: TextToSpeech

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "TTSService created")
        tts = TextToSpeech(this, this)
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            Log.d(TAG, "TTS Engine initialized successfully")
            // TODO: Set language based on user preference
            tts.language = Locale.US
        } else {
            Log.e(TAG, "Failed to initialize TTS Engine")
        }
    }

    fun speak(text: String) {
        if (::tts.isInitialized) {
            tts.speak(text, TextToSpeech.QUEUE_ADD, null, null)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        if (::tts.isInitialized) {
            tts.stop()
            tts.shutdown()
        }
        Log.d(TAG, "TTSService destroyed")
    }

    override fun onBind(intent: Intent?): IBinder? {
        return null
    }
}
