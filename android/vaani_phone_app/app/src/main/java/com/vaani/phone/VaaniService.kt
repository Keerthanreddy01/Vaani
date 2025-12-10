package com.vaani.phone

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.SharedPreferences
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
import java.util.*

/**
 * Main Vaani Service
 * - Runs continuously in the background
 * - Listens for wake word (e.g., "Vaani", "Hey Assistant")
 * - Processes voice commands when wake word is detected
 * - Executes actions based on commands
 */
class VaaniService : Service() {
    
    private var wakeWordDetector: WakeWordDetector? = null
    private var speechService: SpeechService? = null
    private var tts: TextToSpeech? = null
    private var intentClassifier: VaaniIntentClassifier? = null
    private var actionExecutor: VaaniActionExecutor? = null
    
    private var isProcessingCommand = false
    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    
    private lateinit var prefs: SharedPreferences
    private var currentWakeWord = "Vaani"
    
    companion object {
        const val TAG = "VaaniService"
        const val CHANNEL_ID = "VaaniChannel"
        const val NOTIFICATION_ID = 1001
        
        const val ACTION_START_LISTENING = "com.vaani.phone.START_LISTENING"
        const val ACTION_STOP_LISTENING = "com.vaani.phone.STOP_LISTENING"
        const val ACTION_PROCESS_COMMAND = "com.vaani.phone.PROCESS_COMMAND"
    }
    
    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "VaaniService created")
        
        prefs = getSharedPreferences("VaaniPrefs", MODE_PRIVATE)
        currentWakeWord = prefs.getString("wake_word", "Vaani") ?: "Vaani"
        
        createNotificationChannel()
        
        // Initialize TTS
        tts = TextToSpeech(this) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale.US
                speak("Vaani service started. I'm ready to help.")
            }
        }
        
        // Initialize components
        intentClassifier = VaaniIntentClassifier()
        actionExecutor = VaaniActionExecutor(this)
        
        // Save service state
        prefs.edit().putBoolean("service_running", true).apply()
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "VaaniService started with action: ${intent?.action}")
        
        val notification = createNotification("Initializing...")
        startForeground(NOTIFICATION_ID, notification)
        
        when (intent?.action) {
            ACTION_START_LISTENING -> startWakeWordDetection()
            ACTION_STOP_LISTENING -> stopWakeWordDetection()
            ACTION_PROCESS_COMMAND -> processCommandMode()
            else -> startWakeWordDetection()
        }
        
        return START_STICKY
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "VaaniService destroyed")
        
        stopWakeWordDetection()
        speechService?.shutdown()
        tts?.shutdown()
        scope.cancel()
        
        prefs.edit().putBoolean("service_running", false).apply()
    }
    
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Vaani Voice Assistant",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Voice assistant running in background"
                setShowBadge(false)
            }
            
            val manager = getSystemService(NotificationManager::class.java)
            manager?.createNotificationChannel(channel)
        }
    }
    
    private fun createNotification(status: String): Notification {
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
        
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Vaani is listening")
            .setContentText(status)
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }
    
    private fun updateNotification(status: String) {
        val notification = createNotification(status)
        val manager = getSystemService(NotificationManager::class.java)
        manager?.notify(NOTIFICATION_ID, notification)
    }
    
    private fun startWakeWordDetection() {
        if (wakeWordDetector?.isActive() == true) {
            Log.d(TAG, "Wake word detection already active")
            return
        }
        
        Log.d(TAG, "Starting wake word detection for: $currentWakeWord")
        updateNotification("Listening for \"$currentWakeWord\"...")
        
        wakeWordDetector = WakeWordDetector(
            context = applicationContext,
            wakeWord = currentWakeWord,
            onWakeWordDetected = {
                onWakeWordDetected()
            }
        )
        
        wakeWordDetector?.start()
    }
    
    private fun stopWakeWordDetection() {
        Log.d(TAG, "Stopping wake word detection")
        wakeWordDetector?.stop()
        wakeWordDetector = null
    }
    
    private fun onWakeWordDetected() {
        Log.d(TAG, "Wake word detected: $currentWakeWord")
        
        // Give feedback
        vibrate()
        speak("Yes?")
        updateNotification("Wake word detected! Listening for command...")
        
        // Show overlay indicator
        showOverlayIndicator()
        
        // Start command listening mode
        startCommandListening()
    }
    
    private fun startCommandListening() {
        if (isProcessingCommand) {
            Log.d(TAG, "Already processing a command")
            return
        }
        
        isProcessingCommand = true
        updateNotification("Listening for your command...")
        
        scope.launch(Dispatchers.IO) {
            try {
                val voskManager = VoskManager.getInstance(applicationContext)
                val model = voskManager.getModel()
                
                if (model != null) {
                    withContext(Dispatchers.Main) {
                        initializeCommandRecognizer(model)
                    }
                } else {
                    withContext(Dispatchers.Main) {
                        speak("Speech model not available")
                        isProcessingCommand = false
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error starting command listening", e)
                withContext(Dispatchers.Main) {
                    speak("Error starting command recognition")
                    isProcessingCommand = false
                }
            }
        }
    }
    
    private fun initializeCommandRecognizer(model: Model) {
        try {
            val recognizer = Recognizer(model, 16000.0f)
            speechService = SpeechService(recognizer, 16000.0f)
            
            speechService?.startListening(object : RecognitionListener {
                override fun onPartialResult(hypothesis: String?) {
                    // Show partial results in overlay
                    hypothesis?.let {
                        val text = extractTextFromResult(it)
                        if (text.isNotBlank()) {
                            updateOverlay("Hearing: $text")
                        }
                    }
                }
                
                override fun onResult(hypothesis: String?) {
                    hypothesis?.let {
                        handleCommandResult(it)
                    }
                }
                
                override fun onFinalResult(hypothesis: String?) {
                    hypothesis?.let {
                        handleCommandResult(it)
                    }
                    stopCommandListening()
                }
                
                override fun onError(exception: Exception?) {
                    Log.e(TAG, "Recognition error", exception)
                    speak("Sorry, I couldn't hear that")
                    stopCommandListening()
                }
                
                override fun onTimeout() {
                    Log.d(TAG, "Recognition timeout")
                    speak("I didn't hear anything")
                    stopCommandListening()
                }
            })
            
            // Auto-stop after 10 seconds
            scope.launch {
                delay(10000)
                if (isProcessingCommand) {
                    stopCommandListening()
                    speak("Listening timeout")
                }
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Error initializing command recognizer", e)
            speak("Error initializing speech recognition")
            isProcessingCommand = false
        }
    }
    
    private fun stopCommandListening() {
        speechService?.stop()
        speechService?.shutdown()
        speechService = null
        isProcessingCommand = false
        hideOverlayIndicator()
        updateNotification("Listening for \"$currentWakeWord\"...")
    }
    
    private fun handleCommandResult(result: String) {
        val text = extractTextFromResult(result)
        
        if (text.isBlank() || text.length < 3) {
            speak("I didn't catch that")
            return
        }
        
        Log.d(TAG, "Command recognized: $text")
        updateNotification("Processing: $text")
        updateOverlay("Command: $text")
        
        // Process the command
        processCommand(text)
    }
    
    private fun extractTextFromResult(json: String): String {
        return try {
            val jsonObject = org.json.JSONObject(json)
            jsonObject.optString("text", jsonObject.optString("partial", ""))
        } catch (e: Exception) {
            ""
        }
    }
    
    private fun processCommand(text: String) {
        scope.launch {
            try {
                updateNotification("Processing command...")
                
                // Classify intent
                val classification = intentClassifier?.classify(text)
                
                if (classification != null) {
                    Log.d(TAG, "Intent: ${classification.intent}, Entities: ${classification.entities}")
                    
                    // Execute action
                    val result = actionExecutor?.execute(classification.intent, classification.entities)
                    
                    if (result?.success == true) {
                        speak(result.message)
                        updateOverlay("✓ ${result.message}")
                    } else {
                        speak(result?.message ?: "Sorry, I couldn't do that")
                        updateOverlay("✗ ${result?.message ?: "Failed"}")
                    }
                } else {
                    speak("I didn't understand that command")
                    updateOverlay("✗ Command not recognized")
                }
                
                // Hide overlay after 2 seconds
                delay(2000)
                hideOverlayIndicator()
                
                updateNotification("Listening for \"$currentWakeWord\"...")
                
            } catch (e: Exception) {
                Log.e(TAG, "Error processing command", e)
                speak("Error processing command")
            }
        }
    }
    
    private fun processCommandMode() {
        // Direct command processing mode (triggered from UI)
        onWakeWordDetected()
    }
    
    private fun speak(text: String) {
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, null)
    }
    
    private fun vibrate() {
        try {
            val vibrator = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                val vibratorManager = getSystemService(android.os.VibratorManager::class.java)
                vibratorManager?.defaultVibrator
            } else {
                @Suppress("DEPRECATION")
                getSystemService(android.os.Vibrator::class.java)
            }
            
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                val effect = android.os.VibrationEffect.createOneShot(100, android.os.VibrationEffect.DEFAULT_AMPLITUDE)
                vibrator?.vibrate(effect)
            } else {
                @Suppress("DEPRECATION")
                vibrator?.vibrate(100)
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error vibrating", e)
        }
    }
    
    private fun showOverlayIndicator() {
        // Send broadcast to overlay service
        val intent = Intent("com.vaani.phone.SHOW_OVERLAY")
        sendBroadcast(intent)
    }
    
    private fun hideOverlayIndicator() {
        val intent = Intent("com.vaani.phone.HIDE_OVERLAY")
        sendBroadcast(intent)
    }
    
    private fun updateOverlay(text: String) {
        val intent = Intent("com.vaani.phone.UPDATE_OVERLAY")
        intent.putExtra("text", text)
        sendBroadcast(intent)
    }
}
