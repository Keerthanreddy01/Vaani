package com.vaani.phone

import android.content.Context
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import kotlinx.coroutines.*
import kotlin.math.abs

/**
 * Wake Word Detector for Vaani
 * Continuously listens for the wake word (e.g., "Vaani", "Hey Assistant", etc.)
 * Uses pattern matching and keyword spotting to detect wake words
 */
class WakeWordDetector(
    private val context: Context,
    private val wakeWord: String,
    private val onWakeWordDetected: () -> Unit
) {
    
    companion object {
        const val TAG = "WakeWordDetector"
        const val SAMPLE_RATE = 16000
        const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
        const val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT
        
        // Energy threshold for voice activity detection
        const val ENERGY_THRESHOLD = 1000
        const val SILENCE_DURATION_MS = 800
    }
    
    private var audioRecord: AudioRecord? = null
    private var isListening = false
    private var detectionJob: Job? = null
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    private var recognizer: org.vosk.Recognizer? = null
    private var model: org.vosk.Model? = null
    
    fun start() {
        if (isListening) {
            Log.w(TAG, "Already listening")
            return
        }
        
        Log.d(TAG, "Starting wake word detection for: $wakeWord")
        
        scope.launch {
            try {
                initializeVosk()
                startAudioRecording()
            } catch (e: Exception) {
                Log.e(TAG, "Error starting wake word detection", e)
            }
        }
    }
    
    fun stop() {
        Log.d(TAG, "Stopping wake word detection")
        isListening = false
        
        detectionJob?.cancel()
        
        audioRecord?.apply {
            if (state == AudioRecord.STATE_INITIALIZED) {
                stop()
                release()
            }
        }
        audioRecord = null
        
        recognizer?.close()
        recognizer = null
    }
    
    fun updateWakeWord(newWakeWord: String) {
        Log.d(TAG, "Updating wake word to: $newWakeWord")
        // Restart detection with new wake word
        val wasListening = isListening
        stop()
        if (wasListening) {
            // Give a brief delay before restarting
            scope.launch {
                delay(500)
                start()
            }
        }
    }
    
    private suspend fun initializeVosk() {
        withContext(Dispatchers.IO) {
            try {
                val voskManager = VoskManager.getInstance(context)
                
                if (!voskManager.isModelReady()) {
                    Log.d(TAG, "Downloading Vosk model...")
                    val downloaded = voskManager.downloadModelSync()
                    if (!downloaded) {
                        Log.e(TAG, "Failed to download Vosk model")
                        return@withContext
                    }
                }
                
                model = voskManager.getModel()
                if (model != null) {
                    recognizer = org.vosk.Recognizer(model, SAMPLE_RATE.toFloat())
                    Log.d(TAG, "Vosk initialized successfully")
                } else {
                    Log.e(TAG, "Failed to load Vosk model")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error initializing Vosk", e)
            }
        }
    }
    
    private suspend fun startAudioRecording() {
        withContext(Dispatchers.IO) {
            try {
                val bufferSize = AudioRecord.getMinBufferSize(
                    SAMPLE_RATE,
                    CHANNEL_CONFIG,
                    AUDIO_FORMAT
                )
                
                audioRecord = AudioRecord(
                    MediaRecorder.AudioSource.VOICE_RECOGNITION,
                    SAMPLE_RATE,
                    CHANNEL_CONFIG,
                    AUDIO_FORMAT,
                    bufferSize * 2
                )
                
                if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
                    Log.e(TAG, "Failed to initialize AudioRecord")
                    return@withContext
                }
                
                audioRecord?.startRecording()
                isListening = true
                
                Log.d(TAG, "Audio recording started, listening for wake word...")
                
                detectionJob = scope.launch {
                    processAudioStream(bufferSize)
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Error starting audio recording", e)
            }
        }
    }
    
    private suspend fun processAudioStream(bufferSize: Int) {
        val buffer = ShortArray(bufferSize)
        var silenceStart = 0L
        var lastSpeech = System.currentTimeMillis()
        
        while (isListening && audioRecord?.recordingState == AudioRecord.RECORDSTATE_RECORDING) {
            try {
                val readCount = audioRecord?.read(buffer, 0, buffer.size) ?: 0
                
                if (readCount > 0) {
                    // Calculate audio energy (simple VAD)
                    val energy = calculateEnergy(buffer, readCount)
                    
                    val currentTime = System.currentTimeMillis()
                    
                    if (energy > ENERGY_THRESHOLD) {
                        // Speech detected
                        lastSpeech = currentTime
                        silenceStart = 0L
                        
                        // Feed to Vosk for recognition
                        recognizer?.let { rec ->
                            // Convert short array to byte array
                            val byteBuffer = java.nio.ByteBuffer.allocate(readCount * 2)
                            byteBuffer.order(java.nio.ByteOrder.LITTLE_ENDIAN)
                            for (i in 0 until readCount) {
                                byteBuffer.putShort(buffer[i])
                            }
                            
                            if (rec.acceptWaveForm(byteBuffer.array(), readCount * 2)) {
                                val result = rec.result
                                checkForWakeWord(result)
                            } else {
                                val partialResult = rec.partialResult
                                checkForWakeWord(partialResult)
                            }
                        }
                        
                    } else {
                        // Silence detected
                        if (silenceStart == 0L) {
                            silenceStart = currentTime
                        } else if (currentTime - silenceStart > SILENCE_DURATION_MS) {
                            // Reset recognizer after prolonged silence
                            recognizer?.let { rec ->
                                val finalResult = rec.result
                                checkForWakeWord(finalResult)
                            }
                        }
                    }
                }
                
                // Small delay to avoid consuming too much CPU
                delay(10)
                
            } catch (e: Exception) {
                Log.e(TAG, "Error processing audio", e)
                if (!isListening) break
            }
        }
    }
    
    private fun calculateEnergy(buffer: ShortArray, count: Int): Long {
        var sum = 0L
        for (i in 0 until count) {
            sum += abs(buffer[i].toLong())
        }
        return sum / count
    }
    
    private fun checkForWakeWord(jsonResult: String) {
        try {
            val text = extractText(jsonResult).lowercase().trim()
            
            if (text.isEmpty()) return
            
            Log.d(TAG, "Checking text: $text")
            
            // Check if the text contains the wake word
            val normalizedWakeWord = wakeWord.lowercase().trim()
            
            if (text.contains(normalizedWakeWord)) {
                Log.d(TAG, "WAKE WORD DETECTED: $wakeWord")
                
                // Trigger wake word callback
                scope.launch(Dispatchers.Main) {
                    onWakeWordDetected()
                }
                
                // Brief pause after detection to avoid multiple triggers
                scope.launch {
                    val wasListening = isListening
                    isListening = false
                    delay(2000) // 2 second pause
                    isListening = wasListening
                }
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Error checking wake word", e)
        }
    }
    
    private fun extractText(jsonResult: String): String {
        return try {
            val json = org.json.JSONObject(jsonResult)
            json.optString("text", json.optString("partial", ""))
        } catch (e: Exception) {
            Log.e(TAG, "Error parsing JSON", e)
            ""
        }
    }
    
    fun isActive(): Boolean = isListening
    
    fun getWakeWord(): String = wakeWord
}
