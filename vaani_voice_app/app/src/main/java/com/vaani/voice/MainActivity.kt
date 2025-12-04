package com.vaani.voice

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import java.util.*

class MainActivity : AppCompatActivity() {

    private lateinit var statusText: TextView
    private lateinit var listenButton: Button
    private lateinit var speechRecognizer: SpeechRecognizer
    private lateinit var tts: TextToSpeech

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        statusText = findViewById(R.id.status_text)
        listenButton = findViewById(R.id.listen_button)

        // Check microphone permission
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) 
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.RECORD_AUDIO), 100)
        }

        setupSpeechRecognizer()
        setupTTS()

        listenButton.setOnClickListener {
            startListening()
        }
    }

    private fun setupSpeechRecognizer() {
        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this)
        
        speechRecognizer.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {
                statusText.text = "🎤 Listening..."
                listenButton.isEnabled = false
            }

            override fun onBeginningOfSpeech() {
                statusText.text = "🗣️ Speaking..."
            }

            override fun onEndOfSpeech() {
                statusText.text = "⚙️ Processing..."
            }

            override fun onError(error: Int) {
                statusText.text = "❌ Error - Tap to try again"
                listenButton.isEnabled = true
            }

            override fun onResults(results: Bundle?) {
                val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                if (matches != null && matches.isNotEmpty()) {
                    val command = matches[0]
                    statusText.text = "Heard: \"$command\""
                    executeCommand(command)
                }
                listenButton.isEnabled = true
            }

            override fun onPartialResults(partialResults: Bundle?) {}
            override fun onEvent(eventType: Int, params: Bundle?) {}
            override fun onRmsChanged(rmsdB: Float) {}
            override fun onBufferReceived(buffer: ByteArray?) {}
        })
    }

    private fun setupTTS() {
        tts = TextToSpeech(this) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts.language = Locale.US
            }
        }
    }

    private fun startListening() {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-US")
        }
        speechRecognizer.startListening(intent)
    }

    private fun executeCommand(command: String) {
        val cmd = command.lowercase()
        
        val result = when {
            cmd.contains("whatsapp") -> {
                openApp("com.whatsapp")
                "Opening WhatsApp"
            }
            cmd.contains("chrome") -> {
                openApp("com.android.chrome")
                "Opening Chrome"
            }
            cmd.contains("gmail") -> {
                openApp("com.google.android.gm")
                "Opening Gmail"
            }
            cmd.contains("youtube") -> {
                openApp("com.google.android.youtube")
                "Opening YouTube"
            }
            cmd.contains("home") -> {
                val intent = Intent(Intent.ACTION_MAIN).apply {
                    addCategory(Intent.CATEGORY_HOME)
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK
                }
                startActivity(intent)
                "Going home"
            }
            else -> "I don't understand: $command"
        }
        
        statusText.text = "✅ $result"
        speak(result)
    }

    private fun openApp(packageName: String) {
        try {
            val intent = packageManager.getLaunchIntentForPackage(packageName)
            if (intent != null) {
                startActivity(intent)
            } else {
                Toast.makeText(this, "App not installed", Toast.LENGTH_SHORT).show()
            }
        } catch (e: Exception) {
            Toast.makeText(this, "Error opening app", Toast.LENGTH_SHORT).show()
        }
    }

    private fun speak(text: String) {
        tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, null)
    }

    override fun onDestroy() {
        super.onDestroy()
        speechRecognizer.destroy()
        tts.shutdown()
    }
}
