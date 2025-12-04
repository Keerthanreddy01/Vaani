package com.vaani.phone

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.Build
import android.os.IBinder
import android.speech.tts.TextToSpeech
import android.util.Log
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.*
import org.vosk.Model
import org.vosk.Recognizer
import org.vosk.android.RecognitionListener
import org.vosk.android.SpeechService
import org.vosk.android.StorageService
import java.util.*

class VaaniVoiceService : Service() {
    
    private var speechService: SpeechService? = null
    private var tts: TextToSpeech? = null
    private var intentClassifier: VaaniIntentClassifier? = null
    private var actionExecutor: VaaniActionExecutor? = null
    
    private var isListening = false
    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    
    companion object {
        const val TAG = "VaaniVoiceService"
        const val CHANNEL_ID = "VaaniVoiceChannel"
        const val NOTIFICATION_ID = 1
        
        private var statusListener: StatusListener? = null
        
        fun setStatusListener(listener: StatusListener?) {
            statusListener = listener
        }
        
        interface StatusListener {
            fun onStatusChanged(status: String)
            fun onCommandReceived(command: String)
        }
    }
    
    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "Service created")
        
        createNotificationChannel()
        
        // Initialize TTS
        tts = TextToSpeech(this) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale.US
            }
        }
        
        // Initialize components
        intentClassifier = VaaniIntentClassifier()
        actionExecutor = VaaniActionExecutor(this)
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "Service started")
        
        val notification = createNotification("Initializing...")
        startForeground(NOTIFICATION_ID, notification)
        
        // Start listening
        startListening()
        
        return START_STICKY
    }
    
    private fun startListening() {
        updateStatus("Loading speech model...")
        
        scope.launch(Dispatchers.IO) {
            try {
                val voskManager = VoskManager.getInstance(applicationContext)
                
                if (!voskManager.isModelReady()) {
                    withContext(Dispatchers.Main) {
                        updateStatus("Downloading speech model...")
                    }
                    
                    val downloaded = voskManager.downloadModelSync()
                    
                    if (!downloaded) {
                        withContext(Dispatchers.Main) {
                            updateStatus("Failed to download model")
                            speak("Failed to download speech model")
                        }
                        return@launch
                    }
                }
                
                // Create recognizer
                val model = voskManager.getModel()
                if (model != null) {
                    withContext(Dispatchers.Main) {
                        initializeRecognizer(model)
                    }
                } else {
                    withContext(Dispatchers.Main) {
                        updateStatus("Failed to load model")
                        speak("Failed to load speech model")
                    }
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Error starting listening", e)
                withContext(Dispatchers.Main) {
                    updateStatus("Error: ${e.message}")
                }
            }
        }
    }
    
    private fun initializeRecognizer(model: Model) {
        try {
            val recognizer = Recognizer(model, 16000.0f)
            
            speechService = SpeechService(recognizer, 16000.0f)
            
            speechService?.startListening(object : RecognitionListener {
                override fun onPartialResult(hypothesis: String?) {
                    // Ignore partial results
                }
                
                override fun onResult(hypothesis: String?) {
                    hypothesis?.let {
                        handleRecognitionResult(it)
                    }
                }
                
                override fun onFinalResult(hypothesis: String?) {
                    hypothesis?.let {
                        handleRecognitionResult(it)
                    }
                }
                
                override fun onError(exception: Exception?) {
                    Log.e(TAG, "Recognition error", exception)
                    updateStatus("Error: ${exception?.message}")
                }
                
                override fun onTimeout() {
                    Log.d(TAG, "Recognition timeout")
                }
            })
            
            isListening = true
            updateStatus("🎤 Listening... Speak now!")
            updateNotification("Listening...")
            speak("Ready. I'm listening.")
            
        } catch (e: Exception) {
            Log.e(TAG, "Error initializing recognizer", e)
            updateStatus("Error: ${e.message}")
        }
    }
    
    private fun handleRecognitionResult(result: String) {
        try {
            // Parse JSON result
            val text = extractTextFromVoskResult(result)
            
            if (text.isNotBlank() && text.length > 2) {
                Log.d(TAG, "Recognized: $text")
                updateStatus("🎤 Heard: $text")
                notifyCommand(text)
                processCommand(text)
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Error handling result", e)
        }
    }
    
    private fun extractTextFromVoskResult(json: String): String {
        try {
            val jsonObject = org.json.JSONObject(json)
            return jsonObject.optString("text", "")
        } catch (e: Exception) {
            return ""
        }
    }
    
    private fun processCommand(text: String) {
        scope.launch {
            try {
                updateStatus("⚙️ Processing...")
                updateNotification("Processing...")
                
                // Classify intent
                val result = intentClassifier?.classify(text)
                
                if (result != null) {
                    val intent = result.intent
                    val entities = result.entities
                    
                    Log.d(TAG, "Intent: $intent, Entities: $entities")
                    
                    updateStatus("⚡ Executing: $intent")
                    updateNotification("Executing...")
                    
                    // Execute action
                    val actionResult = actionExecutor?.execute(intent, entities)
                    
                    if (actionResult?.success == true) {
                        val response = actionResult.message
                        updateStatus("✅ $response")
                        speak(response)
                    } else {
                        val error = actionResult?.message ?: "Sorry, I couldn't do that"
                        updateStatus("❌ $error")
                        speak(error)
                    }
                    
                } else {
                    updateStatus("❓ Didn't understand: $text")
                    speak("Sorry, I didn't understand that")
                }
                
                // Return to listening
                delay(2000)
                updateStatus("🎤 Listening...")
                updateNotification("Listening...")
                
            } catch (e: Exception) {
                Log.e(TAG, "Error processing command", e)
                updateStatus("Error: ${e.message}")
            }
        }
    }
    
    private fun speak(text: String) {
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, null)
    }
    
    private fun updateStatus(status: String) {
        statusListener?.onStatusChanged(status)
    }
    
    private fun notifyCommand(command: String) {
        statusListener?.onCommandReceived(command)
    }
    
    private fun updateNotification(text: String) {
        val notification = createNotification(text)
        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager?.notify(NOTIFICATION_ID, notification)
    }
    
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "VAANI Voice Service",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "VAANI voice assistant is running"
            }
            
            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager?.createNotificationChannel(channel)
        }
    }
    
    private fun createNotification(text: String): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("VAANI Voice Assistant")
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setOngoing(true)
            .build()
    }
    
    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "Service destroyed")
        
        isListening = false
        speechService?.stop()
        speechService?.shutdown()
        tts?.shutdown()
        scope.cancel()
    }
    
    override fun onBind(intent: Intent?): IBinder? {
        return null
    }
}
